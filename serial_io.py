"""Ideal asynchronous serial framing, one already-aligned bit slot per step.

No baud mismatch, electrical signalling, start detection or oversampling.
A bad frame is discarded; one IRQ notification per completed frame.
"""
from dataclasses import dataclass
from dma_model import CircularFIFO


@dataclass(frozen=True)
class Format:
    data_bits:int=8
    parity:str="none"
    stop_bits:int=1

    def __post_init__(self):
        if self.data_bits not in (5,6,7,8) or self.parity not in ("none","even","odd") or self.stop_bits not in (1,2):
            raise ValueError("Invalid serial format")

    @property
    def labels(self):
        return ("START",)+tuple(f"D{i}" for i in range(self.data_bits))+(("P",) if self.parity!="none" else ())+tuple(f"STOP{i+1}" for i in range(self.stop_bits))


def encode(value,fmt):
    if type(value) is not int or not 0<=value<(1<<fmt.data_bits):
        raise ValueError("Payload outside format")
    data=tuple((value>>i)&1 for i in range(fmt.data_bits))
    parity=() if fmt.parity=="none" else ((sum(data)%2)^int(fmt.parity=="odd"),)
    return (0,)+data+parity+(1,)*fmt.stop_bits


@dataclass(frozen=True)
class Received:
    value:int
    start_error:bool
    parity_error:bool
    framing_error:bool

    @property
    def ok(self):return not(self.start_error or self.parity_error or self.framing_error)


def decode(bits,fmt):
    bits=tuple(bits)
    if len(bits)!=len(fmt.labels) or any(type(b) is not int or b not in (0,1) for b in bits):
        raise ValueError("Invalid frame")
    data=bits[1:1+fmt.data_bits]
    parity_error=False
    if fmt.parity!="none":
        parity_error=(sum(data)+bits[1+fmt.data_bits])%2!=int(fmt.parity=="odd")
    return Received(sum(b<<i for i,b in enumerate(data)),bits[0]!=0,
                    parity_error,any(b!=1 for b in bits[-fmt.stop_bits:]))


@dataclass(frozen=True)
class BitEvent:
    index:int
    label:str
    tx:int
    rx:int
    shift:int
    result:Received | None
    overrun:bool
    queued:bool


class SerialLink:
    """Single frame in flight; receiver queue persists across frames."""
    def __init__(self,fmt=Format(),capacity=4,notify=None):
        self.format=fmt;self.fifo=CircularFIFO(capacity);self.notify=notify
        self.tx=();self.rx=[];self.events=[]
        self.flip=None;self.shift=0;self.result=None
        self.overrun=False;self.completed=0;self.errors=0;self.dropped=0

    @property
    def active(self):return len(self.rx)<len(self.tx)

    def start(self,value,flip=None):
        if self.active:raise ValueError("Frame in progress")
        tx=encode(value,self.format)
        if flip is not None and (type(flip) is not int or not 0<=flip<len(tx)):
            raise ValueError("Invalid corruption position")
        self.tx=tx;self.rx=[];self.events=[];self.flip=flip
        self.shift=0;self.result=None;self.overrun=False

    def step(self):
        if not self.active:return None
        index=len(self.rx);tx=self.tx[index];rx=tx^int(index==self.flip)
        self.rx.append(rx)
        if 1<=index<=self.format.data_bits:self.shift|=rx<<(index-1)
        queued=False
        if not self.active:
            self.result=decode(self.rx,self.format)
            self.completed+=1
            if not self.result.ok:self.errors+=1
            elif self.fifo.full:
                self.overrun=True;self.dropped+=1
            else:
                self.fifo.edge(write=self.result.value);queued=True
        event=BitEvent(index,self.format.labels[index],tx,rx,self.shift,self.result,self.overrun,queued)
        self.events.append(event)
        if self.result is not None and self.notify is not None:self.notify()
        return event

    def run(self):
        while self.active:self.step()
        return tuple(self.events)

    def read(self):
        return self.fifo.edge(read=True).read_value
