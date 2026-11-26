"""Paint a portable layered glass backdrop using Qt."""
from PySide6.QtCore import QPointF, QVariantAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QRadialGradient
from PySide6.QtWidgets import QWidget
from ui.theme import PALETTES
from ui.motion import motion_allowed

GLOWS = {
    "dark": ("#426af2", "#a044ce", "#16b9c6"),
    "light": ("#8cb8ff", "#d1a7fa", "#91e0e9"),
    "night": ("#775052", "#524063", "#815d40"),
}


def paint_backdrop(painter, rect, theme, enabled=True, pulse=0.0):
    theme = theme if theme in PALETTES else "dark"
    painter.fillRect(rect, QColor(PALETTES[theme][0]))
    if not enabled:
        return
    w, h = rect.width(), rect.height()
    for (x, y, radius), tint in zip(((0.12, 0.05, 0.70), (0.94, 0.35, 0.65), (0.30, 1.0, 0.55)), GLOWS[theme]):
        glow = QRadialGradient(QPointF(rect.left() + x*w, rect.top() + y*h), max(1.0, radius*max(w,h)))
        color = QColor(tint)
        color.setAlpha(int((68 if theme!="light" else 78) + 18*max(0.0,min(1.0,pulse))))
        glow.setColorAt(0.0, color)
        color.setAlpha(0)
        glow.setColorAt(1.0, color)
        painter.fillRect(rect, glow)


class GlassRoot(QWidget):
    def __init__(self, theme, enabled=True):
        super().__init__()
        self.theme = theme
        self.enabled = enabled
        self.setObjectName("glassRoot")
        self.setProperty("manoMotionSurface", True)
        self.pulse = 0.0
        self.animation = QVariantAnimation(self)
        self.animation.setDuration(420)
        self.animation.setStartValue(0.0)
        self.animation.setKeyValueAt(0.35, 1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.animation.valueChanged.connect(self._frame)
        self.animation.finished.connect(self.snap)

    def _frame(self, value):
        self.pulse = float(value)
        self.update()

    def snap(self):
        self.animation.stop()
        self.pulse = 0.0
        self.update()

    def feedback(self):
        self.snap()
        if self.enabled and self.isVisible() and motion_allowed():
            self.animation.start()

    def hideEvent(self, event):
        self.snap()
        super().hideEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        paint_backdrop(painter, self.rect(), self.theme, self.enabled, self.pulse)
        painter.end()
