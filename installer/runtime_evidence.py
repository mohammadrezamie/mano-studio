"""Offline runtime evidence for internal Windows builds; never approves release."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import ssl
import sys
import zipfile

MINIMUM = (3, 5, 10)  # OpenSSL 3.5 advisory baseline, 2026-11-24.
VERSION = re.compile(rb'OpenSSL ([0-9]+)\.([0-9]+)\.([0-9]+)(?![0-9])')


def scan(archive, python_version, runtime_version):
    rows, flags = [], []
    names = archive.namelist()
    if len(names) != len(set(names)):
        raise ValueError('Duplicate archive member')
    for name in sorted(names):
        base = PurePosixPath(name).name.lower()
        if not re.fullmatch(r'lib(?:ssl|crypto)[-\w]*\.dll', base):
            continue
        data = archive.read(name)
        versions = sorted({tuple(map(int, match.groups())) for match in VERSION.finditer(data)})
        rows.append({'path': name, 'sha256': hashlib.sha256(data).hexdigest(),
                     'embedded_versions': versions})
        # libssl can lack a version string; its actual crypto dependency needs review.
        if base.startswith('libcrypto') and len(versions) != 1:
            flags.append({'code': 'unknown-crypto-version', 'path': name})
        if any(v[:2] != MINIMUM[:2] or v < MINIMUM for v in versions):
            flags.append({'code': 'crypto-version-review', 'path': name})
    if not any(PurePosixPath(row['path']).name.lower().startswith('libcrypto') for row in rows):
        flags.append({'code': 'missing-crypto-evidence'})
    if tuple(runtime_version[:2]) != MINIMUM[:2] or tuple(runtime_version[:3]) < MINIMUM:
        flags.append({'code': 'build-ssl-version-review'})
    return {'kind': 'runtime-evidence', 'python_version': python_version,
            'build_ssl_version': list(runtime_version[:3]), 'minimum_review_baseline': list(MINIMUM),
            'binaries': rows, 'flags': flags, 'public_release_approved': False,
            'manual_review_required': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('portable_zip', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    with zipfile.ZipFile(args.portable_zip) as archive:
        report = scan(archive, sys.version.split()[0], ssl.OPENSSL_VERSION_INFO)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f"Runtime review: {len(report['flags'])} flags; public release not approved.")


if __name__ == '__main__':
    main()
