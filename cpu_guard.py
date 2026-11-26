"""Compare a CPU workspace with its last saved or deliberately loaded state."""


def state_key(source, cpu, history):
    if cpu is None:
        return (source, None)
    if history is None or history.cpu is not cpu:
        raise ValueError("CPU history does not match the live CPU")
    pending = cpu.pending_event
    return (source, tuple(sorted(cpu.registers().items())), tuple(cpu.memory),
            history.steps, tuple(sorted(history.breakpoints)),
            len(pending.microevents) if pending else 0)


class CpuGuard:
    def __init__(self, source, cpu, history):
        self.mark_saved(source, cpu, history)

    def mark_saved(self, source, cpu, history):
        self.saved = state_key(source, cpu, history)

    def is_dirty(self, source, cpu, history):
        return self.saved != state_key(source, cpu, history)
