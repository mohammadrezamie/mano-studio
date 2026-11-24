"""Ideal DMA bus ownership protocol and synchronous circular FIFO.

The CPU is an abstract bus user, not the Chapter 5 simulator. DMA transfer
edges operate on actual MemoryArray RAM chips; completion raises IRQ2.
"""
from dataclasses import dataclass
from collections import deque
from memory_organization import MemoryArray


@dataclass(frozen=True)
class DMAEvent:
    number:int
    action:str
    owner:str
    request:bool
    grant:bool
    address:int | None
    value:int | None
    remaining:int
    irq:bool


class DMA:
    def __init__(self,memory,device,direction,start,count,mode="burst",interrupt=None):
        if direction not in ("to_memory","from_memory") or mode not in ("burst","cycle_steal"):
            raise ValueError("Invalid DMA mode")
        if not isinstance(memory,MemoryArray) or memory.width!=16:
            raise ValueError("Expected 16-bit memory array")
        if type(start) is not int or type(count) is not int or not 1<=count<=memory.size or not 0<=start<=memory.size-count:
            raise ValueError("Invalid DMA address range")
        data=tuple(device)
        for value in data:memory.slices(value)
        if direction=="to_memory" and len(data)!=count:
            raise ValueError("Device must supply exactly count words")
        if direction=="from_memory" and data:
            raise ValueError("Output device must start empty")
        self.memory=memory
        self.device=deque(data)
        self.direction=direction
        self.mode=mode
        self.address=start
        self.remaining=count
        self.interrupt=interrupt
        self.phase="request"
        self.owner="CPU"
        self.irq=False
        self.cycles=0

    @property
    def done(self):return self.phase=="done"

    def step(self):
        if self.done:return None
        action=self.phase
        address=value=None
        if action=="request":self.phase="grant"
        elif action=="grant":
            self.owner="DMA"
            self.phase="transfer"
        elif action=="transfer":
            address=self.address
            if self.direction=="to_memory":
                value=self.device.popleft()
                self.memory.write(address,value)
            else:
                value=self.memory.read(address)
                self.device.append(value)
            self.address+=1
            self.remaining-=1
            if not self.remaining or self.mode=="cycle_steal":self.phase="release"
        elif action=="release":
            self.owner="CPU"
            if self.remaining:self.phase="cpu_cycle"
            else:
                self.phase="done"
                self.irq=True
                if self.interrupt is not None:self.interrupt.request(2)
        elif action=="cpu_cycle":self.phase="request"
        self.cycles+=1
        return DMAEvent(self.cycles,action,self.owner,
            self.phase in ("grant","transfer","release"),
            self.owner=="DMA",address,value,self.remaining,self.irq)

    def run(self):
        events=[]
        while not self.done:events.append(self.step())
        return tuple(events)


@dataclass(frozen=True)
class FIFOEvent:
    read_value:int | None
    written:int | None
    read_pointer:int
    write_pointer:int
    depth:int


class CircularFIFO:
    """One read and/or write per edge; full exchange allowed, no empty bypass.

    A failed read/write rejects the whole edge before mutation. Physical
    stale cells remain visible; logical occupancy follows pointers/count.
    """
    def __init__(self,capacity=8):
        if capacity not in (4,8,16):raise ValueError("Invalid FIFO capacity")
        self.capacity=capacity
        self.cells=[0]*capacity
        self.read_pointer=self.write_pointer=self.depth=0

    @property
    def full(self):return self.depth==self.capacity

    @property
    def empty(self):return self.depth==0

    def contents(self):
        return tuple(self.cells[(self.read_pointer+i)%self.capacity] for i in range(self.depth))

    def edge(self,read=False,write=None):
        if write is not None and (type(write) is not int or not 0<=write<=65535):
            raise ValueError("Invalid FIFO word")
        if read and self.empty:raise ValueError("FIFO underflow")
        if write is not None and self.full and not read:raise ValueError("FIFO overflow")
        value=None
        if read:
            value=self.cells[self.read_pointer]
            self.read_pointer=(self.read_pointer+1)%self.capacity
            self.depth-=1
        if write is not None:
            self.cells[self.write_pointer]=write
            self.write_pointer=(self.write_pointer+1)%self.capacity
            self.depth+=1
        return FIFOEvent(value,write,self.read_pointer,self.write_pointer,self.depth)
