"""Bilingual four-stage floating arithmetic trace."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPlainTextEdit,
    QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView)
from floating_pipeline import FloatPipeline,parse_jobs,EXAMPLE


class FloatPipelineView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa;self.model=None
        layout=QVBoxLayout(self)
        note=QLabel(self.t("Binary16 ADD/SUB, four ideal stages. Each line: ADD or SUB and two raw 4-digit HEX words. Exact alignment; round to nearest, ties to even. Modern teaching format, not Mano's historical encoding.",
            "جمع و تفریق binary16 در چهار مرحله ایده‌آل. هر خط: ADD یا SUB و دو کلمه خام چهاررقمی هگز. هم‌ترازی دقیق و گردکردن به نزدیک‌ترین عدد زوج. قالب آموزشی مدرن، نه قالب تاریخی مانو."))
        note.setWordWrap(True);layout.addWidget(note)
        self.source=QPlainTextEdit(EXAMPLE);self.source.setMaximumHeight(85)
        self.source.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.source.setAccessibleName(self.t("Floating-point jobs","عملیات ممیز شناور"));layout.addWidget(self.source)
        row=QHBoxLayout()
        for en,fa_label,fn in (("Example","مثال",self.example),("Load / Reset","بارگذاری / بازنشانی",self.load),("Next cycle","چرخه بعد",self.step),("Run","اجرا",self.run)):
            b=QPushButton(self.t(en,fa_label));b.clicked.connect(fn);row.addWidget(b)
        layout.addLayout(row)
        self.summary=QLabel();self.summary.setWordWrap(True);layout.addWidget(self.summary)
        self.timeline=QTableWidget(0,5)
        self.timeline.setHorizontalHeaderLabels(["#",self.t("Compare exponents","مقایسه نماها"),self.t("Align","هم‌ترازی"),self.t("Add significands","جمع بخش معنادار"),self.t("Normalize / round","نرمال‌سازی / گردکردن")])
        self.timeline.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.timeline.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.timeline.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.timeline,1)
        self.output=QPlainTextEdit();self.output.setReadOnly(True);self.output.setMaximumHeight(70)
        self.output.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.output.setAccessibleName(self.t("Completed floating results","نتایج ممیز شناور"));layout.addWidget(self.output)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        self.source.textChanged.connect(self.invalidate)
        self.load()

    def t(self,en,fa):return fa if self.fa else en

    def invalidate(self,*_):
        self.model=None;self.timeline.setRowCount(0);self.output.clear();self.summary.clear()
        self.status.setText(self.t("Source changed. Load again.","متن تغییر کرد؛ دوباره بارگذاری کنید."))

    def example(self):
        self.source.setPlainText(EXAMPLE);self.load()

    def load(self):
        self.invalidate()
        try:self.model=FloatPipeline(parse_jobs(self.source.toPlainText()))
        except ValueError as error:
            self.status.setText(self.t(str(error),"ورودی نامعتبر است؛ دستور و دو کلمه هگز را بررسی کنید."));return
        self.refresh();self.status.setText(self.t("Ready.","آماده."))

    def status_name(self,status):
        return {"exact":"دقیق","rounded":"گردشده","overflow":"سرریز","invalid":"نامعتبر","nan":"NaN","infinity":"بی‌نهایت"}.get(status,status) if self.fa else status

    def refresh(self):
        m=self.model
        speed=f"{4*len(m.jobs)/m.cycles:.2f}×" if m.done else "—"
        self.summary.setText(self.t("Cycles","چرخه")+f": {m.cycles} | "+self.t("Completed","تکمیل‌شده")+f": {len(m.results)}/{len(m.jobs)} | "+self.t("Speedup vs serial 4 stages","شتاب نسبت به چهار مرحله ترتیبی")+f": {speed}")
        self.output.setPlainText("\n".join(f"#{r.summed.aligned.compared.number}: {r.result.word:04X} | {self.status_name(r.result.status)}" for r in m.results))

    def step(self):
        if self.model is None:return
        r=self.model.step()
        if r is None:return
        special=self.t("special","حالت ویژه")
        c,a,s,f=r.compare,r.align,r.add,r.round
        cells=[str(r.number)]
        cells.append(f"#{c.number} {c.job.op} "+(f"e={c.exponent}, Δ={c.shifts}" if c.exponent is not None else special) if c else "—")
        cells.append(f"#{a.compared.number} "+(f"{a.left}, {a.right}" if a.left is not None else special) if a else "—")
        cells.append(f"#{s.aligned.compared.number} "+(f"{s.significand} → {s.exact}" if s.exact is not None else special) if s else "—")
        cells.append(f"#{f.summed.aligned.compared.number} {f.result.word:04X} | {self.status_name(f.result.status)}" if f else "—")
        row=self.timeline.rowCount();self.timeline.insertRow(row)
        for col,value in enumerate(cells):
            item=QTableWidgetItem(value);item.setToolTip(value)
            self.timeline.setItem(row,col,item)
        self.timeline.scrollToBottom();self.refresh()
        self.status.setText(self.t("Complete.","تکمیل شد.") if self.model.done else "")

    def run(self):
        if self.model is None:return
        while not self.model.done:self.step()
