from itertools import product
from random import Random
import pytest
from logic_engine import CIRCUITS, Gate, basic
from circuit_document import CircuitDocument, MAX_GATES
from boolean_synthesis import synthesize
from universal_gates import universalize


@pytest.mark.parametrize("family", ["NAND","NOR"])
@pytest.mark.parametrize("op", ["NOT","AND","OR","NAND","NOR","XOR","XNOR"])
def test_each_gate(family,op):
    for count in ((1,) if op=="NOT" else (2,3,4)):
        doc=CircuitDocument.from_circuit(basic(op,count))
        result=universalize(doc,family)
        assert all(g.op==family and len(g.inputs)==2 for g in result.gates)
        assert tuple(doc.compile().truth_table())==tuple(result.compile().truth_table())


@pytest.mark.parametrize("family", ["NAND","NOR"])
def test_library(family):
    for c in CIRCUITS.values():
        doc=CircuitDocument.from_circuit(c)
        try:
            result=universalize(doc,family)
        except ValueError as exc:
            assert str(exc)=="Universal circuit exceeds gate limit"
            continue
        assert result.outputs and [n for n,_ in result.outputs]==[n for n,_ in doc.outputs]
        assert all(g.op==family for g in result.gates)
        assert tuple(CircuitDocument.loads(result.dumps()).compile().truth_table())==tuple(c.truth_table())


@pytest.mark.parametrize("family", ["NAND","NOR"])
@pytest.mark.parametrize("form", ["SOP","POS"])
def test_all_three_variable_maps(family,form):
    for values in product((0,1),repeat=8):
        converted=universalize(synthesize(values,form),family).compile()
        assert tuple(out[0] for _,out in converted.truth_table())==values
        assert all(g.op==family for g in converted.gates)


@pytest.mark.parametrize("family", ["NAND","NOR"])
def test_incomplete_maps_and_constant(family):
    rng=Random(908)
    for form in ("SOP","POS"):
        for values in [(0,)*16,(1,)*16,(None,)*16]+[tuple(rng.choice((0,1,None)) for _ in range(16)) for _ in range(64)]:
            doc=synthesize(values,form)
            result=universalize(doc,family)
            assert tuple(doc.compile().truth_table())==tuple(result.compile().truth_table())
            assert all(g.op==family for g in result.gates)


def test_aliases_names_and_limit():
    doc=CircuitDocument(("u1","A"),(Gate("Y","NOT",("A",)),), (("u2","Y"),("Direct","u1"),("Alias","Y")))
    result=universalize(doc,"NAND")
    assert result.gates[0].output=="u3"
    assert result.outputs==(("u2","u3"),("Direct","u1"),("Alias","u3"))
    assert doc.gates[0].op=="NOT"
    with pytest.raises(ValueError,match="Expected NAND or NOR"):
        universalize(doc,"AND")
    gates=[]
    prior="A"
    for i in range(MAX_GATES):
        output=f"g{i}"
        gates.append(Gate(output,"XOR",(prior,"B","C","D")))
        prior=output
    large=CircuitDocument(("A","B","C","D"),tuple(gates),(("Y",prior),))
    with pytest.raises(ValueError,match="exceeds gate limit"):
        universalize(large,"NAND")
