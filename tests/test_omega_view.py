import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.omega_view import OmegaView


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize("fa",[False,True])
def test_omega_interaction(app,fa):
    v=OmegaView(fa=fa)
    try:
        assert v.table.layoutDirection()==Qt.LayoutDirection.LeftToRight
        v.example()
        assert len(v.results)==2
        assert v.results[0].granted and not v.results[1].granted
        assert v.table.item(1,2).text()==("مسدود" if fa else "Blocked")
        assert v.table.item(1,4).text()=="S0 / P0"
        v.source.setValue(0)
        v.remove()
        assert not v.results
        v.run()
        assert len(v.results)==1 and v.results[0].granted
        v.size.setCurrentIndex(v.size.findData(2))
        assert v.source.maximum()==1 and not v.requests and not v.results
        v.example()
        assert all(t.granted for t in v.results)
        v.resize(800,600)
        v.show()
        app.processEvents()
        assert not v.canvas.grab().isNull()
    finally:
        v.close()
        v.deleteLater()
