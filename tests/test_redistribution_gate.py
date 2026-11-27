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
        z.writestr(NOTICES + 'inventory.json', json.dumps(inv))
        if duplicate:
            with pytest.warns(UserWarning):
                z.writestr(NOTICES + 'inventory.json', '{}')
    return zipfile.ZipFile(b)


def test_clear_preflight_does_not_approve_release():
    with archive_for() as z:
        report = audit(z)
    assert report['flags'] == [{'code': 'qt-corresponding-source-and-relink-review'}]
    assert report['manual_review_required'] is True
    assert report['public_release_approved'] is False


@pytest.mark.parametrize('binary', ['Qt6VirtualKeyboard.dll', 'plugins/platforminputcontexts/qtvirtualkeyboardplugin.dll'])
def test_gpl_module_flag(binary):
    with archive_for(binary=binary) as z:
        assert audit(z)['flags'][0]['code'] == 'qt-gpl-module-review'


def test_global_lgpl_text_and_metadata_are_required_even_with_commercial_wheel_marker():
    with archive_for(notice='LicenseRef-Qt-Commercial.txt', qt_lgpl=False) as z:
        assert audit(z)['flags'] == [{'code': 'qt-lgpl-text-not-identified', 'package': 'PySide6'}]
    with archive_for(metadata_lgpl=False) as z:
        assert audit(z)['flags'] == [{'code': 'qt-lgpl-license-expression-not-identified', 'package': 'PySide6'}]


@pytest.mark.parametrize('options', [{'omit': True}, {'tamper': True}, {'duplicate': True}])
def test_rejects_bad_inventory(options):
    with archive_for(**options) as z, pytest.raises(ValueError):
        audit(z)


def test_warn_and_missing_python_license():
    with archive_for(warning=True, python_license=False) as z:
        assert {x['code'] for x in audit(z)['flags']} == {'inventory-warning', 'missing-python-license', 'qt-corresponding-source-and-relink-review'}
