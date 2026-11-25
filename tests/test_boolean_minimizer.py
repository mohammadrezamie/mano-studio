from itertools import product
import random

import pytest

from boolean_minimizer import gray_indices, minimize


def oracle(values, target):
    # Independent enumeration of all fixed-bit masks and dynamic programming
    # over covered required cells, including non-prime cubes.
    size = len(values)
    required = sum(1 << i for i, v in enumerate(values) if v == target)
    costs = {0: (0, 0)}
    cubes = []
    for fixed in range(size):
        for bits in range(size):
            if bits & ~fixed:
                continue
            cells = [i for i in range(size) if i & fixed == bits]
            if any(values[i] == 1-target for i in cells):
                continue
            mask = sum(1 << i for i in cells) & required
            if mask:
                cubes.append((mask, fixed.bit_count()))
    for mask, literals in cubes:
        for covered, cost in list(costs.items()):
            union = covered | mask
            proposed = (cost[0]+1, cost[1]+literals)
            costs[union] = min(costs.get(union, proposed), proposed)
    return costs[required]


def check(values, form):
    result = minimize(values, form)
    assert all(result.evaluate(i) == v for i, v in enumerate(values) if v is not None)
    assert (len(result.groups), sum(g.literals for g in result.groups)) == oracle(values, int(form == 'SOP'))
    assert result == minimize(values, form)


@pytest.mark.parametrize('form', ['SOP', 'POS'])
def test_all_three_variable_binary_functions(form):
    for values in product((0, 1), repeat=8):
        check(values, form)


@pytest.mark.parametrize('form', ['SOP', 'POS'])
def test_all_two_variable_ternary_functions(form):
    for values in product((0, 1, None), repeat=4):
        check(values, form)


@pytest.mark.parametrize('form', ['SOP', 'POS'])
def test_four_variable_dont_cares(form):
    rng = random.Random(2026)
    for _ in range(80):
        check(tuple(rng.choice((0, 1, None)) for _ in range(16)), form)


def test_wraparound_and_constants():
    assert gray_indices(4) == ((0,1,3,2),(4,5,7,6),(12,13,15,14),(8,9,11,10))
    v = tuple(int(i in (0,2,8,10)) for i in range(16))
    assert minimize(v).expression == "B'D'"
    assert minimize(v, 'POS').expression == "(D') · (B')"
    for value in (0, 1):
        for form in ('SOP', 'POS'):
            assert minimize([value]*8, form).expression == str(value)
    assert minimize([None]*4).expression == '0'
    assert minimize([None]*4, 'POS').expression == '1'


@pytest.mark.parametrize('values,form', [([0]*3,'SOP'),([2]*4,'SOP'),([True]*4,'SOP'),([0]*4,'XOR')])
def test_invalid(values, form):
    with pytest.raises(ValueError):
        minimize(values, form)


@pytest.mark.parametrize("key",["half_adder","full_adder","decoder","mux"])
def test_copy_circuit_output_exact(key):
    from boolean_minimizer import circuit_output_values
    from logic_engine import CIRCUITS
    circuit=CIRCUITS[key]
    for name,_ in circuit.outputs:
        values=circuit_output_values(circuit,name)
        result=minimize(values)
        for i in range(len(values)):
            bits=tuple(int(bit) for bit in f"{i:0{len(circuit.inputs)}b}")
            assert result.evaluate(i)==circuit.result(dict(zip(circuit.inputs,bits)))[name]


def test_circuit_import_rejects_unsupported():
    from boolean_minimizer import circuit_output_values
    from logic_engine import CIRCUITS
    for key,name in (("not","Y"),("ripple4","S0"),("half_adder","unknown")):
        with pytest.raises(ValueError):
            circuit_output_values(CIRCUITS[key],name)


@pytest.mark.parametrize("form",["SOP","POS"])
def test_synthesized_netlist_matches_all_small_functions(form):
    from boolean_synthesis import synthesize
    from circuit_document import CircuitDocument
    for values in product((0,1,None),repeat=4):
        document=synthesize(values,form)
        restored=CircuitDocument.loads(document.dumps())
        result=minimize(values,form)
        assert [out[0] for _,out in restored.compile().truth_table()]==[result.evaluate(i) for i in range(4)]


@pytest.mark.parametrize("form",["SOP","POS"])
def test_synthesis_large_covers_and_constants(form):
    from boolean_synthesis import synthesize
    cases=[[0]*16,[1]*16,[None]*16,[i.bit_count()%2 for i in range(16)]]
    rng=random.Random(172)
    cases.extend([rng.choice((0,1,None)) for _ in range(16)] for _ in range(64))
    for values in cases:
        doc=synthesize(values,form)
        assert all(1<=len(g.inputs)<=4 for g in doc.gates)
        result=minimize(values,form)
        assert [o[0] for _,o in doc.compile().truth_table()]==[result.evaluate(i) for i in range(16)]
