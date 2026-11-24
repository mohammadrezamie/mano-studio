"""Capture actual Qt workspace screenshots for visual review."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path
import tempfile
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication
from ui.theme import apply_theme
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
        window.editor.document().setModified(False)
        window.close()


if __name__ == "__main__":
    main()
