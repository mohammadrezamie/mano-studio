"""Turn an exact minimized Boolean cover into the existing editable netlist.

The cover is the source of truth; the display expression is never parsed.
This is two-level functional synthesis, not a minimum gate-count optimizer.
"""
from logic_engine import Gate
from circuit_document import CircuitDocument
from boolean_minimizer import minimize


def synthesize(values, form="SOP"):
    """Return a validated circuit implementing one allowed completion of the map."""
    values = tuple(values)
    solution = minimize(values, form)
    inputs = tuple("ABCD"[:solution.variables])
    gates = []
    inverted = {}

    def gate(op, *signals):
        output = f"g{len(gates)+1}"
        gates.append(Gate(output, op, tuple(signals)))
        return output

    def invert(signal):
        if signal not in inverted:
            inverted[signal] = gate("NOT", signal)
        return inverted[signal]

    def combine(op, signals):
        signals = list(signals)
        # Existing functional gates accept 2–4 inputs. Reduce large covers in
        # bounded fan-in stages; a single signal needs no buffer gate.
        while len(signals) > 4:
            signals = [gate(op, *signals[:4]), *signals[4:]]
        return signals[0] if len(signals) == 1 else gate(op, *signals)

    def constant(value):
        a = inputs[0]
        return gate("OR" if value else "AND", a, invert(a))

    sop = form == "SOP"
    if not solution.groups:
        output = constant(int(not sop))
    elif any(group.literals == 0 for group in solution.groups):
        output = constant(int(sop))
    else:
        terms = []
        for group in solution.groups:
            literals = [invert(name) if bit == ("0" if sop else "1") else name
                        for name, bit in zip(inputs, group.pattern) if bit != "-"]
            terms.append(combine("AND" if sop else "OR", literals))
        output = combine("OR" if sop else "AND", terms)
    document = CircuitDocument(inputs, tuple(gates), (("F", output),))
    circuit = document.compile()
    # Validate every cell, including the deterministic chosen X completion.
    for index, (bits, outputs) in enumerate(circuit.truth_table()):
        if outputs != (solution.evaluate(index),):
            raise RuntimeError("Synthesized circuit does not match the Boolean cover")
    return document


def comparison_rows(values, form="SOP"):
    """Return (index, specified value, cover value, gate output) for every input."""
    values = tuple(values)
    solution = minimize(values, form)
    circuit = synthesize(values, form).compile()
    return tuple((i, values[i], solution.evaluate(i), outputs[0])
                 for i, (_, outputs) in enumerate(circuit.truth_table()))
