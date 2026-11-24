"""Clocked digital components, independent of Qt and the combinational engine.

Ideal positive-edge-triggered models; not an electrical timing simulator.
Every sample records the actual clock, input pins and output pins.
"""
from collections import deque
from dataclasses import dataclass

MODELS = {
    "D": (("D",), 1),
    "JK": (("J","K"), 1),
    "T": (("T",), 1),
    "SR": (("S","R"), 1),
    "REG4": (("D0","D1","D2","D3","EN"), 4),
    "COUNT4": (("EN",), 4),
}


@dataclass(frozen=True)
class Sample:
    clock: int
    inputs: tuple
    outputs: tuple


class ClockedCircuit:
    def __init__(self, kind):
        if kind not in MODELS:
            raise ValueError("Unknown clocked component")
        self.kind=kind
        self.pins,self.width=MODELS[kind]
        self.reset()

    @property
    def outputs(self):
        if self.width==1:
            return {"Q":self.value,"Qbar":1-self.value}
        return {f"Q{i}":(self.value>>i)&1 for i in range(self.width)}

    def sample(self):
        item=Sample(self.clock,tuple(self.inputs.values()),tuple(self.outputs.values()))
        if not self.history or self.history[-1]!=item:
            self.history.append(item)

    def reset(self):
        self.value=0
        self.clock=0
        self.inputs=dict.fromkeys(self.pins,0)
        self.history=deque(maxlen=64)
        self.sample()

    def set_input(self,name,bit):
        if name not in self.inputs or bit not in (0,1):
            raise ValueError("Invalid input")
        self.inputs[name]=int(bit)
        self.sample()

    def set_clock(self,bit):
        if bit not in (0,1):
            raise ValueError("Invalid clock")
        if self.clock==0 and bit==1:
            p=self.inputs
            if self.kind=="D":
                self.value=p["D"]
            elif self.kind=="JK":
                self.value=(self.value ^ 1) if p["J"] and p["K"] else 1 if p["J"] else 0 if p["K"] else self.value
            elif self.kind=="T":
                self.value^=p["T"]
            elif self.kind=="SR":
                if p["S"] and p["R"]:
                    raise ValueError("SR = 11 is forbidden; clock edge rejected.")
                self.value=1 if p["S"] else 0 if p["R"] else self.value
            elif self.kind=="REG4" and p["EN"]:
                self.value=sum(p[f"D{i}"]<<i for i in range(4))
            elif self.kind=="COUNT4" and p["EN"]:
                self.value=(self.value+1)&15
        self.clock=int(bit)
        self.sample()

    def pulse(self):
        self.set_clock(0)
        self.set_clock(1)
        self.set_clock(0)
