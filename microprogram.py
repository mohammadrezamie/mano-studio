"""Chapter 7's distinct microprogrammed computer, not the Chapter 5 CPU."""
from dataclasses import dataclass
from word_arithmetic import alu

FIELDS=(("NOP","ADD","CLRAC","INCAC","DRTAC","DRTAR","PCTAR","WRITE"),
        ("NOP","SUB","OR","AND","READ","ACTDR","INCDR","PCTDR"),
        ("NOP","XOR","COM","SHL","SHR","INCPC","ARTPC","RESERVED"))
CONDITIONS=("U","I","S","Z")
BRANCHES=("JMP","CALL","RET","MAP")


@dataclass(frozen=True)
class Microinstruction:
    f1:int
    f2:int
    f3:int
    cd:int
    br:int
    ad:int

    def encode(self):
        values=(self.f1,self.f2,self.f3,self.cd,self.br,self.ad)
        if any(not isinstance(v,int) or not 0<=v<1<<n for v,n in zip(values,(3,3,3,2,2,7))):
            raise ValueError("Invalid microinstruction field")
        return (self.f1<<17)|(self.f2<<14)|(self.f3<<11)|(self.cd<<9)|(self.br<<7)|self.ad

    @classmethod
    def decode(cls,word):
        if not isinstance(word,int) or not 0<=word<1<<20:
            raise ValueError("Invalid 20-bit control word")
        return cls(word>>17,(word>>14)&7,(word>>11)&7,(word>>9)&3,(word>>7)&3,word&127)

    @property
    def operations(self):
        return tuple(FIELDS[i][v] for i,v in enumerate((self.f1,self.f2,self.f3)) if v)


@dataclass(frozen=True)
class Microstep:
    word:int
    instruction:Microinstruction
    before:dict
    after:dict
    condition:bool
    next_source:str
    reads:tuple
    writes:tuple
    created_cells:tuple = ()

    @property
    def address_candidates(self):
        """All four pre-edge inputs of the CAR multiplexer, not predictions."""
        return (("CAR+1",(self.before['CAR']+1)&127),
                ("AD",self.instruction.ad),("SBR",self.before['SBR']),
                ("MAP",((self.before['DR']>>11)&15)<<2))


class MicroComputer:
    """Ideal synchronous datapath; all transfers/conditions sample old values.

    A single-port memory is assumed. Conflicting writes and reserved F3
    are rejected before any state change. SBR is one register, not a stack.
    """
    def __init__(self,control=None,memory=None,entry=64):
        self.control=dict(control or {})
        self.memory=dict(memory or {})
        if not 0<=entry<128 or any(not 0<=a<128 or not 0<=w<1<<20 for a,w in self.control.items()):
            raise ValueError("Invalid control store")
        if any(not 0<=a<2048 or not 0<=w<65536 for a,w in self.memory.items()):
            raise ValueError("Invalid data memory")
        self.car=entry
        self.sbr=self.ac=self.dr=self.ar=self.pc=0

    def registers(self):
        return {k:getattr(self,k.lower()) for k in ("CAR","SBR","AC","DR","AR","PC")}

    def step(self):
        old=self.registers()
        if self.car not in self.control:
            raise ValueError("Uninitialized control address")
        word=self.control[self.car]
        ins=Microinstruction.decode(word)
        a,d,ar,pc=self.ac,self.dr,self.ar,self.pc
        updates={}
        reads=[]
        writes=[]
        def setreg(name,value):
            if name in updates:
                raise ValueError("Conflicting microoperations")
            updates[name]=value & (2047 if name in ("AR","PC") else 65535)
        for op in ins.operations:
            if op in ("ADD","SUB","OR","AND","XOR"):
                setreg("AC",alu(op,a,d).word)
            elif op in ("INCAC","COM","SHL","SHR"):
                setreg("AC",alu({"INCAC":"INC","COM":"NOT","SHL":"SHL","SHR":"SHR"}[op],a).word)
            elif op=="CLRAC":setreg("AC",0)
            elif op=="DRTAC":setreg("AC",d)
            elif op=="DRTAR":setreg("AR",d)
            elif op=="PCTAR":setreg("AR",pc)
            elif op=="WRITE":writes.append((ar,self.memory.get(ar,0),d))
            elif op=="READ":
                v=self.memory.get(ar,0)
                reads.append((ar,v))
                setreg("DR",v)
            elif op=="ACTDR":setreg("DR",a)
            elif op=="INCDR":setreg("DR",d+1)
            elif op=="PCTDR":setreg("DR",(d&0xF800)|pc)
            elif op=="INCPC":setreg("PC",pc+1)
            elif op=="ARTPC":setreg("PC",ar)
            else:raise ValueError("Reserved microoperation")
        if reads and writes:
            raise ValueError("Conflicting memory access")
        condition=(True,bool(d&0x8000),bool(a&0x8000),a==0)[ins.cd]
        sequential=(self.car+1)&127
        if ins.br==2:
            next_address,source=self.sbr,"SBR"
        elif ins.br==3:
            next_address,source=((d>>11)&15)<<2,"MAP"
        elif condition:
            next_address,source=ins.ad,"AD"
            if ins.br==1:self.sbr=sequential
        else:
            next_address,source=sequential,"CAR+1"
        for name,value in updates.items():setattr(self,name.lower(),value)
        created=tuple(address for address,_,_ in writes if address not in self.memory)
        for address,_,value in writes:self.memory[address]=value
        self.car=next_address
        return Microstep(word,ins,old,self.registers(),condition,source,tuple(reads),tuple(writes),created)


def parse_image(text,address_limit,word_limit):
    """Strict sparse hex address:word image; blank lines and # comments allowed."""
    import re
    image={}
    for i,line in enumerate(text.splitlines(),1):
        line=line.split("#",1)[0].strip()
        if not line:continue
        m=re.fullmatch(r"([0-9A-Fa-f]{1,4})\s*:\s*([0-9A-Fa-f]{1,5})",line)
        if not m:raise ValueError(f"Invalid image line {i}")
        addr,word=(int(x,16) for x in m.groups())
        if addr>=address_limit or word>=word_limit or addr in image:
            raise ValueError(f"Invalid or duplicate address/word at line {i}")
        image[addr]=word
    return image


def demo_images():
    """Original demonstration: ADD direct and indirect plus a shared pointer routine."""
    def w(f1=0,f2=0,f3=0,cd=0,br=0,ad=0):
        return Microinstruction(f1,f2,f3,cd,br,ad).encode()
    control={
        64:w(f1=6,ad=65),65:w(f2=4,f3=5,ad=66),66:w(f1=5,br=3),
        0:w(cd=1,br=1,ad=80),1:w(f2=4,ad=2),2:w(f1=1,ad=64),
        80:w(f2=4,ad=81),81:w(f1=5,br=2)}
    memory={0:0x0100,1:0x8101,0x100:5,0x101:0x102,0x102:7}
    return control,memory
