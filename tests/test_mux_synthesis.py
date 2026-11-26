from itertools import product
from random import Random
import pytest
from boolean_minimizer import minimize
from mux_synthesis import synthesize_mux
from circuit_document import CircuitDocument


@pytest.mark.parametrize("form",["SOP","POS"])
def test_all_three_variable_functions(form):
    for values in product((0,1),repeat=8):
        doc=synthesize_mux(values,form)
        assert tuple(out[0] for _,out in doc.compile().truth_table())==values


@pytest.mark.parametrize("form",["SOP","POS"])
def test_partial_maps_preserve_completion(form):
    rng=Random(61)
    for _ in range(128):
        values=tuple(rng.choice((0,1,None)) for _ in range(16))
        solution=minimize(values,form)
        expected=tuple(solution.evaluate(i) for i in range(16))
        doc=synthesize_mux(values,form)
        assert tuple(out[0] for _,out in doc.compile().truth_table())==expected
        assert CircuitDocument.loads(doc.dumps())==doc
        assert all(v is None or v==expected[i] for i,v in enumerate(values))
