"""Deterministic two-processor lost-update and atomic test-and-set experiment.

Each action is one ideal sequentially consistent model event. The atomic lock
and data operations are illustrative, not instructions of Mano Basic Computer.
"""
from dataclasses import dataclass
from memory_organization import MemoryArray


@dataclass
class Worker:
    remaining:int
    phase:str
    local:int | None=None


@dataclass(frozen=True)
class SyncEvent:
    number:int
    processor:int
    action:str
    phase:str
    local:int | None
    shared:int
    owner:int | None
    remaining:int


class Synchronization:
    def __init__(self,locked=True,repeats=1,initial=0):
        if type(locked) is not bool or type(repeats) is not int or not 1<=repeats<=8:
            raise ValueError("Invalid experiment configuration")
        if type(initial) is not int or not 0<=initial<65536:
            raise ValueError("Invalid initial word")
        self.locked=locked;self.repeats=repeats;self.initial=initial
        self.ram=MemoryArray(4,8,1,2)
        self.ram.write(0,initial)
        self.owner=None
        self.workers=[Worker(repeats,"acquire" if locked else "read") for _ in range(2)]
        self.events=[]

    @property
    def shared(self):return self.ram.read(0)

    @property
    def expected(self):return (self.initial+2*self.repeats)&0xFFFF

    @property
    def done(self):return all(w.remaining==0 and w.phase=="done" for w in self.workers)

    def _complete(self,w):
        w.remaining-=1
        w.phase=("acquire" if self.locked else "read") if w.remaining else "done"

    def step(self,processor):
        if type(processor) is not int or processor not in (0,1):raise ValueError("Invalid processor")
        w=self.workers[processor]
        if w.phase=="done":return None
        phase=w.phase;action=phase
        if phase=="acquire":
            if self.owner is None:
                self.owner=processor;w.phase="read"
            else:action="wait"
        elif phase=="read":
            w.local=self.shared;w.phase="increment"
        elif phase=="increment":
            w.local=(w.local+1)&0xFFFF;w.phase="write"
        elif phase=="write":
            self.ram.write(0,w.local)
            if self.locked:w.phase="release"
            else:self._complete(w)
        elif phase=="release":
            if self.owner!=processor:raise AssertionError("Lock ownership violated")
            self.owner=None;self._complete(w)
        else:raise AssertionError("Unknown phase")
        event=SyncEvent(len(self.events)+1,processor,action,w.phase,w.local,
                        self.shared,self.owner,w.remaining)
        self.events.append(event)
        return event

    def run(self):
        """Alternating schedule; no real threads and no wall-clock assumptions."""
        while not self.done:
            self.step(0);self.step(1)
        return tuple(self.events)
