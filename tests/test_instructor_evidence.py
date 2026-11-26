import hashlib
import pytest
from instructor_evidence import expected_captures, validate


def inspect(root, name):
    payload = (root / name).read_bytes()
    w, h = map(int, payload.decode().split(','))
    return w, h, hashlib.sha256(payload).hexdigest()


@pytest.fixture
def captures(tmp_path):
    rows = []
    for name, size in expected_captures().items():
        w, h = size or (500, 300)
        (tmp_path / name).write_text(f'{w},{h}')
        width, height, sha = inspect(tmp_path, name)
        rows.append(dict(image=name, width=width, height=height, sha256=sha))
    return tmp_path, rows


def test_exact_matrix(captures):
    root, rows = captures
    assert len(expected_captures()) == 48
    assert validate(root, rows, inspect) == 48


@pytest.mark.parametrize('defect', ['missing', 'duplicate', 'wrong-name', 'hash', 'extra-file', 'oversize'])
def test_reject_incomplete_or_inaccurate_evidence(captures, defect):
    root, rows = captures
    if defect == 'missing':
        rows.pop()
    elif defect == 'duplicate':
        rows.append(rows[0])
    elif defect == 'wrong-name':
        rows[0]['image'] = '../wrong.png'
    elif defect == 'hash':
        rows[0]['sha256'] = 'bad'
    elif defect == 'extra-file':
        (root / 'stale.png').write_text('old')
    elif defect == 'oversize':
        row = next(r for r in rows if r['image'].endswith('workspace-1024.png'))
        (root / row['image']).write_text('1100,768')
        row['width'], row['height'], row['sha256'] = inspect(root, row['image'])
    with pytest.raises(ValueError):
        validate(root, rows, inspect)
