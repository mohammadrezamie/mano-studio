import json
import pytest
from mano_file import encode, decode, load, save, MAX_BYTES


@pytest.mark.parametrize('kind,payload', [('rtl','AC ← 0\nآزمایش'),('asm','CLA\nHLT'),('circuit',{'format':'mano-logic','version':2})])
def test_roundtrip(tmp_path,kind,payload):
    path=tmp_path/'sample.mano'
    save(path,kind,payload)
    assert load(path)==(kind,payload)
    assert decode(encode(kind,payload))==(kind,payload)


@pytest.mark.parametrize('text', ['{}','[]','{"format":"mano-studio","version":true,"kind":"rtl","payload":"x"}',
    '{"format":"mano-studio","version":2,"kind":"rtl","payload":"x"}',
    '{"format":"mano-studio","version":1,"kind":"bad","payload":"x"}',
    '{"format":"mano-studio","version":1,"kind":"rtl","payload":3}',
    '{"format":"mano-studio","version":1,"kind":"rtl","payload":"x","payload":"y"}'])
def test_invalid(text):
    with pytest.raises(ValueError):
        decode(text)


def test_failed_save_keeps_existing(tmp_path):
    path=tmp_path/'sample.mano'
    save(path,'rtl','original')
    with pytest.raises(ValueError):
        save(path,'rtl','x'*MAX_BYTES)
    assert load(path)==('rtl','original')
    assert list(tmp_path.iterdir())==[path]


def test_oversize_read(tmp_path):
    path=tmp_path/'sample.mano'
    path.write_bytes(b'x'*(MAX_BYTES+1))
    with pytest.raises(ValueError):
        load(path)


@pytest.mark.parametrize('key', [1, True, None, 1.5, (1,)])
def test_no_lossy_nested_keys(tmp_path, key):
    path = tmp_path / 'safe.mano'
    save(path, 'rtl', 'AC ← 0')
    with pytest.raises(ValueError, match='keys must be text'):
        save(path, 'circuit', {'blocks': [{key: 'bad'}]})
    assert load(path) == ('rtl', 'AC ← 0')
    assert list(tmp_path.iterdir()) == [path]


def test_duplicate_after_key_coercion():
    with pytest.raises(ValueError):
        encode('circuit', {1: 'number', '1': 'text'})


@pytest.mark.parametrize('kind', [[], {}, None, 1])
def test_invalid_kind(kind):
    with pytest.raises(ValueError):
        encode(kind, {})


def test_cycle():
    payload = {}
    payload['self'] = payload
    with pytest.raises(ValueError, match='nesting too deep'):
        encode('circuit', payload)


def test_excessive_depth_on_read_and_write():
    payload = 'x'
    for _ in range(70):
        payload = [payload]
    payload = {'blocks': payload}
    with pytest.raises(ValueError, match='nesting too deep'):
        encode('circuit', payload)
    with pytest.raises(ValueError, match='nesting too deep'):
        decode(json.dumps({'format': 'mano-studio', 'version': 1,
                           'kind': 'circuit', 'payload': payload}))


@pytest.mark.parametrize('value', [object(), b'x', {1, 2}, '\ud800'])
def test_invalid_value(value):
    with pytest.raises(ValueError):
        encode('circuit', {'x': value})


def test_bilingual_and_tuple_compatibility():
    payload = {'نام': 'آزمایش ←', 'pins': (1, 2), 'items': [{'1': True}]}
    assert decode(encode('circuit', payload)) == ('circuit', {
        'نام': 'آزمایش ←', 'pins': [1, 2], 'items': [{'1': True}]})


def test_shared_graph_expansion_is_bounded(monkeypatch):
    import mano_file
    monkeypatch.setattr(mano_file, 'MAX_BYTES', 2048)
    node = ['x']
    for _ in range(40):
        node = [node, node]
    with pytest.raises(ValueError, match='too large'):
        encode('circuit', {'nodes': node})


def test_exact_utf8_limit(monkeypatch):
    import mano_file
    payload = 'آزمایش ←\n' * 20
    text = encode('rtl', payload)
    size = len(text.encode('utf-8'))
    monkeypatch.setattr(mano_file, 'MAX_BYTES', size)
    assert encode('rtl', payload) == text
    monkeypatch.setattr(mano_file, 'MAX_BYTES', size - 1)
    with pytest.raises(ValueError, match='too large'):
        encode('rtl', payload)


def test_indentation_and_escaping_count_against_limit(monkeypatch, tmp_path):
    import mano_file
    path = tmp_path / 'safe.mano'
    save(path, 'rtl', 'original')
    monkeypatch.setattr(mano_file, 'MAX_BYTES', 200)
    with pytest.raises(ValueError, match='too large'):
        save(path, 'circuit', {'items': ['\n'] * 40})
    assert load(path) == ('rtl', 'original')
    assert list(tmp_path.iterdir()) == [path]


def test_serialization_format_unchanged():
    payload = {'نام': 'آزمایش ←', 'pins': (1, 2), 'items': [{'1': True}]}
    expected = json.dumps({'format': 'mano-studio', 'version': 1,
                           'kind': 'circuit', 'payload': payload},
                          ensure_ascii=False, allow_nan=False, indent=2) + '\n'
    assert encode('circuit', payload) == expected
