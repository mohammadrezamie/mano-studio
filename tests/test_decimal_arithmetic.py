import pytest
from decimal_arithmetic import decimal_alu, packed_decimal


@pytest.mark.parametrize("digits", [1,2])
def test_decimal_exhaustive(digits):
    modulus = 10**digits
    width = digits*4
    for a in range(modulus):
        for b in range(modulus):
            for op in ("ADD","SUB"):
                result = decimal_alu(op,int(str(a),16),int(str(b),16),width)
                expected = a+b if op=="ADD" else a-b
                assert result.decimal == expected % modulus
                assert result.word == int(str(expected % modulus),16)
                assert result.carry == int(expected >= (modulus if op=="ADD" else 0))
                assert result.borrow == (int(expected<0) if op=="SUB" else None)
                assert len(result.steps)==digits
                cin = int(op=="SUB")
                for i,s in enumerate(result.steps):
                    x,y = a//10**i%10,b//10**i%10
                    operand = y if op=="ADD" else 9-y
                    raw = x+operand+cin
                    assert (s.position,s.a,s.b,s.carry_in,s.binary_sum)==(i,x,operand,cin,raw)
                    assert s.correction == (6 if raw>9 else 0)
                    assert (s.digit,s.carry_out)==(raw%10,raw//10)
                    cin = s.carry_out


@pytest.mark.parametrize("width",[12,16])
def test_carry_borrow_chain(width):
    maximum = int("9"*(width//4),16)
    add = decimal_alu("ADD",maximum,1,width)
    assert add.word==0 and add.carry==1
    sub = decimal_alu("SUB",0,1,width)
    assert sub.word==maximum and sub.borrow==1
    assert decimal_alu("SUB",maximum,maximum,width).word==0


@pytest.mark.parametrize("op,a,b,width",[("ADD",0xA,1,4),("SUB",1,0xF,4),
    ("ADD",0x100,1,8),("ADD",-1,1,4),("MUL",1,1,4),("ADD",1,1,5)])
def test_invalid(op,a,b,width):
    with pytest.raises(ValueError):
        decimal_alu(op,a,b,width)


def test_decode_leading_zero():
    assert packed_decimal(0x0099,16)==99
