"""Bank conflict and throughput inspector, driven by actual memory cycles."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPlainTextEdit,QComboBox,
    QSpinBox,QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView)
from memory_interleaving import Interleaving,parse_requests


class InterleavingView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa;self.model=None
        layout=QVBoxLayout(self)
        note=QLabel(self.t("One request issues per clock; independent banks stay busy for the selected latency. HEX address = read; address:word = write. 16 words per bank, 16-bit data.",
            "در هر چرخه یک درخواست صادر می‌شود؛ بانک‌ها به مدت تأخیر انتخابی مشغول‌اند. آدرس هگز برای خواندن و آدرس:کلمه برای نوشتن. هر بانک ۱۶ کلمه ۱۶ بیتی."))
        note.setWordWrap(True);layout.addWidget(note)
        row=QHBoxLayout()
        self.banks=QComboBox()
        for n in (1,2,4):self.banks.addItem(str(n),n)
        self.banks.setCurrentIndex(2)
        self.mapping=QComboBox()
        self.mapping.addItem(self.t("Low-order interleaved","درهم‌تنیده با بیت کم‌ارزش"),True)
        self.mapping.addItem(self.t("High-order contiguous banks","بانک‌های پیوسته با بیت پرارزش"),False)
        self.latency=QSpinBox();self.latency.setRange(1,16);self.latency.setValue(4)
        for en,fa_label,widget in (("Banks","بانک‌ها",self.banks),("Mapping","نگاشت",self.mapping),("Latency","تأخیر",self.latency)):
            row.addWidget(QLabel(self.t(en,fa_label)));row.addWidget(widget)
        layout.addLayout(row)
        self.requests=QPlainTextEdit("00:000A 01:000B 02:000C 03:000D 00 01 02 03")
        self.requests.setLayoutDirection(Qt.LayoutDirection.LeftToRight);self.requests.setMaximumHeight(70)
        self.requests.setAccessibleName(self.t("Memory requests","درخواست‌های حافظه"));layout.addWidget(self.requests)
        row=QHBoxLayout()
        for en,fa_label,fn in (("Sequential example","مثال متوالی",self.sequential),("Stride example","مثال گام‌دار",self.strided),("Load / Reset","بارگذاری / بازنشانی",self.load),("Next cycle","چرخه بعد",self.step),("Run","اجرا",self.run)):
            b=QPushButton(self.t(en,fa_label));b.clicked.connect(fn);row.addWidget(b)
        layout.addLayout(row)
        self.summary=QLabel();self.summary.setWordWrap(True);layout.addWidget(self.summary)
        self.timeline=QTableWidget(0,0)
        self.timeline.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.timeline.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.timeline.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.timeline,1)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        self.requests.textChanged.connect(self.invalidate)
        self.banks.currentIndexChanged.connect(self.invalidate);self.mapping.currentIndexChanged.connect(self.invalidate)
        self.latency.valueChanged.connect(self.invalidate)
        self.load()

    def t(self,en,fa):return fa if self.fa else en

    def invalidate(self,*_):
        self.model=None;self.timeline.setRowCount(0);self.summary.clear()
        self.status.setText(self.t("Settings changed. Load again.","تنظیمات تغییر کرد؛ دوباره بارگذاری کنید."))

    def sequential(self):
        self.requests.setPlainText(" ".join(f"{n:02X}" for n in range(16)));self.load()

    def strided(self):
        n=self.banks.currentData()
        self.requests.setPlainText(" ".join(f"{i*n:02X}" for i in range(16)));self.load()

    def load(self):
        self.invalidate()
        try:self.model=Interleaving(parse_requests(self.requests.toPlainText()),self.banks.currentData(),self.latency.value(),self.mapping.currentData())
        except ValueError as e:
            self.status.setText(self.t(str(e),"درخواست یا آدرس حافظه نامعتبر است."));return
        count=self.banks.currentData()
        self.timeline.setColumnCount(count+3)
        self.timeline.setHorizontalHeaderLabels(["#",self.t("Issue / stall","صدور / توقف")]+[f"B{i}" for i in range(count)]+[self.t("Completed","تکمیل‌شده")])
        self.refresh();self.status.setText(self.t("Ready.","آماده."))

    def refresh(self):
        m=self.model
        speed=f"{len(m.requests)*m.latency/m.cycles:.2f}×" if m.done else "—"
        self.summary.setText(self.t("Cycles","چرخه")+f": {m.cycles} | "+self.t("Bank stalls","توقف بانک")+f": {m.stalls} | "+self.t("Completed","تکمیل‌شده")+f": {len(m.results)}/{len(m.requests)} | "+self.t("Speedup vs serial","شتاب نسبت به ترتیبی")+f": {speed}")

    def step(self):
        if self.model is None:return
        c=self.model.step()
        if c is None:return
        issue=f"#{c.issued.number} → B{c.issued.bank}" if c.issued else self.t("Stall ","توقف ")+f"B{c.stalled_bank}" if c.stalled_bank is not None else "—"
        active=[f"#{a.number} @ {a.local:X}" if a else "—" for a in c.active]
        done=", ".join(f"#{r.access.number}: {r.value:04X}" for r in c.completed) or "—"
        row=self.timeline.rowCount();self.timeline.insertRow(row)
        for col,value in enumerate([str(c.number),issue]+active+[done]):
            self.timeline.setItem(row,col,QTableWidgetItem(value))
        self.timeline.scrollToBottom();self.refresh()
        self.status.setText(self.t("Complete.","تکمیل شد.") if self.model.done else "")

    def run(self):
        if self.model is None:return
        while not self.model.done:self.step()
