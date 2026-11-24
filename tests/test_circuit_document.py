import pytest
from circuit_document import CircuitDocument
from logic_engine import CIRCUITS, Gate


def test_roundtrip_all_presets():
    for circuit in CIRCUITS.values():
        doc=CircuitDocument.from_circuit(circuit)
        restored=CircuitDocument.loads(doc.dumps())
        assert restored==doc
        assert list(restored.compile().truth_table())==list(circuit.truth_table())


def test_unordered_netlist_is_sorted():
    doc=CircuitDocument(("A","B"),(Gate("Y","NOT",("p",)),Gate("p","AND",("A","B"))),(("Out","Y"),))
    assert doc.compile().result({"A":1,"B":1})=={"Out":0}


@pytest.mark.parametrize("gates",[
    (Gate("q","AND",("A","missing")),),
    (Gate("q","NOT",("q",)),),
    (Gate("q","AND",("A",)),),
    (Gate("A","NOT",("A",)),),
])
def test_bad_connections(gates):
    with pytest.raises(ValueError):
        CircuitDocument(("A",),gates,(("Y",gates[-1].output),)).compile()


def test_invalid_file():
    with pytest.raises(ValueError):
        CircuitDocument.loads('{"format":"unknown","version":1}')


def test_rewire_preserves_original_and_rejects_loop():
    doc=CircuitDocument.from_circuit(CIRCUITS["half_adder"])
    updated=doc.reconnect("A","sum",1)
    assert updated.compile().result({"A":1,"B":0})["S"]==0
    assert doc.compile().result({"A":1,"B":0})["S"]==1
    with pytest.raises(ValueError,match="feedback"):
        doc.reconnect("sum","sum",0)
    with pytest.raises(ValueError):
        doc.reconnect("A","sum",4)
    assert doc.reconnect("A","@S").compile().result({"A":1,"B":1})["S"]==1


def test_positions_roundtrip_and_legacy_v1():
    import json
    doc=CircuitDocument.from_circuit(CIRCUITS["and"])
    moved=doc.with_positions({"A":(20,30),"q":(240,100),"@Y":(500,110)})
    assert CircuitDocument.loads(moved.dumps())==moved
    assert moved.compile().result({"A":1,"B":1})=={"Y":1}
    legacy=json.loads(doc.dumps())
    legacy["version"]=1
    legacy.pop("positions")
    assert CircuitDocument.loads(json.dumps(legacy))==doc


@pytest.mark.parametrize("positions",[{"unknown":(0,0)},{"A":(float("nan"),0)},{"A":(50000,0)}])
def test_invalid_placement(positions):
    doc=CircuitDocument.from_circuit(CIRCUITS["and"])
    with pytest.raises(ValueError):
        doc.with_positions(positions)
