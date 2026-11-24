"""Optional canonical reverse translation; never part of academic RTL core.

A deliberately restricted import: named instructions with literal hexadecimal
addresses, no labels, data or origin directives. Reconstruction cannot preserve
original RTL formatting or arbitrary microoperation sequences.
"""
import re
from dataclasses import dataclass
from instruction_catalog import TEMPLATES,build_rtl
from rtl_translator import translate

@dataclass(frozen=True)
class ReverseError:
    line: int
    message: str
    column: int = 1
    code: str = "UNSUPPORTED_ASM"

@dataclass(frozen=True)
class ReverseResult:
    rtl: str
    errors: tuple
    source_lines: tuple = ()

    @property
    def diagnostics(self):
        return self.errors

    @property
    def ok(self):
        return not self.errors

def reverse_translate(text):
    lines=[]
    source_lines=[]
    errors=[]
    for n,raw in enumerate(text.splitlines(),1):
        statement=re.split(r"[;#/]",raw,maxsplit=1)[0].strip()
        if not statement:
            continue
        tokens=statement.upper().split()
        mnemonic,args=tokens[0],tokens[1:]
        try:
            if mnemonic not in TEMPLATES:
                raise ValueError("Only named instructions are supported; labels and directives cannot be reconstructed.")
            memory="{a}" in TEMPLATES[mnemonic]
            if memory:
                if len(args) not in (1,2) or (len(args)==2 and args[1]!="I"):
                    raise ValueError("Expected a hexadecimal address and optional I.")
                rtl=build_rtl(mnemonic,args[0],len(args)==2)
                expected=mnemonic+" "+args[0].zfill(3)+(" I" if len(args)==2 else "")
            else:
                if args:
                    raise ValueError("This instruction takes no operands.")
                rtl=build_rtl(mnemonic)
                expected=mnemonic
            result=translate(rtl)
            if not result.ok or result.assembly!=expected:
                raise ValueError("Canonical RTL failed forward verification.")
            lines.append(rtl)
            source_lines.append(n)
        except ValueError as exc:
            errors.append(ReverseError(n,str(exc)))
    if not lines and not errors:
        errors.append(ReverseError(1,"No named instructions to import."))
    return ReverseResult("\n".join(lines)+"\n" if not errors else "",tuple(errors),tuple(source_lines) if not errors else ())
