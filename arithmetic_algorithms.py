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


@dataclass(frozen=True)
class NonRestoringStep:
    cycle: int
    shifted_remainder: int
    operation: str
    partial_remainder: int
    quotient: int


@dataclass(frozen=True)
class NonRestoringResult:
    quotient: int
    remainder: int
    steps: tuple
    correction: int


def nonrestoring_division(dividend, divisor, width):
    """Unsigned radix-2: select add/subtract from the old remainder sign.
    
    Emit the new quotient bit from the new sign. Correct a negative final
    remainder once; the intermediate signed register has n+1 bits.
    """
    mask = mask_for(width)
    if not 0 <= dividend <= mask or not 0 <= divisor <= mask:
        raise ValueError("Operand outside selected word width")
    if divisor == 0:
        raise ValueError("Division by zero")
    r, q = 0, dividend
    rows = []
    for cycle in range(1, width + 1):
        subtract = r >= 0
        shifted = 2 * r + (q >> (width - 1))
        r = shifted - divisor if subtract else shifted + divisor
        q = ((q << 1) & mask) | int(r >= 0)
        rows.append(NonRestoringStep(cycle, shifted, "-B" if subtract else "+B", r, q))
    correction = divisor if r < 0 else 0
    return NonRestoringResult(q, r + correction, tuple(rows), correction)


@dataclass(frozen=True)
class SignedDivisionResult:
    quotient: int
    remainder: int
    steps: tuple
    magnitude_dividend: int
    magnitude_divisor: int
    overflow: bool


def signed_division(dividend_word, divisor_word, width):
    """Two's complement input; divide magnitudes, then apply signs.
    
    Quotient truncates toward zero; nonzero remainder follows dividend sign.
    Return mathematical result and explicit overflow instead of silently wrapping.
    """
    a, b = signed(dividend_word, width), signed(divisor_word, width)
    q, r, steps = restoring_division(abs(a), abs(b), width)
    if (a < 0) != (b < 0):
        q = -q
    if a < 0:
        r = -r
    bound = 1 << (width - 1)
    return SignedDivisionResult(q, r, steps, abs(a), abs(b), not -bound <= q < bound)
