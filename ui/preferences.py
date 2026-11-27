"""Preferences and a user-triggered, nonblocking release check."""
from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QPushButton, QPlainTextEdit, QComboBox, QFileDialog, QMessageBox, QProgressBar
from threading import Event
from update_service import release_info, RELEASES_PAGE, VERSION, CHANNEL
from ui.motion import MotionButton
from update_download import download, DownloadCancelled


class UpdateWorker(QObject):
    finished = Signal(object, str)

    @Slot()
    def run(self):
        try:
            self.finished.emit(release_info(explicit=True), "")
        except Exception as exc:
            self.finished.emit(None, str(exc))


class DownloadWorker(QObject):
    finished = Signal(object, str)
    progress = Signal(int, int)

    def __init__(self,asset,path,stop):
        super().__init__()
        self.asset,self.path,self.stop=asset,path,stop
        self.last_percent=-1

    def report(self,count,total):
        # Avoid thousands of queued GUI updates for large assets.
        percent=count*100//total
        if percent!=self.last_percent:
            self.last_percent=percent
            self.progress.emit(count,total)

    @Slot()
    def run(self):
        try:
            path=download(self.asset,self.path,explicit=True,cancelled=self.stop.is_set,progress=self.report)
            self.finished.emit(path,"")
        except DownloadCancelled:
            self.finished.emit(None,"cancelled")
        except Exception:
            self.finished.emit(None,"failed")


class Preferences(QDialog):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.workspace = workspace
        self.settings = workspace.settings
        self.fa = workspace.language == "fa"
        self.thread = None
        self.asset = None
        self.stop = None
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
            "All tools work offline. Manual checks, optional startup checks and explicit downloads contact GitHub. No automatic installation or telemetry.",
            "تمام ابزارها آفلاین هستند. بررسی دستی، بررسی اختیاری هنگام شروع و دریافت با تأیید شما به گیت‌هاب متصل می‌شوند. بدون نصب خودکار یا ارسال داده."))
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addWidget(QLabel(self.text("Installed version: ", "نسخه نصب‌شده: ")+VERSION))
        channel_name = self.text("Stable", "پایدار") if CHANNEL == "stable" else self.text("Beta", "آزمایشی")
        layout.addWidget(QLabel(self.text("Update channel: ", "کانال به‌روزرسانی: ")+channel_name))
        self.auto_check = QCheckBox(self.text("Check for updates at startup (optional)",
                                              "بررسی به‌روزرسانی هنگام شروع (اختیاری)"))
        self.auto_check.setChecked(workspace.update_notice.enabled())
        self.auto_check.toggled.connect(workspace.update_notice.set_enabled)
        layout.addWidget(self.auto_check)
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
        self.download_button=MotionButton(self.text("Download installer…","دریافت نصب‌کننده…"))
        self.download_button.clicked.connect(self.start_download)
        self.download_button.hide()
        layout.addWidget(self.download_button)
        self.download_progress=QProgressBar()
        self.download_progress.setRange(0,100)
        self.download_progress.setAccessibleName(self.text("Installer download progress","پیشرفت دریافت نصب‌کننده"))
        self.download_progress.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.download_progress.hide()
        layout.addWidget(self.download_progress)
        self.cancel_download_button=MotionButton(self.text("Cancel download","لغو دریافت"))
        self.cancel_download_button.clicked.connect(self.cancel_download)
        self.cancel_download_button.hide()
        layout.addWidget(self.cancel_download_button)
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
        self.download_progress.hide()
        self.notes.hide()
        self.releases.hide()
        self.download_button.hide()
        self.asset=None
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
            self.asset=release.asset
            self.download_button.setVisible(self.asset is not None)
            self.download_button.setEnabled(self.asset is not None)
        else:
            self.status.setText(self.text("No newer version in this channel.", "نسخه جدیدتری در این کانال یافت نشد."))

    def start_download(self):
        if self.thread is not None or self.asset is None:
            return
        if QMessageBox.question(self,self.text("Download update","دریافت به‌روزرسانی"),
            self.text("Download the official installer? SHA-256 checks integrity, not publisher signature. The app will not execute or install it.",
                      "نصب‌کننده رسمی دریافت شود؟ SHA-256 سلامت فایل را بررسی می‌کند، نه امضای ناشر. برنامه آن را اجرا یا نصب نمی‌کند."))!=QMessageBox.StandardButton.Yes:
            return
        path,_=QFileDialog.getSaveFileName(self,self.text("Save installer","ذخیره نصب‌کننده"),self.asset.name,"Windows installer (*.exe)")
        if not path:
            return
        self.check.setEnabled(False)
        self.download_button.setEnabled(False)
        self.stop=Event()
        self.download_progress.setValue(0)
        self.download_progress.show()
        self.cancel_download_button.setEnabled(True)
        self.cancel_download_button.show()
        self.status.setText(self.text("Downloading and checking SHA-256…","در حال دریافت و بررسی SHA-256…"))
        self.thread=QThread(self)
        self.worker=DownloadWorker(self.asset,path,self.stop)
        self.worker.progress.connect(self.show_progress)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.download_result)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.cleanup)
        self.thread.start()

    @Slot(int,int)
    def show_progress(self,count,total):
        if self.stop is None or self.stop.is_set():
            return
        # 100% is reserved for successful integrity verification and publication.
        self.download_progress.setValue(min(99,count*100//total))
        self.status.setText(self.text("Downloaded: ","دریافت‌شده: ")+f"{count/1048576:.1f} / {total/1048576:.1f} MiB")

    def cancel_download(self):
        if self.stop is not None:
            self.stop.set()
            self.cancel_download_button.setEnabled(False)
            self.status.setText(self.text("Cancellation requested…","درخواست لغو دریافت…"))

    @Slot(object,str)
    def download_result(self,path,error):
        self.cancel_download_button.hide()
        if error=="cancelled":
            self.download_progress.hide()
            self.status.setText(self.text("Download cancelled; no installer saved.","دریافت لغو شد؛ نصب‌کننده ذخیره نشد."))
        elif error:
            self.download_progress.hide()
            self.status.setText(self.text("Download failed or integrity could not be verified. Existing files were not overwritten.",
                "دریافت ناموفق بود یا سلامت فایل تأیید نشد. فایل‌های موجود بازنویسی نشدند."))
        else:
            self.download_progress.setValue(100)
            self.status.setText(self.text("Downloaded; SHA-256 matches. Installer not executed. Verify publisher before running.",
                "فایل دریافت شد و SHA-256 منطبق است. نصب‌کننده اجرا نشده؛ پیش از اجرا ناشر را بررسی کنید.")+"\n"+str(path))

    @Slot()
    def cleanup(self):
        self.thread.deleteLater()
        self.thread = None
        self.worker = None
        self.stop = None
        self.cancel_download_button.hide()
        self.check.setEnabled(True)
        self.download_button.setEnabled(self.asset is not None)

    def done(self, result):
        if self.thread is not None:
            self.status.setText(self.text("Update operation is still running.", "عملیات به‌روزرسانی در حال انجام است."))
            return
        super().done(result)
