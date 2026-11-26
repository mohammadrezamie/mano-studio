"""Insert validated combinational documents through the shared circuit engine."""
from block_composition import insert
from circuit_document import CircuitDocument
from logic_engine import Gate


def compose(base, block, prefix, bindings):
    b, c = base.compile(), block.compile()
    triples = lambda circuit: tuple((g.output, g.op, g.inputs) for g in circuit.gates)
    inputs, gates, outputs = insert(b.inputs, triples(b), b.outputs,
                                    c.inputs, triples(c), c.outputs, prefix, bindings)
    result = CircuitDocument(inputs, tuple(Gate(*g) for g in gates), outputs)
    result.compile()
    # Reset layout: automatic routing handles the combined topology.
    return result
