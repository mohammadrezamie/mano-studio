"""Compose actual RAM chips in depth and width; word-addressed, ideal logic."""
from dataclasses import dataclass
from memory_model import MemoryChip

@dataclass(frozen=True)
class AddressSelection:
    bank: int
    local: int
    cs_n: tuple

class MemoryArray:
    def __init__(self, address_bits=4, chip_bits=8, banks=2, lanes=2, interleaved=False):
        if banks not in (1,2,4) or lanes not in (1,2,4) or chip_bits not in (4,8) or address_bits not in (4,8):
            raise ValueError("Unsupported memory array")
        self.address_bits=address_bits
        self.chip_bits=chip_bits
        self.banks=banks
        self.interleaved=interleaved
        self.lanes=lanes
        self.depth=1<<address_bits
        self.size=self.depth*banks
        self.width=chip_bits*lanes
        self.chips=tuple(tuple(MemoryChip("RAM",address_bits,chip_bits) for _ in range(lanes)) for _ in range(banks))

    def decode(self,address,enabled=True):
        if type(address) is not int or not 0<=address<self.size:
            raise ValueError("Address outside memory array")
        if self.interleaved:
            local,bank=divmod(address,self.banks)
        else:
            bank,local=divmod(address,self.depth)
        return AddressSelection(bank,local,tuple(int(not enabled or i!=bank) for i in range(self.banks)))

    def slices(self,word):
        if type(word) is not int or not 0<=word<(1<<self.width):
            raise ValueError("Word outside array width")
        return tuple((word>>(i*self.chip_bits))&((1<<self.chip_bits)-1) for i in range(self.lanes))

    def read(self,address,enabled=True):
        selected=self.decode(address,enabled)
        if not enabled:return None
        return sum(chip.output(selected.local)<<(i*self.chip_bits) for i,chip in enumerate(self.chips[selected.bank]))

    def write(self,address,word,enabled=True):
        selected=self.decode(address,enabled)
        pieces=self.slices(word) # validate whole word before any chip changes
        if enabled:
            for chip,piece in zip(self.chips[selected.bank],pieces):
                chip.access(selected.local,0,1,0,piece)
        return selected

    def reset(self):
        for bank in self.chips:
            for chip in bank:chip.reset()
