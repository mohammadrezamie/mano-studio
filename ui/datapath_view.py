"""Single CPU visual view: consumes actual CPU state and StepEvent, never simulates."""
from PySide6.QtCore import Qt, QRectF, QPointF, QVariantAnimation
from PySide6.QtGui import QColor, QPainter, QPen, QFont
from PySide6.QtWidgets import QWidget
from ui.theme import PALETTES


class DatapathView(QWidget):
    def __init__(self, theme, reduced_motion=False, parent=None):
        super().__init__(parent)
        self.theme=theme
        self.reduced_motion=reduced_motion
        self.cpu=None
        self.event=None
        self.progress=1.0
        self.setMinimumHeight(230)
        self.animation=QVariantAnimation(self)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setDuration(280)
        self.animation.valueChanged.connect(self.advance)

    def advance(self,value):
        self.progress=float(value)
        self.update()

    def stop(self):
        self.animation.stop()
        self.progress=1.0
        self.update()

    def set_state(self,cpu,event=None):
        self.stop()
        self.cpu,self.event=cpu,event
        if event and event.mnemonic in ("LDA","ADD","AND","STA","BSA","ISZ","INT") and not self.reduced_motion and self.isVisible():
            self.progress=0.0
            self.animation.start()
        self.update()

    def hideEvent(self,event):
        self.stop()
        super().hideEvent(event)

    def paintEvent(self,event):
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg,panel,raised,fg,muted,accent,border=PALETTES[self.theme]
        p.fillRect(self.rect(),QColor(bg))
        scale=min(self.width()/760,self.height()/260)
        p.translate((self.width()-760*scale)/2,(self.height()-260*scale)/2)
        p.scale(scale,scale)
        cpu=self.cpu
        ev=self.event
        def card(x,y,w,h,title,lines,active=False):
            p.setPen(QPen(QColor(accent if active else border),1.3))
            p.setBrush(QColor(panel))
            p.drawRoundedRect(QRectF(x,y,w,h),11,11)
            p.setPen(QColor(accent if active else fg))
            p.setFont(QFont("Segoe UI",11,QFont.Weight.Bold))
            p.drawText(QRectF(x+12,y+6,w-24,22),Qt.AlignmentFlag.AlignLeft,title)
            p.setFont(QFont("Consolas",12))
            for i,(text,changed) in enumerate(lines):
                p.setPen(QColor(accent if changed else fg))
                p.drawText(QRectF(x+12,y+35+i*25,w-24,23),Qt.AlignmentFlag.AlignLeft,text)
        def reg(name,width):
            value=getattr(cpu,name.lower(),0)
            changed=bool(ev and ev.before.get(name)!=ev.after.get(name))
            return (f"{name:4} {value:0{width}X}" if cpu else f"{name:4} —",changed)
        address=ev.effective_address if ev else None
        mem=[("4096 × 16 bit",False),("EA  —" if address is None else f"EA  {address:03X}",False),
             ("M   —" if address is None else f"M   {cpu.memory[address]:04X}",bool(ev and ev.writes))]
        card(20,30,180,180,"MEMORY",mem,bool(ev and address is not None))
        card(280,30,190,180,"CPU REGISTERS",[reg("PC",3),reg("IR",4),reg("AR",3),reg("DR",4),reg("AC",4)])
        op=ev.mnemonic if ev else "—"
        card(550,30,190,180,"EXECUTION",[(f"OP  {op}",False),reg("E",1),reg("IEN",1),reg("FGI",1),reg("FGO",1)],bool(ev))
        # Conceptual instruction-level activity, not hardware bus timing.
        transfer=bool(ev and ev.mnemonic in ("LDA","ADD","AND","STA","BSA","ISZ","INT"))
        p.setPen(QPen(QColor(accent if transfer else border),2.2))
        p.drawLine(QPointF(200,120),QPointF(280,120))
        p.setPen(QPen(QColor(accent if ev else border),2))
        p.drawLine(QPointF(470,120),QPointF(550,120))
        if transfer and self.progress<1:
            fraction=1-self.progress if ev.mnemonic in ("STA","BSA","INT") else self.progress
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(accent))
            p.drawEllipse(QPointF(200+80*fraction,120),4.5,4.5)
        p.setFont(QFont("Segoe UI",10))
        p.setPen(QColor(muted))
        p.drawText(QRectF(20,225,720,20),Qt.AlignmentFlag.AlignCenter,"Instruction-level activity · not a clock-cycle bus trace")
        p.end()
