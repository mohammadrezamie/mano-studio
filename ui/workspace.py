"""Workspace UI. All translation is delegated to rtl_translator.py."""
from pathlib import Path
from ui.motion import MotionTabs, set_reduced_motion
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFontDatabase, QTextCursor, QTextCharFormat, QSyntaxHighlighter, QColor, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QComboBox,
    QPlainTextEdit, QLineEdit, QCheckBox, QTabWidget, QSplitter, QVBoxLayout,
    QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox, QAbstractItemView, QScrollArea, QFrame, QMenu, QDialog, QDialogButtonBox,
)
import re
from rtl_translator import translate
from asm_to_rtl import reverse_translate
from update_service import VERSION
from instruction_catalog import TEMPLATES, build_rtl
from example_catalog import EXAMPLES, computer_source
from ui.strings import FA, HELP, NAMES, EN_NAMES
from ui.theme import PALETTES, SYNTAX, apply_theme
from ui.icons import icon
from ui.brand import BrandMark, brand_icon
from ui.credits import COPYRIGHT, REPOSITORY, THANKS, PURPOSE, LICENSE_NOTE, ACADEMIC_ACKNOWLEDGMENT, COURSE, INSTITUTION, REFERENCE
from ui.localization import error_text
from ui.code_editor import CodeEditor
from ui.glass import GlassRoot

LTR = Qt.LayoutDirection.LeftToRight


class CodeHighlighter(QSyntaxHighlighter):
    theme = "dark"

    def highlightBlock(self, text):
        for pattern, color in [(r"\b(?:AC|PC|AR|DR|IR|TR|E|INPR|OUTR|IEN|FGI|FGO|S|M|IF|THEN|AND|ADD|LDA|STA|BUN|BSA|ISZ|CLA|CLE|CMA|CME|CIR|CIL|INC|SPA|SNA|SZA|SZE|HLT|INP|OUT|SKI|SKO|ION|IOF)\b", SYNTAX[self.theme][0]),
                               (r"←|<-|=|∧|¬|\+", SYNTAX[self.theme][1]),
                               (r"[#;].*$", SYNTAX[self.theme][2])]:
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            for match in re.finditer(pattern, text, re.I):
                self.setFormat(match.start(), match.end() - match.start(), fmt)


def code_editor(readonly=False, theme=None):
    editor = CodeEditor()
    editor.setReadOnly(readonly)
    editor.setLayoutDirection(LTR)
    option = editor.document().defaultTextOption()
    option.setTextDirection(LTR)
    editor.document().setDefaultTextOption(option)
    font=QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
    font.setPointSize(12)
    editor.setFont(font)
    editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
    editor.resize_gutter()
    editor.highlighter = CodeHighlighter(editor.document())
    editor.highlighter.theme = theme if theme in SYNTAX else "dark"
    editor.highlighter.rehighlight()
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
        self.direction = "forward"
        self.path = None
        self.active_example = None
        self.result = None
        self.translated_source = None
        self.labels = []
        self.icon_buttons = []
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
        self.brand_mark = BrandMark(self.theme)
        header.addWidget(self.brand_mark)
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
        self.menu_actions = []
        for name, entries in [("File", [("New", self.new_file), ("Choose file", self.open_file), ("Save input", self.save_file), ("Save input as", self.save_as)]),
                              ("Help", [("Instruction reference", self.open_instruction_reference), ("About", self.about)])]:
            button = QPushButton(self.t(name))
            self.labels.append((button, name))
            menu = QMenu(button)
            for key, slot in entries:
                action = menu.addAction(self.t(key))
                action.triggered.connect(lambda checked=False, fn=slot: fn())
                self.menu_actions.append((action, key))
            button.setMenu(menu)
            toolbar.addWidget(button)
        self.direction_box = QComboBox()
        self.direction_box.addItem(self.t("RTL → ASM"),"forward")
        self.direction_box.addItem(self.t("ASM → RTL"),"reverse")
        self.direction_box.currentIndexChanged.connect(self.change_direction)
        toolbar.addWidget(self.direction_box)
        toolbar.addWidget(self.button("Choose file", self.open_file))
        examples_button = QPushButton(self.t("Examples"))
        self.labels.append((examples_button, "Examples"))
        examples_menu = QMenu(examples_button)
        self.example_actions = []
        for example in EXAMPLES:
            action = examples_menu.addAction(example.title[self.language == "fa"])
            action.triggered.connect(lambda checked=False, item=example: self.load_example(item))
            self.example_actions.append((action, example))
        examples_button.setMenu(examples_menu)
        toolbar.addWidget(examples_button)
        self.icon_buttons.append((examples_button, "examples"))
        labs = QPushButton(self.t("Learning Center"))
        self.labels.append((labs, "Learning Center"))
        self.lab_actions = []
        labs.setObjectName("learnAction")
        labs.setToolTip(self.t("Learning Center")+" · Ctrl+K")
        labs.clicked.connect(self.open_learning_center)
        self.learning_button=labs
        self.learning_shortcut=QShortcut(QKeySequence("Ctrl+K"),self)
        self.learning_shortcut.activated.connect(self.open_learning_center)
        toolbar.addWidget(labs)
        self.icon_buttons.append((labs, "labs"))
        toolbar.addStretch()
        toolbar.addWidget(self.button("Translate", self.run_translation, True))
        self.export_button = self.button("Export ASM", self.export_file)
        self.export_button.setEnabled(False)
        toolbar.addWidget(self.export_button)
        layout.addWidget(toolbar_frame)
        split = QSplitter(Qt.Orientation.Vertical)
        self.workspace_split = split
        editors = QSplitter(Qt.Orientation.Horizontal)
        self.editor, self.output = code_editor(), code_editor(True)
        for title, editor in [("RTL input", self.editor), ("Assembly output", self.output)]:
            pane = QFrame()
            pane.setObjectName("editorPanel")
            box = QVBoxLayout(pane)
            box.setContentsMargins(10, 8, 10, 10)
            heading = QHBoxLayout()
            title_label=QLabel(self.t(title))
            title_label.setObjectName("section")
            if editor is self.editor:self.input_title=title_label
            else:self.output_title=title_label
            heading.addWidget(title_label)
            heading.addStretch()
            if editor is self.output:
                self.output_state = QLabel()
                heading.addWidget(self.output_state)
            else:
                heading.addWidget(self.label("UTF-8", "muted"))
            box.addLayout(heading)
            editor.setObjectName("workspaceCode")
            editor.setAccessibleName(self.t(title))
            box.addWidget(editor)
            editors.addWidget(pane)
        editors.setSizes([600, 600])
        split.addWidget(editors)
        self.tabs = MotionTabs()
        page = QWidget()
        row = QHBoxLayout(page)
        row.addWidget(self.button("Undo", self.editor.undo))
        row.addWidget(self.button("Redo", self.editor.redo))
        row.addWidget(self.button("Instruction reference", self.open_instruction_reference))
        row.addStretch()
        row.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tabs.addTab(page, self.t("Editor"))
        self.tabs.addTab(self.pad(), self.t("Symbol pad"))
        self.tabs.addTab(self.builder(), self.t("Builder"))
        self.tabs.setCurrentIndex(max(0, min(2, int(settings.value("input_mode", 0)))))
        self.tabs.currentChanged.connect(self.input_mode_changed)
        split.addWidget(self.tabs)
        diagnostics = QWidget()
        self.diagnostics_panel = diagnostics
        dl = QVBoxLayout(diagnostics)
        dl.addWidget(self.label("Diagnostics", "section"))
        self.table = QTableWidget(0, 4)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.cellClicked.connect(self.jump_error)
        dl.addWidget(self.table)
        split.addWidget(diagnostics)
        split.setStretchFactor(0, 1)
        split.setStretchFactor(1, 0)
        split.setStretchFactor(2, 0)
        self.diagnostics_panel.hide()
        split.setSizes([560, 80 if self.tabs.currentIndex() == 0 else 260, 0])
        layout.addWidget(split, 1)
        self.editor.textChanged.connect(self.invalidate)
        self.editor.document().modificationChanged.connect(self.update_document_title)
        self.mapping_active = False
        self.editor.cursorPositionChanged.connect(self.follow_source)
        self.output.cursorPositionChanged.connect(self.follow_output)
        self.shortcut = QShortcut(QKeySequence("F5"), self)
        self.shortcut.activated.connect(self.run_translation)
        self.reference_shortcut = QShortcut(QKeySequence("Ctrl+Space"), self)
        self.reference_shortcut.activated.connect(self.open_instruction_reference)
        self.file_shortcuts = []
        for sequence, handler in [("Ctrl+O", self.open_file), ("Ctrl+S", self.save_file), ("Ctrl+Shift+S", self.save_as), ("Ctrl+N", self.new_file)]:
            shortcut = QShortcut(QKeySequence(sequence), self)
            shortcut.activated.connect(handler)
            self.file_shortcuts.append(shortcut)
        self.relabel()
        self.input_mode_changed(self.tabs.currentIndex())
        self.offline_label = self.label("Offline", "muted")
        self.statusBar().addPermanentWidget(self.offline_label)
        self.update_output_state()
        self.apply_appearance()
        self.statusBar().showMessage(self.t("Ready"))
        self.update_document_title()
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

    def source_lines(self):
        return tuple(i.line for i in self.result.instructions) if self.direction=="forward" else self.result.source_lines

    def input_suffix(self):
        return ".rtl" if self.direction=="forward" else ".asm"

    def output_suffix(self):
        return ".asm" if self.direction=="forward" else ".rtl"

    def input_filter(self):
        return "RTL (*.rtl *.txt);;All files (*)" if self.direction=="forward" else "Assembly (*.asm *.txt);;All files (*)"

    def refresh_direction_labels(self):
        reverse=self.direction=="reverse"
        input_key="Assembly input" if reverse else "RTL input"
        output_key="RTL output" if reverse else "Assembly output"
        self.input_title.setText(self.t(input_key))
        self.output_title.setText(self.t(output_key))
        self.editor.setAccessibleName(self.t(input_key))
        self.output.setAccessibleName(self.t(output_key))
        self.export_button.setText(self.t("Export RTL" if reverse else "Export ASM"))
        if reverse and self.tabs.currentIndex()==1:self.tabs.setCurrentIndex(0)
        self.tabs.setTabEnabled(1,not reverse)
        self.update_preview()

    def set_direction(self,direction):
        self.direction=direction
        self.direction_box.blockSignals(True)
        self.direction_box.setCurrentIndex(self.direction_box.findData(direction))
        self.direction_box.blockSignals(False)
        self.refresh_direction_labels()

    def change_direction(self,*_):
        direction=self.direction_box.currentData()
        if direction==self.direction:return
        if not self.confirm_discard():
            self.set_direction(self.direction)
            return
        self.set_direction(direction)
        self.replace_document("")

    def open_number_lab(self):
        from ui.program_lab import ProgramLab
        lab=ProgramLab(self)
        lab.select_tool('alu')
        lab.exec()

    def input_mode_changed(self, index):
        self.settings.setValue("input_mode", index)
        total = max(self.workspace_split.height(), 520)
        diagnostic = 145 if not self.diagnostics_panel.isHidden() else 0
        tools = 92 if index == 0 else 260
        self.tabs.setMaximumHeight(100 if index == 0 else 360)
        self.workspace_split.setSizes([max(180, total-tools-diagnostic), tools, diagnostic])

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
        names = {"Open RTL":"open","Choose file":"open","Translate":"translate","Export ASM":"export",
                 "Settings":"settings","Undo":"undo","Redo":"redo","Instruction reference":"search"}
        if key in names:
            self.icon_buttons.append((widget,names[key]))
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
            ("Redo", self.editor.redo)]):
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
        self.instruction_search = QLineEdit()
        self.instruction_search.setPlaceholderText(self.t("Search instructions"))
        box.addWidget(self.instruction_search)
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
        self.insert_button = self.button("Insert instruction", self.insert_instruction, True)
        self.replace_button = self.button("Replace line", lambda: self.edit_line("replace"))
        row.addWidget(self.insert_button)
        row.addWidget(self.replace_button)
        row.addWidget(self.button("Delete line", lambda: self.edit_line("delete")))
        row.addWidget(self.button("Move up", lambda: self.edit_line("up")))
        row.addWidget(self.button("Move down", lambda: self.edit_line("down")))
        box.addLayout(row)
        self.operations.currentIndexChanged.connect(self.update_preview)
        self.instruction_search.textChanged.connect(self.filter_instructions)
        self.address.textChanged.connect(self.update_preview)
        self.indirect.toggled.connect(self.update_preview)
        self.update_preview()
        return page

    def filter_instructions(self):
        query = self.instruction_search.text().strip().casefold()
        previous = self.operations.currentData()
        names = NAMES if self.language == "fa" else EN_NAMES
        self.operations.blockSignals(True)
        self.operations.clear()
        for mnemonic, template in TEMPLATES.items():
            searchable = " ".join((mnemonic, names[mnemonic], template)).casefold()
            if query in searchable:
                self.operations.addItem(f"{mnemonic} — {names[mnemonic]}", mnemonic)
        if self.operations.findData(previous) >= 0:
            self.operations.setCurrentIndex(self.operations.findData(previous))
        self.operations.blockSignals(False)
        self.update_preview()

    def template(self):
        name = self.operations.currentData()
        if name is None:
            raise ValueError("No matching instruction")
        memory = "{a}" in TEMPLATES[name]
        rtl=build_rtl(name, self.address.text() if memory else "",
                         self.indirect.isChecked() if memory else False)
        return rtl if self.direction=="forward" else translate(rtl).assembly

    def update_preview(self):
        name = self.operations.currentData()
        memory = name is not None and "{a}" in TEMPLATES[name]
        self.address.setEnabled(memory)
        self.indirect.setEnabled(memory)
        valid = False
        try:
            source = self.template()
            result=translate(source) if self.direction=="forward" else reverse_translate(source)
            target=result.assembly if self.direction=="forward" else result.rtl.rstrip("\n")
            self.preview.setText(source + "    →    " + target)
            valid = result.ok
        except ValueError:
            self.preview.setText(self.t("No matching instruction") if name is None else self.t("Choose 000–FFF."))
        self.insert_button.setEnabled(valid)
        self.replace_button.setEnabled(valid)

    def insert_instruction(self):
        try:
            rtl = self.template()
        except ValueError:
            QMessageBox.warning(self, self.t("Invalid address"), self.t("Choose 000–FFF."))
            return
        cursor = self.editor.textCursor()
        cursor.clearSelection()
        block = cursor.block()
        cursor.beginEditBlock()
        if not block.text().strip():
            has_next = block.next().isValid()
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            cursor.insertText(rtl + ("" if has_next else "\n"))
            if has_next:
                cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
        elif block.next().isValid():
            cursor.setPosition(block.next().position())
            cursor.insertText(rtl + "\n")
        else:
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
            cursor.insertText("\n" + rtl + "\n")
        cursor.endEditBlock()
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
        self.export_button.setEnabled(False)
        self.update_output_state()
        self.table.setRowCount(0)
        self.editor.mark_errors(())
        self.diagnostics_panel.hide()
        self.statusBar().showMessage(self.t("Input changed — translate again"))

    def run_translation(self):
        source = self.editor.toPlainText()
        self.result = translate(source) if self.direction=="forward" else reverse_translate(source)
        self.translated_source = source
        self.mapping_active = True
        try:
            target=(self.result.assembly if self.direction=="forward" else self.result.rtl.rstrip("\n")) if self.result.ok else ""
            self.output.setPlainText(target)
        finally:
            self.mapping_active = False
        self.follow_source()
        self.export_button.setEnabled(self.result.ok)
        self.update_output_state()
        self.render_errors()
        self.statusBar().showMessage(self.t("Translation successful" if self.result.ok else "Translation failed"))
        self.brand_mark.feedback(self.result.ok)
        if self.result.ok:
            self.centralWidget().feedback()

    def update_output_state(self):
        if self.result is None:
            state, label = "neutral", self.t("Awaiting translation")
        elif not self.result.ok:
            state, label = "error", self.t("Translation failed")
        else:
            count = len(self.source_lines())
            state, label = "success", f"{count} " + self.t("instruction" if count == 1 else "instructions")
        self.output_state.setText(label)
        self.output_state.setProperty("state", state)
        self.output_state.style().unpolish(self.output_state)
        self.output_state.style().polish(self.output_state)

    def mapped_cursor(self, editor, line):
        block = editor.document().findBlockByNumber(line)
        if block.isValid():
            editor.setTextCursor(QTextCursor(block))
            editor.ensureCursorVisible()

    def follow_source(self):
        if self.mapping_active or not self.result or not self.result.ok or self.translated_source != self.editor.toPlainText():
            return
        line = self.editor.textCursor().blockNumber() + 1
        for index, source_line in enumerate(self.source_lines()):
            if source_line == line:
                self.mapping_active = True
                try:
                    self.mapped_cursor(self.output, index)
                finally:
                    self.mapping_active = False
                break

    def follow_output(self):
        if self.mapping_active or not self.result or not self.result.ok or self.translated_source != self.editor.toPlainText():
            return
        index = self.output.textCursor().blockNumber()
        lines=self.source_lines()
        if 0 <= index < len(lines):
            self.mapping_active = True
            try:
                self.mapped_cursor(self.editor, lines[index] - 1)
            finally:
                self.mapping_active = False

    def render_errors(self):
        errors = self.result.diagnostics if self.result else ()
        self.table.setRowCount(len(errors))
        self.diagnostics_panel.setVisible(bool(errors))
        if errors:
            self.input_mode_changed(self.tabs.currentIndex())
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
        for action, key in self.lab_actions + self.menu_actions:
            action.setText(self.t(key))
        for action, example in self.example_actions:
            action.setText(example.title[self.language == "fa"])
        for index, title in enumerate(("Editor", "Symbol pad", "Builder")):
            self.tabs.setTabText(index, self.t(title))
        for index, title in enumerate(("Light", "Dark", "Night")):
            self.themes.setItemText(index, self.t(title))
        self.instruction_search.setPlaceholderText(self.t("Search instructions"))
        self.filter_instructions()
        self.table.setHorizontalHeaderLabels([self.t(k) for k in ("Line", "Column", "Code", "Help")])
        self.render_errors()
        self.update_preview()
        self.update_output_state()
        self.direction_box.setItemText(0,self.t("RTL → ASM"))
        self.direction_box.setItemText(1,self.t("ASM → RTL"))
        self.refresh_direction_labels()
        self.learning_button.setToolTip(self.t("Learning Center")+" · Ctrl+K")

    def change_language(self):
        self.language = self.languages.currentData()
        self.settings.setValue("language", self.language)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if self.language == "fa" else LTR)
        self.relabel()
        self.update_document_title()
        self.statusBar().showMessage(self.t("Ready"))

    def change_theme(self):
        self.theme = self.themes.currentData()
        self.settings.setValue("theme", self.theme)
        self.apply_appearance()

    def apply_appearance(self):
        enabled = self.settings.value("glass_enabled", True, type=bool)
        apply_theme(QApplication.instance(), self.theme, enabled)
        set_reduced_motion(QApplication.instance(), self.settings.value("reduced_motion", False, type=bool))
        bg, panel, raised, fg, muted, accent, border = PALETTES[self.theme]
        self.brand_mark.set_appearance(self.theme,enabled,self.settings.value("reduced_motion",False,type=bool))
        self.setWindowIcon(brand_icon(self.theme,enabled))
        for button,name in self.icon_buttons:
            color = ("#ffffff" if self.theme=="light" else bg) if button.objectName()=="primary" else fg
            button.setIcon(icon(name,color))
            button.setIconSize(QSize(18,18))
        for editor in (self.editor,self.output):
            editor.highlighter.theme=self.theme
            editor.highlighter.rehighlight()
            editor.gutter.update()
        self.centralWidget().theme = self.theme
        self.centralWidget().enabled = enabled
        self.centralWidget().snap()
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

    def update_document_title(self, *_):
        name = self.path.name if self.path else self.t("Untitled")
        if self.path is None and self.active_example:
            name = self.active_example.title[self.language == "fa"]
        dirty = " *" if self.editor.document().isModified() else ""
        self.setWindowTitle(f"{name}{dirty} — Mano Studio")

    def last_directory(self):
        return str(self.path.parent) if self.path else self.settings.value("last_directory", "")

    def replace_document(self, value, path=None, example=None):
        self.path, self.active_example = path, example
        self.editor.setPlainText(value)
        self.editor.document().setModified(False)
        # Even an identical or empty document must not inherit old output.
        self.invalidate()
        self.update_document_title()

    def load_example(self, example):
        if not self.confirm_discard():
            return
        self.set_direction("forward")
        self.replace_document(example.rtl, example=example)
        self.run_translation()
        self.statusBar().showMessage(example.description[self.language == "fa"])

    def new_file(self):
        if self.confirm_discard():
            self.replace_document("")

    def open_file(self):
        if not self.confirm_discard():
            return
        name, _ = QFileDialog.getOpenFileName(self, self.t("Choose file"), self.last_directory(), self.input_filter())
        if not name:
            return
        try:
            path = Path(name)
            if path.stat().st_size>2_000_000:
                raise ValueError(self.t("Input file too large"))
            value = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError, ValueError) as exc:
            QMessageBox.warning(self, self.t("File error"), error_text(exc,self.language=="fa"))
            return
        self.settings.setValue("last_directory", str(path.parent))
        self.replace_document(value, path=path)
        self.run_translation()

    def save_file(self):
        if self.path is None:
            return self.save_as()
        return self.write_document(self.path)

    def save_as(self):
        suggested = str(self.path) if self.path else str(Path(self.last_directory()) / ((self.active_example.key if self.active_example else "untitled") + self.input_suffix()))
        name, _ = QFileDialog.getSaveFileName(self, self.t("Save input as"), suggested, self.input_filter())
        if not name:
            return False
        path = Path(name)
        if not path.suffix:
            path = path.with_suffix(self.input_suffix())
        return self.write_document(path)

    def write_document(self, path):
        try:
            path.write_text(self.editor.toPlainText(), encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            QMessageBox.warning(self, self.t("File error"), error_text(exc,self.language=="fa"))
            return False
        self.path = path
        self.settings.setValue("last_directory", str(path.parent))
        self.editor.document().setModified(False)
        self.update_document_title()
        self.statusBar().showMessage(self.t("Input saved"))
        return True

    def export_file(self):
        if self.result is None or not self.result.ok or self.translated_source != self.editor.toPlainText():
            QMessageBox.warning(self, self.t("No valid output"), self.t("Translate the input successfully before exporting."))
            return
        suggested = str(self.path.with_suffix(self.output_suffix())) if self.path else str(Path(self.last_directory()) / ((self.active_example.key if self.active_example else "untitled") + self.output_suffix()))
        if self.path and Path(suggested)==self.path:
            suggested=str(self.path.with_name(self.path.stem+"-converted"+self.output_suffix()))
        name, _ = QFileDialog.getSaveFileName(self, self.t("Export ASM" if self.direction=="forward" else "Export RTL"), suggested, "Assembly (*.asm)" if self.direction=="forward" else "RTL (*.rtl)")
        if not name:
            return
        path = Path(name)
        if not path.suffix:
            path = path.with_suffix(self.output_suffix())
        try:
            if self.path and path.resolve() == self.path.resolve():
                raise OSError(self.t("Input and output must be different files"))
            output=self.output.toPlainText()
            path.write_text(output + ("\n" if output else ""), encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            QMessageBox.warning(self, self.t("File error"), error_text(exc,self.language=="fa"))
            return
        self.statusBar().showMessage(self.t("Output exported"))

    def open_instruction_reference(self):
        self.tabs.setCurrentIndex(2)
        self.instruction_search.setFocus()
        self.instruction_search.selectAll()

    def open_learning_center(self):
        from ui.learning_center import LearningCenter
        center=LearningCenter(self)
        if center.exec() and center.selected:
            self.launch_learning_tool(center.selected)

    def launch_learning_tool(self,tool):
        if tool.lab=='workspace':
            self.editor.setFocus()
        elif tool.lab=='logic':
            self.open_logic_lab(tool.route)
        elif tool.lab=='computer':
            self.open_program_lab(tool.route)

    def open_logic_lab(self,route='gates'):
        from ui.logic_lab import LogicLab
        lab=LogicLab(self)
        lab.select_tool(route)
        lab.exec()

    def open_program_lab(self,route='live'):
        from ui.program_lab import ProgramLab
        assembly=''
        if self.direction=='reverse':
            assembly=self.editor.toPlainText()
        else:
            result=translate(self.editor.toPlainText())
            if result.ok:
                assembly=result.assembly
                if self.active_example and self.editor.toPlainText()==self.active_example.rtl:
                    assembly=computer_source(self.active_example,assembly)
        lab=ProgramLab(self,assembly)
        lab.select_tool(route)
        lab.exec()

    def about(self):
        fa = self.language == "fa"
        dialog = QDialog(self)
        dialog.setWindowTitle(self.t("About") + " — Mano Studio")
        dialog.setLayoutDirection(Qt.LayoutDirection.RightToLeft if fa else LTR)
        dialog.setMinimumWidth(460)
        dialog.resize(580, 540)
        outer = QVBoxLayout(dialog)
        scroll = QScrollArea(dialog)
        scroll.setWidgetResizable(True)
        content = QWidget()
        body = QVBoxLayout(content)
        header = QHBoxLayout()
        mark = BrandMark(self.theme, content)
        mark.setFixedSize(64, 64)
        mark.set_appearance(self.theme, self.settings.value("glass_enabled", True, type=bool), True)
        header.addWidget(mark)
        title = QLabel("Mano Studio · " + VERSION)
        title.setObjectName("hero")
        title.setWordWrap(True)
        header.addWidget(title, 1)
        body.addLayout(header)

        def section(heading, lines):
            card = QFrame()
            card.setObjectName("editorPanel")
            layout = QVBoxLayout(card)
            label = QLabel(heading)
            label.setObjectName("section")
            layout.addWidget(label)
            for line in lines:
                label = QLabel(line)
                label.setTextFormat(Qt.TextFormat.PlainText)
                label.setWordWrap(True)
                label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                layout.addWidget(label)
            body.addWidget(card)

        section("تقدیر و تشکر" if fa else "Academic acknowledgment", [ACADEMIC_ACKNOWLEDGMENT[fa]])
        section("درباره پروژه و درس" if fa else "Project and course", [PURPOSE[fa], COURSE[fa], INSTITUTION[fa], REFERENCE[fa]])
        section("مجوز و مخزن" if fa else "License and repository", [COPYRIGHT, LICENSE_NOTE[fa], REPOSITORY])
        body.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.button(QDialogButtonBox.StandardButton.Close).setText("بستن" if fa else "Close")
        buttons.rejected.connect(dialog.reject)
        outer.addWidget(buttons)
        dialog.exec()

    def closeEvent(self, event):
        if not self.confirm_discard():
            event.ignore()
            return
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.sync()
        event.accept()
