import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QWidget
from shiboken6 import isValid
from capture_lifecycle import dispose_capture_widget


def test_dispose_capture_tree():
    app = QApplication.instance() or QApplication([])
    root = QWidget()
    child = QWidget(root)
    timer = QTimer(child)
    timer.start(1000)
    unrelated = QWidget()
    try:
        root.show()
        assert timer.isActive()
        dispose_capture_widget(root)
        assert not any(isValid(obj) for obj in (root, child, timer))
        assert isValid(unrelated)
        dispose_capture_widget(root)  # already destroyed
    finally:
        dispose_capture_widget(unrelated)
        if isValid(root):
            dispose_capture_widget(root)


def test_refused_close_is_not_silently_destroyed():
    app = QApplication.instance() or QApplication([])
    class Refuses(QWidget):
        def closeEvent(self, event):
            event.ignore()
    widget = Refuses()
    try:
        with pytest.raises(RuntimeError, match="refused"):
            dispose_capture_widget(widget)
        assert isValid(widget)
    finally:
        from PySide6.QtCore import QCoreApplication, QEvent
        widget.deleteLater()
        QCoreApplication.sendPostedEvents(widget, QEvent.Type.DeferredDelete)


def test_disposable_lab_does_not_invoke_user_close_handler():
    from capture_lifecycle import discard_capture_lab
    app = QApplication.instance() or QApplication([])
    class Refuses(QWidget):
        close_calls = 0
        def closeEvent(self, event):
            type(self).close_calls += 1
            event.ignore()
    root = Refuses()
    child = QWidget(root)
    timer = QTimer(child)
    timer.start(1000)
    root.show()
    discard_capture_lab(root)
    assert Refuses.close_calls == 0
    assert not any(isValid(obj) for obj in (root, child, timer))


@pytest.mark.parametrize("language", ["en", "fa"])
def test_discard_dirty_capture_cpu_without_prompt(tmp_path, language, monkeypatch):
    from capture_lifecycle import discard_capture_lab
    from PySide6.QtCore import QSettings
    from PySide6.QtWidgets import QMessageBox
    from ui.workspace import Workspace
    from ui.program_lab import ProgramLab
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "capture.ini"), QSettings.Format.IniFormat)
    settings.setValue("language", language)
    settings.setValue("reduced_motion", True)
    root = Workspace(settings)
    lab = ProgramLab(root)
    def unexpected(*args, **kwargs):
        pytest.fail("Unexpected save prompt in disposable capture")
    monkeypatch.setattr(QMessageBox, "question", unexpected)
    try:
        lab.show()
        lab.step()
        assert lab.is_dirty()
        timer = lab.timer
        discard_capture_lab(lab)
        assert not isValid(lab) and not isValid(timer)
        assert isValid(root)
    finally:
        discard_capture_lab(lab)
        root.editor.document().setModified(False)
        dispose_capture_widget(root)
