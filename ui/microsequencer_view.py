"""Functional CAR selector diagram: actual recorded candidates, no second execution."""
from PySide6.QtCore import Qt,QRectF,QPointF
from PySide6.QtGui import QPainter,QPen,QFont,QPolygonF
from PySide6.QtWidgets import QWidget


class MicrosequencerView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa
        self.trace=None
        self.setMinimumHeight(126)
        self.setAccessibleName("مسیر انتخاب آدرس ریزدستور" if fa else "Microinstruction address selector")

    def set_trace(self,trace):
        self.trace=trace
        self.update()

    def paintEvent(self,event):
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        palette=self.palette()
        fg,muted,accent=palette.text().color(),palette.mid().color(),palette.highlight().color()
        scale=min(self.width()/600,self.height()/150)
        p.translate((self.width()-600*scale)/2,(self.height()-150*scale)/2)
        p.scale(scale,scale)
        p.setFont(QFont("Consolas",10))
        t=self.trace
        candidates=t.address_candidates if t else tuple((k,None) for k in ("CAR+1","AD","SBR","MAP"))
        for i,(name,value) in enumerate(candidates):
            x=32+132*i
            on=t is not None and name==t.next_source
            p.setPen(QPen(accent if on else muted,2 if on else 1))
            p.setBrush(palette.base())
            p.drawRect(QRectF(x,6,116,29))
            p.setPen(fg)
            p.drawText(QRectF(x,6,116,29),Qt.AlignmentFlag.AlignCenter,name+"  "+("—" if value is None else f"{value:02X}"))
            p.setPen(QPen(accent if on else muted,3 if on else 1))
            p.drawLine(QPointF(x+58,35),QPointF(x+58,55))
            if on:
                p.drawText(QRectF(x+59,35,56,20),Qt.AlignmentFlag.AlignCenter,"✓")
        p.setPen(QPen(accent if t else muted,1.5))
        p.setBrush(palette.base())
        p.drawPolygon(QPolygonF([QPointF(32,55),QPointF(544,55),QPointF(410,92),QPointF(166,92)]))
        p.setPen(fg)
        p.drawText(QRectF(166,60,244,26),Qt.AlignmentFlag.AlignCenter,"4:1 MUX · 7 bit")
        p.setPen(QPen(accent if t else muted,2))
        p.drawLine(QPointF(288,92),QPointF(288,106))
        p.setBrush(palette.base())
        p.drawRect(QRectF(226,106,124,30))
        p.setPen(fg)
        p.drawText(QRectF(226,106,124,30),Qt.AlignmentFlag.AlignCenter,"CAR ← "+(f"{t.after['CAR']:02X}" if t else "—"))
        p.end()
