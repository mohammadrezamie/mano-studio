"""Prune the unused Qt QML/Quick runtime from this Widgets-only application.

The import scan is conservative but cannot detect every dynamic load. Frozen
smoke, full regression, native Windows acceptance and security review remain
mandatory before promotion.
"""
import argparse
import hashlib
import json
from pathlib import Path

TARGETS = frozenset({
    "_internal/PySide6/Qt6Qml.dll",
    "_internal/PySide6/Qt6QmlMeta.dll",
    "_internal/PySide6/Qt6QmlModels.dll",
    "_internal/PySide6/Qt6QmlWorkerScript.dll",
    "_internal/PySide6/Qt6Quick.dll",
})
TARGET_NAMES = frozenset(Path(p).name.lower() for p in TARGETS)


def plan(root, imports):
    root = Path(root)
    if not (root / "ManoStudio.exe").is_file():
        raise ValueError("Not a frozen Mano Studio application")
    files = {p.relative_to(root).as_posix(): p for p in root.rglob("*") if p.is_file()}
    candidates = {name for name, path in files.items() if path.name.lower() in TARGET_NAMES}
    if candidates != TARGETS:
        raise ValueError("Expected exact five-library Qt QML/Quick group; inspect changed payload")
    unexpected = [
        name for name, path in files.items()
        if path.suffix.lower() in {".dll", ".pyd"}
        and any(token in path.name.lower() for token in ("qml", "quick"))
        and path.name.lower() not in TARGET_NAMES
    ]
    if unexpected:
        raise ValueError("Unexpected QML/Quick binary payload: " + ", ".join(sorted(unexpected)))
    for relative, path in sorted(files.items()):
        if relative in TARGETS or path.suffix.lower() not in {".exe", ".dll", ".pyd"}:
            continue
        dependencies = {str(value).lower() for value in imports(path)}
        if TARGET_NAMES.intersection(dependencies):
            raise ValueError("Retained binary imports Qt QML/Quick: " + relative)
    rows = []
    for relative in sorted(TARGETS):
        path = files[relative]
        data = path.read_bytes()
        rows.append({"path": relative, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    return {
        "kind": "qt-qml-quick-prune-evidence",
        "targets": rows,
        "removed_bytes": sum(row["size"] for row in rows),
        "static_inbound_imports": 0,
        "dynamic_loading_proven_absent": False,
        "full_feature_regression_required": True,
        "native_acceptance_required": True,
        "security_approved": False,
        "public_release_approved": False,
    }


def apply(root, imports):
    root = Path(root)
    report = plan(root, imports)
    for row in report["targets"]:
        (root / row["path"]).unlink()
    (root / "qt-qml-prune-evidence.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main():
    from installer.prune_qt import pe_imports
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(json.dumps(apply(args.root, pe_imports), indent=2))


if __name__ == "__main__":
    main()
