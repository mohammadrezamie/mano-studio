"""Bilingual Boolean laws inspector, embedded in the existing logic lab."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,
    QCheckBox,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QLineEdit)
from boolean_laws import LAWS,compare


class BooleanLawsView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa
        box=QVBoxLayout(self)
        note=QLabel(self.t("Duality swaps AND with OR and 0 with 1. Variables and complements stay unchanged. Compare both sides for every binary input.",
            "دوگانگی، AND و OR و همچنین ۰ و ۱ را جابه‌جا می‌کند. متغیرها و متمم‌ها ثابت می‌مانند. دو طرف را برای تمام ورودی‌ها مقایسه کنید."))
        note.setWordWrap(True)
        box.addWidget(note)
        row=QHBoxLayout()
        label=QLabel(self.t("Law","قانون"))
        self.law=QComboBox()
        self.law.setAccessibleName(label.text())
        label.setBuddy(self.law)
        for law in LAWS:
            self.law.addItem(law.title[fa],law.id)
        row.addWidget(label)
        row.addWidget(self.law,1)
        self.dual=QCheckBox(self.t("Dual form","فرم دوگان"))
        row.addWidget(self.dual)
        box.addLayout(row)
        self.equation=QLineEdit()
        self.equation.setReadOnly(True)
        self.equation.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.equation.setAccessibleName(self.t("Boolean identity","اتحاد بولی"))
        box.addWidget(self.equation)
        self.table=QTableWidget(8,5)
        self.table.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.table.setHorizontalHeaderLabels(["A","B","C",self.t("Left","چپ"),self.t("Right","راست")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().hide()
        box.addWidget(self.table,1)
        self.status=QLabel()
        self.status.setWordWrap(True)
        box.addWidget(self.status)
        self.law.currentIndexChanged.connect(self.refresh)
        self.dual.toggled.connect(self.refresh)
        self.refresh()

    def t(self,en,fa):
        return fa if self.fa else en

    def refresh(self,*_):
        left,right,rows=compare(self.law.currentData(),self.dual.isChecked())
        self.equation.setText(f"{left} = {right}")
        for r,values in enumerate(rows):
            for c,value in enumerate(values):
                item=QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(r,c,item)
        count=sum(row[-1]==row[-2] for row in rows)
        self.status.setText(self.t(f"Matching rows: {count}/8. Unused variables repeat rows.",
            f"ردیف‌های منطبق: {count}/8. متغیرهای بدون استفاده باعث تکرار ردیف‌ها می‌شوند."))
