"""Educational IEEE binary16 arithmetic, exact finite intermediates, nearest-even.

This is not a Mano Basic Computer instruction or a full IEEE exception environment.
NaN results are canonical quiet NaNs; payloads and signaling flags are not modeled.
"""
from dataclasses import dataclass
from fractions import Fraction


def power2(e):
    return Fraction(1 << e) if e >= 0 else Fraction(1, 1 << -e)


@dataclass(frozen=True)
class Half:
    word: int
    sign: int
    exponent: int
    fraction: int
    kind: str
    value: Fraction | None


def decode_half(word):
    if not 0 <= word <= 0xFFFF:
        raise ValueError("Expected a 16-bit word")
    s, e, f = word >> 15, (word >> 10) & 31, word & 1023
    if e == 31:
        return Half(word,s,e,f,"nan" if f else "infinity",None)
    kind = "normal" if e else "subnormal" if f else "zero"
    v = (1024+f)*power2(e-25) if e else f*power2(-24)
    return Half(word,s,e,f,kind,-v if s else v)


@dataclass(frozen=True)
class Rounding:
    exponent: int
    quantum: Fraction
    truncated: int
    remainder: Fraction
    rounded: int


@dataclass(frozen=True)
class FloatResult:
    word: int
    exact: Fraction | None
    rounding: Rounding | None
    status: str


def encode_half(value, zero_sign=0):
    """Round an exact rational once; record the integer rounding decision."""
    value = Fraction(value)
    if zero_sign not in (0,1):
        raise ValueError("Invalid zero sign")
    sign = int(value < 0) if value else zero_sign
    x = abs(value)
    if not x:
        return FloatResult(sign << 15,value,None,"exact")
    e = x.numerator.bit_length() - x.denominator.bit_length()
    if x < power2(e):
        e -= 1
    e = max(e,-14)
    quantum = power2(e-10)
    scaled = x/quantum
    n = scaled.numerator//scaled.denominator
    remainder = scaled-n
    q = n + int(remainder > Fraction(1,2) or (remainder == Fraction(1,2) and n%2))
    trace = Rounding(e,quantum,n,remainder,q)
    if q == 2048:
        e += 1
        q = 1024
    if e > 15:
        return FloatResult((sign << 15)|0x7C00,value,trace,"overflow")
    if q < 1024:
        bits = q
    else:
        bits = ((e+15)<<10)|(q-1024)
    word = (sign << 15)|bits
    return FloatResult(word,value,trace,"exact" if decode_half(word).value == value else "rounded")


def float_alu(op,a_word,b_word):
    if op not in ("ADD","SUB","MUL","DIV"):
        raise ValueError("Invalid floating operation")
    a = decode_half(a_word)
    b = decode_half(b_word ^ (0x8000 if op == "SUB" else 0))
    sign = a.sign ^ b.sign
    def special(word,status):
        return FloatResult(word,None,None,status)
    def inf(s,status="infinity"):
        return special((s<<15)|0x7C00,status)
    if "nan" in (a.kind,b.kind):
        return special(0x7E00,"nan")
    if op in ("ADD","SUB"):
        if a.kind == b.kind == "infinity" and a.sign != b.sign:
            return special(0x7E00,"invalid")
        if a.kind == "infinity":
            return inf(a.sign)
        if b.kind == "infinity":
            return inf(b.sign)
        return encode_half(a.value+b.value,int(a.kind == b.kind == "zero" and a.sign == b.sign == 1))
    if op == "MUL":
        if (a.kind == "infinity" and b.kind == "zero") or (b.kind == "infinity" and a.kind == "zero"):
            return special(0x7E00,"invalid")
        if "infinity" in (a.kind,b.kind):
            return inf(sign)
        return encode_half(a.value*b.value,sign)
    if a.kind == b.kind and a.kind in ("zero","infinity"):
        return special(0x7E00,"invalid")
    if a.kind == "infinity":
        return inf(sign)
    if b.kind == "infinity":
        return encode_half(0,sign)
    if b.kind == "zero":
        return inf(sign,"divide by zero")
    return encode_half(a.value/b.value,sign)
