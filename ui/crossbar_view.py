"""Live crosspoint matrix, one transaction-level model, no fictitious paths."""
from PySide6.QtCore import Qt,QRectF,QPointF
from PySide6.QtGui import QPainter,QColor,QPen,QFont
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QSpinBox,
    QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView)
from multiprocessor import Crossbar
from ui.theme import PALETTES


class CrossbarCanvas(QWidget):
    def __init__(self,view):
        super().__init__(view);self.view=view;self.setMinimumHeight(265)
        self.setAccessibleName(view.t("Crossbar grant matrix","ماتریس مجوز اتصال متقاطع"))

    def paintEvent(self,event):
        v=self.view;m=v.model;e=v.last
        bg,panel,raised,fg,muted,accent,border=PALETTES[v.theme]
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);p.fillRect(self.rect(),QColor(bg))
        scale=min(self.width()/800,self.height()/290)
        p.translate((self.width()-800*scale)/2,(self.height()-290*scale)/2);p.scale(scale,scale)
        def label(x,y,w,h,s,size=13,color=fg):
            font=QFont("Consolas");font.setPixelSize(size);p.setFont(font);p.setPen(QColor(color))
            p.drawText(QRectF(x,y,w,h),Qt.AlignmentFlag.AlignCenter,s)
        def line(x,y,x2,y2,active=False):
            p.setPen(QPen(QColor(accent if active else border),2.8 if active else 1.2))
            p.drawLine(QPointF(x,y),QPointF(x2,y2))
        def tile(x,y,w,h,active=False):
            p.setPen(QPen(QColor(accent if active else border),1.5));p.setBrush(QColor(raised if active else panel))
            p.drawRoundedRect(QRectF(x,y,w,h),8,8)
        grants={(t.master,t.bank):t for t in e.transfers} if e else {}
        requests={(i,r.address//16) for i,r in enumerate(e.heads) if r is not None} if e else set()
        for i in range(4):
            y=79+i*53
            tile(10,y-21,143,42,any(a==i for a,b in grants))
            label(10,y-20,143,20,f"P{i}  Q:{len(m.queues[i])}",15)
            label(10,y,143,20,v.t("WAIT","انتظار")+f" {m.waited[i]}",12,muted)
            line(153,y,710,y)
        for bank in range(4):
            x=215+bank*145
            tile(x-57,5,114,45,any(b==bank for a,b in grants))
            label(x-57,5,114,22,f"B{bank} RAM",14)
            label(x-57,26,114,20,f"{bank*16:02X}–{bank*16+15:02X}",12,muted)
            line(x,50,x,252)
        for (master,bank),transfer in grants.items():
            x=215+bank*145;y=79+master*53
            line(153,y,x,y,True);line(x,y,x,50,True)
        # Crosspoints are switches, not junction dots: only granted ones close.
        for master in range(4):
            for bank in range(4):
                x=215+bank*145;y=79+master*53
                granted=(master,bank) in grants;requested=(master,bank) in requests
                p.setPen(QPen(QColor(accent if granted else fg if requested else border),2 if granted else 1))
                p.setBrush(QColor(accent if granted else panel))
                p.drawRoundedRect(QRectF(x-7,y-7,14,14),3,3)
                if requested and not granted:label(x+9,y-12,42,22,v.t("REQ","درخواست"),9,muted)
        label(10,260,780,24,v.t("Closed switch = granted · outlined request = waiting","کلید بسته = مجوز · درخواست بدون مجوز = انتظار"),13,muted)
        p.end()


class CrossbarView(QWidget):
    def __init__(self,theme="dark",fa=False):
        super().__init__();self.theme=theme;self.fa=fa
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if fa else Qt.LayoutDirection.LeftToRight)
        self.model=Crossbar();self.last=None
        layout=QVBoxLayout(self)
        self.note=QLabel(self.t("Four independent memory banks; up to four transfers per clock. Each master offers only its queue head. Compare conflicts and independent grants.",
            "چهار بانک حافظه مستقل؛ حداکثر چهار انتقال در هر چرخه. هر پردازنده فقط سر صف خود را عرضه می‌کند. تداخل درخواست‌ها و مجوزهای مستقل را مقایسه کنید."))
        self.note.setWordWrap(True);layout.addWidget(self.note)
        row=QHBoxLayout();self.policy=QComboBox()
        self.policy.addItem(self.t("Rotating priority","اولویت چرخشی"),"rotating")
        self.policy.addItem(self.t("Fixed priority","اولویت ثابت"),"fixed");row.addWidget(self.policy)
        self.demo=QComboBox()
        self.demo.addItem(self.t("Independent banks","بانک‌های مستقل"),"parallel")
        self.demo.addItem(self.t("One bank conflict","تداخل در یک بانک"),"conflict");row.addWidget(self.demo)
        for en,fa_label,fn in (("Load example","بارگذاری مثال",self.example),("Reset","بازنشانی",self.reset),("Next clock","چرخه بعد",self.step),("Run queued","اجرای صف",self.run)):
            b=QPushButton(self.t(en,fa_label));b.clicked.connect(fn);row.addWidget(b)
        layout.addLayout(row)
        row=QHBoxLayout();self.master=QSpinBox();self.master.setRange(0,3)
        self.address=QSpinBox();self.address.setRange(0,63);self.address.setDisplayIntegerBase(16)
        self.value=QSpinBox();self.value.setRange(0,65535);self.value.setDisplayIntegerBase(16)
        for label,w in (("P",self.master),("AR HEX",self.address),("DATA HEX",self.value)):
            w.setLayoutDirection(Qt.LayoutDirection.LeftToRight);row.addWidget(QLabel(label));row.addWidget(w)
        for en,fa_label,write in (("Queue read","صف خواندن",False),("Queue write","صف نوشتن",True)):
            b=QPushButton(self.t(en,fa_label));b.clicked.connect(lambda checked=False,w=write:self.enqueue(w));row.addWidget(b)
        layout.addLayout(row)
        self.canvas=CrossbarCanvas(self);self.canvas.setLayoutDirection(Qt.LayoutDirection.LeftToRight);layout.addWidget(self.canvas,1)
        self.stats=QLabel();self.stats.setWordWrap(True);layout.addWidget(self.stats)
        self.trace=QTableWidget(0,4)
        self.trace.setHorizontalHeaderLabels([self.t("Clock","چرخه"),self.t("Grants","مجوزها"),self.t("Transfers","انتقال‌ها"),self.t("Waiting","انتظار")])
        self.trace.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.trace.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.trace.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.trace.horizontalHeader().setStretchLastSection(True);layout.addWidget(self.trace,1)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        self.policy.currentIndexChanged.connect(self.reset);self.example()

    def t(self,en,fa):return fa if self.fa else en
    def reset(self,*_):
        self.model=Crossbar(self.policy.currentData());self.last=None;self.trace.setRowCount(0);self.status.clear();self.refresh()
    def example(self):
        self.reset()
        for i in range(4):
            address=i*16 if self.demo.currentData()=="parallel" else i
            self.model.enqueue(i,address,0x100+i);self.model.enqueue(i,address)
        self.refresh()
    def enqueue(self,write):
        try:self.model.enqueue(self.master.value(),self.address.value(),self.value.value() if write else None)
        except ValueError:self.status.setText(self.t("Request queue is full.","صف درخواست پر است."));return
        self.status.clear();self.refresh()
    def refresh(self):
        m=self.model;total=sum(m.served)
        rate=total/m.cycles if m.cycles else 0
        self.stats.setText(self.t("Clocks","چرخه‌ها")+f" {m.cycles} · "+self.t("Transfers","انتقال‌ها")+f" {total} · "+
            self.t("Transfers/clock","انتقال در چرخه")+f" {rate:.2f} · "+self.t("Per-bank grants","مجوز هر بانک")+": "+", ".join(f"B{i}={n}" for i,n in enumerate(m.bank_served)))
        self.canvas.update()
    def step(self):
        e=self.last=self.model.step()
        grants=", ".join(f"P{t.master}→B{t.bank}" for t in e.transfers) or "—"
        operations=" | ".join(f"{'R' if t.request.value is None else 'W'}[{t.request.address:02X}]={t.value:04X}" for t in e.transfers) or "—"
        values=(e.number,grants,operations,", ".join(f"P{i}" for i in e.waiting) or "—")
        if self.trace.rowCount()>=512:self.trace.removeRow(0)
        row=self.trace.rowCount();self.trace.insertRow(row)
        for col,value in enumerate(values):self.trace.setItem(row,col,QTableWidgetItem(str(value)))
        self.trace.scrollToBottom();self.refresh()
    def run(self):
        while not self.model.done:self.step()
