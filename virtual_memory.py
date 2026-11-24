"""Ideal single-process demand paging; word addresses, no real OS/CPU."""
from dataclasses import dataclass
from collections import OrderedDict
from memory_organization import MemoryArray
from associative_memory import checked_word,masked_match


@dataclass
class Page:
    frame:int | None=None
    dirty:bool=False
    loaded:int=0
    used:int=0


@dataclass(frozen=True)
class Translation:
    number:int
    virtual:int
    vpn:int
    offset:int
    tlb_hit:bool
    fault:bool
    frame:int
    physical:int
    value:int
    write:bool
    evicted:int | None
    written_back:bool


class VirtualMemory:
    def __init__(self,replacement="lru",tlb_size=2):
        if replacement not in ("lru","fifo") or tlb_size not in (2,4):
            raise ValueError("Invalid configuration")
        self.replacement=replacement;self.tlb_size=tlb_size
        self.pages=[Page() for _ in range(16)]
        self.owners=[None]*4
        self.ram=MemoryArray(4,8,4,2)
        self.disk=[[0]*16 for _ in range(16)]
        self.tlb=OrderedDict()
        self.accesses=self.hits=self.faults=self.page_ins=self.page_outs=0

    def access(self,address,value=None):
        checked_word(address,8)
        if value is not None:checked_word(value,16)
        vpn,offset=divmod(address,16)
        self.accesses+=1
        page=self.pages[vpn]
        # Exact CAM comparison over currently valid VPN entries.
        hit=next((key for key in self.tlb if masked_match(key,vpn,15,4)),None)
        tlb_hit=hit is not None
        if tlb_hit:
            self.hits+=1;self.tlb.move_to_end(hit)
        fault=page.frame is None
        evicted=None;wb=False
        if fault:
            self.faults+=1
            frame=next((i for i,owner in enumerate(self.owners) if owner is None),None)
            if frame is None:
                evicted=min((owner for owner in self.owners),
                            key=lambda p:self.pages[p].used if self.replacement=="lru" else self.pages[p].loaded)
                victim=self.pages[evicted];frame=victim.frame
                if victim.dirty:
                    self.disk[evicted]=[self.ram.read(frame*16+i) for i in range(16)]
                    self.page_outs+=1;wb=True
                self.tlb.pop(evicted,None)
                self.pages[evicted]=Page()
            for i,word in enumerate(self.disk[vpn]):self.ram.write(frame*16+i,word)
            self.owners[frame]=vpn
            page.frame=frame;page.loaded=self.accesses
            self.page_ins+=1
        frame=page.frame;page.used=self.accesses
        if not tlb_hit:
            self.tlb[vpn]=frame
            if len(self.tlb)>self.tlb_size:self.tlb.popitem(last=False)
        physical=frame*16+offset
        if value is not None:
            self.ram.write(physical,value);page.dirty=True
        return Translation(self.accesses,address,vpn,offset,tlb_hit,fault,frame,
                           physical,self.ram.read(physical),value is not None,evicted,wb)
