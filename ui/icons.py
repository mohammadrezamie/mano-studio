"""Original vector icons; no network, font icon dependency or external assets."""
from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

PATHS = {
    "open": "M3 7V5h7l2 2h9v3 M3 7v12h15l3-9H7l-4 9",
    "translate": "M4 7h15m-4-4 4 4-4 4M20 17H5m4-4-4 4 4 4",
    "export": "M12 3v12m-4-4 4 4 4-4M4 16v5h16v-5",
    "settings": "M4 6h16M4 12h16M4 18h16 M8 4v4m8 2v4m-5 2v4",
    "examples": "M4 4h7v16H4zM13 4h7v16h-7z",
    "labs": "M4 4h16v16H4zM8 8h8v8H8zM12 1v3m0 16v3M1 12h3m16 0h3",
    "undo": "M9 5 4 10l5 5M4 10h10a5 5 0 0 1 0 10",
    "redo": "M15 5l5 5-5 5m5-5H10a5 5 0 0 0 0 10",
    "search": "M10 3a7 7 0 1 0 0 14 7 7 0 0 0 0-14m5 12 6 6",
    "copy": "M8 8h12v12H8zM4 16V4h12",
    "brand": "M4 20V4l8 9 8-9v16M8 20v-6m8 6v-6",
}


def icon(name, color, size=18):
    path = PATHS.get(name)
    if not path:
        return QIcon()
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="{path}" fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    renderer=QSvgRenderer(QByteArray(svg.encode("utf-8")))
    result=QIcon()
    for scale in (1,2,3):
        pix=QPixmap(size*scale,size*scale)
        pix.fill(Qt.GlobalColor.transparent)
        painter=QPainter(pix)
        renderer.render(painter)
        painter.end()
        pix.setDevicePixelRatio(scale)
        result.addPixmap(pix)
    return result
