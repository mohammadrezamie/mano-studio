"""Convert a validated combinational circuit into NAND-only or NOR-only gates.

Use two-input universal gates, tied inputs for inversion, and shared
commutative subexpressions. No minimum gate count or timing claim.
"""
from circuit_document import CircuitDocument, MAX_GATES
from logic_engine import Gate


def universalize(document, family):
    if family not in ("NAND", "NOR"):
        raise ValueError("Expected NAND or NOR")
    circuit = document.compile()
    gates = []
    names = set(circuit.inputs) | {name for name, _ in circuit.outputs}
    mapped = {name: name for name in circuit.inputs}
    memo = {}
    serial = 0

    def primitive(a, b):
        nonlocal serial
        key = tuple(sorted((a, b)))
        if key not in memo:
            if len(gates) >= MAX_GATES:
                raise ValueError("Universal circuit exceeds gate limit")
            serial += 1
            while f"u{serial}" in names:
                serial += 1
            name = f"u{serial}"
            names.add(name)
            gates.append(Gate(name, family, key))
            memo[key] = name
        return memo[key]

    def inv(a):
        return primitive(a, a)

    def conj(a, b):
        return inv(primitive(a, b)) if family == "NAND" else primitive(inv(a), inv(b))

    def disj(a, b):
        return primitive(inv(a), inv(b)) if family == "NAND" else inv(primitive(a, b))

    def parity(a, b):
        c = primitive(a, b)
        d = primitive(a, c)
        e = primitive(b, c)
        f = primitive(d, e)
        return f if family == "NAND" else inv(f)

    def reduce_pair(fn, args):
        value = args[0]
        for arg in args[1:]:
            value = fn(value, arg)
        return value

    for gate in circuit.gates:
        args = tuple(mapped[name] for name in gate.inputs)
        if gate.op == "NOT":
            output = inv(args[0])
        elif gate.op in ("AND", "NAND"):
            output = reduce_pair(conj, args)
            if gate.op == "NAND":
                output = inv(output)
        elif gate.op in ("OR", "NOR"):
            output = reduce_pair(disj, args)
            if gate.op == "NOR":
                output = inv(output)
        elif gate.op in ("XOR", "XNOR"):
            output = reduce_pair(parity, args)
            if gate.op == "XNOR":
                output = inv(output)
        else:
            raise ValueError("Unsupported gate")
        mapped[gate.output] = output

    result = CircuitDocument(circuit.inputs, tuple(gates),
                             tuple((name, mapped[signal]) for name, signal in circuit.outputs))
    converted = result.compile()
    if tuple(converted.truth_table()) != tuple(circuit.truth_table()):
        raise RuntimeError("Universal circuit failed equivalence check")
    return result
