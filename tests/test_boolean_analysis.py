from itertools import product
from random import Random
import pytest
from boolean_analysis import analyze


@pytest.mark.parametrize('form', ['SOP', 'POS'])
def test_all_three_variable_functions(form):
    for values in product((0, 1), repeat=8):
        a = analyze(values, form)
        assert a.completed == values
        assert a.minterms == tuple(i for i, v in enumerate(values) if v)
        assert a.maxterms == tuple(i for i, v in enumerate(values) if not v)
        target = int(form == 'SOP')
        expected = []
        for i in range(8):
            for bit in range(3):
                j = i ^ (1 << bit)
                if i < j and values[i] == values[j] == target:
                    assert any(i in g.cells and j in g.cells for g in a.repaired.groups)
                    if not any(i in g.cells and j in g.cells for g in a.solution.groups):
                        expected.append((i, j))
        assert a.hazards == tuple(sorted(expected))
        assert tuple(a.repaired.evaluate(i) for i in range(8)) == values


@pytest.mark.parametrize('form', ['SOP', 'POS'])
def test_four_variable_completions(form):
    rng = Random(49)
    for _ in range(128):
        values = tuple(rng.choice((0, 1, None)) for _ in range(16))
        a = analyze(values, form)
        assert all(v is None or a.completed[i] == v for i, v in enumerate(values))
        assert a.dont_cares == tuple(i for i, v in enumerate(values) if v is None)
        assert tuple(a.repaired.evaluate(i) for i in range(16)) == a.completed
        for i, j in a.hazards:
            assert (i ^ j).bit_count() == 1
            assert any(i in g.cells and j in g.cells for g in a.repaired.groups)


def test_consensus_examples_and_canonical():
    values = tuple(int(bool((not (i & 4) and i & 2) or (i & 4 and i & 1))) for i in range(8))
    a = analyze(values, 'SOP')
    assert a.hazards == ((3, 7),)
    assert '-11' in [g.pattern for g in a.repaired.groups]
    b = analyze(tuple(1-v for v in values), 'POS')
    assert b.hazards == ((3, 7),)
    assert '-11' in [g.pattern for g in b.repaired.groups]
    c = analyze((0, 1, 1, 0))
    assert c.canonical_sop == "A'B + AB'"
    assert c.canonical_pos == "(A + B) · (A' + B')"
    assert analyze((0,)*4).canonical_sop == '0'
    assert analyze((1,)*4).canonical_pos == '1'


@pytest.mark.parametrize('values,form', [((0,)*3,'SOP'),((0,)*4,'bad'),((True,)*4,'SOP')])
def test_invalid(values,form):
    with pytest.raises(ValueError):
        analyze(values,form)
