import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QMessageBox
from ui.workspace import Workspace
from ui.program_lab import ProgramLab
from program_samples import SAMPLES, load_sample


@pytest.mark.parametrize("language", ["en", "fa"])
def test_saved_program_menu(tmp_path, monkeypatch, language):
    app = QApplication.instance() or QApplication([])
    settings = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    settings.setValue("language", language)
    settings.setValue("reduced_motion", True)
    workspace = Workspace(settings)
    lab = ProgramLab(workspace)
    try:
        actions = lab.examples_button.menu().actions()
        assert [action.text() for action in actions] == [s.title[language == "fa"] for s in SAMPLES]
        before = lab.source.toPlainText()
        cpu = lab.cpu
        monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.No)
        actions[1].trigger()
        assert lab.source.toPlainText() == before and lab.cpu is cpu
        monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.StandardButton.Yes)
        actions[1].trigger()
        sample, source = load_sample("counted-loop")
        assert lab.source.toPlainText() == source
        assert lab.cpu.pc == 0x100 and lab.steps == 0 and not lab.cpu.halted
        assert lab.status.text() == sample.task[language == "fa"]
        for _ in range(sample.steps):
            lab.step()
        assert lab.cpu.halted and lab.cpu.ac == 12
    finally:
        lab.mark_saved()
        lab.close()
        workspace.close()
