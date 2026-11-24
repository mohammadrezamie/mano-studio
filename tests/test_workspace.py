"""Desktop smoke tests; run with QT_QPA_PLATFORM=offscreen."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from ui.workspace import Workspace


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def workspace(app, tmp_path):
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    window = Workspace(settings)
    yield window
    window.editor.document().setModified(False)
    window.close()


def test_translation_and_stale_output(workspace):
    workspace.editor.setPlainText("AC ← M[100]")
    workspace.run_translation()
    assert workspace.output.toPlainText() == "LDA 100"
    workspace.editor.setPlainText("AR ← PC")
    assert workspace.output.toPlainText() == ""
    workspace.run_translation()
    assert workspace.table.rowCount() == 1
    assert workspace.result.ok is False


def test_builder_and_pad(workspace):
    workspace.operations.setCurrentIndex(workspace.operations.findData("LDA"))
    workspace.address.setText("abc")
    workspace.indirect.setChecked(True)
    workspace.insert_instruction()
    workspace.run_translation()
    assert workspace.output.toPlainText() == "LDA ABC I"
    workspace.insert("AC ← 0")
    workspace.run_translation()
    assert workspace.output.toPlainText() == "LDA ABC I\nCLA"


def test_settings(workspace):
    workspace.languages.setCurrentIndex(1)
    workspace.themes.setCurrentIndex(workspace.themes.findData("night"))
    workspace.tabs.setCurrentIndex(2)
    assert workspace.settings.value("language") == "fa"
    assert workspace.settings.value("theme") == "night"
    assert int(workspace.settings.value("input_mode")) == 2
    restored = Workspace(workspace.settings)
    assert restored.language == "fa"
    assert restored.theme == "night"
    assert restored.tabs.currentIndex() == 2
    restored.close()


def test_error_marker_and_cursor_navigation(workspace):
    workspace.editor.setPlainText("AC=0\nAC=M[1000]\nS=0")
    workspace.run_translation()
    assert len(workspace.editor.extraSelections()) == 1
    workspace.jump_error(0, 0)
    assert workspace.editor.textCursor().blockNumber() == 1
    workspace.editor.setPlainText("AC=0")
    assert not workspace.editor.extraSelections()


def test_gutter_expands(workspace):
    workspace.editor.setPlainText("AC=0")
    before = workspace.editor.gutter_width()
    workspace.editor.setPlainText("\n".join(["AC=0"] * 100))
    assert workspace.editor.gutter_width() > before


def test_pad_replaces_selection(workspace):
    workspace.editor.setPlainText("AC=0")
    cursor = workspace.editor.textCursor()
    cursor.select(cursor.SelectionType.Document)
    workspace.editor.setTextCursor(cursor)
    workspace.insert("E ← 0")
    assert workspace.editor.toPlainText() == "E ← 0"


def test_calm_preferences(workspace):
    from ui.preferences import Preferences
    from ui.program_lab import ProgramLab
    prefs = Preferences(workspace)
    prefs.change("glass_enabled", False)
    prefs.change("reduced_motion", True)
    assert not workspace.centralWidget().enabled
    assert workspace.settings.value("reduced_motion", type=bool)
    lab = ProgramLab(workspace)
    lab.step()
    assert lab.datapath.reduced_motion
    assert lab.datapath.progress == 1.0
    assert lab.cpu.ac == 5
    lab.close()
    prefs.close()


def test_file_roundtrip_and_stale_export(workspace, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QFileDialog, QMessageBox
    source = tmp_path / "program.rtl"
    output = tmp_path / "program.asm"
    source.write_text("AC ← M[100]\nS ← 0\n", encoding="utf-8-sig")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args: (str(source), ""))
    workspace.open_file()
    workspace.run_translation()
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args: (str(output), ""))
    workspace.export_file()
    assert output.read_text(encoding="utf-8") == "LDA 100\nHLT\n"
    workspace.editor.setPlainText("AR ← PC")
    workspace.run_translation()
    warnings = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: warnings.append(args))
    workspace.export_file()
    assert warnings and output.read_text(encoding="utf-8") == "LDA 100\nHLT\n"


def test_core_does_not_request_network(workspace, monkeypatch):
    import socket
    from ui.program_lab import ProgramLab
    from ui.preferences import Preferences
    def blocked(*args, **kwargs):
        pytest.fail("Unexpected Python network request")
    monkeypatch.setattr(socket, "create_connection", blocked)
    workspace.editor.setPlainText("AC ← M[100]")
    workspace.run_translation()
    assert workspace.output.toPlainText() == "LDA 100"
    prefs = Preferences(workspace)
    lab = ProgramLab(workspace)
    lab.step()
    assert lab.cpu.ac == 5
    lab.close()
    prefs.close()


def test_integrated_reference_lookup(workspace):
    workspace.open_instruction_reference()
    assert workspace.tabs.currentIndex()==2
    workspace.instruction_search.setText("LDA")
    workspace.address.setText("ABC")
    workspace.indirect.setChecked(True)
    assert workspace.operations.currentData()=="LDA"
    assert workspace.template()=="AC ← M[M[ABC]]"
    assert "LDA ABC I" in workspace.preview.text()
    workspace.insert_instruction()
    assert workspace.editor.toPlainText()=="AC ← M[M[ABC]]\n"
    workspace.instruction_search.setText("no such instruction")
    assert not workspace.insert_button.isEnabled()
    workspace.instruction_search.clear()
    assert workspace.operations.count()==25


def test_source_output_mapping(workspace):
    from PySide6.QtGui import QTextCursor
    workspace.editor.setPlainText("# note\nAC ← M[100]\n\nS ← 0")
    workspace.run_translation()
    assert workspace.output.toPlainText()=="LDA 100\nHLT"
    workspace.editor.setTextCursor(QTextCursor(workspace.editor.document().findBlockByNumber(3)))
    assert workspace.output.textCursor().blockNumber()==1
    workspace.output.setTextCursor(QTextCursor(workspace.output.document().findBlockByNumber(0)))
    assert workspace.editor.textCursor().blockNumber()==1


def test_builder_preserves_neighboring_lines(workspace):
    from PySide6.QtGui import QTextCursor
    workspace.editor.setPlainText("AC ← 0\nS ← 0")
    workspace.editor.setTextCursor(QTextCursor(workspace.editor.document().firstBlock()))
    workspace.operations.setCurrentIndex(workspace.operations.findData("CLE"))
    workspace.insert_instruction()
    assert workspace.editor.toPlainText()=="AC ← 0\nE ← 0\nS ← 0"


def test_logic_pin_count_and_truth_table(workspace):
    from ui.logic_lab import LogicLab
    from ui.gate_symbols import pin_offsets
    dialog=LogicLab(workspace)
    dialog.selector.setCurrentIndex(dialog.selector.findData("xor"))
    dialog.pin_count.setValue(4)
    assert len(dialog.buttons)==4 and dialog.table.rowCount()==16
    assert len(pin_offsets(4))==4
    dialog.choose_row(7,0)
    assert dialog.summary.text()=="Y = 1"
    dialog.selector.setCurrentIndex(dialog.selector.findData("not"))
    assert len(dialog.buttons)==1 and not dialog.pin_count.isEnabled()
    dialog.close()


def test_computer_single_state(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace,"ORG 000\nLDA 100\nADD 101\nSTA 102\nHLT\nORG 100\nDEC 5\nDEC 3\nDEC 0\nEND")
    assert lab.datapath.cpu is lab.cpu
    lab.step()
    assert lab.datapath.last_step.mnemonic=="LDA" and lab.cpu.ac==5
    lab.step()
    assert lab.datapath.last_step.after["AC"]==8
    lab.step()
    assert lab.datapath.last_step.writes==((0x102,0,8),)
    assert lab.cpu.memory[0x102]==8
    lab.source.setPlainText("HLT")
    assert lab.cpu is None and lab.datapath.cpu is None
    lab.close()


def test_example_workflow(workspace, tmp_path, monkeypatch):
    from example_catalog import EXAMPLES
    from PySide6.QtWidgets import QFileDialog
    workspace.load_example(EXAMPLES[0])
    assert workspace.path is None and workspace.result.ok
    assert not workspace.editor.document().isModified()
    assert workspace.output.toPlainText()=="LDA 100\nADD 101\nSTA 102\nHLT"
    target=tmp_path/"my-example"
    monkeypatch.setattr(QFileDialog,"getSaveFileName",lambda *a:(str(target),""))
    assert workspace.save_as()
    assert workspace.path==target.with_suffix(".rtl")
    assert workspace.path.read_text(encoding="utf-8")==EXAMPLES[0].rtl
    workspace.new_file()
    assert workspace.path is None and workspace.active_example is None
    assert workspace.result is None and not workspace.export_button.isEnabled()


def test_example_cancel_preserves_document(workspace, monkeypatch):
    from example_catalog import EXAMPLES
    workspace.editor.setPlainText("S ← 0")
    monkeypatch.setattr(workspace,"confirm_discard",lambda:False)
    workspace.load_example(EXAMPLES[0])
    assert workspace.editor.toPlainText()=="S ← 0"
    assert workspace.active_example is None


def test_visual_status_and_theme(workspace):
    from PySide6.QtGui import QPalette, QColor
    from ui.theme import PALETTES
    assert workspace.output_state.property("state")=="neutral"
    assert not workspace.export_button.icon().isNull()
    workspace.editor.setPlainText("AC ← M[100]")
    workspace.run_translation()
    assert workspace.output_state.property("state")=="success"
    assert workspace.output_state.text()=="1 instruction"
    workspace.editor.setPlainText("AR ← PC")
    workspace.run_translation()
    assert workspace.output_state.property("state")=="error"
    for theme in ("light","night","dark"):
        workspace.themes.setCurrentIndex(workspace.themes.findData(theme))
        assert workspace.editor.highlighter.theme==theme
        assert workspace.output.highlighter.theme==theme
        assert QApplication.instance().palette().color(QPalette.ColorRole.Base)==QColor(PALETTES[theme][1])
