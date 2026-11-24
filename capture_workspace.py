"""Capture actual Qt workspace screenshots for visual review."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path
import tempfile
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication
from ui.logic_lab import LogicLab
from ui.program_lab import ProgramLab
from ui.workspace import Workspace


def main():
    app = QApplication([])
    app.setStyle("Fusion")
    output = Path("screenshots")
    output.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        settings = QSettings(str(Path(directory) / "settings.ini"), QSettings.Format.IniFormat)
        window = Workspace(settings)
        window.apply_appearance()
        window.resize(1360, 900)
        window.editor.setPlainText("AC ← M[100]\nAC ← AC + M[101]\nM[102] ← AC\nS ← 0")
        window.run_translation()
        window.show()
        for language in ("en", "fa"):
            window.languages.setCurrentIndex(1 if language == "fa" else 0)
            for theme in ("dark", "light", "night"):
                window.themes.setCurrentIndex(window.themes.findData(theme))
                for tab, mode in enumerate(("editor", "pad", "builder")):
                    window.tabs.setCurrentIndex(tab)
                    app.processEvents()
                    target = output / f"{language}-{theme}-{mode}.png"
                    if not window.grab().save(str(target)):
                        raise RuntimeError(f"Could not save {target}")
                # Capture actual optional labs too, without opening modal exec loops.
                lab=LogicLab(window)
                lab.resize(1360,900)
                lab.selector.setCurrentIndex(lab.selector.findData("full_adder"))
                lab.show()
                app.processEvents()
                lab.diagram.fit()
                lab.choose_row(5,0)
                app.processEvents()
                target=output/f"{language}-{theme}-logic.png"
                if not lab.grab().save(str(target)):
                    raise RuntimeError(f"Could not save {target}")
                lab.canvas_edit.setChecked(True)
                app.processEvents()
                target=output/f"{language}-{theme}-logic-edit.png"
                if not lab.grab().save(str(target)):
                    raise RuntimeError(f"Could not save {target}")
                lab.canvas_edit.setChecked(False)
                lab.mode_tabs.setCurrentIndex(1)
                lab.sequential.buttons["D"].setChecked(True)
                lab.sequential.pulse()
                app.processEvents()
                target=output/f"{language}-{theme}-sequential.png"
                if not lab.grab().save(str(target)):
                    raise RuntimeError(f"Could not save {target}")
                lab.close()
                computer=ProgramLab(window)
                computer.resize(1360,900)
                computer.show()
                computer.step()
                computer.step()
                computer.pause()
                app.processEvents()
                target=output/f"{language}-{theme}-computer.png"
                if not computer.grab().save(str(target)):
                    raise RuntimeError(f"Could not save {target}")
                computer.close()
        window.editor.document().setModified(False)
        window.close()


if __name__ == "__main__":
    main()
