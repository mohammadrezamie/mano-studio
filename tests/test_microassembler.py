import pytest
from microassembler import assemble_micro, DEMO_SOURCE, full_demo
from microprogram import MicroComputer, Microinstruction


def test_forward_labels_and_fields():
    r=assemble_micro("ORG 64\nstart: READ, INCPC U JMP end\nend: DRTAR U MAP")
    assert r.ok and r.labels=={"START":64,"END":65}
    assert r.words=={64:Microinstruction(0,4,5,0,0,65).encode(),
                     65:Microinstruction(5,0,0,0,3,0).encode()}
    assert r.source_lines=={64:2,65:3}
    assert r.listing().startswith("40:")


@pytest.mark.parametrize("source,code",[
    ("ORG 128\nNOP U JMP NEXT","ADDRESS"),
    ("X: NOP U JMP NEXT\nX: NOP U RET","LABEL"),
    ("NOP U JMP missing","TARGET"),
    ("NOP U RET 5","TARGET"),
    ("ADD, CLRAC U JMP NEXT","CONFLICT"),
    ("ADD, SUB U JMP NEXT","CONFLICT"),
    ("WRITE, READ U JMP NEXT","CONFLICT"),
    ("RESERVED U MAP","OPERATION"),
    ("NOP, READ U MAP","OPERATION"),
    ("ORG 0\nNOP U MAP\nORG 0\nNOP U MAP","OVERLAP"),
    ("READ JMP NEXT","SYNTAX"),
    ("# empty","EMPTY")])
def test_diagnostics_atomic(source,code):
    r=assemble_micro(source)
    assert not r.ok and not r.words and code in {e.code for e in r.errors}
    with pytest.raises(ValueError):r.listing()


def test_next_wrap_and_hex_address():
    r=assemble_micro("ORG 0x7f\nNOP U JMP NEXT")
    assert r.ok and Microinstruction.decode(r.words[127]).ad==0


def finish(c):
    for _ in range(12):
        c.step()
        if c.car==64:return
    raise AssertionError("Did not return to fetch")


@pytest.mark.parametrize("indirect",[False,True])
@pytest.mark.parametrize("opcode",[0,1,2,3])
def test_four_machine_routines(opcode,indirect):
    control,_=full_demo()
    ptr=0x110 if indirect else 0x100
    c=MicroComputer(control,{0:(int(indirect)<<15)|(opcode<<11)|ptr,0x110:0x100,0x100:3})
    c.ac=0xFFFE if opcode==1 else 5
    finish(c)
    if opcode==0:assert c.ac==8 and c.pc==1
    elif opcode==1:assert c.pc==0x100
    elif opcode==2:assert c.memory[0x100]==5 and c.ac==5
    else:assert c.memory[0x100]==5 and c.ac==3


def test_branch_not_taken_and_demo():
    control,memory=full_demo()
    c=MicroComputer(control,{0:0x8900,0x100:0x300})
    c.ac=1
    finish(c)
    assert c.pc==1
    c=MicroComputer(control,memory)
    for _ in range(4):finish(c)
    assert c.ac==0xFFFE and c.memory[0x103]==5 and c.memory[0x104]==5 and c.pc==0x106
