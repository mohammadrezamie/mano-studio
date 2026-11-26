from itertools import product
import pytest
from block_composition import insert


HALF = (('A', 'B'), (('sum', 'XOR', ('A', 'B')), ('carry', 'AND', ('A', 'B'))),
        (('S', 'sum'), ('C', 'carry')))
OR = (('A', 'B'), (('y', 'OR', ('A', 'B')),), (('Y', 'y'),))


def test_full_adder_from_two_half_adders():
    second = insert(*HALF, *HALF, 'h2', {'A': 'sum', 'B': None})
    result = insert(*second, *OR, 'or1', {'A': 'carry', 'B': 'h2_carry'})
    inputs, gates, outputs = result
    assert inputs == ('A', 'B', 'h2_B')
    assert outputs[:2] == HALF[2]
    assert len(gates) == 5
    for bits in product((0, 1), repeat=3):
        values = dict(zip(inputs, bits))
        for name, op, (a, b) in gates:
            x, y = values[a], values[b]
            values[name] = {'XOR': x ^ y, 'AND': x & y, 'OR': x | y}[op]
        out = {name: values[signal] for name, signal in outputs}
        assert out['h2_S'] + 2 * out['or1_Y'] == sum(bits)
    assert insert(*HALF, *HALF, 'h2', {'A': 'sum', 'B': None}) == second


def test_reuse_signal_and_alias():
    result = insert(*HALF, ('X',), (), (('Y', 'X'),), 'tap', {'X': 'carry'})
    assert result == (HALF[0], HALF[1], HALF[2] + (('tap_Y', 'carry'),))


@pytest.mark.parametrize('prefix,bindings', [('', {'A':None,'B':None}),
    ('a-b', {'A':None,'B':None}), ('h', {'A':'S','B':None}),
    ('h', {'A':'future','B':None}), ('h', {'A':None}),
    ('h', {'A':None,'B':None,'C':None}), ('h', {'A':1,'B':None})])
def test_invalid_bindings(prefix, bindings):
    with pytest.raises(ValueError):
        insert(*HALF, *HALF, prefix, bindings)


def test_collision_and_limit():
    second = insert(*HALF, *HALF, 'h2', {'A': 'sum', 'B': None})
    with pytest.raises(ValueError, match='collision'):
        insert(*second, *HALF, 'h2', {'A': 'sum', 'B': None})
    with pytest.raises(ValueError, match='limits'):
        insert(tuple(f'A{i}' for i in range(10)), (), (('Y','A0'),),
               *HALF, 'h', {'A':None,'B':None})
    assert HALF[0] == ('A','B')
