"""Chapter 9 live cycle timeline and hazard statistics."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPlainTextEdit,QCheckBox,
    QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView)
from pipeline import Pipeline,parse_program,EXAMPLE


class PipelineView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa;self.model=None
        layout=QVBoxLayout(self)
        note=QLabel(self.t("Five-stage teaching pipeline, separate instruction/data memory; branches resolve in EX. Edit ADD/SUB/AND/OR/XOR, ADDI, LD/ST, BEQ or NOP. R0 is zero.",
            "خط لوله آموزشی پنج‌مرحله‌ای، حافظه دستور و داده جدا؛ پرش در EX تعیین می‌شود. دستورهای ADD/SUB/AND/OR/XOR، ADDI، LD/ST، BEQ یا NOP. ثبات R0 صفر است."))
        note.setWordWrap(True);layout.addWidget(note)
        self.source=QPlainTextEdit(EXAMPLE);self.source.setMaximumHeight(100)
        self.source.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.source)
        row=QHBoxLayout()
        self.forward=QCheckBox("Forwarding");self.forward.setChecked(True);row.addWidget(self.forward)
        for en,fa_label,fn in [("Example","مثال",self.example),("Load / Reset","بارگذاری / بازنشانی",self.load),("Next cycle","چرخه بعد",self.step),("Run to end","اجرا تا پایان",self.run)]:
            b=QPushButton(self.t(en,fa_label));b.clicked.connect(fn);row.addWidget(b)
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
        self.load()

    def t(self,en,fa):return fa if self.fa else en

    def invalidate(self,*_):
        self.model=None;self.timeline.setRowCount(0);self.stats.clear();self.state.clear()
        self.status.setText(self.t("Settings changed. Load again.","تنظیمات تغییر کرد؛ دوباره بارگذاری کنید."))

    def example(self):
        self.source.setPlainText(EXAMPLE);self.load()

    def load(self):
        self.invalidate()
        try:self.model=Pipeline(parse_program(self.source.toPlainText()),self.forward.isChecked())
        except ValueError as e:
            self.status.setText(self.t(str(e),"برنامه نامعتبر است؛ دستورها و برچسب‌ها را بررسی کنید."));return
        self.refresh();self.status.setText(self.t("Ready.","آماده."))

    def refresh(self):
        m=self.model
        speedup=f"{5*m.retired/m.cycles:.2f}×" if m.done and m.cycles else "—"
        self.stats.setText(self.t("Cycles","چرخه")+f": {m.cycles} | "+self.t("Retired","تکمیل‌شده")+f": {m.retired} | Stall: {m.stalls} | Flush: {m.flushes} | "+self.t("Speedup vs 5 cycles/instruction","شتاب نسبت به ۵ چرخه برای هر دستور")+f": {speedup}")
        self.state.setText(" · ".join(f"R{i}={v:04X}" for i,v in enumerate(m.registers))+"\n"+" · ".join(f"M[{a:04X}]={v:04X}" for a,v in sorted(m.memory.items())))

    def step(self):
        if not self.model:return
        try:r=self.model.step()
        except ValueError:
            self.status.setText(self.t("Cycle limit reached.","حد چرخه‌ها رسید."));return
        if r is None:return
        events=[]
        if r.stall:events.append("RAW stall")
        if r.flushed:events.append("Flush "+",".join(str(n+1) for n in r.flushed))
        if r.forwarded:events.append("Forward "+",".join(f"R{reg}←{stage}" for reg,_,stage in r.forwarded))
        row=self.timeline.rowCount();self.timeline.insertRow(row)
        values=[str(r.number)]+["—" if n is None else f"{n+1}: {self.model.program[n].op}" for n in r.stages]+[" · ".join(events) or "—"]
        for col,value in enumerate(values):self.timeline.setItem(row,col,QTableWidgetItem(value))
        self.timeline.scrollToBottom();self.refresh()
        self.status.setText(self.t("Complete.","تکمیل شد.") if self.model.done else "")

    def run(self):
        if not self.model:return
        while not self.model.done and self.model.cycles<512:self.step()
        if not self.model.done:self.status.setText(self.t("Cycle limit reached.","حد چرخه‌ها رسید."))
