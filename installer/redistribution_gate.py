"""Conservative public-distribution preflight for a frozen portable ZIP.

This is evidence, not legal approval. Do not execute or extract the archive.
"""
import argparse
import hashlib
import json
from pathlib import PurePosixPath
import zipfile

from installer.windows_zip_paths import validate_windows_paths

PREFIX = 'ManoStudio/'
NOTICES = PREFIX + 'third-party-notices/'
BINARY_SUFFIXES = {'.dll', '.pyd', '.exe'}
QT_ONLY_GPL_MARKERS = ('virtualkeyboard',)
QT_LGPL_TEXT = NOTICES + 'qt-license-texts/LGPL-3.0-only.txt'


def has_lgpl_text(archive):
    try:
        data = archive.read(QT_LGPL_TEXT)
    except KeyError:
        return False
    return b'GNU LESSER GENERAL PUBLIC LICENSE' in data and b'Version 3' in data


def audit(archive):
    validate_windows_paths(archive, PREFIX)
    names = archive.namelist()
    inventory = json.loads(archive.read(NOTICES + 'inventory.json'))
    if inventory.get('kind') != 'build-license-evidence':
        raise ValueError('Invalid build inventory')
    actual = {n[len(PREFIX):] for n in names
              if PurePosixPath(n).suffix.lower() in BINARY_SUFFIXES}
    expected = {}
    for item in inventory['binaries']:
        if item['path'] in expected:
            raise ValueError('Duplicate binary inventory entry')
        expected[item['path']] = item
    if actual != set(expected):
        raise ValueError('Binary inventory does not match archive')
    for relative, item in expected.items():
        data = archive.read(PREFIX + relative)
        if len(data) != item['size'] or hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError('Binary evidence mismatch: ' + relative)
    flags = []
    qt_source_review = False
    for relative in sorted(actual):
        if any(marker in relative.lower() for marker in QT_ONLY_GPL_MARKERS):
            flags.append({'code': 'qt-gpl-module-review', 'path': relative})
    for package in inventory['packages']:
        name = package['name']
        key = name.lower().replace('_', '-')
        paths = []
        for notice in package['notices']:
            relative = notice['path']
            if not relative.startswith(name + '/') or '..' in relative.split('/'):
                raise ValueError('Unexpected notice path: ' + relative)
            data = archive.read(NOTICES + relative)
            if hashlib.sha256(data).hexdigest() != notice['sha256']:
                raise ValueError('License evidence mismatch: ' + relative)
            paths.append(PurePosixPath(relative).name.lower())
        if not paths:
            flags.append({'code': 'missing-package-notice', 'package': name})
        if key.startswith(('pyside6', 'shiboken6')):
            try:
                metadata = archive.read(NOTICES + name + '/METADATA.txt')
            except KeyError:
                metadata = b''
            if b'LGPL-3.0-only' not in metadata and b'LGPLv3' not in metadata:
                flags.append({'code': 'qt-lgpl-license-expression-not-identified', 'package': name})
            elif not has_lgpl_text(archive):
                flags.append({'code': 'qt-lgpl-text-not-identified', 'package': name})
            else:
                qt_source_review = True
    if qt_source_review:
        flags.append({'code': 'qt-corresponding-source-and-relink-review'})
    for warning in inventory['warnings']:
        flags.append({'code': 'inventory-warning', 'detail': warning})
    flags.append(audit_qt_imageformats(archive))
    if not inventory.get('python_license'):
        flags.append({'code': 'missing-python-license'})
    else:
        item = inventory['python_license']
        if hashlib.sha256(archive.read(NOTICES + item['path'])).hexdigest() != item['sha256']:
            raise ValueError('Python license evidence mismatch')
    return {'binary_count': len(actual), 'package_count': len(inventory['packages']),
            'flags': flags, 'manual_review_required': True, 'public_release_approved': False}



def audit_qt_imageformats(archive):
    base = NOTICES + 'qt-license-texts/qtimageformats/'
    manifest = json.loads(archive.read(base + 'SUPPLEMENT.json'))
    if (manifest.get('kind') != 'qt-imageformats-license-supplement'
            or manifest.get('source_version') != '6.12.0'
            or manifest.get('source_archive_sha256') != '0943132b5db8de6b6a7f1d162682173e8763c7ed94e80fd39113292845f67762'
            or manifest.get('review_complete') is not False
            or manifest.get('exact_corresponding_source_verified') is not False
            or manifest.get('redistribution_approved') is not False):
        raise ValueError('Invalid Qt Image Formats notice supplement')
    expected = {'BSD-3-Clause.txt','libtiff.txt','libwebp-COPYING.txt','NOTICE.md',
                'plugin-map.json','libtiff-attribution.json','libwebp-attribution.json'}
    rows = manifest.get('files')
    if not isinstance(rows, list) or {item.get('file') for item in rows} != expected or len(rows) != len(expected):
        raise ValueError('Qt Image Formats notice inventory incomplete')
    for item in rows:
        name = item['file']
        data = archive.read(base + name)
        if len(data) != item.get('bytes') or hashlib.sha256(data).hexdigest() != item.get('sha256'):
            raise ValueError('Qt Image Formats notice hash mismatch: ' + name)
    mapping = json.loads(archive.read(base + 'plugin-map.json'))
    if set(mapping.get('plugins', {})) != {'qicns','qtga','qtiff','qwbmp','qwebp'}:
        raise ValueError('Qt Image Formats plugin map incomplete')
    return {'code':'qt-imageformats-notice-and-corresponding-source-review'}



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('portable_zip')
    args = parser.parse_args()
    with zipfile.ZipFile(args.portable_zip) as archive:
        result = audit(archive)
    print(json.dumps(result, indent=2))
    return 2 if result['flags'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
