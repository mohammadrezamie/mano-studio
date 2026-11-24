"""Interactive architecture canvas backed exclusively by CPU microevents."""
from PySide6.QtCore import Qt,QRectF,QPointF,QVariantAnimation,QEasingCurve,QSignalBlocker
from PySide6.QtGui import QColor,QPainter,QPen,QFont,QPainterPath
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QComboBox
from ui.theme import PALETTES
from ui.motion import motion_allowed

REGISTERS=("AR","PC","DR","AC","IR","TR","M")
WIDTH={"AR":3,"PC":3,"DR":4,"AC":4,"IR":4,"TR":4,"INPR":2,"OUTR":2}
# These are model control labels, not a gate-level connectivity assertion.
BUS_LOADS={"AR.LD":"AR","PC.LD":"PC","DR.LD":"DR","IR.LD":"IR","TR.LD":"TR","M.WRITE":"M"}


def edge_routes(group):
    """Derive highlighting only from a recorded control trace."""
    if group is None or group.control is None:return None,()
    c=group.control
    if c.source is None:return None,()
    return c.source,tuple(BUS_LOADS[s] for s in c.signals if s in BUS_LOADS)


class ArchitectureCanvas(QWidget):
    def __init__(self,view):
        super().__init__(view)
        self.view=view
        self.setMinimumHeight(200)
        self.setAccessibleName(view.t("Recorded CPU datapath","مسیر داده ثبت‌شده پردازنده"))

    def paintEvent(self,event):
        v=self.view;g=v.group
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg,panel,raised,fg,muted,accent,border=PALETTES[v.theme]
        p.fillRect(self.rect(),QColor(bg))
        scale=min(self.width()/1000,self.height()/300)
        p.translate((self.width()-1000*scale)/2,(self.height()-300*scale)/2);p.scale(scale,scale)
        align=Qt.AlignmentFlag
        def text(x,y,w,h,value,size=13,color=fg,bold=False,center=False,mono=False):
            p.setPen(QColor(color));font=QFont("Consolas" if mono else "Segoe UI")
            font.setPixelSize(size);font.setBold(bold);p.setFont(font)
            p.drawText(QRectF(x,y,w,h),(align.AlignHCenter if center else align.AlignLeft)|align.AlignVCenter,str(value))
        def rect(x,y,w,h,active=False,fill=panel,r=10):
            p.setPen(QPen(QColor(accent if active else border),1.5 if active else 1))
            p.setBrush(QColor(fill));p.drawRoundedRect(QRectF(x,y,w,h),r,r)
        def line(x1,y1,x2,y2,on=False):
            p.setPen(QPen(QColor(accent if on else border),2.6 if on else 1.3,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap))
            p.drawLine(QPointF(x1,y1),QPointF(x2,y2))
        def arrow(x,y,down):
            sign=1 if down else -1
            p.setPen(QPen(QColor(accent),2))
            p.drawLine(QPointF(x-4,y-6*sign),QPointF(x,y))
            p.drawLine(QPointF(x+4,y-6*sign),QPointF(x,y))
        def fmt(name,value):
            return "—" if value is None else f"{value:0{WIDTH.get(name,1)}X}"
        source,targets=edge_routes(g)
        state=g.after if g else v.cpu.registers() if v.cpu else {}
        before=g.before if g else state
        c=g.control if g else None
        # A sparse static dot grid is decorative, never a net or signal.
        p.setPen(Qt.PenStyle.NoPen)
        dot=QColor(border);dot.setAlpha(75);p.setBrush(dot)
        for x in range(12,1000,20):
            for y in range(10,300,20):p.drawEllipse(QPointF(x,y),.7,.7)
        text(20,3,660,24,v.t("COMMON BUS · REGISTER TRANSFERS","گذرگاه مشترک · انتقال ثبات‌ها"),15,muted,True)
        select="—" if not c else f"{c.select:03b}"
        value="—" if not c or c.value is None else f"{c.value:04X}"
        rect(735,4,245,24,bool(source),raised,6)
        text(745,4,225,24,f"S2 S1 S0  {select}  ·  {value}",14,accent if source else muted,True,True,True)
        # Seven functional sources share the modeled bus. No separate
        # dedicated ALU route is inferred from register-value changes.
        for i,name in enumerate(REGISTERS):
            x=20+i*139;cx=x+63
            on=name==source or name in targets
            changed=name!="M" and before.get(name)!=state.get(name)
            rect(x,38,126,80,on or changed)
            text(x+10,43,106,20,name,15,accent if on or changed else fg,True,mono=True)
            if name=="M":
                access=g.writes[-1] if g and g.writes else g.reads[-1] if g and g.reads else None
                text(x+10,65,106,25,f"@ {access[0]:03X}" if access else "4096 × 16",16,fg,True,mono=True)
                text(x+10,92,106,18,f"{access[-1]:04X}" if access else "—",13,muted,mono=True)
            else:
                text(x+10,64,106,29,fmt(name,state.get(name)),23,accent if changed else fg,True,mono=True)
                text(x+10,94,106,18,(fmt(name,before.get(name))+" → "+fmt(name,state.get(name))) if changed else f"{12 if name in ('AR','PC') else 16} bit",12,muted,mono=True)
            line(cx,118,cx,145,on)
            if name==source:arrow(cx,142,True)
            if name in targets:arrow(cx,120,False)
        line(83,145,917,145,bool(source))
        if source and v.progress<1:
            sx=83+139*REGISTERS.index(source)
            p.setPen(Qt.PenStyle.NoPen);p.setBrush(QColor(accent))
            p.drawEllipse(QPointF(sx,118+27*v.progress),4,4)
        text(20,151,960,20,v.t("Recorded shared-bus selection · dedicated ALU controls shown separately","انتخاب ثبت‌شده گذرگاه · کنترل‌های مستقل ALU جداگانه نمایش داده می‌شوند"),12,muted,center=True)
        signals=c.signals if c else ()
        alu=tuple(s for s in signals if s.startswith("ALU."))
        rect(20,182,300,99,bool(alu))
        text(32,188,276,19,"ALU  /  E",14,muted,True,mono=True)
        text(32,211,276,28," · ".join(alu) if alu else "—",18,accent if alu else fg,True,mono=True)
        text(32,246,276,21,f"E: {fmt('E',before.get('E'))} → {fmt('E',state.get('E'))}",14,fg,mono=True)
        rect(335,182,300,99)
        text(347,188,276,19,v.t("I/O REGISTERS","ثبات‌های ورودی/خروجی"),14,muted,True)
        text(347,211,276,27,f"INPR {fmt('INPR',state.get('INPR'))}   OUTR {fmt('OUTR',state.get('OUTR'))}",18,fg,True,mono=True)
        text(347,246,276,21,f"FGI {fmt('FGI',state.get('FGI'))}     FGO {fmt('FGO',state.get('FGO'))}",14,fg,mono=True)
        rect(650,182,330,99)
        text(662,188,306,19,v.t("CONTROL STATE","وضعیت کنترل"),14,muted,True)
        text(662,211,306,27,f"SC {fmt('SC',state.get('SC'))}   I {fmt('I',state.get('I'))}   R {fmt('R',state.get('R'))}",18,fg,True,mono=True)
        text(662,246,306,21,f"IEN {fmt('IEN',state.get('IEN'))}   TR {fmt('TR',state.get('TR'))}",14,fg,mono=True)
        p.end()


class DatapathView(QWidget):
    def __init__(self,theme,reduced_motion=False,parent=None,fa=False):
        super().__init__(parent)
        self.theme=theme;self.fa=fa;self.reduced_motion=reduced_motion
        self.cpu=None;self.last_step=None;self.group=None;self.progress=1.0
        self.animation=QVariantAnimation(self)
        self.animation.setStartValue(0.0);self.animation.setEndValue(1.0)
        self.animation.setDuration(240)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.valueChanged.connect(self.advance)
        layout=QVBoxLayout(self);layout.setContentsMargins(6,6,6,6);layout.setSpacing(4)
        row=QHBoxLayout()
        self.title=QLabel();self.title.setObjectName("section");row.addWidget(self.title,1)
        self.previous=QPushButton(self.t("Previous group","گروه قبلی"))
        self.next=QPushButton(self.t("Next group","گروه بعدی"))
        self.groups=QComboBox();self.groups.setAccessibleName(self.t("Inspect recorded timing group","بررسی گروه زمانی ثبت‌شده"))
        self.groups.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.previous.clicked.connect(lambda:self.groups.setCurrentIndex(max(0,self.groups.currentIndex()-1)))
        self.next.clicked.connect(lambda:self.groups.setCurrentIndex(min(self.groups.count()-1,self.groups.currentIndex()+1)))
        row.addWidget(self.previous);row.addWidget(self.groups);row.addWidget(self.next)
        self.focus=QPushButton(self.t("Focus canvas","تمرکز روی بوم"));self.focus.setCheckable(True);row.addWidget(self.focus)
        layout.addLayout(row)
        self.canvas=ArchitectureCanvas(self);layout.addWidget(self.canvas,1)
        self.rtl=QLabel();self.rtl.setWordWrap(True);self.rtl.setLayoutDirection(Qt.LayoutDirection.LeftToRight);layout.addWidget(self.rtl)
        self.signals=QLabel();self.signals.setWordWrap(True);self.signals.setObjectName("muted");self.signals.setLayoutDirection(Qt.LayoutDirection.LeftToRight);layout.addWidget(self.signals)
        self.note=QLabel(self.t("Recorded timing groups, not electrical bus timing. Inspecting a group never changes the CPU.","گروه‌های زمانی ثبت‌شده، نه زمان‌بندی الکتریکی گذرگاه. بررسی گروه، CPU را تغییر نمی‌دهد."))
        self.note.setWordWrap(True);self.note.setObjectName("muted");layout.addWidget(self.note)
        self.groups.currentIndexChanged.connect(self.select_group)
        self.set_state(None)

    def t(self,en,fa):return fa if self.fa else en

    def advance(self,value):
        self.progress=float(value);self.canvas.update()

    def stop(self):
        self.animation.stop();self.progress=1.0;self.canvas.update()

    def set_state(self,cpu,event=None):
        self.stop()
        self.cpu,self.last_step=cpu,event
        with QSignalBlocker(self.groups):
            self.groups.clear()
            for g in event.microevents if event else ():
                self.groups.addItem(f"{'RT' if g.phase=='interrupt' else 'T'}{g.timing}")
            self.groups.setCurrentIndex(self.groups.count()-1)
        self.select_group(self.groups.currentIndex())

    def select_group(self,index):
        self.stop()
        events=self.last_step.microevents if self.last_step else ()
        self.group=events[index] if 0<=index<len(events) else None
        self.previous.setEnabled(index>0)
        self.next.setEnabled(0<=index<len(events)-1)
        self.groups.setEnabled(bool(events))
        e=self.last_step;g=self.group
        self.title.setText(f"{e.address:03X} · {e.mnemonic} · {self.groups.currentText()}" if e and g else self.t("Live CPU state","وضعیت زنده CPU"))
        self.rtl.setText(g.rtl if g else "—")
        self.signals.setText(" · ".join(g.control.signals) if g and g.control else "—")
        if g and edge_routes(g)[0] and not self.reduced_motion and motion_allowed() and self.isVisible():
            self.progress=0.0;self.animation.start()
        self.canvas.update()

    def hideEvent(self,event):
        self.stop();super().hideEvent(event)
