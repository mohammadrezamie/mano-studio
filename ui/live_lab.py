"""Animated instruction-level demonstration, separated from translation."""
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QFont
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QCheckBox
from demo_cpu import DemoCPU
from ui.glass import paint_backdrop
from ui.theme import PALETTES


class Datapath(QWidget):
    def __init__(self, cpu, theme, glass_enabled=True):
        super().__init__()
        self.cpu = cpu
        self.theme = theme
        self.glass_enabled = glass_enabled
        self.phase = 0.0
        self.setMinimumHeight(260)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        paint_backdrop(p, self.rect(), self.theme, self.glass_enabled)
        p.scale(self.width() / 680, self.height() / 260)
        bg, panel, raised, fg, muted, accent, border = PALETTES[self.theme]
        def card(x, y, w, h, title, lines):
            p.setPen(QPen(QColor(border), 1.2))
            p.setBrush(QColor(panel))
            p.drawRoundedRect(QRectF(x, y, w, h), 12, 12)
            p.setPen(QColor(accent))
            p.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            p.drawText(QRectF(x+12,y+7,w-24,23), Qt.AlignmentFlag.AlignLeft, title)
            p.setPen(QColor(fg))
            p.setFont(QFont("Consolas", 11))
            for i, line in enumerate(lines):
                p.drawText(QRectF(x+12,y+37+i*27,w-24,25), Qt.AlignmentFlag.AlignLeft, line)
        card(16, 40, 198, 175, "MEMORY", [f"100 : {self.cpu.memory[0x100]:04X}", f"101 : {self.cpu.memory[0x101]:04X}", f"102 : {self.cpu.memory[0x102]:04X}"])
        card(466, 40, 198, 175, "CPU", [f"AC : {self.cpu.ac:04X}", f"PC : {self.cpu.pc:03X}", f"IR : {self.cpu.ir:04X}", f"E  : {self.cpu.e}"])
        p.setPen(QPen(QColor(accent), 3))
        p.drawLine(QPointF(214,130), QPointF(466,130))
        p.setPen(QColor(fg))
        p.drawText(QRectF(214,88,252,28), Qt.AlignmentFlag.AlignCenter, "DATA BUS")
        if self.cpu.last in ("LDA","ADD","STA") and self.phase < 1:
            fraction = 1-self.phase if self.cpu.last == "STA" else self.phase
            p.setPen(Qt.PenStyle.NoPen)
            glow = QColor(accent)
            glow.setAlpha(65)
            x = 214+252*fraction
            p.setBrush(glow)
            p.drawEllipse(QPointF(x,130),14,14)
            p.setBrush(QColor(accent))
            p.drawEllipse(QPointF(x,130),6,6)
        p.end()


class LabDialog(QDialog):
    def __init__(self, parent, language, theme, settings):
        super().__init__(parent)
        self.settings = settings
        self.fa = language == "fa"
        self.setWindowTitle("Mano Live Lab")
        self.resize(760, 460)
        self.cpu = DemoCPU()
        layout = QVBoxLayout(self)
        heading = QLabel("آزمایشگاه زنده · مثال جمع" if self.fa else "Live Lab · Addition demo")
        heading.setObjectName("brand")
        layout.addWidget(heading)
        note = QLabel("نمایش آموزشی اجرای چهار دستور؛ نه شبیه‌ساز کامل یا زمان‌بندی ریزعملیات." if self.fa else "Four-instruction educational example; not a full simulator or microoperation timing view.")
        note.setWordWrap(True)
        layout.addWidget(note)
        self.view = Datapath(self.cpu, theme, settings.value("glass_enabled", True, type=bool))
        layout.addWidget(self.view, 1)
        self.status = QLabel()
        layout.addWidget(self.status)
        self.motion = QCheckBox("انیمیشن" if self.fa else "Animation")
        self.motion.setChecked(settings.value("lab_motion", True, type=bool) and not settings.value("reduced_motion", False, type=bool))
        self.motion.setEnabled(not settings.value("reduced_motion", False, type=bool))
        self.motion.toggled.connect(lambda value: settings.setValue("lab_motion", value))
        layout.addWidget(self.motion)
        row = QHBoxLayout()
        for text, slot in [("شروع خودکار" if self.fa else "Play", self.play),
                           ("توقف موقت" if self.fa else "Pause", self.pause),
                           ("گام بعد" if self.fa else "Step", self.step),
                           ("بازنشانی" if self.fa else "Reset", self.reset)]:
            button = QPushButton(text)
            button.clicked.connect(slot)
            row.addWidget(button)
        layout.addLayout(row)
        self.timer = QTimer(self)
        self.timer.setInterval(850)
        self.timer.timeout.connect(self.step)
        self.frames = QTimer(self)
        self.frames.setInterval(30)
        self.frames.timeout.connect(self.frame)
        self.motion.toggled.connect(self.motion_changed)
        self.refresh()

    def refresh(self):
        messages = {"": ("Ready", "آماده"), "LDA": ("Load memory into AC", "انتقال مقدار حافظه به انباره"),
                    "ADD": ("Add memory to AC", "جمع مقدار حافظه با انباره"),
                    "STA": ("Store AC in memory", "ذخیره انباره در حافظه"),
                    "HLT": ("Program halted", "پایان اجرای برنامه")}
        self.status.setText(messages[self.cpu.last][self.fa] + f"  |  AC = {self.cpu.ac}")
        self.view.update()

    def motion_changed(self, enabled):
        if not enabled:
            self.frames.stop()
            self.view.phase = 1
            self.view.update()

    def frame(self):
        self.view.phase = min(1.0, self.view.phase + 0.05)
        self.view.update()
        if self.view.phase >= 1.0:
            self.frames.stop()

    def step(self):
        if not self.cpu.step():
            self.pause()
            return
        self.frames.stop()
        self.view.phase = 0 if self.motion.isChecked() else 1
        if self.motion.isChecked() and not self.cpu.halted:
            self.frames.start()
        self.refresh()
        if self.cpu.halted:
            self.pause()

    def play(self):
        if not self.cpu.halted:
            self.timer.start()

    def pause(self):
        self.timer.stop()
        self.frames.stop()
        self.view.phase = 1
        self.view.update()

    def reset(self):
        self.pause()
        self.cpu = DemoCPU()
        self.view.cpu = self.cpu
        self.refresh()

    def done(self, result):
        self.pause()
        super().done(result)
