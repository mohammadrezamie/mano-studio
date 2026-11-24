import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
import xml.etree.ElementTree as ET
import pytest
pytest.importorskip("PySide6")
from PySide6.QtCore import QByteArray
from PySide6.QtSvg import QSvgRenderer
from ui.brand import brand_svg,pulse_point,MARK_POINTS
from ui.theme import PALETTES


@pytest.mark.parametrize("theme",tuple(PALETTES))
@pytest.mark.parametrize("glass",[True,False])
@pytest.mark.parametrize("compact",[True,False])
def test_vector_brand_renderable(theme,glass,compact):
    svg=brand_svg(theme,glass,0.5,"success",compact)
    root=ET.fromstring(svg)
    assert root.attrib["viewBox"]=="0 0 64 64"
    assert QSvgRenderer(QByteArray(svg.encode())).isValid()
    if not glass or compact:assert "linearGradient" not in svg
    assert "http://" not in svg.replace("http://www.w3.org/2000/svg","")


def test_pulse_geometry():
    assert [pulse_point(i/4) for i in range(5)]==list(MARK_POINTS)
    assert pulse_point(-1)==MARK_POINTS[0]
    assert pulse_point(2)==MARK_POINTS[-1]
    with pytest.raises(ValueError):pulse_point(float("nan"))
