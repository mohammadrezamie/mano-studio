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
Later support indirect memory, labels, BSA/ISZ, register-reference and I/O instructions, ORG/END/DEC/HEX assembler directives after checking Mano semantics. Two-pass assembler resolves symbols and validates address range. Simulator must model 16-bit wrap, carry, PC, memory, halt and supported instructions; distinguish instruction-level from timing-level simulation.
Example: memory[0x100]=5, memory[0x101]=3; LDA 100, ADD 101, STA 102, HLT yields memory[0x102]=8. Program starts at 000. Tests: spacing variants, case, malformed tokens, bounds, unsupported transfers, carry and source mapping.
