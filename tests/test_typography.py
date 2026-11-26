import pytest
from ui.typography import choose_family, POINT_SIZE


@pytest.mark.parametrize("language,available,arabic,fallback,expected", [
    ("en", ["Tahoma", "Segoe UI"], [], "Tahoma", "Segoe UI"),
    ("en", ["Noto Sans", "DejaVu Sans"], [], "Default", "Noto Sans"),
    ("fa", ["Noto Sans Arabic", "Tahoma"], ["Tahoma", "Noto Sans Arabic"], "Default", "Noto Sans Arabic"),
    ("fa", ["Vazirmatn", "Tahoma"], ["Tahoma"], "Default", "Tahoma"),
    ("fa", ["TAHOMA"], ["tahoma"], "Default", "TAHOMA"),
    ("fa", ["Segoe UI", "Other Arabic"], ["Other Arabic"], "Segoe UI", "Other Arabic"),
    ("fa", ["B Arabic", "A Arabic"], ["B Arabic", "A Arabic"], "Unknown", "A Arabic"),
    ("fa", ["B Arabic", "A Arabic"], ["B Arabic", "A Arabic"], "B Arabic", "B Arabic"),
    ("fa", ["Latin only"], [], "Default", "Default"),
    ("en", ["Other"], [], "Default", "Default"),
    ("unknown", ["Segoe UI"], [], "Default", "Segoe UI"),
])
def test_font_selection(language, available, arabic, fallback, expected):
    assert choose_family(language, available, arabic, fallback) == expected


def test_readability_defaults():
    assert POINT_SIZE["fa"] > POINT_SIZE["en"] >= 10
