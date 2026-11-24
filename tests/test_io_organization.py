import pytest
from io_organization import Handshake,PriorityInterrupt


@pytest.mark.parametrize("mode,signals,capture",[
    ("source",[(1,0),(1,1),(0,1),(0,0)],1),
    ("destination",[(0,1),(1,1),(1,0),(0,0)],2)])
def test_handshake_all_bytes(mode,signals,capture):
    h=Handshake(mode)
    for byte in range(256):
        events=[]
        for action in h.SEQUENCES[mode]:
            events.append(h.act(action,byte if action in ("offer","provide") else None))
        assert [(e.valid,e.ready) for e in events]==signals
        assert [e.received for e in events]==[byte if i==capture else None for i in range(4)]
        assert all(e.bus==byte if e.valid else e.bus is None for e in events)
    assert h.received==list(range(256))
    assert h.phase==0


@pytest.mark.parametrize("mode",["source","destination"])
def test_invalid_transition_atomic(mode):
    h=Handshake(mode)
    with pytest.raises(ValueError):h.act("release_data")
    assert not h.events and h.phase==0
    if mode=="destination":h.act("request")
    before=(h.phase,h.valid,h.ready,h.bus,list(h.events))
    with pytest.raises(ValueError):h.act(h.next_action,256)
    assert (h.phase,h.valid,h.ready,h.bus,h.events)==before


def test_all_request_mask_combinations():
    for pending in range(16):
        for mask in range(16):
            p=PriorityInterrupt()
            for i in range(4):
                if pending&(1<<i):p.request(i)
            p.set_mask(mask)
            s=p.select()
            expected=next((i for i in range(4) if pending&mask&(1<<i)),None)
            assert s.winner==expected and s.eligible==pending&mask
            assert [i for i,_,a,_ in s.grant if a]==([] if expected is None else [expected])
            assert s.vector==(None if expected is None else 0x100+4*expected)
            p.enabled=False
            assert p.select().winner is None and p.pending==pending


def test_nested_interrupt_and_pending():
    p=PriorityInterrupt()
    p.request(3);p.request(3)
    assert p.acknowledge().winner==3
    p.request(3);p.request(1);p.request(2)
    assert p.acknowledge().winner==1
    assert p.select().winner is None
    p.request(0)
    assert p.acknowledge().winner==0
    assert p.service==[3,1,0] and p.pending==12
    assert p.end()==0 and p.end()==1
    assert p.acknowledge().winner==2
    assert p.end()==2 and p.end()==3
    assert p.acknowledge().winner==3
    assert p.end()==3 and p.pending==0
    with pytest.raises(ValueError):p.end()
    with pytest.raises(ValueError):p.acknowledge()
