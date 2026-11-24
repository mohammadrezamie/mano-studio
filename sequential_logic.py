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
    "SHIFT4": (("SI","EN"),4),
    "UNIVERSAL4": (("D0","D1","D2","D3","SL","SR","S1","S0"),4),
    "UPDOWN4": (("D0","D1","D2","D3","EN","UP","LOAD","CLR"),4),
    "RING4": (("EN",),4),
    "JOHNSON4": (("EN",),4),
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
            self.sample_count+=1

    def reset(self):
        self.value=1 if self.kind=="RING4" else 0
        self.clock=0
        self.inputs=dict.fromkeys(self.pins,0)
        self.history=deque(maxlen=64)
        self.sample_count=0
        self.sample()

    def set_input(self,name,bit):
        if name not in self.inputs or bit not in (0,1):
            raise ValueError("Invalid input")
        self.inputs[name]=int(bit)
        self.sample()

    def next_value(self):
        """Evaluate the next rising-edge state without mutating history or pins."""
        return transition(self.kind,self.value,self.inputs)

    def set_clock(self,bit):
        if bit not in (0,1):
            raise ValueError("Invalid clock")
        if self.clock==0 and bit==1:
            self.value=self.next_value()
        self.clock=int(bit)
        self.sample()

    def pulse(self):
        self.set_clock(0)
        self.set_clock(1)
        self.set_clock(0)


def transition(kind,q,p):
    """Ideal synchronous state transition. q is an unsigned word, Q0 is LSB."""
    if kind not in MODELS:
        raise ValueError("Unknown clocked component")
    pins,width=MODELS[kind]
    if not isinstance(q,int) or not 0<=q<(1<<width) or set(p)!=set(pins) or any(v not in (0,1) for v in p.values()):
        raise ValueError("Invalid state or inputs")
    if kind=="D":return int(p["D"])
    if kind=="JK":return (p["J"] & (1-q)) | ((1-p["K"]) & q)
    if kind=="T":return q^p["T"]
    if kind=="SR":
        if p["S"] and p["R"]:raise ValueError("SR = 11 is forbidden; clock edge rejected.")
        return p["S"] | ((1-p["R"]) & q)
    if kind=="REG4":
        return sum(p[f"D{i}"]<<i for i in range(4)) if p["EN"] else q
    if kind=="COUNT4":return (q+p["EN"])&15
    if kind=="SHIFT4":return ((q<<1)|p["SI"])&15 if p["EN"] else q
    if kind=="UNIVERSAL4":
        mode=2*p["S1"]+p["S0"]
        if mode==0:return q
        if mode==1:return (q>>1)|(p["SR"]<<3)
        if mode==2:return ((q<<1)|p["SL"])&15
        return sum(p[f"D{i}"]<<i for i in range(4))
    if kind=="UPDOWN4":
        if p["CLR"]:return 0
        if p["LOAD"]:return sum(p[f"D{i}"]<<i for i in range(4))
        return (q+(1 if p["UP"] else -1))&15 if p["EN"] else q
    if kind=="RING4":
        return ((q<<1)|(q>>3))&15 if p["EN"] else q
    if kind=="JOHNSON4":
        return ((q<<1)|(1-(q>>3)))&15 if p["EN"] else q
    raise AssertionError("Missing transition")


RULES = {
    "D": ("Q′ = D","Next state equals D.","حالت بعد برابر D است."),
    "JK": ("Q′ = J·¬Q + ¬K·Q","J=K=1 toggles Q.","با J=K=1 مقدار Q معکوس می‌شود."),
    "T": ("Q′ = Q ⊕ T","T=1 toggles Q.","با T=1 مقدار Q معکوس می‌شود."),
    "SR": ("Q′ = S + ¬R·Q","S=R=1 is forbidden.","حالت S=R=1 نامعتبر است."),
    "REG4": ("Q′ = EN ? D : Q","EN controls parallel load; D = D3…D0.","با EN=1 بارگذاری موازی انجام می‌شود."),
    "COUNT4": ("Q′ = (Q + EN) mod 16","Four-bit modulo-16 counter.","شمارنده ۴ بیتی پیمانه ۱۶."),
    "SHIFT4": ("Q′ = EN ? ((2Q + SI) mod 16) : Q","Shift toward the MSB; SI enters Q0.","شیفت به سوی بیت پرارزش؛ SI وارد Q0 می‌شود."),
    "UNIVERSAL4": ("S1S0: 00 Q | 01 (Q >> 1) + 8SR | 10 (2Q + SL) mod 16 | 11 D","Hold, numeric right shift, left shift, or parallel load. SL enters Q0; SR enters Q3.","حفظ، شیفت راست عددی، شیفت چپ یا بارگذاری موازی؛ SL وارد Q0 و SR وارد Q3 می‌شود."),
    "UPDOWN4": ("CLR > LOAD > EN; Q′ = 0 | D | (Q ± 1) mod 16 | Q","Synchronous clear overrides load, then enable; UP=1 counts up.","صفرکردن همگام بر بارگذاری و فعال‌سازی اولویت دارد؛ UP=1 شمارش صعودی."),
    "RING4": ("Q′ = EN ? ((2Q + Q3) mod 16) : Q","Reset seeds 0001; one bit circulates.","بازنشانی از 0001 آغاز می‌کند؛ یک بیت در حلقه می‌چرخد."),
    "JOHNSON4": ("Q′ = EN ? ((2Q + ¬Q3) mod 16) : Q","Inverted feedback; eight states from zero.","بازخورد معکوس؛ هشت حالت از صفر."),
}
