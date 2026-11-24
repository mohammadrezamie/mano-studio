"""Bounded reversible instruction history. No second CPU or full memory copies."""
from collections import deque
from dataclasses import dataclass
from simulator import CPU, StepEvent

@dataclass(frozen=True)
class TraceEntry:
    number: int
    event: StepEvent

class ExecutionHistory:
    def __init__(self,cpu: CPU,limit=512):
        if not 1<=limit<=10000:
            raise ValueError("Invalid history limit")
        self.cpu=cpu
        self.entries=deque(maxlen=limit)
        self.steps=0
        self.breakpoints=set()

    def step(self):
        event=self.cpu.step()
        if event is not None:
            self.steps+=1
            self.entries.append(TraceEntry(self.steps,event))
        return event

    def back(self):
        if not self.entries:
            return None
        entry=self.entries.pop()
        event=entry.event
        for address,old,_ in reversed(event.writes):
            self.cpu.memory[address]=old
        for name,value in event.before.items():
            setattr(self.cpu,name.lower(),value)
        self.steps=entry.number-1
        return event

    def barrier(self):
        """External input/output or memory edits start a new reversible segment."""
        self.entries.clear()

    def toggle_breakpoint(self,address):
        if not 0<=address<=0xFFF:
            raise ValueError("Breakpoint outside memory")
        if address in self.breakpoints:
            self.breakpoints.remove(address)
            return False
        self.breakpoints.add(address)
        return True

    def should_break(self):
        # Interrupt service may replace the next instruction; do not claim a
        # hardware microcycle breakpoint. PC address is the pre-step boundary.
        return self.cpu.pc in self.breakpoints and not self.cpu.halted
