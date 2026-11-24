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


# Match entire statements; whitespace is allowed BETWEEN tokens only.
ASSIGN = r"\s*(?:←|<-|=)\s*"
ADDRESS = r"(?P<address>[0-9A-F]+)"
MEM = r"M\s*\[\s*" + ADDRESS + r"\s*\]"
RULES = tuple((re.compile(pattern, re.IGNORECASE | re.ASCII), mnemonic) for pattern, mnemonic in [
    (r"AC" + ASSIGN + MEM, "LDA"),
    (r"AC" + ASSIGN + r"AC\s*\+\s*" + MEM, "ADD"),
    (MEM + ASSIGN + r"AC", "STA"),
    (r"AC" + ASSIGN + r"AC\s*(?:∧|&)\s*" + MEM, "AND"),
    (r"AC" + ASSIGN + r"0", "CLA"),
    (r"AC" + ASSIGN + r"AC\s*\+\s*1", "INC"),
    (r"AC" + ASSIGN + r"(?:¬|~)\s*AC", "CMA"),
    (r"PC" + ASSIGN + ADDRESS, "BUN"),
    (r"S" + ASSIGN + r"0", "HLT"),
])


def translate(text: str) -> TranslationResult:
    """Translate each non-comment line, preserving its original line number."""
    instructions, diagnostics = [], []
    for number, raw in enumerate(text.splitlines(), 1):
        statement = re.split(r"[#;]", raw, maxsplit=1)[0]
        offset = len(statement) - len(statement.lstrip())
        statement = statement.strip()
        if not statement:
            continue
        for pattern, mnemonic in RULES:
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
                instructions.append(Instruction(number, f"{mnemonic} {address.upper().zfill(3)}"))
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
