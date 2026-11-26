import csv
import io
import pytest
import memory_export


@pytest.mark.parametrize('word,signed', [(0, 0), (32767, 32767), (32768, -32768), (65535, -1)])
def test_word_formats(word, signed):
    memory = [0] * 4096
    memory[4095] = word
    rows = list(csv.DictReader(io.StringIO(memory_export.render(memory, {4095}))))
    assert rows == [{'address_hex': 'FFF', 'word_hex': f'{word:04X}',
                     'unsigned_decimal': str(word), 'signed_decimal': str(signed),
                     'binary': f'{word:016b}'}]


def test_visible_page_and_no_mutation():
    memory = [0] * 4096
    known = {0, 0xFFF}
    memory[0xAB1] = 123
    before = memory.copy()
    rows = list(csv.DictReader(io.StringIO(memory_export.render(memory, known, 0xAB1))))
    assert len(rows) == 18 and rows[0]['address_hex'] == '000'
    assert rows[-1]['address_hex'] == 'FFF'
    assert next(r for r in rows if r['address_hex'] == 'AB1')['word_hex'] == '007B'
    assert memory == before and known == {0, 0xFFF}


@pytest.mark.parametrize('word', [-1, 65536, True, '0000'])
def test_invalid_word_preserves_destination(tmp_path, word):
    memory = [0] * 4096
    memory[0] = word
    path = tmp_path / 'memory.csv'
    path.write_bytes(b'old')
    with pytest.raises(ValueError):
        memory_export.save(path, memory, {0})
    assert path.read_bytes() == b'old'


def test_atomic_save_and_wrong_extension(tmp_path):
    path = tmp_path / 'memory.CSV'
    memory_export.save(path, [0] * 4096, {0})
    assert path.read_bytes().startswith(b'\xef\xbb\xbfaddress_hex,')
    with pytest.raises(ValueError):
        memory_export.save(tmp_path / 'memory.txt', [0] * 4096, {0})
    assert set(tmp_path.iterdir()) == {path}


def test_replace_failure_keeps_destination(tmp_path, monkeypatch):
    path = tmp_path / 'memory.csv'
    path.write_bytes(b'old')
    def fail(*args):
        raise OSError('cannot replace')
    monkeypatch.setattr(memory_export.os, 'replace', fail)
    with pytest.raises(OSError):
        memory_export.save(path, [0] * 4096, {0})
    assert path.read_bytes() == b'old'
    assert set(tmp_path.iterdir()) == {path}
