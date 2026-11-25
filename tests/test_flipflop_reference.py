import pytest
from itertools import product
from flipflop_reference import KINDS, characteristic, excitation, formula
from sequential_logic import ClockedCircuit, MODELS


@pytest.mark.parametrize('kind', KINDS)
def test_characteristic(kind):
    for q, bits, nxt in characteristic(kind):
        if kind == 'D':
            expected = bits[0]
        elif kind == 'T':
            expected = 1-q if bits[0] else q
        elif kind == 'JK':
            expected = (q, 0, 1, 1-q)[2*bits[0]+bits[1]]
        else:
            expected = (q, 0, 1, None)[2*bits[0]+bits[1]]
        assert nxt == expected
        m = ClockedCircuit(kind)
        m.value = q
        for pin, bit in zip(m.pins, bits):
            m.set_input(pin, bit)
        snapshot = (m.value, m.clock, tuple(m.history))
        if expected is None:
            with pytest.raises(ValueError):
                m.set_clock(1)
            assert (m.value, m.clock, tuple(m.history)) == snapshot
        else:
            assert m.next_value() == expected
            assert (m.value, m.clock, tuple(m.history)) == snapshot
            m.set_clock(1)
            assert m.value == expected
    assert formula(kind).startswith('Q′ =')


@pytest.mark.parametrize('kind,patterns', [
    ('D', ('0','1','0','1')), ('T', ('0','1','1','0')),
    ('JK', ('0X','1X','X1','X0')), ('SR', ('0X','10','01','X0')),
])
def test_excitation(kind, patterns):
    rows = excitation(kind)
    assert tuple(r[3] for r in rows) == patterns
    assert tuple(r[:2] for r in rows) == tuple(product((0,1),repeat=2))
    for q,nxt,choices,pattern in rows:
        assert choices
        for bits in product((0,1),repeat=len(MODELS[kind][0])):
            match = all(p == 'X' or int(p) == b for p,b in zip(pattern,bits))
            assert match == (bits in choices)
            if match:
                assert (q,bits,nxt) in characteristic(kind)


@pytest.mark.parametrize('fn', [characteristic, excitation, formula])
def test_unsupported(fn):
    with pytest.raises(ValueError):
        fn('REG4')
