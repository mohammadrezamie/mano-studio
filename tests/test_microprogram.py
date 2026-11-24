import pytest
from microprogram import Microinstruction,MicroComputer,demo_images,parse_image


def test_all_field_layouts():
    for value in range(1<<20):
        assert Microinstruction.decode(value).encode()==value


@pytest.mark.parametrize("op",range(16))
def test_map(op):
    c=MicroComputer({64:Microinstruction(0,0,0,3,3,127).encode()})
    c.dr=0x8000|(op<<11)|0x7FF
    e=c.step()
    assert c.car==op*4 and e.next_source=="MAP"


@pytest.mark.parametrize("cd,ac,dr,taken",[(0,1,0,True),(1,1,0,False),(1,1,0x8000,True),
    (2,0x8000,0,True),(2,1,0,False),(3,0,0,True),(3,1,0,False)])
@pytest.mark.parametrize("br",[0,1])
def test_conditional(cd,ac,dr,taken,br):
    c=MicroComputer({127:Microinstruction(0,0,0,cd,br,7).encode()},entry=127)
    c.ac,c.dr,c.sbr=ac,dr,22
    e=c.step()
    assert e.condition==taken and c.car==(7 if taken else 0)
    assert c.sbr==(0 if taken and br==1 else 22)


def test_demo_actual_data_and_return():
    control,memory=demo_images()
    c=MicroComputer(control,memory)
    for _ in range(6):c.step()
    assert c.ac==5 and c.car==64 and c.pc==1
    for _ in range(8):c.step()
    assert c.ac==12 and c.car==64 and c.pc==2 and c.sbr==1


def test_parallel_swap_and_preedge_condition():
    c=MicroComputer({64:Microinstruction(4,5,0,3,0,8).encode()})
    c.ac,c.dr=0,123
    e=c.step()
    assert (c.ac,c.dr,c.car)==(123,0,8) and e.condition


@pytest.mark.parametrize("fields",[(2,1,0),(7,4,0),(0,0,7)])
def test_conflicts_atomic(fields):
    c=MicroComputer({64:Microinstruction(*fields,0,0,65).encode()},{0:9})
    before=c.registers()
    with pytest.raises(ValueError):c.step()
    assert c.registers()==before and c.memory=={0:9}


@pytest.mark.parametrize("text",["0:100000","80:00000","0:0\n0:1","BAD"])
def test_invalid_image(text):
    with pytest.raises(ValueError):parse_image(text,128,1<<20)


def test_uninitialized_and_partial_transfer():
    c=MicroComputer({64:Microinstruction(0,7,0,0,0,65).encode()})
    c.dr,c.pc=0xF800,0x7FF
    c.step()
    assert c.dr==0xFFFF
    with pytest.raises(ValueError):c.step()
