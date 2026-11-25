"""Finite-state teaching model: one binary input and one binary output.

All encoded states are explicitly defined; Q MSB first, then X, maps to A-D.
Excitation covers reuse exact single-output minimization; no shared-gate or
state-assignment optimization, physical timing, or asynchronous reset model.
"""
from dataclasses import dataclass
from boolean_minimizer import Solution, minimize


@dataclass(frozen=True)
class StateDesign:
    bits: int
    mode: str
    flipflop: str
    table: tuple[tuple[int, int], ...]
    equations: tuple[tuple[str, Solution], ...]

    @property
    def aliases(self):
        return tuple(zip('ABCD', tuple(f'Q{i}' for i in reversed(range(self.bits))) + ('X',)))

    def step(self, state, x):
        if type(state) is not int or not 0 <= state < 2**self.bits or type(x) is not int or x not in (0, 1):
            raise ValueError('Invalid state or input')
        index = state*2 + x
        signals = {name: cover.evaluate(index) for name, cover in self.equations}
        next_state = 0
        for i in range(self.bits):
            q = (state >> i) & 1
            if self.flipflop == 'D':
                bit = signals[f'D{i}']
            elif self.flipflop == 'T':
                bit = q ^ signals[f'T{i}']
            else:
                bit = (1-signals[f'K{i}']) if q else signals[f'J{i}']
            next_state |= bit << i
        return next_state, signals['Y']


def design_state_machine(bits, table, mode='Mealy', flipflop='D'):
    """Synthesize D, T or JK excitations and output from a complete state table."""
    if type(bits) is not int or bits not in (1, 2, 3):
        raise ValueError('Expected 1–3 state bits')
    if mode not in ('Mealy', 'Moore') or flipflop not in ('D', 'T', 'JK'):
        raise ValueError('Unknown machine or flip-flop type')
    table = tuple(tuple(row) for row in table)
    if len(table) != 2**(bits+1) or any(len(row) != 2 or type(row[0]) is not int or
            not 0 <= row[0] < 2**bits or type(row[1]) is not int or row[1] not in (0, 1) for row in table):
        raise ValueError('Expected next state and binary output for every state/input pair')
    if mode == 'Moore' and any(table[i][1] != table[i+1][1] for i in range(0,len(table),2)):
        raise ValueError('Moore output must depend only on current state')
    equations = []
    for i in reversed(range(bits)):
        q = [(index//2 >> i) & 1 for index in range(len(table))]
        nxt = [(row[0] >> i) & 1 for row in table]
        if flipflop == 'D':
            equations.append((f'D{i}', minimize(nxt)))
        elif flipflop == 'T':
            equations.append((f'T{i}', minimize(a ^ b for a,b in zip(q,nxt))))
        else:
            equations.append((f'J{i}', minimize(None if a else b for a,b in zip(q,nxt))))
            equations.append((f'K{i}', minimize(1-b if a else None for a,b in zip(q,nxt))))
    equations.append(('Y', minimize(row[1] for row in table)))
    result = StateDesign(bits, mode, flipflop, table, tuple(equations))
    for index, expected in enumerate(table):
        if result.step(index//2, index%2) != expected:
            raise RuntimeError('Excitation cover does not implement state table')
    return result


@dataclass(frozen=True)
class StateEdge:
    destination: int
    conditions: tuple[tuple[int, int], ...]


def outgoing_edges(model, state):
    """Group actual evaluated outgoing transitions by destination, in X order."""
    grouped = {}
    for x in (0, 1):
        destination, y = model.step(state, x)
        grouped.setdefault(destination, []).append((x, y))
    return tuple(StateEdge(destination, tuple(conditions))
                 for destination, conditions in grouped.items())
