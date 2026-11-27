"""Real first-run wizard language, navigation and persistence."""
import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import Qt, QSettings
from PySide6.QtWidgets import QApplication, QDialog
from onboarding_state import read_state, LAST_PAGE
from ui.onboarding import Onboarding

@pytest.mark.parametrize("language", ["en","fa"])
def test_wizard(tmp_path, language):
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path/"prefs.ini"), QSettings.Format.IniFormat)
    dialog = Onboarding(settings)
    dialog.options[language].setChecked(True)
    dialog.next.click()
    assert dialog.state.page == 1
    assert dialog.layoutDirection() == (Qt.LayoutDirection.RightToLeft if language=="fa" else Qt.LayoutDirection.LeftToRight)
    assert dialog.credits.text()
    dialog.previous.click()
    assert dialog.state.page == 0
    dialog.next.click()
    dialog.reject()
    assert read_state(settings).page == 1
    resumed = Onboarding(settings)
    assert resumed.state.language == language
    while resumed.state.page < LAST_PAGE:
        resumed.next.click()
    resumed.next.click()
    assert resumed.result() == QDialog.DialogCode.Accepted
    assert settings.value("language") == language
    assert read_state(settings).complete
