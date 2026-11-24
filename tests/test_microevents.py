import pytest
from simulator import CPU
from mano_isa import FIXED,MEMORY
from execution_history import ExecutionHistory

@pytest.mark.parametrize("op,word",list(FIXED.items())+[(op,(code<<12)|0x100) for op,code in MEMORY.items()]+[(op,0x8000|(code<<12)|0x100) for op,code in MEMORY.items()])
def test_actual_group_chain(op,word):
    c=CPU({0:word,0x100:0x200,0x200:0xFFFF})
    c.ac=0xAAAA;c.e=1
    before=c.registers()
    h=ExecutionHistory(c)
    e=h.step()
    assert e.mnemonic==op
    assert e.microevents[0].before==before
    assert e.microevents[-1].after==e.after
    assert tuple(w for g in e.microevents for w in g.writes)==e.writes
    assert e.microevents[1].reads==((0,word),)
    assert all(a.after==b.before for a,b in zip(e.microevents,e.microevents[1:]))
    assert [g.timing for g in e.microevents]==list(range(len(e.microevents)))
    end=6 if op=="ISZ" else 5 if op in ("AND","ADD","LDA","BSA") else 4 if op in MEMORY else 3
    assert e.microevents[-1].timing==end
    h.back()
    assert c.registers()==before
    assert c.memory[0x100]==0x200 and c.memory[0x200]==0xFFFF

def test_indirect_isz_reads_and_skip():
    c=CPU({0:0xE100,0x100:0x200,0x200:0xFFFF})
    e=c.step()
    assert e.microevents[3].reads==((0x100,0x200),)
    assert e.microevents[4].reads==((0x200,0xFFFF),)
    assert e.microevents[5].after["DR"]==0
    assert e.microevents[6].writes==((0x200,0xFFFF,0),)
    assert c.pc==2

def test_bsa_wrap():
    c=CPU({0:0x5FFF})
    e=c.step()
    assert e.microevents[4].after["AR"]==0
    assert e.microevents[4].writes==((0xFFF,0,1),)
    assert e.microevents[5].after["PC"]==0

def test_interrupt_groups():
    c=CPU(entry=0x100)
    c.ien=1
    e=c.step()
    assert e.mnemonic=="INT"
    assert e.microevents[0].after["TR"]==0x100
    assert e.microevents[1].writes==((0,0,0x100),)
    assert c.pc==1 and c.ien==0

def test_invalid_preflight():
    c=CPU({0:0x7FFF})
    before=c.registers()
    with pytest.raises(ValueError):c.step()
    assert c.registers()==before
