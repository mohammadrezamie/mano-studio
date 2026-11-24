"""Chapter 8 functional register datapath and register stack.

The control word follows the 3+3+3+5 field layout. Only documented
example OPR encodings below are accepted; this is not a new ISA.
"""
from dataclasses import dataclass
from word_arithmetic import alu

OPR={0b00000:"MOV",0b00001:"INC",0b00010:"ADD",0b00101:"SUB",
     0b00110:"DEC",0b01000:"AND",0b01010:"OR",0b01100:"XOR",
     0b01110:"NOT",0b10000:"SHR",0b11000:"SHL"}


@dataclass(frozen=True)
class RegisterControl:
    sela:int
    selb:int
    seld:int
    opr:int

    def encode(self):
        if any(not isinstance(v,int) or not 0<=v<8 for v in (self.sela,self.selb,self.seld)) or self.opr not in OPR:
            raise ValueError("Invalid register control field")
        return (self.sela<<11)|(self.selb<<8)|(self.seld<<5)|self.opr

    @classmethod
    def decode(cls,word):
        if not isinstance(word,int) or not 0<=word<16384:
            raise ValueError("Invalid 14-bit control word")
        control=cls(word>>11,(word>>8)&7,(word>>5)&7,word&31)
        control.encode()
        return control


@dataclass(frozen=True)
class RegisterTransfer:
    control:RegisterControl
    before:tuple
    after:tuple
    a:int
    b:int
    output:int
    operation:str


class RegisterFile:
    """Seven 16-bit registers with two source multiplexers and one destination."""
    def __init__(self):
        self.words=[0]*7

    def transfer(self,control,external=0):
        control.encode()
        if not isinstance(external,int) or not 0<=external<=65535:
            raise ValueError("Invalid external word")
        before=tuple(self.words)
        sources=(external,)+before
        a,b=sources[control.sela],sources[control.selb]
        op=OPR[control.opr]
        output=a if op=="MOV" else alu(op,a,b).word
        if control.seld:
            self.words[control.seld-1]=output
        return RegisterTransfer(control,before,tuple(self.words),a,b,output,op)


@dataclass(frozen=True)
class StackTransfer:
    operation:str
    address:int
    value:int
    before_sp:int
    after_sp:int
    full:bool
    empty:bool


class RegisterStack:
    """64-word ascending register stack, SP=0 initially empty.

    At full capacity SP wraps to 0; FULL distinguishes it from EMPTY.
    Unoccupied physical words retain their previous values.
    """
    def __init__(self):
        self.words=[0]*64
        self.sp=0
        self.depth=0

    @property
    def full(self):return self.depth==64

    @property
    def empty(self):return self.depth==0

    def push(self,value):
        if not isinstance(value,int) or not 0<=value<=65535:
            raise ValueError("Invalid stack word")
        if self.full:raise ValueError("Stack overflow")
        before=self.sp
        self.sp=(self.sp+1)&63
        self.words[self.sp]=value
        self.depth+=1
        return StackTransfer("PUSH",self.sp,value,before,self.sp,self.full,self.empty)

    def pop(self):
        if self.empty:raise ValueError("Stack underflow")
        before=self.sp
        value=self.words[self.sp]
        self.sp=(self.sp-1)&63
        self.depth-=1
        return StackTransfer("POP",before,value,before,self.sp,self.full,self.empty)

    def occupied(self,address):
        if not 0<=address<64:raise ValueError("Invalid stack address")
        return (address==0 and self.full) or (1<=address<=self.depth)
