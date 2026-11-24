"""Controlled bus transfer with actual Z/X state and simultaneous destination load."""
from PySide6.QtCore import Qt,QPointF,QRectF
from PySide6.QtGui import QPainter,QPen,QColor,QFont,QPainterPath
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QSpinBox,QCheckBox,QPushButton,QComboBox
from bus_model import RegisterBus
from ui.theme import PALETTES

class BusDiagram(QWidget):
    def __init__(self,theme):
        super().__init__()
        self.theme=theme;self.state=None
        self.setMinimumHeight(210)
    def paintEvent(self,event):
        if self.state is None:return
        words,enabled,load,state,width=self.state
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg,panel,raised,fg,muted,accent,border=PALETTES[self.theme]
        p.fillRect(self.rect(),QColor(bg))
        scale=min(self.width()/660,self.height()/250)
        p.translate((self.width()-660*scale)/2,(self.height()-250*scale)/2);p.scale(scale,scale)
        p.setFont(QFont("Consolas",11))
        for i,word in enumerate(words):
            x=45+i*210
            p.setPen(QPen(QColor(accent if load[i] else fg),1.5));p.setBrush(QColor(panel))
            p.drawRect(QRectF(x,22,150,54))
            p.drawText(QRectF(x,22,150,54),Qt.AlignmentFlag.AlignCenter,f"R{i} = {word:0{width//4}X}")
            mid=x+75
            # Standard triangular non-inverting buffer with separate enable pin.
            path=QPainterPath(QPointF(mid-19,100));path.lineTo(mid+19,100);path.lineTo(mid,137);path.closeSubpath()
            p.setPen(QPen(QColor(accent if enabled[i] else muted),1.5))
            p.drawLine(QPointF(mid,76),QPointF(mid,100));p.drawPath(path)
            p.drawLine(QPointF(mid,137),QPointF(mid,186))
            p.drawLine(QPointF(mid-45,113),QPointF(mid-12,113))
            p.drawText(QRectF(mid-75,88,68,22),Qt.AlignmentFlag.AlignRight,f"EN={int(enabled[i])}")
            p.setPen(QPen(QColor(accent if load[i] else muted),1))
            p.drawLine(QPointF(x+145,186),QPointF(x+145,76))
            p.drawText(QRectF(x+90,77,60,22),Qt.AlignmentFlag.AlignRight,f"LD={int(load[i])}")
        p.setPen(QPen(QColor(accent if state.drivers==1 else muted),3))
        p.drawLine(QPointF(28,186),QPointF(632,186))
        p.setPen(QColor(fg));p.drawText(QRectF(10,200,640,34),Qt.AlignmentFlag.AlignCenter,f"BUS[{width-1}:0] = {state.bits}")
        p.end()

class BusView(QWidget):
    def __init__(self,theme,fa=False):
        super().__init__()
        self.fa=fa
        layout=QVBoxLayout(self)
        note=QLabel(self.t("Enable one register output and choose destination load controls. A clock transfer loads all destinations from the old bus value. Z = high impedance; X = conflicting bits.","خروجی یک ثبات را فعال و مقصدهای بارگذاری را انتخاب کنید. انتقال ساعت، همه مقصدها را از مقدار قبلی گذرگاه بارگذاری می‌کند. Z امپدانس بالا و X تعارض بیت‌هاست."))
        note.setWordWrap(True);layout.addWidget(note)
        row=QHBoxLayout();self.width=QComboBox()
        for n in (4,8,16):self.width.addItem(str(n),n)
        self.width.setCurrentIndex(1)
        row.addWidget(QLabel(self.t("Bus width","عرض گذرگاه")));row.addWidget(self.width)
        pulse=QPushButton(self.t("Transfer on clock","انتقال با ساعت"));pulse.clicked.connect(self.transfer);row.addWidget(pulse)
        layout.addLayout(row)
        grid=QGridLayout();self.words=[];self.en=[];self.ld=[]
        for i in range(3):
            word=QSpinBox();word.setDisplayIntegerBase(16)
            en=QCheckBox("EN");ld=QCheckBox("LD")
            self.words.append(word);self.en.append(en);self.ld.append(ld)
            grid.addWidget(QLabel(f"R{i}"),i,0);grid.addWidget(word,i,1);grid.addWidget(en,i,2);grid.addWidget(ld,i,3)
            word.valueChanged.connect(lambda v,n=i:self.edit(n,v))
            en.toggled.connect(self.refresh);ld.toggled.connect(self.refresh)
        layout.addLayout(grid)
        self.diagram=BusDiagram(theme);layout.addWidget(self.diagram,1)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        self.width.currentIndexChanged.connect(self.configure);self.configure()
    def t(self,en,fa):return fa if self.fa else en
    def configure(self,*_):
        self.model=RegisterBus(self.width.currentData())
        for i,word in enumerate(self.words):
            word.blockSignals(True);word.setRange(0,(1<<self.model.width)-1);word.setValue(0);word.blockSignals(False)
        self.refresh()
    def edit(self,index,value):
        self.model.set_word(index,value);self.refresh()
    def controls(self):return ([c.isChecked() for c in self.en],[c.isChecked() for c in self.ld])
    def refresh(self,*_):
        en,ld=self.controls();state=self.model.preview(en)
        self.diagram.state=(tuple(self.model.registers),en,ld,state,self.model.width);self.diagram.update()
        status=self.t("Ready","آماده") if state.drivers==1 else self.t("No enabled driver (Z)","هیچ خروجی فعالی نیست (Z)") if not state.drivers else self.t("Multiple drivers: transfer blocked","چند خروجی فعال: انتقال مسدود است")
        if state.contention:status+=" · X"
        self.status.setText(status)
    def transfer(self):
        en,ld=self.controls()
        try:self.model.transfer(en,ld)
        except ValueError:
            self.status.setText(self.t("Transfer blocked: enable exactly one output.","انتقال مسدود شد: دقیقاً یک خروجی را فعال کنید."));return
        for i,word in enumerate(self.words):
            word.blockSignals(True);word.setValue(self.model.registers[i]);word.blockSignals(False)
        self.refresh()
