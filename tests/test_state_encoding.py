from itertools import product
from random import Random
import pytest
from state_synthesis import design_state_machine
from state_reduction import reduce_machine
from state_encoding import encode_reduced


def check(model):
    reduced=reduce_machine(model)
    result=encode_reduced(model)
    assert result.codes[0]==0 and len(set(result.codes))==len(reduced.groups)
    assert result.design.bits==max(1,reduced.bits)
    assert result.design.mode==model.mode and result.design.flipflop==model.flipflop
    for q,r in enumerate(reduced.mapping):
        if r is not None:
            for x in (0,1):
                nxt,y=model.step(q,x)
                assert result.design.step(result.codes[r],x)==(result.codes[reduced.mapping[nxt]],y)
    for code in result.unused:
        assert result.design.step(code,0)==result.design.step(code,1)==(0,0)
    assert result==encode_reduced(model)
    return result


@pytest.mark.parametrize('ff',['D','T','JK'])
def test_all_small(ff):
    for rows in product(tuple(product(range(2),repeat=2)),repeat=4):
        check(design_state_machine(1,rows,'Mealy',ff))


@pytest.mark.parametrize('bits',[2,3])
@pytest.mark.parametrize('mode',['Moore','Mealy'])
def test_larger(bits,mode):
    rng=Random(451)
    for _ in range(24):
        rows=[(rng.randrange(2**bits),rng.randrange(2)) for _ in range(2**(bits+1))]
        if mode=='Moore':rows=[(n,rows[i//2*2][1]) for i,(n,_) in enumerate(rows)]
        check(design_state_machine(bits,rows,mode,'JK'))


def test_three_classes_and_single():
    for ff in ('D','T','JK'):
        result=check(design_state_machine(2,[(0,0),(1,0),(1,0),(2,0),(2,1),(0,1),(3,0),(3,0)],'Moore',ff))
        assert result.candidates==6 and len(result.unused)==1
        one=check(design_state_machine(1,[(0,0)]*4,'Moore',ff))
        assert one.design.bits==1 and one.unused==(1,)
