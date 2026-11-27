"""Exercise the real direction-aware keypad without changing the academic core."""
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication
from instruction_catalog import TEMPLATES
from ui.workspace import Workspace


@pytest.fixture
def window(tmp_path):
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "pad.ini"), QSettings.Format.IniFormat)
    w = Workspace(settings)
    yield w
    w.editor.document().setModified(False)
    w.close()


@pytest.mark.parametrize("language", ["en", "fa"])
def test_bidirectional_pad(window, language):
    w = window
    w.languages.setCurrentIndex(w.languages.findData(language))
    w.tabs.setCurrentIndex(1)
    assert w.pad_stack.currentIndex() == 0
    for token in ("AC", "←", "M[", "1", "0", "0", "]"):
        w.pad_buttons[("forward", token)].click()
    w.run_translation()
    assert w.output.toPlainText() == "LDA 100"
    w.editor.clear()
    w.set_direction("reverse")
    assert w.tabs.currentIndex() == 1
    assert w.tabs.isTabEnabled(1)
    assert w.pad_stack.currentIndex() == 1
    assert w.pad_stack.parentWidget().layoutDirection() == Qt.LayoutDirection.LeftToRight
    for token in ("LDA ", "A", "B", "C"):
        w.pad_buttons[("reverse", token)].click()
    w.insert(" ")
    w.pad_buttons[("reverse", "I")].click()
    assert w.editor.toPlainText() == "LDA ABC I"
    w.run_translation()
    assert w.result.ok and w.output.toPlainText() == "AC ← M[M[ABC]]"
    w.editor.clear()
    w.set_direction("forward")
    assert w.pad_stack.currentIndex() == 0
    assert w.tabs.isTabEnabled(1)


def test_all_named_instructions_present(window):
    for name, template in TEMPLATES.items():
        token = name + (" " if "{a}" in template else "")
        assert ("reverse", token) in window.pad_buttons
    for digit in "0123456789ABCDEF":
        assert ("reverse", digit) in window.pad_buttons
        assert ("forward", digit) in window.pad_buttons
