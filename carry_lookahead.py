"""Bounded-fan-in carry look-ahead netlist, using XOR propagate and AND generate.

Signal names follow LSB-first indexing. This module generates structural gate
specifications; the existing Logic Lab engine evaluates and draws them.
"""


def network(width=4):
    """Return (inputs, gate triples, outputs) for widths 2 through 4.

    C_i = G_i OR (P_i AND Cin), with G_i expanded independently for each prefix.
    Fan-in never exceeds four. No physical delay or speedup is claimed.
    """
    if type(width) is not int or not 2 <= width <= 4:
        raise ValueError("Carry look-ahead width must be 2–4")
    inputs = tuple(f"A{i}" for i in range(width)) + tuple(f"B{i}" for i in range(width)) + ("Cin",)
    gates = []

    def add(name, op, *args):
        gates.append((name, op, args))
        return name

    for i in range(width):
        add(f"p{i}", "XOR", f"A{i}", f"B{i}")
        add(f"g{i}", "AND", f"A{i}", f"B{i}")
    carry = "Cin"
    outputs = []
    for i in range(width):
        outputs.append((f"S{i}", add(f"s{i}", "XOR", f"p{i}", carry)))
        terms = [f"g{i}"]
        for j in range(i):
            terms.append(add(f"t{i}_{j}", "AND", f"g{j}", *(f"p{k}" for k in range(j+1, i+1))))
        group_g = add(f"gg{i}", "OR", *terms) if i else terms[0]
        group_p = add(f"gp{i}", "AND", *(f"p{k}" for k in range(i+1))) if i else "p0"
        incoming = add(f"in{i}", "AND", group_p, "Cin")
        carry = add(f"c{i+1}", "OR", group_g, incoming)
    return inputs, tuple(gates), tuple(outputs) + (("Cout", carry),)


def depths(inputs, gates, outputs):
    """Count ideal unit-gate levels, not physical time."""
    levels = dict.fromkeys(inputs, 0)
    for name, _, args in gates:
        levels[name] = 1 + max(levels[arg] for arg in args)
    return {name: levels[source] for name, source in outputs}
