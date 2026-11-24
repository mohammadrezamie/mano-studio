import itertools
import pytest
from multiprocessor import Crossbar


@pytest.mark.parametrize("policy",["fixed","rotating"])
def test_all_head_destinations(policy):
    for banks in itertools.product(range(4),repeat=4):
        c=Crossbar(policy)
        for master,bank in enumerate(banks):c.enqueue(master,bank*16+master,master+1)
        e=c.step()
        assert len(e.transfers)==len(set(banks))
        assert len({t.master for t in e.transfers})==len(e.transfers)
        assert len({t.bank for t in e.transfers})==len(e.transfers)
        assert len(e.waiting)==4-len(e.transfers)
        c.run()
        assert c.done and c.served==[1]*4
        for master,bank in enumerate(banks):assert c.memory.read(bank*16+master)==master+1


def test_parallel_and_conflict():
    for parallel,clocks in ((True,2),(False,8)):
        c=Crossbar()
        for i in range(4):
            address=i*16 if parallel else i
            c.enqueue(i,address,0x100+i);c.enqueue(i,address)
        events=c.run()
        assert len(events)==clocks
        assert sum(c.served)==8
        for e in events:
            for t in e.transfers:
                assert t.value==0x100+t.master


def test_priority_fairness_and_head_blocking():
    c=Crossbar()
    for i in range(4):c.enqueue(i,0,i)
    for i in range(40):
        e=c.step()
        assert e.transfers[0].master==i%4
        c.enqueue(i%4,0,i)
    assert c.waited==[30]*4
    c=Crossbar()
    c.enqueue(0,0);c.enqueue(1,0);c.enqueue(1,16)
    assert len(c.step().transfers)==1
    assert c.step().transfers[0].bank==0
    assert c.step().transfers[0].bank==1


def test_read_observes_prior_write_and_invalid_atomic():
    c=Crossbar("fixed")
    c.enqueue(0,1,0x1234);c.enqueue(1,1)
    assert c.step().transfers[0].value==0x1234
    assert c.step().transfers[0].value==0x1234
    for args in ((4,0,1),(0,64,1),(0,0,65536)):
        with pytest.raises(ValueError):c.enqueue(*args)
    assert c.done
