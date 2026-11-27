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
    # Keep the original test identity while adding the distribution-text contract.
    import hashlib
    license_dir = BUILD_SCRIPT.parent / "licenses"
    expected = {
        "LGPL-3.0-only.txt": "65c5ca88a67c30becee01c5a8816d964b03862f9",
        "GPL-3.0-only.txt": "94a9ed024d3859793618152ea559a168bbcbb5e2",
        "README.md": "eb59c9b4b3075e223fa196aa7e2f8ba783a1bd5a",
    }
    assert "qt-license-texts" in script
    assert "Copy-Item -LiteralPath" in script
    for name, digest in expected.items():
        data = (license_dir / name).read_bytes().replace(b"\r\n", b"\n")
        blob = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
        assert hashlib.sha1(blob).hexdigest() == digest
        assert f"'{name}'" in script


def test_installed_smoke_clears_developer_python_and_qt_paths():
    script = (BUILD_SCRIPT.parents[0] / "smoke.ps1").read_text(encoding="utf-8")
    assert "$env:PATH = \"$env:SystemRoot\\System32;$env:SystemRoot\"" in script
    for name in ("PYTHONHOME", "PYTHONPATH", "QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH",
                 "QT_QPA_FONTDIR", "QML_IMPORT_PATH", "QML2_IMPORT_PATH", "VIRTUAL_ENV", "CONDA_PREFIX"):
        assert f"'{name}'" in script
    assert "SetEnvironmentVariable($name, $null, 'Process')" in script
    assert "SetEnvironmentVariable($name, $savedEnvironment[$name], 'Process')" in script


def test_installer_workflow_test_targets_exist():
    import re
    root = BUILD_SCRIPT.parents[1]
    workflow = (root / ".github" / "workflows" / "windows-installer.yml").read_text(encoding="utf-8")
    targets = set(re.findall(r"tests/test_[a-z_0-9]+\.py", workflow))
    assert "tests/test_release_channel.py" in targets
    assert "tests/test_verify_installed.py" in targets
    missing = sorted(target for target in targets if not (root / target).is_file())
    assert not missing, f"Missing workflow test files: {missing}"


def test_candidate_manifest_module_entry_point():
    import subprocess
    import sys
    root = BUILD_SCRIPT.parents[1]
    result = subprocess.run([sys.executable, "-m", "installer.candidate_manifest", "--help"],
                            cwd=root, capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
    assert "--sha" in result.stdout and "--root" in result.stdout


def test_unused_qml_and_pdf_runtime_are_pruned_before_notice_collection():
    script = BUILD_SCRIPT.read_text(encoding="utf-8")
    assert "python -m installer.prune_qml $dist" in script
    assert "python -m installer.prune_pdf $dist --apply" in script
    assert script.index("python -m installer.prune_qml $dist") < script.index("python installer/collect_notices.py")
    assert script.index("python -m installer.prune_pdf $dist --apply") < script.index("python installer/collect_notices.py")
    assert script.index("python installer/collect_notices.py") < script.index("python -m installer.openssl_notice")
