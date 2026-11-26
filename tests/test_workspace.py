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
    lab.mark_saved(); lab.close()
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
    lab.mark_saved(); lab.close()
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
    lab.mark_saved(); lab.close()


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


def test_integrated_circuit_edit(workspace):
    from ui.logic_lab import LogicLab
    lab=LogicLab(workspace)
    lab.selector.setCurrentIndex(lab.selector.findData("and"))
    lab.edit_circuit()
    assert not lab.selector.isEnabled()
    lab.circuit_editor.gates.cellWidget(0,1).setCurrentText("OR")
    lab.circuit_editor.apply()
    assert lab.selector.currentData()=="custom" and lab.dirty
    lab.change("A",True)
    assert lab.summary.text()=="Y = 1"
    lab.undo_edit()
    lab.change("A",True)
    assert lab.summary.text()=="Y = 0"
    lab.dirty=False
    lab.close()


def test_canvas_rewire_and_export(workspace,tmp_path):
    from PySide6.QtCore import QPointF,Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
    from ui.logic_lab import LogicLab
    lab=LogicLab(workspace)
    lab.selector.setCurrentIndex(lab.selector.findData("and"))
    lab.show()
    lab.canvas_edit.setChecked(True)
    QApplication.processEvents()
    lab.diagram.fit()
    lab.change("A",True)
    def click_pin(name,pin):
        pos=next(p for n,i,p in lab.diagram.ports if n==name and i==pin)
        QTest.mouseClick(lab.diagram.viewport(),Qt.MouseButton.LeftButton,
                         pos=lab.diagram.mapFromScene(QPointF(*pos)))
    click_pin("A",-1)
    click_pin("q",1)
    assert lab.document.gates[0].inputs==("A","A")
    assert lab.summary.text()=="Y = 1"
    assert lab.document.positions
    before=lab.document
    lab.rewire_pin("q","q",0)
    assert lab.document==before
    x,y=lab.diagram.positions["q"]
    lab.move_component("q",x,y+200)
    assert dict((n,(x,y)) for n,x,y in lab.document.positions)["q"]==(x,y+200)
    lab.undo_edit()
    assert lab.document==before
    csv=tmp_path/"truth.csv"
    svg=tmp_path/"circuit.svg"
    lab.write_truth_table(csv)
    lab.write_schematic(svg)
    assert csv.read_text(encoding="utf-8-sig").splitlines()[0]=="A,B,Y"
    assert "<svg" in svg.read_text(encoding="utf-8")
    lab.dirty=False
    lab.close()


def test_integrated_sequential_view(workspace):
    from ui.logic_lab import LogicLab
    lab=LogicLab(workspace)
    lab.mode_tabs.setCurrentIndex(1)
    view=lab.sequential
    view.buttons["D"].setChecked(True)
    assert view.model.value==0
    view.pulse()
    assert view.model.value==1 and "Q = 1" in view.summary.text()
    view.selector.setCurrentIndex(view.selector.findData("COUNT4"))
    view.buttons["EN"].setChecked(True)
    view.pulse()
    assert view.model.value==1
    lab.close()


def test_computer_debugger_and_alu(workspace,tmp_path):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace,"LDA 100\nADD 101\nSTA 102\nHLT\nORG 100\nHEX 7FFF\nDEC 1\nDEC 0")
    lab.break_address.setText("002")
    lab.toggle_breakpoint()
    lab.run_tick()
    lab.run_tick()
    lab.run_tick()
    assert lab.steps==2 and lab.cpu.pc==2
    assert lab.trace.rowCount()==2
    lab.use_registers()
    assert lab.arithmetic.a.text()=="8000"
    lab.arithmetic.a.setText("7FFF")
    lab.arithmetic.b.setText("0001")
    assert lab.arithmetic.result.word==0x8000 and lab.arithmetic.result.overflow
    lab.run_tick()
    assert lab.cpu.memory[0x102]==0x8000 and lab.steps==3
    lab.back()
    assert lab.cpu.memory[0x102]==0 and lab.cpu.pc==2
    assert lab.source.textCursor().blockNumber()==2
    path=tmp_path/"trace.csv"
    lab.write_trace(path)
    assert len(path.read_text(encoding="utf-8-sig").splitlines())==3
    lab.mark_saved(); lab.close()


def test_optional_reverse_import(workspace,tmp_path,monkeypatch):
    from PySide6.QtWidgets import QFileDialog
    path=tmp_path/"input.asm"
    path.write_text("LDA 100 I\nHLT",encoding="utf-8")
    workspace.direction_box.setCurrentIndex(1)
    monkeypatch.setattr(QFileDialog,"getOpenFileName",lambda *a:(str(path),""))
    workspace.open_file()
    assert workspace.path==path and not workspace.editor.document().isModified()
    assert workspace.output.toPlainText()=="AC ← M[M[100]]\nS ← 0"
    target=tmp_path/"out"
    monkeypatch.setattr(QFileDialog,"getSaveFileName",lambda *a:(str(target),""))
    workspace.export_file()
    assert target.with_suffix(".rtl").read_text(encoding="utf-8")=="AC ← M[M[100]]\nS ← 0\n"
    assert path.read_text(encoding="utf-8")=="LDA 100 I\nHLT"
    workspace.editor.setPlainText("ORG 100\nHLT")
    workspace.run_translation()
    assert not workspace.result.ok and not workspace.export_button.isEnabled()
    workspace.editor.document().setModified(False)


def test_alu_base_switch_preserves_word(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    view=lab.arithmetic
    assert view.result.word==0x8000
    view.base.setCurrentIndex(view.base.findData(10))
    assert view.a.text()=="32767" and view.b.text()=="1"
    assert view.result.word==0x8000
    view.base.setCurrentIndex(view.base.findData(2))
    assert view.a.text()=="0111111111111111"
    assert view.result.word==0x8000
    lab.mark_saved(); lab.close()


def test_number_conversion_only(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    view=lab.arithmetic
    view.op.setCurrentIndex(0)
    view.a.setText("FF")
    assert view.representation.rowCount()==1
    assert view.representation.item(0,1).text()=="0000000011111111"
    assert view.representation.item(0,2).text()=="000377"
    assert view.representation.item(0,3).text()=="00FF"
    assert view.representation.item(0,4).text()=="255"
    assert view.stages.isHidden()
    lab.mark_saved(); lab.close()

def test_reverse_builder_and_mapping(workspace):
    from PySide6.QtGui import QTextCursor
    workspace.direction_box.setCurrentIndex(1)
    workspace.operations.setCurrentIndex(workspace.operations.findData("LDA"))
    workspace.address.setText("100")
    workspace.indirect.setChecked(True)
    workspace.insert_instruction()
    assert workspace.editor.toPlainText()=="LDA 100 I\n"
    workspace.editor.setPlainText("# note\nLDA 100 I\n\nHLT")
    workspace.run_translation()
    workspace.editor.setTextCursor(QTextCursor(workspace.editor.document().findBlockByNumber(3)))
    assert workspace.output.textCursor().blockNumber()==1
    workspace.output.setTextCursor(QTextCursor(workspace.output.document().firstBlock()))
    assert workspace.editor.textCursor().blockNumber()==1
    workspace.editor.document().setModified(False)


@pytest.mark.parametrize(("language", "required"), [
    ("en", ("Prof. Siawash Eshaghiyeh", "faculty member", "Science & Research Branch")),
    ("fa", ("سیاوش اسحقیه", "عضو هیئت علمی", "واحد علوم و تحقیقات")),
])
def test_about_academic_attribution_is_exact_in_both_languages(workspace, language, required):
    from PySide6.QtWidgets import QLabel
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    dialog = workspace.about_dialog()
    try:
        visible_text = "\n".join(label.text() for label in dialog.findChildren(QLabel))
        for phrase in required:
            assert phrase in visible_text
    finally:
        dialog.close()


def test_persian_credits_and_optional_labs(workspace,monkeypatch):
    from PySide6.QtWidgets import QDialog, QLabel
    from ui.program_lab import ProgramLab
    from ui.logic_lab import LogicLab
    workspace.languages.setCurrentIndex(1)
    messages=[]
    def inspect_about(dialog):
        messages.extend(label.text() for label in dialog.findChildren(QLabel))
        return 0
    monkeypatch.setattr(QDialog,"exec",inspect_about)
    workspace.about()
    assert any("سیاوش اسحقیه" in text for text in messages)
    assert any("عضو هیئت علمی" in text for text in messages)
    assert any("واحد علوم و تحقیقات" in text for text in messages)
    assert any("Copyright (c) 2026" in text for text in messages)
    lab=ProgramLab(workspace,"UNKNOWN")
    assert "ناشناخته" in lab.machine.toPlainText()
    assert lab.arithmetic.representation.horizontalHeaderItem(0).text()=="کلمه"
    lab.mark_saved(); lab.close()
    logic=LogicLab(workspace)
    assert "منطق" in logic.windowTitle()
    logic.canvas_edit.setChecked(True)
    assert logic.diagram.fa
    logic.close()


def test_schematic_notation_preference(workspace):
    from ui.preferences import Preferences
    from ui.logic_lab import LogicLab
    from ui.gate_symbols import rectangular_qualifier
    settings=Preferences(workspace)
    settings.symbols.setCurrentIndex(1)
    assert workspace.settings.value("gate_symbol_style")=="iec"
    settings.close()
    lab=LogicLab(workspace)
    lab.selector.setCurrentIndex(lab.selector.findData("xor"))
    lab.pin_count.setValue(3)
    assert lab.diagram.symbol_style=="iec"
    assert rectangular_qualifier("XOR",2)=="=1"
    assert rectangular_qualifier("XOR",3)=="2k+1"
    assert rectangular_qualifier("XNOR",4)=="2k+1"
    lab.choose_row(7,0)
    assert lab.summary.text()=="Y = 1"
    assert len([p for p in lab.diagram.ports if p[0]=="q" and p[1]>=0])==3
    lab.close()


def test_expanded_circuit_equations(workspace):
    from ui.logic_lab import LogicLab
    lab=LogicLab(workspace)
    lab.selector.setCurrentIndex(lab.selector.findData("full_subtractor"))
    assert lab.table.rowCount()==8
    assert "diff = p ⊕ Bin" in lab.equations.toPlainText()
    lab.selector.setCurrentIndex(lab.selector.findData("compare4"))
    assert lab.table.rowCount()==256
    assert "LT = less3" in lab.equations.toPlainText()
    lab.close()


def test_universal_shift_register_ui(workspace):
    from ui.logic_lab import LogicLab
    lab=LogicLab(workspace)
    view=lab.sequential
    view.selector.setCurrentIndex(view.selector.findData("UNIVERSAL4"))
    assert len(view.buttons)==8
    for pin in ("D0","D2","S1","S0"):view.buttons[pin].setChecked(True)
    assert view.model.value==0 and "0101" in view.rule.text()
    view.pulse()
    assert view.model.value==5
    view.buttons["S0"].setChecked(False)
    view.buttons["SL"].setChecked(True)
    view.pulse()
    assert view.model.value==11
    lab.close()


def test_memory_and_data_codes_views(workspace):
    from ui.logic_lab import LogicLab
    from ui.program_lab import ProgramLab
    lab=LogicLab(workspace)
    view=lab.memory_view
    view.address.setValue(3)
    view.data.setValue(0xA5)
    view.we.setChecked(False)
    assert view.chip.words[3]==0
    view.cycle()
    assert view.chip.words[3]==0xA5
    view.we.setChecked(True)
    assert "A5" in view.summary.text()
    view.cs.setChecked(True)
    assert "Z" in view.summary.text()
    lab.close()
    computer=ProgramLab(workspace)
    codes=computer.codes
    codes.input.setText("09")
    assert codes.output.toPlainText()=="0000 1001"
    codes.mode.setCurrentIndex(1)
    codes.input.setText("1010")
    assert not codes.output.toPlainText()
    computer.mark_saved(); computer.close()


def test_memory_expansion_and_register_bus(workspace):
    from ui.logic_lab import LogicLab
    lab=LogicLab(workspace)
    view=lab.memory_array
    view.address.setValue(17)
    view.word.setText("ABCD")
    view.write()
    assert view.model.read(17)==0xABCD
    assert view.model.chips[1][0].words[1]==0xCD
    assert view.model.chips[1][1].words[1]==0xAB
    assert view.model.read(1)==0
    assert view.table.item(1,1).text()=="0"
    assert "CD" in view.table.item(1,2).text()
    assert "AB" in view.table.item(1,3).text()
    bus=lab.bus_view
    bus.words[0].setValue(0xA5)
    bus.en[0].setChecked(True)
    bus.ld[1].setChecked(True)
    bus.transfer()
    assert bus.words[1].value()==0xA5
    bus.words[2].setValue(1)
    bus.en[2].setChecked(True)
    bus.transfer()
    assert bus.words[1].value()==0xA5
    lab.close()


def test_cycle_inspector_and_reverse(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace,"LDA 100\nHLT\nORG 100\nHEX ABCD\nEND")
    lab.step()
    assert lab.cycles.groups.rowCount()==6
    lab.cycles.select(4)
    assert "ABCD" in lab.cycles.memory.text()
    assert lab.cycles.current_trace.after["AC"]==0xABCD
    lab.step()
    assert lab.cycles.groups.rowCount()==4
    lab.trace_selected(0,0)
    assert lab.cycles.current_trace.mnemonic=="LDA"
    lab.back()
    assert lab.cycles.current_trace.mnemonic=="LDA"
    lab.back()
    assert lab.cycles.groups.rowCount()==0
    lab.mark_saved(); lab.close()


def test_live_timing_controls(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace,"STA 100\nHLT\nORG 100\nHEX 0000\nEND")
    lab.cpu.ac=0xCAFE
    lab.microstep()
    assert lab.cpu.in_progress and lab.steps==0 and lab.cycles.groups.rowCount()==1
    lab.microstep()
    assert lab.cpu.pc==1 and lab.cycles.groups.rowCount()==2
    lab.microback()
    assert lab.cpu.pc==0 and lab.cycles.groups.rowCount()==1
    lab.step()
    assert lab.steps==1 and lab.cpu.memory[0x100]==0xCAFE
    lab.microback()
    assert lab.steps==0 and lab.cpu.memory[0x100]==0 and lab.cpu.in_progress
    lab.back()
    assert lab.cpu.pc==0 and not lab.cpu.in_progress
    lab.mark_saved(); lab.close()

def test_arithmetic_algorithm_modes(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    view=lab.arithmetic
    view.width.setCurrentIndex(view.width.findData(4))
    view.a.setText("8")
    view.b.setText("F")
    view.op.setCurrentIndex(view.op.findData("booth"))
    assert view.stages.rowCount()==4 and view.stages.columnCount()==7
    assert view.flags.text().endswith("00001000")
    assert view.result[-1].multiplier==8
    view.op.setCurrentIndex(view.op.findData("divide"))
    view.a.setText("F")
    view.b.setText("3")
    assert view.stages.rowCount()==4 and view.stages.columnCount()==6
    assert view.result[-1].quotient==5 and view.result[-1].remainder==0
    view.b.setText("0")
    assert view.result is None and view.stages.rowCount()==0 and view.status.text()
    view.b.setText("1")
    view.op.setCurrentIndex(1)
    assert view.result.word==0 and view.result.carry==1
    assert view.stages.horizontalHeaderItem(3).text()=="Cin"
    lab.mark_saved(); lab.close()


def test_extended_division_modes(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    view=lab.arithmetic
    view.width.setCurrentIndex(view.width.findData(4))
    view.a.setText("1")
    view.b.setText("3")
    view.op.setCurrentIndex(view.op.findData("nonrestore"))
    assert view.stages.rowCount()==5
    assert view.stages.item(4,3).text()=="1"
    view.op.setCurrentIndex(view.op.findData("signeddivide"))
    view.a.setText("9")
    view.b.setText("3")
    assert view.result[-1].quotient==2
    assert view.result[-1].remainder==1
    assert "= -2" in view.flags.text() and "= -1" in view.flags.text()
    view.a.setText("8")
    view.b.setText("F")
    assert "overflow" in view.flags.text().lower()
    view.b.setText("0")
    assert view.result is None and view.stages.rowCount()==0
    lab.mark_saved(); lab.close()


def test_packed_bcd_modes(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    view=lab.arithmetic
    view.width.setCurrentIndex(view.width.findData(8))
    view.a.setText("99")
    view.b.setText("01")
    view.op.setCurrentIndex(view.op.findData("bcdadd"))
    assert view.result.word==0 and view.result.carry==1
    assert view.stages.rowCount()==2 and view.stages.item(0,5).text()=="6"
    assert view.representation.item(0,5).text()=="99"
    view.base.setCurrentIndex(view.base.findData(10))
    assert view.a.text()=="153" and view.result.word==0
    view.base.setCurrentIndex(view.base.findData(16))
    view.a.setText("00")
    view.op.setCurrentIndex(view.op.findData("bcdsub"))
    assert view.result.word==0x99 and view.result.borrow==1
    view.a.setText("AB")
    assert view.result is None and view.stages.rowCount()==0
    view.op.setCurrentIndex(1)
    assert view.result.word==0xAC
    assert view.representation.item(0,5).text()=="-85"
    lab.mark_saved(); lab.close()


def test_binary16_inspector(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    view=lab.arithmetic
    view.width.setCurrentIndex(view.width.findData(8))
    view.a.setText("3C00")
    view.b.setText("3800")
    view.op.setCurrentIndex(view.op.findData("fpADD"))
    assert view.width.currentData()==16 and not view.width.isEnabled()
    assert view.result.word==0x3E00
    assert view.representation.item(2,5).text()=="3/2"
    view.op.setCurrentIndex(view.op.findData("fpdecode"))
    assert view.result.value==1 and view.representation.rowCount()==1
    view.a.setText("10000")
    assert view.result is None and view.stages.rowCount()==0
    view.a.setText("3C00")
    view.op.setCurrentIndex(1)
    assert view.width.isEnabled() and view.result.word==0x7400
    lab.mark_saved(); lab.close()


def test_control_registers_in_cycle_view(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace,"ION\nCLA\nHLT")
    lab.step()
    assert lab.cpu.ien==1 and lab.cpu.r==0
    lab.step()
    assert lab.cpu.r==1 and lab.cpu.sc==0
    lab.cycles.select(3)
    detail={lab.cycles.detail.item(i,0).text():lab.cycles.detail.item(i,2).text()
            for i in range(lab.cycles.detail.rowCount())}
    assert detail["R"]=="1" and detail["SC"]=="0" and detail["I"]=="0"
    lab.step()
    assert lab.cycles.groups.item(0,0).text()=="RT0" and lab.cpu.r==0
    lab.back()
    assert lab.cpu.r==1
    lab.mark_saved(); lab.close()


def test_selected_common_bus_view(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace,"LDA 100\nHLT\nORG 100\nHEX ABCD\nEND")
    lab.step()
    lab.cycles.select(4)
    assert lab.cycles.bus.control.source=="M"
    assert lab.cycles.bus.control.value==0xABCD
    assert "DR.LD" in lab.cycles.controls.text()
    lab.cycles.select(5)
    assert lab.cycles.bus.control.select==0
    assert "ALU.DR" in lab.cycles.controls.text()
    lab.back()
    assert lab.cycles.bus.control is None
    lab.mark_saved(); lab.close()


def test_microprogram_inspector(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    view=lab.microprogram
    for _ in range(6):view.step()
    assert view.model.ac==5 and view.model.car==64
    assert "ADD" in view.fields.text()
    view.control.setPlainText("80:00000")
    assert view.model is None and not view.step_button.isEnabled()
    view.load()
    assert view.model is None
    view.example()
    assert view.model.car==64 and view.model.ac==0
    lab.mark_saved(); lab.close()


def test_symbolic_microassembler_ui(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    view=lab.microprogram
    original=view.control.toPlainText()
    view.mode.setCurrentIndex(view.mode.findData("symbolic"))
    assert view.model is None and view.control.toPlainText()==original
    view.example()
    assert view.model.car==64 and "40:" in view.listing.toPlainText()
    for _ in range(6):view.step()
    assert view.model.ac==5
    view.control.setPlainText("ADD, SUB U JMP NEXT")
    view.load()
    assert view.model is None and not view.listing.toPlainText() and view.status.text()
    lab.mark_saved(); lab.close()


def test_microprogram_reverse_and_sequencer(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    view=lab.microprogram
    assert not view.back_button.isEnabled()
    for _ in range(3):view.step()
    assert view.sequencer.trace.next_source=="MAP"
    assert view.trace.rowCount()==3 and view.model.car==0
    view.back()
    assert view.model.car==66 and view.trace.rowCount()==2
    assert view.sequencer.trace.after["CAR"]==66
    view.back();view.back()
    assert view.model.car==64 and view.sequencer.trace is None
    assert not view.back_button.isEnabled()
    view.step()
    view.control.setPlainText("40:00000")
    assert view.history is None and view.trace.rowCount()==0
    lab.mark_saved(); lab.close()


def test_microinstruction_builder_and_source_navigation(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    view=lab.microprogram
    builder=view.builder
    initial=view.control.toPlainText()
    builder.address.setValue(90)
    builder.fields[0].setCurrentIndex(builder.fields[0].findData(1))
    builder.fields[1].setCurrentIndex(builder.fields[1].findData(1))
    assert builder.word is None and not builder.append_button.isEnabled()
    builder.fields[1].setCurrentIndex(0)
    assert builder.word is not None
    builder.append()
    assert view.model is None and view.control.toPlainText().startswith(initial)
    appended=view.control.toPlainText()
    builder.append()
    assert view.control.toPlainText()==appended
    view.load()
    for _ in range(3):view.step()
    live=view.model.registers()
    view.inspect_history(0)
    assert view.model.registers()==live and view.last.before["CAR"]==64
    assert view.control.textCursor().selectedText().startswith("40:")
    view.mode.setCurrentIndex(view.mode.findData("symbolic"))
    view.example()
    view.step()
    assert "FETCH:" in view.control.textCursor().selectedText()
    builder.address.setValue(91)
    builder.append()
    assert "ORG 91" in view.control.toPlainText() and view.history is None
    lab.mark_saved(); lab.close()


def test_cpu_organization_view(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    view=lab.organization
    view.external.setValue(12)
    view.selectors[2].setCurrentIndex(1)
    view.execute()
    assert view.registers.words[0]==12
    view.selectors[0].setCurrentIndex(1)
    view.op.setCurrentIndex(view.op.findData(2))
    view.execute()
    assert view.registers.words[0]==24 and "001" in view.control.text()
    view.stack_input.setValue(0xABCD)
    view.push()
    assert view.stack.sp==1 and view.stack.words[1]==0xABCD
    view.stack_input.setValue(0)
    view.pop()
    assert view.stack_input.value()==0xABCD and view.stack.empty
    view.pop()
    assert view.stack.empty and view.stack_status.text()
    lab.mark_saved(); lab.close()


def test_memory_stack_and_addressing_view(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    view=lab.organization
    view.stack_mode.setCurrentIndex(view.stack_mode.findData("memory"))
    assert view.stack.sp==0x440
    view.stack_input.setValue(0x1234);view.push()
    assert view.stack.sp==0x43F and view.stack.words[0x43F]==0x1234
    view.pop();assert view.stack.empty and view.stack_input.value()==0x1234
    view.address_field.setValue(0x100)
    view.address_mode.setCurrentIndex(view.address_mode.findData("indirect"))
    view.evaluate_address()
    assert view.last_address.operand==0xABCD and view.address_reads.rowCount()==2
    view.address_mode.setCurrentIndex(view.address_mode.findData("auto_increment"))
    view.address_register.setValue(65535);view.evaluate_address()
    assert view.address_register.value()==0 and view.last_address.effective_address==65535
    view.address_memory.setPlainText("FFFF:10000");view.evaluate_address()
    assert view.last_address is None and view.address_reads.rowCount()==0
    lab.mark_saved(); lab.close()


def test_expression_formats_view(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    view=lab.organization.expression_view
    assert view.result.word==56 and view.trace.rowCount()==8
    view.format.setCurrentIndex(view.format.findData(3))
    assert view.result is None and view.trace.rowCount()==0
    view.evaluate()
    assert view.result.word==56 and view.trace.rowCount()==4
    view.expression.setText("A/(B-B)")
    view.evaluate()
    assert view.result is None and view.trace.rowCount()==0 and view.summary.text()
    lab.mark_saved(); lab.close()


def test_pipeline_view(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    view=lab.pipeline
    view.step()
    assert view.timeline.rowCount()==1
    view.run()
    assert view.model.done and view.model.registers[5]==5
    view.forward.setChecked(False)
    assert view.model is None and view.timeline.rowCount()==0
    view.load();view.run()
    assert view.model.done and view.model.registers[5]==5 and view.model.stalls>0
    lab.mark_saved(); lab.close()


def test_pipeline_predictor_controls(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    view=lab.pipeline
    view.shared.setChecked(True)
    view.predictor.setCurrentIndex(view.predictor.findData("taken"))
    assert view.model is None
    view.load();view.run()
    assert view.model.done and view.model.registers[5]==5
    assert view.model.branches==1 and view.model.mispredictions==0
    assert view.model.shared_port
    lab.mark_saved(); lab.close()


def test_vector_pipeline_view(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    view=lab.vector_pipeline
    view.step()
    assert view.trace.rowCount()==1
    view.run()
    assert view.model.output()==((6,13,22,33),) and view.model.cycles==6
    view.mode.setCurrentIndex(view.mode.findData("matrix"))
    assert view.model is None
    view.example();view.run()
    assert view.model.output()==((58,64),(139,154)) and view.trace.rowCount()==14
    view.inputs[0].setPlainText("1 x")
    view.load()
    assert view.model is None and view.trace.rowCount()==0
    lab.mark_saved(); lab.close()


def test_interleaving_view(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    view=lab.interleaving
    view.sequential();view.run()
    assert view.model.cycles==19 and view.timeline.rowCount()==19
    view.strided();view.run()
    assert view.model.cycles==64 and view.model.stalls==45
    view.mapping.setCurrentIndex(1)
    assert view.model is None and view.timeline.rowCount()==0
    view.sequential();view.run()
    assert view.model.cycles==64
    lab.mark_saved(); lab.close()


def test_floating_pipeline_view(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    view=lab.float_pipeline
    view.step()
    assert view.timeline.rowCount()==1 and not view.model.results
    view.run()
    assert view.model.cycles==9 and view.timeline.rowCount()==9
    assert [r.result.word for r in view.model.results]==[0x3E00,0x3C00,0x3C00,2,0x7C00,0x7E00]
    view.source.setPlainText("ADD 0000 FFFFF")
    view.load()
    assert view.model is None and view.timeline.rowCount()==0
    lab.mark_saved(); lab.close()


def test_io_organization_view(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    v=lab.io_organization
    for action in v.handshake.SEQUENCES["source"]:v.advance(action)
    assert v.handshake.received==[0x41] and v.handshake_trace.rowCount()==4
    v.handshake_mode.setCurrentIndex(1)
    for action in v.handshake.SEQUENCES["destination"]:v.advance(action)
    assert v.handshake.received==[0x41] and v.handshake_trace.rowCount()==4
    v.request(3);v.request(1)
    assert v.irq.select().winner==1
    v.acknowledge()
    assert v.irq.service==[1] and not v.ack.isEnabled()
    v.end()
    assert v.irq.select().winner==3
    v.mask.setValue(0)
    assert not v.ack.isEnabled() and v.irq.pending==8
    lab.mark_saved(); lab.close()


def test_dma_fifo_view(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    v=lab.io_organization
    v.dma.run()
    assert v.dma.model.done and v.dma.model.memory.read(0)==0x1234
    assert v.irq.pending==4
    v.dma.direction.setCurrentIndex(1)
    v.dma.mode.setCurrentIndex(1);v.dma.load();v.dma.run()
    assert list(v.dma.model.device)==[0x1234,0xABCD,0,0xFF]
    assert v.dma.model.cycles==19
    v.fifo.value.setValue(9);v.fifo.edge(False,True)
    v.fifo.value.setValue(8);v.fifo.edge(True,True)
    assert v.fifo.model.contents()==(8,)
    v.fifo.edge(True,False)
    assert v.fifo.model.empty
    lab.mark_saved(); lab.close()


def test_learning_center_search_progress_and_routes(workspace):
    from ui.learning_center import LearningCenter
    from ui.program_lab import ProgramLab
    from ui.logic_lab import LogicLab
    from learning_catalog import TOOLS
    workspace.editor.setPlainText("AC ← M[100]")
    workspace.run_translation()
    source=workspace.editor.toPlainText()
    output=workspace.output.toPlainText()
    center=LearningCenter(workspace)
    assert center.list.count()==len(TOOLS)
    center.search.setText("DMA")
    assert center.list.count()==1 and center.current_id()=="dma"
    center.toggle_practiced()
    assert center.practiced=={"dma"}
    restored=LearningCenter(workspace)
    assert restored.practiced=={"dma"}
    center.chapter.setCurrentIndex(center.chapter.findData(13))
    assert center.list.count()==0 and not center.open_button.isEnabled()
    center.search.clear()
    assert "coherence" in center.gap.text()
    assert center.current_id()=="multiprocessor" and center.open_button.isEnabled()
    computer=ProgramLab(workspace)
    logic=LogicLab(workspace)
    for tool in TOOLS:
        if tool.lab=="computer":computer.select_tool(tool.route)
        elif tool.lab=="logic":logic.select_tool(tool.route)
    computer.select_tool("dma")
    assert computer.inspector.currentWidget() is computer.io_organization
    assert computer.io_organization.tabs.currentWidget() is computer.io_organization.dma
    assert all(widget.isHidden() for widget in computer.cpu_widgets)
    computer.select_tool("live")
    assert all(not widget.isHidden() for widget in computer.cpu_widgets)
    computer.select_tool("microbuilder")
    assert computer.microprogram.detail_tabs.currentWidget() is computer.microprogram.builder
    logic.select_tool("bus")
    assert logic.memory_tabs.currentWidget() is logic.bus_view
    assert workspace.editor.toPlainText()==source and workspace.output.toPlainText()==output
    computer.mark_saved(); computer.close();logic.close();center.close();restored.close()


def test_learning_center_persian_and_launch(workspace):
    from ui.learning_center import LearningCenter
    workspace.languages.setCurrentIndex(workspace.languages.findData("fa"))
    center=LearningCenter(workspace)
    center.search.setText("وقفه اولویت")
    assert center.current_id()=="interrupt"
    center.launch()
    assert center.selected.id=="interrupt"


def test_focused_learning_tool_pauses_without_reset(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    assert lab.cpu is not None
    cpu=lab.cpu
    lab.step()
    before=lab.steps
    lab.timer.start(1000)
    lab.select_tool("fifo")
    assert not lab.timer.isActive()
    assert lab.cpu is cpu and lab.steps==before
    lab.select_tool("live")
    assert lab.cpu is cpu and lab.steps==before
    lab.mark_saved(); lab.close()


def test_shared_motion_policy(workspace,app):
    from ui.motion import MotionTabs,motion_allowed,TAB_DURATION
    from ui.preferences import Preferences
    from PySide6.QtCore import QAbstractAnimation
    from PySide6.QtWidgets import QWidget
    tabs=MotionTabs()
    tabs.addTab(QWidget(),"First")
    tabs.addTab(QWidget(),"Second")
    tabs.resize(400,220);tabs.show();app.processEvents()
    bar=tabs.tabBar()
    assert isinstance(workspace.tabs,MotionTabs)
    assert bar._animation.duration()==TAB_DURATION
    prefs=Preferences(workspace)
    prefs.change("reduced_motion",True)
    assert not motion_allowed()
    tabs.setCurrentIndex(1)
    assert bar._animation.state()==QAbstractAnimation.State.Stopped
    assert bar._position==bar.target()
    prefs.change("reduced_motion",False)
    assert motion_allowed()
    tabs.setCurrentIndex(0)
    app.processEvents()
    prefs.change("reduced_motion",True)
    assert bar._animation.state()==QAbstractAnimation.State.Stopped
    assert bar._position==bar.target()
    tabs.close();prefs.close()


def test_learning_visual_roles(workspace):
    from ui.learning_center import LearningCenter
    center=LearningCenter(workspace)
    assert center.list.objectName()=="learningList"
    assert center.task.objectName()=="learningTask"
    assert center.gap.objectName()=="muted"
    assert center.progress.maximum()==center.list.count()
    center.close()


def test_shared_navigation_rail(workspace,app):
    from ui.program_lab import ProgramLab
    from ui.logic_lab import LogicLab
    from PySide6.QtTest import QTest
    from PySide6.QtCore import Qt
    lab=ProgramLab(workspace)
    lab.show();app.processEvents()
    nav=lab.navigation
    assert nav.list.count()==lab.inspector.count()==11
    assert not nav.compact and lab.inspector.tabBar().isHidden()
    cpu=lab.cpu
    nav.list.setCurrentRow(9)
    assert lab.inspector.currentWidget() is lab.io_organization
    assert lab.cpu is cpu
    lab.select_tool("microbuilder")
    assert nav.list.currentRow()==6
    nav.list.setFocus()
    QTest.keyClick(nav.list,Qt.Key.Key_Down)
    assert lab.inspector.currentWidget() is lab.organization
    nav.toggle.click()
    assert nav.compact and nav.list.isHidden() and not lab.inspector.tabBar().isHidden()
    assert lab.inspector.currentWidget() is lab.organization
    lab.select_tool("dma")
    assert nav.list.currentRow()==9
    nav.toggle.click()
    assert not nav.compact and nav.list.currentRow()==9
    nav.set_compact(True)
    restored=ProgramLab(workspace)
    assert restored.navigation.compact
    logic=LogicLab(workspace)
    assert not logic.navigation.compact
    logic.select_tool("bus")
    assert logic.navigation.list.currentRow()==2
    logic.navigation.list.setCurrentRow(1)
    assert logic.mode_tabs.currentWidget() is logic.sequential
    lab.mark_saved(); lab.close();restored.mark_saved(); restored.close();logic.close()


def test_navigation_rail_persian(workspace):
    from ui.program_lab import ProgramLab
    workspace.languages.setCurrentIndex(workspace.languages.findData("fa"))
    lab=ProgramLab(workspace)
    assert lab.navigation.list.item(0).text()=="نمای زنده"
    assert lab.navigation.list.item(9).text()=="سازمان ورودی/خروجی"
    assert "جمع" in lab.navigation.toggle.accessibleName()
    lab.navigation.set_compact(True)
    assert "باز" in lab.navigation.toggle.accessibleName()
    lab.mark_saved(); lab.close()


def test_live_architecture_canvas(workspace,app):
    from ui.program_lab import ProgramLab
    from ui.datapath_view import edge_routes
    lab=ProgramLab(workspace)
    lab.show();app.processEvents()
    lab.step()
    v=lab.datapath
    assert v.last_step.mnemonic=="LDA" and v.groups.count()==6
    snapshot=lab.cpu.registers().copy()
    v.groups.setCurrentIndex(1)
    assert v.group.timing==1 and edge_routes(v.group)==("M",("IR",))
    assert v.group.control.value==v.last_step.word
    assert lab.cpu.registers()==snapshot
    v.groups.setCurrentIndex(4)
    assert edge_routes(v.group)==("M",("DR",))
    v.groups.setCurrentIndex(5)
    assert edge_routes(v.group)==(None,()) and "ALU.DR" in v.signals.text()
    v.focus.setChecked(True)
    assert lab.cpu_widgets[1].isHidden() and not lab.cpu_widgets[2].isHidden()
    assert not v.canvas.grab().isNull()
    v.focus.setChecked(False)
    assert not lab.cpu_widgets[1].isHidden()
    lab.microstep()
    assert v.group.timing==0 and v.last_step==lab.cpu.pending_event
    lab.mark_saved(); lab.close()


def test_procedural_brand_feedback(workspace,app):
    from ui.brand import brand_icon
    from ui.preferences import Preferences
    from PySide6.QtCore import QAbstractAnimation
    assert not brand_icon().isNull()
    workspace.show();app.processEvents()
    mark=workspace.brand_mark
    prefs=Preferences(workspace)
    prefs.change("reduced_motion",True)
    workspace.editor.setPlainText("AC ← M[100]")
    workspace.run_translation()
    assert mark.state=="success" and mark.progress is None
    assert mark.animation.state()==QAbstractAnimation.State.Stopped
    workspace.editor.setPlainText("AR ← PC")
    workspace.run_translation()
    assert mark.state=="error"
    prefs.change("glass_enabled",False)
    assert not mark.glass and not mark.grab().isNull()
    prefs.change("reduced_motion",False)
    workspace.editor.setPlainText("AC ← M[100]")
    workspace.run_translation()
    assert mark.state=="success"
    prefs.change("reduced_motion",True)
    assert mark.progress is None and mark.animation.state()==QAbstractAnimation.State.Stopped
    prefs.close()


def test_multiprocessor_route_and_live_grant(workspace):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace)
    lab.select_tool("multiprocessor")
    v=lab.multiprocessor
    assert lab.inspector.currentWidget() is lab.multiprocessor_tabs
    assert lab.multiprocessor_tabs.currentWidget() is v
    v.step()
    assert v.last.grant==0 and v.model.memory[0]==0x100
    v.run()
    assert v.model.served==[2]*4 and v.trace.rowCount()==8
    v.policy.setCurrentIndex(1);v.example();v.run()
    assert v.model.waited==[0,2,4,6]
    assert not v.canvas.grab().isNull()
    lab.mark_saved(); lab.close()


def test_waveform_inspection_and_export(workspace,tmp_path):
    from ui.logic_lab import LogicLab
    lab=LogicLab(workspace)
    lab.select_tool("sequential")
    v=lab.sequential
    v.selector.setCurrentIndex(v.selector.findData("D"))
    v.buttons["D"].setChecked(True);v.pulse()
    assert v.waveform.rows[-1].number==3 and v.cursor==3
    v.waveform.choose(2)
    assert not v.follow.isChecked() and "Q=1" in v.inspection.text()
    before=(v.model.value,v.model.clock,tuple(v.model.history))
    v.waveform.choose(0)
    assert "Q=0" in v.inspection.text()
    assert (v.model.value,v.model.clock,tuple(v.model.history))==before
    v.follow.setChecked(True);assert v.cursor==3
    for _ in range(40):v.pulse()
    assert len(v.waveform.rows)==16 and v.position.maximum()>0
    v.position.setValue(v.position.minimum())
    assert not v.follow.isChecked()
    assert not v.waveform.grab().isNull()
    target=tmp_path/"trace.csv";v.write_history(target)
    assert len(target.read_text().splitlines())==65
    v.reset();assert v.cursor==0 and len(v.waveform.rows)==1
    lab.close()


def test_cache_view_conflicts_and_dirty_flush(workspace):
    from ui.logic_lab import LogicLab
    lab=LogicLab(workspace);lab.select_tool("cache")
    v=lab.cache
    assert lab.memory_tabs.currentWidget() is v
    v.example();assert v.model.hits==0 and v.trace.rowCount()==6
    v.ways.setCurrentIndex(1);v.example()
    assert v.model.hits==4 and v.lines.rowCount()==8
    v.address.setValue(4);v.value.setValue(0xABCD);v.access(True)
    assert v.model.memory.read(4)==0 and v.last.value==0xABCD
    v.flush();assert v.model.memory.read(4)==0xABCD
    assert not v.canvas.grab().isNull()
    lab.close()


def test_cam_and_paging_routes(workspace):
    from ui.logic_lab import LogicLab
    lab=LogicLab(workspace);lab.select_tool("cam")
    v=lab.address_translation
    assert v.tabs.currentWidget() is v.cam
    assert v.cam.match.matches==(0,1,3)
    v.cam.mask.setValue(255);assert v.cam.match.matches==(3,)
    lab.select_tool("virtual-memory")
    assert v.tabs.currentWidget() is v.paging
    v.paging.example()
    assert v.paging.last.value==0xCAFE and v.paging.model.page_outs==1
    assert v.paging.trace.rowCount()==7 and not v.paging.canvas.grab().isNull()
    lab.close()


def test_serial_frame_fifo_and_irq_route(workspace,app):
    from ui.program_lab import ProgramLab
    lab=ProgramLab(workspace);lab.select_tool("serial")
    io=lab.io_organization;v=io.serial
    assert io.tabs.currentWidget() is v
    v.parity.setCurrentIndex(1)
    v.start();v.step();assert v.model.rx==[0]
    v.finish();assert v.model.fifo.contents()==(0xA5,)
    assert io.irq.select().pending & 8
    v.flip.setCurrentIndex(v.flip.findData(1))
    v.start();v.finish()
    assert v.model.result.parity_error and v.model.fifo.contents()==(0xA5,)
    assert v.trace.rowCount()==11 and not v.canvas.grab().isNull()
    v.read();assert v.model.fifo.empty
    lab.show();app.processEvents()
    v.flip.setCurrentIndex(0);v.start();v.play()
    assert v.timer.isActive()
    lab.select_tool("interrupt");app.processEvents()
    assert not v.timer.isActive() and v.model.active
    lab.select_tool("serial");assert v.model.active
    v.finish();assert v.model.fifo.contents()==(0xA5,)
    lab.mark_saved(); lab.close()


def test_crossbar_routes_bilingual(workspace):
    from ui.program_lab import ProgramLab
    from PySide6.QtCore import Qt
    for language in ("en","fa"):
        workspace.languages.setCurrentIndex(workspace.languages.findData(language))
        lab=ProgramLab(workspace);lab.select_tool("crossbar")
        v=lab.crossbar
        assert lab.multiprocessor_tabs.currentWidget() is v
        assert v.fa==(language=="fa")
        assert v.layoutDirection()==(Qt.LayoutDirection.RightToLeft if v.fa else Qt.LayoutDirection.LeftToRight)
        assert v.trace.layoutDirection()==Qt.LayoutDirection.LeftToRight
        assert v.demo.itemText(0)==("بانک‌های مستقل" if v.fa else "Independent banks")
        v.run();assert v.model.cycles==2 and sum(v.model.served)==8
        v.demo.setCurrentIndex(1);v.example();v.run()
        assert v.model.cycles==8
        assert not v.canvas.grab().isNull()
        lab.select_tool("multiprocessor");assert lab.multiprocessor_tabs.currentWidget() is lab.multiprocessor
        lab.mark_saved(); lab.close()


def test_synchronization_bilingual_route(workspace):
    from ui.program_lab import ProgramLab
    from PySide6.QtCore import Qt
    for lang in ("en","fa"):
        workspace.languages.setCurrentIndex(workspace.languages.findData(lang))
        lab=ProgramLab(workspace);lab.select_tool("synchronization")
        v=lab.synchronization
        assert lab.multiprocessor_tabs.currentWidget() is v
        assert v.layoutDirection()==(Qt.LayoutDirection.RightToLeft if lang=="fa" else Qt.LayoutDirection.LeftToRight)
        assert v.trace.layoutDirection()==Qt.LayoutDirection.LeftToRight
        v.run();assert v.model.shared==2 and v.model.done
        v.mode.setCurrentIndex(1);v.run()
        assert v.model.shared==1 and v.trace.rowCount()==6
        assert ("به‌روزرسانی ازدست‌رفته" if lang=="fa" else "Lost update") in v.status.text()
        assert not v.canvas.grab().isNull()
        lab.mark_saved(); lab.close()


@pytest.mark.parametrize("style",["ansi","iec"])
def test_gate_symbol_functional_geometry(app,style):
    from PySide6.QtWidgets import QGraphicsScene
    from ui.gate_symbols import draw_gate,pin_offsets,WIDTH,CENTER
    from ui.theme import PALETTES
    from logic_engine import gate_value
    for op in ("NOT","AND","OR","NAND","NOR","XOR","XNOR"):
        for count in ((1,) if op=="NOT" else (2,3,4)):
            bits=tuple(i%2 for i in range(count))
            out=gate_value(op,*bits)
            scene=QGraphicsScene()
            draw_gate(scene,op,0,0,bits,out,PALETTES["dark"],style)
            inputs=sorted((i for i in scene.items() if i.data(0)=="functional-input"),key=lambda i:i.data(1))
            outputs=[i for i in scene.items() if i.data(0)=="functional-output"]
            states={i.data(1):i.text() for i in scene.items() if i.data(0)=="pin-state"}
            bubbles=[i for i in scene.items() if i.data(0)=="inversion-bubble"]
            assert len(inputs)==count and len(outputs)==1
            assert [i.rect().center().y() for i in inputs]==list(pin_offsets(count))
            assert outputs[0].rect().center().x()==WIDTH
            assert outputs[0].rect().center().y()==CENTER
            assert states=={-1:str(out),**{i:str(b) for i,b in enumerate(bits)}}
            assert len(bubbles)==int(op in ("NOT","NAND","NOR","XNOR"))


@pytest.mark.parametrize("language",["en","fa"])
def test_all_learning_routes_locale_and_document_integrity(workspace,language):
    from PySide6.QtCore import Qt
    from ui.learning_center import LearningCenter
    from ui.logic_lab import LogicLab
    from ui.program_lab import ProgramLab
    from learning_catalog import TOOLS
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    workspace.editor.setPlainText("AC ← M[100]")
    workspace.run_translation()
    snapshot=(workspace.editor.toPlainText(),workspace.output.toPlainText())
    direction=Qt.LayoutDirection.RightToLeft if language=="fa" else Qt.LayoutDirection.LeftToRight
    center=LearningCenter(workspace);logic=LogicLab(workspace);computer=ProgramLab(workspace)
    for dialog in (center,logic,computer):assert dialog.layoutDirection()==direction
    assert logic.diagram.layoutDirection()==Qt.LayoutDirection.LeftToRight
    assert computer.source.layoutDirection()==Qt.LayoutDirection.LeftToRight
    assert center.list.count()==len(TOOLS)
    for tool in TOOLS:
        center.search.setText(tool.id)
        # The catalog may match additional keywords; the requested entry must be present.
        assert any(center.list.item(i).data(Qt.ItemDataRole.UserRole)==tool.id for i in range(center.list.count()))
        if tool.lab=="logic":logic.select_tool(tool.route)
        elif tool.lab=="computer":computer.select_tool(tool.route)
    assert snapshot==(workspace.editor.toPlainText(),workspace.output.toPlainText())
    computer.mark_saved()
    for dialog in (center,logic,computer):dialog.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_memory_serial_localized_transaction_feedback(workspace,language):
    from PySide6.QtCore import Qt
    from ui.logic_lab import LogicLab
    from ui.program_lab import ProgramLab
    from ui.virtual_memory_view import translation_route
    fa=language=="fa"
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    logic=LogicLab(workspace);logic.select_tool("virtual-memory")
    v=logic.address_translation.paging
    assert translation_route(v.last)==()
    v.access(False)
    assert translation_route(v.last)==("va","tlb","pt","backing","pa")
    v.access(False)
    assert translation_route(v.last)==("va","tlb","pa")
    # Remove the TLB mapping via accesses to other still-resident pages.
    for a in (16,32,0):v.address.setValue(a);v.access(False)
    assert not v.last.fault and not v.last.tlb_hit
    assert translation_route(v.last)==("va","tlb","pt","pa")
    assert ("اصابت TLB" if fa else "TLB hits") in v.stats.text()
    assert v.address.layoutDirection()==Qt.LayoutDirection.LeftToRight
    assert not v.canvas.grab().isNull()
    logic.select_tool("cache");c=logic.cache
    c.access();assert c.status.text()==("عدم اصابت" if fa else "Miss")
    c.access();assert c.status.text()==("اصابت" if fa else "Hit")
    lab=ProgramLab(workspace);lab.select_tool("serial")
    s=lab.io_organization.serial
    s.parity.setCurrentIndex(1);s.flip.setCurrentIndex(s.flip.findData(1))
    s.start();s.finish()
    assert ("خطای توازن" if fa else "Parity error") in s.status.text()
    assert s.payload.layoutDirection()==Qt.LayoutDirection.LeftToRight
    lab.mark_saved(); lab.close();logic.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_arithmetic_focused_without_losing_cpu(workspace,language):
    from ui.program_lab import ProgramLab
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=ProgramLab(workspace)
    lab.step();cpu=lab.cpu;source=lab.source.toPlainText();before=cpu.registers().copy()
    lab.timer.start(1000)
    for route in ("alu","booth","division","decimal","floating"):
        lab.select_tool(route)
        assert all(w.isHidden() for w in lab.cpu_widgets)
        assert not lab.timer.isActive()
        assert lab.cpu is cpu and cpu.registers()==before
    lab.use_registers()
    assert lab.cpu is cpu and cpu.registers()==before
    lab.select_tool("live")
    assert all(not w.isHidden() for w in lab.cpu_widgets)
    assert lab.source.toPlainText()==source and lab.steps==1
    lab.mark_saved(); lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_karnaugh_interactive_route(workspace,app,language):
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from ui.logic_lab import LogicLab
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace)
    document=lab.document
    lab.select_tool("karnaugh")
    view=lab.karnaugh
    assert lab.mode_tabs.currentWidget() is view
    assert lab.navigation.list.currentRow()==3
    assert view.map.layoutDirection()==Qt.LayoutDirection.LeftToRight
    assert view.expression.text()=="D'"
    assert view.cells[0].property("groupSelected")
    lab.show();app.processEvents()
    view.cells[0].setFocus()
    QTest.keyClick(view.cells[0],Qt.Key.Key_Space)
    assert view.values[0] is None
    QTest.keyClick(view.cells[0],Qt.Key.Key_Space)
    assert view.values[0]==0
    view.form.setCurrentIndex(1)
    assert view.solution.form=="POS"
    assert all(view.solution.evaluate(i)==v for i,v in enumerate(view.values) if v is not None)
    view.width.setCurrentIndex(0)
    assert len(view.cells)==4 and view.expression.text()=="0"
    view.example()
    assert view.expression.text()=="(B')"
    assert not view.grab().isNull()
    lab.select_tool("gates")
    assert lab.document is document
    lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_karnaugh_import_existing_circuit(workspace,language):
    from ui.logic_lab import LogicLab
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace)
    lab.selector.setCurrentIndex(lab.selector.findData("full_adder"))
    doc=lab.document
    inputs=dict(lab.inputs)
    lab.select_tool("karnaugh")
    v=lab.karnaugh
    original=v.values.copy()
    assert v.values==original and v.source_output.count()==2
    v.source_output.setCurrentIndex(v.source_output.findData("Cout"))
    v.import_button.click()
    assert v.width.currentData()==3 and len(v.cells)==8
    assert v.values==[0,0,0,1,0,1,1,1]
    assert "C = Cin" in v.mapping.text() and "F = Cout" in v.mapping.text()
    assert lab.document is doc and lab.inputs==inputs
    v.cycle(0)
    edited=v.values.copy()
    lab.select_tool("gates")
    lab.selector.setCurrentIndex(lab.selector.findData("not"))
    lab.select_tool("karnaugh")
    assert not v.import_button.isEnabled() and v.values==edited
    lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_karnaugh_build_confirm_and_undo(workspace,monkeypatch,language):
    from PySide6.QtWidgets import QMessageBox
    from ui.logic_lab import LogicLab
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace)
    lab.select_tool("karnaugh")
    original=lab.document
    view=lab.karnaugh
    values=view.values.copy()
    monkeypatch.setattr(QMessageBox,"question",lambda *a,**k:QMessageBox.StandardButton.No)
    view.build_button.click()
    assert lab.document is original
    assert lab.mode_tabs.currentWidget() is view
    monkeypatch.setattr(QMessageBox,"question",lambda *a,**k:QMessageBox.StandardButton.Yes)
    view.build_button.click()
    assert lab.mode_tabs.currentIndex()==0 and lab.dirty
    assert lab.document.outputs[0][0]=="F"
    assert [o[0] for _,o in lab.circuit.truth_table()]==values
    assert view.values==values
    lab.undo_edit()
    assert lab.document==original and not lab.dirty
    lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_karnaugh_equivalence_table(workspace,language):
    from ui.logic_lab import LogicLab
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace);lab.select_tool("karnaugh")
    view=lab.karnaugh
    document=lab.document
    view.width.setCurrentIndex(0)
    view.cycle(0);view.cycle(0)
    view.results.setCurrentWidget(view.proof)
    assert view.proof.rowCount()==4
    assert view.proof.item(0,1).text()=="X"
    assert view.proof.item(0,2).text()==view.proof.item(0,3).text()=="0"
    view.form.setCurrentIndex(1)
    assert view.proof.item(0,2).text()==view.proof.item(0,3).text()=="0"
    view.cycle(1)
    assert view.proof.item(1,1).text()==view.proof.item(1,3).text()=="1"
    assert lab.document is document
    lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_state_synthesis_route_and_clock(workspace,language):
    from ui.logic_lab import LogicLab
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace);original=lab.document
    lab.select_tool("state-design")
    v=lab.state_design
    assert lab.mode_tabs.currentWidget() is v
    assert v.table.rowCount()==4
    assert not v.out_boxes[1].isEnabled()
    v.ff.setCurrentIndex(v.ff.findData("JK"))
    assert dict(v.model.equations)["J0"].expression=="B"
    v.input.setCurrentIndex(1)
    v.clock.click();assert v.state==1 and len(v.trace)==1
    v.clock.click();assert v.state==0 and len(v.trace)==2
    v.mode.setCurrentIndex(v.mode.findData("Mealy"))
    assert v.out_boxes[1].isEnabled() and not v.trace
    v.out_boxes[1].setCurrentIndex(1)
    assert v.model.step(0,1)[1]==1
    v.width.setCurrentIndex(2)
    assert v.table.rowCount()==16 and v.state==0
    assert lab.document is original
    lab.state_design.mark_saved()  # Explicit test teardown; close guard tested separately.
    lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_state_graph_preview_and_clock(workspace,app,language):
    from ui.logic_lab import LogicLab
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace);lab.select_tool("state-design")
    v=lab.state_design
    lab.show();app.processEvents()
    assert v.graph.state==0 and len(v.graph.edges)==2
    v.input.setCurrentIndex(1)
    assert v.graph.x==1 and v.graph.state==0 and not v.trace
    assert "X=1" in v.graph.accessibleDescription()
    v.clock.click()
    assert v.graph.state==1 and len(v.trace)==1
    v.next_boxes[0].setCurrentIndex(1)
    assert v.graph.state==0 and len(v.graph.edges)==1
    assert v.graph.edges[0].conditions==((0,0),(1,0))
    assert not v.graph.grab().isNull()
    lab.state_design.mark_saved()  # Explicit test teardown; close guard tested separately.
    lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_state_analysis_updates_without_clock(workspace,language):
    from ui.logic_lab import LogicLab
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace);lab.select_tool("state-design")
    v=lab.state_design
    v.views.setCurrentWidget(v.analysis_text)
    assert v.analysis.paths==((0,''),(1,'1'))
    assert v.analysis.classes==((0,),(1,))
    v.next_boxes[1].setCurrentIndex(0)
    assert v.analysis.unreachable==(1,)
    assert not v.trace
    assert ("حالت‌های دسترس‌ناپذیر" if language=="fa" else "Unreachable states") in v.analysis_text.toPlainText()
    v.input.setCurrentIndex(1);v.clock.click()
    assert v.state==0 and len(v.trace)==1
    v.views.setCurrentWidget(v.graph)
    assert len(v.trace)==1
    lab.state_design.mark_saved()  # Explicit test teardown; close guard tested separately.
    lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_state_reduction_preview_preserves_design(workspace,language):
    from ui.logic_lab import LogicLab
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace);lab.select_tool("state-design")
    v=lab.state_design
    v.next_boxes[1].setCurrentIndex(0)
    assert v.reduction.groups==((0,),)
    assert v.reduction.bits==0
    original=v.model
    v.views.setCurrentWidget(v.reduction_text)
    assert v.model is original and v.table.rowCount()==4 and not v.trace
    assert "R0 | 1 | R0 | 0" in v.reduction_text.toPlainText()
    v.input.setCurrentIndex(1);v.clock.click()
    assert v.state==0 and len(v.trace)==1
    lab.state_design.mark_saved()  # Explicit test teardown; close guard tested separately.
    lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_reduced_binary_encoding_preview(workspace,language):
    from ui.logic_lab import LogicLab
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace);lab.select_tool("state-design")
    v=lab.state_design
    v.next_boxes[1].setCurrentIndex(0)
    assert v.reduction.bits==0 and v.encoding.design.bits==1
    assert v.encoding.codes==(0,) and v.encoding.unused==(1,)
    assert v.encoding.design.step(1,0)==v.encoding.design.step(1,1)==(0,0)
    original=v.model
    v.views.setCurrentWidget(v.reduction_text)
    assert "R0 = 0" in v.reduction_text.toPlainText()
    assert v.model is original and v.state==0
    lab.state_design.mark_saved()  # Explicit test teardown; close guard tested separately.
    lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_exercise_file_actions(workspace,language,tmp_path,monkeypatch):
    from PySide6.QtWidgets import QFileDialog,QMessageBox
    from ui.logic_lab import LogicLab
    from logic_exercise import KarnaughExercise,StateExercise,read_exercise,write_exercise
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace)
    circuit=lab.document
    for route,view,exercise in (
        ("karnaugh",lab.karnaugh,KarnaughExercise((0,1,None,0),"POS")),
        ("state-design",lab.state_design,StateExercise(2,"Mealy","JK",tuple(((i//2+i%2)%4,i%2) for i in range(8)))),
    ):
        lab.select_tool(route)
        path=tmp_path/(route+".mano-exercise.json")
        write_exercise(path,exercise)
        monkeypatch.setattr(QFileDialog,"getOpenFileName",lambda *a:(str(path),""))
        monkeypatch.setattr(QMessageBox,"question",lambda *a:QMessageBox.StandardButton.No)
        before=view.exercise()
        view.open_exercise_button.click()
        assert view.exercise()==before
        monkeypatch.setattr(QMessageBox,"question",lambda *a:QMessageBox.StandardButton.Yes)
        view.open_exercise_button.click()
        assert view.exercise()==exercise
        output=tmp_path/(route+"-saved.json")
        monkeypatch.setattr(QFileDialog,"getSaveFileName",lambda *a:(str(output),""))
        view.save_exercise_button.click()
        assert read_exercise(output)==exercise
        path.write_text("invalid",encoding="utf-8")
        monkeypatch.setattr(QMessageBox,"warning",lambda *a:None)
        view.open_exercise_button.click()
        assert view.exercise()==exercise
        assert lab.document is circuit
    lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_chapter1_map_geometry_and_keyboard(workspace,app,language):
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from ui.logic_lab import LogicLab
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace);lab.resize(1360,900)
    lab.select_tool("karnaugh");lab.show();app.processEvents()
    v=lab.karnaugh
    for width in (4,2,3,4):
        v.width.setCurrentIndex(v.width.findData(width));app.processEvents()
        assert v.grid.rowStretch(0)==0 and v.grid.columnStretch(0)==0
        assert v.grid.rowStretch(len(v.matrix))==1
        assert all(h.alignment() & Qt.AlignmentFlag.AlignHCenter for h in v.column_headers)
        for c,h in enumerate(v.column_headers):
            cell=v.cells[v.matrix[0][c]]
            assert abs(h.geometry().center().x()-cell.geometry().center().x())<=2
            assert h.height()<cell.height()
        assert v.grid.rowStretch(4)==(1 if width==4 else 0)
    before=v.values.copy()
    first,second,below=v.matrix[0][0],v.matrix[0][1],v.matrix[1][1]
    v.cells[first].setFocus()
    QTest.keyClick(v.cells[first],Qt.Key.Key_Right)
    assert v.cells[second].hasFocus()
    QTest.keyClick(v.cells[second],Qt.Key.Key_Down)
    assert v.cells[below].hasFocus()
    assert v.values==before
    QTest.keyClick(v.cells[below],Qt.Key.Key_Space)
    assert v.values[below]==1
    lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_state_table_focus_and_row_sizing(workspace,language):
    from PySide6.QtWidgets import QHeaderView
    from ui.logic_lab import LogicLab
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace);lab.select_tool("state-design")
    v=lab.state_design
    assert v.table.verticalHeader().sectionResizeMode(0)==QHeaderView.ResizeMode.Stretch
    v.input.setCurrentIndex(1)
    assert v.table.currentRow()==1
    v.clock.click()
    assert v.table.currentRow()==3 and len(v.trace)==1
    v.width.setCurrentIndex(2)
    assert v.table.verticalHeader().sectionResizeMode(0)==QHeaderView.ResizeMode.ResizeToContents
    assert v.table.currentRow()==1 and not v.trace
    lab.state_design.mark_saved()  # Explicit test teardown; close guard tested separately.
    lab.close()


@pytest.mark.parametrize("language", ["en", "fa"])
def test_lab_motion_preference_shared_by_cpu_and_logic(workspace, language):
    from PySide6.QtWidgets import QCheckBox
    from ui.preferences import Preferences
    from ui.program_lab import ProgramLab
    from ui.logic_lab import LogicLab
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    prefs = Preferences(workspace)
    toggle = prefs.findChild(QCheckBox, "lab_motion")
    assert toggle is not None
    assert toggle.text() == ("انیمیشن سیگنال‌های آزمایشگاه" if language == "fa" else "Animate lab signals")
    toggle.setChecked(False)
    assert not workspace.settings.value("lab_motion", True, type=bool)
    prefs.close()
    cpu = ProgramLab(workspace)
    logic = LogicLab(workspace)
    try:
        assert cpu.datapath.reduced_motion
        assert logic.diagram.reduced_motion
    finally:
        cpu.mark_saved(); cpu.close()
        logic.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_lookahead_preset(workspace,language):
    from ui.logic_lab import LogicLab
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace)
    try:
        lab.selector.setCurrentIndex(lab.selector.findData("lookahead4"))
        assert len(lab.buttons)==9 and lab.table.rowCount()==512
        assert len(lab.circuit.outputs)==5
        for pin in ("A0","A1","A2","A3","Cin"):
            lab.buttons[pin].setChecked(True)
        assert lab.circuit.result(lab.inputs)=={"S0":0,"S1":0,"S2":0,"S3":0,"Cout":1}
        assert "gp3" in lab.equations.toPlainText() and "c4" in lab.equations.toPlainText()
        assert not lab.dirty
        assert not lab.diagram.grab().isNull()
    finally:
        lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_karnaugh_mux_build(workspace,monkeypatch,language):
    from ui.logic_lab import LogicLab
    from PySide6.QtWidgets import QMessageBox
    from boolean_minimizer import minimize
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace)
    try:
        original=lab.document
        lab.select_tool("karnaugh")
        view=lab.karnaugh
        view.gate_family.setCurrentIndex(view.gate_family.findData("MUX"))
        solution=minimize(view.values,view.form.currentData())
        monkeypatch.setattr(QMessageBox,"question",lambda *a,**k:QMessageBox.StandardButton.No)
        view.build_button.click()
        assert lab.document is original
        monkeypatch.setattr(QMessageBox,"question",lambda *a,**k:QMessageBox.StandardButton.Yes)
        view.build_button.click()
        assert tuple(out[0] for _,out in lab.circuit.truth_table())==tuple(solution.evaluate(i) for i in range(len(view.values)))
        lab.undo_edit()
        assert lab.document==original and not lab.dirty
    finally:
        lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_library_and_block_insertion(workspace,monkeypatch,language):
    from ui.logic_lab import LogicLab
    from ui.block_dialog import BlockDialog
    from PySide6.QtWidgets import QDialog,QMessageBox
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace)
    try:
        lab.selector.setCurrentIndex(lab.selector.findData("half_adder"))
        before=lab.document
        monkeypatch.setattr(BlockDialog,"exec",lambda self:QDialog.DialogCode.Rejected)
        lab.insert_block()
        assert lab.document is before
        def accept(dialog):
            dialog.selector.setCurrentIndex(dialog.selector.findData("half_adder"))
            dialog.prefix.setText("h2")
            dialog.fields["A"].setCurrentIndex(dialog.fields["A"].findData("sum"))
            dialog.validate()
            assert dialog.result_document is not None
            return QDialog.DialogCode.Accepted
        monkeypatch.setattr(BlockDialog,"exec",accept)
        lab.insert_block()
        assert lab.dirty and len(lab.document.gates)==4
        assert lab.document.inputs==("A","B","h2_B")
        lab.undo_edit()
        assert lab.document==before and not lab.dirty
        lab.open_sample("nand-xor")
        assert len(lab.document.gates)==4 and all(g.op=="NAND" for g in lab.document.gates)
        assert lab.circuit.result({"A":1,"B":0})=={"Y":1}
        lab.dirty=True
        current=lab.document
        monkeypatch.setattr(QMessageBox,"question",lambda *a,**k:QMessageBox.StandardButton.No)
        lab.open_sample("mux-majority")
        assert lab.document is current
        lab.dirty=False
    finally:
        lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_saved_block_import(workspace,tmp_path,monkeypatch,language):
    from ui.block_dialog import BlockDialog
    from PySide6.QtWidgets import QFileDialog,QMessageBox
    from classic_samples import load_sample
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    base=load_sample("nand-xor")
    dialog=BlockDialog(base,language=="fa",workspace)
    try:
        saved=tmp_path/"majority.mano-logic.json"
        saved.write_text(load_sample("mux-majority").dumps(),encoding="utf-8")
        monkeypatch.setattr(QFileDialog,"getOpenFileName",lambda *a:(str(saved),""))
        dialog.browse()
        assert dialog.selector.currentData()=="imported"
        assert tuple(dialog.fields)==("A","B","C")
        before=dialog.imported
        invalid=tmp_path/"invalid.json"
        invalid.write_text("{}",encoding="utf-8")
        monkeypatch.setattr(QFileDialog,"getOpenFileName",lambda *a:(str(invalid),""))
        monkeypatch.setattr(QMessageBox,"warning",lambda *a:None)
        dialog.browse()
        assert dialog.imported is before
        monkeypatch.setattr(QFileDialog,"getOpenFileName",lambda *a:("",""))
        dialog.browse()
        assert dialog.imported is before
        dialog.fields["A"].setCurrentIndex(dialog.fields["A"].findData("y"))
        dialog.fields["B"].setCurrentIndex(dialog.fields["B"].findData("A"))
        dialog.prefix.setText("majority")
        dialog.validate()
        assert dialog.result_document is not None
        assert dialog.result_document.inputs==("A","B","majority_C")
        for bits,out in dialog.result_document.compile().truth_table():
            a,b,c=bits
            assert out==(a^b,int((a^b)+a+c>=2))
    finally:
        dialog.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_databus_lesson(workspace,monkeypatch,language):
    from ui.logic_lab import LogicLab
    from PySide6.QtWidgets import QMessageBox
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace)
    try:
        lab.select_tool("bus")
        lab.memory_tabs.setCurrentWidget(lab.databus)
        v=lab.databus
        v.examples.setCurrentIndex(v.examples.findData("parallel-load"))
        v.load_example()
        for _ in range(3):
            v.next_step()
        assert tuple(v.model.registers.values())==(6,6,6)
        assert v.model.memory.read(9)==6 and v.model.memory.read(6)==0
        assert v.trace.rowCount()==3 and not v.next_button.isEnabled()
        monkeypatch.setattr(QMessageBox,"question",lambda *a:QMessageBox.StandardButton.No)
        v.reset()
        assert len(v.model.history)==3
        monkeypatch.setattr(QMessageBox,"question",lambda *a:QMessageBox.StandardButton.Yes)
        v.examples.setCurrentIndex(v.examples.findData("bus-contention"))
        v.load_example()
        for _ in range(3):
            v.next_step()
        assert v.bus.text()=="BUS[3:0] = 01XX"
        before=tuple(v.model.registers.values())
        v.loads["AR"].setChecked(True)
        v.tick()
        assert tuple(v.model.registers.values())==before and len(v.model.history)==3
    finally:
        monkeypatch.setattr(QMessageBox,"question",lambda *a:QMessageBox.StandardButton.Discard)
        lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_native_databus_save_open(workspace,tmp_path,monkeypatch,language):
    from ui.logic_lab import LogicLab
    from PySide6.QtWidgets import QFileDialog,QMessageBox
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace)
    try:
        v=lab.databus
        v.drivers["EXT"].setChecked(True)
        v.loads["R0"].setChecked(True)
        v.external.setValue(13)
        v.tick()
        assert v.is_dirty()
        path=tmp_path/"saved.mano"
        monkeypatch.setattr(QFileDialog,"getSaveFileName",lambda *a:(str(path),""))
        assert v.save_file() and not v.is_dirty()
        v.external.setValue(7)
        v.tick()
        monkeypatch.setattr(QFileDialog,"getOpenFileName",lambda *a:(str(path),""))
        monkeypatch.setattr(QMessageBox,"question",lambda *a:QMessageBox.StandardButton.No)
        v.open_file()
        assert v.model.registers["R0"]==7 and v.is_dirty()
        monkeypatch.setattr(QMessageBox,"question",lambda *a:QMessageBox.StandardButton.Yes)
        v.open_file()
        assert v.model.registers["R0"]==13 and v.external.value()==13
        assert v.trace.rowCount()==1 and not v.is_dirty()
        v.external.setValue(2)
        monkeypatch.setattr(QMessageBox,"question",lambda *a:QMessageBox.StandardButton.Cancel)
        assert not v.confirm_close()
    finally:
        monkeypatch.setattr(QMessageBox,"question",lambda *a:QMessageBox.StandardButton.Discard)
        lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_native_state_session(workspace,tmp_path,monkeypatch,language):
    from ui.logic_lab import LogicLab
    from PySide6.QtWidgets import QFileDialog,QMessageBox
    from native_exercise import load
    from state_session import load as load_session
    from pathlib import Path
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace)
    try:
        lab.select_tool("state-design")
        view=lab.state_design
        root=Path(__file__).resolve().parents[1]
        view.apply_exercise(load(root/"examples/design/overlap-101.mano"))
        for bit in (1,0,1)*23:
            view.input.setCurrentIndex(bit)
            view.pulse()
        view.input.setCurrentIndex(0)
        before=view.session()
        assert len(before.inputs)==64
        path=tmp_path/"session.mano"
        monkeypatch.setattr(QFileDialog,"getSaveFileName",lambda *a:(str(path),""))
        view.save_exercise_button.click()
        assert load_session(path)==before
        view.reset_state()
        monkeypatch.setattr(QFileDialog,"getOpenFileName",lambda *a:(str(path),""))
        monkeypatch.setattr(QMessageBox,"question",lambda *a:QMessageBox.StandardButton.No)
        view.open_exercise_button.click()
        assert view.state==0 and not view.trace
        monkeypatch.setattr(QMessageBox,"question",lambda *a:QMessageBox.StandardButton.Yes)
        view.open_exercise_button.click()
        assert view.session()==before and len(view.trace)==64
        expected=view.model.step(before.state,0)[0]
        view.pulse()
        assert view.state==expected and len(view.trace)==64
    finally:
        monkeypatch.setattr(QMessageBox,"question",lambda *a:QMessageBox.StandardButton.Discard)
        lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_databus_alu_controls(workspace,tmp_path,monkeypatch,language):
    from ui.logic_lab import LogicLab
    from PySide6.QtWidgets import QFileDialog,QMessageBox
    from databus_file import load
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace)
    try:
        v=lab.databus
        v.examples.setCurrentIndex(v.examples.findData("alu-borrow"))
        v.load_example()
        for _ in range(4):
            v.next_step()
        assert v.model.registers["R0"]==13
        assert v.model.memory.read(3)==13
        assert v.operation.currentText()=="SUB"
        assert v.trace.item(3,4).text()=="0 / 0 / 1 / 0"
        path=tmp_path/"alu.mano"
        monkeypatch.setattr(QFileDialog,"getSaveFileName",lambda *a:(str(path),""))
        assert v.save_file()
        model,staged=load(path)
        assert staged[-2:]==("SUB",0)
        assert model.history==v.model.history
        v.operation.setCurrentText("ADC")
        v.carry.setChecked(True)
        assert v.is_dirty()
        monkeypatch.setattr(QFileDialog,"getOpenFileName",lambda *a:(str(path),""))
        monkeypatch.setattr(QMessageBox,"question",lambda *a:QMessageBox.StandardButton.Yes)
        v.open_file()
        assert v.operation.currentText()=="SUB" and not v.carry.isChecked()
        assert not v.is_dirty()
    finally:
        monkeypatch.setattr(QMessageBox,"question",lambda *a:QMessageBox.StandardButton.Discard)
        lab.close()


@pytest.mark.parametrize("language",["en","fa"])
@pytest.mark.parametrize("theme",["dark","light","night"])
def test_instructor_source_and_splash(workspace,tmp_path,monkeypatch,language,theme):
    from PySide6.QtWidgets import QFileDialog
    from PySide6.QtCore import Qt
    from academic_source import read_source
    from ui.splash import splash_pixmap
    from update_service import VERSION
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    workspace.themes.setCurrentIndex(workspace.themes.findData(theme))
    workspace.editor.setPlainText("AC ← 0")
    workspace.run_translation()
    before=workspace.editor.toPlainText(),workspace.output.toPlainText()
    dialog=workspace.academic_dialog()
    try:
        dialog.show()
        QApplication.processEvents()
        assert workspace.academic_button.text()==workspace.t("Translator source")
        assert dialog.editor.isReadOnly()
        assert dialog.editor.layoutDirection()==Qt.LayoutDirection.LeftToRight
        assert dialog.raw==read_source()
        assert dialog.editor.toPlainText().splitlines()==dialog.raw.decode("utf-8-sig").splitlines()
        path=tmp_path/"exact.py"
        monkeypatch.setattr(QFileDialog,"getSaveFileName",lambda *args:(str(path),""))
        dialog.save_source()
        assert path.read_bytes()==read_source()
        assert (workspace.editor.toPlainText(),workspace.output.toPlainText())==before
        assert not dialog.grab().isNull()
        for glass in (True,False):
            pix=splash_pixmap(theme,glass,VERSION,language=="fa")
            assert pix.width()==680 and pix.height()==360 and not pix.isNull()
    finally:
        dialog.close()
        dialog.deleteLater()


@pytest.mark.parametrize("language", ["en", "fa"])
def test_state_session_close_guard(workspace, tmp_path, monkeypatch, language):
    from PySide6.QtWidgets import QFileDialog, QMessageBox, QDialog
    from ui.logic_lab import LogicLab
    from state_session import load
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab = LogicLab(workspace)
    view = lab.state_design
    try:
        assert not view.is_dirty()
        view.input.setCurrentIndex(1)
        view.pulse()
        expected = view.session()
        assert view.is_dirty()
        monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Cancel)
        assert not view.confirm_close()
        assert view.session() == expected
        lab.show()
        lab.done(QDialog.DialogCode.Rejected)
        assert lab.isVisible()
        monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Save)
        monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a: ("", ""))
        assert not view.confirm_close()
        assert view.is_dirty()
        monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a: (str(tmp_path / "legacy.json"), ""))
        monkeypatch.setattr(QMessageBox, "warning", lambda *a: None)
        assert not view.confirm_close()
        assert not (tmp_path / "legacy.json").exists()
        # Explicit legacy export saves design only and must not mark the run clean.
        view.save_exercise_button.click()
        assert (tmp_path / "legacy.json").is_file() and view.is_dirty()
        path = tmp_path / "state.mano"
        monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a: (str(path), ""))
        assert view.confirm_close()
        assert load(path) == expected and not view.is_dirty()
        view.pulse()
        assert view.is_dirty()
        monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Discard)
        assert view.confirm_close()
    finally:
        monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Discard)
        lab.close()


@pytest.mark.parametrize("language",["en","fa"])
def test_visual_polish_compact(workspace,language):
    from PySide6.QtGui import QFontDatabase
    from PySide6.QtCore import Qt
    from ui.typography import POINT_SIZE,choose_family
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    workspace.resize(1024,768)
    workspace.show()
    QApplication.processEvents()
    font=QApplication.instance().font()
    default=QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont).family()
    arabic=QFontDatabase.families(QFontDatabase.WritingSystem.Arabic) if language=="fa" else ()
    assert font.family()==choose_family(language,QFontDatabase.families(),arabic,default)
    assert font.pointSizeF()==POINT_SIZE[language]
    assert workspace.width()==1024 and workspace.height()==768
    assert workspace.editor.width()>250 and workspace.output.width()>250
    assert workspace.academic_button.isVisible()
    for editor in (workspace.editor,workspace.output):
        assert editor.font().pointSize()==12
        assert editor.layoutDirection()==Qt.LayoutDirection.LeftToRight
    workspace.editor.setPlainText("AC <- M[100]")
    workspace.run_translation()
    assert workspace.output.toPlainText()=="LDA 100"
