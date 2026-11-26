import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox
from ui.workspace import Workspace
from ui.program_lab import ProgramLab


@pytest.mark.parametrize("language", ["en", "fa"])
def test_inspect_full_memory_without_cpu_mutation(tmp_path, language):
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "memory.ini"), QSettings.Format.IniFormat)
    settings.setValue("language", language)
    settings.setValue("reduced_motion", True)
    workspace = Workspace(settings)
    lab = ProgramLab(workspace)
    def rows():
        return {int(lab.memory.item(i,0).text(),16): int(lab.memory.item(i,1).text(),16)
                for i in range(lab.memory.rowCount())}
    try:
        lab.select_tool("register-memory")
        before = lab.cpu.registers()
        known = lab.addresses.copy()
        lab.memory_address.setText("FFF")
        assert lab.inspect_memory()
        assert rows()[4095] == 0 and all(a in rows() for a in range(4080,4096))
        assert lab.memory_page_label.text() == "FF0–FFF"
        assert lab.cpu.registers() == before and not lab.is_dirty()
        lab.memory_address.setText("1000")
        assert not lab.inspect_memory() and lab.inspected_address == 4095
        lab.memory_address.setText("۱۲f")
        assert lab.inspect_memory() and lab.inspected_address == 0x12F
        assert 4095 not in rows() and lab.addresses == known
        lab.break_address.setText("۰x۱۰۰")
        lab.toggle_breakpoint()
        assert lab.history.breakpoints == {0x100}
        lab.clear_memory_page()
        assert set(rows()) == known and lab.inspected_address is None
        lab.mark_saved()
        lab.reset_program()
        assert lab.inspected_address is None
    finally:
        lab.mark_saved()
        lab.close()
        workspace.close()


@pytest.mark.parametrize("language", ["en", "fa"])
def test_export_memory_page(tmp_path, monkeypatch, language):
    import csv
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "export.ini"), QSettings.Format.IniFormat)
    settings.setValue("language", language)
    workspace = Workspace(settings)
    lab = ProgramLab(workspace)
    try:
        lab.memory_address.setText("FFF")
        assert lab.inspect_memory()
        before = lab.cpu.registers()
        memory = lab.cpu.memory.copy()
        path = tmp_path / "report.csv"
        monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a: ("", ""))
        assert not lab.export_memory()
        monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a: (str(path), ""))
        assert lab.export_memory()
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        assert any(row["address_hex"] == "FFF" and row["word_hex"] == "0000" for row in rows)
        assert len(rows) == lab.memory.rowCount()
        assert lab.cpu.registers() == before and lab.cpu.memory == memory and not lab.is_dirty()
    finally:
        lab.mark_saved()
        lab.close()
        workspace.close()


@pytest.mark.parametrize("language", ["en", "fa"])
def test_edit_memory_with_real_cpu(tmp_path, monkeypatch, language):
    import cpu_session
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "edit.ini"), QSettings.Format.IniFormat)
    settings.setValue("language", language)
    settings.setValue("reduced_motion", True)
    workspace = Workspace(settings)
    lab = ProgramLab(workspace)
    try:
        lab.step()
        lab.memory_address.setText("FFF")
        before = lab.cpu.registers()
        monkeypatch.setattr(QInputDialog, "getText", lambda *a, **kw: ("FFFF", True))
        monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.No)
        assert not lab.edit_memory() and lab.cpu.memory[4095] == 0
        assert lab.history.entries
        monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Yes)
        assert lab.edit_memory()
        assert lab.cpu.memory[4095] == 65535 and lab.cpu.registers() == before
        assert not lab.history.entries and lab.steps == 1 and lab.is_dirty()
        path = tmp_path / "edited.mano"
        monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a: (str(path), ""))
        assert lab.save_cpu_session()
        assert cpu_session.load(path)[2].memory[4095] == 65535
        lab.microstep()
        assert not lab.edit_memory() and lab.cpu.memory[4095] == 65535
    finally:
        lab.mark_saved()
        lab.close()
        workspace.close()


@pytest.mark.parametrize("language", ["en", "fa"])
def test_memory_instruction_interpretation(tmp_path, language):
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "decode.ini"), QSettings.Format.IniFormat)
    settings.setValue("language", language)
    settings.setValue("reduced_motion", True)
    workspace = Workspace(settings)
    lab = ProgramLab(workspace, "LDA 100\nHLT\nORG 100\nHEX FFFF\nEND")
    try:
        def decoded(address):
            return next(lab.memory.item(row,2).text() for row in range(lab.memory.rowCount())
                        if lab.memory.item(row,0).text() == address)
        assert decoded("000") == "LDA 100"
        assert decoded("001") == "HLT"
        assert decoded("100") == lab.t("Unsupported", "پشتیبانی‌نشده")
        assert lab.memory.columnCount() == 3
        assert not lab.is_dirty()
    finally:
        lab.mark_saved()
        lab.close()
        workspace.close()


@pytest.mark.parametrize("language", ["en", "fa"])
def test_memory_page_navigation(tmp_path, language):
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "navigate.ini"), QSettings.Format.IniFormat)
    settings.setValue("language", language)
    settings.setValue("reduced_motion", True)
    workspace = Workspace(settings)
    lab = ProgramLab(workspace)
    try:
        lab.select_tool("register-memory")
        before = lab.cpu.registers()
        assert not lab.previous_memory_button.isEnabled()
        assert lab.next_memory_button.isEnabled()
        lab.next_memory_button.click()
        assert lab.inspected_address == 0
        assert not lab.previous_memory_button.isEnabled()
        lab.memory_address.setText("FFF")
        assert lab.inspect_memory()
        assert not lab.next_memory_button.isEnabled()
        assert lab.previous_memory_button.isEnabled()
        lab.previous_memory_button.click()
        assert lab.inspected_address == 0xFE0
        assert lab.memory_page_label.text() == "FE0–FEF"
        lab.clear_memory_page()
        assert lab.inspected_address is None
        assert not lab.clear_memory_button.isEnabled()
        assert lab.cpu.registers() == before and not lab.is_dirty()
        assert lab.begin_source_edit()
        assert not lab.next_memory_button.isEnabled()
        assert not lab.edit_memory_button.isEnabled()
    finally:
        lab.mark_saved()
        lab.close()
        workspace.close()


@pytest.mark.parametrize("language", ["en", "fa"])
def test_incremental_memory_refresh_and_invalid_assembly(tmp_path, language):
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "refresh.ini"), QSettings.Format.IniFormat)
    settings.setValue("language", language)
    settings.setValue("reduced_motion", True)
    workspace = Workspace(settings)
    lab = ProgramLab(workspace)
    try:
        lab.memory_address.setText("FFF")
        assert lab.inspect_memory()
        row = lab.memory.currentRow()
        assert lab.memory.item(row, 0).text() == "FFF"
        first = lab.memory.item(0, 1)
        lab.refresh_memory()
        assert lab.memory.item(0, 1) is first
        lab.cpu.memory[4095] = 0x7001
        lab.refresh_memory()
        assert lab.memory.item(row, 1).text() == "7001"
        assert lab.memory.item(row, 2).text() == "HLT"
        assert lab.memory.item(0, 1) is first
        assert lab.memory.currentRow() == row
        lab.mark_saved()
        assert lab.begin_source_edit()
        lab.source.setPlainText("INVALID")
        lab.reset_program()
        assert lab.cpu is None and lab.memory.rowCount() == 0
        assert not lab.next_memory_button.isEnabled()
        assert not lab.edit_memory_button.isEnabled()
        assert not lab.export_memory_button.isEnabled()
        lab.source.setPlainText("HLT")
        lab.reset_program()
        assert lab.cpu is not None and lab.memory.item(0, 1).text() == "7001"
        assert lab.next_memory_button.isEnabled()
        lab.microstep()
        assert not lab.edit_memory_button.isEnabled()
    finally:
        lab.mark_saved()
        lab.close()
        workspace.close()
