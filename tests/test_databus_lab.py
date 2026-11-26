from itertools import product
import pytest
from databus_lab import Databus,REGISTERS


def test_transfer_and_old_address():
    m=Databus()
    m.tick(("EXT",),("AR",),9)
    m.tick(("EXT",),("R0",),6)
    result=m.tick(("R0",),("AR","R1","RAM"))
    assert result.before==(9,6,0)
    assert result.after==(6,6,6)
    assert result.memory_write==(9,0,6)
    assert m.memory.read(9)==6 and m.memory.read(6)==0
    m.tick(("EXT",),("AR",),9)
    m.tick(("RAM",),("R0","R1"))
    assert tuple(m.registers.values())==(9,6,6)


@pytest.mark.parametrize("source",["AR","R0","R1","RAM","EXT"])
def test_all_words_and_destination_masks(source):
    for word,mask in product(range(16),range(16)):
        m=Databus()
        m.tick(("EXT",),("AR",),3)
        if source=="AR":
            m.tick(("EXT",),("AR",),word)
        elif source=="RAM":
            m.tick(("EXT",),("RAM",),word)
        elif source!="EXT":
            m.tick(("EXT",),(source,),word)
        before=tuple(m.registers.values())
        address=before[0]
        memory_before=m.memory.read(address)
        dest=tuple(d for i,d in enumerate((*REGISTERS,"RAM")) if mask>>i&1)
        result=m.tick((source,),dest,word)
        assert result.bus==f"{word:04b}"
        assert result.after==tuple(word if mask>>i&1 else before[i] for i in range(3))
        assert m.memory.read(address)==(word if mask&8 else memory_before)
        assert result.memory_write==((address,memory_before,word) if mask&8 else None)


@pytest.mark.parametrize("sources,dest,external",[
    ((),("AR",),0),(("R0","R1"),("RAM",),0),
    (("R0","R0"),(),0),(("bad",),(),0),
    (("EXT",),("R1","R1"),1),(("EXT",),("bad",),1),
    (("EXT",),("R0",),16),(("EXT",),("R0",),True),
])
def test_invalid_atomic(sources,dest,external):
    m=Databus()
    m.tick(("EXT",),("R0","RAM"),5)
    before=(dict(m.registers),tuple(m.memory.read(a) for a in range(16)),tuple(m.history))
    with pytest.raises(ValueError):
        m.tick(sources,dest,external)
    assert (m.registers,tuple(m.memory.read(a) for a in range(16)),tuple(m.history))==before


def test_z_x_history_reset():
    m=Databus()
    assert m.tick((),()).bus=="ZZZZ"
    m.tick(("EXT",),("R0",),5)
    m.tick(("EXT",),("R1",),6)
    assert m.preview(("R0","R1")).bits=="01XX"
    assert m.tick(("R0","R1"),()).bus=="01XX"
    for _ in range(70):
        m.tick(("R0",),())
    assert len(m.history)==64
    m.reset()
    assert tuple(m.registers.values())==(0,0,0) and not m.history
    assert all(m.memory.read(i)==0 for i in range(16))
