import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.sequential_view import SequentialView


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize("fa",[False,True])
def test_reference_preserves_clocked_state(app,fa):
    v=SequentialView("dark",fa)
    try:
        v.selector.setCurrentIndex(v.selector.findData("JK"))
        v.buttons["J"].setChecked(True)
        v.pulse()
        before=(v.model.value,v.model.clock,tuple(v.model.history))
        v.details.setCurrentWidget(v.reference)
        assert v.reference.characteristic.rowCount()==8
        assert v.reference.excitation.rowCount()==4
        assert v.reference.excitation.item(2,2).text()=="X"
        assert v.reference.excitation.item(2,3).text()=="1"
        assert v.reference.excitation.layoutDirection()==Qt.LayoutDirection.LeftToRight
        assert (v.model.value,v.model.clock,tuple(v.model.history))==before
        v.selector.setCurrentIndex(v.selector.findData("SR"))
        assert v.reference.characteristic.item(3,3).text()==("ممنوع" if fa else "Forbidden")
        v.selector.setCurrentIndex(v.selector.findData("REG4"))
        assert v.reference.characteristic.rowCount()==0
        assert v.reference.excitation.rowCount()==0
        v.details.setCurrentIndex(0)
        assert v.waveform.rows
    finally:
        v.close()
        v.deleteLater()
