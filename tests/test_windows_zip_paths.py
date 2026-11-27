import io
import stat
import warnings
import zipfile

import pytest
from installer.windows_zip_paths import validate_windows_paths


@pytest.mark.parametrize('paths', [
    ['ManoStudio/a.dll', 'ManoStudio/A.DLL'],
    ['ManoStudio/lib/a.dll', 'ManoStudio/LIB/b.dll'],
    ['ManoStudio/lib', 'ManoStudio/lib/a.dll'],
    ['ManoStudio/lib/a.dll', 'ManoStudio/lib'],
    ['ManoStudio/a.dll', 'ManoStudio/a.dll/'],
    ['ManoStudio/a.dll', 'ManoStudio/a.dll'],
    ['ManoStudio/lib//a.dll'],
    ['ManoStudio/../a.dll'],
    ['ManoStudio/./a.dll'],
    ['ManoStudio/a.dll.'],
    ['ManoStudio/a.dll '],
    ['ManoStudio/a.dll:stream'],
    ['ManoStudio/lib\\a.dll'],
    ['ManoStudio/NUL.txt'],
    ['ManoStudio/COM¹.dll'],
    ['ManoStudio/LPT1 .dll'],
    ['ManoStudio/bad?.dll'],
    ['ManoStudio/bad\x01.dll'],
    ['Other/a.dll'],
])
def test_reject_windows_aliases_and_unsafe_paths(paths):
    b = io.BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        with zipfile.ZipFile(b, 'w') as archive:
            for path in paths:
                archive.writestr(path.replace(chr(92), '/'), b'')
    # zipfile normalizes backslashes when writing on Windows. Inject the
    # raw filename into both ZIP headers after writing a same-length name.
    raw = b.getvalue()
    for path in paths:
        if chr(92) in path:
            canonical = path.replace(chr(92), '/').encode('utf-8')
            assert raw.count(canonical) == 2
            raw = raw.replace(canonical, path.encode('utf-8'))
    with zipfile.ZipFile(io.BytesIO(raw)) as archive, pytest.raises(ValueError):
        validate_windows_paths(archive, 'ManoStudio/')


@pytest.mark.parametrize('mode', [stat.S_IFLNK, stat.S_IFIFO, stat.S_IFCHR])
def test_reject_special_files(mode):
    b = io.BytesIO()
    entry = zipfile.ZipInfo('ManoStudio/file')
    entry.create_system = 3
    entry.external_attr = (mode | 0o777) << 16
    with zipfile.ZipFile(b, 'w') as archive:
        archive.writestr(entry, 'target')
    with zipfile.ZipFile(b) as archive, pytest.raises(ValueError):
        validate_windows_paths(archive, 'ManoStudio/')


def test_valid_archive_with_explicit_and_implicit_parents():
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w') as archive:
        for path in ('ManoStudio/lib/a.dll', 'ManoStudio/', 'ManoStudio/lib/',
                     'ManoStudio/lib/b.dll', 'ManoStudio/نمونه.txt'):
            archive.writestr(path, b'')
    with zipfile.ZipFile(b) as archive:
        validate_windows_paths(archive, 'ManoStudio/')


def test_public_distribution_audit_calls_path_gate_before_inventory():
    from installer.redistribution_gate import audit
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w') as archive:
        archive.writestr('ManoStudio/a.dll', b'1')
        archive.writestr('ManoStudio/A.dll', b'2')
    with zipfile.ZipFile(b) as archive, pytest.raises(ValueError, match='Ambiguous'):
        audit(archive)
