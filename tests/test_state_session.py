from dataclasses import replace
from itertools import product
import pytest
from logic_exercise import StateExercise
from state_session import snapshot, payload, restore, save, load


@pytest.mark.parametrize('mode,ff,bits', list(product(('Moore','Mealy'),('D','T','JK'),(1,2,3))))
def test_replay_roundtrip(tmp_path, mode, ff, bits):
    size = 2**bits
    table = tuple(((q+x)%size, q%2 if mode=='Moore' else x) for q in range(size) for x in (0,1))
    design = StateExercise(bits, mode, ff, table)
    seq = tuple((i*i//3)%2 for i in range(250))
    base = sum(seq[:-64])%size
    session = snapshot(design, base, seq[-64:], 1)
    q = base
    for x, row in zip(seq[-64:], session.trace):
        nxt,y = table[q*2+x]
        assert row == (q,x,nxt,y)
        q = nxt
    assert session.state == q == sum(seq)%size
    path = tmp_path/'session.mano'
    save(path,session)
    assert load(path)==session
    next_input = 1
    continued = snapshot(design,session.trace[0][2],session.inputs[1:]+(next_input,),0)
    assert continued.state == (q+1)%size
    assert continued.trace[:-1] == session.trace[1:]


@pytest.fixture
def valid():
    return snapshot(StateExercise(1,'Moore','T',((0,0),(1,0),(1,1),(0,1))),0,(1,0,1),1)


@pytest.mark.parametrize('key,value',[('base',True),('base',2),('selected',2),('selected',False),('inputs',[0]*65),('inputs',[True]),('inputs','01'),('inputs',[2]),('design',{})])
def test_invalid(valid,key,value):
    obj=payload(valid)
    obj[key]=value
    with pytest.raises(ValueError):
        restore(obj)


def test_inconsistent_save(valid,tmp_path):
    path=tmp_path/'session.mano'
    save(path,valid)
    original=path.read_bytes()
    with pytest.raises(ValueError):
        save(path,replace(valid,state=1-valid.state))
    assert path.read_bytes()==original


def test_empty(valid):
    session=snapshot(valid.design,1,(),0)
    assert session.state==1 and not session.trace
    assert restore(payload(session))==session
