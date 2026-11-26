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


def test_prerelease_guard_accepts_forward_beta_line_only():
    script = BUILD_SCRIPT.read_text(encoding="utf-8")
    assert r"$version -notmatch '^\d+\.\d+\.\d+-(dev|alpha|beta|rc)(\.\d+)?$'" in script
    assert "Only explicitly marked development/prerelease builds are allowed." in script



def test_unused_qt_virtual_keyboard_is_pruned_with_a_dependency_guard():
    script = BUILD_SCRIPT.read_text(encoding="utf-8")
    assert "python -m installer.prune_qt $dist" in script
    assert "Qt Virtual Keyboard payload pruning failed." in script


def test_installed_smoke_clears_developer_python_and_qt_paths():
    script = (BUILD_SCRIPT.parents[0] / "smoke.ps1").read_text(encoding="utf-8")
    assert "$env:PATH = \"$env:SystemRoot\\System32;$env:SystemRoot\"" in script
    for name in ("PYTHONHOME", "PYTHONPATH", "QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH",
                 "QT_QPA_FONTDIR", "QML_IMPORT_PATH", "QML2_IMPORT_PATH", "VIRTUAL_ENV", "CONDA_PREFIX"):
        assert f"'{name}'" in script
    assert "SetEnvironmentVariable($name, $null, 'Process')" in script
    assert "SetEnvironmentVariable($name, $savedEnvironment[$name], 'Process')" in script
