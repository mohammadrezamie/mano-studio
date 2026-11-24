"""Live program workspace: actual assembler and CPU, not the fixed demo."""
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QPlainTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QSplitter, QSpinBox, QLineEdit)
from PySide6.QtCore import Qt
from assembler import assemble
from simulator import CPU
from ui.workspace import code_editor

EXAMPLE = """ORG 000
LDA A
ADD B
STA C
HLT
A, DEC 5
B, DEC 3
C, HEX 0000
END"""


class ProgramLab(QDialog):
    def __init__(self, parent, assembly=""):
        super().__init__(parent)
        self.fa = parent.language == "fa"
        self.setWindowTitle("Mano Studio — " + self.t("Program Lab", "آزمایشگاه برنامه"))
        self.resize(1060, 700)
        self.cpu = None
        self.program = None
        self.steps = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.step)
        layout = QVBoxLayout(self)
        intro = QLabel(self.t("Assemble and execute your own program, one instruction at a time.",
            "برنامه خود را اسمبل کنید و اجرای هر دستور را مرحله‌به‌مرحله ببینید."))
        intro.setWordWrap(True)
        layout.addWidget(intro)
        panes = QSplitter(Qt.Orientation.Horizontal)
        self.source = code_editor()
        self.source.setPlainText(assembly or EXAMPLE)
        self.machine = code_editor(True)
        panes.addWidget(self.source)
        panes.addWidget(self.machine)
        panes.setSizes([500, 500])
        layout.addWidget(panes, 2)
        controls = QHBoxLayout()
        for en, fa, slot in [("Load example","مثال جمع",self.example),
            ("Assemble / Reset","اسمبل و بازنشانی",self.load),
            ("Step","گام بعد",self.step),("Run","اجرا",self.run),
            ("Pause","توقف موقت",self.pause)]:
            b = QPushButton(self.t(en,fa))
            b.clicked.connect(slot)
            controls.addWidget(b)
        self.speed = QSpinBox()
        self.speed.setRange(100, 2000)
        self.speed.setValue(600)
        self.speed.setSuffix(" ms")
        self.speed.valueChanged.connect(self.timer.setInterval)
        controls.addWidget(self.speed)
        layout.addLayout(controls)
        lower = QSplitter(Qt.Orientation.Horizontal)
        self.registers = QTableWidget(0, 2)
        self.registers.setHorizontalHeaderLabels([self.t("Register","ثبات"), self.t("Value (HEX)","مقدار هگز")])
        self.memory = QTableWidget(0, 2)
        self.memory.setHorizontalHeaderLabels([self.t("Address","آدرس"), self.t("Word (HEX)","کلمه هگز")])
        for table in (self.registers,self.memory):
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            lower.addWidget(table)
        layout.addWidget(lower, 2)
        io = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText(self.t("Input byte (00–FF)","بایت ورودی (00–FF)"))
        self.input.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        io.addWidget(self.input)
        for en,fa,slot in [("Send input","ارسال ورودی",self.send_input),
                           ("Read output","خواندن خروجی",self.read_output)]:
            b=QPushButton(self.t(en,fa))
            b.clicked.connect(slot)
            io.addWidget(b)
        layout.addLayout(io)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.source.textChanged.connect(self.invalidate)
        self.load()

    def t(self,en,fa):
        return fa if self.fa else en

    def invalidate(self):
        self.pause()
        self.cpu = self.program = None
        self.machine.clear()
        self.registers.setRowCount(0)
        self.memory.setRowCount(0)
        self.status.setText(self.t("Source changed. Assemble again.","کد تغییر کرد؛ دوباره اسمبل کنید."))

    def example(self):
        self.source.setPlainText(EXAMPLE)
        self.load()

    def load(self):
        self.pause()
        self.program = assemble(self.source.toPlainText())
        self.cpu = None
        self.steps = 0
        if not self.program.ok:
            self.machine.setPlainText("\n".join(f"{e.line}: {e.message}" for e in self.program.errors))
            self.status.setText(self.t("Assembly failed.","اسمبل ناموفق بود."))
            self.registers.setRowCount(0)
            self.memory.setRowCount(0)
            return
        self.machine.setPlainText(self.program.listing())
        self.cpu = CPU(self.program.words, self.program.entry)
        self.addresses = set(self.program.words)
        self.refresh()
        self.status.setText(self.t("Ready.","آماده."))

    def refresh(self,event=None):
        values = self.cpu.registers()
        self.registers.setRowCount(len(values))
        for row,(name,value) in enumerate(values.items()):
            width = 3 if name in ("PC","AR") else 4 if name in ("AC","DR","IR","TR") else 2 if name in ("INPR","OUTR") else 1
            self.registers.setItem(row,0,QTableWidgetItem(name))
            item = QTableWidgetItem(f"{value:0{width}X}")
            if event and event.before.get(name) != value:
                from PySide6.QtGui import QColor
                item.setBackground(QColor(80,145,185,70))
            self.registers.setItem(row,1,item)
        if event:
            self.addresses.update(a for a,old,new in event.writes)
            if event.effective_address is not None:
                self.addresses.add(event.effective_address)
        addresses = sorted(self.addresses)
        self.memory.setRowCount(len(addresses))
        for row,a in enumerate(addresses):
            self.memory.setItem(row,0,QTableWidgetItem(f"{a:03X}"))
            self.memory.setItem(row,1,QTableWidgetItem(f"{self.cpu.memory[a]:04X}"))

    def step(self):
        if self.cpu is None:
            self.pause()
            return
        if self.steps >= 10000:
            self.pause()
            self.status.setText(self.t("Step limit reached. Reset to continue.","حد اجرای گام‌ها رسید؛ بازنشانی کنید."))
            return
        try:
            event = self.cpu.step()
        except ValueError as error:
            self.pause()
            self.status.setText(str(error))
            return
        if event is None:
            self.pause()
            return
        self.steps += 1
        self.refresh(event)
        self.status.setText(f"{event.address:03X} · {event.mnemonic} · AC={self.cpu.ac:04X} · PC={self.cpu.pc:03X}")
        if self.cpu.halted:
            self.pause()

    def run(self):
        if self.cpu and not self.cpu.halted:
            self.timer.start(self.speed.value())

    def pause(self):
        self.timer.stop()

    def send_input(self):
        if self.cpu:
            try:
                self.cpu.input_byte(int(self.input.text(),16))
                self.refresh()
            except ValueError as error:
                self.status.setText(str(error))

    def read_output(self):
        if self.cpu:
            byte = self.cpu.output_byte()
            self.refresh()
            self.status.setText(self.t("No output pending.","خروجی آماده نیست.") if byte is None else f"OUT: {byte:02X}")

    def done(self,result):
        self.pause()
        super().done(result)
