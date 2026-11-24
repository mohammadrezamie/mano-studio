"""Ideal single-level, word-addressed cache for Chapter 12.

Eight four-word lines over a real MemoryArray (1024 x 16). Configurable
associativity, FIFO/LRU, write-through/write-back with write allocation.
Traffic is counted in words, not electrical timing or CPU cycles.
"""
from dataclasses import dataclass,field
from memory_organization import MemoryArray


@dataclass
class Line:
    tag:int | None=None
    data:list=field(default_factory=lambda:[0]*4)
    dirty:bool=False
    inserted:int=0
    used:int=0


@dataclass(frozen=True)
class Access:
    number:int
    address:int
    tag:int
    index:int
    offset:int
    way:int
    hit:bool
    write:bool
    value:int
    evicted_block:int | None
    written_back:bool
    ram_reads:int
    ram_writes:int


class Cache:
    def __init__(self,ways=1,replacement="lru",policy="back",memory=None):
        if ways not in (1,2,4,8) or replacement not in ("lru","fifo") or policy not in ("back","through"):
            raise ValueError("Invalid cache configuration")
        if memory is None:memory=MemoryArray(8,8,4,2)
        if memory.size!=1024 or memory.width!=16:raise ValueError("Expected 1024 x 16 RAM")
        self.memory=memory
        self.ways=ways;self.sets=8//ways
        self.replacement=replacement;self.policy=policy
        self.lines=[[Line() for _ in range(ways)] for _ in range(self.sets)]
        self.accesses=self.hits=self.misses=self.ram_reads=self.ram_writes=0

    def decode(self,address):
        if type(address) is not int or not 0<=address<1024:raise ValueError("Invalid address")
        block,offset=divmod(address,4)
        tag,index=divmod(block,self.sets)
        return tag,index,offset

    def writeback(self,index,line):
        if not line.dirty:return 0
        base=(line.tag*self.sets+index)*4
        for i,value in enumerate(line.data):self.memory.write(base+i,value)
        line.dirty=False
        self.ram_writes+=4
        return 4

    def access(self,address,value=None):
        tag,index,offset=self.decode(address)
        if value is not None:self.memory.slices(value)
        self.accesses+=1
        ways=self.lines[index]
        way=next((i for i,l in enumerate(ways) if l.tag==tag),None)
        hit=way is not None
        evicted=None;wb=False;reads=writes=0
        if hit:self.hits+=1
        else:
            self.misses+=1
            way=next((i for i,l in enumerate(ways) if l.tag is None),None)
            if way is None:
                way=min(range(self.ways),key=lambda i:ways[i].used if self.replacement=="lru" else ways[i].inserted)
            line=ways[way]
            if line.tag is not None:
                evicted=line.tag*self.sets+index
                writes=self.writeback(index,line);wb=bool(writes)
            base=address-offset
            ways[way]=Line(tag,[self.memory.read(base+i) for i in range(4)],False,self.accesses,self.accesses)
            reads=4;self.ram_reads+=4
        line=ways[way];line.used=self.accesses
        if value is not None:
            line.data[offset]=value
            if self.policy=="back":line.dirty=True
            else:
                self.memory.write(address,value);self.ram_writes+=1;writes+=1
        return Access(self.accesses,address,tag,index,offset,way,hit,value is not None,
                      line.data[offset],evicted,wb,reads,writes)

    def flush(self):
        """Write all dirty lines without invalidating or counting an access."""
        return sum(self.writeback(i,line) for i,ways in enumerate(self.lines) for line in ways)
