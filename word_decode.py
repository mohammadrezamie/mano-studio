"""Interpret a raw word as a supported instruction, not proof it is executable code."""
from mano_isa import MEMORY_BY_CODE, FIXED_BY_CODE


def decode_word(word):
    if type(word) is not int or not 0 <= word <= 0xFFFF:
        raise ValueError('Expected a 16-bit memory word')
    opcode = (word >> 12) & 7
    if opcode in MEMORY_BY_CODE:
        return f'{MEMORY_BY_CODE[opcode]} {word & 0xFFF:03X}' + (' I' if word & 0x8000 else '')
    return FIXED_BY_CODE.get(word)
