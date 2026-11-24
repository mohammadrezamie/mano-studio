import pytest
from simulator import CPU
from mano_isa import FIXED,MEMORY
from execution_history import ExecutionHistory


@pytest.mark.parametrize("word",list(FIXED.values())+[(code<<12)|0x100 for code in MEMORY.values()]+[0x8000|(code<<12)|0x100 for code in MEMORY.values()])
def test_control_consistency(word):
    c=CPU({0:word,0x100:0x200,0x200:0xFFFF})
    c.ac=0xAAAA
    h=ExecutionHistory(c)
    e=h.step()
    for g in e.microevents:
        t=g.control
        assert t.timing==g.timing and t.decoder==(g.before["IR"]>>12)&7
        assert ("M.READ" in t.signals)==bool(g.reads)
        assert ("M.WRITE" in t.signals)==bool(g.writes)
        assert ("SC.CLR" if g.final else "SC.INR") in t.signals
        if t.source=="M":assert t.value==g.reads[0][1] and t.select==7
        elif t.source:assert t.value==g.before[t.source]
        else:assert t.select==0 and t.value is None
        for _,_,new in g.writes:assert t.value==new
    assert [(g.control.source,g.control.select) for g in e.microevents[:3]]==[("PC",2),("M",7),("IR",5)]
    h.back()
    assert h.step()==e


@pytest.mark.parametrize("word,expected",[(0x2100,[(None,0),("M",7),(None,0)]),
    (0xA100,[("M",7),("M",7),(None,0)]),(0x3100,[(None,0),("AC",4)]),
    (0x4100,[(None,0),("AR",1)]),(0x5100,[(None,0),("PC",2),("AR",1)]),
    (0x6100,[(None,0),("M",7),(None,0),("DR",3)]),
    (0xF800,[(None,0)]),(0xF400,[("AC",4)])])
def test_named_bus_paths(word,expected):
    c=CPU({0:word,0x100:0x200,0x200:1})
    e=c.step()
    assert [(g.control.source,g.control.select) for g in e.microevents[3:]]==expected


def test_interrupt_and_conditional_controls():
    c=CPU(entry=0x100)
    c.r=c.ien=1
    e=c.step()
    assert [g.control.select for g in e.microevents]==[2,6,0]
    assert all(g.control.interrupt_cycle for g in e.microevents)
    assert e.microevents[1].control.value==0x100
    assert "R.CLR" in e.microevents[2].control.signals
    for ac in (0,1):
        c=CPU({0:0x7004})
        c.ac=ac
        e=c.step()
        assert ("PC.INR" in e.microevents[-1].control.signals)==(ac==0)
