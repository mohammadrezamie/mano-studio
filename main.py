"""Launch Mano Studio with persisted settings and a startup splash."""
import sys
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
from PySide6.QtWidgets import QApplication, QSplashScreen
from ui.theme import PALETTES, stylesheet
from ui.strings import FA

VERSION = "0.3.0-dev"


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("ManoStudio")
    app.setApplicationName("ManoStudio")
    settings = QSettings()
    language = settings.value("language", "en")
    theme = settings.value("theme", "dark")
    if theme not in PALETTES:
        theme = "dark"
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft if language == "fa" else Qt.LayoutDirection.LeftToRight)
    app.setStyle("Fusion")
    app.setStyleSheet(stylesheet(theme))
    bg, panel, raised, fg, muted, accent, border = PALETTES[theme]
    pix = QPixmap(640, 310)
    pix.fill(QColor(bg))
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QColor(accent))
    painter.setFont(QFont("Segoe UI", 30, QFont.Weight.Bold))
    painter.drawText(35, 85, "MANO STUDIO")
    painter.setPen(QColor(fg))
    painter.setFont(QFont("Segoe UI", 13))
    painter.drawText(35, 125, FA["Build. Translate. Learn."] if language == "fa" else "Build. Translate. Learn.")
    painter.setPen(QColor(muted))
    painter.drawText(35, 165, VERSION)
    painter.drawText(35, 200, FA["Academic project · Morris Mano Basic Computer"] if language == "fa" else "Academic project · Morris Mano Basic Computer")
    painter.end()
    splash = QSplashScreen(pix)
    splash.show()
    splash.showMessage(FA["Loading workspace…"] if language == "fa" else "Loading workspace…", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, QColor(fg))
    app.processEvents()
    from ui.workspace import Workspace
    window = Workspace(settings)
    window.show()
    splash.finish(window)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
