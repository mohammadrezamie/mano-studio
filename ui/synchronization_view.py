"""Bilingual synchronization experiment using actual shared-word transitions."""
from PySide6.QtCore import Qt,QRectF,QPointF
from PySide6.QtGui import QColor,QPainter,QPen,QFont
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QSpinBox,
    QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView)
from synchronization import Synchronization
from ui.theme import PALETTES

PHASES={
    "acquire":("Acquire (TAS)","اخذ قفل (TAS)"),"wait":("Wait","انتظار"),
    "read":("Read","خواندن"),"increment":("Increment","افزایش"),
    "write":("Write","نوشتن"),"release":("Release","آزادسازی"),"done":("Done","پایان")
}


class SyncCanvas(QWidget):
    def __init__(self,view):
        super().__init__(view);self.view=view;self.setMinimumHeight(190)
        self.setAccessibleName(view.t("Shared word and lock ownership","کلمه مشترک و مالک قفل"))

    def paintEvent(self,event):
        v=self.view;m=v.model;e=m.events[-1] if m.events else None
        bg,panel,raised,fg,muted,accent,border=PALETTES[v.theme]
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);p.fillRect(self.rect(),QColor(bg))
        scale=min(self.width()/760,self.height()/205)
        p.translate((self.width()-760*scale)/2,(self.height()-205*scale)/2);p.scale(scale,scale)
        def tile(x,y,w,h,active=False):
            p.setPen(QPen(QColor(accent if active else border),2 if active else 1))
            p.setBrush(QColor(raised if active else panel));p.drawRoundedRect(QRectF(x,y,w,h),12,12)
        def text(x,y,w,h,value,size=14,color=fg,bold=False):
            font=QFont("Segoe UI");font.setPixelSize(size);font.setBold(bold);p.setFont(font);p.setPen(QColor(color))
            p.drawText(QRectF(x,y,w,h),Qt.AlignmentFlag.AlignCenter,value)
        for i,w in enumerate(m.workers):
            x=16+i*494
            tile(x,25,234,148,m.owner==i)
            text(x,31,234,28,f"P{i}",22,accent if m.owner==i else fg,True)
            text(x,65,234,25,v.phase(w.phase),16)
            text(x,99,234,25,"R = "+("—" if w.local is None else f"{w.local:04X}"),20,fg,True)
            text(x,138,234,24,v.t("Remaining","باقی‌مانده")+f" {w.remaining}",13,muted)
            active=e is not None and e.processor==i and e.action in ("read","write")
            p.setPen(QPen(QColor(accent if active else border),3 if active else 1.4))
            a,b=(250,284) if i==0 else (476,510)
            p.drawLine(QPointF(a,98),QPointF(b,98))
        tile(284,25,192,148,True)
        text(284,32,192,23,v.t("SHARED WORD","کلمه مشترک"),14,muted,True)
        text(284,58,192,45,f"{m.shared:04X}",33,fg,True)
        lock=v.t("Lock disabled","قفل غیرفعال") if not m.locked else v.t("Lock free","قفل آزاد") if m.owner is None else f"LOCK = P{m.owner}"
        text(284,110,192,25,lock,15,accent)
        text(284,140,192,23,v.t("Expected","مقدار مورد انتظار")+f" {m.expected:04X}",13,muted)
        p.end()


class SynchronizationView(QWidget):
    def __init__(self,theme="dark",fa=False):
        super().__init__();self.theme=theme;self.fa=fa
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if fa else Qt.LayoutDirection.LeftToRight)
        layout=QVBoxLayout(self)
        self.note=QLabel(self.t(
            "Two processors increment the same 16-bit word. Read, increment and write are separate events; atomic test-and-set protects the entire critical section. Compare the same alternating schedule with and without the lock.",
            "دو پردازنده یک کلمه ۱۶ بیتی مشترک را افزایش می‌دهند. خواندن، افزایش و نوشتن رویدادهای جداگانه‌اند؛ آزمون و تنظیم اتمی از کل بخش بحرانی محافظت می‌کند. زمان‌بندی نوبتی یکسان را با قفل و بدون قفل مقایسه کنید."))
        self.note.setWordWrap(True);layout.addWidget(self.note)
        row=QHBoxLayout();self.mode=QComboBox()
        self.mode.addItem(self.t("Atomic test-and-set","آزمون و تنظیم اتمی"),True)
        self.mode.addItem(self.t("No lock","بدون قفل"),False);row.addWidget(self.mode)
        self.repeats=QSpinBox();self.repeats.setRange(1,8)
        row.addWidget(QLabel(self.t("Increments / processor","افزایش برای هر پردازنده")));row.addWidget(self.repeats)
        self.initial=QSpinBox();self.initial.setRange(0,65535);self.initial.setDisplayIntegerBase(16)
        self.initial.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        row.addWidget(QLabel(self.t("Initial word (hex)","کلمه آغازین (هگز)")));row.addWidget(self.initial)
        reset=QPushButton(self.t("Reset","بازنشانی"));reset.clicked.connect(self.reset);row.addWidget(reset)
        layout.addLayout(row)
        row=QHBoxLayout();self.steps=[]
        for i in range(2):
            b=QPushButton(self.t("Step","گام")+f" P{i}");b.clicked.connect(lambda checked=False,n=i:self.step(n));self.steps.append(b);row.addWidget(b)
        self.run_button=QPushButton(self.t("Run alternating schedule","اجرای زمان‌بندی نوبتی"))
        self.run_button.clicked.connect(self.run);row.addWidget(self.run_button)
        layout.addLayout(row)
        self.canvas=SyncCanvas(self);self.canvas.setLayoutDirection(Qt.LayoutDirection.LeftToRight);layout.addWidget(self.canvas,1)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        self.trace=QTableWidget(0,7)
        self.trace.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.trace.setHorizontalHeaderLabels(["#","P",self.t("Event","رویداد"),self.t("Next","بعدی"),"R",self.t("Shared","مشترک"),self.t("Owner","مالک")])
        self.trace.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.trace.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch);layout.addWidget(self.trace,1)
        self.mode.currentIndexChanged.connect(self.reset)
        self.repeats.valueChanged.connect(self.reset);self.initial.valueChanged.connect(self.reset)
        self.reset()

    def t(self,en,fa):return fa if self.fa else en
    def phase(self,key):return PHASES[key][int(self.fa)]
    def reset(self,*_):
        self.model=Synchronization(self.mode.currentData(),self.repeats.value(),self.initial.value())
        self.trace.setRowCount(0);self.refresh()
    def refresh(self):
        m=self.model
        for i,b in enumerate(self.steps):b.setEnabled(m.workers[i].phase!="done")
        self.run_button.setEnabled(not m.done)
        state=self.t("Schedule in progress","زمان‌بندی در جریان است")
        if m.done:state=self.t("Correct result","نتیجه درست") if m.shared==m.expected else self.t("Lost update","به‌روزرسانی ازدست‌رفته")
        self.status.setText(state+f" · {m.shared:04X} / {m.expected:04X}")
        self.canvas.update()
    def step(self,processor):
        e=self.model.step(processor)
        if e is not None:
            values=(e.number,f"P{e.processor}",self.phase(e.action),self.phase(e.phase),
                    "—" if e.local is None else f"{e.local:04X}",f"{e.shared:04X}",
                    "—" if e.owner is None else f"P{e.owner}")
            if self.trace.rowCount()>=512:self.trace.removeRow(0)
            row=self.trace.rowCount();self.trace.insertRow(row)
            for i,value in enumerate(values):self.trace.setItem(row,i,QTableWidgetItem(str(value)))
            self.trace.scrollToBottom()
        self.refresh()
    def run(self):
        while not self.model.done:self.step(0);self.step(1)
