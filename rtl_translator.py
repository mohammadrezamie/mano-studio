"""Translate Mano instruction-level RTL shorthand into assembly (no GUI)."""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Instruction:
    line: int
    assembly: str


@dataclass(frozen=True)
class Diagnostic:
    line: int
    column: int
    code: str
    message: str


@dataclass(frozen=True)
class TranslationResult:
    instructions: tuple[Instruction, ...]
    diagnostics: tuple[Diagnostic, ...]

    @property
    def ok(self) -> bool:
        return not self.diagnostics

    @property
    def assembly(self) -> str:
        # Never export a partially translated program.
        if not self.ok:
            raise ValueError("Translation contains errors")
        return "\n".join(i.assembly for i in self.instructions)


# Match full statements, with whitespace only between tokens.
ASSIGN = r"\s*(?:←|<-|=)\s*"
ADDRESS = r"(?P<address>[0-9A-F]+)"
REPEAT = r"(?P=address)"
PLUS = r"\s*\+\s*"
COMMA = r"\s*,\s*"


def mem(address):
    return r"M\s*\[\s*" + address + r"\s*\]"


def skip(condition):
    return r"IF\s+" + condition + r"\s+THEN\s+PC" + ASSIGN + r"PC" + PLUS + "1"


def memory_rules(indirect):
    target = mem(ADDRESS) if indirect else ADDRESS
    repeated = mem(REPEAT) if indirect else REPEAT
    word = mem(target)
    same_word = mem(repeated)
    return [
        (r"AC" + ASSIGN + word, "LDA"),
        (r"AC" + ASSIGN + r"AC" + PLUS + word, "ADD"),
        (word + ASSIGN + r"AC", "STA"),
        (r"AC" + ASSIGN + r"AC\s*(?:∧|&)\s*" + word, "AND"),
        (r"PC" + ASSIGN + target, "BUN"),
        (word + ASSIGN + "PC" + COMMA + "PC" + ASSIGN + repeated + PLUS + "1", "BSA"),
        (word + ASSIGN + same_word + PLUS + "1" + COMMA + skip(same_word + r"\s*=\s*0"), "ISZ"),
    ]


# The catalog includes all 25 named instructions. Compound statements are
# instruction-level shorthand, not independently scheduled microoperations.
FIXED_RULES = [
    (r"AC" + ASSIGN + "0", "CLA"),
    (r"E" + ASSIGN + "0", "CLE"),
    (r"AC" + ASSIGN + r"(?:¬|~)\s*AC", "CMA"),
    (r"E" + ASSIGN + r"(?:¬|~)\s*E", "CME"),
    (r"E\s*:\s*AC" + ASSIGN + r"CIR\s*\(\s*E\s*:\s*AC\s*\)", "CIR"),
    (r"E\s*:\s*AC" + ASSIGN + r"CIL\s*\(\s*E\s*:\s*AC\s*\)", "CIL"),
    (r"AC" + ASSIGN + "AC" + PLUS + "1", "INC"),
    (skip(r"AC\s*\[\s*15\s*\]\s*=\s*0"), "SPA"),
    (skip(r"AC\s*\[\s*15\s*\]\s*=\s*1"), "SNA"),
    (skip(r"AC\s*=\s*0"), "SZA"),
    (skip(r"E\s*=\s*0"), "SZE"),
    (r"S" + ASSIGN + "0", "HLT"),
    (r"AC\s*\[\s*7\s*:\s*0\s*\]" + ASSIGN + "INPR" + COMMA + "FGI" + ASSIGN + "0", "INP"),
    (r"OUTR" + ASSIGN + r"AC\s*\[\s*7\s*:\s*0\s*\]" + COMMA + "FGO" + ASSIGN + "0", "OUT"),
    (skip(r"FGI\s*=\s*1"), "SKI"),
    (skip(r"FGO\s*=\s*1"), "SKO"),
    (r"IEN" + ASSIGN + "1", "ION"),
    (r"IEN" + ASSIGN + "0", "IOF"),
]
RULES = tuple(
    (re.compile(pattern, re.IGNORECASE | re.ASCII), mnemonic, indirect)
    for indirect, entries in [(False, memory_rules(False)),
                              (True, memory_rules(True)),
                              (False, FIXED_RULES)]
    for pattern, mnemonic in entries
)

def translate(text: str) -> TranslationResult:
    """Translate each non-comment line, preserving its original line number."""
    instructions, diagnostics = [], []
    for number, raw in enumerate(text.splitlines(), 1):
        statement = re.split(r"[#;]", raw, maxsplit=1)[0]
        offset = len(statement) - len(statement.lstrip())
        statement = statement.strip()
        if not statement:
            continue
        for pattern, mnemonic, indirect in RULES:
            match = pattern.fullmatch(statement)
            if match is None:
                continue
            address = match.groupdict().get("address")
            if address is None:
                instructions.append(Instruction(number, mnemonic))
            elif len(address) > 3:
                diagnostics.append(Diagnostic(number, offset + match.start("address") + 1,
                    "ADDRESS_RANGE", "Expected a hexadecimal address (000–FFF)."))
            else:
                suffix = " I" if indirect else ""
                instructions.append(Instruction(number, f"{mnemonic} {address.upper().zfill(3)}{suffix}"))
            break
        else:
            diagnostics.append(Diagnostic(number, offset + 1, "UNSUPPORTED_RTL",
                "Unsupported RTL or invalid syntax; expected e.g. AC <- M[100]."))
    return TranslationResult(tuple(instructions), tuple(diagnostics))


def main() -> int:
    """Command line: python rtl_translator.py input.rtl -o output.asm."""
    import argparse
    from pathlib import Path
    import sys

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.input.resolve() == args.output.resolve():
            raise ValueError("Input and output must be different files")
        result = translate(args.input.read_text(encoding="utf-8-sig"))
        if not result.ok:
            for error in result.diagnostics:
                print(f"{error.line}:{error.column}: {error.code}: {error.message}", file=sys.stderr)
            return 1
        args.output.write_text(result.assembly + ("\n" if result.instructions else ""), encoding="utf-8")
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
