"""Executable comparison of address-count instruction formats."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QSpinBox,
    QComboBox,QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView)
from expression_machine import evaluate_expression
from word_arithmetic import signed


class ExpressionView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa;self.result=None
        layout=QVBoxLayout(self)
        note=QLabel(self.t("Educational pseudo-instructions, not binary ISA encodings. 16-bit words wrap; division is signed, toward zero. Enter A–D and decimal literals, binary + − * / and parentheses.",
            "شبه‌دستور آموزشی، نه کد باینری ISA. کلمات ۱۶ بیتی دور می‌زنند؛ تقسیم علامت‌دار به سمت صفر است. از A تا D، اعداد ده‌دهی، عملگرهای دودویی و پرانتز استفاده کنید."))
        note.setWordWrap(True);layout.addWidget(note)
        row=QHBoxLayout()
        self.expression=QLineEdit("(A+B)*(C-D)")
        self.expression.setMaxLength(512);self.expression.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.expression.setAccessibleName(self.t("Expression","عبارت"));row.addWidget(self.expression,1)
        self.format=QComboBox()
        for n in range(4):self.format.addItem(f"{n} "+self.t("address","آدرسی"),n)
        row.addWidget(self.format)
        button=QPushButton(self.t("Evaluate","محاسبه"));button.clicked.connect(self.evaluate);row.addWidget(button)
        layout.addLayout(row)
        row=QHBoxLayout();self.operands={}
        for key,value in zip("ABCD",(5,3,9,2)):
            box=QSpinBox();box.setRange(0,65535);box.setDisplayIntegerBase(16);box.setValue(value)
            self.operands[key]=box;row.addWidget(QLabel(key+" HEX"));row.addWidget(box)
            box.valueChanged.connect(self.clear)
        layout.addLayout(row)
        self.summary=QLabel();self.summary.setWordWrap(True);layout.addWidget(self.summary)
        self.trace=QTableWidget(0,4)
        self.trace.setHorizontalHeaderLabels([self.t("Instruction","دستور"),"AC",self.t("Stack bottom → top","پشته پایین به بالا"),self.t("Writes","نوشتن")])
        self.trace.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.trace.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.trace.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.trace,1)
        self.expression.textChanged.connect(self.clear)
        self.format.currentIndexChanged.connect(self.clear)
        self.evaluate()

    def t(self,en,fa):return fa if self.fa else en

    def clear(self,*_):
        self.result=None
        if hasattr(self,"trace"):self.trace.setRowCount(0);self.summary.clear()

    def evaluate(self):
        self.clear()
        try:r=evaluate_expression(self.expression.text(),{k:b.value() for k,b in self.operands.items()},self.format.currentData())
        except ValueError as e:
            self.summary.setText(self.t(str(e),"عبارت نامعتبر یا تقسیم بر صفر."));return
        self.result=r
        self.summary.setText("Postfix: "+" ".join(r.postfix)+f" | RESULT={r.word:04X} ({signed(r.word,16)}) | "+self.t("Instructions","دستورها")+f": {len(r.program)}")
        self.trace.setRowCount(len(r.steps))
        for row,step in enumerate(r.steps):
            values=(step.instruction[0]+" "+", ".join(step.instruction[1:]),
                    f"{step.accumulator:04X}" if self.format.currentData()==1 else "—",
                    " ".join(f"{v:04X}" for v in step.stack) or "—",
                    ", ".join(f"{k}={v:04X}" for k,v in step.writes) or "—")
            for col,value in enumerate(values):self.trace.setItem(row,col,QTableWidgetItem(value))
