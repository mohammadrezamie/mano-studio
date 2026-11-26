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
        assert lab.begin_source_edit()
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


@pytest.mark.parametrize("language", ["en", "fa"])
def test_edit_source_requires_safe_transition(tmp_path, monkeypatch, language):
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "edit.ini"), QSettings.Format.IniFormat)
    settings.setValue("language", language)
    workspace = Workspace(settings)
    lab = ProgramLab(workspace)
    try:
        assert lab.source.isReadOnly() and lab.edit_source_button.isEnabled()
        lab.step()
        original = lab.source.toPlainText()
        cpu, expected = lab.cpu, lab.cpu.registers()
        lab.source.setPlainText("HLT")
        assert lab.source.toPlainText() == original and lab.cpu is cpu
        assert lab.cpu.registers() == expected
        monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Cancel)
        assert not lab.begin_source_edit()
        assert lab.source.isReadOnly() and lab.cpu is cpu
        monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Save)
        path = tmp_path / "before-edit.mano"
        monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a: ("", ""))
        assert not lab.begin_source_edit() and lab.cpu is cpu
        monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a: (str(path), ""))
        assert lab.begin_source_edit()
        assert cpu_session.load(path)[2].registers() == expected
        assert not lab.source.isReadOnly() and lab.cpu is None
        lab.source.setPlainText("HLT")
        lab.reset_program()
        assert lab.cpu is not None and lab.source.isReadOnly()
        lab.step()
        assert lab.cpu.halted
    finally:
        lab.mark_saved()
        lab.close()
        workspace.close()


@pytest.mark.parametrize("language", ["en", "fa"])
def test_open_assembly_draft_without_running(tmp_path, monkeypatch, language):
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "draft.ini"), QSettings.Format.IniFormat)
    settings.setValue("language", language)
    workspace = Workspace(settings)
    lab = ProgramLab(workspace)
    try:
        lab.step()
        cpu, expected = lab.cpu, lab.cpu.registers()
        path = tmp_path / "draft.mano"
        mano_file.save(path, "asm", "unfinished !")
        monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a: (str(path), ""))
        monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Cancel)
        assert not lab.open_cpu_session()
        assert lab.cpu is cpu and lab.cpu.registers() == expected
        monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Discard)
        assert lab.open_cpu_session()
        assert lab.source.toPlainText() == "unfinished !"
        assert not lab.source.isReadOnly() and lab.cpu is None and not lab.is_dirty()
        lab.source.setPlainText("HLT")
        lab.reset_program()
        assert lab.cpu is not None and not lab.cpu.halted
        lab.step()
        assert lab.cpu.halted
    finally:
        lab.mark_saved()
        lab.close()
        workspace.close()


@pytest.mark.parametrize("language", ["en", "fa"])
def test_replace_saves_current_cpu_first(tmp_path, monkeypatch, language):
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "replace.ini"), QSettings.Format.IniFormat)
    settings.setValue("language", language)
    workspace = Workspace(settings)
    lab = ProgramLab(workspace)
    try:
        lab.step()
        cpu, expected = lab.cpu, lab.cpu.registers()
        monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Save)
        monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a: ("", ""))
        assert not lab.open_saved_sample("counted-loop")
        assert lab.cpu is cpu and lab.cpu.registers() == expected
        saved = tmp_path / "before-sample.mano"
        monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a: (str(saved), ""))
        assert lab.open_saved_sample("counted-loop")
        assert cpu_session.load(saved)[2].registers() == expected
        assert lab.cpu is not cpu and not lab.is_dirty()
        lab.step()
        old_cpu = lab.cpu
        invalid = tmp_path / "invalid.mano"
        mano_file.save(invalid, "cpu-run", {})
        monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a: (str(invalid), ""))
        monkeypatch.setattr(QMessageBox, "warning", lambda *a: None)
        def unexpected(*args):
            pytest.fail("Invalid document must be rejected before replacement prompt")
        monkeypatch.setattr(QMessageBox, "question", unexpected)
        assert not lab.open_cpu_session() and lab.cpu is old_cpu
    finally:
        lab.mark_saved()
        lab.close()
        workspace.close()


@pytest.mark.parametrize("language", ["en", "fa"])
def test_empty_assembly_remains_editable_draft(tmp_path, monkeypatch, language):
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "empty.ini"), QSettings.Format.IniFormat)
    settings.setValue("language", language)
    workspace = Workspace(settings)
    lab = ProgramLab(workspace, "; empty")
    try:
        assert lab.cpu is None and lab.history is None
        assert not lab.source.isReadOnly()
        path = tmp_path / "empty.mano"
        monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a: (str(path), ""))
        assert lab.save_cpu_session()
        assert mano_file.load(path) == ("asm", "; empty")
    finally:
        lab.mark_saved()
        lab.close()
        workspace.close()
