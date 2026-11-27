"""Launch Mano Studio with persisted settings and a startup splash."""
import sys
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QSplashScreen
from ui.theme import PALETTES, apply_theme
from ui.strings import FA
from ui.brand import brand_icon
from ui.splash import splash_pixmap
from ui.typography import apply_ui_font

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
            from example_catalog import EXAMPLES, computer_source
            from ui.program_lab import ProgramLab
            from ui.logic_lab import LogicLab
            window.editor.document().setModified(False)
            window.load_example(EXAMPLES[0])
            assert window.result.ok
            computer = ProgramLab(window, computer_source(EXAMPLES[0], window.result.assembly))
            for _ in range(4):
                computer.step()
            assert computer.cpu.halted and computer.cpu.memory[0x102] == 8
            computer.back()
            assert not computer.cpu.halted
            computer.back()
            assert computer.cpu.memory[0x102] == 0
            computer.arithmetic.a.setText("7FFF")
            computer.arithmetic.b.setText("0001")
            assert computer.arithmetic.result.word == 0x8000 and computer.arithmetic.result.overflow
            computer.close()
            from asm_to_rtl import reverse_translate
            assert reverse_translate("LDA 100 I\nHLT").ok
            lab = LogicLab(window)
            lab.selector.setCurrentIndex(lab.selector.findData("full_adder"))
            lab.choose_row(7,0)
            assert lab.summary.text() == "S = 1   |   Cout = 1"
            lab.write_schematic(Path(directory) / "circuit.svg")
            lab.write_truth_table(Path(directory) / "truth.csv")
            assert (Path(directory) / "circuit.svg").stat().st_size > 0
            lab.mode_tabs.setCurrentIndex(1)
            lab.sequential.buttons["D"].setChecked(True)
            lab.sequential.pulse()
            assert lab.sequential.model.value == 1
            lab.close()
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
    if language not in ("en", "fa"):
        language = "en"
    theme = settings.value("theme", "dark")
    if theme not in PALETTES:
        theme = "dark"
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft if language == "fa" else Qt.LayoutDirection.LeftToRight)
    app.setStyle("Fusion")
    apply_ui_font(app, language)
    glass_enabled = settings.value("glass_enabled", True, type=bool)
    apply_theme(app, theme, glass_enabled)
    app.setWindowIcon(brand_icon(theme,glass_enabled))
    bg, panel, raised, fg, muted, accent, border = PALETTES[theme]
    pix = splash_pixmap(theme,glass_enabled,VERSION,language=="fa")
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
    if len(sys.argv) == 3 and sys.argv[1] == "--runtime-probe":
        from installer.standalone_probe import write_report
        raise SystemExit(write_report(sys.argv[2]))
    raise SystemExit(main())
