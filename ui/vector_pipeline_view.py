"""Interactive vector/matrix arithmetic using actual three-stage records."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPlainTextEdit,QComboBox,
    QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView)
from vector_pipeline import parse_matrix,build_pipeline
from word_arithmetic import signed


class VectorPipelineView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa;self.model=None
        layout=QVBoxLayout(self)
        note=QLabel(self.t("Ideal three-stage LOAD → MUL → ADD/ACC, 16-bit modular integers. Matrix rows on separate lines; vector inputs are single rows. One job per cycle; no memory or floating-point latency.",
            "خط لوله ایده‌آل سه‌مرحله‌ای بارگذاری، ضرب و جمع/انباشت؛ اعداد صحیح ۱۶ بیتی. هر سطر ماتریس در یک خط و بردار در یک سطر. یک ورودی در هر چرخه؛ بدون تأخیر حافظه یا ممیز شناور."))
        note.setWordWrap(True);layout.addWidget(note)
        row=QHBoxLayout()
        self.mode=QComboBox()
        for key,en,fa_label in (("mac","A × B + C","ضرب و جمع"),("add","Vector add","جمع برداری"),
            ("sub","Vector subtract","تفریق برداری"),("mul","Vector multiply","ضرب عضو به عضو"),
            ("dot","Dot product","ضرب داخلی"),("matrix","Matrix product","ضرب ماتریسی")):
            self.mode.addItem(self.t(en,fa_label),key)
        row.addWidget(self.mode)
        for en,fa_label,fn in (("Example","مثال",self.example),("Load / Reset","بارگذاری / بازنشانی",self.load),
            ("Next cycle","چرخه بعد",self.step),("Run","اجرا",self.run)):
            b=QPushButton(self.t(en,fa_label));b.clicked.connect(fn);row.addWidget(b)
        layout.addLayout(row)
        row=QHBoxLayout();self.inputs=[]
        for name in ("A","B","C"):
            col=QVBoxLayout();col.addWidget(QLabel(name))
            edit=QPlainTextEdit();edit.setMaximumHeight(75);edit.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            edit.setAccessibleName(name);col.addWidget(edit);row.addLayout(col);self.inputs.append(edit)
            edit.textChanged.connect(self.invalidate)
        layout.addLayout(row)
        self.summary=QLabel();self.summary.setWordWrap(True);layout.addWidget(self.summary)
        self.trace=QTableWidget(0,5)
        self.trace.setHorizontalHeaderLabels(["#",self.t("LOAD","بارگذاری"),"MUL","ADD / ACC",self.t("Result","نتیجه")])
        self.trace.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.trace.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.trace.setLayoutDirection(Qt.LayoutDirection.LeftToRight);layout.addWidget(self.trace,1)
        self.output=QPlainTextEdit();self.output.setReadOnly(True);self.output.setMaximumHeight(65)
        self.output.setLayoutDirection(Qt.LayoutDirection.LeftToRight);layout.addWidget(self.output)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        self.mode.currentIndexChanged.connect(self.mode_changed)
        self.example()

    def t(self,en,fa):return fa if self.fa else en

    def invalidate(self,*_):
        self.model=None
        if hasattr(self,"trace"):
            self.trace.setRowCount(0);self.summary.clear();self.output.clear()
            self.status.setText(self.t("Inputs changed. Load again.","ورودی تغییر کرد؛ دوباره بارگذاری کنید."))

    def mode_changed(self,*_):
        self.inputs[2].setEnabled(self.mode.currentData()=="mac")
        self.invalidate()

    def example(self):
        texts=("1 2 3\n4 5 6","7 8\n9 10\n11 12","") if self.mode.currentData()=="matrix" else ("1 2 3 4","5 6 7 8","1 1 1 1")
        for edit,text in zip(self.inputs,texts):edit.setPlainText(text)
        self.mode_changed();self.load()

    def load(self):
        self.invalidate()
        try:
            mode=self.mode.currentData()
            a,b=(parse_matrix(edit.toPlainText()) for edit in self.inputs[:2])
            c=parse_matrix(self.inputs[2].toPlainText()) if mode=="mac" else None
            self.model=build_pipeline(mode,a,b,c)
        except ValueError as e:
            self.status.setText(self.t(str(e),"ورودی یا ابعاد نامعتبر است."));return
        self.refresh();self.status.setText(self.t("Ready.","آماده."))

    def refresh(self):
        m=self.model
        speed=f"{3*len(m.jobs)/m.cycles:.2f}×" if m.done else "—"
        self.summary.setText(self.t("Cycles","چرخه")+f": {m.cycles} | "+self.t("Jobs","عملیات")+f": {len(m.jobs)} | "+self.t("Speedup vs serial 3 stages","شتاب نسبت به سه مرحله ترتیبی")+f": {speed}")
        self.output.setPlainText("\n".join(" ".join(str(signed(v,16)) for v in row) for row in m.output()))

    def step(self):
        if self.model is None:return
        r=self.model.step()
        if r is None:return
        def index(job):return "["+",".join(str(i+1) for i in job.index)+"]"
        values=(str(r.number),f"{index(r.load)} {r.load.a:04X}, {r.load.b:04X}, {r.load.c:04X}" if r.load else "—",
            f"{index(r.multiply.job)} = {r.multiply.value:04X}" if r.multiply else "—",
            f"{index(r.accumulate.job)} {r.before:04X}+{r.accumulate.value:04X}+{r.accumulate.job.c:04X}" if r.accumulate else "—",
            f"{r.after:04X}" if r.after is not None else "—")
        row=self.trace.rowCount();self.trace.insertRow(row)
        for col,value in enumerate(values):self.trace.setItem(row,col,QTableWidgetItem(value))
        self.trace.scrollToBottom();self.refresh()
        self.status.setText(self.t("Complete.","تکمیل شد.") if self.model.done else "")

    def run(self):
        if self.model is None:return
        while not self.model.done:self.step()
