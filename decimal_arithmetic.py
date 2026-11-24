"""Packed 8421 BCD arithmetic with observable correction and carry."""
from dataclasses import dataclass
from data_codes import bcd_decode
from word_arithmetic import mask_for


@dataclass(frozen=True)
class DecimalStep:
    position: int
    a: int
    b: int
    carry_in: int
    binary_sum: int
    correction: int
    digit: int
    carry_out: int


@dataclass(frozen=True)
class DecimalResult:
    word: int
    decimal: int
    carry: int
    borrow: int | None
    steps: tuple


def packed_decimal(word, width):
    mask = mask_for(width)
    if not 0 <= word <= mask:
        raise ValueError("Word outside selected width")
    return int(bcd_decode(f"{word:0{width}b}"))


def decimal_alu(operation, a, b, width):
    """ADD or SUB modulo 10**digits; SUB uses nine's complement plus one.

    Carry on SUB means no borrow, not binary ALU carry. Each raw binary
    digit sum (0..19) gets +6 precisely if it exceeds nine.
    """
    if operation not in ("ADD", "SUB"):
        raise ValueError("Invalid decimal operation")
    packed_decimal(a, width)
    packed_decimal(b, width)
    carry = int(operation == "SUB")
    out = 0
    steps = []
    for i in range(width // 4):
        x, y = (a >> (4*i)) & 15, (b >> (4*i)) & 15
        operand = 9-y if operation == "SUB" else y
        raw = x + operand + carry
        correction = 6 if raw > 9 else 0
        corrected = raw + correction
        digit, next_carry = corrected & 15, corrected >> 4
        steps.append(DecimalStep(i,x,operand,carry,raw,correction,digit,next_carry))
        out |= digit << (4*i)
        carry = next_carry
    return DecimalResult(out,packed_decimal(out,width),carry,
                         1-carry if operation == "SUB" else None,tuple(steps))
