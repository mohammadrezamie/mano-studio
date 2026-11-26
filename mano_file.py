"""Versioned native Mano Studio documents, independent of UI and engine."""
import json
import os
from pathlib import Path
import tempfile

MAGIC = "mano-studio"
SUFFIX = ".mano"
MAX_BYTES = 2_000_000
KINDS = {"rtl", "asm", "circuit"}


def encode(kind, payload):
    if kind not in KINDS or (kind in ("rtl", "asm") and not isinstance(payload, str)) or (kind == "circuit" and not isinstance(payload, dict)):
        raise ValueError("Unsupported Mano document")
    text = json.dumps({"format": MAGIC, "version": 1, "kind": kind, "payload": payload},
                      ensure_ascii=False, allow_nan=False, indent=2) + "\n"
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError("Mano document too large")
    return text


def decode(text):
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError("Mano document too large")
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError("Duplicate document key")
            obj[key] = value
        return obj
    try:
        obj = json.loads(text, object_pairs_hook=unique)
        if not isinstance(obj, dict) or set(obj) != {"format", "version", "kind", "payload"} or obj["format"] != MAGIC or type(obj["version"]) is not int or obj["version"] != 1:
            raise ValueError("Unsupported Mano document format or version")
        encode(obj["kind"], obj["payload"])
        return obj["kind"], obj["payload"]
    except (TypeError, RecursionError) as exc:
        raise ValueError("Invalid Mano document") from exc


def load(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("Mano document too large")
    return decode(raw.decode("utf-8-sig"))


def save(path, kind, payload):
    """Replace only after complete encoding and same-directory staging."""
    raw = encode(kind, payload).encode("utf-8")
    path = Path(path)
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
