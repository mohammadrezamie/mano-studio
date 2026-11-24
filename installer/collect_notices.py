"""Preserve third-party package notices available in build environment."""
from importlib.metadata import distributions
from pathlib import Path
import sys


def main():
    target = Path(sys.argv[1])
    for dist in distributions():
        name = dist.metadata.get("Name", "")
        if not name.lower().startswith(("pyside6", "shiboken6", "pyinstaller")):
            continue
        folder = target / name
        folder.mkdir(exist_ok=True)
        (folder / "METADATA.txt").write_text(str(dist.metadata), encoding="utf-8")
        for file in dist.files or ():
            if ".dist-info" in str(file) and any(word in file.name.lower() for word in ("license", "copying", "notice")):
                path = Path(dist.locate_file(file))
                if path.is_file():
                    (folder / file.name).write_bytes(path.read_bytes())


if __name__ == "__main__":
    main()
