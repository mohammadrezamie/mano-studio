"""Native offline launch card; no artificial delay or remote assets."""
from PySide6.QtCore import Qt,QRect
from PySide6.QtGui import QPixmap,QPainter,QColor,QFont
from ui.theme import PALETTES
from ui.glass import paint_backdrop
from ui.brand import render_mark
from ui.credits import THANKS,COPYRIGHT


def splash_pixmap(theme,glass,version,fa=False):
    bg,panel,raised,fg,muted,accent,border=PALETTES[theme]
    pix=QPixmap(680,360)
    pix.fill(QColor(bg))
    p=QPainter(pix)
    try:
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        paint_backdrop(p,pix.rect(),theme,glass)
        p.setPen(QColor(border))
        p.setBrush(QColor(panel))
        p.drawRoundedRect(QRect(22,22,636,292),20,20)
        render_mark(p,QRect(44,40,84,84),theme,glass)
        p.setPen(QColor(fg))
        p.setFont(QFont("Segoe UI",29,QFont.Weight.Bold))
        p.drawText(QRect(145,42,480,50),int(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter),"MANO STUDIO")
        p.setFont(QFont("Segoe UI",12))
        p.setPen(QColor(accent))
        p.drawText(QRect(145,94,480,28),int(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter),
                   "RTL  →  ASM   ·   v"+version)
        p.setPen(QColor(border))
        p.drawLine(44,140,636,140)
        alignment=Qt.AlignmentFlag.AlignRight if fa else Qt.AlignmentFlag.AlignLeft
        p.setFont(QFont("Segoe UI",15,QFont.Weight.DemiBold))
        p.setPen(QColor(fg))
        p.drawText(QRect(44,153,592,35),int(alignment|Qt.AlignmentFlag.AlignVCenter),
                   "کامپیوتر پایه موریس مانو" if fa else "Morris Mano Basic Computer")
        p.setFont(QFont("Segoe UI",11))
        p.setPen(QColor(muted))
        p.drawText(QRect(44,195,592,68),int(alignment|Qt.AlignmentFlag.AlignVCenter)|int(Qt.TextFlag.TextWordWrap),
                   THANKS[fa])
        p.setFont(QFont("Segoe UI",9))
        p.drawText(QRect(44,275,592,24),int(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter),COPYRIGHT)
        # Leave a distinct footer for QSplashScreen's real startup message.
    finally:
        p.end()
    return pix
