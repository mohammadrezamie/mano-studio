import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from ui.coherence_view import CoherenceView


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize("fa", [False, True])
def test_msi_view(app, fa):
    v = CoherenceView(fa=fa)
    try:
        assert v.cache.layoutDirection() == Qt.LayoutDirection.LeftToRight
        v.address.setValue(3)
        v.value.setValue(0xABCD)
        v.access(True)
        assert v.cache.item(0, 3).text() == "3 / M / ABCD"
        assert v.ram.item(0, 3).text() == "0000"
        v.core.setValue(1)
        v.access(False)
        assert v.last.bus == "BusRd"
        assert v.cache.item(0, 3).text() == v.cache.item(1, 3).text() == "3 / S / ABCD"
        assert v.ram.item(0, 3).text() == "ABCD"
        assert v.trace.item(1, 2).text() == ("عدم اصابت" if fa else "Miss")
        v.access(True)
        assert v.last.bus == "BusUpgr"
        assert v.cache.item(0, 3).text() == "I"
        for _ in range(130):
            v.access(False)
        assert v.trace.rowCount() == 128
        v.reset()
        assert v.trace.rowCount() == 0 and v.last is None
        v.example()
        assert v.model.accesses == 2 and v.last.value == 0xABCD
    finally:
        v.close()
        v.deleteLater()
