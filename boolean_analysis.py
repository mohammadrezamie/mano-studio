"""Canonical forms and single-input static hazard analysis for Boolean covers."""
from dataclasses import dataclass
from itertools import combinations
from boolean_minimizer import Group, Solution, minimize


@dataclass(frozen=True)
class Analysis:
    solution: Solution
    completed: tuple[int, ...]
    minterms: tuple[int, ...]
    maxterms: tuple[int, ...]
    dont_cares: tuple[int, ...]
    canonical_sop: str
    canonical_pos: str
    hazards: tuple[tuple[int, int], ...]
    repaired: Solution


def _edges(solution, completed):
    target = int(solution.form == 'SOP')
    return tuple((a, b) for a, b in combinations(range(len(completed)), 2)
                 if completed[a] == completed[b] == target
                 and (a ^ b).bit_count() == 1
                 and not any(a in g.cells and b in g.cells for g in solution.groups))


def analyze(values, form='SOP'):
    """Preserve the chosen X completion; add consensus cubes for uncovered edges.

    Static-1 SOP and static-0 POS only, ideal two-level realization. The repair
    is deterministic, not a minimum redundant cover or a timing simulation.
    """
    values = tuple(values)
    solution = minimize(values, form)
    n = solution.variables
    completed = tuple(solution.evaluate(i) for i in range(len(values)))
    ones = tuple(i for i, value in enumerate(completed) if value == 1)
    zeros = tuple(i for i, value in enumerate(completed) if value == 0)
    xs = tuple(i for i, value in enumerate(values) if value is None)

    def literals(i, sop):
        return [name + ("'" if bit == ('0' if sop else '1') else '')
                for name, bit in zip('ABCD', f'{i:0{n}b}')]

    sop = ' + '.join(''.join(literals(i, True)) for i in ones) or '0'
    pos = ' · '.join('(' + ' + '.join(literals(i, False)) + ')' for i in zeros) or '1'
    edges = _edges(solution, completed)
    groups = list(solution.groups)
    for a, b in edges:
        pattern = ''.join(x if x == y else '-' for x, y in zip(f'{a:0{n}b}', f'{b:0{n}b}'))
        groups.append(Group(pattern, (a, b)))
    repaired = Solution(n, form, tuple(sorted(groups, key=lambda g: g.pattern)))
    if any(repaired.evaluate(i) != v for i, v in enumerate(completed)) or _edges(repaired, completed):
        raise RuntimeError('Static cover repair failed')
    return Analysis(solution, completed, ones, zeros, xs, sop, pos, edges, repaired)
