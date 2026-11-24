"""Searchable offline instruction reference powered by the existing translator."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,
    QCheckBox,QTableWidget,QTableWidgetItem,QAbstractItemView,QHeaderView,QPushButton)
import re
from instruction_catalog import TEMPLATES, build_rtl
from rtl_translator import translate
from ui.strings import NAMES, EN_NAMES


class InstructionReference(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.fa=parent.language=="fa"
        self.chosen=None
        self.setWindowTitle(self.t("Instruction reference","راهنمای دستورات"))
        self.resize(870,560)
        layout=QVBoxLayout(self)
        heading=QLabel(self.t("25 Mano instructions","۲۵ دستور مانو"))
        heading.setObjectName("brand")
        layout.addWidget(heading)
        self.search=QLineEdit()
        self.search.setPlaceholderText(self.t("Search mnemonic, RTL or description…","جست‌وجوی دستور، RTL یا توضیح…"))
        layout.addWidget(self.search)
        row=QHBoxLayout()
        row.addWidget(QLabel(self.t("Example address (HEX)","آدرس نمونه (هگز)")))
        self.address=QLineEdit("100")
        self.address.setMaxLength(3)
        self.address.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        row.addWidget(self.address)
        self.indirect=QCheckBox(self.t("Indirect memory","حافظه غیرمستقیم"))
        row.addWidget(self.indirect)
        layout.addLayout(row)
        self.table=QTableWidget(0,4)
        self.table.setHorizontalHeaderLabels(["ASM",self.t("Operation","عملیات"),"RTL",self.t("Translation","ترجمه")])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table,1)
        self.message=QLabel()
        layout.addWidget(self.message)
        row=QHBoxLayout()
        self.insert=QPushButton(self.t("Insert RTL","درج RTL"))
        self.insert.setObjectName("primary")
        self.insert.clicked.connect(self.select)
        row.addWidget(self.insert)
        close=QPushButton(self.t("Close","بستن"))
        close.clicked.connect(self.reject)
        row.addWidget(close)
        layout.addLayout(row)
        self.search.textChanged.connect(self.refresh)
        self.address.textChanged.connect(self.refresh)
        self.indirect.toggled.connect(self.refresh)
        self.table.itemSelectionChanged.connect(self.update_insert)
        self.table.cellDoubleClicked.connect(lambda *_:self.select())
        self.refresh()

    def t(self,en,fa):
        return fa if self.fa else en

    def refresh(self):
        query=self.search.text().strip().casefold()
        rows=[]
        address=self.address.text()
        names=NAMES if self.fa else EN_NAMES
        for mnemonic,template in TEMPLATES.items():
            try:
                memory="{a}" in template
                rtl=build_rtl(mnemonic,address if memory else "",self.indirect.isChecked() if memory else False)
                asm=translate(rtl).assembly
            except ValueError:
                continue
            if query in " ".join((mnemonic,names[mnemonic],rtl,asm)).casefold():
                rows.append((mnemonic,names[mnemonic],rtl,asm))
        self.rows=rows
        self.table.setRowCount(len(rows))
        for i,values in enumerate(rows):
            for j,value in enumerate(values):
                self.table.setItem(i,j,QTableWidgetItem(value))
        self.message.setText(self.t("Enter a valid hexadecimal address (000–FFF).","آدرس هگز معتبر وارد کنید (000–FFF).") if not re.fullmatch(r"[0-9a-fA-F]{1,3}",address) else self.t(f"{len(rows)} matching instructions",f"{len(rows)} دستور مطابق"))
        if rows:
            self.table.selectRow(0)
        self.update_insert()

    def update_insert(self):
        self.insert.setEnabled(0<=self.table.currentRow()<len(self.rows))

    def select(self):
        row=self.table.currentRow()
        if 0<=row<len(self.rows):
            self.chosen=self.rows[row][2]
            self.accept()
