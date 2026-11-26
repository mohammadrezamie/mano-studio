"""Ideal shared 4-bit bus connecting real RAM and synchronous register models.

All drivers read pre-edge state. Destinations sample a single valid driver
simultaneously. Address comes from the old address register, even when loaded.
No electrical timing, multi-clock domains or arbitrary wiring is modeled.
"""
from dataclasses import dataclass
from bus_model import resolve_bus
from memory_organization import MemoryArray
from sequential_logic import transition

REGISTERS = ("AR", "R0", "R1")
SOURCES = (*REGISTERS, "RAM", "EXT")
DESTINATIONS = (*REGISTERS, "RAM")


@dataclass(frozen=True)
class Cycle:
    before: tuple
    after: tuple
    address: int
    bus: str
    memory_write: tuple | None


class Databus:
    def __init__(self):
        self.reset()

    def reset(self):
        self.registers = dict.fromkeys(REGISTERS, 0)
        self.memory = MemoryArray(4, 4, 1, 1)
        self.history = []
        self.events = []

    def preview(self, sources, external=0):
        sources = tuple(sources)
        if (any(s not in SOURCES for s in sources)
                or len(set(sources)) != len(sources)
                or type(external) is not int or not 0 <= external < 16):
            raise ValueError("Invalid driver selection or external word")
        words = dict(self.registers, RAM=self.memory.read(self.registers["AR"]), EXT=external)
        return resolve_bus(4, [words[s] for s in sources])

    def tick(self, sources, destinations, external=0):
        sources = tuple(sources)
        destinations = tuple(destinations)
        if any(d not in DESTINATIONS for d in destinations) or len(set(destinations)) != len(destinations):
            raise ValueError("Invalid destination selection")
        bus = self.preview(sources, external)
        if destinations and bus.drivers != 1:
            raise ValueError("Clock transfer requires exactly one driver")
        before = tuple(self.registers.values())
        address = self.registers["AR"]
        after = dict(self.registers)
        for reg in REGISTERS:
            if reg in destinations:
                pins = {f"D{i}": (bus.word >> i) & 1 for i in range(4)}
                pins["EN"] = 1
                after[reg] = transition("REG4", self.registers[reg], pins)
        write = None
        if "RAM" in destinations:
            write = (address, self.memory.read(address), bus.word)
            self.memory.write(address, bus.word)
        self.registers.update(after)
        result = Cycle(before, tuple(after.values()), address, bus.bits, write)
        self.history.append(result)
        self.history = self.history[-64:]
        self.events.append((sources, destinations, external))
        self.events = self.events[-64:]
        return result
