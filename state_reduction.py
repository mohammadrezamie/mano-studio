"""Minimal reachable behavioral quotient, without changing the encoded design."""
from dataclasses import dataclass
from state_analysis import analyze_machine


@dataclass(frozen=True)
class ReducedMachine:
    groups: tuple[tuple[int, ...], ...]
    table: tuple[tuple[int, int], ...]
    mapping: tuple[int | None, ...]

    @property
    def bits(self):
        return (len(self.groups)-1).bit_length()

    def step(self, state, x):
        if type(state) is not int or not 0 <= state < len(self.groups) or type(x) is not int or x not in (0, 1):
            raise ValueError('Invalid reduced state or input')
        return self.table[2*state+x]


def reduce_machine(model):
    """Remove unreachable states, then merge reachable equivalent states.

    R0 contains reset Q=0. The quotient has abstract states, not a padded
    binary encoding; a one-state machine requires zero state bits ideally.
    """
    analysis = analyze_machine(model)
    reached = set(dict(analysis.paths))
    groups = tuple(g for group in analysis.classes
                   if (g := tuple(q for q in group if q in reached)))
    mapping = [None]*(2**model.bits)
    for i,group in enumerate(groups):
        for q in group:
            mapping[q] = i
    table = []
    for group in groups:
        for x in (0,1):
            targets = {(mapping[nxt],y) for q in group
                       for nxt,y in (model.step(q,x),)}
            if len(targets) != 1 or any(nxt is None for nxt,_ in targets):
                raise RuntimeError('Invalid reachable equivalence class')
            table.append(targets.pop())
    return ReducedMachine(groups,tuple(table),tuple(mapping))
