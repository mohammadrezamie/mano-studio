import pytest
from cpu_organization import RegisterControl,RegisterFile,RegisterStack,OPR


@pytest.mark.parametrize("op",list(OPR))
def test_control_words_and_register_destinations(op):
    for a in range(8):
        for b in range(8):
            for d in range(8):
                c=RegisterControl(a,b,d,op)
                assert RegisterControl.decode(c.encode())==c
                assert c.encode()==(a<<11)|(b<<8)|(d<<5)|op
                r=RegisterFile()
                r.words[:]=[1,2,3,4,5,6,7]
                event=r.transfer(c,0xFFFF)
                x,y=(65535,1,2,3,4,5,6,7)[a],(65535,1,2,3,4,5,6,7)[b]
                value={"MOV":x,"INC":x+1,"ADD":x+y,"SUB":x-y,"DEC":x-1,
                       "AND":x&y,"OR":x|y,"XOR":x^y,"NOT":~x,"SHR":x>>1,"SHL":x<<1}[OPR[op]]&65535
                assert event.output==value and (event.a,event.b)==(x,y)
                expected=list(event.before)
                if d:expected[d-1]=value
                assert r.words==expected


@pytest.mark.parametrize("word",[-1,16384,31])
def test_invalid_word(word):
    with pytest.raises(ValueError):RegisterControl.decode(word)


def test_stack_wrap_full_and_lifo():
    s=RegisterStack()
    assert s.empty and s.sp==0 and not s.full
    for i in range(64):
        e=s.push(i+100)
        assert e.address==(i+1)&63 and s.occupied(e.address)
    assert s.full and s.sp==0 and not s.empty
    snapshot=(s.sp,s.depth,list(s.words))
    with pytest.raises(ValueError):s.push(9)
    assert (s.sp,s.depth,s.words)==snapshot
    for i in reversed(range(64)):
        e=s.pop()
        assert e.value==i+100 and e.address==(i+1)&63
        assert not s.occupied(e.address)
    assert s.empty and s.sp==0
    with pytest.raises(ValueError):s.pop()
    assert s.empty and s.sp==0 and s.words[0]==163


def test_invalid_operations_atomic():
    s=RegisterStack()
    with pytest.raises(ValueError):s.push(65536)
    assert s.empty
    r=RegisterFile()
    with pytest.raises(ValueError):r.transfer(RegisterControl(0,0,1,31))
    assert r.words==[0]*7
