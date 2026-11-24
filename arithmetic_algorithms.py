"""Chapter 10 register algorithms; educational models, not Basic Computer opcodes."""
from dataclasses import dataclass
from word_arithmetic import mask_for, signed


@dataclass(frozen=True)
class BoothStep:
    cycle: int
    pair: str
    operation: str
    accumulator_after_operation: int
    accumulator: int
    multiplier: int
    previous_bit: int


@dataclass(frozen=True)
class DivisionStep:
    cycle: int
    shifted_remainder: int
    trial_remainder: int
    restored: bool
    remainder: int
    quotient: int


def booth(multiplicand, multiplier, width):
    """Signed radix-2 Booth; operands are n-bit words, result is signed 2n-bit.
    
    A has n+1 bits to represent both M and -M even for minimum signed M.
    Each row records the actual operation followed by arithmetic right shift.
    """
    mask = mask_for(width)
    m = signed(multiplicand, width)
    signed(multiplier, width)  # validate input word
    a, q, prev = 0, multiplier, 0
    rows = []
    for cycle in range(1, width + 1):
        pair = f"{q & 1}{prev}"
        operation = {"01": "+M", "10": "-M"}.get(pair, "—")
        if pair == "01":
            a += m
        elif pair == "10":
            a -= m
        after_op = a
        prev, q, a = q & 1, ((a & 1) << (width - 1)) | (q >> 1), a >> 1
        rows.append(BoothStep(cycle, pair, operation, after_op, a, q & mask, prev))
    return (a << width) | q, tuple(rows)


def restoring_division(dividend, divisor, width):
    """Unsigned n-bit division, recording each shift, subtraction and restore."""
    mask = mask_for(width)
    if not 0 <= dividend <= mask or not 0 <= divisor <= mask:
        raise ValueError("Operand outside selected word width")
    if divisor == 0:
        raise ValueError("Division by zero")
    r, q = 0, dividend
    rows = []
    for cycle in range(1, width + 1):
        shifted = (r << 1) | (q >> (width - 1))
        q = (q << 1) & mask
        trial = shifted - divisor
        restored = trial < 0
        r = trial + divisor if restored else trial
        if not restored:
            q |= 1
        rows.append(DivisionStep(cycle, shifted, trial, restored, r, q))
    return q, r, tuple(rows)
