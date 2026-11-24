import random
import pytest
from associative_memory import AssociativeMemory,masked_match
from virtual_memory import VirtualMemory


def test_cam_mask_truth():
    for word in range(16):
        for key in range(16):
            for mask in range(16):
                expected=all(not(mask>>i&1) or (word>>i&1)==(key>>i&1) for i in range(4))
                assert masked_match(word,key,mask,4)==expected
    m=AssociativeMemory()
    for i,w in enumerate((0xA0,0xA5,0xB0,0xA0)):m.write(i,w)
    assert m.search(0xA0,0xF0).matches==(0,1,3)
    assert m.search(0xA0).matches==(0,3)
    m.invalidate(0);assert m.search(0,0).matches==(1,2,3)
    assert m.search(0xA0).first==3


def test_dirty_eviction_reload_and_tlb():
    m=VirtualMemory()
    e=m.access(0,0xCAFE);assert e.fault and not e.tlb_hit
    assert m.access(1).tlb_hit
    for a in (16,32,48):m.access(a)
    e=m.access(64)
    assert e.evicted==0 and e.written_back and m.pages[0].frame is None and 0 not in m.tlb
    e=m.access(0)
    assert e.fault and e.value==0xCAFE and m.page_outs==1


def test_fifo_vs_lru():
    for policy,victim in (("fifo",0),("lru",1)):
        m=VirtualMemory(policy,4)
        for a in (0,16,32,48,0):m.access(a)
        assert m.access(64).evicted==victim
        assert victim not in m.tlb
        assert m.access(64).tlb_hit


@pytest.mark.parametrize("policy",["fifo","lru"])
@pytest.mark.parametrize("size",[2,4])
def test_random_oracle(policy,size):
    m=VirtualMemory(policy,size);oracle=[0]*256;rng=random.Random(41)
    for _ in range(1000):
        a=rng.randrange(256)
        if rng.randrange(2):
            w=rng.randrange(65536);oracle[a]=w;e=m.access(a,w)
        else:e=m.access(a)
        assert e.value==oracle[a] and e.physical==e.frame*16+a%16
        assert all(m.pages[vpn].frame==f for vpn,f in m.tlb.items())
        assert len(m.tlb)<=size
        assert all(m.pages[vpn].frame==f for f,vpn in enumerate(m.owners) if vpn is not None)
        assert not(e.fault and e.tlb_hit)
    for a in range(256):assert m.access(a).value==oracle[a]
    assert m.page_ins==m.faults


def test_invalid_atomic():
    m=VirtualMemory()
    for a,w in ((256,1),(0,65536),(-1,None)):
        with pytest.raises(ValueError):m.access(a,w)
    assert m.accesses==0 and not m.tlb
