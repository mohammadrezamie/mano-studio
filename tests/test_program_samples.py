from pathlib import Path
import pytest
import mano_file
from program_samples import SAMPLES, load_sample

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('sample', SAMPLES, ids=lambda item: item.key)
def test_native_samples(sample):
    actual, source = load_sample(sample.key, ROOT)
    assert actual == sample
    assert source.startswith('ORG 100\n') and source.endswith('END\n')
    assert len(sample.title) == len(sample.task) == 2
    assert sample.steps > 0 and 0 <= sample.ac <= 0xFFFF and sample.e in (0, 1)


def test_exact_catalog_and_native_files():
    keys = [sample.key for sample in SAMPLES]
    assert len(keys) == len(set(keys)) == 13
    assert {p.stem for p in (ROOT / 'examples/programs').glob('*.mano')} == set(keys)


def test_unknown_key_cannot_escape_catalog(tmp_path):
    with pytest.raises(ValueError):
        load_sample('../addition', tmp_path)


@pytest.mark.parametrize('kind,payload', [('rtl', 'AC ← 0'), ('asm', '  ')])
def test_invalid_native_sample(tmp_path, kind, payload):
    folder = tmp_path / 'examples/programs'
    folder.mkdir(parents=True)
    mano_file.save(folder / 'addition.mano', kind, payload)
    with pytest.raises(ValueError):
        load_sample('addition', tmp_path)


@pytest.mark.parametrize('sample', SAMPLES, ids=lambda item: item.key)
def test_cpu_expected_results(sample):
    from assembler import assemble
    from simulator import CPU
    _, source = load_sample(sample.key, ROOT)
    program = assemble(source)
    assert program.ok, program.errors
    cpu = CPU(program.words, program.entry)
    for i in range(sample.steps):
        assert not cpu.halted, f'Unexpected early halt at {i}'
        assert cpu.step() is not None
    assert cpu.halted and cpu.step() is None
    assert (cpu.ac, cpu.e) == (sample.ac, sample.e)
    assert all(cpu.memory[address] == expected for address, expected in sample.memory)


@pytest.mark.parametrize("value,expected,steps", [(0, 0, 5), (7, 7, 5), (0xFFF9, 7, 7), (0x8000, 0x8000, 7)])
def test_absolute_value_sign_paths(value, expected, steps):
    from assembler import assemble
    from simulator import CPU
    _, source = load_sample("absolute-value", ROOT)
    program = assemble(source)
    assert program.ok
    cpu = CPU(program.words, program.entry)
    cpu.memory[program.symbols["VALUE"]] = value
    for _ in range(steps):
        assert not cpu.halted
        assert cpu.step() is not None
    assert cpu.halted and cpu.ac == expected
    assert cpu.memory[program.symbols["RESULT"]] == expected


@pytest.mark.parametrize("a,b", [(0, 0), (0xFFFF, 0), (0xAAAA, 0x5555), (0x1234, 0x00FF), (0x8000, 1)])
def test_logical_or_independent_oracle(a, b):
    from assembler import assemble
    from simulator import CPU
    _, source = load_sample("logical-or", ROOT)
    program = assemble(source)
    assert program.ok, program.errors
    cpu = CPU(program.words, program.entry)
    cpu.memory[program.symbols["FIRST"]] = a
    cpu.memory[program.symbols["SECOND"]] = b
    for _ in range(9):
        assert not cpu.halted
        assert cpu.step() is not None
    assert cpu.halted and cpu.ac == a | b
    assert cpu.memory[program.symbols["RESULT"]] == a | b


@pytest.mark.parametrize("value,count", [(0, 1), (6, 7), (0xFFFF, 2), (0x8000, 2)])
def test_repeated_addition_wraparound(value, count):
    from assembler import assemble
    from simulator import CPU
    _, source = load_sample("multiply-loop", ROOT)
    program = assemble(source)
    assert program.ok, program.errors
    cpu = CPU(program.words, program.entry)
    cpu.memory[program.symbols["VALUE"]] = value
    cpu.memory[program.symbols["COUNT"]] = (-count) & 0xFFFF
    for _ in range(3 * count + 2):
        assert not cpu.halted
        assert cpu.step() is not None
    assert cpu.halted and cpu.ac == (value * count) & 0xFFFF
    assert cpu.memory[program.symbols["RESULT"]] == (value * count) & 0xFFFF
    assert cpu.memory[program.symbols["COUNT"]] == 0
