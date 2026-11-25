"""Encode a reachable quotient with explicit recovery for unused codes."""
from dataclasses import dataclass
from itertools import permutations
from state_reduction import reduce_machine
from state_synthesis import design_state_machine, StateDesign


@dataclass(frozen=True)
class Encoding:
    codes: tuple[int, ...]
    unused: tuple[int, ...]
    design: StateDesign
    cost: tuple[int, int]
    candidates: int


def encode_reduced(model):
    """Reset class R0 is code zero. Search all assignments for <=4 classes.

    Larger quotients use ascending codes. Cost is the sum of independent
    SOP terms then literals, not shared hardware area. Unused codes recover
    to zero on either input and emit zero before the edge. A one-state
    quotient uses one bit for compatibility with the existing teaching model.
    """
    reduced = reduce_machine(model)
    count = len(reduced.groups)
    bits = max(1, reduced.bits)
    size = 2**bits
    assignments = ((0, *tail) for tail in permutations(range(1, size), count-1)) if count <= 4 else (tuple(range(count)),)
    best = None
    candidates = 0
    for codes in assignments:
        candidates += 1
        rows = [(0, 0)]*(size*2)
        for r, code in enumerate(codes):
            for x in (0, 1):
                nxt, y = reduced.step(r, x)
                rows[2*code+x] = (codes[nxt], y)
        design = design_state_machine(bits, rows, model.mode, model.flipflop)
        covers = [cover for _, cover in design.equations]
        cost = (sum(len(c.groups) for c in covers),
                sum(g.literals for c in covers for g in c.groups))
        unused = tuple(i for i in range(size) if i not in codes)
        candidate = Encoding(codes, unused, design, cost, 0)
        if best is None or (cost, codes) < (best.cost, best.codes):
            best = candidate
    for q, r in enumerate(reduced.mapping):
        if r is not None:
            for x in (0, 1):
                nxt, y = model.step(q, x)
                if best.design.step(best.codes[r], x) != (best.codes[reduced.mapping[nxt]], y):
                    raise RuntimeError('Encoded quotient does not preserve behavior')
    return Encoding(best.codes, best.unused, best.design, best.cost, candidates)
