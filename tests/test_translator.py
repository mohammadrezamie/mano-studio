import subprocess
import sys
from pathlib import Path

import pytest
from rtl_translator import translate


@pytest.mark.parametrize("rtl,asm", [
    ("AC ← M[100]", "LDA 100"),
    ("AC=AC+M[101]", "ADD 101"),
    ("M[102] <- AC", "STA 102"),
    ("AC ← AC ∧ M[100]", "AND 100"),
    ("AC=AC&M[a]", "AND 00A"),
    ("AC=0", "CLA"),
    ("AC=AC+1", "INC"),
    ("AC=¬AC", "CMA"),
    ("AC=~AC", "CMA"),
    ("PC=fff", "BUN FFF"),
    ("S=0", "HLT"),
    ("  ac   <-  m [ 0 ]  ; comment", "LDA 000"),
])
def test_rules(rtl, asm):
    result = translate(rtl)
    assert result.ok and result.assembly == asm


@pytest.mark.parametrize("rtl", ["AR=PC", "A C=0", "AC=M[1 0]", "AC=M[GGG]", "AC=M[1000]", "AC=AC+2", "AC=M[100] junk", "AC=M[-1]"])
def test_rejection(rtl):
    result = translate(rtl)
    assert not result.ok
    with pytest.raises(ValueError):
        _ = result.assembly


def test_mapping_and_error_position():
    result = translate("# header\r\nAC=0\r\n\r\n  AC=M[1000]\nS=0")
    assert [i.line for i in result.instructions] == [2, 5]
    error = result.diagnostics[0]
    assert (error.line, error.column, error.code) == (4, 8, "ADDRESS_RANGE")


def test_empty():
    assert translate("\n# comment\n; comment").assembly == ""


def test_cli(tmp_path):
    script = Path(__file__).resolve().parents[1] / "rtl_translator.py"
    source, output = tmp_path / "input.rtl", tmp_path / "output.asm"
    source.write_text("AC ← M[100]\nAC=AC+M[101]\nM[102]=AC\nS=0", encoding="utf-8-sig")
    command = [sys.executable, str(script), str(source), "-o", str(output)]
    assert subprocess.run(command, capture_output=True).returncode == 0
    expected = "LDA 100\nADD 101\nSTA 102\nHLT\n"
    assert output.read_text() == expected
    source.write_text("AR=PC", encoding="utf-8")
    assert subprocess.run(command, capture_output=True).returncode == 1
    assert output.read_text() == expected
    assert subprocess.run([sys.executable, str(script), str(source), "-o", str(source)], capture_output=True).returncode == 1
