from itertools import product
from random import Random
import pytest
from state_analysis import analyze_machine
from state_synthesis import design_state_machine


def outputs(model,q,word):
    ys=[]
    for x in word:
        q,y=model.step(q,int(x));ys.append(y)
    return ys


def check(model):
    report=analyze_machine(model)
    n=2**model.bits
    reached={0}
    for _ in range(n):
        reached|={model.step(q,x)[0] for q in reached for x in (0,1)}
    assert set(dict(report.paths))==reached
    assert set(report.unreachable)==set(range(n))-reached
    for q,word in report.paths:
        s=0
        for x in word:s,_=model.step(s,int(x))
        assert q==s
    # Independent partition refinement.
    labels=[0]*n
    while True:
        keys=[tuple((model.step(q,x)[1],labels[model.step(q,x)[0]]) for x in (0,1)) for q in range(n)]
        new=[keys.index(k) for k in keys]
        if new==labels:break
        labels=new
    assert report.classes==tuple(tuple(i for i in range(n) if labels[i]==k) for k in sorted(set(labels)))
    for a,b,word in report.witnesses:
        assert (word is None)==(labels[a]==labels[b])
        if word is not None:
            assert outputs(model,a,word)!=outputs(model,b,word)
            for length in range(1,len(word)):
                assert all(outputs(model,a,w)==outputs(model,b,w) for w in product('01',repeat=length))
            assert all(outputs(model,a,w)==outputs(model,b,w) for w in product('01',repeat=len(word)) if ''.join(w)<word)


def test_exhaustive_two_state_mealy():
    for rows in product(tuple(product(range(2),repeat=2)),repeat=4):
        check(design_state_machine(1,rows,'Mealy','D'))


@pytest.mark.parametrize('bits',[2,3])
@pytest.mark.parametrize('mode',['Moore','Mealy'])
def test_seeded_analysis(bits,mode):
    rng=Random(2026)
    for _ in range(32):
        rows=[(rng.randrange(2**bits),rng.randrange(2)) for _ in range(2**(bits+1))]
        if mode=='Moore':rows=[(n,rows[i//2*2][1]) for i,(n,_) in enumerate(rows)]
        check(design_state_machine(bits,rows,mode,'JK'))


def test_unreachable_and_equivalent():
    model=design_state_machine(2,[(0,0),(1,0),(1,0),(0,0),(2,1),(2,1),(3,1),(3,1)],'Moore')
    result=analyze_machine(model)
    assert result.paths==((0,''),(1,'1'))
    assert result.unreachable==(2,3)
    assert result.classes==((0,1),(2,3))
    assert dict(((a,b),w) for a,b,w in result.witnesses)[0,2]=='0'
