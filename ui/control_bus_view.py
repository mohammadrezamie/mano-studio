"""Compact functional common-bus diagram driven only by selected MicroEvent."""
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QFont
from PySide6.QtWidgets import QWidget
from control_trace import BUS_SOURCES


class ControlBusView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa
        self.control=None
        self.setMinimumHeight(110)
        self.setMaximumHeight(150)
        self.setAccessibleName("گذرگاه مشترک" if fa else "Common bus")

    def set_control(self,control):
        self.control=control
        self.update()

    def paintEvent(self,event):
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        palette=self.palette()
        fg=palette.text().color()
        muted=palette.mid().color()
        active=palette.highlight().color()
        scale=min(self.width()/660,self.height()/110)
        p.translate((self.width()-660*scale)/2,(self.height()-110*scale)/2)
        p.scale(scale,scale)
        p.setFont(QFont("Consolas",10))
        c=self.control
        for index,source in enumerate(BUS_SOURCES[1:],1):
            x=24+(index-1)*88
            on=c is not None and c.select==index
            p.setPen(QPen(active if on else muted,2 if on else 1))
            p.setBrush(palette.base())
            p.drawRect(QRectF(x,8,64,27))
            p.setPen(fg)
            p.drawText(QRectF(x,8,64,27),Qt.AlignmentFlag.AlignCenter,f"{source} / {index:03b}")
            p.setPen(QPen(active if on else muted,2 if on else 1))
            p.drawLine(x+32,35,x+32,56)
        p.setPen(QPen(active if c and c.source else muted,3))
        p.drawLine(56,56,584,56)
        p.setPen(fg)
        value="—" if not c or c.value is None else f"{c.value:04X}"
        select="—" if not c else f"{c.select:03b}"
        p.drawText(QRectF(12,65,636,34),Qt.AlignmentFlag.AlignCenter,f"S2 S1 S0 = {select}    |    BUS[15:0] = {value}")
        p.end()
