"""Compare two internal portable archives without extracting or executing binaries."""
import argparse
import hashlib
import json
from pathlib import PurePosixPath
import zipfile

ROOT = 'ManoStudio/'
TARGETS = {'_internal/PySide6/Qt6Pdf.dll', '_internal/PySide6/plugins/imageformats/qpdf.dll'}


def binary_inventory(archive):
    names = archive.namelist()
    if len(names) != len({n.lower() for n in names}):
        raise ValueError('Duplicate Windows archive path')
    for name in names:
        if not name.startswith(ROOT) or '\\' in name or '..' in name.split('/') or ':' in name:
            raise ValueError('Invalid portable member path')
    actual = {name[len(ROOT):] for name in names
              if PurePosixPath(name).suffix.lower() in {'.dll', '.pyd', '.exe'}}
    report = json.loads(archive.read(ROOT + 'third-party-notices/inventory.json'))
    if report.get('kind') != 'build-license-evidence':
        raise ValueError('Invalid inventory')
    rows = {}
    for row in report['binaries']:
        path = row['path']
        if path in rows or path not in actual:
            raise ValueError('Invalid or duplicate binary inventory path')
        data = archive.read(ROOT + path)
        if len(data) != row['size'] or hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError('Binary evidence mismatch: ' + path)
        rows[path] = row
    if set(rows) != actual or 'ManoStudio.exe' not in rows:
        raise ValueError('Incomplete inventory')
    return rows


def compare(before, after):
    old, new = binary_inventory(before), binary_inventory(after)
    removed = sorted(set(old) - set(new))
    added = sorted(set(new) - set(old))
    changed = sorted(path for path in set(old) & set(new)
                     if old[path]['sha256'] != new[path]['sha256'])
    allowed = set(removed) == TARGETS and not added and set(changed) <= {'ManoStudio.exe'}
    return {'before_binaries': len(old), 'after_binaries': len(new),
            'removed': removed, 'removed_bytes': sum(old[path]['size'] for path in removed),
            'added': added, 'changed': changed,
            'unchanged': len(set(old) & set(new)) - len(changed),
            'expected_pdf_only_delta': allowed, 'public_release_approved': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before')
    parser.add_argument('after')
    args = parser.parse_args()
    with zipfile.ZipFile(args.before) as before, zipfile.ZipFile(args.after) as after:
        result = compare(before, after)
    print(json.dumps(result, indent=2))
    return 0 if result['expected_pdf_only_delta'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
