import random
from fractions import Fraction
import pytest
from floating_pipeline import FloatPipeline,Job,parse_jobs,EXAMPLE
from floating_arithmetic import float_alu


def test_four_actual_stages():
    p=FloatPipeline([Job("ADD",0x3C00,0x3800),Job("SUB",0x4000,0x3C00)])
    rows=p.run()
    assert len(rows)==5
    assert rows[0].compare.exponent==0 and rows[0].compare.shifts==(0,1)
    assert rows[0].align is None and rows[0].round is None
    assert rows[1].align.left==1 and rows[1].align.right==Fraction(1,2)
    assert rows[2].add.exact==Fraction(3,2)
    assert rows[3].round.result.word==0x3E00
    assert rows[4].round.result.word==0x3C00
    assert rows[4].compare is None and p.step() is None


def test_random_equivalence_and_order():
    rng=random.Random(913)
    for op in ("ADD","SUB"):
        for _ in range(16):
            jobs=[Job(op,rng.randrange(65536),rng.randrange(65536)) for _ in range(128)]
            p=FloatPipeline(jobs);p.run()
            assert p.cycles==131
            assert [r.result for r in p.results]==[float_alu(j.op,j.a,j.b) for j in jobs]
            assert [r.summed.aligned.compared.number for r in p.results]==list(range(1,129))


@pytest.mark.parametrize("op,a,b,word",[
    ("ADD",0x8000,0x8000,0x8000),("SUB",0x8000,0,0x8000),
    ("ADD",0x3C00,0xBC00,0),("ADD",1,1,2),
    ("ADD",0x3C00,0x1000,0x3C00),("ADD",0x7BFF,0x7BFF,0x7C00),
    ("ADD",0x7C00,0xFC00,0x7E00),("SUB",0x7C00,0x7C00,0x7E00),
    ("ADD",0x7D00,0x3C00,0x7E00)])
def test_special_and_rounding(op,a,b,word):
    p=FloatPipeline([Job(op,a,b)]);p.run()
    assert p.cycles==4 and p.results[0].result.word==word
    assert p.results[0].result==float_alu(op,a,b)


def test_example_and_validation():
    assert len(parse_jobs(EXAMPLE))==6
    for text in ("","MUL 0000 0000","ADD 0 0000","ADD 0000 FFFFF","SUB 0000 0000 trailing"):
        with pytest.raises(ValueError):parse_jobs(text)
    with pytest.raises(ValueError):FloatPipeline([Job("ADD",65536,0)])
