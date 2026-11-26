"""Ideal storage elements: atomic input events, no electrical timing prediction.

SR outputs represent settled cross-coupled NOR/NAND gates. Releasing both
asserted inputs together is unknown until a deterministic set/reset event.
Asynchronous D controls are an abstract active-low preset/clear model.
"""
from dataclasses import dataclass

PINS = {
    "SR_NOR": ("S", "R"),
    "SR_NAND": ("Sbar", "Rbar"),
    "D_LATCH": ("D", "EN"),
    "D_ASYNC": ("D", "CLK", "PREbar", "CLRbar"),
}


@dataclass(frozen=True)
class Storage:
    q: int | None = 0
    qbar: int | None = 1

    @property
    def known(self):
        return (self.q, self.qbar) in ((0, 1), (1, 0))


def _bit(q):
    return Storage(q, 1-q)


def _hold(state):
    return state if state.known else Storage(None, None)


def step(kind, state, pins, previous_clock=0):
    """Apply one complete input vector; return a new immutable output state."""
    if kind not in PINS or set(pins) != set(PINS[kind]):
        raise ValueError("Unknown component or incorrect pins")
    if (not isinstance(state, Storage)
            or (state.q, state.qbar) not in ((0,1),(1,0),(0,0),(1,1),(None,None))
            or any(type(v) is not int or v not in (0,1)
                   for v in (*pins.values(), previous_clock))):
        raise ValueError("Invalid storage state or nonbinary input")
    if kind in ("SR_NOR", "SR_NAND"):
        active_low = kind == "SR_NAND"
        s,r = (int(not v) if active_low else v for v in (pins[name] for name in PINS[kind]))
        if s and r:
            return Storage(1,1) if active_low else Storage(0,0)
        if s:
            return _bit(1)
        if r:
            return _bit(0)
        return _hold(state)
    if kind == "D_LATCH":
        return _bit(pins["D"]) if pins["EN"] else _hold(state)
    preset,clear = not pins["PREbar"], not pins["CLRbar"]
    if preset and clear:
        return Storage(None,None)
    if preset:
        return _bit(1)
    if clear:
        return _bit(0)
    if previous_clock == 0 and pins["CLK"] == 1:
        return _bit(pins["D"])
    return _hold(state)
