"""Developer-only check that real text resolves to visible glyphs before capture.

The Windows offscreen QPA uses a FreeType database rather than the native
Windows font database. CI points it at installed system fonts. No font files
are copied, installed by the app, or redistributed.
"""
import os
from pathlib import Path
import sys


def configure_offscreen_fonts():
    """Call before QApplication; honor an explicit developer override."""
    if sys.platform=="win32" and os.environ.get("QT_QPA_PLATFORM","").split(":")[0]=="offscreen":
        system_fonts=Path(os.environ.get("WINDIR",r"C:\Windows"))/"Fonts"
        if system_fonts.is_dir():os.environ.setdefault("QT_QPA_FONTDIR",str(system_fonts))


def probe_text(text,font):
    """Return actual shaped glyph runs; glyph zero is the missing-glyph sentinel."""
    from PySide6.QtGui import QTextLayout
    layout=QTextLayout(text,font)
    layout.beginLayout()
    line=layout.createLine()
    if line.isValid():line.setLineWidth(10000)
    layout.endLayout()
    runs=layout.glyphRuns()
    glyphs=[int(g) for run in runs for g in run.glyphIndexes()]
    if not glyphs or 0 in glyphs:
        raise RuntimeError(f"Missing glyphs for {font.family()!r}: {text!r} (indices={glyphs})")
    return {"text":text,"requested_family":font.family(),
            "resolved_families":sorted({run.rawFont().familyName() for run in runs}),
            "glyph_count":len(glyphs)}


def check_fonts(app):
    from PySide6.QtCore import qVersion
    from PySide6.QtGui import QFont,QFontDatabase
    families=QFontDatabase.families()
    if not families:raise RuntimeError("No Qt fonts available; screenshot capture would be invalid")
    samples=[]
    for font in (app.font(),QFont("Segoe UI",12)):
        samples.append(probe_text("Mano Studio 0123",font))
        samples.append(probe_text("فارسی گچ پژ",font))
    for font in (QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont),QFont("Consolas",12)):
        samples.append(probe_text("AC ← M[100] ∧ ¬ ⊕",font))
    return {"qt":qVersion(),"platform":app.platformName(),"font_family_count":len(families),
            "samples":samples}


def main():
    import json
    os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
    configure_offscreen_fonts()
    from PySide6.QtWidgets import QApplication
    app=QApplication([])
    print(json.dumps(check_fonts(app),ensure_ascii=True,indent=2))


if __name__=="__main__":main()
