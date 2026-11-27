"""Validate the actual embedded capture bytes and wizard fallback."""
import hashlib
import json
from pathlib import Path
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from ui.onboarding import Onboarding, PREVIEWS, preview_path

def test_embedded_capture_integrity():
    root = Path(__file__).resolve().parents[1] / "docs" / "assets" / "onboarding"
    manifest = json.loads((root / "provenance.json").read_text(encoding="utf-8"))
    expected = {name for names in PREVIEWS.values() for name in names}
    assert {row["file"] for row in manifest} == expected
    for row in manifest:
        assert hashlib.sha256((root / row["file"]).read_bytes()).hexdigest() == row["sha256"]

@pytest.mark.parametrize("language", ["en", "fa"])
def test_preview_pages(tmp_path, language):
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "visual.ini"), QSettings.Format.IniFormat)
    wizard = Onboarding(settings)
    wizard.options[language].setChecked(True)
    wizard.show()
    app.processEvents()
    assert wizard.preview.isHidden()
    for _ in range(2): wizard.next.click()
    for page in range(2, 6):
        assert wizard.state.page == page
        assert not wizard.preview_pixmap.isNull()
        assert not wizard.preview.isHidden()
        assert preview_path(page, language).is_file()
        assert wizard.preview.pixmap().height() <= wizard.preview.height()
        if page < 5: wizard.next.click()
    wizard.reject()

def test_missing_preview_falls_back(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "missing.ini"), QSettings.Format.IniFormat)
    monkeypatch.setattr("ui.onboarding.preview_path", lambda *_: tmp_path / "missing.png")
    wizard = Onboarding(settings)
    wizard.next.click()
    wizard.next.click()
    assert wizard.preview.isHidden()
    assert wizard.description.text()
    wizard.reject()
