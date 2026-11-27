"""Validate pip's Windows build report as evidence, not a signature or license grant."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlsplit


def canonical(name):
    return re.sub(r'[-_.]+', '-', name).lower()


def pins(path):
    result = {}
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        name, version = line.split('==', 1)
        key = canonical(name)
        if key in result or not version:
            raise ValueError('Invalid or duplicate constraint: ' + line)
        result[key] = version
    return result


REQUIRED = {'pyside6', 'pyside6-essentials', 'pyside6-addons', 'shiboken6',
            'pyinstaller', 'pyinstaller-hooks-contrib', 'pefile', 'pytest'}


def validate(report, expected):
    if report.get('version') != '1' or not isinstance(report.get('install'), list):
        raise ValueError('Unsupported pip report')
    verified = {}
    for row in report['install']:
        metadata = row['metadata']
        name = canonical(metadata['name'])
        version = metadata['version']
        if name in verified or expected.get(name) != version:
            raise ValueError('Unpinned, mismatched or duplicate dependency: ' + name)
        download = row['download_info']
        url = urlsplit(download['url'])
        if (url.scheme != 'https' or url.netloc != 'files.pythonhosted.org'
                or url.query or url.fragment or not url.path.endswith('.whl')):
            raise ValueError('Unexpected wheel origin: ' + name)
        sha = download.get('archive_info', {}).get('hashes', {}).get('sha256', '')
        if not re.fullmatch(r'[a-f0-9]{64}', sha):
            raise ValueError('Missing wheel SHA-256: ' + name)
        verified[name] = {'version': version, 'url': download['url'], 'sha256': sha}
    missing = REQUIRED - set(verified)
    if missing:
        raise ValueError('Missing required dependencies: ' + ', '.join(sorted(missing)))
    return {'kind': 'pip-wheel-download-evidence', 'packages': verified,
            'independent_authenticity_verified': False, 'redistribution_approved': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('constraints', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    data = validate(json.loads(args.report.read_text(encoding='utf-8-sig')), pins(args.constraints))
    args.output.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    print(f"Recorded {len(data['packages'])} pinned wheel origins and digests; review still required.")


if __name__ == '__main__':
    main()
