from itertools import product
import pytest
from databus_lab import Databus
from databus_file import save, load, snapshot, restore
from word_arithmetic import OPERATIONS


def expected(op, a, b, c):
    values = {"ADD": a+b, "ADC": a+b+c, "SUB": a-b,
              "INC": a+1, "DEC": a-1, "AND": a&b, "OR": a|b,
              "XOR": a^b, "NOT": ~a, "SHL": a<<1, "SHR": a>>1,
              "ASR": (a-16 if a&8 else a)>>1,
              "ROL": (a<<1)|(a>>3), "ROR": (a>>1)|((a&1)<<3),
              "CIL": (a<<1)|c, "CIR": (a>>1)|(c<<3)}
    return values[op]&15


@pytest.mark.parametrize("op", OPERATIONS)
def test_alu_transfer(op):
    for a,b,c in product(range(16),range(16),range(2)):
        m=Databus()
        m.tick(("EXT",),("AR",),9)
        m.tick(("EXT",),("R0",),a)
        m.tick(("EXT",),("R1",),b)
        word=expected(op,a,b,c)
        result=m.tick(("ALU",),("AR","R0","R1","RAM"),0,op,c)
        assert result.before==(9,a,b)
        assert result.after==(word,word,word)
        assert result.bus==f"{word:04b}"
        assert result.memory_write==(9,0,word)
        assert result.arithmetic.word==word
        assert result.arithmetic.negative==bool(word&8)
        assert result.arithmetic.zero==(word==0)
        assert m.memory.read(9)==word
        if op in ("ADD","ADC","SUB","INC","DEC"):
            sa=a-16 if a&8 else a
            sb=b-16 if b&8 else b
            signed={"ADD":sa+sb,"ADC":sa+sb+c,"SUB":sa-sb,"INC":sa+1,"DEC":sa-1}[op]
            assert result.arithmetic.overflow==not_in_range(signed)


def not_in_range(value):
    return not -8<=value<=7


def test_contention_atomic():
    m=Databus()
    m.tick(("EXT",),("R0",),7)
    m.tick(("EXT",),("R1",),1)
    assert m.preview(("ALU","R0"),0,"ADD").bits=="XXXX"
    before=snapshot(m,((),(),0))
    with pytest.raises(ValueError):
        m.tick(("ALU","EXT"),("RAM",),8,"ADD")
    assert snapshot(m,((),(),0))==before
    assert m.tick(("ALU","R0"),(),0,"ADD").arithmetic.word==8


@pytest.mark.parametrize("operation,carry",[("bad",0),("ADD",True),("ADD",2)])
def test_invalid_controls(operation,carry):
    m=Databus()
    before=snapshot(m,((),(),0))
    with pytest.raises(ValueError):
        m.tick(("ALU",),("RAM",),0,operation,carry)
    assert snapshot(m,((),(),0))==before


def test_checkpoint(tmp_path):
    m=Databus()
    m.tick(("EXT",),("R0",),7)
    m.tick(("EXT",),("R1",),1)
    for i in range(100):
        m.tick(("ALU",),("R0","RAM"),0,OPERATIONS[i%16],i%2)
    staged=(("ALU",),("R1",),0,"CIR",1)
    path=tmp_path/"alu.mano"
    save(path,m,staged)
    restored,controls=load(path)
    assert controls==staged
    assert restored.history==m.history
    assert snapshot(restored,controls)==snapshot(m,staged)
    assert restored.tick(*controls)==m.tick(*staged)


def test_legacy_controls():
    m,staged=restore({"registers":[0,1,2],"ram":[0]*16,"events":[],"controls":{"sources":["R0"],"destinations":["R1"],"external":0}})
    assert staged==(("R0",),("R1",),0)
    assert m.tick(*staged).after==(0,1,1)
