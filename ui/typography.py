"""Platform-aware, offline UI typography. Code fonts remain separate."""

PREFERRED = {
    "en": ("Segoe UI", "Inter", "Noto Sans", "DejaVu Sans"),
    "fa": ("Vazirmatn", "Noto Sans Arabic", "Tahoma", "Segoe UI", "Noto Naskh Arabic", "DejaVu Sans"),
}
POINT_SIZE = {"en": 10.0, "fa": 11.0}


def choose_family(language, available, arabic, fallback):
    """Only choose an installed family; Persian also requires Arabic support."""
    language = "fa" if language == "fa" else "en"
    families = {name.casefold(): name for name in available}
    if language == "fa":
        supported = {name.casefold() for name in arabic}
        families = {key: name for key, name in families.items() if key in supported}
    for preferred in PREFERRED[language]:
        if preferred.casefold() in families:
            return families[preferred.casefold()]
    # Prefer a confirmed Arabic-capable font to an unknown default in Persian.
    if fallback.casefold() in families:
        return families[fallback.casefold()]
    if language == "fa" and families:
        return families[sorted(families)[0]]
    return fallback


def apply_ui_font(app, language):
    from PySide6.QtGui import QFontDatabase
    language = "fa" if language == "fa" else "en"
    font = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont)
    available = QFontDatabase.families()
    arabic = QFontDatabase.families(QFontDatabase.WritingSystem.Arabic) if language == "fa" else ()
    font.setFamily(choose_family(language, available, arabic, font.family()))
    font.setPointSizeF(POINT_SIZE[language])
    if app.font() != font:
        app.setFont(font)
    return font
