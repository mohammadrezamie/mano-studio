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
