"""Verify exact upstream Qt license texts in an internal portable archive."""
import argparse
import hashlib
import json
import zipfile

PREFIX = 'ManoStudio/third-party-notices/qt-license-texts/'
EXPECTED = {
    'LGPL-3.0-only.txt': '65c5ca88a67c30becee01c5a8816d964b03862f9',
    'GPL-3.0-only.txt': '94a9ed024d3859793618152ea559a168bbcbb5e2',
}


def git_blob(data):
    normalized = data.replace(b'\r\n', b'\n')
    return hashlib.sha1(b'blob ' + str(len(normalized)).encode('ascii') + b'\0' + normalized).hexdigest()


def audit(archive, expected=EXPECTED):
    names = archive.namelist()
    if len(names) != len(set(names)) or len(names) != len({n.lower() for n in names}):
        raise ValueError('Duplicate Windows archive path')
    rows = []
    for name, digest in sorted(expected.items()):
        member = PREFIX + name
        actual = None
        if member in names:
            if archive.getinfo(member).file_size > 100_000:
                raise ValueError('Oversized license text')
            actual = git_blob(archive.read(member))
        rows.append({'path': member, 'expected_git_blob': digest,
                     'actual_git_blob': actual, 'matches': actual == digest})
    return {'texts_match': bool(rows) and all(row['matches'] for row in rows),
            'texts': rows, 'corresponding_source_verified': False,
            'public_release_approved': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('portable_zip')
    args = parser.parse_args()
    with zipfile.ZipFile(args.portable_zip) as archive:
        result = audit(archive)
    print(json.dumps(result, indent=2))
    return 0 if result['texts_match'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
