from itertools import product
import pytest
from memory_model import MemoryChip
from data_codes import *

@pytest.mark.parametrize("kind",["RAM","ROM"])
@pytest.mark.parametrize("ab,wb",[(4,4),(4,8),(8,8)])
def test_memory_controls(kind,ab,wb):
    m=MemoryChip(kind,ab,wb)
    for a in (0,1,m.size-1):
        for cs,oe,we in product((0,1),repeat=3):
            before=m.words[a]
            access=m.access(a,cs,oe,we,m.mask)
            expected="DISABLED" if cs else "WRITE" if kind=="RAM" and not we else "READ" if not oe else "IDLE"
            assert access.operation==expected
            assert access.after==(m.mask if expected=="WRITE" else before)
            assert access.output==(before if expected=="READ" else None)
    if kind=="ROM":assert m.words==m.initial
    m.reset()
    assert m.words==m.initial

def test_ram_address_isolation():
    m=MemoryChip()
    m.access(5,0,0,0,0xAB)
    assert m.output(5)==0xAB and m.output(4)==0
    assert m.output(5,1)==None
    with pytest.raises(ValueError):m.access(16)
    with pytest.raises(ValueError):m.access(0,data=256)
    assert m.words[5]==0xAB

def test_bcd():
    for n in range(1000):
        text=f"{n:03}"
        assert bcd_decode(bcd_encode(text))==text
    for code in ("1010","1111","001"):
        with pytest.raises(ValueError):bcd_decode(code)

def test_gray_all_8_bit_words():
    values=[binary_to_gray(f"{n:08b}") for n in range(256)]
    for n,g in enumerate(values):
        assert gray_to_binary(g)==f"{n:08b}"
        if n:assert (int(g,2)^int(values[n-1],2)).bit_count()==1

def test_ascii_all_characters():
    for n in range(128):assert ascii_decode(ascii_encode(chr(n)))==chr(n)
    with pytest.raises(ValueError):ascii_encode("مانو")

def test_hamming_all_single_bit_errors():
    for n in range(16):
        data=f"{n:04b}"
        code=hamming_encode(data)
        assert hamming_decode(code).syndrome==0
        for i in range(7):
            bad=code[:i]+str(1-int(code[i]))+code[i+1:]
            result=hamming_decode(bad)
            assert (result.syndrome,result.corrected,result.data)==(i+1,code,data)
