import pytest
from assembler import assemble
from mano_isa import MEMORY, FIXED
from simulator import CPU


@pytest.mark.parametrize("name,code", list(FIXED.items()))
def test_fixed_encoding(name, code):
    assert assemble(name).words == {0: code}


@pytest.mark.parametrize("name,code", list(MEMORY.items()))
@pytest.mark.parametrize("indirect", [False, True])
def test_address_encoding(name, code, indirect):
    result = assemble(name + " 123" + (" I" if indirect else ""))
    assert result.words == {0: (code << 12) | 0x123 | (0x8000 if indirect else 0)}


def test_labels_and_origin():
    result = assemble("ORG 020\nLDA A\nADD B\nSTA C\nHLT\nA, DEC 5\nB, DEC 3\nC, HEX 0000\nEND")
    assert result.ok and result.entry == 0x20
    assert result.words[0x20] == 0x2024
    cpu = CPU(result.words, result.entry)
    assert [cpu.step().mnemonic for _ in range(4)] == ["LDA", "ADD", "STA", "HLT"]
    assert cpu.memory[0x26] == 8 and cpu.halted


@pytest.mark.parametrize("source", ["LDA MISSING", "ORG 1000", "HLT 1", "HEX FFFFF", "DEC -32769", "ORG FFF\nCLA\nHLT", "A, CLA\nA, HLT", "CLA\nORG 0\nHLT", "END\nCLA", "LDA 001 Z"])
def test_reject_invalid_assembly(source):
    result = assemble(source)
    assert not result.ok and not result.words
    with pytest.raises(ValueError):
        result.listing()


def test_indirect_and_carry():
    cpu = CPU({0:0xA100,1:0x1101,0x100:0x0200,0x200:0xFFFF,0x101:1})
    assert cpu.step().effective_address == 0x200
    assert cpu.ac == 0xFFFF
    cpu.step()
    assert (cpu.ac,cpu.e) == (0,1)


def test_bsa_return_and_isz():
    cpu = CPU({0:0x5100,0x101:0xC100,1:0x6200,0x200:0xFFFF})
    event = cpu.step()
    assert cpu.pc == 0x101 and event.writes == ((0x100,0,1),)
    cpu.step()
    assert cpu.pc == 1
    cpu.step()
    assert cpu.pc == 3 and cpu.memory[0x200] == 0


@pytest.mark.parametrize("op,ac,e,expected", [
    ("CLA",0x1234,1,(0,1)), ("CLE",0x1234,1,(0x1234,0)),
    ("CMA",0x1234,1,(0xEDCB,1)), ("CME",0,1,(0,0)),
    ("CIR",1,1,(0x8000,1)), ("CIL",0x8000,1,(1,1)),
    ("INC",0xFFFF,1,(0,1))])
def test_register_ops(op,ac,e,expected):
    cpu = CPU({0:FIXED[op]})
    cpu.ac,cpu.e=ac,e
    cpu.step()
    assert (cpu.ac,cpu.e)==expected


@pytest.mark.parametrize("op,ac,e,skip", [
    ("SPA",0,0,True),("SPA",0x8000,0,False),("SNA",0x8000,0,True),
    ("SNA",0,0,False),("SZA",0,0,True),("SZA",1,0,False),
    ("SZE",0,0,True),("SZE",0,1,False)])
def test_skip_conditions(op,ac,e,skip):
    cpu=CPU({0:FIXED[op]})
    cpu.ac,cpu.e=ac,e
    cpu.step()
    assert cpu.pc == (2 if skip else 1)


def test_io_and_interrupt():
    cpu = CPU({0:FIXED["INP"],1:FIXED["OUT"],2:FIXED["ION"]})
    cpu.ac=0xAA00
    cpu.input_byte(0x42)
    cpu.step()
    assert cpu.ac==0xAA42 and cpu.fgi==0
    cpu.step()
    assert cpu.output_byte()==0x42 and cpu.fgo==1
    cpu.step()
    assert cpu.step().mnemonic=="INT" and cpu.memory[0]==3 and cpu.pc==1 and cpu.ien==0


def test_unsupported_word_does_not_mutate():
    cpu=CPU({0:0x7FFF})
    before=cpu.registers()
    with pytest.raises(ValueError):
        cpu.step()
    assert cpu.registers()==before
