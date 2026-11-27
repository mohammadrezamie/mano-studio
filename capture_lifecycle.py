"""Developer capture cleanup; never used by the desktop application."""
from PySide6.QtCore import QCoreApplication, QEvent
from shiboken6 import isValid


def dispose_capture_widget(widget):
    """Close a disposable capture widget and synchronously finish its deletion."""
    if not isValid(widget):
        return
    if not widget.close():
        raise RuntimeError("Capture widget refused normal close")
    widget.deleteLater()
    # Target only this widget's deferred delete event; QObject ownership
    # handles child widgets and timers. No unrelated posted events are flushed.
    QCoreApplication.sendPostedEvents(widget, QEvent.Type.DeferredDelete)
    if isValid(widget):
        raise RuntimeError("Capture widget survived deferred deletion")
