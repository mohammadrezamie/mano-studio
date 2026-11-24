"""Functional Mano common-bus/control observation; not a second CPU."""
from dataclasses import dataclass

BUS_SOURCES = (None, "AR", "PC", "DR", "AC", "IR", "TR", "M")


@dataclass(frozen=True)
class ControlTrace:
    decoder: int
    timing: int
    interrupt_cycle: bool
    select: int
    source: str | None
    value: int | None
    signals: tuple


def capture_control(before, timing, phase, source, signals, reads):
    """Capture explicit controls from the executing edge.

    D is the raw decode of pre-edge IR, even during fetch/interrupt when
    instruction-specific control is gated. Selector 000 is unused here;
    no electrical bus voltage is claimed. Narrow register sources zero extend.
    """
    select = BUS_SOURCES.index(source)
    if source == "M":
        if len(reads) != 1:
            raise ValueError("Memory bus source requires one recorded read")
        value = reads[0][1]
    else:
        value = before[source] if source is not None else None
    return ControlTrace((before["IR"] >> 12) & 7, timing, phase=="interrupt",
                        select, source, value, tuple(signals))
