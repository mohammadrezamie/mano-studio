"""Live four-master shared bus: real grant, queues and memory transactions."""
from PySide6.QtCore import Qt,QRectF,QPointF
from PySide6.QtGui import QPainter,QColor,QPen,QFont
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QSpinBox,
    QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView)
from multiprocessor import SharedBus
from ui.theme import PALETTES


class BusCanvas(QWidget):
    def __init__(self,view):
        super().__init__(view);self.view=view
        self.setMinimumHeight(210)
        self.setAccessibleName(view.t("Shared bus grant diagram","نمودار مجوز گذرگاه مشترک"))

    def paintEvent(self,event):
        v=self.view;m=v.model;e=v.last
        bg,panel,raised,fg,muted,accent,border=PALETTES[v.theme]
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(),QColor(bg))
        scale=min(self.width()/800,self.height()/220)
        p.translate((self.width()-800*scale)/2,(self.height()-220*scale)/2);p.scale(scale,scale)
        def box(x,y,w,h,active=False):
            p.setPen(QPen(QColor(accent if active else border),2 if active else 1))
            p.setBrush(QColor(raised if active else panel));p.drawRoundedRect(QRectF(x,y,w,h),10,10)
        def text(x,y,w,h,s,size=14,color=fg):
            font=QFont("Segoe UI");font.setPixelSize(size);p.setFont(font);p.setPen(QColor(color))
            p.drawText(QRectF(x,y,w,h),Qt.AlignmentFlag.AlignCenter,s)
        def line(x,y,x2,y2,on=False):
            p.setPen(QPen(QColor(accent if on else border),3 if on else 1.4));p.drawLine(QPointF(x,y),QPointF(x2,y2))
        grant=e.grant if e else None
        for i in range(4):
            x=20+195*i;cx=x+87
            box(x,10,174,65,grant==i)
            text(x,15,174,23,f"P{i}",19,accent if grant==i else fg)
            text(x,39,174,28,v.t("Queued","در صف")+f" {len(m.queues[i])}  ·  "+v.t("Served","سرویس")+f" {m.served[i]}",13,muted)
            line(cx,75,cx,110,grant==i)
        line(107,110,692,110,grant is not None)
        line(400,110,400,145,grant is not None)
        text(20,115,760,24,v.t("SHARED BUS · ONE OWNER","گذرگاه مشترک · یک مالک"),13,muted)
        box(245,145,310,65,grant is not None)
        text(245,150,310,24,"RAM 64 × 16",17)
        result="—" if grant is None else f"{'R' if e.request.value is None else 'W'}  [{e.request.address:02X}] = {e.value:04X}"
        text(245,175,310,24,result,16,accent)
        p.end()


class MultiprocessorView(QWidget):
    def __init__(self,theme="dark",fa=False):
        super().__init__();self.theme=theme;self.fa=fa;self.model=SharedBus();self.last=None
        layout=QVBoxLayout(self)
        note=QLabel(self.t("Four independent masters, one shared memory. Each clock grants at most one queued word request. Compare fixed priority and rotating priority; this is an ideal transaction-level bus.",
            "چهار پردازنده مستقل، یک حافظه مشترک. هر چرخه حداکثر یک درخواست کلمه مجوز می‌گیرد. اولویت ثابت و چرخشی را مقایسه کنید؛ مدل ایده‌آل سطح تراکنش."))
        note.setWordWrap(True);layout.addWidget(note)
        row=QHBoxLayout();self.policy=QComboBox()
        self.policy.addItem(self.t("Rotating priority","اولویت چرخشی"),"rotating")
        self.policy.addItem(self.t("Fixed priority","اولویت ثابت"),"fixed")
        row.addWidget(self.policy)
        for en,fa_label,fn in (("Example","مثال",self.example),("Reset","بازنشانی",self.reset),("Next clock","چرخه بعد",self.step),("Run queued","اجرای صف",self.run)):
            b=QPushButton(self.t(en,fa_label));b.clicked.connect(fn);row.addWidget(b)
        layout.addLayout(row)
        row=QHBoxLayout();self.master=QSpinBox();self.master.setRange(0,3)
        self.address=QSpinBox();self.address.setRange(0,63);self.address.setDisplayIntegerBase(16)
        self.value=QSpinBox();self.value.setRange(0,65535);self.value.setDisplayIntegerBase(16)
        for name,w in (("P",self.master),("AR HEX",self.address),("DATA HEX",self.value)):
            w.setLayoutDirection(Qt.LayoutDirection.LeftToRight);row.addWidget(QLabel(name));row.addWidget(w)
        for en,fa_label,write in (("Queue read","صف خواندن",False),("Queue write","صف نوشتن",True)):
            b=QPushButton(self.t(en,fa_label));b.clicked.connect(lambda checked=False,w=write:self.enqueue(w));row.addWidget(b)
        layout.addLayout(row)
        self.canvas=BusCanvas(self);layout.addWidget(self.canvas,1)
        self.state=QLabel();self.state.setWordWrap(True);layout.addWidget(self.state)
        self.trace=QTableWidget(0,6);self.trace.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.trace.setHorizontalHeaderLabels(["#",self.t("Requests","درخواست‌ها"),self.t("Priority","اولویت"),self.t("Grant","مجوز"),self.t("Transfer","انتقال"),self.t("Waiting","انتظار")])
        self.trace.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.trace.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch);layout.addWidget(self.trace,1)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        self.policy.currentIndexChanged.connect(self.reset)
        self.example()

    def t(self,en,fa):return fa if self.fa else en
    def reset(self,*_):
        self.model=SharedBus(self.policy.currentData());self.last=None;self.trace.setRowCount(0);self.status.clear();self.refresh()
    def example(self):
        self.reset()
        for i in range(4):
            self.model.enqueue(i,i,0x100+i)
            self.model.enqueue(i,i)
        self.refresh()
    def enqueue(self,write):
        try:self.model.enqueue(self.master.value(),self.address.value(),self.value.value() if write else None)
        except ValueError:self.status.setText(self.t("Queue full.","صف پر است."));return
        self.status.clear();self.refresh()
    def refresh(self):
        m=self.model
        self.state.setText(self.t("Clock","چرخه")+f" {m.cycles}  ·  "+self.t("Waiting clocks by master","چرخه‌های انتظار هر پردازنده")+": "+", ".join(f"P{i}={n}" for i,n in enumerate(m.waited)))
        self.canvas.update()
    def step(self):
        e=self.last=self.model.step()
        operation="—" if e.grant is None else f"{'R' if e.request.value is None else 'W'} [{e.request.address:02X}] = {e.value:04X}"
        values=(str(e.number),str(e.pending)," → ".join(map(str,e.order)),"—" if e.grant is None else f"P{e.grant}",operation,", ".join(f"P{i}" for i in e.waiting) or "—")
        if self.trace.rowCount()>=512:self.trace.removeRow(0)
        row=self.trace.rowCount();self.trace.insertRow(row)
        for i,s in enumerate(values):self.trace.setItem(row,i,QTableWidgetItem(s))
        self.trace.scrollToBottom();self.refresh()
    def run(self):
        while not self.model.done:self.step()
