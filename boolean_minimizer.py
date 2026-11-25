"""Exact single-output Boolean minimization for 2–4 variable Karnaugh maps.

Minterms use A as the most significant bit. None denotes don't-care.
Minimize term count, then literal count, then choose a stable lexical cover.
No GUI, dependencies, or changes to the academic translator.
"""
from dataclasses import dataclass
from functools import lru_cache
from itertools import product


@dataclass(frozen=True)
class Group:
    pattern: str
    cells: tuple[int, ...]

    @property
    def literals(self):
        return sum(bit != '-' for bit in self.pattern)


@dataclass(frozen=True)
class Solution:
    variables: int
    form: str
    groups: tuple[Group, ...]

    def evaluate(self, index):
        if type(index) is not int or not 0 <= index < 2**self.variables:
            raise ValueError('Invalid minterm index')
        covered = any(index in group.cells for group in self.groups)
        return int(covered if self.form == 'SOP' else not covered)

    @property
    def expression(self):
        if not self.groups:
            return '0' if self.form == 'SOP' else '1'
        terms = []
        for group in self.groups:
            literals = [name + ("'" if bit == ('0' if self.form == 'SOP' else '1') else '')
                        for name, bit in zip('ABCD', group.pattern) if bit != '-']
            if not literals:
                return '1' if self.form == 'SOP' else '0'
            terms.append(''.join(literals) if self.form == 'SOP' else '(' + ' + '.join(literals) + ')')
        return (' + ' if self.form == 'SOP' else ' · ').join(terms)


def gray_indices(variables):
    """Rows use the high bits; columns the low bits, both in Gray order."""
    if type(variables) is not int or variables not in (2, 3, 4):
        raise ValueError('Expected 2–4 variables')
    rows, cols = variables // 2, variables - variables // 2
    gray = lambda i: i ^ (i >> 1)
    return tuple(tuple((gray(r) << cols) | gray(c) for c in range(2**cols))
                 for r in range(2**rows))


def minimize(values, form='SOP'):
    """Cover required 1s (SOP) or 0s (POS) with maximal legal cubes."""
    values = tuple(values)
    n = {4: 2, 8: 3, 16: 4}.get(len(values))
    if n is None or any(v is not None and (type(v) is not int or v not in (0, 1)) for v in values):
        raise ValueError('Expected 4, 8 or 16 values of 0, 1 or None')
    if form not in ('SOP', 'POS'):
        raise ValueError('Expected SOP or POS')
    target = 1 if form == 'SOP' else 0
    required = sum(1 << i for i, v in enumerate(values) if v == target)
    forbidden = sum(1 << i for i, v in enumerate(values) if v == 1-target)
    candidates = []
    for bits in product('01-', repeat=n):
        pattern = ''.join(bits)
        cells = tuple(i for i in range(len(values)) if all(p == '-' or p == b for p, b in zip(pattern, f'{i:0{n}b}')))
        mask = sum(1 << i for i in cells)
        if mask & required and not mask & forbidden:
            candidates.append((Group(pattern, cells), mask))
    primes = [(g, m) for g, m in candidates if not any(m != other and m & other == m for _, other in candidates)]

    def score(groups):
        return len(groups), sum(g.literals for g in groups), tuple(g.pattern for g in groups)

    @lru_cache(None)
    def cover(left):
        if not left:
            return ()
        pivot = left & -left
        choices = (tuple(sorted((g, *cover(left & ~m)), key=lambda g: g.pattern))
                   for g, m in primes if m & pivot)
        return min(choices, key=score)

    return Solution(n, form, cover(required))
