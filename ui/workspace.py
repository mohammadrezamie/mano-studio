"""Workspace UI. All translation is delegated to rtl_translator.py."""
from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFontDatabase, QTextCursor, QTextCharFormat, QSyntaxHighlighter, QColor, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QComboBox,
    QPlainTextEdit, QLineEdit, QCheckBox, QTabWidget, QSplitter, QVBoxLayout,
    QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox, QDialog, QAbstractItemView, QScrollArea, QFrame,
)
import re
from rtl_translator import translate
from instruction_catalog import TEMPLATES, build_rtl
from ui.strings import FA, HELP, NAMES, EN_NAMES
from ui.theme import PALETTES, stylesheet
from ui.code_editor import CodeEditor
from ui.glass import GlassRoot

LTR = Qt.LayoutDirection.LeftToRight


class CodeHighlighter(QSyntaxHighlighter):
    def highlightBlock(self, text):
        for pattern, color in [(r"\b(?:AC|PC|AR|DR|IR|TR|E|INPR|OUTR|IEN|FGI|FGO|S|M|IF|THEN|AND|ADD|LDA|STA|BUN|BSA|ISZ|CLA|CLE|CMA|CME|CIR|CIL|INC|SPA|SNA|SZA|SZE|HLT|INP|OUT|SKI|SKO|ION|IOF)\b", "#488ed1"),
                               (r"←|<-|=|∧|¬|\+", "#a875ce"),
                               (r"[#;].*$", "#8996a5")]:
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            for match in re.finditer(pattern, text, re.I):
                self.setFormat(match.start(), match.end() - match.start(), fmt)


def code_editor(readonly=False):
    editor = CodeEditor()
    editor.setReadOnly(readonly)
    editor.setLayoutDirection(LTR)
    option = editor.document().defaultTextOption()
    option.setTextDirection(LTR)
    editor.document().setDefaultTextOption(option)
    editor.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
    editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
    editor.resize_gutter()
    editor.highlighter = CodeHighlighter(editor.document())
    return editor


class Workspace(QMainWindow):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.language = settings.value("language", "en")
        if self.language not in ("en", "fa"):
            self.language = "en"
        self.theme = settings.value("theme", "dark")
        if self.theme not in PALETTES:
            self.theme = "dark"
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if self.language == "fa" else LTR)
        self.path = None
        self.result = None
        self.translated_source = None
        self.labels = []
        self.setWindowTitle("Mano Studio")
        self.resize(1240, 790)
        root = GlassRoot(self.theme, settings.value("glass_enabled", True, type=bool))
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(16, 14, 16, 10)
        layout.setSpacing(10)
        header_frame = QFrame()
        header_frame.setObjectName("glassBar")
        header = QHBoxLayout(header_frame)
        brand = QLabel("MANO STUDIO")
        brand.setObjectName("brand")
        header.addWidget(brand)
        header.addWidget(self.label("Build. Translate. Learn.", "subtitle"))
        header.addStretch()
        self.languages = QComboBox()
        self.languages.addItem("English", "en")
        self.languages.addItem("فارسی", "fa")
        self.languages.setCurrentIndex(1 if self.language == "fa" else 0)
        self.languages.currentIndexChanged.connect(self.change_language)
        header.addWidget(self.languages)
        self.themes = QComboBox()
        for name in ("Light", "Dark", "Night"):
            self.themes.addItem(self.t(name), name.lower())
        self.themes.setCurrentIndex(max(0, self.themes.findData(self.theme)))
        self.themes.currentIndexChanged.connect(self.change_theme)
        header.addWidget(self.themes)
        header.addWidget(self.button("Settings", self.open_preferences))
        layout.addWidget(header_frame)
        toolbar_frame = QFrame()
        toolbar_frame.setObjectName("glassBar")
        toolbar = QHBoxLayout(toolbar_frame)
        for name, slot in [("New", self.new_file), ("Open RTL", self.open_file),
                           ("Save RTL", self.save_file), ("Export ASM", self.export_file),
                           ("Source", self.show_source), ("Live Lab", self.open_lab), ("About", self.about)]:
            toolbar.addWidget(self.button(name, slot))
        toolbar.addWidget(self.button("Program Lab", self.open_program_lab))
        toolbar.addStretch()
        toolbar.addWidget(self.button("Translate", self.run_translation, True))
        layout.addWidget(toolbar_frame)
        split = QSplitter(Qt.Orientation.Vertical)
        editors = QSplitter(Qt.Orientation.Horizontal)
        self.editor, self.output = code_editor(), code_editor(True)
        for title, editor in [("RTL input", self.editor), ("Assembly output", self.output)]:
            pane = QWidget()
            box = QVBoxLayout(pane)
            box.addWidget(self.label(title, "section"))
            box.addWidget(editor)
            editors.addWidget(pane)
        editors.setSizes([600, 600])
        split.addWidget(editors)
        self.tabs = QTabWidget()
        page = QWidget()
        row = QHBoxLayout(page)
        row.addWidget(self.button("Undo", self.editor.undo))
        row.addWidget(self.button("Redo", self.editor.redo))
        row.addStretch()
        row.addWidget(self.button("Translate", self.run_translation, True))
        self.tabs.addTab(page, self.t("Editor"))
        self.tabs.addTab(self.pad(), self.t("Symbol pad"))
        self.tabs.addTab(self.builder(), self.t("Builder"))
        self.tabs.setCurrentIndex(max(0, min(2, int(settings.value("input_mode", 0)))))
        self.tabs.currentChanged.connect(lambda n: settings.setValue("input_mode", n))
        split.addWidget(self.tabs)
        diagnostics = QWidget()
        dl = QVBoxLayout(diagnostics)
        dl.addWidget(self.label("Diagnostics", "section"))
        self.table = QTableWidget(0, 4)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.cellClicked.connect(self.jump_error)
        dl.addWidget(self.table)
        split.addWidget(diagnostics)
        split.setSizes([320, 260, 130])
        layout.addWidget(split, 1)
        self.editor.textChanged.connect(self.invalidate)
        self.shortcut = QShortcut(QKeySequence("F5"), self)
        self.shortcut.activated.connect(self.run_translation)
        self.relabel()
        self.statusBar().showMessage(self.t("Ready"))
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

    def t(self, text):
        return FA.get(text, text) if self.language == "fa" else text

    def label(self, key, object_name=""):
        widget = QLabel(self.t(key))
        widget.setObjectName(object_name)
        self.labels.append((widget, key))
        return widget

    def button(self, key, action, primary=False):
        widget = QPushButton(self.t(key))
        if primary:
            widget.setObjectName("primary")
        widget.clicked.connect(lambda checked=False: action())
        self.labels.append((widget, key))
        return widget

    def pad(self):
        page = QWidget()
        grid = QGridLayout(page)
        tokens = ["AC", "PC", "AR", "DR", "E", "IR", "TR", "INPR", "OUTR", "IEN",
                  "FGI", "FGO", "S", "M[", "]", "[", "←", "=", "+", "∧", "¬", "(",
                  ")", ":", ",", "IF ", " THEN ", "CIR", "CIL", "0", "1", "2", "3",
                  "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
        for index, token in enumerate(tokens):
            button = QPushButton(token.strip())
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.clicked.connect(lambda checked=False, value=token: self.insert(value))
            grid.addWidget(button, index // 10, index % 10)
        for index, (title, action) in enumerate([
            ("Space", lambda: self.insert(" ")), ("Enter", lambda: self.insert("\n")),
            ("Backspace", lambda: self.move_cursor("delete")), ("◀", lambda: self.move_cursor("left")),
            ("▶", lambda: self.move_cursor("right")), ("Undo", self.editor.undo),
            ("Redo", self.editor.redo), ("Translate", self.run_translation)]):
            grid.addWidget(self.button(title, action), 5, index)
        return page

    def insert(self, value):
        self.editor.insertPlainText(value)
        self.editor.setFocus()

    def move_cursor(self, direction):
        cursor = self.editor.textCursor()
        if direction == "delete":
            if cursor.hasSelection():
                cursor.removeSelectedText()
            else:
                cursor.deletePreviousChar()
        else:
            cursor.movePosition(QTextCursor.MoveOperation.Left if direction == "left" else QTextCursor.MoveOperation.Right)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def builder(self):
        page = QWidget()
        box = QVBoxLayout(page)
        top = QHBoxLayout()
        self.operations = QComboBox()
        for name in TEMPLATES:
            self.operations.addItem(name, name)
        top.addWidget(self.label("Instruction"))
        top.addWidget(self.operations, 2)
        top.addWidget(self.label("Address (HEX)"))
        self.address = QLineEdit("100")
        self.address.setLayoutDirection(LTR)
        self.address.setMaxLength(3)
        top.addWidget(self.address)
        self.indirect = QCheckBox(self.t("Indirect"))
        self.labels.append((self.indirect, "Indirect"))
        top.addWidget(self.indirect)
        box.addLayout(top)
        pad = QGridLayout()
        for i, token in enumerate("0123456789ABCDEF"):
            b = QPushButton(token)
            b.clicked.connect(lambda checked=False, value=token: self.address.insert(value))
            pad.addWidget(b, i // 8, i % 8)
        pad.addWidget(self.button("Backspace", self.address.backspace), 0, 8)
        pad.addWidget(self.button("Clear", self.address.clear), 1, 8)
        box.addLayout(pad)
        self.preview = QLabel()
        self.preview.setLayoutDirection(LTR)
        self.preview.setWordWrap(True)
        box.addWidget(self.preview)
        row = QHBoxLayout()
        row.addWidget(self.button("Insert instruction", self.insert_instruction, True))
        row.addWidget(self.button("Replace line", lambda: self.edit_line("replace")))
        row.addWidget(self.button("Delete line", lambda: self.edit_line("delete")))
        row.addWidget(self.button("Move up", lambda: self.edit_line("up")))
        row.addWidget(self.button("Move down", lambda: self.edit_line("down")))
        box.addLayout(row)
        self.operations.currentIndexChanged.connect(self.update_preview)
        self.address.textChanged.connect(self.update_preview)
        self.indirect.toggled.connect(self.update_preview)
        self.update_preview()
        return page

    def template(self):
        name = self.operations.currentData()
        memory = "{a}" in TEMPLATES[name]
        return build_rtl(name, self.address.text() if memory else "",
                         self.indirect.isChecked() if memory else False)

    def update_preview(self):
        memory = "{a}" in TEMPLATES[self.operations.currentData()]
        self.address.setEnabled(memory)
        self.indirect.setEnabled(memory)
        try:
            rtl = self.template()
            self.preview.setText(rtl + "    →    " + translate(rtl).assembly)
        except ValueError:
            self.preview.setText(self.t("Choose 000–FFF."))

    def insert_instruction(self):
        try:
            rtl = self.template()
        except ValueError:
            QMessageBox.warning(self, self.t("Invalid address"), self.t("Choose 000–FFF."))
            return
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
        prefix = "\n" if cursor.block().text().strip() else ""
        cursor.insertText(prefix + rtl + "\n")
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def edit_line(self, operation):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber()
        lines = self.editor.toPlainText().split("\n")
        if operation == "replace":
            try:
                lines[line] = self.template()
            except ValueError:
                QMessageBox.warning(self, self.t("Invalid address"), self.t("Choose 000–FFF."))
                return
        elif operation == "delete":
            lines.pop(line)
            line = max(0, min(line, len(lines) - 1))
        else:
            target = line + (-1 if operation == "up" else 1)
            if not 0 <= target < len(lines):
                return
            lines[line], lines[target] = lines[target], lines[line]
            line = target
        cursor.beginEditBlock()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.insertText("\n".join(lines))
        cursor.endEditBlock()
        self.goto_line(line + 1, 1)

    def invalidate(self):
        self.result = None
        self.translated_source = None
        self.output.clear()
        self.table.setRowCount(0)
        self.editor.mark_errors(())
        self.statusBar().showMessage(self.t("Input changed — translate again"))

    def run_translation(self):
        source = self.editor.toPlainText()
        self.result = translate(source)
        self.translated_source = source
        self.output.setPlainText(self.result.assembly if self.result.ok else "")
        self.render_errors()
        self.statusBar().showMessage(self.t("Translation successful" if self.result.ok else "Translation failed"))

    def render_errors(self):
        errors = self.result.diagnostics if self.result else ()
        self.table.setRowCount(len(errors))
        self.editor.mark_errors(errors)
        for row, error in enumerate(errors):
            help_text = HELP.get(error.code, (error.message, error.message))[self.language == "fa"]
            for column, value in enumerate((error.line, error.column, error.code, help_text)):
                item = QTableWidgetItem(str(value))
                item.setToolTip(str(value))
                self.table.setItem(row, column, item)
        self.table.resizeRowsToContents()

    def goto_line(self, line, column):
        block = self.editor.document().findBlockByNumber(line - 1)
        if block.isValid():
            cursor = QTextCursor(block)
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, max(0, column - 1))
            self.editor.setTextCursor(cursor)
            self.editor.centerCursor()
            self.editor.setFocus()

    def jump_error(self, row, column):
        if self.result and row < len(self.result.diagnostics):
            error = self.result.diagnostics[row]
            self.goto_line(error.line, error.column)

    def relabel(self):
        for widget, key in self.labels:
            widget.setText(self.t(key))
        for index, title in enumerate(("Editor", "Symbol pad", "Builder")):
            self.tabs.setTabText(index, self.t(title))
        for index, title in enumerate(("Light", "Dark", "Night")):
            self.themes.setItemText(index, self.t(title))
        names = NAMES if self.language == "fa" else EN_NAMES
        for index, mnemonic in enumerate(TEMPLATES):
            self.operations.setItemText(index, f"{mnemonic} — {names[mnemonic]}")
        self.table.setHorizontalHeaderLabels([self.t(k) for k in ("Line", "Column", "Code", "Help")])
        self.render_errors()
        self.update_preview()

    def change_language(self):
        self.language = self.languages.currentData()
        self.settings.setValue("language", self.language)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if self.language == "fa" else LTR)
        self.relabel()
        self.statusBar().showMessage(self.t("Ready"))

    def change_theme(self):
        self.theme = self.themes.currentData()
        self.settings.setValue("theme", self.theme)
        self.apply_appearance()

    def apply_appearance(self):
        enabled = self.settings.value("glass_enabled", True, type=bool)
        QApplication.instance().setStyleSheet(stylesheet(self.theme, enabled))
        self.centralWidget().theme = self.theme
        self.centralWidget().enabled = enabled
        self.centralWidget().update()

    def open_preferences(self):
        from ui.preferences import Preferences
        Preferences(self).exec()

    def confirm_discard(self):
        if not self.editor.document().isModified():
            return True
        choice = QMessageBox.question(self, self.t("Unsaved changes"), self.t("Save your changes before continuing?"),
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
        if choice == QMessageBox.StandardButton.Save:
            return self.save_file()
        return choice == QMessageBox.StandardButton.Discard

    def new_file(self):
        if self.confirm_discard():
            self.path = None
            self.editor.clear()
            self.editor.document().setModified(False)

    def open_file(self):
        if not self.confirm_discard():
            return
        name, _ = QFileDialog.getOpenFileName(self, self.t("Open RTL"), "", "RTL (*.rtl *.txt);;All files (*)")
        if not name:
            return
        try:
            value = Path(name).read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            QMessageBox.warning(self, self.t("File error"), str(exc))
            return
        self.path = Path(name)
        self.editor.setPlainText(value)
        self.editor.document().setModified(False)

    def save_file(self):
        path = self.path
        if path is None:
            name, _ = QFileDialog.getSaveFileName(self, self.t("Save RTL"), "", "RTL (*.rtl);;Text (*.txt)")
            if not name:
                return False
            path = Path(name)
            if not path.suffix:
                path = path.with_suffix(".rtl")
        try:
            path.write_text(self.editor.toPlainText(), encoding="utf-8")
        except OSError as exc:
            QMessageBox.warning(self, self.t("File error"), str(exc))
            return False
        self.path = path
        self.editor.document().setModified(False)
        return True

    def export_file(self):
        if self.result is None or not self.result.ok or self.translated_source != self.editor.toPlainText():
            QMessageBox.warning(self, self.t("No valid output"), self.t("Translate the input successfully before exporting."))
            return
        name, _ = QFileDialog.getSaveFileName(self, self.t("Export ASM"), "", "Assembly (*.asm)")
        if not name:
            return
        path = Path(name)
        if not path.suffix:
            path = path.with_suffix(".asm")
        try:
            if self.path and path.resolve() == self.path.resolve():
                raise OSError("Input and output must be different files")
            path.write_text(self.result.assembly + ("\n" if self.result.instructions else ""), encoding="utf-8")
        except OSError as exc:
            QMessageBox.warning(self, self.t("File error"), str(exc))

    def show_source(self):
        import sys
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
        try:
            source = (base / "rtl_translator.py").read_text(encoding="utf-8")
        except OSError as exc:
            QMessageBox.warning(self, self.t("File error"), str(exc))
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("rtl_translator.py")
        dialog.resize(850, 640)
        layout = QVBoxLayout(dialog)
        editor = code_editor(True)
        editor.setPlainText(source)
        layout.addWidget(editor)
        copy = QPushButton(self.t("Copy"))
        copy.clicked.connect(lambda: QApplication.clipboard().setText(source))
        layout.addWidget(copy)
        dialog.exec()

    def open_program_lab(self):
        from ui.program_lab import ProgramLab
        result = translate(self.editor.toPlainText())
        if not result.ok:
            self.run_translation()
            return
        ProgramLab(self, result.assembly).exec()

    def open_lab(self):
        from ui.live_lab import LabDialog
        LabDialog(self, self.language, self.theme, self.settings).exec()

    def about(self):
        QMessageBox.about(self, "Mano Studio", "Mano Studio · 0.3.0-dev\n" + self.t("Academic project · Morris Mano Basic Computer") + "\nMIT · " + self.t("Open source") + "\nhttps://github.com/mohammadrezamie/mano-studio")

    def closeEvent(self, event):
        if not self.confirm_discard():
            event.ignore()
            return
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.sync()
        event.accept()
