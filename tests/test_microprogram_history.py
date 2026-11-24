import pytest
from microprogram import MicroComputer,Microinstruction
from microassembler import full_demo
from microprogram_history import MicroHistory


def test_reverse_full_demo():
    control,memory=full_demo()
    c=MicroComputer(control,memory)
    initial=c.registers(),dict(c.memory)
    h=MicroHistory(c)
    events=[]
    for _ in range(6+8+7+6):
        if c.car==64 and c.pc==0x106:break
        events.append(h.step())
    assert c.memory!=initial[1]
    for event in reversed(events):
        assert h.back()==event
        assert c.registers()==event.before
    assert (c.registers(),c.memory)==initial and h.steps==0 and h.back() is None
    for event in events:assert h.step()==event


@pytest.mark.parametrize("present",[True,False])
def test_sparse_memory_presence(present):
    c=MicroComputer({64:Microinstruction(7,0,0,0,0,64).encode()},
                    {0:0} if present else {})
    h=MicroHistory(c)
    c.dr=4
    h.step()
    assert c.memory[0]==4
    h.back()
    assert c.memory==({0:0} if present else {})


@pytest.mark.parametrize("br,cd,expected",[(0,0,"AD"),(0,3,"CAR+1"),(1,0,"AD"),(2,0,"SBR"),(3,0,"MAP")])
def test_address_candidates(br,cd,expected):
    c=MicroComputer({64:Microinstruction(0,0,0,cd,br,9).encode()})
    c.ac,c.dr,c.sbr=1,0xA800,22
    e=c.step()
    assert dict(e.address_candidates)=={"CAR+1":65,"AD":9,"SBR":22,"MAP":20}
    assert e.next_source==expected and e.after["CAR"]==dict(e.address_candidates)[expected]


def test_capacity_and_failed_step():
    c=MicroComputer({64:Microinstruction(3,0,0,0,0,64).encode()})
    h=MicroHistory(c,2)
    for _ in range(3):h.step()
    assert h.steps==3 and len(h.entries)==2
    h.back();h.back()
    assert h.steps==1 and c.ac==1 and h.back() is None
    c.control.clear()
    with pytest.raises(ValueError):h.step()
    assert h.steps==1 and not h.entries
