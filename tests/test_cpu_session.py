import copy
import pytest
from assembler import assemble
from simulator import CPU
import cpu_session
import mano_file

SOURCE = 'ORG 100\nLDA A\nADD B\nSTA C\nHLT\nA, DEC 5\nB, DEC 3\nC, HEX 0000\nEND\n'


def setup():
    p = assemble(SOURCE)
    return CPU(p.words, p.entry)


@pytest.mark.parametrize('steps', range(5))
def test_resume_exact_cpu(tmp_path, steps):
    cpu = setup()
    for _ in range(steps):
        cpu.step()
    path = tmp_path / 'cpu.mano'
    cpu_session.save(path, SOURCE, cpu, steps, {0x103})
    source, program, restored, count, breaks = cpu_session.load(path)
    assert (source, count, breaks) == (SOURCE, steps, {0x103})
    assert restored.registers() == cpu.registers()
    assert restored.memory == cpu.memory
    while not cpu.halted:
        assert restored.step() == cpu.step()
    assert restored.memory[0x106] == 8 and restored.halted


def test_zero_memory_and_pending_io(tmp_path):
    cpu = setup()
    cpu.memory[0x104] = 0
    cpu.memory[4095] = 65535
    cpu.input_byte(42)
    path = tmp_path / 'io.mano'
    cpu_session.save(path, SOURCE, cpu, 0, set())
    _, _, restored, _, _ = cpu_session.load(path)
    assert restored.memory == cpu.memory
    assert restored.inpr == 42 and restored.fgi == 1


def test_partial_instruction_rejected_without_overwrite(tmp_path):
    cpu = setup()
    path = tmp_path / 'cpu.mano'
    cpu_session.save(path, SOURCE, cpu, 0, set())
    before = path.read_bytes()
    cpu.microstep()
    with pytest.raises(ValueError):
        cpu_session.save(path, SOURCE, cpu, 0, set())
    assert path.read_bytes() == before


@pytest.mark.parametrize('key,value', [('source', 'bad instruction'), ('steps', True),
    ('steps', 10001), ('breakpoints', [1, 1]), ('breakpoints', [4096]),
    ('memory', [[0, 1], [0, 2]]), ('memory', [[0, 0]]), ('memory', [[True, 1]]),
    ('memory', [[4096, 1]]), ('memory', [[1, 65536]]), ('registers', {})])
def test_malformed(key, value):
    obj = cpu_session.snapshot(SOURCE, setup(), 0, set())
    obj[key] = value
    with pytest.raises(ValueError):
        cpu_session.restore(obj)


@pytest.mark.parametrize('name,value', [('AC', 65536), ('PC', 4096), ('SC', 1), ('HALTED', 1), ('E', True)])
def test_register_width(name, value):
    obj = cpu_session.snapshot(SOURCE, setup(), 0, set())
    obj['registers'][name] = value
    with pytest.raises(ValueError):
        cpu_session.restore(obj)


def test_wrong_native_kind(tmp_path):
    path = tmp_path / 'other.mano'
    mano_file.save(path, 'asm', SOURCE)
    with pytest.raises(ValueError):
        cpu_session.load(path)


@pytest.mark.parametrize("invalid", [False, 0.0, None])
def test_corrupt_memory_does_not_replace_checkpoint(tmp_path, invalid):
    cpu = setup()
    path = tmp_path / "good.mano"
    cpu_session.save(path, SOURCE, cpu, 0, set())
    before = path.read_bytes()
    cpu.memory[-1] = invalid
    with pytest.raises(ValueError):
        cpu_session.save(path, SOURCE, cpu, 0, set())
    assert path.read_bytes() == before
