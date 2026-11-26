"""Validated Basic Computer checkpoint at an instruction boundary.

A checkpoint stores state, not proof of how it was reached. No code is evaluated
and no execution starts on load. Reverse history begins anew after restore.
"""
from assembler import assemble
from simulator import CPU
import mano_file

WIDTHS = {"PC": 12, "AR": 12, "AC": 16, "DR": 16, "IR": 16, "TR": 16,
          "INPR": 8, "OUTR": 8, "E": 1, "FGI": 1, "FGO": 1, "IEN": 1,
          "R": 1, "I": 1, "SC": 4}


def integer(value, maximum):
    return type(value) is int and 0 <= value <= maximum


def restore(obj):
    if not isinstance(obj, dict) or set(obj) != {"source", "registers", "memory", "steps", "breakpoints"}:
        raise ValueError("Invalid CPU checkpoint fields")
    source = obj["source"]
    if not isinstance(source, str) or not source.strip() or len(source.encode("utf-8")) > 500_000:
        raise ValueError("Invalid CPU source")
    program = assemble(source)
    if not program.ok or not program.words:
        raise ValueError("Invalid checkpoint assembly")
    registers = obj["registers"]
    if not isinstance(registers, dict) or set(registers) != set(WIDTHS) | {"HALTED"}:
        raise ValueError("Invalid CPU registers")
    if (any(not integer(registers[k], (1 << w) - 1) for k, w in WIDTHS.items())
            or registers["SC"] != 0 or type(registers["HALTED"]) is not bool):
        raise ValueError("Invalid instruction-boundary registers")
    memory = obj["memory"]
    if not isinstance(memory, list) or len(memory) > 4096:
        raise ValueError("Invalid CPU memory")
    words = {}
    for row in memory:
        if (not isinstance(row, list) or len(row) != 2 or not integer(row[0], 4095)
                or not integer(row[1], 65535) or row[1] == 0 or row[0] in words):
            raise ValueError("Invalid or duplicate sparse memory word")
        words[row[0]] = row[1]
    steps, breaks = obj["steps"], obj["breakpoints"]
    if not integer(steps, 10000) or not isinstance(breaks, list) or len(breaks) > 4096:
        raise ValueError("Invalid CPU debugger state")
    if any(not integer(x, 4095) for x in breaks) or len(set(breaks)) != len(breaks):
        raise ValueError("Invalid breakpoint")
    cpu = CPU(words, program.entry)
    for key, value in registers.items():
        setattr(cpu, key.lower(), value)
    return source, program, cpu, steps, set(breaks)


def snapshot(source, cpu, steps, breakpoints):
    if cpu.in_progress:
        raise ValueError("Finish or rewind the current instruction before saving")
    obj = {"source": source, "registers": cpu.registers(),
           "memory": [[a, w] for a, w in enumerate(cpu.memory) if w],
           "steps": steps, "breakpoints": sorted(breakpoints)}
    restore(obj)
    return obj


def save(path, source, cpu, steps, breakpoints):
    mano_file.save(path, "cpu-run", snapshot(source, cpu, steps, breakpoints))


def load(path):
    kind, obj = mano_file.load(path)
    if kind != "cpu-run":
        raise ValueError("Expected CPU checkpoint")
    return restore(obj)
