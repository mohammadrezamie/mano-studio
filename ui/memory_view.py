"""Memory device workbench, integrated in Logic Lab."""
from PySide6.QtCore import Qt,QRectF,QPointF
from PySide6.QtGui import QPainter,QColor,QPen,QFont
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,
    QSpinBox,QCheckBox,QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView)
from memory_model import MemoryChip
from ui.theme import PALETTES

class MemoryDiagram(QWidget):
    def __init__(self,theme):
        super().__init__()
        self.theme=theme
        self.state=None
        self.setMinimumHeight(160)
    def paintEvent(self,event):
        if self.state is None:return
        chip,address,data,cs,oe,we,out=self.state
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg,panel,raised,fg,muted,accent,border=PALETTES[self.theme]
        p.fillRect(self.rect(),QColor(bg))
        scale=min(self.width()/660,self.height()/220)
        p.translate((self.width()-660*scale)/2,(self.height()-220*scale)/2)
        p.scale(scale,scale)
        p.setPen(QPen(QColor(fg),1.5))
        p.setBrush(QColor(panel))
        p.drawRect(QRectF(240,16,180,188))
        p.setFont(QFont("Segoe UI",13,QFont.Weight.Bold))
        p.drawText(QRectF(240,18,180,30),Qt.AlignmentFlag.AlignCenter,f"{chip.kind} {chip.size} × {chip.word_bits}")
        p.setFont(QFont("Consolas",11))
        rows=[(64,f"A[{chip.address_bits-1}:0]",f"{address:0{chip.address_bits//4}X}",True,False),
              (94,"CS̅",str(cs),False,True),(124,"OE̅",str(oe),False,True)]
        if chip.kind=="RAM":
            rows.extend([(154,"WE̅",str(we),False,True),(184,f"DIN[{chip.word_bits-1}:0]",f"{data:0{chip.word_bits//4}X}",True,False)])
        for y,name,value,bus,low in rows:
            p.setPen(QPen(QColor(muted if low and value=="1" else accent),2.8 if bus else 1.3))
            p.drawLine(QPointF(150,y),QPointF(232 if low else 240,y))
            if low:
                p.setBrush(QColor(bg))
                p.setPen(QPen(QColor(fg),1.5))
                p.drawEllipse(QRectF(232,y-4,8,8))
            p.setPen(QColor(fg))
            p.drawText(QRectF(10,y-12,132,24),Qt.AlignmentFlag.AlignRight,value)
            p.drawText(QRectF(249,y-12,160,24),Qt.AlignmentFlag.AlignLeft,name)
        p.setPen(QPen(QColor(accent if out is not None else muted),2.8))
        p.drawLine(QPointF(420,94),QPointF(505,94))
        p.setPen(QColor(fg))
        p.drawText(QRectF(250,82,160,24),Qt.AlignmentFlag.AlignRight,f"Q[{chip.word_bits-1}:0]")
        p.drawText(QRectF(513,82,132,24),Qt.AlignmentFlag.AlignLeft,"Z" if out is None else f"{out:0{chip.word_bits//4}X}")
        p.end()

class MemoryView(QWidget):
    def __init__(self,theme,fa=False):
        super().__init__()
        self.fa=fa
        layout=QVBoxLayout(self)
        self.config=QComboBox()
        for kind in ("RAM","ROM"):
            for ab,wb in ((4,4),(4,8),(8,8)):
                self.config.addItem(f"{kind} · {1<<ab} × {wb}",(kind,ab,wb))
        self.config.setCurrentIndex(1)
        layout.addWidget(self.config)
        self.note=QLabel(self.t("Ideal memory, separate input/output buses. Checked control means logic 1 (inactive). Writes require Apply cycle. Changing organization resets the demonstration.","مدل ایده‌آل حافظه با گذرگاه‌های جداگانه ورودی و خروجی. تیک کنترل یعنی یک (غیرفعال). نوشتن با اعمال چرخه انجام می‌شود. تغییر سازمان حافظه، نمونه را بازنشانی می‌کند."))
        self.note.setWordWrap(True)
        layout.addWidget(self.note)
        row=QHBoxLayout()
        self.address=QSpinBox()
        self.address.setDisplayIntegerBase(16)
        self.data=QSpinBox()
        self.data.setDisplayIntegerBase(16)
        for title,widget in ((self.t("Address","آدرس"),self.address),(self.t("Input word","کلمه ورودی"),self.data)):
            row.addWidget(QLabel(title));row.addWidget(widget)
        self.cs=QCheckBox("CS̅")
        self.oe=QCheckBox("OE̅")
        self.we=QCheckBox("WE̅")
        self.we.setChecked(True)
        for check in (self.cs,self.oe,self.we):row.addWidget(check)
        cycle=QPushButton(self.t("Apply cycle","اعمال چرخه"))
        cycle.setObjectName("primary")
        cycle.clicked.connect(self.cycle)
        row.addWidget(cycle)
        layout.addLayout(row)
        self.diagram=MemoryDiagram(theme)
        layout.addWidget(self.diagram,1)
        self.summary=QLabel()
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        self.table=QTableWidget(0,3)
        self.table.setHorizontalHeaderLabels([self.t("Address","آدرس"),"HEX","BIN"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.cellClicked.connect(lambda row,col:self.address.setValue(row))
        layout.addWidget(self.table,2)
        self.config.currentIndexChanged.connect(self.load)
        for control in (self.address,self.data):control.valueChanged.connect(self.refresh)
        for control in (self.cs,self.oe,self.we):control.toggled.connect(self.refresh)
        self.load()
    def t(self,en,fa):return fa if self.fa else en
    def load(self,*_):
        self.chip=MemoryChip(*self.config.currentData())
        self.address.setRange(0,self.chip.size-1)
        self.data.setRange(0,self.chip.mask)
        self.address.setValue(0)
        self.data.setValue(0)
        self.we.setChecked(True)
        self.we.setEnabled(self.chip.kind=="RAM")
        self.data.setEnabled(self.chip.kind=="RAM")
        self.table.setRowCount(self.chip.size)
        self.update_cells()
        self.refresh()
    def signals(self):
        return (int(self.cs.isChecked()),int(self.oe.isChecked()),int(self.we.isChecked()))
    def refresh(self,*_):
        a=self.address.value()
        cs,oe,we=self.signals()
        out=self.chip.output(a,cs,oe,we)
        self.diagram.state=(self.chip,a,self.data.value(),cs,oe,we,out)
        self.diagram.update()
        labels={"READ":self.t("Read","خواندن"),"WRITE":self.t("Write pending","آماده نوشتن"),"IDLE":self.t("Output disabled","خروجی غیرفعال"),"DISABLED":self.t("Chip disabled","تراشه غیرفعال")}
        self.summary.setText(labels[self.chip.operation(cs,oe,we)]+"  ·  Q = "+("Z" if out is None else f"{out:0{self.chip.word_bits//4}X}"))
        self.table.selectRow(a)
    def update_cells(self):
        for row,word in enumerate(self.chip.words):
            for col,text in enumerate((f"{row:0{self.chip.address_bits//4}X}",f"{word:0{self.chip.word_bits//4}X}",f"{word:0{self.chip.word_bits}b}")):
                item=QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row,col,item)
    def cycle(self):
        access=self.chip.access(self.address.value(),*self.signals(),self.data.value())
        self.update_cells()
        self.refresh()
        if access.operation=="WRITE":
            self.summary.setText(self.t("Write completed","نوشتن انجام شد")+f" · M[{access.address:X}] = {access.after:X} · Q = Z")
