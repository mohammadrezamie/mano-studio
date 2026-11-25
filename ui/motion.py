"""Shared, short, interaction-driven navigation motion.

One lightweight indicator per tab bar; no animated page snapshots, timers
at idle, layout movement or effects on text/circuit content.
"""
from PySide6.QtCore import Qt, QRectF, QVariantAnimation, QEasingCurve, QAbstractAnimation, QEvent
from PySide6.QtGui import QPainter, QPalette, QPen
from PySide6.QtWidgets import QApplication, QTabBar, QTabWidget, QPushButton

TAB_DURATION=160


def motion_allowed():
    app=QApplication.instance()
    return app is not None and not bool(app.property("manoReducedMotion"))


def set_reduced_motion(app, reduced):
    app.setProperty("manoReducedMotion",bool(reduced))
    if reduced:
        for widget in app.allWidgets():
            if widget.property("manoMotionSurface"):
                widget.snap()


class MotionTabBar(QTabBar):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setProperty("manoMotionSurface", True)
        self.setDrawBase(False)
        self._position=QRectF()
        self._animation=QVariantAnimation(self)
        self._animation.setDuration(TAB_DURATION)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._frame)
        self._animation.finished.connect(self.snap)
        self.currentChanged.connect(self._selection)

    def target(self):
        if self.currentIndex()<0:return QRectF()
        r=QRectF(self.tabRect(self.currentIndex()))
        inset=min(12.0,r.width()/4)
        return QRectF(r.left()+inset,r.bottom()-3,max(0.0,r.width()-2*inset),2.5)

    def _frame(self,rect):
        self._position=QRectF(rect)
        self.update()

    def snap(self):
        self._animation.stop()
        self._position=self.target()
        self.update()

    def _selection(self,*_):
        target=self.target()
        self._animation.stop()
        if not motion_allowed() or not self.isVisible() or self._position.isEmpty() or target.isEmpty():
            self.snap()
            return
        self._animation.setStartValue(self._position)
        self._animation.setEndValue(target)
        self._animation.start()

    def resizeEvent(self,event):
        super().resizeEvent(event)
        if hasattr(self,"_animation"):self.snap()

    def hideEvent(self,event):
        super().hideEvent(event)
        if hasattr(self,"_animation"):self.snap()

    def paintEvent(self,event):
        super().paintEvent(event)
        if self.currentIndex()<0:return
        if self._animation.state()!=QAbstractAnimation.State.Running:
            self._position=self.target()
        if self._position.isEmpty():return
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self.palette().color(QPalette.ColorRole.Highlight))
        painter.setBrush(self.palette().color(QPalette.ColorRole.Highlight))
        painter.drawRoundedRect(self._position,1.25,1.25)
        painter.end()


class MotionTabs(QTabWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setTabBar(MotionTabBar(self))
        self.setDocumentMode(True)
        self.setUsesScrollButtons(True)
        self.setElideMode(Qt.TextElideMode.ElideRight)


class MotionButton(QPushButton):
    """Bounded, native button interaction feedback; no layout or text animation."""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setProperty("manoMotionSurface", True)
        self.level = 0.0
        self.hovered = False
        self.animation = QVariantAnimation(self)
        self.animation.setDuration(145)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.valueChanged.connect(self._frame)
        self.pressed.connect(lambda: self._retarget(1.0))
        self.released.connect(lambda: self._retarget(0.48 if self.hovered else 0.0))

    def _frame(self, value):
        self.level = float(value)
        self.update()

    def snap(self):
        self.animation.stop()
        self.level = 0.0
        self.update()

    def _retarget(self, target):
        self.animation.stop()
        if not (self.isVisible() and self.isEnabled() and motion_allowed()):
            self.snap()
            return
        if abs(self.level - target) < 0.001:
            return
        self.animation.setStartValue(self.level)
        self.animation.setEndValue(float(target))
        self.animation.start()

    def enterEvent(self, event):
        self.hovered = True
        super().enterEvent(event)
        self._retarget(1.0 if self.isDown() else 0.48)

    def leaveEvent(self, event):
        self.hovered = False
        super().leaveEvent(event)
        self._retarget(0.0)

    def hideEvent(self, event):
        self.hovered = False
        self.snap()
        super().hideEvent(event)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.EnabledChange and hasattr(self, "animation") and not self.isEnabled():
            self.snap()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.level <= 0 or not self.isEnabled():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = self.palette().color(QPalette.ColorRole.Highlight)
        if self.objectName() == "primary":
            color = self.palette().color(QPalette.ColorRole.HighlightedText)
        color.setAlpha(round(120 * self.level))
        painter.setPen(QPen(color, 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(2, 2, -2, -2), 6, 6)
        painter.end()
