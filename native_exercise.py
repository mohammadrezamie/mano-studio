"""Native .mano adapter for validated legacy design exercises.

Only the editable design is persisted. Derived equations and transient
simulation traces are regenerated/reset by the existing teaching models.
"""
import json
from pathlib import Path
import mano_file
from logic_exercise import dumps, loads, read_exercise, write_exercise

KINDS = ("karnaugh", "state-design")


def restore(kind, payload):
    if kind not in KINDS or not isinstance(payload, dict):
        raise ValueError("Expected a native design exercise")
    if set(payload) & {"format", "version", "kind"}:
        raise ValueError("Reserved exercise field")
    return loads(json.dumps({"format": "mano-exercise", "version": 1,
                             "kind": kind, **payload}, allow_nan=False), kind)


def load(path, expected_kind=None):
    if Path(path).suffix.lower() != mano_file.SUFFIX:
        return read_exercise(path, expected_kind)
    kind, payload = mano_file.load(path)
    if expected_kind is not None and kind != expected_kind:
        raise ValueError("Wrong exercise type")
    return restore(kind, payload)


def save(path, exercise):
    if Path(path).suffix.lower() != mano_file.SUFFIX:
        return write_exercise(path, exercise)
    obj = json.loads(dumps(exercise))
    kind = obj.pop("kind")
    obj.pop("format")
    obj.pop("version")
    restore(kind, obj)
    mano_file.save(path, kind, obj)
