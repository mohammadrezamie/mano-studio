"""Bounded undo for Chapter 7; executes only the existing MicroComputer."""
from collections import deque


class MicroHistory:
    def __init__(self,model,limit=512):
        if not 1<=limit<=10000:
            raise ValueError("Invalid history limit")
        self.model=model
        self.entries=deque(maxlen=limit)
        self.steps=0

    def step(self):
        event=self.model.step()
        self.steps+=1
        self.entries.append((self.steps,event))
        return event

    def back(self):
        if not self.entries:
            return None
        number,event=self.entries.pop()
        for address,old,_ in reversed(event.writes):
            if address in event.created_cells:
                self.model.memory.pop(address,None)
            else:
                self.model.memory[address]=old
        for name,value in event.before.items():
            setattr(self.model,name.lower(),value)
        self.steps=number-1
        return event
