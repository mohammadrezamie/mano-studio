import subprocess
import pytest
from source_metrics import category, line_count, measure


@pytest.mark.parametrize("data,expected", [(b"",0),(b"x",1),(b"x\n",1),(b"\n\n",2),(b"x\r\ny",2)])
def test_lines(data, expected):
    assert line_count(data)==expected


def test_categories():
    assert category("tests/test_a.py")=="python_tests"
    assert category("ui/a.py")=="python_product"
    assert category("installer/build.ps1")=="build_config"
    assert category("README.md")=="documentation"
    assert category("image.png")=="other"


def test_exact_committed_revision(tmp_path):
    def git(*args):
        return subprocess.check_output(["git","-C",str(tmp_path),*args])
    git("init","-q")
    git("config","user.name","Metrics test")
    git("config","user.email","metrics@example.invalid")
    (tmp_path/"tests").mkdir()
    (tmp_path/"main.py").write_bytes(b"# comment\n\nprint(1)\n")
    (tmp_path/"tests"/"test_x.py").write_bytes(b"assert True")
    (tmp_path/"README.md").write_bytes(b"# Intro\n")
    (tmp_path/"image.bin").write_bytes(b"\x00\n\n")
    git("add",".")
    git("commit","-qm","fixture")
    sha=git("rev-parse","HEAD").decode().strip()
    (tmp_path/"main.py").write_bytes(b"changed")
    (tmp_path/"untracked.py").write_bytes(b"not counted\n")
    report=measure(tmp_path,sha)
    assert report["commit"]==sha and report["python_lines"]==4
    assert report["groups"]["python_product"]==dict(files=1,bytes=20,lines=3)
    assert report["groups"]["python_tests"]["lines"]==1
    assert report["groups"]["other"]["lines"]==0
