import json
from itertools import product
import pytest
import logic_exercise as files
from logic_exercise import KarnaughExercise, StateExercise, dumps, loads, read_exercise, write_exercise
from state_synthesis import design_state_machine
from boolean_minimizer import minimize


@pytest.mark.parametrize('form', ['SOP','POS'])
@pytest.mark.parametrize('n',[2,3,4])
def test_map_roundtrip(n,form,tmp_path):
    values=tuple((0,1,None)[i%3] for i in range(2**n))
    original=KarnaughExercise(values,form)
    path=tmp_path/'تمرین.mano-exercise.json'
    write_exercise(path,original)
    restored=read_exercise(path,'karnaugh')
    assert restored==original
    assert minimize(restored.values,restored.form)==minimize(values,form)


@pytest.mark.parametrize('mode',['Moore','Mealy'])
@pytest.mark.parametrize('ff',['D','T','JK'])
@pytest.mark.parametrize('bits',[1,2,3])
def test_state_roundtrip(bits,mode,ff,tmp_path):
    size=2**bits
    rows=tuple(((q+x)%size,int(q==size-1) if mode=='Moore' else x) for q in range(size) for x in (0,1))
    original=StateExercise(bits,mode,ff,rows)
    path=tmp_path/'state.mano-exercise.json'
    write_exercise(path,original)
    restored=read_exercise(path,'state-design')
    assert restored==original
    model=design_state_machine(restored.bits,restored.table,restored.mode,restored.flipflop)
    assert tuple(model.step(q,x) for q in range(size) for x in (0,1))==rows


@pytest.mark.parametrize('change', [
    {'version':True}, {'version':2}, {'format':'other'}, {'kind':'other'},
    {'values':[0,1,2,0]}, {'values':[0,1,True,0]}, {'values':'0000'},
    {'values':[0,1]}, {'form':'XOR'}, {'extra':1}, {'values':None},
])
def test_reject_bad_map(change):
    obj=json.loads(dumps(KarnaughExercise((0,1,None,0))))
    obj.update(change)
    with pytest.raises(ValueError):loads(json.dumps(obj),'karnaugh')


@pytest.mark.parametrize('change',[{'bits':True},{'bits':4},{'mode':'unknown'},{'flipflop':'SR'},
    {'table':[[0,0]]*3},{'table':[[0,0],[1,1],[0,0],[0,0]]},
    {'table':[[0,0],[2,0],[0,0],[0,0]]},{'table':[[0,False]]*4}])
def test_reject_bad_state(change):
    obj=json.loads(dumps(StateExercise(1,'Moore','D',((0,0),)*4)))
    obj.update(change)
    with pytest.raises(ValueError):loads(json.dumps(obj),'state-design')


def test_wrong_kind_duplicate_bom_and_limits(tmp_path):
    source=dumps(KarnaughExercise((0,1,None,0)))
    with pytest.raises(ValueError):loads(source,'state-design')
    with pytest.raises(ValueError):loads(source.replace('"version": 1','"version": 1, "version": 1'))
    with pytest.raises(ValueError):loads('['*10000)
    path=tmp_path/'exercise.json'
    path.write_bytes(b'\xef\xbb\xbf'+source.encode())
    assert read_exercise(path).values==(0,1,None,0)
    path.write_bytes(b' '* (files.MAX_BYTES+1))
    with pytest.raises(ValueError):read_exercise(path)


def test_atomic_failure_preserves_original(tmp_path,monkeypatch):
    path=tmp_path/'exercise.json'
    original=KarnaughExercise((1,0,None,1))
    write_exercise(path,original)
    def fail(*args):raise OSError('mock replacement failure')
    monkeypatch.setattr(files.os,'replace',fail)
    with pytest.raises(OSError):write_exercise(path,KarnaughExercise((0,0,0,0)))
    assert read_exercise(path)==original
    assert list(tmp_path.iterdir())==[path]
