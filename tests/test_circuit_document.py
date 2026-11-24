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
