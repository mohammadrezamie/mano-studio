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
@pytest.mark.parametrize("form",["SOP","POS"])
def test_forms_and_hazards(app,fa,form):
    view=KarnaughView(fa)
    try:
        view.form.setCurrentIndex(view.form.findData(form))
        view.results.setCurrentWidget(view.analysis_panel)
        view.hazard_example_button.click()
        assert view.width.currentData()==3
        assert view.analysis.layoutDirection()==Qt.LayoutDirection.LeftToRight
        report=view.analysis.toPlainText()
        assert "3 ↔ 7" in report
        assert "Σm(" in report and "ΠM(" in report
        assert "Static-1:" in report if form=="SOP" else "Static-0:" in report
        assert ("BC" if form=="SOP" else "(B' + C')") in report
        view.reset()
        assert "3 ↔ 7" not in view.analysis.toPlainText()
        assert view.results.currentWidget() is view.analysis_panel
    finally:
        view.close()
        view.deleteLater()
