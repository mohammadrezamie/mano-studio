"""Two-pass assembler for the documented named Mano instructions."""
from dataclasses import dataclass
import re
from mano_isa import MEMORY, FIXED


@dataclass(frozen=True)
class AssemblyError:
    line: int
    message: str


@dataclass
class AssemblyResult:
    words: dict
    symbols: dict
    source_lines: dict
    entry: int
    errors: tuple

    @property
    def ok(self):
        return not self.errors

    def listing(self):
        if not self.ok:
            raise ValueError("Assembly contains errors")
        return "\n".join(f"{a:03X}: {w:04X}" for a, w in sorted(self.words.items()))


def assemble(text):
    """Labels use NAME, or NAME:; address literals are hexadecimal."""
    symbols, records, words, source_lines, errors = {}, [], {}, {}, []
    location = 0
    entry = None
    ended = False
    allocated = set()
    def fail(line, message):
        errors.append(AssemblyError(line, message))
    for line, raw in enumerate(text.splitlines(), 1):
        statement = re.split(r"[/#;]", raw, maxsplit=1)[0].strip().upper()
        if not statement:
            continue
        if ended:
            fail(line, "Content after END")
            continue
        label = re.match(r"^([A-Z][A-Z0-9_]*)\s*[:,]\s*", statement)
        if label:
            name = label[1]
            if name in symbols or name in MEMORY or name in FIXED or name in ("ORG","END","DEC","HEX"):
                fail(line, "Duplicate or reserved label: " + name)
            elif location > 0xFFF:
                fail(line, "Label outside memory")
            else:
                symbols[name] = location
            statement = statement[label.end():]
        if not statement:
            continue
        tokens = statement.split()
        op, args = tokens[0], tokens[1:]
        if op == "ORG":
            if label or len(args) != 1 or not re.fullmatch(r"[0-9A-F]{1,3}", args[0]):
                fail(line, "ORG requires an unlabeled 12-bit hexadecimal address")
            else:
                location = int(args[0], 16)
            continue
        if op == "END":
            if args or label:
                fail(line, "END takes no operands or label")
            ended = True
            continue
        if location > 0xFFF:
            fail(line, "Address outside 000–FFF")
            continue
        if location in allocated:
            fail(line, "Overlapping memory address")
        allocated.add(location)
        if entry is None and op in MEMORY.keys() | FIXED.keys():
            entry = location
        records.append((line, location, op, args))
        location += 1
    for line, address, op, args in records:
        try:
            if op in MEMORY:
                if len(args) not in (1, 2) or (len(args) == 2 and args[1] != "I"):
                    raise ValueError("Expected address or label, optionally followed by I")
                token = args[0]
                if token in symbols:
                    operand = symbols[token]
                elif re.fullmatch(r"[0-9A-F]{1,3}", token):
                    operand = int(token, 16)
                else:
                    raise ValueError("Unknown label or invalid hexadecimal address: " + token)
                value = (MEMORY[op] << 12) | operand | (0x8000 if len(args) == 2 else 0)
            elif op in FIXED:
                if args:
                    raise ValueError(op + " takes no operand")
                value = FIXED[op]
            elif op in ("DEC", "HEX"):
                pattern = r"[+-]?[0-9]+" if op == "DEC" else r"[0-9A-F]{1,4}"
                if len(args) != 1 or not re.fullmatch(pattern, args[0]):
                    raise ValueError("Invalid " + op + " constant")
                value = int(args[0], 10 if op == "DEC" else 16)
                if not -32768 <= value <= 65535:
                    raise ValueError("Constant outside 16-bit range")
                value &= 0xFFFF
            else:
                raise ValueError("Unknown instruction: " + op)
            words[address] = value
            source_lines[address] = line
        except ValueError as exc:
            fail(line, str(exc))
    if errors:
        words, source_lines = {}, {}
    return AssemblyResult(words, symbols, source_lines, entry or 0, tuple(errors))
