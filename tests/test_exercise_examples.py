from pathlib import Path

from boolean_minimizer import minimize
from logic_exercise import read_exercise
from state_reduction import reduce_machine
from state_synthesis import design_state_machine

ROOT=Path(__file__).resolve().parents[1]/'examples'


def test_karnaugh_examples():
    corners=read_exercise(ROOT/'karnaugh-corners.mano-exercise.json','karnaugh')
    assert minimize(corners.values,corners.form).expression=="B'D'"
    dc=read_exercise(ROOT/'karnaugh-dont-care.mano-exercise.json','karnaugh')
    cover=minimize(dc.values,dc.form)
    assert dc.form=='POS' and None in dc.values
    assert all(v is None or cover.evaluate(i)==v for i,v in enumerate(dc.values))


def test_fsm_examples():
    ex=read_exercise(ROOT/'fsm-moore-reduction.mano-exercise.json','state-design')
    model=design_state_machine(ex.bits,ex.table,ex.mode,ex.flipflop)
    assert reduce_machine(model).groups==((0,1),)
    ex=read_exercise(ROOT/'fsm-mealy-101.mano-exercise.json','state-design')
    model=design_state_machine(ex.bits,ex.table,ex.mode,ex.flipflop)
    q=0;ys=[]
    for x in (1,0,1,0,1):
        q,y=model.step(q,x);ys.append(y)
    assert ys==[0,0,1,0,1]
    assert len(reduce_machine(model).groups)==3
