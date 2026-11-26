import hashlib
import io
import json
import zipfile

import pytest
from compare_payloads import ROOT, TARGETS, compare


def archive(files, corrupt=False):
    stream = io.BytesIO()
    rows = [{'path': path, 'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
            for path, data in files.items()]
    if corrupt:
        rows[0]['sha256'] = 'bad'
    with zipfile.ZipFile(stream, 'w') as z:
        for path, data in files.items():
            z.writestr(ROOT + path, data)
        z.writestr(ROOT + 'third-party-notices/inventory.json', json.dumps({
            'kind': 'build-license-evidence', 'binaries': rows}))
    return zipfile.ZipFile(stream)


KEEP = {'ManoStudio.exe': b'exe', '_internal/Qt6Core.dll': b'core'}
BEFORE = dict(KEEP, **{p: b'pdf' for p in TARGETS})


def test_expected_delta():
    with archive(BEFORE) as a, archive(dict(KEEP, **{'ManoStudio.exe': b'new'})) as b:
        result = compare(a, b)
    assert result['expected_pdf_only_delta'] and result['removed_bytes'] == 6
    assert result['unchanged'] == 1 and not result['public_release_approved']


@pytest.mark.parametrize('after', [BEFORE, {'ManoStudio.exe': b'exe'},
                                   dict(KEEP, **{'_internal/Qt6Core.dll': b'changed'}),
                                   dict(KEEP, **{'extra.dll': b'new'})])
def test_unexpected_delta(after):
    with archive(BEFORE) as a, archive(after) as b:
        assert not compare(a, b)['expected_pdf_only_delta']


def test_invalid_evidence():
    with archive(BEFORE) as a, archive(KEEP, corrupt=True) as b:
        with pytest.raises(ValueError, match='evidence mismatch'):
            compare(a, b)
