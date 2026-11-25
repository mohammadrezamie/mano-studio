"""End-to-end pure-Python workflows using the real existing netlist engine."""
from itertools import product
from random import Random

import pytest

from boolean_minimizer import circuit_output_values
from boolean_synthesis import comparison_rows, synthesize
from circuit_document import CircuitDocument
from logic_engine import CIRCUITS
from logic_exercise import KarnaughExercise, StateExercise, read_exercise, write_exercise
from state_analysis import analyze_machine
from state_encoding import encode_reduced
from state_reduction import reduce_machine
from state_synthesis import design_state_machine


ELIGIBLE = tuple((key, name) for key,circuit in CIRCUITS.items()
                 if 2 <= len(circuit.inputs) <= 4 for name,_ in circuit.outputs)


@pytest.mark.parametrize('key,name',ELIGIBLE)
@pytest.mark.parametrize('form',['SOP','POS'])
def test_library_output_to_saved_minimized_circuit(key,name,form,tmp_path):
    original=CIRCUITS[key]
    values=circuit_output_values(original,name)
    original_table=tuple(original.truth_table())
    path=tmp_path/'exercise.mano-exercise.json'
    write_exercise(path,KarnaughExercise(values,form))
    saved=read_exercise(path,'karnaugh')
    document=synthesize(saved.values,saved.form)
    restored=CircuitDocument.loads(document.dumps()).compile()
    assert circuit_output_values(restored,'F')==values
    assert all(v==c==g for _,v,c,g in comparison_rows(saved.values,saved.form))
    assert tuple(original.truth_table())==original_table


@pytest.mark.parametrize('form',['SOP','POS'])
def test_three_variable_all_binary_functions(form):
    for values in product((0,1),repeat=8):
        document=synthesize(values,form)
        saved=CircuitDocument.loads(document.dumps())
        assert circuit_output_values(saved.compile(),'F')==values


@pytest.mark.parametrize('form',['SOP','POS'])
def test_four_variable_incomplete_functions(form):
    rng=Random(481)
    for _ in range(128):
        values=tuple(rng.choice((0,1,None)) for _ in range(16))
        result=synthesize(values,form).compile()
        assert all(value is None or output[0]==value for value,(_,output) in zip(values,result.truth_table()))
        assert all(c==g for _,v,c,g in comparison_rows(values,form))


@pytest.mark.parametrize('bits',[1,2,3])
@pytest.mark.parametrize('mode',['Moore','Mealy'])
@pytest.mark.parametrize('ff',['D','T','JK'])
def test_saved_fsm_analysis_reduction_and_clock(bits,mode,ff,tmp_path):
    rng=Random(127)
    for trial in range(8):
        size=2**bits
        rows=[(rng.randrange(size),rng.randrange(2)) for _ in range(size*2)]
        if mode=='Moore':rows=[(n,rows[2*(i//2)][1]) for i,(n,_) in enumerate(rows)]
        doc=StateExercise(bits,mode,ff,tuple(rows))
        path=tmp_path/'machine.mano-exercise.json'
        write_exercise(path,doc)
        loaded=read_exercise(path,'state-design')
        model=design_state_machine(loaded.bits,loaded.table,loaded.mode,loaded.flipflop)
        analysis=analyze_machine(model)
        reduced=reduce_machine(model)
        encoding=encode_reduced(model)
        assert set(dict(analysis.paths))=={q for group in reduced.groups for q in group}
        q=r=encoded=0
        for x in (rng.randrange(2) for _ in range(64)):
            q,y=model.step(q,x)
            r,ry=reduced.step(r,x)
            encoded,ey=encoding.design.step(encoded,x)
            assert y==ry==ey and r==reduced.mapping[q] and encoded==encoding.codes[r]
        assert loaded==doc
