"""Paint a portable layered glass backdrop using Qt."""
from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPainter, QRadialGradient
from PySide6.QtWidgets import QWidget
from ui.theme import PALETTES

GLOWS = {
    "dark": ("#315e9c", "#53447c", "#1c6577"),
    "light": ("#a8caf7", "#c4b4f4", "#a9e1e9"),
    "night": ("#775052", "#524063", "#815d40"),
}


def paint_backdrop(painter, rect, theme, enabled=True):
    theme = theme if theme in PALETTES else "dark"
    painter.fillRect(rect, QColor(PALETTES[theme][0]))
    if not enabled:
        return
    w, h = rect.width(), rect.height()
    for (x, y, radius), tint in zip(((0.12, 0.05, 0.70), (0.94, 0.35, 0.65), (0.30, 1.0, 0.55)), GLOWS[theme]):
        glow = QRadialGradient(QPointF(rect.left() + x*w, rect.top() + y*h), max(1.0, radius*max(w,h)))
        color = QColor(tint)
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

    def paintEvent(self, event):
        painter = QPainter(self)
        paint_backdrop(painter, self.rect(), self.theme, self.enabled)
        painter.end()
