import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox, QDialog
from ui.workspace import Workspace
from ui.program_lab import ProgramLab
import mano_file
import cpu_session


@pytest.mark.parametrize("language", ["en", "fa"])
def test_cpu_close_and_reset_guard(tmp_path, monkeypatch, language):
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    settings.setValue("language", language)
    settings.setValue("reduced_motion", True)
    workspace = Workspace(settings)
    lab = ProgramLab(workspace)
    try:
        assert not lab.is_dirty()
        lab.step()
        expected = lab.cpu.registers()
        assert lab.is_dirty()
        monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Cancel)
        lab.show()
        lab.done(QDialog.DialogCode.Rejected)
        assert lab.isVisible() and lab.cpu.registers() == expected
        lab.reset_program()
        assert lab.cpu.registers() == expected
        monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Save)
        monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a: ("", ""))
        assert not lab.confirm_close() and lab.is_dirty()
        path = tmp_path / "saved.mano"
        monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a: (str(path), ""))
        assert lab.confirm_close() and not lab.is_dirty()
        assert cpu_session.load(path)[2].registers() == expected
        lab.microstep()
        monkeypatch.setattr(QMessageBox, "warning", lambda *a: None)
        assert not lab.confirm_close() and lab.is_dirty()
        monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Discard)
        assert lab.confirm_close()
        lab.source.setPlainText("unfinished assembly")
        assert lab.cpu is None and lab.is_dirty()
        draft = tmp_path / "draft.mano"
        monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a: (str(draft), ""))
        assert lab.save_cpu_session() and not lab.is_dirty()
        assert mano_file.load(draft) == ("asm", "unfinished assembly")
    finally:
        lab.mark_saved()
        lab.close()
        workspace.close()
