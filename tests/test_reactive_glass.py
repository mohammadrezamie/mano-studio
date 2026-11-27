import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QPointF, QEvent, Qt
from PySide6.QtGui import QEnterEvent, QMouseEvent
from PySide6.QtWidgets import QApplication
from ui.motion import MotionButton, set_glass_motion, set_reduced_motion
from ui.theme import apply_theme


@pytest.mark.parametrize("theme", ["light", "dark", "night"])
@pytest.mark.parametrize("language", ["en", "fa"])
def test_pointer_reflection_preserves_native_interaction(theme, language):
    app = QApplication.instance() or QApplication([])
    old_motion = bool(app.property("manoReducedMotion"))
    old_glass = app.property("manoGlassEnabled")
    old_palette, old_style = app.palette(), app.styleSheet()
    button = MotionButton("Translate" if language == "en" else "ترجمه")
    button.setLayoutDirection(Qt.LayoutDirection.RightToLeft if language == "fa" else Qt.LayoutDirection.LeftToRight)
    button.resize(160, 48)
    try:
        apply_theme(app, theme, True)
        set_reduced_motion(app, False)
        button.show()
        app.processEvents()
        p = QPointF(10, 5)
        button.enterEvent(QEnterEvent(p, p, p))
        button.animation.stop()
        button._frame(0.8)
        assert button.pointer == p
        geometry = button.geometry()
        image_a = button.grab().toImage()
        q = QPointF(145, 5)
        event = QMouseEvent(QEvent.Type.MouseMove, q, q,
                            Qt.MouseButton.NoButton, Qt.MouseButton.NoButton,
                            Qt.KeyboardModifier.NoModifier)
        button.mouseMoveEvent(event)
        assert button.pointer == q and button.geometry() == geometry
        assert button.grab().toImage() != image_a
        clicks = []
        button.clicked.connect(lambda: clicks.append(1))
        button.click()
        assert clicks == [1]
        set_glass_motion(app, False)
        assert button.pointer is None
        button._track_pointer(p)
        assert button.pointer is None
        set_glass_motion(app, True)
        button._track_pointer(p)
        assert button.pointer == p
        set_reduced_motion(app, True)
        assert button.pointer is None and button.level == 0
        button._track_pointer(q)
        assert button.pointer is None
        set_reduced_motion(app, False)
        button._track_pointer(q)
        button.setEnabled(False)
        assert button.pointer is None
        button.setEnabled(True)
        button._track_pointer(p)
        button.hide()
        assert button.pointer is None
    finally:
        button.close()
        set_reduced_motion(app, old_motion)
        app.setProperty("manoGlassEnabled", old_glass)
        app.setPalette(old_palette)
        app.setStyleSheet(old_style)
