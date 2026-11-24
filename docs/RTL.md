# Provisional RTL dialect
RTL is register transfer notation, not a universal programming grammar. Confirm instructor examples before freezing. This is instruction-level shorthand, not arbitrary hardware microcode. Mano Basic Computer: 4096 x 16-bit words; 12-bit AR/PC, 16-bit AC/DR/IR/TR, 8-bit INPR/OUTR, E carry, SC timing counter.
One statement per line; blank lines and comments (# or ;) allowed; case insensitive keywords; whitespace between tokens optional where unambiguous; accept ←, <-, = as assignment, never strip spaces inside identifiers or numbers. UTF-8, CRLF/LF. Default addresses hexadecimal 000–FFF; reject out of range and malformed tokens. Document explicit decimal syntax if added. No eval. Use anchored token patterns, report line/column and expected syntax; no silent partial export on errors.
| RTL | ASM | HEX example |
|---|---|---|
| AC ← M[100] | LDA 100 | 2100 |
| AC ← AC + M[101] | ADD 101 | 1101 |
| M[102] ← AC | STA 102 | 3102 |
| AC ← AC ∧ M[100] | AND 100 | 0100 |
| AC ← 0 | CLA | 7800 |
| AC ← AC + 1 | INC | 7020 |
| AC ← ¬AC | CMA | 7200 |
| PC ← 100 | BUN 100 | 4100 |
| S ← 0 | HLT | 7001 |
These are semantic shorthand: ADD also changes E; LDA uses DR internally. Document side effects. Arbitrary transfers such as AR ← PC are not directly expressible as assembly; reject unless a proven equivalent sequence exists. Do not promise universal RTL translation.
The translator now recognizes all 25 named instructions. Labels and ORG/END/DEC/HEX assembler directives remain future work. Two-pass assembler resolves symbols and validates address range. Simulator must model 16-bit wrap, carry, PC, memory, halt and supported instructions; distinguish instruction-level from timing-level simulation.
Example: memory[0x100]=5, memory[0x101]=3; LDA 100, ADD 101, STA 102, HLT yields memory[0x102]=8. Program starts at 000. Tests: spacing variants, case, malformed tokens, bounds, unsupported transfers, carry and source mapping.

## Full canonical templates
| ASM | RTL example |
|---|---|
| AND | `AC ← AC ∧ M[100]` |
| ADD | `AC ← AC + M[100]` |
| LDA | `AC ← M[100]` |
| STA | `M[100] ← AC` |
| BUN | `PC ← 100` |
| BSA | `M[100] ← PC, PC ← 100 + 1` |
| ISZ | `M[100] ← M[100] + 1, IF M[100] = 0 THEN PC ← PC + 1` |
| CLA | `AC ← 0` |
| CLE | `E ← 0` |
| CMA | `AC ← ¬AC` |
| CME | `E ← ¬E` |
| CIR | `E:AC ← CIR(E:AC)` |
| CIL | `E:AC ← CIL(E:AC)` |
| INC | `AC ← AC + 1` |
| SPA | `IF AC[15] = 0 THEN PC ← PC + 1` |
| SNA | `IF AC[15] = 1 THEN PC ← PC + 1` |
| SZA | `IF AC = 0 THEN PC ← PC + 1` |
| SZE | `IF E = 0 THEN PC ← PC + 1` |
| HLT | `S ← 0` |
| INP | `AC[7:0] ← INPR, FGI ← 0` |
| OUT | `OUTR ← AC[7:0], FGO ← 0` |
| SKI | `IF FGI = 1 THEN PC ← PC + 1` |
| SKO | `IF FGO = 1 THEN PC ← PC + 1` |
| ION | `IEN ← 1` |
| IOF | `IEN ← 0` |

For all seven memory instructions, use `M[100]` in place of effective address `100` for indirect mode, e.g. `AC ← M[M[100]]` -> `LDA 100 I`. BSA/ISZ repeated address tokens must match apart from case/spacing. Effective address is latched before execution; ISZ condition is evaluated after 16-bit increment. PC denotes post-fetch PC; PC arithmetic is 12-bit, AC/memory arithmetic 16-bit. SPA includes zero. CIR/CIL rotate combined 17-bit E:AC. These are provisional instruction-level templates, not verbatim book microoperations. Unsupported syntax is rejected.
