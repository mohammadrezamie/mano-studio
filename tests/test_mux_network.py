from itertools import product
from random import Random
import pytest
from mux_network import network


def verify(values):
    inputs, gates, outputs, stages = network(values)
    known = set(inputs)
    for name, op, args in gates:
        assert name not in known and set(args) <= known
        assert len(args) == (1 if op == 'NOT' else 2)
        known.add(name)
    assert len(gates) <= 96
    assert len(stages) <= len(values)-1
    for i, bits in enumerate(product((0, 1), repeat=len(inputs))):
        env = dict(zip(inputs, bits))
        for name, op, args in gates:
            row = [env[a] for a in args]
            env[name] = 1-row[0] if op == 'NOT' else (row[0]&row[1] if op == 'AND' else row[0]|row[1])
        assert env[outputs[0][1]] == values[i]
        for select, low, high, out in stages:
            assert env[out] == env[high if env[select] else low]
    assert network(values) == (inputs, gates, outputs, stages)


@pytest.mark.parametrize('n', [2, 3])
def test_all_small_functions(n):
    for values in product((0, 1), repeat=2**n):
        verify(values)


def test_seeded_four_variable_functions():
    rng = Random(2026)
    for _ in range(256):
        verify(tuple(rng.randrange(2) for _ in range(16)))


def test_constant_and_shared_cofactor():
    for bit in (0, 1):
        values = (bit,)*16
        verify(values)
        assert not network(values)[3]
    values = (0, 1, 1, 0)*4
    verify(values)
    assert all(stage[0] in ('C', 'D') for stage in network(values)[3])


@pytest.mark.parametrize('values', [(0,)*2, (0,)*32, (0,1,None,0), (0,1,True,0), (0,1,2,0)])
def test_invalid(values):
    with pytest.raises(ValueError):
        network(values)
