"""Chapter 9 live cycle timeline and hazard statistics."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPlainTextEdit,QCheckBox,QComboBox,
    QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView)
from pipeline import Pipeline,parse_program,EXAMPLE


class PipelineView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa;self.model=None
        layout=QVBoxLayout(self)
        note=QLabel(self.t("Five-stage teaching pipeline, optional shared memory port; branches resolve in EX. Edit ADD/SUB/AND/OR/XOR, ADDI, LD/ST, BEQ or NOP. R0 is zero.",
            "خط لوله آموزشی پنج‌مرحله‌ای، درگاه مشترک حافظه اختیاری؛ پرش در EX تعیین می‌شود. دستورهای ADD/SUB/AND/OR/XOR، ADDI، LD/ST، BEQ یا NOP. ثبات R0 صفر است."))
        note.setWordWrap(True);layout.addWidget(note)
        self.source=QPlainTextEdit(EXAMPLE);self.source.setMaximumHeight(100)
        self.source.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.source)
        row=QHBoxLayout()
        self.forward=QCheckBox(self.t("Forwarding","ارسال مستقیم"));self.forward.setChecked(True);row.addWidget(self.forward)
        for en,fa_label,fn in [("Example","مثال",self.example),("Load / Reset","بارگذاری / بازنشانی",self.load),("Next cycle","چرخه بعد",self.step),("Run to end","اجرا تا پایان",self.run)]:
            b=QPushButton(self.t(en,fa_label));b.clicked.connect(fn);row.addWidget(b)
        layout.addLayout(row)
        row=QHBoxLayout()
        self.shared=QCheckBox(self.t("Shared memory port","درگاه مشترک حافظه"));row.addWidget(self.shared)
        self.predictor=QComboBox()
        for key,en,fa_label in (("not_taken","Always not taken","همیشه بدون پرش"),
                ("taken","Always taken","همیشه پرش"),("two_bit","Two-bit adaptive","تطبیقی دوبیتی")):
            self.predictor.addItem(self.t(en,fa_label),key)
        row.addWidget(QLabel(self.t("Branch predictor","پیش‌بینی پرش")));row.addWidget(self.predictor);row.addStretch()
        layout.addLayout(row)
        self.stats=QLabel();self.stats.setWordWrap(True);layout.addWidget(self.stats)
        self.timeline=QTableWidget(0,7)
        self.timeline.setHorizontalHeaderLabels(["#","IF","ID","EX","MEM","WB",self.t("Hazards","مخاطرات")])
        self.timeline.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.timeline.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.timeline.horizontalHeader().setStretchLastSection(True)
        self.timeline.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.timeline,1)
        self.state=QLabel();self.state.setWordWrap(True);layout.addWidget(self.state)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        self.source.textChanged.connect(self.invalidate);self.forward.toggled.connect(self.invalidate)
        self.shared.toggled.connect(self.invalidate);self.predictor.currentIndexChanged.connect(self.invalidate)
        self.load()

    def t(self,en,fa):return fa if self.fa else en

    def invalidate(self,*_):
        self.model=None;self.timeline.setRowCount(0);self.stats.clear();self.state.clear()
        self.status.setText(self.t("Settings changed. Load again.","تنظیمات تغییر کرد؛ دوباره بارگذاری کنید."))

    def example(self):
        self.source.setPlainText(EXAMPLE);self.load()

    def load(self):
        self.invalidate()
        try:self.model=Pipeline(parse_program(self.source.toPlainText()),self.forward.isChecked(),shared_port=self.shared.isChecked(),predictor=self.predictor.currentData())
        except ValueError as e:
            self.status.setText(self.t(str(e),"برنامه نامعتبر است؛ دستورها و برچسب‌ها را بررسی کنید."));return
        self.refresh();self.status.setText(self.t("Ready.","آماده."))

    def refresh(self):
        m=self.model
        speedup=f"{5*m.retired/m.cycles:.2f}×" if m.done and m.cycles else "—"
        self.stats.setText(self.t("Cycles","چرخه")+f": {m.cycles} | "+self.t("Retired","تکمیل‌شده")+f": {m.retired} | RAW: {m.stalls} | "+self.t("Structural","ساختاری")+f": {m.structural_stalls} | "+self.t("Mispredicted","پیش‌بینی نادرست")+f": {m.mispredictions}/{m.branches} | "+self.t("Flushed","حذف‌شده")+f": {m.flushes} | "+self.t("Speedup vs 5 cycles/instruction","شتاب نسبت به ۵ چرخه برای هر دستور")+f": {speedup}")
        self.state.setText(" · ".join(f"R{i}={v:04X}" for i,v in enumerate(m.registers))+"\n"+" · ".join(f"M[{a:04X}]={v:04X}" for a,v in sorted(m.memory.items())))

    def step(self):
        if not self.model:return
        try:r=self.model.step()
        except ValueError:
            self.status.setText(self.t("Cycle limit reached.","حد چرخه‌ها رسید."));return
        if r is None:return
        events=[]
        if r.stall:events.append(self.t("RAW stall","توقف RAW"))
        if r.structural:events.append(self.t("IF blocked by MEM","توقف IF به دلیل MEM"))
        if r.prediction:
            _,pred,actual,wrong=r.prediction
            events.append(f"BR {int(pred)}→{int(actual)} "+(self.t("miss","خطا") if wrong else self.t("hit","درست")))
        if r.flushed:events.append(self.t("Flush ","حذف ")+ ",".join(str(n+1) for n in r.flushed))
        if r.forwarded:events.append(self.t("Forward ","ارسال مستقیم ")+ ",".join(f"R{reg}←{stage}" for reg,_,stage in r.forwarded))
        row=self.timeline.rowCount();self.timeline.insertRow(row)
        values=[str(r.number)]+["—" if n is None else f"{n+1}: {self.model.program[n].op}" for n in r.stages]+[" · ".join(events) or "—"]
        for col,value in enumerate(values):self.timeline.setItem(row,col,QTableWidgetItem(value))
        self.timeline.scrollToBottom();self.refresh()
        self.status.setText(self.t("Complete.","تکمیل شد.") if self.model.done else "")

    def run(self):
        if not self.model:return
        while not self.model.done and self.model.cycles<512:self.step()
        if not self.model.done:self.status.setText(self.t("Cycle limit reached.","حد چرخه‌ها رسید."))
