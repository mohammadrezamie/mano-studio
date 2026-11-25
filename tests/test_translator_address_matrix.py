"""Independent classroom regression: all memory addresses, both addressing modes.

Run from the repository root: python -m pytest -q tests/test_translator_address_matrix.py
Expected mnemonics and RTL fixtures are intentionally not imported from the catalog.
"""
import subprocess
import sys
from pathlib import Path

import pytest
from rtl_translator import translate


MEMORY = (
    ('LDA', 'AC ← M[{a}]'),
    ('ADD', 'AC ← AC + M[{a}]'),
    ('STA', 'M[{a}] ← AC'),
    ('AND', 'AC ← AC ∧ M[{a}]'),
    ('BUN', 'PC ← {a}'),
    ('BSA', 'M[{a}] ← PC, PC ← {a} + 1'),
    ('ISZ', 'M[{a}] ← M[{a}] + 1, IF M[{a}] = 0 THEN PC ← PC + 1'),
)
FIXED = (
    ('CLA', 'AC ← 0'), ('CLE', 'E ← 0'), ('CMA', 'AC ← ¬AC'),
    ('CME', 'E ← ¬E'), ('CIR', 'E:AC ← CIR(E:AC)'),
    ('CIL', 'E:AC ← CIL(E:AC)'), ('INC', 'AC ← AC + 1'),
    ('SPA', 'IF AC[15] = 0 THEN PC ← PC + 1'),
    ('SNA', 'IF AC[15] = 1 THEN PC ← PC + 1'),
    ('SZA', 'IF AC = 0 THEN PC ← PC + 1'),
    ('SZE', 'IF E = 0 THEN PC ← PC + 1'), ('HLT', 'S ← 0'),
    ('INP', 'AC[7:0] ← INPR, FGI ← 0'), ('OUT', 'OUTR ← AC[7:0], FGO ← 0'),
    ('SKI', 'IF FGI = 1 THEN PC ← PC + 1'),
    ('SKO', 'IF FGO = 1 THEN PC ← PC + 1'),
    ('ION', 'IEN ← 1'), ('IOF', 'IEN ← 0'),
)


def variant(rtl, style):
    if style == 0:
        return rtl
    if style == 1:
        return rtl.lower().replace('←', '<-').replace('∧', '&').replace('¬', '~').replace(' ', '\t')
    return '  ' + rtl.replace('←', '=').replace('∧', '&').replace('¬', '~') + '  # comment'


@pytest.mark.parametrize('mnemonic,template', MEMORY)
@pytest.mark.parametrize('indirect', [False, True])
def test_all_12bit_addresses(mnemonic, template, indirect):
    lines, expected = [], []
    for address in range(4096):
        # Short, mixed-case hex spelling plus all three assignment spellings.
        token = f'{address:x}' if address % 2 else f'{address:03X}'
        if indirect:
            token = f'M[{token}]'
        lines.append(variant(template.format(a=token), address % 3))
        expected.append(f'{mnemonic} {address:03X}' + (' I' if indirect else ''))
    result = translate('\r\n'.join(lines))
    assert result.ok, result.diagnostics[:3]
    assert result.assembly.splitlines() == expected
    assert tuple(i.line for i in result.instructions) == tuple(range(1, 4097))


@pytest.mark.parametrize('style', range(3))
def test_all_fixed_forms(style):
    result = translate('\n'.join(variant(rtl, style) for _, rtl in FIXED))
    assert result.ok
    assert result.assembly.splitlines() == [name for name, _ in FIXED]


@pytest.mark.parametrize('mnemonic,template', MEMORY)
@pytest.mark.parametrize('indirect', [False, True])
def test_reject_out_of_range(mnemonic, template, indirect):
    token = '1000'
    if indirect:
        token = f'M[{token}]'
    result = translate(' # header\n\n  ' + template.format(a=token))
    assert not result.ok and not result.instructions
    assert result.diagnostics[0].line == 3
    assert result.diagnostics[0].code == 'ADDRESS_RANGE'
    with pytest.raises(ValueError):
        _ = result.assembly


def test_cli_isolated(tmp_path):
    # Copy only the actual translator, not the package or GUI.
    import rtl_translator
    script = tmp_path / 'rtl_translator.py'
    script.write_bytes(Path(rtl_translator.__file__).read_bytes())
    src = tmp_path / 'تمرین.rtl'
    dest = tmp_path / 'خروجی.asm'
    valid = '\r\n'.join(template.format(a='a') for _, template in MEMORY) + '\r\n' + '\r\n'.join(rtl for _, rtl in FIXED)
    src.write_bytes(b'\xef\xbb\xbf' + valid.encode('utf-8'))
    args = [sys.executable, '-I', '-S', str(script), str(src), '-o', str(dest)]
    completed = subprocess.run(args, capture_output=True, timeout=20)
    assert completed.returncode == 0, completed.stderr
    expected = [f'{name} 00A' for name, _ in MEMORY] + [name for name, _ in FIXED]
    assert dest.read_text(encoding='utf-8').splitlines() == expected
    old = dest.read_bytes()
    src.write_text('AC ← M[100]\nAR ← PC\nS ← 0', encoding='utf-8')
    completed = subprocess.run(args, capture_output=True, timeout=20)
    assert completed.returncode != 0
    assert b'2:1: UNSUPPORTED_RTL' in completed.stderr
    assert dest.read_bytes() == old
