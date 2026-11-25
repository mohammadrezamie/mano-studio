"""Focused directed state graph, derived exclusively from actual model steps."""
import math
from PySide6.QtCore import Qt, QPointF, QRectF, QSize
from PySide6.QtGui import QPainter, QPainterPath, QPen, QBrush, QPolygonF, QPalette
from PySide6.QtWidgets import QWidget
from state_synthesis import outgoing_edges


class StateGraph(QWidget):
    """Current state and all possible outgoing transitions; no invented edges."""
    def __init__(self, fa=False):
        super().__init__()
        self.fa=fa
        self.model=None
        self.state=0
        self.x=0
        self.edges=()
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.setMinimumHeight(210)
        self.setAccessibleName("نمودار انتقال حالت جاری" if fa else "Current state transition graph")

    def sizeHint(self):
        return QSize(440,260)

    def set_state(self,model,state,x):
        self.model,self.state,self.x=model,state,x
        self.edges=outgoing_edges(model,state)
        n=model.bits
        desc=[f"Q={state:0{n}b}"]
        for edge in self.edges:
            for value,y in edge.conditions:
                desc.append(f"X={value}: Q⁺={edge.destination:0{n}b}, Y={y}")
        self.setAccessibleDescription("; ".join(desc))
        self.update()

    def paintEvent(self,event):
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pal=self.palette()
        bg=pal.color(QPalette.ColorRole.Base)
        fg=pal.color(QPalette.ColorRole.Text)
        muted=pal.color(QPalette.ColorRole.Mid)
        accent=pal.color(QPalette.ColorRole.Highlight)
        painter.fillRect(self.rect(),bg)
        if self.model is None:
            painter.end()
            return
        scale=min(self.width()/440,self.height()/260)
        painter.translate((self.width()-440*scale)/2,(self.height()-260*scale)/2)
        painter.scale(scale,scale)
        radius=32
        source=QPointF(110,130)
        others=[e for e in self.edges if e.destination!=self.state]
        targets={e.destination:QPointF(342,130 if len(others)==1 else 65+130*i)
                 for i,e in enumerate(others)}

        def text(rect,label,color=fg):
            painter.setPen(color)
            painter.drawText(rect,Qt.AlignmentFlag.AlignCenter,label)

        def node(center,state,current=False):
            painter.setPen(QPen(accent if current else muted,3 if current else 1.5))
            painter.setBrush(QBrush(bg))
            painter.drawEllipse(center,radius,radius)
            label=f"{state:0{self.model.bits}b}"
            if self.model.mode=="Moore":
                label+=f" / {self.model.step(state,0)[1]}"
            text(QRectF(center.x()-radius,center.y()-18,2*radius,36),label)
            if current:
                text(QRectF(center.x()-55,center.y()+35,110,22),"جاری" if self.fa else "Current",accent)

        def arrow(path,end,tangent,color,active):
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(color,2.8 if active else 1.4))
            painter.drawPath(path)
            dx,dy=tangent.x(),tangent.y()
            mag=math.hypot(dx,dy) or 1
            ux,uy=dx/mag,dy/mag
            wing=5
            p1=QPointF(end.x()-11*ux+wing*uy,end.y()-11*uy-wing*ux)
            p2=QPointF(end.x()-11*ux-wing*uy,end.y()-11*uy+wing*ux)
            painter.setBrush(QBrush(color))
            painter.drawPolygon(QPolygonF([end,p1,p2]))

        for edge in self.edges:
            active=any(x==self.x for x,_ in edge.conditions)
            color=accent if active else muted
            label=", ".join(str(x) if self.model.mode=="Moore" else f"{x}/{y}"
                            for x,y in edge.conditions)
            if active:label="▶ "+label
            if edge.destination==self.state:
                start=QPointF(88,107);end=QPointF(132,107)
                path=QPainterPath(start)
                path.cubicTo(QPointF(40,22),QPointF(180,22),end)
                arrow(path,end,end-QPointF(180,22),color,active)
                text(QRectF(52,15,116,24),label,color)
            else:
                target=targets[edge.destination]
                dx,dy=target.x()-source.x(),target.y()-source.y()
                mag=math.hypot(dx,dy)
                unit=QPointF(dx/mag,dy/mag)
                start=source+unit*radius
                end=target-unit*radius
                path=QPainterPath(start);path.lineTo(end)
                arrow(path,end,end-start,color,active)
                mid=(start+end)/2
                text(QRectF(mid.x()-52,mid.y()-27,104,23),label,color)
        node(source,self.state,True)
        for destination,center in targets.items():
            node(center,destination)
        painter.end()
