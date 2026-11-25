"""Ideal D flip-flop setup/hold constraint checker, not analog simulation.

Times are integer ticks. Data is stable before tick zero. Events must be
strictly increasing; a transition exactly at the edge is ambiguous even
with zero setup/hold. Endpoints of positive windows satisfy the constraint.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class TimingResult:
    setup_violations: tuple[int, ...]
    hold_violations: tuple[int, ...]
    coincident: bool
    sampled: int | None

    @property
    def valid(self):
        return not (self.setup_violations or self.hold_violations or self.coincident)


def check(initial, events, edge, setup, hold):
    """Evaluate a complete, supplied waveform; violations yield no predicted Q."""
    if type(initial) is not int or initial not in (0, 1):
        raise ValueError("Expected binary initial data")
    if any(type(v) is not int or v < 0 for v in (edge, setup, hold)):
        raise ValueError("Expected nonnegative integer times")
    events = tuple(events)
    last = -1
    value = initial
    transitions = []
    sample = initial
    for time, bit in events:
        if type(time) is not int or time < 0 or time <= last:
            raise ValueError("Events must have strictly increasing nonnegative ticks")
        if type(bit) is not int or bit not in (0, 1):
            raise ValueError("Expected binary data")
        last = time
        if bit != value:
            transitions.append(time)
        value = bit
        if time < edge:
            sample = bit
    before = tuple(t for t in transitions if edge - setup < t < edge)
    after = tuple(t for t in transitions if edge < t < edge + hold)
    coincident = edge in transitions
    return TimingResult(before, after, coincident,
                        None if before or after or coincident else sample)
