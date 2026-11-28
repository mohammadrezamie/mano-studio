"""Bilingual, non-destructive spotlight tour of actual workspace controls."""
from PySide6.QtCore import QEvent, QPoint, QRect, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from ui.theme import PALETTES

TOUR_KEY = "onboarding/tour_v1"
STEPS = (
    ("direction_box", ("Conversion direction", "جهت تبدیل"),
     ("Choose RTL to assembly, or assembly to canonical RTL.", "تبدیل RTL به اسمبلی یا اسمبلی به RTL استاندارد را انتخاب کنید.")),
    ("open_button", ("Open a file", "باز کردن فایل"),
     ("Import a text file, or type your own instructions in the input editor.", "فایل متنی را وارد کنید یا دستورهای خود را در ویرایشگر بنویسید.")),
    ("input_title", ("Input editor", "ویرایشگر ورودی"),
     ("Write instructions here. Code stays left-to-right in both interface languages.", "دستورها را اینجا بنویسید. کد در هر دو زبان از چپ به راست نمایش داده می‌شود.")),
    ("input_tabs", ("Input tools", "ابزارهای ورود دستور"),
     ("Use the editor, symbol keypad or guided instruction builder.", "از ویرایشگر، صفحه‌کلید نمادها یا سازنده دستور استفاده کنید.")),
    ("translate_button", ("Translate", "تبدیل"),
     ("Translate the current input. Diagnostics explain unsupported instructions.", "ورودی را تبدیل کنید. پیام‌های خطا دستورهای پشتیبانی‌نشده را توضیح می‌دهند.")),
    ("output_title", ("Output", "خروجی"),
     ("Review the generated code in the output editor.", "کد تولیدشده را در ویرایشگر خروجی بررسی کنید.")),
    ("export_button", ("Export", "ذخیره خروجی"),
     ("Save a successful translation to a text file.", "نتیجه تبدیل موفق را در فایل متنی ذخیره کنید.")),
    ("learning_button", ("Learning Center", "مرکز یادگیری"),
     ("Find lessons, Basic Computer and Digital Logic experiments.", "درس‌ها، کامپیوتر پایه و آزمایش‌های منطق دیجیتال را پیدا کنید.")),
    ("settings_button", ("Settings", "تنظیمات"),
     ("Change language and appearance, or explicitly check for updates.", "زبان و ظاهر را تغییر دهید یا به‌صورت اختیاری به‌روزرسانی را بررسی کنید.")),
    ("help_button", ("Help", "راهنما"),
     ("Replay this tour, view instruction reference and academic acknowledgments.", "آموزش را دوباره اجرا کنید، مرجع دستورها و تقدیر از استاد را ببینید.")),
)


class ProductTour(QWidget):
    """An overlay over the real controls, not a separate mock workspace."""
    def __init__(self, workspace):
        super().__init__(workspace.centralWidget())
        self.workspace = workspace
        self.root = workspace.centralWidget()
        self.fa = workspace.language == "fa"
        self.index = 0
        self.finished = False
        self.target_rect = QRect()
        self.previous_focus = QApplication.focusWidget()
        self.setObjectName("productTour")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if self.fa else Qt.LayoutDirection.LeftToRight)
        self.card = QFrame(self)
        self.card.setObjectName("editorPanel")
        bg, panel, raised, fg, muted, accent, border = PALETTES[workspace.theme]
        self.card.setStyleSheet(f"QFrame#editorPanel {{background: {panel}; border: 1px solid {accent}; border-radius: 12px;}}")
        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(16, 12, 16, 12)
        self.counter = QLabel()
        self.counter.setObjectName("muted")
        layout.addWidget(self.counter)
        self.title = QLabel()
        self.title.setObjectName("section")
        self.title.setWordWrap(True)
        layout.addWidget(self.title)
        self.description = QLabel()
        self.description.setWordWrap(True)
        layout.addWidget(self.description)
        row = QHBoxLayout()
        self.skip = QPushButton("رد کردن" if self.fa else "Skip tour")
        self.back = QPushButton("قبلی" if self.fa else "Back")
        self.next = QPushButton()
        self.next.setObjectName("primary")
        self.skip.clicked.connect(lambda: self.finish("skipped"))
        self.back.clicked.connect(lambda: self.move(-1))
        self.next.clicked.connect(lambda: self.move(1))
        row.addWidget(self.skip)
        row.addStretch()
        row.addWidget(self.back)
        row.addWidget(self.next)
        layout.addLayout(row)
        self.root.installEventFilter(self)
        QApplication.instance().installEventFilter(self)
        self.setGeometry(self.root.rect())
        self.show()
        self.raise_()
        self.render_step(1)
        if not self.finished:
            self.next.setFocus()

    def target(self, index):
        name = STEPS[index][0]
        if name == "input_tabs":
            return self.workspace.tabs.tabBar()
        return getattr(self.workspace, name, None)

    def locate(self, index):
        target = self.target(index)
        if target is None or not target.isVisible():
            return QRect()
        rect = QRect(target.mapTo(self.root, QPoint(0, 0)), target.size())
        return rect.adjusted(-5, -5, 5, 5).intersected(self.rect())

    def move(self, direction):
        self.index += direction
        self.render_step(direction)

    def render_step(self, direction=1):
        if self.finished:
            return
        while 0 <= self.index < len(STEPS):
            self.target_rect = self.locate(self.index)
            if not self.target_rect.isEmpty():
                break
            self.index += direction
        if self.index >= len(STEPS):
            self.finish("completed")
            return
        if self.index < 0:
            self.index = 0
            self.render_step(1)
            return
        _, title, description = STEPS[self.index]
        self.title.setText(title[self.fa])
        self.description.setText(description[self.fa])
        self.counter.setText(f"مرحله {self.index+1} از {len(STEPS)}" if self.fa
                             else f"Step {self.index+1} of {len(STEPS)}")
        self.back.setEnabled(any(not self.locate(i).isEmpty() for i in range(self.index)))
        self.next.setText(("پایان" if self.fa else "Finish") if self.index == len(STEPS)-1
                          else ("بعدی" if self.fa else "Next"))
        self.position_card()
        self.update()

    def position_card(self):
        margin = 12
        width = max(1, min(400, self.width()-2*margin))
        self.card.setFixedWidth(width)
        self.card.layout().activate()
        height = min(self.card.sizeHint().height(), max(1, self.height()-2*margin))
        target = self.target_rect
        x = target.right()-width+1 if self.fa else target.left()
        x = max(margin, min(x, self.width()-width-margin))
        below = target.bottom()+margin
        above = target.top()-height-margin
        y = below if below+height <= self.height()-margin else above
        if y < margin:
            y = max(margin, min((self.height()-height)//2, self.height()-height-margin))
            # If vertical placement cannot avoid the target, try its other side.
            right = target.right()+margin
            left = target.left()-width-margin
            if right+width <= self.width()-margin:
                x = right
            elif left >= margin:
                x = left
        self.card.setGeometry(x, y, width, height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        shade = QPainterPath()
        from PySide6.QtCore import QRectF
        shade.addRect(QRectF(self.rect()))
        shade.addRoundedRect(QRectF(self.target_rect), 7, 7)
        shade.setFillRule(Qt.FillRule.OddEvenFill)
        painter.fillPath(shade, QColor(0, 0, 0, 180))
        painter.setPen(QPen(QColor(PALETTES[self.workspace.theme][5]), 2))
        painter.drawRoundedRect(self.target_rect, 7, 7)
        painter.end()

    def eventFilter(self, obj, event):
        if self.finished:
            return False
        kind = event.type()
        if obj is self.root and kind in (QEvent.Type.Resize, QEvent.Type.LayoutRequest):
            self.setGeometry(self.root.rect())
            self.render_step()
            return False
        if kind == QEvent.Type.Shortcut:
            # Existing workspace shortcuts must not execute through the overlay.
            parent = obj
            while parent is not None:
                if parent is self.workspace:
                    return True
                parent = parent.parent()
        if isinstance(obj, QWidget) and (obj is self.workspace or self.workspace.isAncestorOf(obj)):
            inside = obj is self or self.isAncestorOf(obj)
            if kind == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
                self.finish("skipped")
                return True
            if kind == QEvent.Type.KeyPress and inside and event.key() in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
                controls = [button for button in (self.skip, self.back, self.next) if button.isEnabled()]
                focus = QApplication.focusWidget()
                delta = -1 if event.key() == Qt.Key.Key_Backtab or event.modifiers() & Qt.KeyboardModifier.ShiftModifier else 1
                index = controls.index(focus) if focus in controls else -1
                controls[(index+delta) % len(controls)].setFocus()
                return True
            if not inside and kind in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease,
                                       QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease,
                                       QEvent.Type.MouseButtonDblClick, QEvent.Type.Wheel):
                return True
        return False

    def finish(self, outcome):
        if self.finished:
            return
        self.finished = True
        self.workspace.settings.setValue(TOUR_KEY, outcome)
        self.workspace.settings.sync()
        self.root.removeEventFilter(self)
        QApplication.instance().removeEventFilter(self)
        self.hide()
        self.workspace.product_tour = None
        if self.previous_focus is not None and self.previous_focus.isVisible():
            self.previous_focus.setFocus()
        self.deleteLater()
