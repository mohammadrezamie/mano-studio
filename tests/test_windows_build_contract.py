from pathlib import Path

BUILD_SCRIPT = Path(__file__).resolve().parents[1] / "installer" / "build.ps1"


def test_windows_pyinstaller_data_arguments_use_windows_separator():
    script = BUILD_SCRIPT.read_text(encoding="utf-8")
    command = next(line for line in script.splitlines() if "python -m PyInstaller" in line)
    for source, destination in (
        ("rtl_translator.py", "."),
        ("LICENSE", "."),
        ("examples", "examples"),
        ("docs", "docs"),
    ):
        assert f"--add-data '{source};{destination}'" in command
        assert f"--add-data '{source}:{destination}'" not in command


def test_unused_qml_runtime_is_pruned_before_notice_collection():
    script = BUILD_SCRIPT.read_text(encoding="utf-8")
    assert "python -m installer.prune_qml $dist" in script


def test_qt_imageformats_notice_collection_runs_once_after_upstream_license_copy():
    script = BUILD_SCRIPT.read_text(encoding="utf-8")
    assert script.count("python -m installer.qt_imageformats_notices") == 1
    assert script.index("python -m installer.qt_imageformats_notices") > script.index("Copy-Item -LiteralPath")
