import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication,QMessageBox
from ui.workspace import Workspace
from ui.logic_lab import LogicLab


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize("language",["en","fa"])
@pytest.mark.parametrize("family",["NAND","NOR"])
def test_karnaugh_universal_build(app,tmp_path,monkeypatch,language,family):
    workspace=Workspace(QSettings(str(tmp_path/"settings.ini"),QSettings.Format.IniFormat))
    workspace.languages.setCurrentIndex(workspace.languages.findData(language))
    lab=LogicLab(workspace)
    try:
        original=lab.document
        lab.select_tool("karnaugh")
        view=lab.karnaugh
        view.gate_family.setCurrentIndex(view.gate_family.findData(family))
        values=tuple(view.values)
        monkeypatch.setattr(QMessageBox,"question",lambda *a,**k:QMessageBox.StandardButton.No)
        view.build_button.click()
        assert lab.document is original
        monkeypatch.setattr(QMessageBox,"question",lambda *a,**k:QMessageBox.StandardButton.Yes)
        view.build_button.click()
        assert lab.document.gates and all(g.op==family for g in lab.document.gates)
        assert all(v is None or out[0]==v for v,(_,out) in zip(values,lab.circuit.truth_table()))
        lab.undo_edit()
        assert lab.document==original and not lab.dirty
    finally:
        lab.close()
        workspace.editor.document().setModified(False)
        workspace.close()
