import pytest
from memory_organization import MemoryArray
from bus_model import resolve_bus,RegisterBus

@pytest.mark.parametrize("banks",[1,2,4])
@pytest.mark.parametrize("lanes",[1,2,4])
@pytest.mark.parametrize("bits",[4,8])
def test_bank_width_and_depth(banks,lanes,bits):
    m=MemoryArray(4,bits,banks,lanes)
    mask=(1<<m.width)-1
    for a in range(m.size):
        word=(a*0x13579BDF)&mask
        sel=m.write(a,word)
        assert sel.bank==a//16 and sel.local==a%16
        assert sel.cs_n.count(0)==1
        assert m.read(a)==word
        assert tuple(c.words[sel.local] for c in m.chips[sel.bank])==m.slices(word)
    assert all(m.read(a)==(a*0x13579BDF)&mask for a in range(m.size))
    assert m.read(0,False) is None
    old=m.read(0)
    m.write(0,mask,False)
    assert m.read(0)==old
    with pytest.raises(ValueError):m.write(0,mask+1)
    assert m.read(0)==old
    m.reset()
    assert all(m.read(a)==0 for a in range(m.size))

def test_bus_resolution():
    assert resolve_bus(4,[None,None]).bits=="ZZZZ"
    assert resolve_bus(4,[None,5]).word==5
    assert resolve_bus(4,[5,5]).bits=="0101"
    assert resolve_bus(4,[5,6]).bits=="01XX"
    assert resolve_bus(4,[5,6]).contention

def test_register_transfer_atomic():
    bus=RegisterBus(8)
    bus.set_word(0,0xA5);bus.set_word(1,0x33)
    assert bus.transfer([True,False,False],[False,True,True]).word==0xA5
    assert bus.registers==[0xA5]*3
    for en in ([False]*3,[True,True,False]):
        with pytest.raises(ValueError):bus.transfer(en,[True]*3)
        assert bus.registers==[0xA5]*3
