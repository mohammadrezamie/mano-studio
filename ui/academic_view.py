"""Instructor-facing read-only viewer for the exact independent Python file."""
import io
import keyword
import tokenize
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase, QColor, QTextCharFormat, QSyntaxHighlighter
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QPushButton, QFileDialog, QMessageBox, QPlainTextEdit, QApplication)
from academic_source import read_source, export_source
from ui.code_editor import CodeEditor
from ui.theme import SYNTAX


class PythonHighlighter(QSyntaxHighlighter):
    """Tokenize the immutable full source, including multiline strings."""
    def __init__(self, document, text, theme):
        super().__init__(document)
        lines = text.splitlines()
        self.ranges = {}
        colors = SYNTAX[theme]
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            color = (colors[0] if token.type == tokenize.NAME and keyword.iskeyword(token.string)
                     else colors[1] if token.type == tokenize.STRING
                     else colors[2] if token.type == tokenize.COMMENT else None)
            if color is None:
                continue
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            for row in range(token.start[0], token.end[0]+1):
                if not 1 <= row <= len(lines):
                    continue
                line = lines[row-1]
                start = token.start[1] if row == token.start[0] else 0
                end = token.end[1] if row == token.end[0] else len(line)
                offset = len(line[:start].encode("utf-16-le"))//2
                length = len(line[start:end].encode("utf-16-le"))//2
                if length:
                    self.ranges.setdefault(row-1, []).append((offset, length, fmt))
        self.rehighlight()

    def highlightBlock(self, _text):
        for start, length, fmt in getattr(self, "ranges", {}).get(self.currentBlock().blockNumber(), ()):
            self.setFormat(start, length, fmt)


class AcademicSourceDialog(QDialog):
    def __init__(self, parent, theme, fa=False):
        super().__init__(parent)
        self.fa=fa
        self.raw=read_source()
        text=self.raw.decode("utf-8-sig")
        self.setWindowTitle(self.t("Academic translator source","سورس دانشگاهی مترجم"))
        self.resize(900,650)
        outer=QVBoxLayout(self)
        outer.setSpacing(12)
        banner=QFrame()
        banner.setObjectName("glassBar")
        header=QVBoxLayout(banner)
        title=QLabel("rtl_translator.py")
        title.setObjectName("hero")
        title.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        header.addWidget(title)
        subtitle=QLabel(self.t("One standalone Python file · standard library only · no GUI dependencies",
            "یک فایل مستقل پایتون · فقط کتابخانه استاندارد · بدون وابستگی به رابط گرافیکی"))
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        header.addWidget(subtitle)
        outer.addWidget(banner)
        note=QLabel(self.t("Read RTL → match Mano instructions → validate addresses → write Assembly. This is the exact bundled source, not a simplified substitute.",
            "خواندن RTL ← تطبیق دستورات مانو ← اعتبارسنجی آدرس‌ها ← تولید اسمبلی. این همان فایل اصلی همراه برنامه است، نه نسخه ساده‌شده."))
        note.setWordWrap(True)
        outer.addWidget(note)
        self.editor=CodeEditor()
        self.editor.setReadOnly(True)
        self.editor.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        option=self.editor.document().defaultTextOption()
        option.setTextDirection(Qt.LayoutDirection.LeftToRight)
        self.editor.document().setDefaultTextOption(option)
        self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        font=QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(12)
        self.editor.setFont(font)
        self.editor.setPlainText(text)
        self.editor.resize_gutter()
        self.editor.highlighter=PythonHighlighter(self.editor.document(),text,theme)
        self.editor.setAccessibleName("rtl_translator.py")
        outer.addWidget(self.editor,1)
        command=QLabel("python rtl_translator.py input.rtl -o output.asm")
        command.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        command.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        command.setFont(font)
        outer.addWidget(command)
        actions=QHBoxLayout()
        self.status=QLabel(self.t("Read-only preview","پیش‌نمایش فقط خواندنی"))
        self.status.setWordWrap(True)
        actions.addWidget(self.status,1)
        copy=QPushButton(self.t("Copy source","کپی سورس"))
        copy.clicked.connect(self.copy_source)
        actions.addWidget(copy)
        self.save_button=QPushButton(self.t("Save Python file…","ذخیره فایل پایتون…"))
        self.save_button.setObjectName("primary")
        self.save_button.clicked.connect(self.save_source)
        actions.addWidget(self.save_button)
        close=QPushButton(self.t("Close","بستن"))
        close.clicked.connect(self.reject)
        actions.addWidget(close)
        outer.addLayout(actions)

    def t(self,en,fa):
        return fa if self.fa else en

    def copy_source(self):
        QApplication.clipboard().setText(self.raw.decode("utf-8-sig"))
        self.status.setText(self.t("Source copied","سورس کپی شد"))

    def save_source(self):
        name,_=QFileDialog.getSaveFileName(self,self.t("Save exact Python source","ذخیره سورس اصلی پایتون"),
            "rtl_translator.py","Python (*.py)")
        if not name:
            return
        try:
            export_source(name,data=self.raw)
        except (OSError,ValueError):
            QMessageBox.warning(self,self.t("Cannot save","ذخیره ناموفق"),
                self.t("Choose a writable .py destination outside the installed source.",
                       "یک مسیر قابل نوشتن با پسوند .py خارج از فایل نصب‌شده انتخاب کنید."))
            return
        self.status.setText(self.t("Exact Python file saved","فایل اصلی پایتون ذخیره شد"))
