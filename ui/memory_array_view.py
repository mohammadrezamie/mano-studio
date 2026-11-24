"""Interactive bank decoder and parallel-chip organization, using MemoryArray."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QComboBox,
    QSpinBox,QCheckBox,QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView)
from memory_organization import MemoryArray

class MemoryArrayView(QWidget):
    def __init__(self,fa=False):
        super().__init__()
        self.fa=fa
        layout=QVBoxLayout(self)
        note=QLabel(self.t("Upper address bits select a bank; lower bits select a word. Parallel chips provide separate data slices. Configuration changes clear demonstration RAM.","بیت‌های بالایی آدرس، بانک و بیت‌های پایینی، کلمه را انتخاب می‌کنند. تراشه‌های موازی بخش‌های جداگانه داده را می‌سازند. تغییر پیکربندی حافظه آزمایشی را پاک می‌کند."))
        note.setWordWrap(True)
        layout.addWidget(note)
        config=QHBoxLayout()
        self.ab=QComboBox();self.cb=QComboBox();self.banks=QComboBox();self.lanes=QComboBox()
        for combo,values,en,fa_name in ((self.ab,(4,8),"Chip address bits","بیت آدرس تراشه"),(self.cb,(4,8),"Chip word bits","بیت کلمه تراشه"),(self.banks,(1,2,4),"Banks","بانک‌ها"),(self.lanes,(1,2,4),"Chips per bank","تراشه در بانک")):
            config.addWidget(QLabel(self.t(en,fa_name)))
            for v in values:combo.addItem(str(v),v)
            config.addWidget(combo)
        self.cb.setCurrentIndex(1);self.banks.setCurrentIndex(1);self.lanes.setCurrentIndex(1)
        layout.addLayout(config)
        row=QHBoxLayout()
        self.address=QSpinBox();self.address.setDisplayIntegerBase(16)
        # QSpinBox is signed 32-bit; the largest 32-bit word uses text instead.
        from PySide6.QtWidgets import QLineEdit
        self.word=QLineEdit("0000");self.word.setMaxLength(8)
        self.word.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        row.addWidget(QLabel(self.t("Address (HEX)","آدرس هگز")));row.addWidget(self.address)
        row.addWidget(QLabel(self.t("Write word (HEX)","کلمه نوشتن هگز")));row.addWidget(self.word)
        self.enabled=QCheckBox(self.t("Memory enable","فعال‌سازی حافظه"));self.enabled.setChecked(True);row.addWidget(self.enabled)
        write=QPushButton(self.t("Write","نوشتن"));write.clicked.connect(self.write);row.addWidget(write)
        layout.addLayout(row)
        self.summary=QLabel();self.summary.setWordWrap(True);layout.addWidget(self.summary)
        self.table=QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.table,1)
        self.status=QLabel();self.status.setWordWrap(True);layout.addWidget(self.status)
        for combo in (self.ab,self.cb,self.banks,self.lanes):combo.currentIndexChanged.connect(self.configure)
        self.address.valueChanged.connect(self.refresh);self.enabled.toggled.connect(self.refresh)
        self.configure()
    def t(self,en,fa):return fa if self.fa else en
    def configure(self,*_):
        self.model=MemoryArray(*(c.currentData() for c in (self.ab,self.cb,self.banks,self.lanes)))
        self.address.setRange(0,self.model.size-1)
        self.word.setText("0"* ((self.model.width+3)//4))
        self.refresh()
    def refresh(self,*_):
        self.status.clear()
        m=self.model;a=self.address.value();en=self.enabled.isChecked()
        sel=m.decode(a,en);value=m.read(a,en)
        self.summary.setText(f"{m.size} × {m.width} bit · {m.banks*m.lanes} "+self.t("chips","تراشه")+f"\nA = {a:0{m.address_bits+(m.banks.bit_length()-1)}b} · "+self.t("Bank","بانک")+f" = {sel.bank} · "+self.t("Local address","آدرس داخلی")+f" = {sel.local:X} · Q = "+("Z" if value is None else f"{value:0{(m.width+3)//4}X}"))
        self.table.setRowCount(m.banks);self.table.setColumnCount(m.lanes+2)
        self.table.setHorizontalHeaderLabels([self.t("Bank / range","بانک / محدوده"),"CS̅"]+[f"D[{(i+1)*m.chip_bits-1}:{i*m.chip_bits}]" for i in range(m.lanes)])
        for bank in range(m.banks):
            self.table.setItem(bank,0,QTableWidgetItem(f"{bank} · {bank*m.depth:X}–{(bank+1)*m.depth-1:X}"))
            self.table.setItem(bank,1,QTableWidgetItem(str(sel.cs_n[bank])))
            for lane,chip in enumerate(m.chips[bank]):
                stored=chip.words[sel.local]
                text=f"{chip.size} × {chip.word_bits}\nM[{sel.local:X}] = {stored:0{m.chip_bits//4}X}\nQ = "+("Z" if sel.cs_n[bank] else f"{stored:0{m.chip_bits//4}X}")
                self.table.setItem(bank,lane+2,QTableWidgetItem(text))
            self.table.setRowHeight(bank,78)
    def write(self):
        import re
        try:
            raw=self.word.text().strip()
            if re.fullmatch(r"[0-9A-Fa-f]{1,8}",raw) is None:raise ValueError()
            if not self.enabled.isChecked():
                self.status.setText(self.t("Memory disabled; no write.","حافظه غیرفعال است؛ نوشتن انجام نشد."));return
            self.model.write(self.address.value(),int(raw,16))
        except ValueError:
            self.status.setText(self.t("Invalid word for selected width.","کلمه برای طول انتخاب‌شده نامعتبر است."));return
        self.refresh()
        self.status.setText(self.t("Write completed.","نوشتن انجام شد."))
