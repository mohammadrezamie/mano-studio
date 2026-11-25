"""Read-only reference tables for the active ideal clocked component."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QLabel,QTableWidget,
    QTableWidgetItem,QHeaderView,QAbstractItemView)
from sequential_logic import MODELS
from flipflop_reference import KINDS,characteristic,excitation,formula


class FlipFlopReferenceView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa
        layout=QVBoxLayout(self)
        self.note=QLabel()
        self.note.setWordWrap(True)
        layout.addWidget(self.note)
        self.equation=QLabel()
        self.equation.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.equation)
        self.characteristic_label=QLabel(self.t("Characteristic table","جدول مشخصه"))
        layout.addWidget(self.characteristic_label)
        self.characteristic=self.make_table()
        layout.addWidget(self.characteristic,2)
        self.excitation_label=QLabel(self.t("Excitation table","جدول تحریک"))
        layout.addWidget(self.excitation_label)
        self.excitation=self.make_table()
        layout.addWidget(self.excitation,1)

    def t(self,en,fa):
        return fa if self.fa else en

    def make_table(self):
        table=QTableWidget()
        table.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().hide()
        return table

    def populate(self,table,headers,rows):
        table.clear()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(rows))
        for i,row in enumerate(rows):
            for j,value in enumerate(row):
                item=QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(i,j,item)

    def set_kind(self,kind):
        available=kind in KINDS
        for widget in (self.equation,self.characteristic_label,self.characteristic,
                       self.excitation_label,self.excitation):
            widget.setVisible(available)
        if not available:
            self.note.setText(self.t("Select D, T, JK or SR to inspect the one-bit reference tables.",
                "برای مشاهده جدول‌های تک‌بیتی، D، T، JK یا SR را انتخاب کنید."))
            self.characteristic.setRowCount(0)
            self.excitation.setRowCount(0)
            return
        self.note.setText(self.t("X means either input is valid. Forbidden SR inputs have no next state in this ideal model.",
            "X یعنی هر دو مقدار ورودی مجاز است. ورودی ممنوع SR در این مدل ایده‌آل حالت بعد ندارد."))
        self.equation.setText(formula(kind))
        pins=MODELS[kind][0]
        self.populate(self.characteristic,("Q",*pins,"Q′"),
            [(q,*bits,self.t("Forbidden","ممنوع") if nxt is None else nxt)
             for q,bits,nxt in characteristic(kind)])
        self.populate(self.excitation,("Q","Q′",*pins),
            [(q,nxt,*pattern) for q,nxt,choices,pattern in excitation(kind)])
