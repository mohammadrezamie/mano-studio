import pytest
from vector_pipeline import build_pipeline,parse_matrix


@pytest.mark.parametrize("mode,expected",[
    ("add",((6,8,10),)),("sub",((65532,65532,65532),)),
    ("mul",((5,12,21),)),("mac",((6,14,24),)),("dot",((38,),))])
def test_vector_operations(mode,expected):
    p=build_pipeline(mode,((1,2,3),),((5,6,7),),((1,2,3),))
    rows=p.run()
    assert p.output()==expected and len(rows)==5
    assert rows[0].load.index==(0,) and rows[0].multiply is None
    assert rows[2].accumulate.job.index==(0,)
    assert rows[-1].load is None and rows[-1].multiply is None
    assert p.step() is None


def test_rectangular_matrix():
    a=((1,2,3),(4,5,6))
    b=((7,8),(9,10),(11,12))
    p=build_pipeline("matrix",a,b)
    rows=p.run()
    assert p.output()==((58,64),(139,154))
    assert len(rows)==14 and len(p.jobs)==12
    assert rows[4].after==58
    assert rows[5].before==0


@pytest.mark.parametrize("n,m,k",[(1,1,1),(2,3,4),(8,8,8),(3,1,5)])
def test_matrix_oracle(n,m,k):
    a=tuple(tuple((i-j)*10000%65536 for j in range(k)) for i in range(n))
    b=tuple(tuple((i+j)*31337%65536 for j in range(m)) for i in range(k))
    p=build_pipeline("matrix",a,b);p.run()
    assert p.output()==tuple(tuple(sum(a[i][t]*b[t][j] for t in range(k))%65536 for j in range(m)) for i in range(n))
    assert p.cycles==n*m*k+2


@pytest.mark.parametrize("text",["","1 2\n3","65536","1 x","-32769","1 2 3 4 5 6 7 8 9"])
def test_bad_matrix(text):
    with pytest.raises(ValueError):parse_matrix(text)


def test_signed_input_and_bad_dimensions():
    assert parse_matrix("-1 65535")==((65535,65535),)
    with pytest.raises(ValueError):build_pipeline("matrix",((1,2),),((1,2),))
    with pytest.raises(ValueError):build_pipeline("mac",((1,2),),((1,2),),((1,),))
