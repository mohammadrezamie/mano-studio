"""Integrated fixed-width representation and ALU workbench."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QLineEdit,
    QCheckBox,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView)
from word_arithmetic import WIDTHS,OPERATIONS,alu,parse_word,representations

class ArithmeticView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa
        self.result=None
        layout=QVBoxLayout(self)
        row=QHBoxLayout()
        row.addWidget(QLabel(self.t("Word width","طول کلمه")))
        self.width=QComboBox()
        for n in WIDTHS:self.width.addItem(f"{n} "+self.t("bit","بیت"),n)
        self.width.setCurrentIndex(self.width.findData(16))
        row.addWidget(self.width)
        row.addWidget(QLabel(self.t("Input base","مبنای ورودی")))
        self.base=QComboBox()
        for name,n in [("BIN",2),("OCT",8),("DEC",10),("HEX",16)]:self.base.addItem(name,n)
        self.base.setCurrentIndex(3)
        self.previous_base=16
        row.addWidget(self.base)
        self.op=QComboBox()
        self.op.addItems(OPERATIONS)
        self.op.insertItem(0,self.t("Convert bases","تبدیل مبنا"),"convert")
        self.op.setCurrentIndex(1)
        row.addWidget(self.op,1)
        self.cin=QCheckBox("Cin / E")
        row.addWidget(self.cin)
        layout.addLayout(row)
        row=QHBoxLayout()
        self.a=QLineEdit("7FFF")
        self.b=QLineEdit("0001")
        for name,edit in [("A",self.a),("B",self.b)]:
            row.addWidget(QLabel(name))
            edit.setMaxLength(32)
            edit.setAccessibleName(name)
            edit.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            row.addWidget(edit,1)
        layout.addLayout(row)
        self.representation=QTableWidget(3,6)
        self.representation.setHorizontalHeaderLabels([self.t("Word","کلمه"),"BIN","OCT","HEX",self.t("Unsigned","بدون علامت"),self.t("Signed","علامت‌دار")])
        self.representation.verticalHeader().hide()
        self.representation.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.representation.horizontalHeader().setStretchLastSection(True)
        self.representation.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.representation.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.representation.setMaximumHeight(132)
        layout.addWidget(self.representation)
        self.flags=QLabel()
        self.flags.setObjectName("section")
        self.flags.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.flags)
        self.note=QLabel(self.t("C: carry (SUB: no borrow). V: signed overflow. N: sign. Z: zero. Teaching flags are not extra Mano CPU registers.",
             "C: نقلی (در تفریق: بدون قرض). V: سرریز علامت‌دار. N: علامت. Z: صفر. این پرچم‌های آموزشی ثبات‌های اضافی مانو نیستند."))
        self.note.setWordWrap(True)
        layout.addWidget(self.note)
        self.stages=QTableWidget(0,6)
        self.stages.setHorizontalHeaderLabels([self.t("Bit","بیت"),"A","B′ / B","Cin",self.t("Sum","جمع"),"Cout"])
        self.stages.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.stages.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.stages.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.stages,1)
        self.status=QLabel()
        self.status.setWordWrap(True)
        self.status.setProperty("state","error")
        layout.addWidget(self.status)
        for control in (self.width,self.op):
            control.currentIndexChanged.connect(self.refresh)
        self.base.currentIndexChanged.connect(self.change_base)
        self.cin.toggled.connect(self.refresh)
        self.a.textChanged.connect(self.refresh)
        self.b.textChanged.connect(self.refresh)
        self.refresh()

    def t(self,en,fa):
        return fa if self.fa else en

    def change_base(self,*_):
        new=self.base.currentData()
        width=self.width.currentData()
        keys={2:"BIN",8:"OCT",10:"Unsigned",16:"HEX"}
        for edit in (self.a,self.b):
            try:
                word=parse_word(edit.text(),self.previous_base,width)
            except ValueError:
                continue
            edit.blockSignals(True)
            edit.setText(representations(word,width)[keys[new]])
            edit.blockSignals(False)
        self.previous_base=new
        self.refresh()

    def set_operands(self,a,b,e=0):
        for edit in (self.a,self.b):edit.blockSignals(True)
        self.width.setCurrentIndex(self.width.findData(16))
        self.base.blockSignals(True)
        self.base.setCurrentIndex(self.base.findData(16))
        self.previous_base=16
        self.base.blockSignals(False)
        self.a.setText(f"{a:04X}")
        self.b.setText(f"{b:04X}")
        self.cin.setChecked(bool(e))
        for edit in (self.a,self.b):edit.blockSignals(False)
        self.refresh()

    def refresh(self,*_):
        width=self.width.currentData()
        base=self.base.currentData()
        op="CONVERT" if self.op.currentData()=="convert" else self.op.currentText()
        binary=op in ("ADD","ADC","SUB","AND","OR","XOR")
        conversion=op=="CONVERT"
        self.note.setVisible(not conversion)
        self.stages.setVisible(not conversion)
        self.representation.setRowCount(1 if conversion else 3)
        self.b.setEnabled(binary)
        self.cin.setEnabled(op in ("ADC","CIR","CIL"))
        self.representation.clearContents()
        self.stages.setRowCount(0)
        self.flags.clear()
        self.result=None
        try:
            a=parse_word(self.a.text(),base,width)
            b=parse_word(self.b.text(),base,width) if binary else 0
            result=None if op=="CONVERT" else alu(op,a,b,width,int(self.cin.isChecked()))
        except ValueError as exc:
            self.status.setText(self.t(str(exc),"عدد ورودی یا طول کلمه معتبر نیست."))
            return
        self.status.clear()
        self.result=result
        words=(("A",a),) if conversion else (("A",a),("B",b if binary else None),(self.t("Result","نتیجه"),result.word))
        for row,(label,word) in enumerate(words):
            values=[label]+(list(representations(word,width).values()) if word is not None else ["—"]*5)
            for col,value in enumerate(values):
                item=QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.representation.setItem(row,col,item)
        if result is None:
            self.flags.setText(self.t("Same word in all four bases","همان کلمه در چهار مبنا"))
            return
        def flag(v):return "—" if v is None else str(int(v))
        self.flags.setText(f"C = {flag(result.carry)}    V = {flag(result.overflow)}    N = {flag(result.negative)}    Z = {flag(result.zero)}")
        self.stages.setRowCount(len(result.stages))
        for row,stage in enumerate(result.stages):
            for col,value in enumerate(stage):
                item=QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.stages.setItem(row,col,item)
