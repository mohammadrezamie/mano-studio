from itertools import permutations, product
from random import Random
from state_synthesis import design_state_machine
from state_reduction import reduce_machine
from state_encoding import encode_reduced
import pytest

# Independent cube enumeration and DP over coverage. No production minimize call.
def min_cost(values):
    size=len(values)
    needed=sum(1<<i for i,v in enumerate(values) if v==1)
    forbidden=sum(1<<i for i,v in enumerate(values) if v==0)
    costs={0:(0,0)}
    for fixed in range(size):
        for pattern in range(size):
            if pattern & ~fixed: continue
            cube=sum(1<<i for i in range(size) if i&fixed==pattern)
            if cube&forbidden or not cube&needed: continue
            for covered,cost in list(costs.items()):
                new=covered|(cube&needed)
                score=(cost[0]+1,cost[1]+fixed.bit_count())
                costs[new]=min(costs.get(new,score),score)
    return costs[needed]

def assignment_cost(quotient,codes,ff):
    width=max(1,quotient.bits)
    rows=[(0,0)]*(2**(width+1))
    for r,code in enumerate(codes):
        for x in (0,1):
            dest,y=quotient.table[2*r+x]
            rows[2*code+x]=(codes[dest],y)
    functions=[[y for _,y in rows]]
    for i in range(width):
        q=[(r//2>>i)&1 for r in range(len(rows))]
        p=[(n>>i)&1 for n,_ in rows]
        if ff=='D':functions.append(p)
        elif ff=='T':functions.append([a^b for a,b in zip(q,p)])
        else:
            functions.append([None if a else b for a,b in zip(q,p)])
            functions.append([1-b if a else None for a,b in zip(q,p)])
    costs=[min_cost(f) for f in functions]
    return tuple(sum(c[i] for c in costs) for i in (0,1))

@pytest.mark.parametrize('ff',['D','T','JK'])
@pytest.mark.parametrize('mode',['Moore','Mealy'])
def test_optimum(ff,mode):
    rng=Random(115)
    counts=set()
    for trial in range(80):
        n=2 if trial<4 else 4
        rows=[(rng.randrange(n),rng.randrange(2)) for _ in range(2*n)]
        if mode=='Moore':rows=[(dest,rows[i//2*2][1]) for i,(dest,_) in enumerate(rows)]
        model=design_state_machine(n.bit_length()-1,rows,mode,ff)
        reduced=reduce_machine(model)
        count=len(reduced.groups)
        counts.add(count)
        width=max(1,reduced.bits)
        candidates=[(0,*tail) for tail in permutations(range(1,2**width),count-1)]
        expected=min((assignment_cost(reduced,codes,ff),codes) for codes in candidates)
        result=encode_reduced(model)
        assert (result.cost,result.codes)==expected
        assert result.candidates==len(candidates)
    assert counts=={1,2,3,4}
