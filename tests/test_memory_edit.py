from types import SimpleNamespace
import pytest
from memory_edit import parse_word, write_word


class History:
    def __init__(self, cpu):
        self.cpu = cpu
        self.entries = [1, 2]
        self.steps = 2
        self.breakpoints = {3}

    def barrier(self):
        self.entries.clear()


def setup():
    cpu = SimpleNamespace(memory=[0] * 4096, in_progress=False, pc=3, halted=False)
    return cpu, History(cpu)


@pytest.mark.parametrize('text,word', [('0', 0), ('ffff', 65535), ('0xAbCD', 0xABCD), ('۱۲۳۴', 0x1234), (' ١٢ ', 0x12)])
def test_word(text, word):
    assert parse_word(text) == word


@pytest.mark.parametrize('text', ['', '0x', '10000', '-1', 'A B', 'G', '+1'])
def test_invalid_word(text):
    with pytest.raises(ValueError):
        parse_word(text)


def test_change_starts_new_segment():
    cpu, history = setup()
    assert write_word(cpu, history, 4095, 65535)
    assert cpu.memory[4095] == 65535 and sum(cpu.memory) == 65535
    assert not history.entries and history.steps == 2 and history.breakpoints == {3}
    assert cpu.pc == 3 and not cpu.halted


def test_no_op_preserves_history():
    cpu, history = setup()
    assert not write_word(cpu, history, 0, 0)
    assert history.entries == [1, 2]


@pytest.mark.parametrize('address,word', [(-1, 1), (4096, 1), (True, 1), (0, -1), (0, 65536), (0, True)])
def test_invalid_preserves_state(address, word):
    cpu, history = setup()
    with pytest.raises(ValueError):
        write_word(cpu, history, address, word)
    assert not any(cpu.memory) and history.entries == [1, 2]


def test_partial_and_wrong_history():
    cpu, history = setup()
    cpu.in_progress = True
    with pytest.raises(ValueError):
        write_word(cpu, history, 0, 1)
    other, _ = setup()
    with pytest.raises(ValueError):
        write_word(other, history, 0, 1)
    assert not any(cpu.memory) and not any(other.memory) and history.entries == [1, 2]
