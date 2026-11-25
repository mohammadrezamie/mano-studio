from itertools import product
import pytest
from timing_constraints import check


def test_boundary_and_coincident():
    assert check(0, [(7,1),(12,0)], 10,3,2).sampled == 1
    r = check(0, [(8,1),(11,0)],10,3,2)
    assert r.setup_violations == (8,) and r.hold_violations == (11,)
    assert not r.valid and r.sampled is None
    r = check(0,[(10,1)],10,0,0)
    assert r.coincident and not r.valid and r.sampled is None
    assert check(1,[(10,1)],10,2,2).sampled == 1


def test_exhaustive_small_waveforms():
    # Enumerate all complete six-tick waveforms, both starting levels,
    # every clock edge and every setup/hold length from zero to three.
    for initial in (0,1):
        for bits in product((0,1),repeat=6):
            events = tuple(enumerate(bits))
            transitions = [i for i,b in enumerate(bits) if b != (bits[i-1] if i else initial)]
            for edge in range(6):
                for setup,hold in product(range(4),repeat=2):
                    r = check(initial,events,edge,setup,hold)
                    before = tuple(t for t in transitions if 0 < edge-t < setup)
                    after = tuple(t for t in transitions if 0 < t-edge < hold)
                    assert r.setup_violations == before
                    assert r.hold_violations == after
                    assert r.coincident == (edge in transitions)
                    valid = not (before or after or edge in transitions)
                    assert r.valid == valid
                    assert r.sampled == ((bits[edge-1] if edge else initial) if valid else None)


@pytest.mark.parametrize("initial,events,edge,setup,hold", [
    (2,(),3,1,1),(True,(),3,1,1),(0,(),-1,1,1),
    (0,(),3,-1,1),(0,(),3,1,1.5),(0,[(1,2)],3,1,1),
    (0,[(2,1),(1,0)],3,1,1),(0,[(1,1),(1,0)],3,1,1),
    (0,[(-1,1)],3,1,1),
])
def test_invalid(initial,events,edge,setup,hold):
    with pytest.raises(ValueError):
        check(initial,events,edge,setup,hold)
