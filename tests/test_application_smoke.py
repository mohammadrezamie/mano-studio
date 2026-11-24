"""Run the same offline smoke used by the frozen Windows application."""
import os
from pathlib import Path
import subprocess
import sys
import pytest

pytest.importorskip("PySide6")
ROOT=Path(__file__).resolve().parents[1]

def test_application_smoke(tmp_path):
    report=tmp_path/"smoke.txt"
    env=dict(os.environ,QT_QPA_PLATFORM="offscreen")
    result=subprocess.run([sys.executable,str(ROOT/"main.py"),"--smoke-test",str(report)],
                          cwd=ROOT,env=env,capture_output=True,text=True,timeout=120)
    assert result.returncode==0, (report.read_text(encoding="utf-8") if report.exists() else result.stderr)
    assert report.read_text(encoding="utf-8").strip()=="PASS"
