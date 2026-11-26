"""Read-only cross-check of downloaded Setup and portable Actions artifacts."""
import argparse
import hashlib
import json
import re
import tempfile
import zipfile
from pathlib import PurePosixPath


def require(condition, message):
    if not condition:
        raise ValueError(message)


def index(archive):
    names = archive.namelist()
    require(len(names) == len(set(n.casefold() for n in names)), 'Duplicate Windows path')
    for name in names:
        parts = name.rstrip('/').split('/')
        require(all(p and p not in ('.', '..') and not p.endswith((' ', '.'))
                    and not re.search(r'[\\:<>"|?*\x00-\x1f]', p)
                    and not re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])', p.split('.')[0])
                    for p in parts), 'Unsafe Windows path: ' + name)
    return set(names)


def read_json(archive, name):
    return json.loads(archive.read(name).decode('utf-8-sig'))


def check_text(archive, name, expected):
    require(archive.read(name).decode('utf-8-sig').strip() == expected, 'Wrong ' + name)


def hash_member(archive, name, destination=None):
    h = hashlib.sha256()
    size = 0
    with archive.open(name) as source:
        while block := source.read(1024 * 1024):
            h.update(block)
            size += len(block)
            if destination is not None:
                destination.write(block)
    return size, h.hexdigest()


def verify(setup, portable, sha):
    require(re.fullmatch(r'[0-9a-f]{40}', sha), 'Invalid expected source SHA')
    index(setup)
    index(portable)
    manifest = read_json(setup, 'candidate-manifest.json')
    require(manifest['source_sha'] == sha and manifest['kind'] == 'internal-development-candidate', 'Wrong manifest source or kind')
    require(manifest['native_acceptance'] is False and manifest['public_release'] is False, 'Unexpected approval claim')
    for archive in (setup, portable):
        check_text(archive, 'commit.txt', 'SHA=' + sha)
        check_text(archive, 'portable-smoke.txt', 'PASS')
    check_text(setup, 'installed-smoke.txt', 'PASS')
    require(manifest['portable_smoke'] == manifest['installed_smoke'] == 'PASS', 'Wrong manifest smoke status')
    version = manifest['version']
    zname = f'ManoStudio-v{version}-Windows-x64.zip'
    ename = f'ManoStudio-Setup-v{version}-x64.exe'
    assets = {x['name']: x for x in manifest['assets']}
    require(len(manifest['assets']) == 2 and set(assets) == {zname, ename}, 'Wrong asset set')
    with tempfile.TemporaryFile() as staged:
        for archive, name, dest in ((setup, ename, None), (portable, zname, staged)):
            size, digest = hash_member(archive, name, dest)
            require((size, digest) == (assets[name]['size'], assets[name]['sha256']), 'Asset mismatch: ' + name)
            checksum = archive.read(name + '.sha256').decode('utf-8-sig').split()
            require(checksum in ([digest], [digest, name]), 'Checksum mismatch: ' + name)
        staged.seek(0)
        with zipfile.ZipFile(staged) as inner:
            names = index(inner)
            prefix = 'ManoStudio/'
            require(all(n.startswith(prefix) for n in names), 'Unexpected portable root')
            require(inner.testzip() is None, 'Portable CRC failure')
            inventory = read_json(inner, prefix + 'third-party-notices/inventory.json')
            binaries = {x['path']: x for x in inventory['binaries']}
            actual = {n[len(prefix):] for n in names if PurePosixPath(n).suffix.lower() in ('.exe', '.dll', '.pyd')}
            require(len(binaries) == len(inventory['binaries']) and set(binaries) == actual, 'Incomplete binary inventory')
            for path, item in binaries.items():
                require(hash_member(inner, prefix + path) == (item['size'], item['sha256']), 'Binary mismatch: ' + path)
            sources = names & {prefix + 'rtl_translator.py', prefix + '_internal/rtl_translator.py'}
            require(len(sources) == 1 and hash_member(inner, next(iter(sources)))[1] == manifest['academic_source_sha256'], 'Academic source mismatch')
    return {'source_sha': sha, 'assets': assets, 'binary_count': len(binaries),
            'smoke_reports': 'PASS', 'integrity_verified': True,
            'native_acceptance': False, 'public_release_approved': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('setup_artifact')
    parser.add_argument('portable_artifact')
    parser.add_argument('source_sha')
    args = parser.parse_args()
    with zipfile.ZipFile(args.setup_artifact) as setup, zipfile.ZipFile(args.portable_artifact) as portable:
        print(json.dumps(verify(setup, portable, args.source_sha), indent=2))


if __name__ == '__main__':
    main()
