import math
import random
import struct
from fractions import Fraction
import pytest
from floating_arithmetic import decode_half, encode_half, float_alu


def test_all_binary16_encodings():
    for word in range(65536):
        value=decode_half(word)
        ref=struct.unpack(">e",word.to_bytes(2,"big"))[0]
        if math.isnan(ref):
            assert value.kind=="nan"
        elif math.isinf(ref):
            assert value.kind=="infinity"
        else:
            assert value.value==Fraction(ref)
            assert encode_half(value.value,value.sign).word==word


@pytest.mark.parametrize("value,expected",[(Fraction(2049,2048),0x3C00),
    (Fraction(2051,2048),0x3C02),(Fraction(1,2**25),0),
    (Fraction(3,2**25),2),(Fraction(-1,2**25),0x8000),
    (Fraction(2047,2**25),0x0400),(Fraction(65519),0x7BFF),
    (Fraction(65520),0x7C00)])
def test_rounding_boundaries(value,expected):
    assert encode_half(value).word==expected


@pytest.mark.parametrize("op",["ADD","SUB","MUL","DIV"])
def test_finite_operations_against_struct(op):
    rng=random.Random(410)
    for _ in range(3500):
        aw,bw=(rng.randrange(65536) for _ in range(2))
        a,b=(struct.unpack(">e",w.to_bytes(2,"big"))[0] for w in (aw,bw))
        if not math.isfinite(a) or not math.isfinite(b) or (op=="DIV" and b==0):
            continue
        v={"ADD":lambda:a+b,"SUB":lambda:a-b,"MUL":lambda:a*b,"DIV":lambda:a/b}[op]()
        try:
            expected=int.from_bytes(struct.pack(">e",v),"big")
        except OverflowError:
            expected=0xFC00 if v<0 else 0x7C00
        assert float_alu(op,aw,bw).word==expected


@pytest.mark.parametrize("op,a,b,expected,status",[
    ("ADD",0x7C00,0xFC00,0x7E00,"invalid"),
    ("SUB",0x7C00,0x7C00,0x7E00,"invalid"),
    ("MUL",0,0x7C00,0x7E00,"invalid"),
    ("DIV",0,0,0x7E00,"invalid"),
    ("DIV",0xBC00,0,0xFC00,"divide by zero"),
    ("DIV",0x3C00,0xFC00,0x8000,"exact"),
    ("ADD",0x8000,0x8000,0x8000,"exact"),
    ("ADD",0x3C00,0xBC00,0,"exact"),
    ("MUL",0x8000,0xBC00,0,"exact"),
    ("ADD",0x7D00,0x3C00,0x7E00,"nan")])
def test_special(op,a,b,expected,status):
    r=float_alu(op,a,b)
    assert (r.word,r.status)==(expected,status)


def test_reject_invalid():
    with pytest.raises(ValueError):
        decode_half(65536)
    with pytest.raises(ValueError):
        float_alu("NOP",0,0)
