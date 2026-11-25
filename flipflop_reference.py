"""Characteristic and excitation tables from the actual clocked model.

X means either input value is allowed, not an unknown output voltage.
The forbidden SR input pair is never included in an excitation.
"""
from itertools import product
from sequential_logic import MODELS, RULES, transition

KINDS = ('D', 'T', 'JK', 'SR')


def characteristic(kind):
    """Rows: current Q, pin values in model order, next Q or None if forbidden."""
    if kind not in KINDS:
        raise ValueError('Expected D, T, JK or SR')
    pins = MODELS[kind][0]
    rows = []
    for q in (0, 1):
        for bits in product((0, 1), repeat=len(pins)):
            try:
                nxt = transition(kind, q, dict(zip(pins, bits)))
            except ValueError:
                if kind != 'SR' or bits != (1, 1):
                    raise
                nxt = None
            rows.append((q, bits, nxt))
    return tuple(rows)


def excitation(kind):
    """Rows: Q, desired next Q, exact valid input tuples, compact X pattern."""
    rows = characteristic(kind)
    result = []
    for q, nxt in product((0, 1), repeat=2):
        choices = tuple(bits for current, bits, following in rows
                        if current == q and following == nxt)
        pattern = ''.join(str(col[0]) if len(set(col)) == 1 else 'X'
                          for col in zip(*choices))
        expanded = tuple(bits for bits in product((0, 1), repeat=len(pattern))
                         if all(p == 'X' or int(p) == b for p, b in zip(pattern, bits)))
        if expanded != choices:
            raise RuntimeError('Excitation pattern would include an invalid input')
        result.append((q, nxt, choices, pattern))
    return tuple(result)


def formula(kind):
    if kind not in KINDS:
        raise ValueError('Expected D, T, JK or SR')
    return RULES[kind][0]
