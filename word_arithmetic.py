"""Fixed-width data representation and arithmetic shared by CPU and teaching tools."""
from dataclasses import dataclass
import re

WIDTHS = (4, 8, 12, 16)

def mask_for(width):
    if width not in WIDTHS:
        raise ValueError("Unsupported word width")
    return (1 << width) - 1

def signed(word,width):
    mask=mask_for(width)
    if not 0 <= word <= mask:
        raise ValueError("Word outside selected width")
    return word - (mask+1) if word & (1 << (width-1)) else word

def parse_word(text,base,width):
    mask=mask_for(width)
    text=text.strip()
    patterns={2:r"[01]+",8:r"[0-7]+",10:r"[+-]?[0-9]+",16:r"[0-9A-Fa-f]+"}
    if base not in patterns or len(text)>32 or not re.fullmatch(patterns[base],text):
        raise ValueError("Invalid digits for selected base")
    value=int(text,base)
    minimum=-(1<<(width-1)) if base==10 else 0
    if not minimum<=value<=mask:
        raise ValueError("Value outside selected word width")
    return value & mask

def representations(word,width):
    s=signed(word,width)
    return {"BIN":f"{word:0{width}b}","OCT":f"{word:0{(width+2)//3}o}",
            "HEX":f"{word:0{(width+3)//4}X}","Unsigned":str(word),"Signed":str(s)}

@dataclass(frozen=True)
class ALUResult:
    word: int
    carry: int | None
    overflow: bool | None
    negative: bool
    zero: bool
    stages: tuple = ()

def ripple_add(a,b,width,carry_in=0):
    """Return sum, carry out, signed overflow, and LSB-first full-adder rows."""
    mask=mask_for(width)
    if not 0<=a<=mask or not 0<=b<=mask or carry_in not in (0,1):
        raise ValueError("Invalid arithmetic operand")
    carry=carry_in
    word=0
    stages=[]
    for i in range(width):
        x,y=(a>>i)&1,(b>>i)&1
        total=x+y+carry
        bit=total&1
        out=total>>1
        stages.append((i,x,y,carry,bit,out))
        word|=bit<<i
        carry=out
    overflow=bool(stages[-1][3]^carry)
    return word,carry,overflow,tuple(stages)

OPERATIONS=("ADD","ADC","SUB","INC","DEC","AND","OR","XOR","NOT","SHL","SHR","ASR","ROL","ROR","CIL","CIR")

def alu(operation,a,b=0,width=16,carry_in=0):
    mask=mask_for(width)
    if operation not in OPERATIONS or not 0<=a<=mask or not 0<=b<=mask or carry_in not in (0,1):
        raise ValueError("Invalid ALU operation or operand")
    carry=overflow=None
    stages=()
    if operation in ("ADD","ADC","SUB","INC","DEC"):
        rhs,cin={
            "ADD":(b,0),"ADC":(b,carry_in),"SUB":(b^mask,1),
            "INC":(0,1),"DEC":(mask,0)
        }[operation]
        word,carry,overflow,stages=ripple_add(a,rhs,width,cin)
    elif operation=="AND": word=a&b
    elif operation=="OR": word=a|b
    elif operation=="XOR": word=a^b
    elif operation=="NOT": word=a^mask
    elif operation in ("SHL","ROL","CIL"):
        carry=a>>(width-1)
        word=((a<<1)|(carry if operation=="ROL" else carry_in if operation=="CIL" else 0))&mask
    else:
        carry=a&1
        high=carry if operation=="ROR" else carry_in if operation=="CIR" else a>>(width-1) if operation=="ASR" else 0
        word=(a>>1)|(high<<(width-1))
    return ALUResult(word,carry,overflow,bool(word&(1<<(width-1))),word==0,stages)
