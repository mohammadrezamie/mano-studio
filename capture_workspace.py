"""Capture actual Qt workspace screenshots for visual review."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path
import tempfile
import json
import hashlib
from learning_catalog import TOOLS
from capture_karnaugh import capture_karnaugh
from ui.learning_center import LearningCenter
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication
from ui.logic_lab import LogicLab
from ui.program_lab import ProgramLab
from ui.workspace import Workspace


def capture_routes(app,window,output):
    """Capture each distinct real route once per locale, with entry-to-image mapping."""
    records=[]
    window.themes.setCurrentIndex(window.themes.findData("dark"))
    for language in ("en","fa"):
        window.languages.setCurrentIndex(window.languages.findData(language))
        window.tabs.setCurrentIndex(0)
        app.processEvents()
        center=LearningCenter(window)
        center.resize(1100,750);center.show();app.processEvents()
        target=output/f"{language}-dark-learning-center.png"
        if not center.grab().save(str(target)):raise RuntimeError(f"Could not save {target}")
        center.close();center.deleteLater()
        logic=LogicLab(window);computer=ProgramLab(window)
        logic.resize(1360,900);computer.resize(1360,900)
        lab_by_name={"workspace":window,"logic":logic,"computer":computer}
        seen={}
        for tool in TOOLS:
            key=(tool.lab,tool.route)
            if key not in seen:
                lab=lab_by_name[tool.lab]
                # Keep only the active dialog visible, ensuring hidden timers stop.
                for other in (logic,computer):
                    if other is not lab:other.hide()
                if tool.lab!="workspace":
                    lab.select_tool(tool.route);lab.show()
                else:window.show()
                app.processEvents()
                if tool.route=="gates":
                    logic.diagram.fit();app.processEvents()
                target=output/f"{language}-dark-route-{tool.lab}-{tool.route}.png"
                image=lab.grab()
                if image.isNull() or not image.save(str(target)):
                    raise RuntimeError(f"Could not save {target}")
                seen[key]={"image":target.name,"width":image.width(),"height":image.height(),
                           "sha256":hashlib.sha256(target.read_bytes()).hexdigest()}
            records.append({"entry":tool.id,"chapter":tool.chapter,"language":language,
                            "theme":"dark","lab":tool.lab,"route":tool.route,**seen[key]})
        for dialog in (logic,computer):
            dialog.close();dialog.deleteLater()
        app.processEvents()
    (output/"route-manifest.json").write_text(json.dumps({
        "kind":"actual Qt offscreen render; not manual visual acceptance",
        "entries":records},ensure_ascii=False,indent=2),encoding="utf-8")


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
                window.direction_box.setCurrentIndex(1)
                window.editor.setPlainText("LDA 100 I\nADD 101\nSTA 102\nHLT")
                window.run_translation()
                window.tabs.setCurrentIndex(0)
                app.processEvents()
                target=output/f"{language}-{theme}-reverse.png"
                if not window.grab().save(str(target)):
                    raise RuntimeError(f"Could not save {target}")
                window.editor.document().setModified(False)
                window.direction_box.setCurrentIndex(0)
                window.editor.setPlainText("AC ← M[100]\nAC ← AC + M[101]\nM[102] ← AC\nS ← 0")
                window.run_translation()
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
                capture_karnaugh(app,lab,output,language,theme)
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
                for tab,suffix in ((2,"debugger"),(3,"alu")):
                    computer.inspector.setCurrentIndex(tab)
                    app.processEvents()
                    target=output/f"{language}-{theme}-{suffix}.png"
                    if not computer.grab().save(str(target)):
                        raise RuntimeError(f"Could not save {target}")
                computer.arithmetic.op.setCurrentIndex(0)
                app.processEvents()
                target=output/f"{language}-{theme}-bases.png"
                if not computer.grab().save(str(target)):
                    raise RuntimeError(f"Could not save {target}")
                computer.close()
                computer.deleteLater();lab.deleteLater()
        capture_routes(app,window,output)
        window.editor.document().setModified(False)
        window.close()


if __name__ == "__main__":
    main()
