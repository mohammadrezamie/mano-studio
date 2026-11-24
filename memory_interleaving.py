"""Banked memory timing, reusing the actual MemoryArray chip model.

One in-order request may issue each clock. Independent non-pipelined
banks take latency clocks including the issue clock. A bank becomes
available on the clock AFTER completion. No cache, bus arbitration,
refresh, or out-of-order issue is implied.
"""
from dataclasses import dataclass
from memory_organization import MemoryArray


@dataclass(frozen=True)
class Request:
    address:int
    value:int | None=None  # None = read, otherwise write


@dataclass(frozen=True)
class Access:
    number:int
    request:Request
    bank:int
    local:int
    start:int
    finish:int


@dataclass(frozen=True)
class Completion:
    access:Access
    value:int


@dataclass(frozen=True)
class MemoryCycle:
    number:int
    issued:Access | None
    stalled_bank:int | None
    active:tuple
    completed:tuple


class Interleaving:
    def __init__(self,requests,banks=4,latency=4,interleaved=True,initial=None):
        if banks not in (1,2,4) or not 1<=latency<=16:
            raise ValueError("Invalid bank count or latency")
        self.array=MemoryArray(4,8,banks,2,interleaved=interleaved)
        self.requests=tuple(requests)
        if not 1<=len(self.requests)<=128:
            raise ValueError("Expected 1–128 requests")
        for request in self.requests:
            self.array.decode(request.address)
            if request.value is not None:self.array.slices(request.value)
        for address,value in (initial or {}).items():
            self.array.write(address,value)
        self.latency=latency
        self.pending=[None]*banks
        self.cursor=0
        self.cycles=0
        self.stalls=0
        self.results=[]

    @property
    def done(self):
        return self.cursor==len(self.requests) and not any(self.pending)

    def step(self):
        if self.done:return None
        self.cycles+=1
        clock=self.cycles
        issued=None;stalled=None
        if self.cursor<len(self.requests):
            request=self.requests[self.cursor]
            selection=self.array.decode(request.address)
            bank=selection.bank
            if self.pending[bank] is not None:
                stalled=bank
                self.stalls+=1
            else:
                issued=Access(self.cursor+1,request,bank,selection.local,clock,clock+self.latency-1)
                self.pending[bank]=issued
                self.cursor+=1
        active=tuple(self.pending)
        completed=[]
        for bank,access in enumerate(active):
            if access is not None and access.finish==clock:
                request=access.request
                if request.value is None:
                    value=self.array.read(request.address)
                else:
                    self.array.write(request.address,request.value)
                    value=request.value
                result=Completion(access,value)
                completed.append(result)
                self.results.append(result)
                self.pending[bank]=None
        return MemoryCycle(clock,issued,stalled,active,tuple(completed))

    def run(self):
        cycles=[]
        while not self.done:cycles.append(self.step())
        return tuple(cycles)


def parse_requests(text):
    """One hexadecimal address, optionally :hexadecimal write word per token."""
    import re
    if len(text)>4096:raise ValueError("Input too long")
    tokens=text.split()
    if not 1<=len(tokens)<=128:raise ValueError("Expected 1–128 requests")
    result=[]
    for token in tokens:
        if not re.fullmatch(r"[0-9A-Fa-f]{1,4}(?::[0-9A-Fa-f]{1,4})?",token):
            raise ValueError("Invalid address or write word")
        parts=token.split(":")
        result.append(Request(int(parts[0],16),int(parts[1],16) if len(parts)==2 else None))
    return tuple(result)
