"""Preferences and a user-triggered, nonblocking release check."""
from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QPushButton, QPlainTextEdit, QComboBox
from update_service import release_info, RELEASES_PAGE, VERSION, CHANNEL
from ui.motion import MotionButton


class UpdateWorker(QObject):
    finished = Signal(object, str)

    @Slot()
    def run(self):
        try:
            self.finished.emit(release_info(explicit=True), "")
        except Exception as exc:
            self.finished.emit(None, str(exc))


class Preferences(QDialog):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.workspace = workspace
        self.settings = workspace.settings
        self.fa = workspace.language == "fa"
        self.thread = None
        self.setWindowTitle(self.text("Settings", "تنظیمات"))
        self.resize(500, 400)
        layout = QVBoxLayout(self)
        title = QLabel(self.text("Appearance", "ظاهر"))
        title.setObjectName("section")
        layout.addWidget(title)
        for key, en, fa, default in [
            ("glass_enabled", "Glass effects", "جلوه‌های شیشه‌ای", True),
            ("reduced_motion", "Reduce motion", "کاهش حرکت و انیمیشن", False),
            ("lab_motion", "Animate lab signals", "انیمیشن سیگنال‌های آزمایشگاه", True),
        ]:
            toggle = QCheckBox(self.text(en, fa))
            toggle.setObjectName(key)
            toggle.setChecked(self.settings.value(key, default, type=bool))
            toggle.toggled.connect(lambda value, k=key: self.change(k, value))
            layout.addWidget(toggle)
        layout.addWidget(QLabel(self.text("Logic gate notation","نمادگذاری گیت‌های منطقی")))
        self.symbols=QComboBox()
        self.symbols.addItem(self.text("Distinctive shapes (ANSI-style)","نمادهای متمایز (سبک ANSI)"),"ansi")
        self.symbols.addItem(self.text("Rectangular shapes (IEC-style)","نمادهای مستطیلی (سبک IEC)"),"iec")
        index=self.symbols.findData(self.settings.value("gate_symbol_style","ansi"))
        self.symbols.setCurrentIndex(max(0,index))
        self.symbols.currentIndexChanged.connect(lambda _:self.change("gate_symbol_style",self.symbols.currentData()))
        layout.addWidget(self.symbols)
        label = QLabel(self.text("Offline by design", "طراحی کاملاً آفلاین"))
        label.setObjectName("section")
        layout.addWidget(label)
        note = QLabel(self.text(
            "All tools work offline. Only pressing Check for updates contacts GitHub. No automatic download or telemetry.",
            "تمام ابزارها آفلاین هستند. فقط با انتخاب بررسی به‌روزرسانی به گیت‌هاب متصل می‌شوید. بدون دانلود خودکار یا ارسال داده."))
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addWidget(QLabel(self.text("Installed version: ", "نسخه نصب‌شده: ")+VERSION))
        channel_name = self.text("Stable", "پایدار") if CHANNEL == "stable" else self.text("Beta", "آزمایشی")
        layout.addWidget(QLabel(self.text("Update channel: ", "کانال به‌روزرسانی: ")+channel_name))
        self.check = MotionButton(self.text("Check for updates", "بررسی به‌روزرسانی"))
        self.check.clicked.connect(self.start_check)
        layout.addWidget(self.check)
        self.status = QLabel()
        self.status.setWordWrap(True)
        self.status.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.status)
        self.notes = QPlainTextEdit()
        self.notes.setReadOnly(True)
        self.notes.setAccessibleName(self.text("Release notes", "توضیحات نسخه"))
        self.notes.hide()
        layout.addWidget(self.notes)
        self.releases = MotionButton(self.text("Open official releases", "مشاهده نسخه‌های رسمی"))
        self.releases.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(RELEASES_PAGE)))
        self.releases.hide()
        layout.addWidget(self.releases)
        layout.addStretch()
        close = MotionButton(self.text("Close", "بستن"))
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
        self.notes.clear()
        self.notes.hide()
        self.releases.hide()
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

    @Slot(object, str)
    def show_result(self, release, error):
        if error:
            self.status.setText(self.text("Update check failed. Offline tools remain available.", "بررسی به‌روزرسانی ناموفق بود. ابزارهای آفلاین همچنان در دسترس هستند."))
        elif release:
            status = self.text("New version: ", "نسخه جدید: ") + release.tag
            if release.installer_size is not None:
                status += "\n" + self.text("Approximate setup size: ", "حجم تقریبی نصب‌کننده: ") + f"{release.installer_size / 1048576:.1f} MiB"
            status += "\n" + self.text("Automatic installation is not enabled in this build.", "نصب خودکار در این نسخه فعال نیست.")
            self.status.setText(status)
            self.notes.setPlainText(release.notes or self.text("No release notes provided.", "توضیحی برای نسخه ارائه نشده است."))
            self.notes.show()
            self.releases.show()
        else:
            self.status.setText(self.text("No newer version in this channel.", "نسخه جدیدتری در این کانال یافت نشد."))

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
