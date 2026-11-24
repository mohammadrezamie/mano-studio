"""Canonical RTL templates for GUI and instruction reference (no Qt)."""

TEMPLATES = {
    "AND": "AC ← AC ∧ M[{a}]",
    "ADD": "AC ← AC + M[{a}]",
    "LDA": "AC ← M[{a}]",
    "STA": "M[{a}] ← AC",
    "BUN": "PC ← {a}",
    "BSA": "M[{a}] ← PC, PC ← {a} + 1",
    "ISZ": "M[{a}] ← M[{a}] + 1, IF M[{a}] = 0 THEN PC ← PC + 1",
    "CLA": "AC ← 0",
    "CLE": "E ← 0",
    "CMA": "AC ← ¬AC",
    "CME": "E ← ¬E",
    "CIR": "E:AC ← CIR(E:AC)",
    "CIL": "E:AC ← CIL(E:AC)",
    "INC": "AC ← AC + 1",
    "SPA": "IF AC[15] = 0 THEN PC ← PC + 1",
    "SNA": "IF AC[15] = 1 THEN PC ← PC + 1",
    "SZA": "IF AC = 0 THEN PC ← PC + 1",
    "SZE": "IF E = 0 THEN PC ← PC + 1",
    "HLT": "S ← 0",
    "INP": "AC[7:0] ← INPR, FGI ← 0",
    "OUT": "OUTR ← AC[7:0], FGO ← 0",
    "SKI": "IF FGI = 1 THEN PC ← PC + 1",
    "SKO": "IF FGO = 1 THEN PC ← PC + 1",
    "ION": "IEN ← 1",
    "IOF": "IEN ← 0",
}


def build_rtl(mnemonic: str, address: str = "", indirect: bool = False) -> str:
    """Render a template; translator remains the authority on syntax."""
    import re
    template = TEMPLATES[mnemonic.upper()]
    if "{a}" not in template:
        if address or indirect:
            raise ValueError("This instruction takes no address")
        return template
    if not re.fullmatch(r"[0-9a-fA-F]{1,3}", address):
        raise ValueError("Expected hexadecimal address 000–FFF")
    address = address.upper().zfill(3)
    return template.format(a=f"M[{address}]" if indirect else address)
