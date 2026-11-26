import io
import zipfile
import pytest
from license_bundle import audit, git_blob, PREFIX


def inspect(rows):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        for name, data in rows:
            z.writestr(name, data)
    with zipfile.ZipFile(buf) as z:
        return audit(z, {'sample.txt': git_blob(b'line\n')})


@pytest.mark.parametrize('data', [b'line\n', b'line\r\n'])
def test_exact(data):
    result = inspect([(PREFIX + 'sample.txt', data)])
    assert result['texts_match'] and not result['public_release_approved']
    assert not result['corresponding_source_verified']


@pytest.mark.parametrize('data', [b'changed\n', b'line', b'\xef\xbb\xbfline\n'])
def test_modified(data):
    assert not inspect([(PREFIX + 'sample.txt', data)])['texts_match']


def test_missing():
    assert not inspect([])['texts_match']


def test_case_duplicate():
    with pytest.raises(ValueError):
        inspect([(PREFIX + 'sample.txt', b'line\n'), (PREFIX + 'Sample.txt', b'line\n')])


def test_oversized():
    with pytest.raises(ValueError):
        inspect([(PREFIX + 'sample.txt', b'x' * 100001)])
