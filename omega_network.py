"""Ideal blocking Omega network: 2x2 switches, perfect shuffle, fixed priority.

A request reserves its entire path for one atomic transfer round. This is
not packet timing, buffering, or a nonblocking crossbar.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Hop:
    stage: int
    input_line: int
    output_line: int

    @property
    def switch(self):
        return self.input_line // 2

    @property
    def crossed(self):
        return self.input_line % 2 != self.output_line % 2


@dataclass(frozen=True)
class Transfer:
    source: int
    destination: int
    hops: tuple[Hop, ...]
    blocked_stage: int | None = None
    blocked_by: int | None = None

    @property
    def granted(self):
        return self.blocked_stage is None


def _validate_size(size):
    if type(size) is not int or size not in (2, 4, 8, 16, 32, 64):
        raise ValueError("Size must be a power of two from 2 to 64")


def _port(size, port):
    if type(port) is not int or not 0 <= port < size:
        raise ValueError("Port out of range")


def route(size, source, destination):
    """Unique self-routing path, destination bits MSB first."""
    _validate_size(size)
    _port(size, source)
    _port(size, destination)
    stages = size.bit_length() - 1
    line = source
    hops = []
    for stage in range(stages):
        bit = (destination >> (stages - 1 - stage)) & 1
        output = (line & ~1) | bit
        hops.append(Hop(stage, line, output))
        # Rotate the line number left between adjacent switch stages.
        line = ((output << 1) & (size - 1)) | (output >> (stages - 1))
    return tuple(hops)


def transfer_round(size, requests):
    """Grant full paths in ascending source order, with no partial reservations."""
    _validate_size(size)
    paths = {}
    for source, destination in requests:
        hops = route(size, source, destination)
        if source in paths:
            raise ValueError("Duplicate source in one round")
        paths[source] = (destination, hops)
    occupied = {}
    results = []
    for source, (destination, hops) in sorted(paths.items()):
        conflict = next((h for h in hops if (h.stage, h.output_line) in occupied), None)
        if conflict is not None:
            results.append(Transfer(source, destination, hops, conflict.stage,
                                    occupied[conflict.stage, conflict.output_line]))
            continue
        for hop in hops:
            occupied[hop.stage, hop.output_line] = source
        results.append(Transfer(source, destination, hops))
    return tuple(results)
