import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from ui.workspace import Workspace
from ui.program_lab import ProgramLab


@pytest.mark.parametrize("language", ["en", "fa"])
def test_cpu_session_dialog(tmp_path, monkeypatch, language):
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    settings.setValue("language", language)
    settings.setValue("reduced_motion", True)
    workspace = Workspace(settings)
    lab = ProgramLab(workspace)
    try:
        lab.step()
        expected = lab.cpu.registers()
        memory = lab.cpu.memory.copy()
        lab.history.breakpoints.add(3)
        path = tmp_path / "session.mano"
        monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a: (str(path), ""))
        assert lab.save_cpu_session()
        lab.step()
        later = lab.cpu.registers()
        monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a: (str(path), ""))
        monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Cancel)
        assert not lab.open_cpu_session()
        assert lab.cpu.registers() == later
        monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Discard)
        assert lab.open_cpu_session()
        assert lab.cpu.registers() == expected and lab.cpu.memory == memory
        assert lab.steps == 1 and lab.history.breakpoints == {3}
        assert not lab.history.entries
        lab.step()
        assert lab.cpu.registers() == later
        lab.microstep()
        before = path.read_bytes()
        monkeypatch.setattr(QMessageBox, "warning", lambda *a: None)
        assert not lab.save_cpu_session()
        assert path.read_bytes() == before
    finally:
        lab.mark_saved()
        lab.close()
        workspace.close()
