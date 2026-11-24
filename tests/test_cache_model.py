import random
import pytest
from cache_model import Cache


@pytest.mark.parametrize("ways",[1,2,4,8])
def test_address_bijection(ways):
    c=Cache(ways)
    for a in range(1024):
        t,i,o=c.decode(a)
        assert (t*c.sets+i)*4+o==a and 0<=i<c.sets and 0<=o<4


def test_conflict_and_associativity():
    for ways,hits in ((1,0),(2,4),(4,4),(8,4)):
        c=Cache(ways)
        for a in (0,32,0,32,1,33):c.access(a)
        assert c.hits==hits and c.ram_reads==4*(6-hits)


def test_fifo_vs_lru():
    for policy,evicted in (("lru",8),("fifo",0)):
        c=Cache(2,policy)
        for a in (0,32,0):c.access(a)
        assert c.access(64).evicted_block==evicted


def test_dirty_eviction_and_flush():
    c=Cache()
    c.memory.write(1,0x2222)
    first=c.access(0,0x1234)
    assert not first.hit and first.ram_reads==4 and c.memory.read(0)==0
    assert c.access(1).value==0x2222
    e=c.access(32)
    assert e.written_back and e.ram_writes==4 and e.evicted_block==0
    assert c.memory.read(0)==0x1234 and c.memory.read(1)==0x2222
    c.access(33,0xABCD)
    assert c.flush()==4 and c.flush()==0 and c.memory.read(33)==0xABCD
    assert c.access(33).hit and c.ram_writes==8


@pytest.mark.parametrize("ways",[1,2,4,8])
@pytest.mark.parametrize("replacement",["lru","fifo"])
@pytest.mark.parametrize("policy",["back","through"])
def test_against_flat_memory_oracle(ways,replacement,policy):
    rng=random.Random(122)
    c=Cache(ways,replacement,policy);oracle=[0]*1024
    for _ in range(256):
        a=rng.randrange(1024)
        if rng.randrange(2):
            value=rng.randrange(65536);oracle[a]=value
            assert c.access(a,value).value==value
            if policy=="through":assert c.memory.read(a)==value
        else:assert c.access(a).value==oracle[a]
    assert c.accesses==c.hits+c.misses==256
    assert c.ram_reads==4*c.misses
    c.flush();assert [c.memory.read(i) for i in range(1024)]==oracle


def test_invalid_write_atomic():
    c=Cache();c.access(0,1)
    for address,value in ((1024,0),(0,65536),(-1,1)):
        with pytest.raises(ValueError):c.access(address,value)
    assert c.accesses==1 and c.access(0).value==1
