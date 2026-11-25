"""Ideal serialized MSI cache coherence, not a timing or electrical model.

Four processors, sixteen 16-bit memory words, four direct-mapped single-word
cache lines per processor. Main memory may be stale only while a line is M.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Line:
    address: int | None = None
    state: str = "I"
    value: int = 0


@dataclass(frozen=True)
class Writeback:
    core: int
    address: int
    value: int
    reason: str


@dataclass(frozen=True)
class Access:
    core: int
    address: int
    operation: str
    hit: bool
    bus: str
    value: int
    invalidated: tuple[int, ...]
    writebacks: tuple[Writeback, ...]
    before: tuple[tuple[Line, ...], ...]
    after: tuple[tuple[Line, ...], ...]
    memory: tuple[int, ...]


class MSICache:
    """Atomic requests on an ideal snooping bus; no concurrent access or latency."""
    CORES = 4
    WORDS = 16
    SETS = 4

    def __init__(self):
        self._memory = [0] * self.WORDS
        self._lines = [[Line() for _ in range(self.SETS)] for _ in range(self.CORES)]
        self.accesses = 0

    @property
    def memory(self):
        return tuple(self._memory)

    @property
    def lines(self):
        return tuple(tuple(lines) for lines in self._lines)

    def read(self, core, address):
        return self._access(core, address, None)

    def write(self, core, address, value):
        if type(value) is not int or not 0 <= value <= 0xFFFF:
            raise ValueError("Invalid 16-bit word")
        return self._access(core, address, value)

    def _access(self, core, address, value):
        if type(core) is not int or not 0 <= core < self.CORES:
            raise ValueError("Invalid processor")
        if type(address) is not int or not 0 <= address < self.WORDS:
            raise ValueError("Invalid word address")
        before = self.lines
        index = address % self.SETS
        local = self._lines[core][index]
        hit = local.state != "I" and local.address == address
        writebacks, invalidated = [], []

        def writeback(owner, line, reason):
            self._memory[line.address] = line.value
            writebacks.append(Writeback(owner, line.address, line.value, reason))

        if not hit and local.state == "M":
            writeback(core, local, "eviction")
        bus = "none"
        if value is None and hit:
            result = local.value
        elif value is not None and hit and local.state == "M":
            result = value
            self._lines[core][index] = Line(address, "M", result)
        else:
            bus = "BusRd" if value is None else ("BusUpgr" if hit else "BusRdX")
            for peer in range(self.CORES):
                if peer == core:
                    continue
                line = self._lines[peer][index]
                if line.state == "I" or line.address != address:
                    continue
                if line.state == "M":
                    writeback(peer, line, "snoop")
                if value is None:
                    self._lines[peer][index] = Line(address, "S", line.value)
                else:
                    self._lines[peer][index] = Line()
                    invalidated.append(peer)
            result = self._memory[address] if value is None else value
            self._lines[core][index] = Line(address, "S" if value is None else "M", result)
        self.accesses += 1
        return Access(core, address, "read" if value is None else "write", hit, bus, result,
                      tuple(invalidated), tuple(writebacks), before, self.lines, self.memory)
