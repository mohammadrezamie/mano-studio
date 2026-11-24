"""Exact educational encodings, with explicit bit ordering and validation."""
import re
from dataclasses import dataclass

def _bits(text,length=None):
    text=text.strip().replace(" ","")
    if not text or len(text)>128 or re.fullmatch("[01]+",text) is None or (length is not None and len(text)!=length):
        raise ValueError("Invalid binary code")
    return text

def bcd_encode(decimal):
    decimal=decimal.strip()
    if not 1<=len(decimal)<=32 or re.fullmatch("[0-9]+",decimal) is None:
        raise ValueError("Expected decimal digits")
    return " ".join(f"{int(d):04b}" for d in decimal)

def bcd_decode(code):
    bits=_bits(code)
    if len(bits)%4:
        raise ValueError("BCD requires four bits per digit")
    digits=[int(bits[i:i+4],2) for i in range(0,len(bits),4)]
    if any(d>9 for d in digits):
        raise ValueError("Invalid BCD digit")
    return "".join(str(d) for d in digits)

def binary_to_gray(code):
    bits=_bits(code)
    value=int(bits,2)
    return f"{value^(value>>1):0{len(bits)}b}"

def gray_to_binary(code):
    bits=_bits(code)
    value=int(bits,2)
    result=0
    while value:
        result^=value
        value>>=1
    return f"{result:0{len(bits)}b}"

def ascii_encode(text):
    if not 1<=len(text)<=16 or any(ord(c)>127 for c in text):
        raise ValueError("Expected 1–16 ASCII characters")
    return " ".join(f"{ord(c):07b}" for c in text)

def ascii_decode(code):
    bits=_bits(code)
    if len(bits)%7:
        raise ValueError("ASCII requires seven bits per character")
    return "".join(chr(int(bits[i:i+7],2)) for i in range(0,len(bits),7))

def hamming_encode(data):
    """Even parity, positions 1..7 left to right, data at 3,5,6,7."""
    d=_bits(data,4)
    c=[0]*8
    for pos,bit in zip((3,5,6,7),d):c[pos]=int(bit)
    for parity in (1,2,4):
        c[parity]=sum(c[i] for i in range(1,8) if i&parity)%2
    return "".join(str(x) for x in c[1:])

@dataclass(frozen=True)
class HammingResult:
    syndrome: int
    corrected: str
    data: str

def hamming_decode(code):
    """Single-error correction only; multiple errors may be miscorrected."""
    c=[0]+[int(x) for x in _bits(code,7)]
    syndrome=sum(p for p in (1,2,4) if sum(c[i] for i in range(1,8) if i&p)%2)
    if syndrome:c[syndrome]^=1
    return HammingResult(syndrome,"".join(str(x) for x in c[1:]),"".join(str(c[i]) for i in (3,5,6,7)))
