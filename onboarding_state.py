"""Versioned, offline first-run state. No Qt dependency."""
from dataclasses import dataclass
import json

KEY = "onboarding/state"
VERSION = 1
LAST_PAGE = 5
LEGACY_KEYS = ("language", "geometry", "theme", "input_mode", "last_directory",
               "glass_enabled", "reduced_motion", "gate_symbol_style")


@dataclass(frozen=True)
class SetupState:
    language: str = "en"
    page: int = 0
    complete: bool = False

    def __post_init__(self):
        if self.language not in ("en", "fa"):
            raise ValueError("Invalid language")
        if type(self.page) is not int or not 0 <= self.page <= LAST_PAGE:
            raise ValueError("Invalid setup page")
        if type(self.complete) is not bool or self.complete and self.page != LAST_PAGE:
            raise ValueError("Invalid completion")

    def choose(self, language):
        return SetupState(language, self.page, self.complete)

    def advance(self):
        return SetupState(self.language, min(self.page + 1, LAST_PAGE), self.complete)

    def back(self):
        return SetupState(self.language, max(0, self.page - 1), False)

    def finish(self):
        if self.page != LAST_PAGE:
            raise ValueError("Finish only on last page")
        return SetupState(self.language, LAST_PAGE, True)

    def encode(self):
        return json.dumps(dict(version=VERSION, language=self.language,
                               page=self.page, complete=self.complete), sort_keys=True)

    @classmethod
    def decode(cls, raw):
        obj = json.loads(raw)
        if not isinstance(obj, dict) or type(obj.get("version")) is not int or obj["version"] != VERSION:
            raise ValueError("Unsupported onboarding schema")
        return cls(obj["language"], obj["page"], obj["complete"])


def read_state(settings):
    """Resume explicitly started setup; never force legacy profiles into setup."""
    if settings.contains(KEY):
        try:
            return SetupState.decode(settings.value(KEY))
        except (ValueError, TypeError, KeyError):
            # Preserve the established language; do not overwrite corrupt/future state.
            pass
    language = settings.value("language", "en")
    if language not in ("en", "fa"):
        language = "en"
    existing = any(settings.contains(k) for k in LEGACY_KEYS)
    return SetupState(language, LAST_PAGE if existing else 0, existing)


def save_state(settings, state):
    """Persist navigation; commit selected language only on completion."""
    settings.setValue(KEY, state.encode())
    if state.complete:
        settings.setValue("language", state.language)
    settings.sync()


def update_language(settings, language):
    """Keep completed onboarding and the current locale consistent.

    Legacy profiles keep their existing settings; unknown schema is not overwritten.
    """
    if language not in ("en", "fa"):
        raise ValueError("Invalid language")
    settings.setValue("language", language)
    if settings.contains(KEY):
        try:
            state = SetupState.decode(settings.value(KEY))
        except (ValueError, TypeError, KeyError):
            pass
        else:
            if state.complete:
                settings.setValue(KEY, state.choose(language).encode())
    settings.sync()
