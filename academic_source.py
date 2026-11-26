"""Locate and export the original standalone Python translator, never run it."""
import os
from pathlib import Path
import sys
import tempfile


def source_path():
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / "rtl_translator.py"


def read_source():
    return source_path().read_bytes()


def export_source(destination, *, data=None):
    """Atomically save exact bytes; do not overwrite the application's source."""
    path = Path(destination)
    original = source_path()
    if path.suffix.lower() != ".py":
        raise ValueError("Expected a Python source filename")
    if path.resolve() == original.resolve() or (path.exists() and original.exists() and path.samefile(original)):
        raise ValueError("Choose a destination outside the original source file")
    raw = read_source() if data is None else data
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temp = Path(stream.name)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)
    return path
