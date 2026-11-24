import pytest
from dma_model import DMA,CircularFIFO
from memory_organization import MemoryArray
from io_organization import PriorityInterrupt


@pytest.mark.parametrize("mode,cycles",[("burst",6),("cycle_steal",14)])
@pytest.mark.parametrize("direction",["to_memory","from_memory"])
def test_dma_actual_transfers(mode,cycles,direction):
    m=MemoryArray(4,8,4,2)
    irq=PriorityInterrupt()
    data=[0x1234,0,0xFFFF]
    if direction=="from_memory":
        for i,v in enumerate(data):m.write(15+i,v)
    d=DMA(m,data if direction=="to_memory" else (),direction,15,3,mode,irq)
    events=d.run()
    assert len(events)==cycles and d.done and d.remaining==0
    assert [e.address for e in events if e.action=="transfer"]==[15,16,17]
    assert all(e.owner=="DMA" and e.grant for e in events if e.action=="transfer")
    assert [e.value for e in events if e.action=="transfer"]==data
    assert d.owner=="CPU" and irq.pending==4 and sum(e.irq for e in events)==1
    assert [m.read(i) for i in (15,16,17)]==data
    if direction=="from_memory":assert list(d.device)==data
    else:assert not d.device
    assert d.step() is None


def test_invalid_dma_no_memory_change():
    m=MemoryArray(4,8,4,2)
    for start,count,data in [(63,2,[1,2]),(0,2,[1]),(0,1,[65536])]:
        with pytest.raises(ValueError):DMA(m,data,"to_memory",start,count)
    assert all(m.read(i)==0 for i in range(64))


@pytest.mark.parametrize("capacity",[4,8,16])
def test_fifo_full_exchange_and_wrap(capacity):
    f=CircularFIFO(capacity)
    for i in range(capacity):f.edge(write=i)
    assert f.full and f.read_pointer==f.write_pointer==0
    with pytest.raises(ValueError):f.edge(write=99)
    assert f.contents()==tuple(range(capacity))
    for i in range(capacity):
        e=f.edge(True,100+i)
        assert e.read_value==i and f.full
    assert f.contents()==tuple(range(100,100+capacity))
    for i in range(capacity):assert f.edge(True).read_value==100+i
    assert f.empty and f.read_pointer==f.write_pointer==0
    with pytest.raises(ValueError):f.edge(True,5)
    assert f.empty and not f.contents()


def test_fifo_reject_invalid_write_atomically():
    f=CircularFIFO(4);f.edge(write=10)
    with pytest.raises(ValueError):f.edge(True,65536)
    assert f.contents()==(10,) and f.read_pointer==0
