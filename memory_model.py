"""Ideal addressed RAM/ROM with active-low control signals.

Separate input/output buses are an educational abstraction, not a specific
physical chip. Writes occur only on an explicit transaction, not on a GUI edit.
None is high impedance (Z), distinct from the binary word zero.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class MemoryAccess:
    address: int
    operation: str
    before: int
    after: int
    output: int | None

class MemoryChip:
    def __init__(self,kind="RAM",address_bits=4,word_bits=8,contents=None):
        if kind not in ("RAM","ROM") or address_bits not in (4,8) or word_bits not in (4,8):
            raise ValueError("Unsupported memory organization")
        self.kind=kind
        self.address_bits=address_bits
        self.word_bits=word_bits
        self.size=1<<address_bits
        self.mask=(1<<word_bits)-1
        initial=tuple(contents) if contents is not None else tuple(
            ((address ^ 0xA5)&self.mask if kind=="ROM" else 0) for address in range(self.size))
        if len(initial)!=self.size or any(type(v) is not int or not 0<=v<=self.mask for v in initial):
            raise ValueError("Invalid memory contents")
        self.initial=initial
        self._words=list(initial)

    @property
    def words(self):
        return tuple(self._words)

    def reset(self):
        self._words=list(self.initial)

    def _validate(self,address,cs_n,oe_n,we_n,data=0):
        if type(address) is not int or not 0<=address<self.size:
            raise ValueError("Address outside memory")
        if any(v not in (0,1) for v in (cs_n,oe_n,we_n)):
            raise ValueError("Control signals must be binary")
        if type(data) is not int or not 0<=data<=self.mask:
            raise ValueError("Data outside word width")

    def operation(self,cs_n,oe_n,we_n):
        if cs_n:return "DISABLED"
        if self.kind=="RAM" and not we_n:return "WRITE"
        if not oe_n:return "READ"
        return "IDLE"

    def output(self,address,cs_n=0,oe_n=0,we_n=1):
        self._validate(address,cs_n,oe_n,we_n)
        return self._words[address] if self.operation(cs_n,oe_n,we_n)=="READ" else None

    def access(self,address,cs_n=0,oe_n=0,we_n=1,data=0):
        self._validate(address,cs_n,oe_n,we_n,data)
        op=self.operation(cs_n,oe_n,we_n)
        before=self._words[address]
        if op=="WRITE":self._words[address]=data
        return MemoryAccess(address,op,before,self._words[address],self.output(address,cs_n,oe_n,we_n))
