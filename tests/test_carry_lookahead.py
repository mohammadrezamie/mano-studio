from itertools import product
import pytest
from carry_lookahead import network, depths


@pytest.mark.parametrize('width', [2, 3, 4])
def test_all_additions_and_prefix_carries(width):
    inputs, gates, outputs = network(width)
    assert len(inputs) == 2*width+1
    assert len(outputs) == width+1
    known = set(inputs)
    for name, op, args in gates:
        assert name not in known and set(args) <= known
        assert op in ('AND', 'OR', 'XOR') and 2 <= len(args) <= 4
        known.add(name)
    for bits in product((0, 1), repeat=len(inputs)):
        values = dict(zip(inputs, bits))
        a = sum(values[f'A{i}'] << i for i in range(width))
        b = sum(values[f'B{i}'] << i for i in range(width))
        for name, op, args in gates:
            row = [values[arg] for arg in args]
            # Independent evaluator, not the application's Circuit engine.
            values[name] = int(all(row)) if op == 'AND' else int(any(row)) if op == 'OR' else sum(row) % 2
        assert sum(values[source] << i for i, (_, source) in enumerate(outputs)) == a+b+values['Cin']
        for i in range(1, width+1):
            mask = (1 << i)-1
            assert values[f'c{i}'] == (((a & mask)+(b & mask)+values['Cin']) >> i)
    assert depths(inputs, gates, outputs)['Cout'] == 4


def test_four_bit_depth_and_no_ripple_dependency():
    inputs, gates, outputs = network()
    levels = depths(inputs, gates, outputs)
    assert levels == {'S0': 2, 'S1': 4, 'S2': 5, 'S3': 5, 'Cout': 4}
    for name, _, args in gates:
        if name.startswith('c'):
            assert not any(arg.startswith('c') for arg in args)
    assert len(gates) <= 96


@pytest.mark.parametrize('width', [1, 5, 8, True, 3.0, '4'])
def test_invalid_width(width):
    with pytest.raises(ValueError):
        network(width)
