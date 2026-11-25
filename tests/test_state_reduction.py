from itertools import product
from random import Random
import pytest
from state_synthesis import design_state_machine
from state_reduction import reduce_machine


def check(model):
    reduced=reduce_machine(model)
    assert reduced.mapping[0]==0
    reachable={0}
    for _ in range(2**model.bits):
        reachable |= {model.step(q,x)[0] for q in reachable for x in (0,1)}
    assert {q for q,r in enumerate(reduced.mapping) if r is not None}==reachable
    # Independent partition refinement restricted to reachable states.
    labels={q:0 for q in reachable}
    while True:
        keys={q:tuple((model.step(q,x)[1],labels[model.step(q,x)[0]]) for x in (0,1)) for q in reachable}
        distinct=list(dict.fromkeys(keys.values()))
        new={q:distinct.index(keys[q]) for q in reachable}
        if new==labels:break
        labels=new
    assert len(reduced.groups)==len(set(labels.values()))
    for q in reachable:
        for x in (0,1):
            nxt,y=model.step(q,x)
            assert reduced.step(reduced.mapping[q],x)==(reduced.mapping[nxt],y)
    return reduced


def test_all_two_state_mealy():
    for rows in product(tuple(product(range(2),repeat=2)),repeat=4):
        check(design_state_machine(1,rows,'Mealy','D'))


@pytest.mark.parametrize('mode',['Moore','Mealy'])
@pytest.mark.parametrize('bits',[2,3])
def test_seeded_reduction(mode,bits):
    rng=Random(274)
    for _ in range(32):
        rows=[(rng.randrange(2**bits),rng.randrange(2)) for _ in range(2**(bits+1))]
        if mode=='Moore':rows=[(n,rows[i//2*2][1]) for i,(n,_) in enumerate(rows)]
        check(design_state_machine(bits,rows,mode,'JK'))


def test_one_state_and_non_power_of_two():
    one=check(design_state_machine(2,[(0,0),(1,0),(1,0),(0,0),(2,1),(2,1),(3,1),(3,1)],'Moore'))
    assert one.groups==((0,1),) and one.bits==0 and one.mapping==(0,0,None,None)
    three=check(design_state_machine(2,[(0,0),(1,0),(1,0),(2,0),(2,1),(0,1),(3,0),(3,0)],'Moore'))
    assert len(three.groups)==3 and three.bits==2
    with pytest.raises(ValueError):three.step(3,0)
