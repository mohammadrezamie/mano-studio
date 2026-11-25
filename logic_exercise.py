"""Portable, strict, bounded exercise files for the two Chapter 1 design tools.

No Qt, execution of user code, or dependency on the academic translator.
Derived equations and simulation traces are deliberately not persisted.
"""
from dataclasses import dataclass
import json
import os
from pathlib import Path
import tempfile

from boolean_minimizer import minimize
from state_synthesis import design_state_machine

MAX_BYTES = 32768
FORMAT = 'mano-exercise'
VERSION = 1


@dataclass(frozen=True)
class KarnaughExercise:
    values: tuple
    form: str = 'SOP'

    def __post_init__(self):
        object.__setattr__(self, 'values', tuple(self.values))
        minimize(self.values, self.form)


@dataclass(frozen=True)
class StateExercise:
    bits: int
    mode: str
    flipflop: str
    table: tuple

    def __post_init__(self):
        object.__setattr__(self, 'table', tuple(tuple(row) for row in self.table))
        design_state_machine(self.bits, self.table, self.mode, self.flipflop)


def dumps(exercise):
    obj = {'format': FORMAT, 'version': VERSION}
    if isinstance(exercise, KarnaughExercise):
        obj.update(kind='karnaugh', values=exercise.values, form=exercise.form)
    elif isinstance(exercise, StateExercise):
        obj.update(kind='state-design', bits=exercise.bits, mode=exercise.mode,
                   flipflop=exercise.flipflop, table=exercise.table)
    else:
        raise ValueError('Unknown exercise type')
    return json.dumps(obj, ensure_ascii=False, indent=2)+'\n'


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


def loads(text, expected_kind=None):
    """Parse a versioned file and validate the complete model before returning."""
    try:
        if not isinstance(text, str) or len(text.encode('utf-8')) > MAX_BYTES:
            raise ValueError('Exercise file too large or invalid')
        obj = json.loads(text, object_pairs_hook=_unique_object)
        if (not isinstance(obj, dict) or obj.get('format') != FORMAT or
                type(obj.get('version')) is not int or obj['version'] != VERSION):
            raise ValueError('Unsupported exercise format or version')
        kind = obj['kind']
        if expected_kind is not None and kind != expected_kind:
            raise ValueError('Wrong exercise type')
        common = {'format', 'version', 'kind'}
        if kind == 'karnaugh' and set(obj) == common | {'values', 'form'}:
            if not isinstance(obj['values'], list):
                raise ValueError('Expected value array')
            return KarnaughExercise(tuple(obj['values']), obj['form'])
        if kind == 'state-design' and set(obj) == common | {'bits', 'mode', 'flipflop', 'table'}:
            if not isinstance(obj['table'], list) or not all(isinstance(row, list) for row in obj['table']):
                raise ValueError('Expected transition rows')
            return StateExercise(obj['bits'], obj['mode'], obj['flipflop'], tuple(map(tuple, obj['table'])))
        raise ValueError('Unknown exercise fields or kind')
    except (KeyError, TypeError, UnicodeError, RecursionError, ValueError) as exc:
        raise ValueError('Invalid exercise file: '+str(exc)) from exc


def read_exercise(path, expected_kind=None):
    with Path(path).open('rb') as stream:
        data = stream.read(MAX_BYTES+1)
    if len(data) > MAX_BYTES:
        raise ValueError('Exercise file too large')
    return loads(data.decode('utf-8-sig'), expected_kind)


def write_exercise(path, exercise):
    """Replace only after the complete UTF-8 document was successfully written."""
    path = Path(path)
    data = dumps(exercise).encode('utf-8')
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', dir=path.parent, prefix='.'+path.name+'.',
                                         suffix='.tmp', delete=False) as stream:
            temp = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)
