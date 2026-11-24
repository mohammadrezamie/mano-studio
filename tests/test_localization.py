from ui.localization import error_text
from ui.credits import COPYRIGHT, THANKS
from pathlib import Path

def test_academic_credit_and_copyright():
    assert COPYRIGHT in (Path(__file__).resolve().parents[1]/"LICENSE").read_text(encoding="utf-8")
    assert "سیاوش اسحقی" in THANKS[1]
    assert "Siavash Eshaghi" in THANKS[0]

def test_localized_errors_keep_technical_identifiers():
    assert "ABC" in error_text("Unknown label or invalid hexadecimal address: ABC",True)
    assert "برچسب" in error_text("Unknown label or invalid hexadecimal address: ABC",True)
    assert "حلقه" in error_text("Combinational feedback loop; sequential circuits require a clocked model.",True)
    assert error_text("Unknown instruction: XYZ",False)=="Unknown instruction: XYZ"
    assert "UTF-8" in error_text(UnicodeError("invalid encoding"),True)
