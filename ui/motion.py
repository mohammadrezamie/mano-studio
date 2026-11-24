"""Shared, short, interaction-driven navigation motion.

One lightweight indicator per tab bar; no animated page snapshots, timers
at idle, layout movement or effects on text/circuit content.
"""
from PySide6.QtCore import Qt, QRectF, QVariantAnimation, QEasingCurve, QAbstractAnimation
from PySide6.QtGui import QPainter, QPalette
from PySide6.QtWidgets import QApplication, QTabBar, QTabWidget

TAB_DURATION=160


def motion_allowed():
    app=QApplication.instance()
    return app is not None and not bool(app.property("manoReducedMotion"))


def set_reduced_motion(app, reduced):
    app.setProperty("manoReducedMotion",bool(reduced))
    if reduced:
        for widget in app.allWidgets():
            if isinstance(widget,MotionTabBar):
                widget.snap()


class MotionTabBar(QTabBar):
    def __init__(self,parent=None):
        super().__init__(parent)
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
