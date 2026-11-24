import pytest
from pipeline import Pipeline,parse_program,EXAMPLE


def test_independent_timing():
    p=Pipeline(parse_program("ADDI R1,R0,3\nADDI R2,R0,7\nNOP"))
    rows=p.run()
    assert len(rows)==7 and p.retired==3 and not p.stalls
    assert rows[0].stages==(0,None,None,None,None)
    assert rows[-1].stages==(None,None,None,None,2)


@pytest.mark.parametrize("forwarding,stalls",[(True,0),(False,2)])
def test_raw_hazard(forwarding,stalls):
    p=Pipeline(parse_program("ADDI R1,R0,3\nADD R2,R1,R1"),forwarding)
    rows=p.run()
    assert p.stalls==stalls and p.cycles==6+stalls and p.registers[2]==6
    assert bool(any(r.forwarded for r in rows))==forwarding


@pytest.mark.parametrize("forwarding,stalls",[(True,1),(False,2)])
def test_load_use(forwarding,stalls):
    p=Pipeline(parse_program("LD R1,R0,4\nSUB R2,R1,R0"),forwarding,{4:11})
    p.run()
    assert p.stalls==stalls and p.registers[2]==11


@pytest.mark.parametrize("forwarding",[True,False])
def test_store_branch_demo(forwarding):
    p=Pipeline(parse_program(EXAMPLE),forwarding)
    rows=p.run()
    assert p.registers==[0,5,5,10,0,5,0,0] and p.memory=={16:5}
    assert p.retired==6 and p.flushes==2
    assert sum(bool(r.flushed) for r in rows)==1
    assert any(r.writes==((16,5),) for r in rows)


def test_newest_producer_and_zero_register():
    p=Pipeline(parse_program("ADDI R1,R0,1\nADDI R1,R1,2\nADD R2,R1,R1\nADDI R0,R0,9\nADDI R3,R0,2"))
    p.run()
    assert p.registers[:4]==[0,3,6,2]


def test_not_taken_and_wrap():
    p=Pipeline(parse_program("ADDI R1,R0,1\nBEQ R1,R0,END\nST R1,R0,-1\nEND: LD R2,R0,-1"))
    p.run()
    assert p.memory=={65535:1} and p.registers[2]==1 and not p.flushes


@pytest.mark.parametrize("source",["","BAD","ADD R8,R0,R0","BEQ R0,R0,MISSING","ADDI R1,R0,32768","X: NOP\nX: NOP"])
def test_invalid(source):
    with pytest.raises(ValueError):parse_program(source)


def test_loop_cap():
    p=Pipeline(parse_program("LOOP: BEQ R0,R0,LOOP"))
    with pytest.raises(ValueError,match="Cycle limit"):p.run()
    assert p.cycles==512
