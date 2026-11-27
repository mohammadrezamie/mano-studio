"""Settings-only language selection and persistence; no network."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication, QDialog
from onboarding_state import LAST_PAGE, SetupState, save_state, read_state
from ui.workspace import Workspace
from ui.preferences import Preferences


@pytest.fixture
def window(tmp_path):
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "language.ini"), QSettings.Format.IniFormat)
    save_state(settings, SetupState("en", LAST_PAGE, True))
    w = Workspace(settings)
    yield w
    w.editor.document().setModified(False)
    w.close()


def test_settings_only_language_preserves_document(window):
    w = window
    w.editor.setPlainText("AC ← M[100]")
    w.run_translation()
    w.editor.document().setModified(True)
    assert w.languages.isHidden()
    p = Preferences(w)
    assert not p.apply_language.isEnabled()
    p.language_choice.setCurrentIndex(p.language_choice.findData("fa"))
    assert p.apply_language.isEnabled()
    p.apply_language.click()
    assert p.result() == QDialog.DialogCode.Accepted and p.reopen_for_language
    assert w.language == "fa" and w.settings.value("language") == "fa"
    assert read_state(w.settings).language == "fa"
    assert w.layoutDirection() == Qt.LayoutDirection.RightToLeft
    assert w.editor.layoutDirection() == Qt.LayoutDirection.LeftToRight
    assert w.editor.toPlainText() == "AC ← M[100]"
    assert w.output.toPlainText() == "LDA 100"
    assert w.editor.document().isModified()
    refreshed = Preferences(w)
    assert refreshed.windowTitle() == "تنظیمات"
    assert refreshed.language_choice.currentData() == "fa"
    refreshed.language_choice.setCurrentIndex(refreshed.language_choice.findData("en"))
    refreshed.apply_language.click()
    assert w.language == "en" and w.layoutDirection() == Qt.LayoutDirection.LeftToRight


def test_active_update_does_not_change_language(window):
    p = Preferences(window)
    p.language_choice.setCurrentIndex(p.language_choice.findData("fa"))
    p.thread = object()
    p.language_selection_changed()
    assert not p.apply_language.isEnabled()
    p.commit_language()
    assert window.language == "en" and not p.reopen_for_language
    p.thread = None
    p.close()
