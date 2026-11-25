import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication
from ui.sequential_view import SequentialView


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize("fa",[False,True])
def test_timing_view_independent(app,fa):
    view=SequentialView("dark",fa)
    try:
        before=(view.model.value,view.model.clock,tuple(view.model.history))
        view.details.setCurrentWidget(view.timing)
        timing=view.timing
        assert timing.result.valid and timing.result.sampled==1
        timing.example()
        assert timing.result.setup_violations==(8,)
        assert timing.result.hold_violations==(11,)
        assert timing.result.sampled is None
        timing.fields[0].setValue(10)
        assert timing.result.coincident
        timing.fields[1].setValue(10)
        assert timing.result is None
        timing.fields[1].setValue(12)
        assert timing.result.coincident
        assert (view.model.value,view.model.clock,tuple(view.model.history))==before
        view.resize(1100,800)
        view.show();app.processEvents()
        assert not timing.diagram.grab().isNull()
    finally:
        view.close()
        view.deleteLater()
