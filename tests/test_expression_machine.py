import pytest
from expression_machine import postfix,evaluate_expression


@pytest.mark.parametrize("expression,expected",[
    ("(A+B)*(C-D)",56),("A+B*C",32),("20/3/2",3),("10-3-2",5),
    ("0-1",65535),("65535+1",0),("65535/2",0),("32768/(0-1)",32768),
    ("(0-7)/2",65533),("A",5)])
@pytest.mark.parametrize("addresses",range(4))
def test_execution_formats(expression,expected,addresses):
    r=evaluate_expression(expression,dict(A=5,B=3,C=9,D=2),addresses)
    assert r.word==expected
    assert len(r.steps)==len(r.program)
    assert r.steps[-1].writes[-1]==("RESULT",expected)
    if addresses==0:assert not r.steps[-1].stack


def test_postfix_and_instruction_counts():
    assert postfix("(a+b)*(c-d)")==("A","B","+","C","D","-","*")
    results=[evaluate_expression("(A+B)*(C-D)",dict(A=5,B=3,C=9,D=2),n) for n in range(4)]
    assert [len(r.program) for r in results]==[8,11,7,4]
    assert results[0].steps[2].stack==(8,)
    assert results[3].program[0]==("ADD","T1","A","B")


@pytest.mark.parametrize("source",["","A+","A B","(A+B","A+B)","A()","()","-A","E","2**3","65536","A//B","Ａ"])
def test_invalid_expression(source):
    with pytest.raises(ValueError):postfix(source)


@pytest.mark.parametrize("addresses",range(4))
def test_divide_zero(addresses):
    with pytest.raises(ValueError,match="Division by zero"):
        evaluate_expression("A/(B-B)",dict(A=5,B=3),addresses)
