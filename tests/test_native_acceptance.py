import copy
import pytest
from installer.native_acceptance import CHECKS, SCENARIOS, validate


@pytest.fixture
def pair():
    manifest = dict(kind="internal-development-candidate", source_sha="a"*40,
                    assets=[dict(name="Setup.exe", sha256="b"*64)])
    record = dict(kind="human-native-windows-observations", source_sha="a"*40,
                  setup_sha256="b"*64, scenarios=[
        dict(scenario=name, windows_architecture="x64", windows_build="26100.1",
             standard_user=True, network_disabled_during_install_and_first_launch=True,
             fixture_reset_before_install=True,
             python_qt_preinstalled=name.startswith("pre-equipped"),
             checks=dict.fromkeys(CHECKS, "PASS"), notes="Synthetic test fixture only",
             evidence_sha256={"fixture.txt":"c"*64}) for name in SCENARIOS])
    return manifest, record


def test_complete_matrix_is_not_release_approval(pair):
    report = validate(*pair)
    assert report["checks"] == 28
    assert report["public_release_approved"] is False
    assert report["human_review_required"] is True


@pytest.mark.parametrize("defect", ["source", "setup", "missing", "duplicate", "architecture",
    "offline", "admin", "snapshot", "clean", "existing", "check", "failed", "notes", "hash"])
def test_reject_incomplete_native_evidence(pair, defect):
    manifest, record = copy.deepcopy(pair)
    row = record["scenarios"][0]
    if defect == "source": record["source_sha"] = "d"*40
    elif defect == "setup": record["setup_sha256"] = "d"*64
    elif defect == "missing": record["scenarios"].pop()
    elif defect == "duplicate": record["scenarios"][1] = row
    elif defect == "architecture": row["windows_architecture"] = "arm64"
    elif defect == "offline": row["network_disabled_during_install_and_first_launch"] = False
    elif defect == "admin": row["standard_user"] = False
    elif defect == "snapshot": row["fixture_reset_before_install"] = False
    elif defect == "clean": row["python_qt_preinstalled"] = True
    elif defect == "existing": record["scenarios"][1]["python_qt_preinstalled"] = False
    elif defect == "check": row["checks"].pop(CHECKS[0])
    elif defect == "failed": row["checks"][CHECKS[0]] = "FAIL"
    elif defect == "notes": row["notes"] = ""
    else: row["evidence_sha256"]["fixture.txt"] = "bad"
    with pytest.raises(ValueError):
        validate(manifest, record)
