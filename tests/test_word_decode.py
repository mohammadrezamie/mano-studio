import pytest
from mano_isa import MEMORY, FIXED
from word_decode import decode_word


@pytest.mark.parametrize('name,opcode', MEMORY.items())
def test_every_memory_instruction(name, opcode):
    for indirect in (0, 0x8000):
        for address in range(4096):
            assert decode_word(indirect | (opcode << 12) | address) == (
                f'{name} {address:03X}' + (' I' if indirect else ''))


@pytest.mark.parametrize('name,word', FIXED.items())
def test_fixed(name, word):
    assert decode_word(word) == name


def test_all_reserved_words():
    named = set(FIXED.values())
    for base in (0x7000, 0xF000):
        for bits in range(4096):
            if base | bits not in named:
                assert decode_word(base | bits) is None


@pytest.mark.parametrize('word', [-1, 65536, True, '7001', None])
def test_invalid(word):
    with pytest.raises(ValueError):
        decode_word(word)
