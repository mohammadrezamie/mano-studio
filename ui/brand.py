"""Original procedural Mano identity. One geometry, all sizes and themes.

The moving highlight is UI feedback, not a simulated hardware signal.
No network, bitmap dependency, timer loop or artificial startup delay.
"""
from math import isfinite
from PySide6.QtCore import Qt,QByteArray,QVariantAnimation,QEasingCurve,QRectF
from PySide6.QtGui import QIcon,QPixmap,QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QWidget
from ui.theme import PALETTES,STATUS
from ui.motion import motion_allowed

MARK_POINTS=((15,45),(15,19),(32,35),(49,19),(49,45))
MARK_PATH="M"+" L".join(f"{x} {y}" for x,y in MARK_POINTS)


def pulse_point(progress):
    if not isfinite(progress):raise ValueError("Non-finite pulse position")
    position=max(0.0,min(1.0,float(progress)))*4
    i=min(3,int(position));t=position-i
    a,b=MARK_POINTS[i:i+2]
    return a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t


def brand_svg(theme="dark",glass=True,progress=None,state="neutral",compact=False):
    """Render the same original mark as self-contained SVG XML."""
    theme=theme if theme in PALETTES else "dark"
    bg,panel,raised,fg,muted,accent,border=PALETTES[theme]
    good,bad=STATUS[theme]
    signal={"neutral":accent,"success":good,"error":bad}.get(state,accent)
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">']
    if glass and not compact:
        parts.append(f'<defs><linearGradient id="tile" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{raised}"/><stop offset="1" stop-color="{bg}"/></linearGradient><linearGradient id="mark" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{fg}"/><stop offset="1" stop-color="{accent}"/></linearGradient></defs>')
        fill,stroke="url(#tile)","url(#mark)"
    else:fill,stroke=panel,accent
    parts.append(f'<rect x="3" y="3" width="58" height="58" rx="15" fill="{fill}" stroke="{border}" stroke-width="1.5"/>')
    if not compact:
        parts.append(f'<path d="M8 23 V18 Q8 8 18 8 H37" fill="none" stroke="{fg}" stroke-opacity=".18" stroke-width="1.5" stroke-linecap="round"/>')
    parts.append(f'<path d="{MARK_PATH}" stroke="{stroke}" stroke-width="6" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')
    if not compact:
        for x,y in (MARK_POINTS[0],MARK_POINTS[2],MARK_POINTS[4]):
            parts.append(f'<circle cx="{x}" cy="{y}" r="2.5" fill="{panel}" stroke="{accent}" stroke-width="1"/>')
    if progress is not None:
        x,y=pulse_point(progress)
        parts.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="4" fill="{signal}" stroke="{panel}" stroke-width="1.2"/>')
    parts.append("</svg>")
    return "".join(parts)


def render_mark(painter,rect,theme="dark",glass=True,progress=None,state="neutral",compact=False):
    renderer=QSvgRenderer(QByteArray(brand_svg(theme,glass,progress,state,compact).encode("utf-8")))
    renderer.render(painter,QRectF(rect))


def brand_icon(theme="dark",glass=True):
    """Native window icon sizes generated from the same source."""
    result=QIcon()
    for size in (16,24,32,48,64,128,256):
        pix=QPixmap(size,size);pix.fill(Qt.GlobalColor.transparent)
        painter=QPainter(pix);painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        render_mark(painter,pix.rect(),theme,glass,compact=size<=24)
        painter.end();result.addPixmap(pix)
    return result


class BrandMark(QWidget):
    """Single 360-ms feedback pulse after an actual translation result."""
    def __init__(self,theme="dark",parent=None):
        super().__init__(parent)
        self.theme=theme;self.glass=True;self.reduced=False
        self.progress=None;self.state="neutral"
        self.setFixedSize(44,44)
        self.setAccessibleName("Mano Studio")
        self.animation=QVariantAnimation(self)
        self.animation.setDuration(360)
        self.animation.setStartValue(0.0);self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.valueChanged.connect(self._frame)
        self.animation.finished.connect(self.snap)

    def _frame(self,value):
        self.progress=float(value);self.update()

    def snap(self):
        self.animation.stop();self.progress=None;self.update()

    def set_appearance(self,theme,glass,reduced):
        self.theme=theme;self.glass=bool(glass);self.reduced=bool(reduced)
        if self.reduced:self.snap()
        self.update()

    def feedback(self,ok):
        self.snap();self.state="success" if ok else "error"
        if not self.reduced and motion_allowed() and self.isVisible():
            self.progress=0.0;self.animation.start()
        self.update()

    def hideEvent(self,event):
        self.snap();super().hideEvent(event)

    def paintEvent(self,event):
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        render_mark(painter,self.rect(),self.theme,self.glass,self.progress,self.state)
        painter.end()
