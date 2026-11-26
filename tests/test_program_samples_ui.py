import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from ui.workspace import Workspace
from ui.program_lab import ProgramLab
from program_samples import SAMPLES, load_sample
import cpu_session


def make_lab(tmp_path, language):
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / f"settings-{language}.ini"),
                         QSettings.Format.IniFormat)
    settings.setValue("language", language)
    settings.setValue("reduced_motion", True)
    workspace = Workspace(settings)
    return app, workspace, ProgramLab(workspace)


@pytest.mark.parametrize("language", ["en", "fa"])
def test_bilingual_examples_menu_opens_validated_sample_without_running(
        tmp_path, monkeypatch, language):
    app, workspace, lab = make_lab(tmp_path, language)
    try:
        actions = lab.examples_button.menu().actions()
        assert [action.text() for action in actions] == [
            sample.title[0 if language == "en" else 1] for sample in SAMPLES]
        assert len(actions) == 5
        sample, source = load_sample("addition")
        monkeypatch.setattr(QMessageBox, "question",
                            lambda *a, **k: QMessageBox.StandardButton.Yes)
        actions[0].trigger()
        assert lab.source.toPlainText() == source
        assert lab.program.ok and lab.cpu is not None
        assert lab.cpu.pc == lab.program.entry
        assert lab.steps == 0 and lab.history.steps == 0
        assert not lab.cpu.halted and not lab.timer.isActive()
        assert not lab.is_dirty()
        assert lab.status.text() == sample.task[0 if language == "en" else 1]
    finally:
        lab.mark_saved()
        lab.close()
        workspace.close()


@pytest.mark.parametrize("language", ["en", "fa"])
def test_dirty_sample_replacement_cancel_preserves_live_cpu(
        tmp_path, monkeypatch, language):
    app, workspace, lab = make_lab(tmp_path, language)
    try:
        lab.step()
        assert lab.steps == 1 and lab.is_dirty()
        source, cpu, history = lab.source.toPlainText(), lab.cpu, lab.history
        registers, steps = cpu.registers(), lab.steps
        calls = []
        def cancel(*a, **k):
            calls.append(1)
            return QMessageBox.StandardButton.Cancel
        monkeypatch.setattr(QMessageBox, "question", cancel)
        assert not lab.open_saved_sample("counted-loop")
        assert len(calls) == 1
        assert lab.source.toPlainText() == source
        assert lab.cpu is cpu and lab.history is history
        assert lab.cpu.registers() == registers and lab.steps == steps
        assert lab.timer.isActive() is False
    finally:
        lab.mark_saved()
        lab.close()
        workspace.close()


@pytest.mark.parametrize("language", ["en", "fa"])
def test_dirty_sample_replacement_save_checkpoints_before_switch(
        tmp_path, monkeypatch, language):
    app, workspace, lab = make_lab(tmp_path, language)
    try:
        lab.step()
        assert lab.steps == 1 and lab.is_dirty()
        old_source, old_steps = lab.source.toPlainText(), lab.steps
        checkpoint = tmp_path / "before-sample.mano"
        choices = iter([QMessageBox.StandardButton.Save, QMessageBox.StandardButton.Yes])
        monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: next(choices))
        monkeypatch.setattr(QFileDialog, "getSaveFileName",
                            lambda *a, **k: (str(checkpoint), ""))
        assert lab.open_saved_sample("counted-loop")
        saved_source, program, cpu, saved_steps, breaks = cpu_session.load(checkpoint)
        assert saved_source == old_source and saved_steps == old_steps
        assert lab.steps == 0 and lab.cpu is not None
        assert lab.source.toPlainText() != old_source
        assert not lab.is_dirty()
    finally:
        lab.mark_saved()
        lab.close()
        workspace.close()


@pytest.mark.parametrize("language", ["en", "fa"])
def test_dirty_sample_replacement_discard_is_explicit(
        tmp_path, monkeypatch, language):
    app, workspace, lab = make_lab(tmp_path, language)
    try:
        lab.step()
        assert lab.is_dirty()
        monkeypatch.setattr(QMessageBox, "question",
                            lambda *a, **k: QMessageBox.StandardButton.Discard)
        assert lab.open_saved_sample("subroutine")
        sample, source = load_sample("subroutine")
        assert lab.source.toPlainText() == source
        assert lab.steps == 0 and lab.cpu is not None and not lab.is_dirty()
    finally:
        lab.mark_saved()
        lab.close()
        workspace.close()


@pytest.mark.parametrize("language", ["en", "fa"])
def test_invalid_sample_never_replaces_current_program(
        tmp_path, monkeypatch, language):
    app, workspace, lab = make_lab(tmp_path, language)
    try:
        source, cpu, history = lab.source.toPlainText(), lab.cpu, lab.history
        monkeypatch.setattr("ui.program_lab.load_sample",
                            lambda key: (_ for _ in ()).throw(ValueError("invalid sample")))
        monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: None)
        assert not lab.open_saved_sample("addition")
        assert lab.source.toPlainText() == source
        assert lab.cpu is cpu and lab.history is history
        assert not lab.is_dirty()
    finally:
        lab.mark_saved()
        lab.close()
        workspace.close()
