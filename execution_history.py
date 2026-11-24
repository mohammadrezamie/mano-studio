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

    def _record(self,event):
        if event is not None:
            self.steps+=1
            self.entries.append(TraceEntry(self.steps,event))
        return event

    def step(self):
        return self._record(self.cpu.step())

    def microstep(self):
        group=self.cpu.microstep()
        if group is not None and group.final:self._record(self.cpu.completed_event)
        return group

    def microback(self):
        if self.cpu.in_progress:return self.cpu.rewind_group()
        event=self.back()
        if event is None:return None
        for _ in range(len(event.microevents)-1):self.cpu.microstep()
        return event.microevents[-1]

    def back(self):
        if self.cpu.in_progress:return self.cpu.cancel_pending()
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
        if self.cpu.in_progress:raise ValueError("Finish or rewind the current instruction before I/O")
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
        return not self.cpu.in_progress and self.cpu.pc in self.breakpoints and not self.cpu.halted
