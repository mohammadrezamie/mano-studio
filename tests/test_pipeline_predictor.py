import pytest
from pipeline import Pipeline,parse_program,EXAMPLE


def reference(program,memory=None):
    r=[0]*8
    m=dict(memory or {})
    pc=0
    for _ in range(512):
        if pc==len(program):return r,m
        ins=program[pc]
        vals=[r[i] for i in ins.sources]
        pc+=1
        v=0
        if ins.op=="ADDI":v=vals[0]+ins.immediate
        elif ins.op=="ADD":v=vals[0]+vals[1]
        elif ins.op=="SUB":v=vals[0]-vals[1]
        elif ins.op=="AND":v=vals[0]&vals[1]
        elif ins.op=="OR":v=vals[0]|vals[1]
        elif ins.op=="XOR":v=vals[0]^vals[1]
        elif ins.op=="LD":v=m.get((vals[0]+ins.immediate)&65535,0)
        elif ins.op=="ST":m[(vals[1]+ins.immediate)&65535]=vals[0]
        elif ins.op=="BEQ" and vals[0]==vals[1]:pc=ins.target
        if ins.dest:r[ins.dest]=v&65535
    raise AssertionError("Reference exceeded limit")


LOOP="""ADDI R1,R0,5
LOOP: ADDI R1,R1,-1
BEQ R1,R0,END
BEQ R0,R0,LOOP
END: ADDI R2,R0,9"""


@pytest.mark.parametrize("source",[EXAMPLE,LOOP,"LD R1,R0,2\nST R1,R0,3\nLD R2,R0,3\nNOP\nNOP\nNOP"])
@pytest.mark.parametrize("forwarding",[True,False])
@pytest.mark.parametrize("shared",[True,False])
@pytest.mark.parametrize("predictor",["not_taken","taken","two_bit"])
def test_all_configurations(source,forwarding,shared,predictor):
    program=parse_program(source)
    p=Pipeline(program,forwarding,{2:17},shared,predictor)
    rows=p.run()
    assert (p.registers,p.memory)==reference(program,{2:17})
    assert p.structural_stalls==sum(r.structural for r in rows)
    assert p.mispredictions==sum(bool(r.prediction and r.prediction[-1]) for r in rows)


def test_structural_port():
    program=parse_program("LD R1,R0,0\nNOP\nNOP\nNOP\nNOP")
    normal=Pipeline(program);normal.run()
    shared=Pipeline(program,shared_port=True);rows=shared.run()
    assert shared.structural_stalls==1 and shared.cycles==normal.cycles+1
    row=next(r for r in rows if r.structural)
    assert row.stages[0] is not None and row.stages[3]==0
    assert rows[row.number].stages[0]==row.stages[0]


def test_predictor_learns_loop():
    p=Pipeline(parse_program(LOOP),predictor="two_bit")
    p.run()
    assert p.counters[3]==3 and p.counters[2]==1
    assert p.branches==9 and p.mispredictions==2
    assert p.registers[2]==9


def test_taken_prediction_not_taken_recovery():
    p=Pipeline(parse_program("ADDI R1,R0,1\nBEQ R1,R0,END\nST R1,R0,3\nEND: NOP"),predictor="taken")
    rows=p.run()
    assert p.memory=={3:1} and p.mispredictions==1
    assert any(r.prediction==(1,True,False,True) for r in rows)
