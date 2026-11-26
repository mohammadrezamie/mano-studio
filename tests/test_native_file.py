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
