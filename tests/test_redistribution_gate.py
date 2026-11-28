import hashlib
import io
import json
import zipfile
import pytest
from installer.redistribution_gate import audit, PREFIX, NOTICES


def archive_for(binary='Qt6Core.dll', notice='LGPL-3.0-only.txt', *, omit=False, tamper=False, duplicate=False, warning=False, python_license=True, qt_lgpl=True, metadata_lgpl=True):
    b = io.BytesIO()
    payload = b'binary fixture'
    text = b'license fixture'
    sha = lambda data: hashlib.sha256(data).hexdigest()
    path = '_internal/PySide6/' + binary
    relative = 'PySide6/licenses/' + notice
    inv = {'kind': 'build-license-evidence', 'binaries': [{'path': path, 'size': len(payload), 'sha256': sha(payload)}],
           'packages': [{'name': 'PySide6', 'notices': [{'path': relative, 'sha256': sha(text)}]}],
           'warnings': ['example'] if warning else []}
    if python_license:
        inv['python_license'] = {'path': 'Python-LICENSE.txt', 'sha256': sha(text)}
    with zipfile.ZipFile(b, 'w') as z:
        if not omit:
            z.writestr(PREFIX + path, b'changed' if tamper else payload)
        z.writestr(NOTICES + relative, text)
        metadata = b'Name: PySide6\nVersion: 6.12.0\nLicense: LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only\n' if metadata_lgpl else b'Name: PySide6\nVersion: 6.12.0\nLicense: LicenseRef-Qt-Commercial\n'
        z.writestr(NOTICES + 'PySide6/METADATA.txt', metadata)
        if qt_lgpl:
            z.writestr(NOTICES + 'qt-license-texts/LGPL-3.0-only.txt', b'GNU LESSER GENERAL PUBLIC LICENSE\nVersion 3, 29 June 2007\n')
        if python_license:
            z.writestr(NOTICES + 'Python-LICENSE.txt', text)
        extra = {
            'BSD-3-Clause.txt': b'BSD notice fixture',
            'libtiff.txt': b'libtiff notice fixture',
            'libwebp-COPYING.txt': b'libwebp notice fixture',
            'NOTICE.md': b'Qt Image Formats notice fixture',
            'plugin-map.json': json.dumps({'plugins': {'qicns': {}, 'qtga': {}, 'qtiff': {}, 'qwbmp': {}, 'qwebp': {}}}).encode(),
            'libtiff-attribution.json': b'libtiff attribution fixture',
            'libwebp-attribution.json': b'libwebp attribution fixture',
        }
        supplement_rows = [{'file': name, 'bytes': len(data), 'sha256': sha(data)} for name, data in extra.items()]
        supplement = {'kind':'qt-imageformats-license-supplement','source_version':'6.12.0',
                      'source_archive_sha256':'0943132b5db8de6b6a7f1d162682173e8763c7ed94e80fd39113292845f67762',
                      'files':supplement_rows,'review_complete':False,
                      'exact_corresponding_source_verified':False,'redistribution_approved':False}
        for name, data in extra.items():
            z.writestr(NOTICES + 'qt-license-texts/qtimageformats/' + name, data)
        z.writestr(NOTICES + 'qt-license-texts/qtimageformats/SUPPLEMENT.json', json.dumps(supplement))
        z.writestr(NOTICES + 'inventory.json', json.dumps(inv))
        if duplicate:
            with pytest.warns(UserWarning):
                z.writestr(NOTICES + 'inventory.json', '{}')
    return zipfile.ZipFile(b)


def test_clear_preflight_does_not_approve_release():
    with archive_for() as z:
        report = audit(z)
    assert report['flags'] == [{'code': 'qt-corresponding-source-and-relink-review'}, {'code': 'qt-imageformats-notice-and-corresponding-source-review'}]
    assert report['manual_review_required'] is True
    assert report['public_release_approved'] is False


@pytest.mark.parametrize('binary', ['Qt6VirtualKeyboard.dll', 'plugins/platforminputcontexts/qtvirtualkeyboardplugin.dll'])
def test_gpl_module_flag(binary):
    with archive_for(binary=binary) as z:
        assert audit(z)['flags'][0]['code'] == 'qt-gpl-module-review'


def test_global_lgpl_text_and_metadata_are_required_even_with_commercial_wheel_marker():
    with archive_for(notice='LicenseRef-Qt-Commercial.txt', qt_lgpl=False) as z:
        assert audit(z)['flags'] == [{'code': 'qt-lgpl-text-not-identified', 'package': 'PySide6'}, {'code': 'qt-imageformats-notice-and-corresponding-source-review'}]
    with archive_for(metadata_lgpl=False) as z:
        assert audit(z)['flags'] == [{'code': 'qt-lgpl-license-expression-not-identified', 'package': 'PySide6'}, {'code': 'qt-imageformats-notice-and-corresponding-source-review'}]


@pytest.mark.parametrize('options', [{'omit': True}, {'tamper': True}, {'duplicate': True}])
def test_rejects_bad_inventory(options):
    with archive_for(**options) as z, pytest.raises(ValueError):
        audit(z)


def test_warn_and_missing_python_license():
    with archive_for(warning=True, python_license=False) as z:
        assert {x['code'] for x in audit(z)['flags']} == {'inventory-warning', 'missing-python-license', 'qt-corresponding-source-and-relink-review', 'qt-imageformats-notice-and-corresponding-source-review'}


def test_rejects_missing_qt_imageformats_supplement():
    with archive_for() as z:
        entries = {name: z.read(name) for name in z.namelist()}
    name = NOTICES + 'qt-license-texts/qtimageformats/SUPPLEMENT.json'
    entries.pop(name)
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w') as out:
        for path, data in entries.items():
            out.writestr(path, data)
    with zipfile.ZipFile(b) as out, pytest.raises(KeyError):
        audit(out)


def test_rejects_tampered_qt_imageformats_notice():
    with archive_for() as z:
        entries = {name: z.read(name) for name in z.namelist()}
    name = NOTICES + 'qt-license-texts/qtimageformats/libtiff.txt'
    entries[name] = b'tampered'
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w') as out:
        for path, data in entries.items():
            out.writestr(path, data)
    with zipfile.ZipFile(b) as out, pytest.raises(ValueError, match='notice hash mismatch'):
        audit(out)
