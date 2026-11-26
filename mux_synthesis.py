"""Realize the selected Karnaugh completion via a Shannon MUX network."""
from boolean_minimizer import minimize
from mux_network import network
from logic_engine import Gate
from circuit_document import CircuitDocument


def synthesize_mux(values, form="SOP"):
    values = tuple(values)
    solution = minimize(values, form)
    completed = tuple(solution.evaluate(i) for i in range(len(values)))
    inputs, gates, outputs, _ = network(completed)
    doc = CircuitDocument(inputs, tuple(Gate(name, op, args) for name, op, args in gates), outputs)
    if tuple(out[0] for _, out in doc.compile().truth_table()) != completed:
        raise RuntimeError("MUX network failed equivalence")
    return doc
