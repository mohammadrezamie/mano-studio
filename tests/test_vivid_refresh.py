import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QAbstractAnimation, QSettings
from PySide6.QtWidgets import QApplication, QLabel
from ui.glass import GlassRoot
from ui.motion import MotionButton, set_reduced_motion
from ui.brand import BrandMark
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
        set_reduced_motion(app, True)
        assert root.animation.state() == QAbstractAnimation.State.Stopped
        assert root.pulse == 0
        set_reduced_motion(app, False)
        root.feedback()
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
    dialog = window.about_dialog()
    try:
        dialog.show()
        app.processEvents()
        captured = [label.text() for label in dialog.findChildren(QLabel)]
        fa = language == "fa"
        assert ACADEMIC_ACKNOWLEDGMENT[fa] in captured
        assert COURSE[fa] in captured
        assert INSTITUTION[fa] in captured
        assert not dialog.grab().isNull()
    finally:
        dialog.close()
        window.editor.document().setModified(False)
        window.close()


def test_button_and_brand_cancel_inflight_motion():
    app = QApplication.instance() or QApplication([])
    previous = bool(app.property("manoReducedMotion"))
    button = MotionButton("Translate")
    mark = BrandMark()
    button.show()
    mark.show()
    try:
        set_reduced_motion(app, False)
        button._retarget(1.0)
        mark.feedback(True)
        assert button.animation.state() == QAbstractAnimation.State.Running
        assert mark.animation.state() == QAbstractAnimation.State.Running
        set_reduced_motion(app, True)
        assert button.level == 0 and mark.progress is None
        assert button.animation.state() == QAbstractAnimation.State.Stopped
        assert mark.animation.state() == QAbstractAnimation.State.Stopped
        set_reduced_motion(app, False)
        button._retarget(1.0)
        button.setEnabled(False)
        assert button.level == 0
        assert button.animation.state() == QAbstractAnimation.State.Stopped
        button.setEnabled(True)
        button._retarget(1.0)
        button.hide()
        assert button.level == 0
        assert button.animation.state() == QAbstractAnimation.State.Stopped
    finally:
        button.close()
        mark.close()
        set_reduced_motion(app, previous)
