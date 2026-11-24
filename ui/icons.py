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
    "sidebar": "M3 4h18v16H3zM9 4v16M5 8h2m-2 4h2m-2 4h2",
    "cpu": "M6 6h12v12H6zM9 9h6v6H9zM9 3v3m6-3v3m-6 12v3m6-3v3M3 9h3m-3 6h3m12-6h3m-3 6h3",
    "registers": "M4 4h16v5H4zM4 10h16v5H4zM4 16h16v4H4zM8 6.5h2M8 12.5h2M8 18h2",
    "debug": "M5 4h14v16H5zM8 8h8M8 12h5M8 16h8M3 8h2m-2 8h2",
    "alu": "M4 4l6 4h4l6-4v16l-6-4h-4l-6 4zM8 12h3m-1.5-1.5v3M14 12h3",
    "codes": "M8 5 3 12l5 7m8-14 5 7-5 7M13 5l-2 14",
    "clock": "M3 16h4V6h5v10h5V6h4",
    "microcode": "M4 3h16v18H4zM8 7h8M8 11h8M8 15h5",
    "organization": "M9 3h6v5H9zM3 16h6v5H3zM15 16h6v5h-6zM12 8v4M6 16v-4h12v4",
    "pipeline": "M3 4h5v5H3zM10 10h5v5h-5zM17 16h4v5h-4zM8 7h4v3m3 3h4v3",
    "io": "M3 7h17m-4-4 4 4-4 4M21 17H4m4-4-4 4 4 4",
    "logic": "M3 7h5m-5 10h5M8 4v16h3a8 8 0 0 0 0-16zM19 12h3",
}


def icon(name, color, size=18):
    if name=="brand":
        from ui.brand import brand_icon
        return brand_icon()
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
