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
