"""Explicit debugger memory edits; never rewind across external changes."""
import re
from memory_inspector import DIGITS


def parse_word(text):
    value = text.strip().translate(DIGITS)
    if value[:2].lower() == '0x':
        value = value[2:]
    if not re.fullmatch(r'[0-9a-fA-F]{1,4}', value):
        raise ValueError('Enter hexadecimal word 0000–FFFF')
    return int(value, 16)


def write_word(cpu, history, address, word):
    if history.cpu is not cpu:
        raise ValueError('History does not match CPU')
    if type(address) is not int or not 0 <= address < 4096:
        raise ValueError('Invalid memory address')
    if type(word) is not int or not 0 <= word <= 65535:
        raise ValueError('Invalid memory word')
    if cpu.in_progress:
        raise ValueError('Finish or rewind current instruction first')
    old = cpu.memory[address]
    if old == word:
        return False
    history.barrier()
    cpu.memory[address] = word
    return True
