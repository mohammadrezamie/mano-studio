"""Cross-check RTL -> ASM -> 16-bit words against independent opcode fixtures."""
import pytest
from rtl_translator import translate
from assembler import assemble


MEMORY = (
    (0x0000, 'AC ← AC ∧ M[{a}]'),
    (0x1000, 'AC ← AC + M[{a}]'),
    (0x2000, 'AC ← M[{a}]'),
    (0x3000, 'M[{a}] ← AC'),
    (0x4000, 'PC ← {a}'),
    (0x5000, 'M[{a}] ← PC, PC ← {a} + 1'),
    (0x6000, 'M[{a}] ← M[{a}] + 1, IF M[{a}] = 0 THEN PC ← PC + 1'),
)
FIXED = (
    (0x7800, 'AC ← 0'), (0x7400, 'E ← 0'), (0x7200, 'AC ← ¬AC'),
    (0x7100, 'E ← ¬E'), (0x7080, 'E:AC ← CIR(E:AC)'),
    (0x7040, 'E:AC ← CIL(E:AC)'), (0x7020, 'AC ← AC + 1'),
    (0x7010, 'IF AC[15] = 0 THEN PC ← PC + 1'),
    (0x7008, 'IF AC[15] = 1 THEN PC ← PC + 1'),
    (0x7004, 'IF AC = 0 THEN PC ← PC + 1'),
    (0x7002, 'IF E = 0 THEN PC ← PC + 1'), (0x7001, 'S ← 0'),
    (0xF800, 'AC[7:0] ← INPR, FGI ← 0'),
    (0xF400, 'OUTR ← AC[7:0], FGO ← 0'),
    (0xF200, 'IF FGI = 1 THEN PC ← PC + 1'),
    (0xF100, 'IF FGO = 1 THEN PC ← PC + 1'),
    (0xF080, 'IEN ← 1'), (0xF040, 'IEN ← 0'),
)


@pytest.mark.parametrize('opcode,template', MEMORY)
@pytest.mark.parametrize('indirect', [False, True])
def test_full_memory_image(opcode, template, indirect):
    lines = []
    for address in range(4096):
        token = f'{address:x}'
        if indirect:
            token = f'M[{token}]'
        lines.append(template.format(a=token))
    rtl = translate('\n'.join(lines))
    assert rtl.ok, rtl.diagnostics[:3]
    asm = assemble(rtl.assembly)
    assert asm.ok, asm.errors[:3]
    prefix = opcode | (0x8000 if indirect else 0)
    assert asm.words == {a: prefix | a for a in range(4096)}
    assert asm.source_lines == {a: a + 1 for a in range(4096)}
    assert asm.entry == 0
    assert asm.listing().splitlines()[-1] == f'FFF: {prefix | 0xFFF:04X}'
    # One more instruction must fail, never return a partial memory image.
    overflow = assemble(rtl.assembly + '\nHLT')
    assert not overflow.ok and not overflow.words and not overflow.source_lines


@pytest.mark.parametrize('word,source', FIXED)
def test_fixed_opcode(word, source):
    rtl = translate(source)
    assert rtl.ok
    asm = assemble(rtl.assembly)
    assert asm.ok and asm.words == {0: word}


def test_mixed_program_and_source_mapping():
    source = '# comment\nAC ← M[100]\n\nAC ← AC + M[M[101]]\nM[102] ← AC\nS ← 0\n'
    rtl = translate(source)
    assert rtl.ok and [i.line for i in rtl.instructions] == [2, 4, 5, 6]
    # ORG is an assembler directive, not accepted as RTL.
    asm = assemble('ORG 200\n' + rtl.assembly + '\nEND')
    assert asm.ok and asm.entry == 0x200
    assert asm.words == {0x200: 0x2100, 0x201: 0x9101, 0x202: 0x3102, 0x203: 0x7001}
    assert asm.source_lines == {0x200: 2, 0x201: 3, 0x202: 4, 0x203: 5}
    assert not translate('ORG 200').ok


def test_invalid_rtl_cannot_produce_assembly():
    rtl = translate('AC ← M[100]\nAR ← PC\nS ← 0')
    assert not rtl.ok
    with pytest.raises(ValueError):
        assemble(rtl.assembly)
