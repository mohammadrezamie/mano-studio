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
    lab.close()


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
    lab.close()


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
    lab.close()

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


def test_persian_credits_and_optional_labs(workspace,monkeypatch):
    from PySide6.QtWidgets import QMessageBox
    from ui.program_lab import ProgramLab
    from ui.logic_lab import LogicLab
    workspace.languages.setCurrentIndex(1)
    messages=[]
    monkeypatch.setattr(QMessageBox,"about",lambda *args:messages.append(args[-1]))
    workspace.about()
    assert "سیاوش اسحقی" in messages[0] and "Copyright (c) 2026" in messages[0]
    lab=ProgramLab(workspace,"UNKNOWN")
    assert "ناشناخته" in lab.machine.toPlainText()
    assert lab.arithmetic.representation.horizontalHeaderItem(0).text()=="کلمه"
    lab.close()
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
    computer.close()


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
    lab.close()


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
    lab.close()

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
    lab.close()


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
    lab.close()


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
    lab.close()
