"""Replayable finite-state lab checkpoint, without trusting derived outputs."""
from dataclasses import dataclass
import json
from logic_exercise import StateExercise, dumps
from native_exercise import restore as restore_design
from state_synthesis import design_state_machine
import mano_file


@dataclass(frozen=True)
class Session:
    design: StateExercise
    base: int
    inputs: tuple
    selected: int
    state: int
    trace: tuple


def snapshot(design, base, inputs, selected):
    if not isinstance(design, StateExercise):
        raise ValueError("Expected state design")
    if type(base) is not int or not 0 <= base < 2**design.bits:
        raise ValueError("Invalid checkpoint state")
    if type(selected) is not int or selected not in (0, 1):
        raise ValueError("Invalid staged input")
    if not isinstance(inputs, (list, tuple)) or len(inputs) > 64 or any(type(x) is not int or x not in (0, 1) for x in inputs):
        raise ValueError("Invalid input history")
    model = design_state_machine(design.bits, design.table, design.mode, design.flipflop)
    state, trace = base, []
    for x in inputs:
        nxt, y = model.step(state, x)
        trace.append((state, x, nxt, y))
        state = nxt
    return Session(design, base, tuple(inputs), selected, state, tuple(trace))


def payload(session):
    obj = json.loads(dumps(session.design))
    for key in ("format", "version", "kind"):
        del obj[key]
    return {"design": obj, "base": session.base, "inputs": list(session.inputs), "selected": session.selected}


def restore(obj):
    if not isinstance(obj, dict) or set(obj) != {"design", "base", "inputs", "selected"}:
        raise ValueError("Invalid state session")
    design = restore_design("state-design", obj["design"])
    return snapshot(design, obj["base"], obj["inputs"], obj["selected"])


def save(path, session):
    obj = payload(session)
    if restore(obj) != session:
        raise ValueError("Inconsistent derived state or trace")
    mano_file.save(path, "state-run", obj)


def load(path):
    kind, obj = mano_file.load(path)
    if kind != "state-run":
        raise ValueError("Expected state session")
    return restore(obj)
