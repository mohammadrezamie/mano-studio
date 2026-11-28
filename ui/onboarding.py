"""First-run language choice and a short, bilingual workspace introduction."""
from pathlib import Path
import sys
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton,
                               QButtonGroup, QPushButton, QProgressBar, QFrame, QSizePolicy)
from onboarding_state import LAST_PAGE, read_state, save_state
from ui.brand import BrandMark
from ui.credits import THANKS
from ui.typography import apply_ui_font

PAGES = (
    (("Choose your language", "زبان خود را انتخاب کنید"),
     ("Select English or Persian. All following steps use your choice.",
      "انگلیسی یا فارسی را انتخاب کنید. مراحل بعدی به زبان انتخابی نمایش داده می‌شوند.")),
    (("Welcome to Mano Studio", "به مانو استودیو خوش آمدید"),
     ("Explore computer architecture through one offline learning workspace.",
      "معماری کامپیوتر را در یک محیط آموزشی آفلاین تجربه کنید.")),
    (("RTL Studio", "محیط RTL"),
     ("Write register-transfer instructions, use the symbol pad or guided builder, and translate to assembly. Reverse mode produces canonical RTL.",
      "دستورهای انتقال ثبات را بنویسید، از صفحه‌کلید نمادها یا سازنده دستور استفاده کنید و به اسمبلی تبدیل کنید. حالت معکوس، RTL استاندارد تولید می‌کند.")),
    (("Basic Computer", "کامپیوتر پایه"),
     ("Assemble and step through programs. Inspect registers, memory and machine activity.",
      "برنامه را اسمبل و مرحله‌به‌مرحله اجرا کنید. ثبات‌ها، حافظه و فعالیت ماشین را بررسی کنید.")),
    (("Digital Logic Lab", "آزمایشگاه منطق دیجیتال"),
     ("Explore gates, circuits, Boolean expressions and truth tables.",
      "گیت‌ها، مدارها، عبارت‌های بولی و جدول‌های درستی را بررسی کنید.")),
    (("Learning Center", "مرکز یادگیری"),
     ("Discover textbook-aligned activities and practice locally. You can start exploring now.",
      "فعالیت‌های مرتبط با کتاب درسی را پیدا کنید و به‌صورت محلی تمرین کنید. اکنون آماده شروع هستید.")),
)


PREVIEWS = {2: ("editor.png", "persian.png"), 3: ("computer.png", "computer.png"),
            4: ("logic.png", "logic.png"), 5: ("learning.png", "learning.png")}


def preview_path(page, language):
    """Resolve shipped, verified captures without accessing the network."""
    names = PREVIEWS.get(page)
    if names is None:
        return None
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return root / "docs" / "assets" / "onboarding" / names[language == "fa"]


class Onboarding(QDialog):
    def __init__(self, settings, theme="dark", parent=None):
        super().__init__(parent)
        self.settings = settings
        self.state = read_state(settings)
        self.setWindowTitle("Mano Studio")
        self.resize(660, 620)
        self.setMinimumWidth(380)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        mark = BrandMark(theme, self)
        mark.setFixedSize(72, 72)
        mark.set_appearance(theme, settings.value("glass_enabled", True, type=bool), True)
        outer.addWidget(mark, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.title = QLabel()
        self.title.setObjectName("hero")
        self.title.setWordWrap(True)
        outer.addWidget(self.title)
        self.description = QLabel()
        self.description.setWordWrap(True)
        outer.addWidget(self.description)
        self.languages = QFrame()
        choice = QVBoxLayout(self.languages)
        self.group = QButtonGroup(self)
        self.options = {}
        for language, label in (("en", "English"), ("fa", "فارسی")):
            option = QRadioButton(label)
            option.setAccessibleName(label)
            option.setChecked(self.state.language == language)
            self.group.addButton(option)
            self.options[language] = option
            choice.addWidget(option)
            option.toggled.connect(lambda checked, lang=language: self.choose(lang) if checked else None)
        outer.addWidget(self.languages)
        self.credits = QLabel()
        self.credits.setWordWrap(True)
        self.credits.setObjectName("muted")
        outer.addWidget(self.credits)
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        self.preview.setFixedHeight(230)
        outer.addWidget(self.preview)
        self.preview_caption = QLabel()
        self.preview_caption.setWordWrap(True)
        self.preview_caption.setObjectName("muted")
        outer.addWidget(self.preview_caption)
        self.preview_pixmap = QPixmap()
        outer.addStretch()
        self.progress = QProgressBar()
        self.progress.setRange(1, LAST_PAGE + 1)
        self.progress.setTextVisible(False)
        outer.addWidget(self.progress)
        self.counter = QLabel()
        outer.addWidget(self.counter)
        row = QHBoxLayout()
        self.previous = QPushButton()
        self.previous.clicked.connect(self.back)
        row.addWidget(self.previous)
        row.addStretch()
        self.next = QPushButton()
        self.next.setObjectName("primary")
        self.next.setDefault(True)
        self.next.clicked.connect(self.advance)
        row.addWidget(self.next)
        outer.addLayout(row)
        self.render()

    def choose(self, language):
        self.state = self.state.choose(language)
        save_state(self.settings, self.state)
        self.render()

    def back(self):
        self.state = self.state.back()
        save_state(self.settings, self.state)
        self.render()

    def advance(self):
        if self.state.page == LAST_PAGE:
            self.state = self.state.finish()
            save_state(self.settings, self.state)
            self.accept()
            return
        self.state = self.state.advance()
        save_state(self.settings, self.state)
        self.render()

    def render(self):
        fa = self.state.language == "fa"
        apply_ui_font(QApplication.instance(), self.state.language)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if fa else Qt.LayoutDirection.LeftToRight)
        title, description = PAGES[self.state.page]
        self.title.setText(title[fa])
        self.description.setText(description[fa])
        self.languages.setVisible(self.state.page == 0)
        self.credits.setText(THANKS[fa])
        self.credits.setVisible(self.state.page == 1)
        path = preview_path(self.state.page, self.state.language)
        self.preview_pixmap = QPixmap(str(path)) if path is not None else QPixmap()
        available = not self.preview_pixmap.isNull()
        self.preview.setVisible(available)
        self.preview_caption.setVisible(available)
        if available:
            caption = ("نمای واقعی نسخه آزمایشی؛ تصویر انگلیسی" if fa and self.state.page != 2
                       else "نمای واقعی نسخه آزمایشی" if fa else "Actual candidate workspace preview")
            self.preview_caption.setText(caption)
            self.preview.setAccessibleName(title[fa] + " — " + caption)
            self.scale_preview()
        else:
            self.preview.clear()
        self.progress.setValue(self.state.page + 1)
        self.counter.setText(f"مرحله {self.state.page+1} از {LAST_PAGE+1}" if fa
                             else f"Step {self.state.page+1} of {LAST_PAGE+1}")
        self.previous.setText("قبلی" if fa else "Back")
        self.previous.setEnabled(self.state.page > 0)
        self.next.setText(("شروع کار" if fa else "Start using Mano Studio")
                          if self.state.page == LAST_PAGE else ("بعدی" if fa else "Next"))

    def scale_preview(self):
        if self.preview_pixmap.isNull():
            return
        width = max(1, self.contentsRect().width()-48)
        self.preview.setPixmap(self.preview_pixmap.scaled(
            QSize(width, self.preview.height()), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "preview_pixmap"):
            self.scale_preview()

    def reject(self):
        save_state(self.settings, self.state)
        super().reject()
