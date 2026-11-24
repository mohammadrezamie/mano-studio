"""Chapter 13 shared-bus arbitration, ideal word transactions.

One complete word transaction per clock. Fixed or rotating priority.
No cache, locks, simultaneous bus ownership, electrical delay, or CPU ISA.
"""
from dataclasses import dataclass
from collections import deque
from memory_organization import MemoryArray


def priority_order(policy,start):
    return tuple(((start if policy=='rotating' else 0)+i)%4 for i in range(4))


def queue_request(queues,master,address,value):
    if type(master) is not int or not 0<=master<4:raise ValueError('Invalid master')
    if type(address) is not int or not 0<=address<64:raise ValueError('Invalid address')
    if value is not None and (type(value) is not int or not 0<=value<65536):raise ValueError('Invalid word')
    if len(queues[master])>=32:raise ValueError('Queue full')
    queues[master].append(Request(address,value))


@dataclass(frozen=True)
class Request:
    address:int
    value:int | None=None


@dataclass(frozen=True)
class BusCycle:
    number:int
    pending:tuple
    order:tuple
    grant:int | None
    request:Request | None
    value:int | None
    old:int | None
    next_priority:int
    waiting:tuple


class SharedBus:
    def __init__(self,policy="rotating"):
        if policy not in ("fixed","rotating"):raise ValueError("Invalid policy")
        self.policy=policy
        self.queues=[deque() for _ in range(4)]
        self.memory=[0]*64
        self.priority=0
        self.cycles=0
        self.served=[0]*4
        self.waited=[0]*4

    def enqueue(self,master,address,value=None):
        queue_request(self.queues,master,address,value)

    @property
    def done(self):return not any(self.queues)

    def step(self):
        pending=tuple(len(q) for q in self.queues)
        order=priority_order(self.policy,self.priority)
        winner=next((i for i in order if pending[i]),None)
        request=value=old=None
        if winner is not None:
            request=self.queues[winner].popleft()
            old=self.memory[request.address]
            if request.value is not None:self.memory[request.address]=request.value
            value=self.memory[request.address]
            self.served[winner]+=1
            if self.policy=="rotating":self.priority=(winner+1)%4
        waiting=tuple(i for i in range(4) if pending[i] and i!=winner)
        for i in waiting:self.waited[i]+=1
        self.cycles+=1
        return BusCycle(self.cycles,pending,order,winner,request,value,old,self.priority,waiting)

    def run(self):
        result=[]
        while not self.done:result.append(self.step())
        return tuple(result)



@dataclass(frozen=True)
class Transfer:
    master:int
    bank:int
    request:Request
    value:int
    old:int


@dataclass(frozen=True)
class CrossbarCycle:
    number:int
    heads:tuple
    orders:tuple
    transfers:tuple
    waiting:tuple


class Crossbar:
    """Four masters, four independent RAM banks; one head per master per clock.

    All requests are sampled before arbitration. Only the head of each
    master's FIFO participates (head-of-line blocking); disjoint banks can
    complete concurrently. No electrical timing or coherence.
    """
    def __init__(self,policy="rotating"):
        if policy not in ("fixed","rotating"):raise ValueError("Invalid policy")
        self.policy=policy
        self.queues=[deque() for _ in range(4)]
        self.memory=MemoryArray(4,8,4,2)
        self.priority=[0]*4
        self.cycles=0
        self.served=[0]*4
        self.waited=[0]*4
        self.bank_served=[0]*4

    def enqueue(self,master,address,value=None):
        queue_request(self.queues,master,address,value)

    @property
    def done(self):return not any(self.queues)

    def step(self):
        heads=tuple(q[0] if q else None for q in self.queues)
        banks=tuple(self.memory.decode(r.address).bank if r is not None else None for r in heads)
        orders=tuple(priority_order(self.policy,p) for p in self.priority)
        winners=tuple(next((m for m in orders[b] if banks[m]==b),None) for b in range(4))
        transfers=[]
        for bank,master in enumerate(winners):
            if master is None:continue
            request=self.queues[master].popleft()
            old=self.memory.read(request.address)
            if request.value is not None:self.memory.write(request.address,request.value)
            transfers.append(Transfer(master,bank,request,self.memory.read(request.address),old))
            self.served[master]+=1;self.bank_served[bank]+=1
            if self.policy=="rotating":self.priority[bank]=(master+1)%4
        waiting=tuple(i for i,r in enumerate(heads) if r is not None and i not in winners)
        for master in waiting:self.waited[master]+=1
        self.cycles+=1
        return CrossbarCycle(self.cycles,heads,orders,tuple(transfers),waiting)

    def run(self):
        events=[]
        while not self.done:events.append(self.step())
        return tuple(events)
