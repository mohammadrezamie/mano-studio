import itertools
import random
import pytest
from synchronization import Synchronization


def test_all_unlocked_interleavings():
    outcomes=set()
    # All 20 schedules preserving three ordered steps for each worker.
    for slots in itertools.combinations(range(6),3):
        m=Synchronization(False)
        for i in range(6):m.step(0 if i in slots else 1)
        assert m.done
        outcomes.add(m.shared)
    assert outcomes=={1,2}


def test_lost_update_vs_atomic_lock():
    race=Synchronization(False);race.run()
    assert race.shared==1 and race.expected==2
    safe=Synchronization(True);safe.run()
    assert safe.shared==safe.expected==2
    assert any(e.action=="wait" for e in safe.events)
    assert safe.owner is None


@pytest.mark.parametrize("repeats",[1,2,8])
def test_locked_random_schedules(repeats):
    rng=random.Random(13)
    for _ in range(32):
        initial=rng.randrange(65536)
        m=Synchronization(True,repeats,initial)
        for _ in range(1000):
            if m.done:break
            i=rng.randrange(2)
            before=m.owner
            e=m.step(i)
            if e and e.action in ("read","increment","write","release"):
                assert before==i
            assert sum(w.phase in ("read","increment","write","release") for w in m.workers)<=1
        assert m.done and m.shared==m.expected and m.owner is None


def test_wrap_and_invalid():
    m=Synchronization(True,1,65535);m.run()
    assert m.shared==1
    with pytest.raises(ValueError):Synchronization(True,0)
    with pytest.raises(ValueError):m.step(2)
    assert m.step(0) is None
