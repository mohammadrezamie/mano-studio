"""Exercise the unmodified academic source outside the application."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "instructor-demo"


def test_independent_instructor_demo(tmp_path):
    script = tmp_path / "rtl_translator.py"
    shutil.copyfile(ROOT / script.name, script)
    output = tmp_path / "output.asm"
    def run(name):
        input_file = tmp_path / name
        shutil.copyfile(FIXTURES / name, input_file)
        return subprocess.run([sys.executable, "-I", "-S", str(script), str(input_file),
                               "-o", str(output)], cwd=tmp_path, capture_output=True, timeout=15)
    good = run("demo.rtl")
    assert good.returncode == 0, good.stderr
    expected = (FIXTURES / "demo.expected.asm").read_text(encoding="utf-8")
    assert output.read_text(encoding="utf-8") == expected
    assert len(expected.splitlines()) == 32
    assert len({line.split()[0] for line in expected.splitlines()}) == 25
    bad = run("invalid.rtl")
    assert bad.returncode == 1
    assert bad.stderr.count(b"ADDRESS_RANGE") == 1
    assert bad.stderr.count(b"UNSUPPORTED_RTL") == 2
    assert output.read_text(encoding="utf-8") == expected
