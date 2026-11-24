import pytest
from sequential_logic import ClockedCircuit


def test_d_rising_edge_only():
    m=ClockedCircuit("D")
    m.set_input("D",1)
    assert m.value==0
    m.set_clock(1)
    assert m.value==1
    m.set_input("D",0)
    m.set_clock(1)
    m.set_clock(0)
    assert m.value==1
    m.set_clock(1)
    assert m.value==0


@pytest.mark.parametrize("kind,inputs", [("JK",("J","K")),("T",("T",))])
def test_toggle(kind,inputs):
    m=ClockedCircuit(kind)
    for p in inputs:
        m.set_input(p,1)
    m.pulse()
    assert m.value==1
    m.pulse()
    assert m.value==0


def test_sr_rejects_forbidden_edge():
    m=ClockedCircuit("SR")
    m.set_input("S",1)
    m.set_input("R",1)
    with pytest.raises(ValueError):
        m.set_clock(1)
    assert m.clock==0 and m.value==0
    m.set_input("R",0)
    m.pulse()
    assert m.value==1
    m.set_input("S",0)
    m.set_input("R",1)
    m.pulse()
    assert m.value==0


def test_register_enable():
    m=ClockedCircuit("REG4")
    m.set_input("D0",1)
    m.set_input("D3",1)
    m.pulse()
    assert m.value==0
    m.set_input("EN",1)
    m.pulse()
    assert m.value==9


def test_counter_wrap_and_bounded_history():
    m=ClockedCircuit("COUNT4")
    m.set_input("EN",1)
    for i in range(40):
        m.pulse()
        assert m.value==(i+1)%16
    assert len(m.history)==64
    m.reset()
    assert m.value==m.clock==0 and len(m.history)==1


@pytest.mark.parametrize("kind",["SHIFT4","UNIVERSAL4","UPDOWN4"])
def test_every_new_register_transition(kind):
    from itertools import product
    from sequential_logic import transition, MODELS
    pins,_=MODELS[kind]
    for q in range(16):
        for bits in product((0,1),repeat=len(pins)):
            p=dict(zip(pins,bits))
            data=sum(p.get(f"D{i}",0)*2**i for i in range(4))
            if kind=="SHIFT4":
                expected=(q*2+p["SI"])%16 if p["EN"] else q
            elif kind=="UNIVERSAL4":
                expected=(q,q//2+8*p["SR"],(q*2+p["SL"])%16,data)[2*p["S1"]+p["S0"]]
            else:
                expected=0 if p["CLR"] else data if p["LOAD"] else (q+(1 if p["UP"] else -1))%16 if p["EN"] else q
            assert transition(kind,q,p)==expected

@pytest.mark.parametrize("kind,sequence",[("RING4",[1,2,4,8]),("JOHNSON4",[0,1,3,7,15,14,12,8])])
def test_feedback_counter(kind,sequence):
    m=ClockedCircuit(kind)
    assert m.value==sequence[0]
    m.pulse()
    assert m.value==sequence[0]
    m.set_input("EN",1)
    for expected in sequence[1:]+sequence[:1]:
        history=tuple(m.history)
        assert m.next_value()==expected
        assert tuple(m.history)==history
        m.pulse()
        assert m.value==expected

def test_new_register_rising_edge_and_preview():
    m=ClockedCircuit("UNIVERSAL4")
    for pin in ("D0","D2","S1","S0"):m.set_input(pin,1)
    assert m.value==0 and m.next_value()==5
    m.set_clock(1)
    assert m.value==5
    m.set_input("D1",1)
    assert m.value==5 and m.next_value()==7
    m.set_clock(1)
    m.set_clock(0)
    assert m.value==5
    m.set_clock(1)
    assert m.value==7
