from types import SimpleNamespace
import pytest
from cpu_guard import CpuGuard, state_key


class FakeCPU:
    def __init__(self):
        self.memory = [0] * 4096
        self.pc = 0
        self.pending_event = None

    def registers(self):
        return {"PC": self.pc, "HALTED": False}


def fixture():
    cpu = FakeCPU()
    history = SimpleNamespace(cpu=cpu, steps=0, breakpoints=set())
    return cpu, history, CpuGuard("HLT", cpu, history)


@pytest.mark.parametrize("field", ["memory", "register", "steps", "breakpoint", "pending"])
def test_runtime_changes(field):
    cpu, history, guard = fixture()
    assert not guard.is_dirty("HLT", cpu, history)
    if field == "memory":
        cpu.memory[4095] = 7
    elif field == "register":
        cpu.pc = 1
    elif field == "steps":
        history.steps = 1
    elif field == "breakpoint":
        history.breakpoints.add(3)
    else:
        cpu.pending_event = SimpleNamespace(microevents=(object(),))
    assert guard.is_dirty("HLT", cpu, history)
    guard.mark_saved("HLT", cpu, history)
    assert not guard.is_dirty("HLT", cpu, history)


def test_source_and_unassembled_draft():
    cpu, history, guard = fixture()
    assert guard.is_dirty("CLA", cpu, history)
    assert guard.is_dirty("HLT", None, None)
    guard.mark_saved("bad source", None, None)
    assert not guard.is_dirty("bad source", None, None)
    assert guard.is_dirty("other draft", None, None)


def test_undo_to_saved_boundary():
    cpu, history, guard = fixture()
    cpu.memory[1] = 9
    assert guard.is_dirty("HLT", cpu, history)
    cpu.memory[1] = 0
    assert not guard.is_dirty("HLT", cpu, history)


def test_mismatched_history_rejected():
    cpu, history, _ = fixture()
    with pytest.raises(ValueError):
        state_key("HLT", FakeCPU(), history)
