import pytest
from session_guard import StateKey, SessionGuard


BASE = StateKey(('Moore', 'D', 1), 0, (), 0)


@pytest.mark.parametrize('changed', [StateKey(('Mealy', 'D', 1), 0, (), 0),
    StateKey(BASE.design, 1, (), 0), StateKey(BASE.design, 0, (1,), 0),
    StateKey(BASE.design, 0, (), 1)])
def test_each_persisted_field_can_be_dirty(changed):
    guard = SessionGuard(BASE)
    assert not guard.is_dirty(BASE)
    assert guard.is_dirty(changed)
    guard.mark_saved(changed, native=True)
    assert not guard.is_dirty(changed)


def test_legacy_export_preserves_unsaved_runtime():
    key = StateKey(('Mealy', 'JK', 2), 1, (0, 1), 1)
    guard = SessionGuard(BASE)
    guard.mark_saved(key, native=False)
    assert guard.is_dirty(key)
    assert not guard.is_dirty(StateKey(key.design, 0, (), 0))


def test_reset_to_saved_state_is_clean():
    guard = SessionGuard(BASE)
    assert guard.is_dirty(StateKey(BASE.design, 0, (1, 0), 0))
    assert not guard.is_dirty(BASE)
