from itertools import product
import random
import pytest
from state_synthesis import design_state_machine


@pytest.mark.parametrize('ff', ['D','T','JK'])
def test_exhaustive_two_state_mealy(ff):
    for rows in product(tuple(product(range(2),repeat=2)),repeat=4):
        model = design_state_machine(1,rows,'Mealy',ff)
        assert tuple(model.step(i//2,i%2) for i in range(4)) == rows


@pytest.mark.parametrize('ff', ['D','T','JK'])
def test_exhaustive_two_state_moore(ff):
    for nexts in product(range(2),repeat=4):
        for outputs in product(range(2),repeat=2):
            rows = tuple((n,outputs[i//2]) for i,n in enumerate(nexts))
            model = design_state_machine(1,rows,'Moore',ff)
            assert tuple(model.step(i//2,i%2) for i in range(4)) == rows
            assert all(g.pattern[-1]=='-' for g in dict(model.equations)['Y'].groups)


@pytest.mark.parametrize('bits', [2,3])
@pytest.mark.parametrize('ff', ['D','T','JK'])
def test_seeded_larger_machines(bits,ff):
    rng=random.Random(619)
    for mode in ('Mealy','Moore'):
        for _ in range(32):
            outputs=[rng.randrange(2) for _ in range(2**(bits+1))]
            if mode=='Moore':outputs[1::2]=outputs[::2]
            rows=tuple((rng.randrange(2**bits),y) for y in outputs)
            model=design_state_machine(bits,rows,mode,ff)
            state=0
            for x in [rng.randrange(2) for _ in range(32)]:
                expected=rows[state*2+x]
                assert model.step(state,x)==expected
                state=expected[0]
            assert model.aliases[-1][1]=='X'


def test_toggle_equations_and_invalid_inputs():
    rows=((0,0),(1,0),(1,1),(0,1))
    for ff in ('D','T','JK'):
        model=design_state_machine(1,rows,'Moore',ff)
        if ff=='T':assert dict(model.equations)['T0'].expression=='B'
        if ff=='JK':assert dict(model.equations)['J0'].expression==dict(model.equations)['K0'].expression=='B'
        with pytest.raises(ValueError):model.step(2,0)
    with pytest.raises(ValueError):design_state_machine(1,((0,0),(1,1),(0,0),(1,0)),'Moore')
    with pytest.raises(ValueError):design_state_machine(1,[(0,0)]*3)
    with pytest.raises(ValueError):design_state_machine(4,[])
    with pytest.raises(ValueError):design_state_machine(1,[(2,0)]*4)


@pytest.mark.parametrize("mode",["Moore","Mealy"])
def test_outgoing_graph_represents_every_input(mode):
    from state_synthesis import outgoing_edges
    rng=random.Random(172)
    for bits in (1,2,3):
        for _ in range(24):
            rows=[(rng.randrange(2**bits),rng.randrange(2)) for _ in range(2**(bits+1))]
            if mode=="Moore":
                rows=[(n,rows[i//2*2][1]) for i,(n,_) in enumerate(rows)]
            model=design_state_machine(bits,rows,mode,"JK")
            for q in range(2**bits):
                edges=outgoing_edges(model,q)
                assert len({edge.destination for edge in edges})==len(edges)
                actual={x:(edge.destination,y) for edge in edges for x,y in edge.conditions}
                assert actual=={x:rows[q*2+x] for x in (0,1)}
