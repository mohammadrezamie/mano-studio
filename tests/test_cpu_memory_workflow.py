"""Exercise the interaction of memory tools, persistence and CPU execution."""
import csv
from types import SimpleNamespace

import pytest
import mano_file
from cpu_documents import read
from cpu_guard import CpuGuard
from cpu_memory_image import sparse_memory, expand_sparse
from memory_edit import parse_word, write_word
from memory_inspector import parse_address, memory_rows
from memory_export import save as export
from word_decode import decode_word

SOURCE = 'ORG 100\nLDA 200\nADD 201\nSTA 202\nHLT\nORG 200\nDEC 5\nDEC 3\nDEC 0\nEND'


class History:
    def __init__(self, cpu):
        self.cpu = cpu
        self.steps = 1
        self.entries = ['previous']
        self.breakpoints = {0x103}

    def barrier(self):
        self.entries.clear()


def fake_workspace():
    cpu = SimpleNamespace(memory=[0] * 4096, in_progress=False, pending_event=None,
                          registers=lambda: {'PC': 0x101, 'AC': 5})
    return cpu, History(cpu)


def test_model_edit_report_and_native_round_trip(tmp_path):
    cpu, history = fake_workspace()
    guard = CpuGuard(SOURCE, cpu, history)
    address = parse_address('۰xFFF')
    word = parse_word('۷۰۰۱')
    assert write_word(cpu, history, address, word)
    assert guard.is_dirty(SOURCE, cpu, history) and not history.entries
    assert decode_word(dict(memory_rows(cpu.memory, set(), address))[address]) == 'HLT'
    report = tmp_path / 'memory.csv'
    export(report, cpu.memory, set(), address)
    with report.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert rows[-1]['word_hex'] == '7001' and len(rows) == 16
    path = tmp_path / 'image.mano'
    mano_file.save(path, 'cpu-run', {'memory': sparse_memory(cpu.memory)})
    kind, words = read(path, lambda payload: expand_sparse(payload['memory']))
    assert kind == 'cpu-run' and words == {4095: 0x7001}
    restored, debugger = fake_workspace()
    restored.memory = [words.get(i, 0) for i in range(4096)]
    assert restored.memory == cpu.memory
    guard.mark_saved(SOURCE, restored, debugger)
    assert not guard.is_dirty(SOURCE, restored, debugger)
    assert not write_word(restored, debugger, address, word)
    assert debugger.entries == ['previous']
    assert not guard.is_dirty(SOURCE, restored, debugger)


def test_model_invalid_edit_does_not_dirty_or_change_report(tmp_path):
    cpu, history = fake_workspace()
    guard = CpuGuard(SOURCE, cpu, history)
    report = tmp_path / 'memory.csv'
    export(report, cpu.memory, {0})
    before = report.read_bytes()
    with pytest.raises(ValueError):
        write_word(cpu, history, 0, 65536)
    assert not guard.is_dirty(SOURCE, cpu, history)
    assert history.entries == ['previous']
    export(report, cpu.memory, {0})
    assert report.read_bytes() == before


def test_real_cpu_edit_checkpoint_continue(tmp_path):
    from assembler import assemble
    from simulator import CPU
    from execution_history import ExecutionHistory
    import cpu_session

    program = assemble(SOURCE)
    assert program.ok
    cpu = CPU(program.words, program.entry)
    history = ExecutionHistory(cpu)
    history.breakpoints.add(0x103)
    history.step()
    assert cpu.ac == 5 and history.steps == 1
    assert write_word(cpu, history, 0x201, 7)
    assert not history.entries and history.steps == 1
    path = tmp_path / 'changed.mano'
    cpu_session.save(path, SOURCE, cpu, history.steps, history.breakpoints)
    _, _, restored, steps, breaks = cpu_session.load(path)
    assert restored.memory == cpu.memory and restored.registers() == cpu.registers()
    resumed = ExecutionHistory(restored)
    resumed.steps, resumed.breakpoints = steps, breaks
    assert resumed.back() is None
    resumed.step()
    assert restored.ac == 12
    resumed.step()
    assert restored.memory[0x202] == 12 and resumed.should_break()
    resumed.step()
    assert restored.halted and resumed.steps == 4


def test_real_cpu_self_modifying_instruction():
    from assembler import assemble
    from simulator import CPU
    from execution_history import ExecutionHistory

    program = assemble(SOURCE)
    cpu = CPU(program.words, program.entry)
    history = ExecutionHistory(cpu)
    history.step()
    assert write_word(cpu, history, 0x101, 0x7001)
    assert decode_word(cpu.memory[0x101]) == 'HLT'
    assert program.words[0x101] != cpu.memory[0x101]
    assert history.step().mnemonic == 'HLT' and cpu.halted
    assert history.back().mnemonic == 'HLT' and not cpu.halted
    assert cpu.memory[0x101] == 0x7001 and history.back() is None
