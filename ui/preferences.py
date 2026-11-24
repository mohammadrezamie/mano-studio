"""Preferences and a user-triggered, nonblocking release check."""
from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QPushButton
from update_service import check_updates, RELEASES_PAGE


class UpdateWorker(QObject):
    finished = Signal(str, str)

    @Slot()
    def run(self):
        try:
            tag = check_updates(explicit=True)
            self.finished.emit(tag or "", "")
        except Exception as exc:
            self.finished.emit("", str(exc))


class Preferences(QDialog):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.workspace = workspace
        self.settings = workspace.settings
        self.fa = workspace.language == "fa"
        self.thread = None
        self.setWindowTitle(self.text("Settings", "تنظیمات"))
        self.resize(440, 320)
        layout = QVBoxLayout(self)
        title = QLabel(self.text("Appearance", "ظاهر"))
        title.setObjectName("section")
        layout.addWidget(title)
        for key, en, fa, default in [
            ("glass_enabled", "Glass effects", "جلوه‌های شیشه‌ای", True),
            ("reduced_motion", "Reduce motion", "کاهش حرکت و انیمیشن", False),
        ]:
            toggle = QCheckBox(self.text(en, fa))
            toggle.setChecked(self.settings.value(key, default, type=bool))
            toggle.toggled.connect(lambda value, k=key: self.change(k, value))
            layout.addWidget(toggle)
        label = QLabel(self.text("Offline by design", "طراحی کاملاً آفلاین"))
        label.setObjectName("section")
        layout.addWidget(label)
        note = QLabel(self.text(
            "All tools work offline. Only pressing Check for updates contacts GitHub. No automatic download or telemetry.",
            "تمام ابزارها آفلاین هستند. فقط با انتخاب بررسی به‌روزرسانی به گیت‌هاب متصل می‌شوید. بدون دانلود خودکار یا ارسال داده."))
        note.setWordWrap(True)
        layout.addWidget(note)
        self.check = QPushButton(self.text("Check for updates", "بررسی به‌روزرسانی"))
        self.check.clicked.connect(self.start_check)
        layout.addWidget(self.check)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addStretch()
        close = QPushButton(self.text("Close", "بستن"))
        close.clicked.connect(self.accept)
        layout.addWidget(close)

    def text(self, en, fa):
        return fa if self.fa else en

    def change(self, key, value):
        self.settings.setValue(key, value)
        self.settings.sync()
        self.workspace.apply_appearance()

    def start_check(self):
        if self.thread is not None:
            return
        self.check.setEnabled(False)
        self.status.setText(self.text("Checking GitHub…", "در حال بررسی گیت‌هاب…"))
        self.thread = QThread(self)
        self.worker = UpdateWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.show_result)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.cleanup)
        self.thread.start()

    @Slot(str, str)
    def show_result(self, tag, error):
        if error:
            self.status.setText(self.text("Update check failed. Offline tools remain available.", "بررسی به‌روزرسانی ناموفق بود. ابزارهای آفلاین همچنان در دسترس هستند."))
        elif tag:
            self.status.setText(self.text("New version: ", "نسخه جدید: ") + tag + "\n" + RELEASES_PAGE)
            self.status.setTextInteractionFlags(self.status.textInteractionFlags() | Qt.TextInteractionFlag.TextSelectableByMouse)
        else:
            self.status.setText(self.text("No newer published version found.", "نسخه منتشرشده جدیدتری یافت نشد."))

    @Slot()
    def cleanup(self):
        self.thread.deleteLater()
        self.thread = None
        self.worker = None
        self.check.setEnabled(True)

    def done(self, result):
        if self.thread is not None:
            self.status.setText(self.text("Update check is still running.", "بررسی به‌روزرسانی در حال انجام است."))
            return
        super().done(result)
