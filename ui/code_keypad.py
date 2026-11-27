"""Reusable, offline technical keypad. Never edits a locked code document."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget
from instruction_catalog import TEMPLATES


def tokens_for(mode):
    """Reverse conversion deliberately excludes full assembler directives."""
    rtl = ("AC", "PC", "AR", "DR", "E", "IR", "TR", "INPR", "OUTR", "IEN",
           "FGI", "FGO", "S", "M[", "]", "[", "←", "=", "+", "∧", "¬", "(",
           ")", ":", ",", "IF ", " THEN ", "CIR", "CIL", *"0123456789ABCDEF")
    instructions = tuple(name + (" " if "{a}" in template else "")
                         for name, template in TEMPLATES.items())
    reverse = instructions + tuple("0123456789ABCDEF") + ("I", ";")
    program = instructions + ("ORG ", "END", "DEC ", "HEX ") + tuple(
        "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ") + (",", ":", "_", "+", "-", ";")
    return tuple(dict.fromkeys({"forward": rtl, "reverse": reverse, "program": program}[mode]))


class CodeKeypad(QWidget):
    def __init__(self, editor, modes, button_factory, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.modes = tuple(modes)
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.stack = QStackedWidget(self)
        self.buttons = {}
        for mode in self.modes:
            panel = QWidget()
            grid = QGridLayout(panel)
            grid.setContentsMargins(2, 2, 2, 2)
            grid.setSpacing(4)
            for index, token in enumerate(tokens_for(mode)):
                button = QPushButton(token.strip())
                button.setProperty("insertToken", token)
                button.setAccessibleName(token.strip())
                button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                button.clicked.connect(lambda checked=False, value=token: self.insert(value))
                grid.addWidget(button, index // 10, index % 10)
                self.buttons[(mode, token)] = button
            self.stack.addWidget(panel)
        outer.addWidget(self.stack)
        controls = QHBoxLayout()
        self.controls = {}
        for title, action in (
            ("Space", lambda: self.insert(" ")), ("Enter", lambda: self.insert("\n")),
            ("Backspace", lambda: self.move_cursor("delete")),
            ("◀", lambda: self.move_cursor("left")), ("▶", lambda: self.move_cursor("right")),
            ("Undo", lambda: self.edit_history(False)), ("Redo", lambda: self.edit_history(True)),
        ):
            button = button_factory(title, action)
            self.controls[title] = button
            controls.addWidget(button)
        outer.addLayout(controls)

    def set_mode(self, mode):
        self.stack.setCurrentIndex(self.modes.index(mode))

    def insert(self, value):
        if self.editor.isReadOnly():
            return
        self.editor.insertPlainText(value)
        self.editor.setFocus()

    def move_cursor(self, direction):
        cursor = self.editor.textCursor()
        if direction == "delete":
            if self.editor.isReadOnly():
                return
            if cursor.hasSelection():
                cursor.removeSelectedText()
            else:
                cursor.deletePreviousChar()
        else:
            cursor.movePosition(QTextCursor.MoveOperation.Left if direction == "left"
                                else QTextCursor.MoveOperation.Right)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def edit_history(self, redo):
        if self.editor.isReadOnly():
            return
        (self.editor.redo if redo else self.editor.undo)()
        self.editor.setFocus()
