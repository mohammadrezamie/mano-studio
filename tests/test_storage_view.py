import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication
from ui.sequential_view import SequentialView
from storage_elements import Storage


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize("fa",[False,True])
def test_storage_lesson(app,fa):
    v=SequentialView("dark",fa)
    try:
        live=(v.model.value,v.model.clock,tuple(v.model.history))
        lesson=v.storage
        v.details.setCurrentWidget(lesson)
        lesson.buttons["S"].setChecked(True)
        lesson.buttons["R"].setChecked(True)
        assert lesson.state==Storage()
        lesson.apply_button.click()
        assert lesson.state==Storage(0,0)
        lesson.buttons["S"].setChecked(False)
        lesson.buttons["R"].setChecked(False)
        lesson.apply_button.click()
        assert lesson.state==Storage(None,None)
        assert lesson.history.rowCount()==2
        lesson.selector.setCurrentIndex(lesson.selector.findData("D_ASYNC"))
        assert lesson.buttons["PREbar"].isChecked() and lesson.buttons["CLRbar"].isChecked()
        lesson.buttons["PREbar"].setChecked(False)
        lesson.apply_button.click()
        assert lesson.state==Storage(1,0)
        assert (v.model.value,v.model.clock,tuple(v.model.history))==live
    finally:
        v.close()
        v.deleteLater()
