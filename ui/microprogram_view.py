"""Interactive Chapter 7 control memory, independent of the Basic Computer."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPlainTextEdit,
    QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QPushButton,QSpinBox)
from microprogram import MicroComputer,parse_image,demo_images,CONDITIONS,BRANCHES


class MicroprogramView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa
        self.model=None
        self.last=None
        layout=QVBoxLayout(self)
        note=QLabel(self.t("Chapter 7 model: 128 × 20 control store; 11-bit PC/AR. Not the Basic Computer ISA. Edit HEX address:word images, load, then execute one microinstruction.",
            "مدل فصل هفتم: حافظه کنترل ۱۲۸ × ۲۰ و PC/AR یازده‌بیتی. این مدل با پردازنده پایه متفاوت است. تصویر هگز آدرس:کلمه را ویرایش و بارگذاری کنید و ریزدستور را اجرا کنید."))
        note.setWordWrap(True);layout.addWidget(note)
        row=QHBoxLayout()
        self.control=QPlainTextEdit()
        self.data=QPlainTextEdit()
        for edit,en,fa_label in [(self.control,"Control store (HEX)","حافظه کنترل (هگز)"),(self.data,"Data memory (HEX)","حافظه داده (هگز)")]:
            col=QVBoxLayout();col.addWidget(QLabel(self.t(en,fa_label)))
            edit.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            edit.setAccessibleName(self.t(en,fa_label))
            edit.setMaximumHeight(110);col.addWidget(edit);row.addLayout(col)
        layout.addLayout(row)
        row=QHBoxLayout()
        row.addWidget(QLabel("CAR"))
        self.entry=QSpinBox();self.entry.setRange(0,127);self.entry.setValue(64);row.addWidget(self.entry)
        for en,fa_label,fn in [("Example","مثال",self.example),("Load / Reset","بارگذاری / بازنشانی",self.load),("Next microinstruction","ریزدستور بعدی",self.step)]:
            button=QPushButton(self.t(en,fa_label));button.clicked.connect(fn);row.addWidget(button)
            if fn==self.step:self.step_button=button
        layout.addLayout(row)
        self.fields=QLabel();self.fields.setWordWrap(True);self.fields.setLayoutDirection(Qt.LayoutDirection.LeftToRight);layout.addWidget(self.fields)
        self.table=QTableWidget(0,3)
        self.table.setHorizontalHeaderLabels([self.t("Register","ثبات"),self.t("Before (HEX)","قبل (هگز)"),self.t("After (HEX)","بعد (هگز)")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.table,1)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        self.control.textChanged.connect(self.invalidate);self.data.textChanged.connect(self.invalidate)
        self.entry.valueChanged.connect(self.invalidate)
        self.example()

    def t(self,en,fa):return fa if self.fa else en

    def invalidate(self,*_):
        self.model=self.last=None
        self.table.setRowCount(0);self.fields.clear();self.step_button.setEnabled(False)
        self.status.setText(self.t("Images changed. Load again.","تصویر حافظه تغییر کرد؛ دوباره بارگذاری کنید."))

    def example(self):
        c,d=demo_images()
        self.control.setPlainText("\n".join(f"{a:02X}:{w:05X}" for a,w in sorted(c.items())))
        self.data.setPlainText("\n".join(f"{a:03X}:{w:04X}" for a,w in sorted(d.items())))
        self.entry.setValue(64);self.load()

    def load(self):
        self.invalidate()
        try:
            self.model=MicroComputer(parse_image(self.control.toPlainText(),128,1<<20),
                parse_image(self.data.toPlainText(),2048,65536),self.entry.value())
        except ValueError as e:
            self.status.setText(self.t(str(e),"تصویر حافظه نامعتبر است؛ آدرس‌ها و کلمات هگز را بررسی کنید."));return
        self.step_button.setEnabled(True)
        regs=self.model.registers();self.show_regs(regs,regs)
        self.status.setText(self.t("Ready.","آماده."))

    def show_regs(self,before,after):
        self.table.setRowCount(len(before))
        for i,k in enumerate(before):
            for j,v in enumerate((k,f"{before[k]:04X}",f"{after[k]:04X}")):
                item=QTableWidgetItem(v)
                if before[k]!=after[k]:
                    font=item.font();font.setBold(True);item.setFont(font)
                self.table.setItem(i,j,item)

    def step(self):
        if self.model is None:return
        try:g=self.model.step()
        except ValueError as e:
            self.status.setText(self.t(str(e),"ریزدستور نامعتبر، مقداردهی‌نشده یا دارای عملیات متعارض است."));return
        self.last=g;self.show_regs(g.before,g.after)
        m=g.instruction
        self.fields.setText(f"F1 {m.f1:03b} | F2 {m.f2:03b} | F3 {m.f3:03b} | CD {m.cd:02b} | BR {m.br:02b} | AD {m.ad:07b}\n"
            +(", ".join(m.operations) or "NOP")+f" | {CONDITIONS[m.cd]}={int(g.condition)} | {BRANCHES[m.br]} | CAR ← {g.next_source} ({g.after['CAR']:02X})")
        accesses=[f"M[{a:03X}] → {v:04X}" for a,v in g.reads]+[f"M[{a:03X}]: {old:04X} → {v:04X}" for a,old,v in g.writes]
        self.status.setText(" · ".join(accesses) or self.t("No memory access.","بدون دسترسی حافظه."))
