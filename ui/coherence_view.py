"""Bilingual interactive inspector for the ideal serialized MSI model."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)
from cache_coherence import MSICache


class CoherenceView(QWidget):
    def __init__(self, theme="dark", fa=False):
        super().__init__()
        self.fa = fa
        self.model = MSICache()
        self.last = None
        layout = QVBoxLayout(self)
        note = QLabel(self.t(
            "M: modified · S: shared · I: invalid. Serialized accesses; RAM may lag while a cache owns M.",
            "M: تغییریافته · S: مشترک · I: نامعتبر. دسترسی ترتیبی؛ هنگام مالکیت M حافظه ممکن است قدیمی باشد."))
        note.setWordWrap(True)
        layout.addWidget(note)
        row = QHBoxLayout()
        self.core, self.address, self.value = QSpinBox(), QSpinBox(), QSpinBox()
        for field, limit, base, label in (
            (self.core, self.model.CORES-1, 10, self.t("Processor", "پردازنده")),
            (self.address, self.model.WORDS-1, 16, self.t("Address HEX", "آدرس هگز")),
            (self.value, 65535, 16, self.t("Word HEX", "کلمه هگز")),
        ):
            field.setRange(0, limit)
            field.setDisplayIntegerBase(base)
            field.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            field.setAccessibleName(label)
            caption = QLabel(label)
            caption.setBuddy(field)
            row.addWidget(caption)
            row.addWidget(field)
        layout.addLayout(row)
        row = QHBoxLayout()
        for name, action in (
            (self.t("Read", "خواندن"), lambda: self.access(False)),
            (self.t("Write", "نوشتن"), lambda: self.access(True)),
            (self.t("Example", "مثال"), self.example),
            (self.t("Reset", "بازنشانی"), self.reset),
        ):
            button = QPushButton(name)
            button.clicked.connect(action)
            row.addWidget(button)
        layout.addLayout(row)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addWidget(QLabel(self.t("Cache slots: address / state / word", "خطوط کش: آدرس / حالت / کلمه")))
        self.cache = self.table(self.model.CORES, self.model.SETS)
        self.cache.setVerticalHeaderLabels([f"P{i}" for i in range(self.model.CORES)])
        self.cache.setHorizontalHeaderLabels([str(i) for i in range(self.model.SETS)])
        layout.addWidget(self.cache, 2)
        layout.addWidget(QLabel(self.t("RAM (hex)", "حافظه اصلی (هگز)")))
        self.ram = self.table(2, 8)
        self.ram.setHorizontalHeaderLabels([f"+{i:X}" for i in range(8)])
        self.ram.setVerticalHeaderLabels(["0", "8"])
        layout.addWidget(self.ram, 1)
        self.trace = self.table(0, 6)
        self.trace.setHorizontalHeaderLabels(["#", self.t("Access", "دسترسی"), self.t("Hit / miss", "اصابت / عدم اصابت"), self.t("Bus", "گذرگاه"), self.t("Invalidated", "نامعتبر"), self.t("Writebacks", "بازنویسی")])
        layout.addWidget(self.trace, 3)
        self.refresh()

    def t(self, en, fa):
        return fa if self.fa else en

    @staticmethod
    def table(rows, cols):
        table = QTableWidget(rows, cols)
        table.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table

    @staticmethod
    def put(table, row, col, value):
        item = QTableWidgetItem(value)
        item.setToolTip(value)
        table.setItem(row, col, item)

    def refresh(self):
        for core, lines in enumerate(self.model.lines):
            for slot, line in enumerate(lines):
                value = "I" if line.state == "I" else f"{line.address:X} / {line.state} / {line.value:04X}"
                self.put(self.cache, core, slot, value)
        for addr, word in enumerate(self.model.memory):
            self.put(self.ram, addr//8, addr%8, f"{word:04X}")
        self.status.setText(self.t("Transactions", "تراکنش‌ها") + f": {self.model.accesses}" +
            ("" if self.last is None else " · " + self.t("Last word", "آخرین کلمه") + f": {self.last.value:04X}"))

    def reset(self):
        self.model = MSICache()
        self.last = None
        self.trace.setRowCount(0)
        self.refresh()

    def access(self, write):
        core, addr = self.core.value(), self.address.value()
        event = self.model.write(core, addr, self.value.value()) if write else self.model.read(core, addr)
        self.record(event)

    def record(self, event):
        self.last = event
        if self.trace.rowCount() >= 128:
            self.trace.removeRow(0)
        row = self.trace.rowCount()
        self.trace.insertRow(row)
        values = (str(self.model.accesses),
            f"P{event.core} {'W' if event.operation == 'write' else 'R'} [{event.address:X}]={event.value:04X}",
            self.t("Hit", "اصابت") if event.hit else self.t("Miss", "عدم اصابت"),
            event.bus if event.bus != "none" else "—",
            ", ".join(f"P{i}" for i in event.invalidated) or "—",
            ", ".join(f"P{w.core} [{w.address:X}]={w.value:04X}" for w in event.writebacks) or "—")
        for col, value in enumerate(values):
            self.put(self.trace, row, col, value)
        self.trace.scrollToBottom()
        self.refresh()

    def example(self):
        self.reset()
        self.record(self.model.write(0, 3, 0xABCD))
        self.record(self.model.read(1, 3))
