import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QAbstractAnimation, QSettings, QTimer
from PySide6.QtWidgets import QApplication, QDialog, QLabel
from ui.glass import GlassRoot
from ui.motion import set_reduced_motion
from ui.credits import ACADEMIC_ACKNOWLEDGMENT, COURSE, INSTITUTION
from ui.theme import stylesheet
from ui.workspace import Workspace


def test_glass_pulse_respects_preferences():
    app = QApplication.instance() or QApplication([])
    previous = bool(app.property("manoReducedMotion"))
    root = GlassRoot("dark")
    root.show()
    try:
        set_reduced_motion(app, False)
        root.feedback()
        assert root.animation.state() == QAbstractAnimation.State.Running
        root.hide()
        assert root.animation.state() == QAbstractAnimation.State.Stopped
        assert root.pulse == 0
        root.show()
        set_reduced_motion(app, True)
        root.feedback()
        assert root.animation.state() == QAbstractAnimation.State.Stopped
        set_reduced_motion(app, False)
        root.enabled = False
        root.feedback()
        assert root.animation.state() == QAbstractAnimation.State.Stopped
    finally:
        root.close()
        set_reduced_motion(app, previous)


def test_vivid_gradient_is_optional():
    assert "stop:1 #d2b1ff" in stylesheet("dark", True)
    assert "stop:1 #d2b1ff" not in stylesheet("dark", False)


@pytest.mark.parametrize("language", ["fa", "en"])
def test_about_sections(language, tmp_path):
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    settings.setValue("language", language)
    window = Workspace(settings)
    captured = []
    def inspect():
        dialog = window.findChild(QDialog)
        if dialog is not None:
            captured.extend(label.text() for label in dialog.findChildren(QLabel))
            dialog.reject()
    QTimer.singleShot(0, inspect)
    try:
        window.about()
        fa = language == "fa"
        assert ACADEMIC_ACKNOWLEDGMENT[fa] in captured
        assert COURSE[fa] in captured
        assert INSTITUTION[fa] in captured
    finally:
        window.editor.document().setModified(False)
        window.close()
