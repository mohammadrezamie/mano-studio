"""Capture the actual instructor workflow at two practical desktop sizes."""
import json
import os
from pathlib import Path
import tempfile
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from ui.workspace import Workspace
from ui.splash import splash_pixmap
from update_service import VERSION
from academic_source import read_source
from visual_review import image_info


def capture(output):
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    app=QApplication.instance() or QApplication([])
    app.setStyle("Fusion")
    records=[]
    def save(pix,name):
        if pix.isNull() or not pix.save(str(output/name)):
            raise RuntimeError("Failed real Qt capture: "+name)
        width,height,sha=image_info(output,name)
        records.append(dict(image=name,width=width,height=height,sha256=sha))
    with tempfile.TemporaryDirectory() as directory:
        for language in ("en","fa"):
            for theme in ("dark","light","night"):
                for glass in (True,False):
                    settings=QSettings(str(Path(directory)/f"{language}-{theme}-{glass}.ini"),QSettings.Format.IniFormat)
                    settings.setValue("language",language)
                    settings.setValue("theme",theme)
                    settings.setValue("glass_enabled",glass)
                    settings.setValue("reduced_motion",True)
                    window=Workspace(settings)
                    try:
                        window.editor.setPlainText("AC ← M[100]\nAC ← AC + M[101]\nM[102] ← AC\nS ← 0")
                        window.run_translation()
                        assert window.output.toPlainText()=="LDA 100\nADD 101\nSTA 102\nHLT"
                        stem=f"{language}-{theme}-{'glass' if glass else 'plain'}"
                        for width,height in ((1360,900),(1024,768)):
                            window.resize(width,height)
                            window.show()
                            app.processEvents()
                            save(window.grab(),f"{stem}-workspace-{width}.png")
                        dialog=window.academic_dialog()
                        try:
                            dialog.show()
                            app.processEvents()
                            assert dialog.raw==read_source() and dialog.editor.isReadOnly()
                            save(dialog.grab(),f"{stem}-academic-source.png")
                        finally:
                            dialog.close()
                            dialog.deleteLater()
                        save(splash_pixmap(theme,glass,VERSION,language=="fa"),f"{stem}-splash.png")
                    finally:
                        window.editor.document().setModified(False)
                        window.close()
                        window.deleteLater()
                        app.processEvents()
    (output/"manifest.json").write_text(json.dumps({"version":VERSION,"evidence":"actual Qt offscreen; native visual acceptance pending","captures":records},indent=2),encoding="utf-8")


if __name__=="__main__":
    import sys
    capture(sys.argv[1])
