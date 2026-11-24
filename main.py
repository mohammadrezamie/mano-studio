"""Launch Mano Studio with persisted settings and a startup splash."""
import sys
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
from PySide6.QtWidgets import QApplication, QSplashScreen
from ui.theme import PALETTES, apply_theme
from ui.strings import FA
from ui.glass import paint_backdrop

from update_service import VERSION


def smoke_test(report_path):
    """Exercise the installed application without internet or personal settings."""
    import tempfile
    from pathlib import Path
    import traceback
    from ui.workspace import Workspace

    report = Path(report_path)
    try:
        app = QApplication([sys.argv[0]])
        app.setStyle("Fusion")
        apply_theme(app, "dark")
        with tempfile.TemporaryDirectory() as directory:
            settings = QSettings(str(Path(directory) / "smoke.ini"), QSettings.Format.IniFormat)
            window = Workspace(settings)
            window.show()
            app.processEvents()
            window.editor.setPlainText("AC ← M[100]\nAC ← AC + M[101]\nM[102] ← AC\nS ← 0")
            window.run_translation()
            assert window.output.toPlainText() == "LDA 100\nADD 101\nSTA 102\nHLT"
            window.editor.setPlainText("AR ← PC")
            window.run_translation()
            assert not window.result.ok and window.output.toPlainText() == ""
            base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
            assert (base / "rtl_translator.py").is_file()
            assert (base / "examples" / "add.rtl").is_file()
            window.editor.document().setModified(False)
            window.close()
        report.write_text("PASS\n", encoding="utf-8")
        return 0
    except Exception:
        report.write_text(traceback.format_exc(), encoding="utf-8")
        return 1


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
    glass_enabled = settings.value("glass_enabled", True, type=bool)
    apply_theme(app, theme, glass_enabled)
    bg, panel, raised, fg, muted, accent, border = PALETTES[theme]
    pix = QPixmap(640, 310)
    pix.fill(QColor(bg))
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    paint_backdrop(painter, pix.rect(), theme, glass_enabled)
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
    if len(sys.argv) == 3 and sys.argv[1] == "--smoke-test":
        raise SystemExit(smoke_test(sys.argv[2]))
    raise SystemExit(main())
