import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import pytest
pytest.importorskip("PySide6")
from render_preflight import configure_offscreen_fonts
configure_offscreen_fonts()
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from render_preflight import check_fonts,probe_text


def test_required_shaped_glyphs():
    app=QApplication.instance() or QApplication([])
    report=check_fonts(app)
    assert report["font_family_count"]>0
    assert len(report["samples"])==6
    assert all(r["glyph_count"] and r["resolved_families"] for r in report["samples"])


def test_empty_text_rejected():
    app=QApplication.instance() or QApplication([])
    with pytest.raises(RuntimeError):probe_text("",QFont())
