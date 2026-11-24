"""Field-based control word editor; validation uses the real microassembler."""
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QSpinBox,QPushButton
from microprogram import FIELDS,CONDITIONS,BRANCHES
from microassembler import assemble_micro


class MicroinstructionBuilder(QWidget):
    def __init__(self,fa=False,insert=None):
        super().__init__()
        self.fa=fa
        self.insert=insert
        self.word=None
        layout=QVBoxLayout(self)
        row=QHBoxLayout()
        self.address=QSpinBox();self.address.setRange(0,127);self.address.setValue(64)
        row.addWidget(QLabel("ORG"));row.addWidget(self.address)
        self.fields=[]
        for index,choices in enumerate(FIELDS):
            box=QComboBox()
            for code,name in enumerate(choices):
                if name!="RESERVED":box.addItem(name,code)
            row.addWidget(QLabel(f"F{index+1}"));row.addWidget(box)
            self.fields.append(box)
        layout.addLayout(row)
        row=QHBoxLayout()
        self.condition=QComboBox();self.condition.addItems(CONDITIONS)
        self.branch=QComboBox();self.branch.addItems(BRANCHES)
        self.target=QSpinBox();self.target.setRange(0,127);self.target.setValue(65)
        for name,widget in (("CD",self.condition),("BR",self.branch),("AD",self.target)):
            row.addWidget(QLabel(name));row.addWidget(widget)
        self.append_button=QPushButton(self.t("Append to source","افزودن به متن"))
        self.append_button.clicked.connect(self.append);row.addWidget(self.append_button)
        layout.addLayout(row)
        self.preview=QLabel();self.preview.setWordWrap(True);layout.addWidget(self.preview)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        layout.addStretch()
        for box in self.fields+[self.condition,self.branch]:
            box.currentIndexChanged.connect(self.refresh)
        for box in (self.address,self.target):box.valueChanged.connect(self.refresh)
        self.refresh()

    def t(self,en,fa):return fa if self.fa else en

    def refresh(self,*_):
        ops=", ".join(box.currentText() for box in self.fields if box.currentData()) or "NOP"
        br=self.branch.currentText()
        self.target.setEnabled(br in ("JMP","CALL"))
        suffix=f" {self.target.value()}" if self.target.isEnabled() else ""
        self.source=f"ORG {self.address.value()}\n{ops} {self.condition.currentText()} {br}{suffix}"
        result=assemble_micro(self.source)
        self.word=result.words.get(self.address.value()) if result.ok else None
        self.append_button.setEnabled(self.word is not None)
        if self.word is None:
            self.preview.setText(ops)
            self.status.setText(self.t("Conflicting microoperations.","ریزعملیات متعارض هستند."))
        else:
            self.preview.setText(f"{self.word:05X}  |  {self.word:020b}\n{self.source}")
            self.status.setText(self.t("Valid control word; append explicitly to edit source.","کلمه کنترل معتبر است؛ برای تغییر متن، افزودن را انتخاب کنید."))

    def append(self):
        if self.word is not None and self.insert:
            ok=self.insert(self.address.value(),self.word,self.source)
            self.status.setText(self.t("Appended. Load again to execute.","افزوده شد؛ برای اجرا دوباره بارگذاری کنید.") if ok else self.t("Cannot append: invalid source or occupied address.","افزودن ممکن نیست؛ متن نامعتبر یا آدرس اشغال است."))
