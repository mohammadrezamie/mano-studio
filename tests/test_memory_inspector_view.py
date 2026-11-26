import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QFileDialog
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
