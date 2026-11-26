"""Bounded UTF-8 reads for saved circuit documents."""
from pathlib import Path

MAX_BYTES = 200_000


def read_text(path):
    """Read at most MAX_BYTES + 1 bytes; reject oversized or invalid UTF-8."""
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("Circuit file too large.")
    return raw.decode("utf-8")
