"""Versioned first-run and migration contracts without Qt."""
import pytest
from onboarding_state import KEY, LAST_PAGE, SetupState, read_state, save_state

class Settings(dict):
    def contains(self, key): return key in self
    def value(self, key, default=None): return self.get(key, default)
    def setValue(self, key, value): self[key] = value
    def sync(self): pass

@pytest.mark.parametrize("language", ["en", "fa"])
def test_resume_and_finish(language):
    store = Settings()
    state = read_state(store)
    assert state == SetupState()
    state = state.choose(language).advance().advance()
    save_state(store, state)
    assert "language" not in store
    assert read_state(store) == state
    assert state.back().page == 1
    while state.page < LAST_PAGE:
        state = state.advance()
    state = state.finish()
    save_state(store, state)
    assert read_state(store).complete
    assert store["language"] == language

@pytest.mark.parametrize("key,value", [("language","fa"),("geometry",b"x"),("theme","night")])
def test_legacy_profile_not_forced(key,value):
    store = Settings({key:value})
    assert read_state(store).complete
    assert KEY not in store

@pytest.mark.parametrize("raw", ["bad", "[]", '{"version":2}', '{"version":1,"language":"x","page":0,"complete":false}'])
def test_malformed_state_preserves_legacy_language(raw):
    store = Settings({KEY:raw,"language":"fa"})
    assert read_state(store) == SetupState("fa",LAST_PAGE,True)
    assert store[KEY] == raw

def test_invalid_completion():
    with pytest.raises(ValueError):
        SetupState().finish()
    with pytest.raises(ValueError):
        SetupState(page=True)
    assert SetupState().back().page == 0


def test_language_updates_completed_state():
    from onboarding_state import update_language
    store = Settings()
    save_state(store, SetupState("en", LAST_PAGE, True))
    update_language(store, "fa")
    assert store["language"] == "fa"
    assert read_state(store) == SetupState("fa", LAST_PAGE, True)


def test_language_preserves_unknown_schema():
    from onboarding_state import update_language
    store = Settings({KEY:'{"version":99}', "language":"en"})
    update_language(store, "fa")
    assert store[KEY] == '{"version":99}'
    assert store["language"] == "fa"


@pytest.mark.parametrize("raw", ["broken", '{"version":99,"language":"fa"}', '[]', None])
def test_existing_unreadable_state_without_legacy_settings_is_not_fresh(raw):
    store = Settings({KEY: raw})
    assert read_state(store) == SetupState("en", LAST_PAGE, True)
    assert store == {KEY: raw}
    from onboarding_state import update_language
    update_language(store, "fa")
    assert store[KEY] == raw
    assert read_state(store) == SetupState("fa", LAST_PAGE, True)
