import io
import hashlib
import json
import zipfile
import pytest
from candidate_artifacts import index, verify

SHA = 'a' * 40


def archive(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        for name, data in files.items():
            z.writestr(name, data)
    return buf.getvalue()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pair(change=None):
    prefix = 'ManoStudio/'
    binary, source = b'binary', b'python source'
    inv = {'binaries': [{'path': 'app.exe', 'size': len(binary), 'sha256': digest(binary)}]}
    inner = {prefix + 'app.exe': binary, prefix + 'rtl_translator.py': source,
             prefix + 'third-party-notices/inventory.json': json.dumps(inv)}
    if change == 'binary':
        inner[prefix + 'app.exe'] = b'corrupt'
    if change == 'source':
        inner[prefix + 'rtl_translator.py'] = b'changed'
    if change == 'extra':
        inner[prefix + 'other.dll'] = b'extra'
    zdata = archive(inner)
    ename, zname = 'ManoStudio-Setup-v1.0.0-x64.exe', 'ManoStudio-v1.0.0-Windows-x64.zip'
    exe = b'setup'
    manifest = {'kind': 'internal-development-candidate', 'version': '1.0.0', 'source_sha': SHA,
                'native_acceptance': False, 'public_release': False,
                'portable_smoke': 'PASS', 'installed_smoke': 'PASS',
                'academic_source_sha256': digest(source),
                'assets': [{'name': n, 'size': len(d), 'sha256': digest(d)} for n, d in [(ename, exe), (zname, zdata)]]}
    common = {'commit.txt': 'SHA=' + SHA, 'portable-smoke.txt': 'PASS'}
    s = dict(common, **{ename: exe, ename + '.sha256': digest(exe), 'installed-smoke.txt': 'PASS'})
    p = dict(common, **{zname: zdata, zname + '.sha256': digest(zdata)})
    if change == 'smoke':
        s['installed-smoke.txt'] = 'FAIL'
    if change == 'approval':
        manifest['public_release'] = True
    if change == 'asset':
        s[ename] = b'bad'
    if change == 'checksum':
        p[zname + '.sha256'] = 'bad'
    s['candidate-manifest.json'] = json.dumps(manifest)
    return zipfile.ZipFile(io.BytesIO(archive(s))), zipfile.ZipFile(io.BytesIO(archive(p)))


def test_valid():
    with pair()[0] as s, pair()[1] as p:
        result = verify(s, p, SHA)
        assert result['binary_count'] == 1 and result['integrity_verified']
        assert result['public_release_approved'] is False


@pytest.mark.parametrize('change', ['binary', 'source', 'extra', 'smoke', 'approval', 'asset', 'checksum'])
def test_mismatch(change):
    s, p = pair(change)
    with s, p, pytest.raises(ValueError):
        verify(s, p, SHA)


@pytest.mark.parametrize('names', [['foo', 'FOO'], ['../x'], ['/x'], ['dir/CON.txt'], ['x.'], ['x '], ['a:b'], ['a\\b']])
def test_bad_windows_paths(names):
    with zipfile.ZipFile(io.BytesIO(archive(dict.fromkeys(names, b'x')))) as z:
        with pytest.raises(ValueError):
            index(z)
