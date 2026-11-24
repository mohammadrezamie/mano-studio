"""Chapter 13 shared-bus arbitration, ideal word transactions.

One complete word transaction per clock. Fixed or rotating priority.
No cache, locks, simultaneous bus ownership, electrical delay, or CPU ISA.
"""
from dataclasses import dataclass
from collections import deque


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
        if type(master) is not int or not 0<=master<4:raise ValueError("Invalid master")
        if type(address) is not int or not 0<=address<64:raise ValueError("Invalid address")
        if value is not None and (type(value) is not int or not 0<=value<65536):raise ValueError("Invalid word")
        if len(self.queues[master])>=32:raise ValueError("Queue full")
        self.queues[master].append(Request(address,value))

    @property
    def done(self):return not any(self.queues)

    def step(self):
        pending=tuple(len(q) for q in self.queues)
        start=self.priority if self.policy=="rotating" else 0
        order=tuple((start+i)%4 for i in range(4))
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
