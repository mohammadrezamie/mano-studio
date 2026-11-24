import pytest
from multiprocessor import SharedBus


@pytest.mark.parametrize("policy,expected",[("fixed",[0,0,1,1,2,2,3,3]),("rotating",[0,1,2,3,0,1,2,3])])
def test_order_and_real_memory(policy,expected):
    b=SharedBus(policy)
    for i in range(4):
        b.enqueue(i,i,i+10);b.enqueue(i,i)
    events=b.run()
    assert [e.grant for e in events]==expected
    assert b.memory[:4]==[10,11,12,13]
    assert [e.value for e in events if e.request.value is None]==[10,11,12,13]
    assert b.served==[2]*4 and b.done
    assert b.step().grant is None


def test_rotating_bound_under_continuous_contention():
    b=SharedBus()
    for i in range(4):b.enqueue(i,0,i)
    for cycle in range(100):
        e=b.step()
        assert e.grant==cycle%4
        b.enqueue(e.grant,0,e.grant)
    assert b.served==[25]*4 and b.waited==[75]*4


def test_cross_master_visibility_and_atomic_rejection():
    b=SharedBus()
    b.enqueue(0,3,0xABCD);b.enqueue(1,3)
    assert b.step().value==0xABCD
    assert b.step().value==0xABCD
    for master,address,value in ((4,0,0),(0,64,0),(0,0,65536)):
        with pytest.raises(ValueError):b.enqueue(master,address,value)
    assert b.done and b.memory[3]==0xABCD
