from random import Random

import pytest
from cache_coherence import MSICache, Writeback


def test_read_share_upgrade_and_dirty_intervention():
    m = MSICache()
    assert m.read(0, 3).bus == "BusRd"
    assert m.read(1, 3).bus == "BusRd"
    e = m.write(0, 3, 0xABCD)
    assert e.hit and e.bus == "BusUpgr" and e.invalidated == (1,)
    assert m.memory[3] == 0 and m.lines[0][3].state == "M"
    assert m.write(0, 3, 0x1234).bus == "none"
    e = m.read(2, 3)
    assert e.value == 0x1234 and e.writebacks == (Writeback(0, 3, 0x1234, "snoop"),)
    assert m.memory[3] == 0x1234
    assert m.lines[0][3].state == m.lines[2][3].state == "S"
    assert m.read(2, 3).bus == "none"


def test_write_miss_invalidates_dirty_owner():
    m = MSICache()
    m.write(0, 0, 9)
    e = m.write(1, 0, 10)
    assert e.bus == "BusRdX" and not e.hit and e.invalidated == (0,)
    assert e.writebacks == (Writeback(0, 0, 9, "snoop"),)
    assert m.memory[0] == 9 and m.lines[1][0].value == 10
    assert m.read(3, 0).value == 10


def test_dirty_conflict_eviction_and_snoop_in_same_access():
    m = MSICache()
    m.write(0, 0, 7)
    m.write(1, 4, 8)
    e = m.read(0, 4)
    assert e.writebacks == (Writeback(0, 0, 7, "eviction"), Writeback(1, 4, 8, "snoop"))
    assert m.memory[0] == 7 and m.memory[4] == 8
    assert e.before[0][0].address == 0 and e.after[0][0].address == 4
    assert m.read(2, 0).value == 7


@pytest.mark.parametrize("seed", range(10))
def test_randomized_against_sequential_memory_oracle(seed):
    rng = Random(seed)
    m = MSICache()
    expected = [0] * m.WORDS
    for _ in range(1000):
        core, address = rng.randrange(m.CORES), rng.randrange(m.WORDS)
        if rng.randrange(2):
            value = rng.randrange(65536)
            expected[address] = value
            e = m.write(core, address, value)
        else:
            e = m.read(core, address)
        assert e.value == expected[address]
        assert e.after == m.lines and e.memory == m.memory
        for a in range(m.WORDS):
            lines = [row[a % m.SETS] for row in m.lines]
            valid = [line for line in lines if line.address == a and line.state != "I"]
            modified = [line for line in valid if line.state == "M"]
            assert all(line.value == expected[a] for line in valid)
            if modified:
                assert len(modified) == len(valid) == 1
            else:
                assert m.memory[a] == expected[a]
        assert all(w.value == m.memory[w.address] for w in e.writebacks)
    assert m.accesses == 1000


@pytest.mark.parametrize("core,address,value", [(True, 0, 1), (4, 0, 1), (0, 16, 1), (0, -1, 1), (0, 0, True), (0, 0, -1), (0, 0, 65536)])
def test_invalid_access_is_atomic(core, address, value):
    m = MSICache()
    m.write(0, 0, 12)
    before = m.lines, m.memory, m.accesses
    with pytest.raises(ValueError):
        m.write(core, address, value)
    assert (m.lines, m.memory, m.accesses) == before
