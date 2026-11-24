"""Ideal tri-state word bus and synchronous controlled register transfer."""
from dataclasses import dataclass

@dataclass(frozen=True)
class BusState:
    bits: str
    drivers: int
    @property
    def word(self):
        return int(self.bits,2) if set(self.bits)<=set("01") else None
    @property
    def contention(self):
        return "X" in self.bits

def resolve_bus(width,drivers):
    if width not in (4,8,16):
        raise ValueError("Unsupported bus width")
    active=tuple(v for v in drivers if v is not None)
    if any(type(v) is not int or not 0<=v<(1<<width) for v in active):
        raise ValueError("Driver outside bus width")
    bits=[]
    for i in reversed(range(width)):
        states={(v>>i)&1 for v in active}
        bits.append("Z" if not states else str(next(iter(states))) if len(states)==1 else "X")
    return BusState("".join(bits),len(active))

class RegisterBus:
    """Three registers; enabled outputs read old state and destinations load simultaneously."""
    def __init__(self,width=8):
        if width not in (4,8,16):raise ValueError("Unsupported bus width")
        self.width=width
        self.registers=[0,0,0]

    def set_word(self,index,word):
        if index not in (0,1,2) or type(word) is not int or not 0<=word<(1<<self.width):
            raise ValueError("Invalid register word")
        self.registers[index]=word

    def preview(self,enabled):
        if len(enabled)!=3:raise ValueError("Expected three enables")
        return resolve_bus(self.width,[v if en else None for v,en in zip(self.registers,enabled)])

    def transfer(self,enabled,load):
        if len(load)!=3:raise ValueError("Expected three load controls")
        state=self.preview(enabled)
        # Conservative teaching rule: one source only, even if multiple agree.
        if any(load) and state.drivers!=1:
            raise ValueError("Transfer requires exactly one enabled driver")
        for i,flag in enumerate(load):
            if flag:self.registers[i]=state.word
        return state
