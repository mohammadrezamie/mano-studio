import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.karnaugh_view import KarnaughView


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize("fa",[False,True])
def test_boolean_laws_view(app,fa):
    v=KarnaughView(fa)
    try:
        values=tuple(v.values)
        v.results.setCurrentWidget(v.laws)
        assert v.laws.law.count()==12
        assert v.laws.table.layoutDirection()==Qt.LayoutDirection.LeftToRight
        v.laws.law.setCurrentIndex(v.laws.law.findData("de-morgan"))
        original=v.laws.equation.text()
        assert "(A + B)'" in original
        v.laws.dual.setChecked(True)
        assert "(A · B)'" in v.laws.equation.text()
        for r in range(8):
            assert v.laws.table.item(r,3).text()==v.laws.table.item(r,4).text()
        assert tuple(v.values)==values
        assert v.results.currentWidget() is v.laws
    finally:
        v.close()
        v.deleteLater()
