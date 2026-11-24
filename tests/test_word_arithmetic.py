import pytest
from word_arithmetic import alu,parse_word,representations,signed

@pytest.mark.parametrize("width",[4,8,12,16])
def test_representation(width):
    maxword=(1<<width)-1
    assert parse_word("-1",10,width)==maxword
    assert representations(maxword,width)["Signed"]=="-1"
    assert parse_word(representations(maxword,width)["HEX"],16,width)==maxword
    assert len(representations(maxword,width)["BIN"])==width

@pytest.mark.parametrize("text,base,width",[("2",2,4),("10000",16,16),("-9",10,4),("16",10,4),("0xFF",16,8)])
def test_invalid_word(text,base,width):
    with pytest.raises(ValueError):
        parse_word(text,base,width)

def test_exhaustive_four_bit_arithmetic():
    for a in range(16):
        for b in range(16):
            for op in ("ADD","SUB","ADC"):
                for cin in (0,1):
                    out=alu(op,a,b,4,cin)
                    total=a-b if op=="SUB" else a+b+(cin if op=="ADC" else 0)
                    signed_total=signed(a,4)-signed(b,4) if op=="SUB" else signed(a,4)+signed(b,4)+(cin if op=="ADC" else 0)
                    assert out.word==total%16
                    assert out.carry==int(total>=0 if op=="SUB" else total>=16)
                    assert out.overflow==not_in_range(signed_total)
                    assert len(out.stages)==4

def not_in_range(value):
    return not -8<=value<=7

@pytest.mark.parametrize("op,a,cin,word,carry",[
    ("CIL",0x8000,1,1,1),("CIR",1,1,0x8000,1),
    ("SHL",8,0,0,1),("ASR",8,0,12,0),("ROR",1,0,8,1)])
def test_shift(op,a,cin,word,carry):
    width=16 if op in ("CIL","CIR") else 4
    out=alu(op,a,width=width,carry_in=cin)
    assert (out.word,out.carry)==(word,carry)
