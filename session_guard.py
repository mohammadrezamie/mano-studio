"""Track persisted FSM inputs without recomputing a derived simulation."""
from dataclasses import dataclass


@dataclass(frozen=True)
class StateKey:
    design: object
    base: int
    inputs: tuple
    selected: int

    @property
    def design_only(self):
        return self.base == 0 and not self.inputs and self.selected == 0


class SessionGuard:
    def __init__(self, key):
        self.saved = key

    def is_dirty(self, key):
        return key != self.saved

    def mark_saved(self, key, *, native):
        # A legacy design export cannot claim that runtime history was saved.
        self.saved = key if native else StateKey(key.design, 0, (), 0)
