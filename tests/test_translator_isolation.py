"""Permanent academic contract: the actual translator must work alone."""
import ast
from pathlib import Path
import shutil
import subprocess
import sys

SOURCE = Path(__file__).resolve().parents[1] / "rtl_translator.py"


def test_translator_imports_only_standard_library():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(alias.name.split(".")[0] in sys.stdlib_module_names for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0
            assert node.module.split(".")[0] in sys.stdlib_module_names


def test_translator_cli_in_isolation(tmp_path):
    # Copy just the source file, no project packages or dependencies.
    script = tmp_path / SOURCE.name
    shutil.copyfile(SOURCE, script)
    source, output = tmp_path / "input.rtl", tmp_path / "output.asm"
    source.write_text("AC ← M[100]\nAC ← AC + M[101]\nM[102] ← AC\nS ← 0\n", encoding="utf-8")
    command = [sys.executable, "-I", "-S", str(script), str(source), "-o", str(output)]
    result = subprocess.run(command, cwd=tmp_path, capture_output=True, timeout=15)
    assert result.returncode == 0, result.stderr
    assert output.read_text(encoding="utf-8") == "LDA 100\nADD 101\nSTA 102\nHLT\n"
    source.write_text("AR ← PC\n", encoding="utf-8")
    result = subprocess.run(command, cwd=tmp_path, capture_output=True, timeout=15)
    assert result.returncode != 0
    assert b"UNSUPPORTED_RTL" in result.stderr
    assert output.read_text(encoding="utf-8") == "LDA 100\nADD 101\nSTA 102\nHLT\n"
