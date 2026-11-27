"""Validate a human-recorded native Windows acceptance matrix.

This does not run an installer or attest that observations are truthful.
It only rejects incomplete, wrong-candidate or contradictory records.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

SCENARIOS = ("clean-standard-user", "pre-equipped-standard-user")
CHECKS = ("offline-install", "no-manual-prerequisites", "private-runtime",
          "no-global-path-change", "offline-first-launch", "rtl-asm-roundtrip",
          "persian-english-persistence", "three-themes", "glass-and-low-motion",
          "keyboard-navigation", "display-100-150-200", "save-open-reopen",
          "reinstall-preserves-settings", "uninstall-preserves-other-apps")


def validate(manifest, record):
    if manifest.get("kind") != "internal-development-candidate":
        raise ValueError("Expected internal candidate manifest")
    source = manifest["source_sha"]
    if not re.fullmatch(r"[a-f0-9]{40}", source):
        raise ValueError("Invalid candidate source")
    assets = [a for a in manifest["assets"] if a["name"].endswith(".exe")]
    if len(assets) != 1 or not re.fullmatch(r"[a-f0-9]{64}", assets[0]["sha256"]):
        raise ValueError("Expected exact Setup asset")
    if (record.get("source_sha") != source or
            record.get("setup_sha256") != assets[0]["sha256"]):
        raise ValueError("Native record belongs to another candidate")
    if record.get("kind") != "human-native-windows-observations":
        raise ValueError("Wrong native evidence kind")
    seen = set()
    for row in record["scenarios"]:
        name = row["scenario"]
        if name not in SCENARIOS or name in seen:
            raise ValueError("Unexpected or duplicate native scenario")
        seen.add(name)
        if (row.get("windows_architecture") != "x64" or
                not isinstance(row.get("windows_build"), str) or
                not re.fullmatch(r"\d{4,6}(?:\.\d+)?", row["windows_build"]) or
                row.get("standard_user") is not True or
                row.get("network_disabled_during_install_and_first_launch") is not True or
                row.get("fixture_reset_before_install") is not True):
            raise ValueError("Incomplete native environment evidence: " + name)
        if name == "clean-standard-user" and row.get("python_qt_preinstalled") is not False:
            raise ValueError("Clean scenario must have no Python/Qt prerequisites")
        if name == "pre-equipped-standard-user" and row.get("python_qt_preinstalled") is not True:
            raise ValueError("Pre-equipped scenario must exercise existing prerequisites")
        checks = row["checks"]
        if set(checks) != set(CHECKS) or any(value != "PASS" for value in checks.values()):
            raise ValueError("Missing or failed native checks: " + name)
        if not isinstance(row.get("notes"), str) or not row["notes"].strip():
            raise ValueError("Record actual observations, not just checkboxes")
        evidence = row.get("evidence_sha256")
        if not isinstance(evidence, dict) or not evidence or any(
                not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", key)
                or not isinstance(value, str) or not re.fullmatch(r"[a-f0-9]{64}", value)
                for key, value in evidence.items()):
            raise ValueError("Missing native observation evidence hashes")
    if seen != set(SCENARIOS):
        raise ValueError("Missing native machine scenario")
    return {"kind": "native-observation-structure-check", "source_sha": source,
            "setup_sha256": assets[0]["sha256"], "scenarios": len(seen),
            "checks": len(seen) * len(CHECKS), "human_review_required": True,
            "public_release_approved": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("setup", type=Path)
    parser.add_argument("observations", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    record = json.loads(args.observations.read_text(encoding="utf-8-sig"))
    result = validate(manifest, record)
    with args.setup.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != result["setup_sha256"]:
            raise ValueError("Setup bytes differ from recorded candidate")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
