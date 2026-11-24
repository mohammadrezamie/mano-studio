"""Embedded clocked-component workbench with sample-based waveform view."""
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QColor,QPainter,QPen,QFont,QPainterPath
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QComboBox,QLabel,QPushButton
from sequential_logic import ClockedCircuit, MODELS
from ui.theme import PALETTES

TITLES={
    "D":("D flip-flop","فلیپ‌فلاپ D"),
    "JK":("JK flip-flop","فلیپ‌فلاپ JK"),
    "T":("T flip-flop","فلیپ‌فلاپ T"),
    "SR":("Clocked SR flip-flop","فلیپ‌فلاپ SR ساعت‌دار"),
    "REG4":("4-bit register","ثبات ۴ بیتی"),
    "COUNT4":("4-bit up counter","شمارنده صعودی ۴ بیتی"),
}


class ClockedDiagram(QWidget):
    def __init__(self, theme):
        super().__init__()
        self.theme=theme
        self.model=None
        self.setMinimumHeight(155)

    def paintEvent(self,event):
        if self.model is None:
            return
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg,panel,raised,fg,muted,accent,border=PALETTES[self.theme]
        p.fillRect(self.rect(),QColor(bg))
        scale=min(self.width()/640,self.height()/205)
        p.translate((self.width()-640*scale)/2,(self.height()-205*scale)/2)
        p.scale(scale,scale)
        m=self.model
        inputs=list(m.inputs.items())+[("CLK",m.clock)]
        outputs=list(m.outputs.items())
        body=QRectF(258,14,124,174)
        p.setBrush(QColor(panel))
        p.setPen(QPen(QColor(fg),1.5))
        p.drawRect(body)
        p.setFont(QFont("Segoe UI",12,QFont.Weight.Bold))
        p.drawText(QRectF(260,14,120,27),Qt.AlignmentFlag.AlignCenter,m.kind)
        p.setFont(QFont("Consolas",11))
        for i,(name,value) in enumerate(inputs):
            y=51+i*min(23,118/max(1,len(inputs)-1))
            color=QColor(accent if value else muted)
            p.setPen(QPen(color,2 if value else 1))
            p.drawLine(QPointF(160,y),QPointF(258,y))
            p.drawText(QRectF(80,y-10,70,20),Qt.AlignmentFlag.AlignRight,f"{name} {value}")
            if name=="CLK":
                path=QPainterPath(QPointF(258,y-7))
                path.lineTo(270,y)
                path.lineTo(258,y+7)
                p.setPen(QPen(QColor(fg),1.5))
                p.drawPath(path)
            else:
                p.setPen(QColor(fg))
                p.drawText(QRectF(265,y-10,55,20),Qt.AlignmentFlag.AlignLeft,name)
        for i,(name,value) in enumerate(outputs):
            y=51+i*32
            color=QColor(accent if value else muted)
            p.setPen(QPen(color,2 if value else 1))
            p.drawLine(QPointF(382,y),QPointF(480,y))
            p.drawText(QRectF(490,y-10,80,20),Qt.AlignmentFlag.AlignLeft,f"{name} {value}")
            p.setPen(QColor(fg))
            p.drawText(QRectF(320,y-10,55,20),Qt.AlignmentFlag.AlignRight,name)
        p.end()


class WaveformView(QWidget):
    def __init__(self, theme, fa=False):
        super().__init__()
        self.theme=theme
        self.model=None
        self.setMinimumHeight(300)
        self.fa=fa
        self.setAccessibleName("تاریخچه نمودار زمانی" if fa else "Digital waveform history")

    def paintEvent(self,event):
        p=QPainter(self)
        bg,panel,raised,fg,muted,accent,border=PALETTES[self.theme]
        p.fillRect(self.rect(),QColor(panel))
        if not self.model:
            return
        m=self.model
        names=("CLK",)+m.pins+tuple(m.outputs)
        samples=[(s.clock,)+s.inputs+s.outputs for s in m.history]
        left=68
        right=max(left+1,self.width()-16)
        top=16
        pitch=max(15,(self.height()-top-25)/len(names))
        spacing=(right-left)/max(1,len(samples))
        p.setFont(QFont("Consolas",10))
        for i,name in enumerate(names):
            y=top+i*pitch
            p.setPen(QColor(fg))
            p.drawText(QRectF(8,y,56,pitch),Qt.AlignmentFlag.AlignVCenter,name)
            p.setPen(QPen(QColor(border),1))
            p.drawLine(QPointF(left,y+pitch-1),QPointF(right,y+pitch-1))
            if not samples:
                continue
            height=min(13,pitch*.46)
            def level(value):
                return y+pitch*.73-height*value
            path=QPainterPath(QPointF(left,level(samples[0][i])))
            for j,sample in enumerate(samples):
                x=left+j*spacing
                path.lineTo(x,level(sample[i]))
                path.lineTo(x+spacing,level(sample[i]))
            p.setPen(QPen(QColor(accent if i==0 else fg),1.65))
            p.drawPath(path)
        p.setPen(QColor(muted))
        p.drawText(QRectF(left,self.height()-20,right-left,18),Qt.AlignmentFlag.AlignRight,"ترتیب رویدادها" if self.fa else "Event samples  →")
        p.end()


class SequentialView(QWidget):
    def __init__(self, theme, fa=False):
        super().__init__()
        self.fa=fa
        layout=QVBoxLayout(self)
        row=QHBoxLayout()
        self.selector=QComboBox()
        for key in MODELS:
            self.selector.addItem(TITLES[key][fa],key)
        row.addWidget(self.selector,1)
        self.clock=QPushButton("CLK = 0")
        self.clock.setCheckable(True)
        self.clock.toggled.connect(self.change_clock)
        row.addWidget(self.clock)
        pulse=QPushButton(self.t("Pulse clock","یک پالس ساعت"))
        pulse.setObjectName("primary")
        pulse.clicked.connect(self.pulse)
        row.addWidget(pulse)
        reset=QPushButton(self.t("Reset","بازنشانی"))
        reset.clicked.connect(self.reset)
        row.addWidget(reset)
        layout.addLayout(row)
        self.note=QLabel(self.t("Outputs update only on a rising clock edge. Waveforms show event order, not physical delay.",
              "خروجی‌ها فقط در لبه بالارونده ساعت تغییر می‌کنند. نمودار ترتیب رویدادهاست، نه تأخیر فیزیکی."))
        self.note.setWordWrap(True)
        layout.addWidget(self.note)
        self.input_layout=QGridLayout()
        layout.addLayout(self.input_layout)
        self.diagram=ClockedDiagram(theme)
        self.diagram.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.diagram,1)
        self.summary=QLabel()
        self.summary.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.summary)
        self.waveform=WaveformView(theme,self.fa)
        self.waveform.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.waveform,3)
        self.status=QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.selector.currentIndexChanged.connect(self.load)
        self.load()

    def t(self,en,fa):
        return fa if self.fa else en

    def load(self):
        self.model=ClockedCircuit(self.selector.currentData())
        while self.input_layout.count():
            item=self.input_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.buttons={}
        for i,name in enumerate(self.model.pins):
            button=QPushButton()
            button.setCheckable(True)
            button.toggled.connect(lambda v,n=name:self.input_changed(n,v))
            self.buttons[name]=button
            self.input_layout.addWidget(button,i//6,i%6)
        self.diagram.model=self.waveform.model=self.model
        self.status.clear()
        self.refresh()

    def reset(self):
        self.model.reset()
        self.status.clear()
        self.refresh()

    def input_changed(self,name,value):
        self.model.set_input(name,int(value))
        self.status.clear()
        self.refresh()

    def change_clock(self,value):
        self.perform(lambda:self.model.set_clock(int(value)))

    def pulse(self):
        self.perform(self.model.pulse)

    def perform(self,fn):
        try:
            fn()
            self.status.clear()
        except ValueError:
            self.status.setText(self.t("SR = 11 is forbidden; edge rejected.","حالت SR = 11 نامعتبر است؛ لبه ساعت اعمال نشد."))
        self.refresh()

    def refresh(self):
        for name,button in self.buttons.items():
            button.blockSignals(True)
            button.setChecked(bool(self.model.inputs[name]))
            button.setText(f"{name} = {self.model.inputs[name]}")
            button.blockSignals(False)
        self.clock.blockSignals(True)
        self.clock.setChecked(bool(self.model.clock))
        self.clock.setText(f"CLK = {self.model.clock}")
        self.clock.blockSignals(False)
        self.summary.setText("   |   ".join(f"{n} = {v}" for n,v in self.model.outputs.items())+
                             (f"    HEX = {self.model.value:X}" if self.model.width>1 else ""))
        self.diagram.update()
        self.waveform.update()
