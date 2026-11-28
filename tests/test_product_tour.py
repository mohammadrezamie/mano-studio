"""Exercise the real spotlight, skip, replay and document preservation."""
import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from ui.workspace import Workspace
from ui.product_tour import STEPS, TOUR_KEY

@pytest.fixture
def window(tmp_path):
    app=QApplication.instance() or QApplication([])
    settings=QSettings(str(tmp_path/"tour.ini"), QSettings.Format.IniFormat)
    w=Workspace(settings)
    w.show()
    app.processEvents()
    yield w
    if w.product_tour:
        w.product_tour.finish("skipped")
    w.editor.document().setModified(False)
    w.close()
    app.processEvents()

@pytest.mark.parametrize("language",["en","fa"])
def test_tour_navigation_preserves_document(window, language):
    w=window
    w.languages.setCurrentIndex(w.languages.findData(language))
    w.editor.setPlainText("AC ← M[100]")
    w.run_translation()
    w.editor.document().setModified(True)
    w.start_product_tour()
    tour=w.product_tour
    assert tour is not None and tour.index==0
    assert not tour.target_rect.isEmpty()
    assert tour.layoutDirection()==(Qt.LayoutDirection.RightToLeft if language=="fa" else Qt.LayoutDirection.LeftToRight)
    tour.next.click()
    assert tour.index==1
    tour.back.click()
    assert tour.index==0
    w.resize(1100,700)
    QApplication.processEvents()
    assert tour.geometry()==w.centralWidget().rect()
    for _ in STEPS:
        tour.next.click()
        if tour.finished:
            break
    assert tour.finished and w.product_tour is None
    assert w.settings.value(TOUR_KEY)=="completed"
    assert w.editor.toPlainText()=="AC ← M[100]"
    assert w.output.toPlainText()=="LDA 100"
    assert w.editor.document().isModified()
    w.start_product_tour()
    assert w.product_tour.index==0
    QTest.keyClick(w.product_tour.next,Qt.Key.Key_Escape)
    assert w.product_tour is None
    assert w.settings.value(TOUR_KEY)=="skipped"


def test_missing_target_skips(window):
    window.open_button.hide()
    window.start_product_tour()
    tour=window.product_tour
    tour.next.click()
    assert tour.index==2
    tour.skip.click()
    assert window.product_tour is None
