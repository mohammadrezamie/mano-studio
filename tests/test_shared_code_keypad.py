"""Shared keypad can build full CPU programs but cannot mutate live source."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from ui.workspace import Workspace
from ui.program_lab import ProgramLab
from ui.code_keypad import tokens_for


@pytest.fixture
def lab(tmp_path):
    app = QApplication.instance() or QApplication([])
    w = Workspace(QSettings(str(tmp_path / "shared.ini"), QSettings.Format.IniFormat))
    view = ProgramLab(w)
    yield view
    view.mark_saved()
    view.close()
    w.editor.document().setModified(False)
    w.close()


def test_program_keypad_covers_labels_and_directives(lab):
    assert lab.source.isReadOnly()
    assert not lab.keypad_toggle.isEnabled()
    original = lab.source.toPlainText()
    cpu = lab.cpu
    lab.source_keypad.insert("HLT")
    lab.source_keypad.move_cursor("delete")
    lab.source_keypad.edit_history(False)
    assert lab.source.toPlainText() == original and lab.cpu is cpu
    assert lab.begin_source_edit()
    assert lab.keypad_toggle.isEnabled()
    lab.source.clear()
    pad = lab.source_keypad
    def write(*tokens):
        for token in tokens:
            pad.buttons[("program", token)].click()
        pad.controls["Enter"].click()
    write("ORG ", "0", "0", "0")
    write("LDA ", "X")
    write("HLT")
    write("X", ",", "DEC ", "5")
    write("END")
    assert lab.source.toPlainText() == "ORG 000\nLDA X\nHLT\nX,DEC 5\nEND\n"
    lab.load()
    assert lab.cpu is not None and lab.source.isReadOnly()
    assert not lab.keypad_toggle.isEnabled()
    lab.step()
    assert lab.cpu.ac == 5


def test_conversion_pad_stays_within_supported_language():
    assert "ORG " in tokens_for("program") and "ORG " not in tokens_for("reverse")
    assert "←" in tokens_for("forward") and "←" not in tokens_for("reverse")
    for mode in ("forward", "reverse", "program"):
        assert len(tokens_for(mode)) == len(set(tokens_for(mode)))
