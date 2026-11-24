# Assembly and live program laboratory
Development preview — not a release or clock-accurate simulator.

The original assignment remains RTL-to-ASM, using standalone rtl_translator.py. The optional Program Lab uses assembler.py (two-pass labels, ORG, END, DEC, HEX, 25 named instructions, direct/indirect memory operands) and simulator.py (pure Python instruction-level CPU). mano_isa.py centralizes machine encodings. No network or external service.

The assembler uses 12-bit hexadecimal addresses, case-insensitive labels, comma or colon label notation, and reports line-numbered errors. Labels take precedence over hexadecimal literals of the same spelling. DEC accepts -32768 through 65535; HEX accepts 1–4 hexadecimal digits. END is optional; content after END is rejected. Entry is the first instruction, not first data word. Sparse memory images are zero-filled. Only the 25 named instructions are supported, not arbitrary combined register-reference bits.

CPU state includes 4096 16-bit memory words, AC, E, PC, AR, DR, IR, TR and I/O flags/registers. Execution emits StepEvent with before/after registers, effective address and memory writes. Interrupts are approximated at instruction boundaries; this is not the exact hardware timing sequence. INP/OUT use explicit input and output controls. Unsupported opcodes stop execution with an error. The UI limits continuous execution to 10000 steps per loaded program.

Program Lab opens valid translated RTL in an editable ASM panel. Load example supplies data and labels. Machine listing, step/run/pause, speed and changed register highlighting are connected to actual CPU state. The Computer workspace now integrates the live datapath, register/memory inspector, example and custom programs using one CPU and StepEvent. Former fixed demonstration retired. The view shows instruction-level activity, not hardware timing. Next: improve register/memory navigation, bilingual explanations, breakpoints, history, and source mapping. Keep these independent from the assignment translator.

Reference: Morris Mano, Computer System Architecture, 3rd ed., chapters 5–6, table 5-2. Encoding cross-check: https://open-book-project.github.io/courses/csa_course/the-basic-computer-registers-bus-and-instruction-codes.html . Instructor-specific RTL syntax remains to be confirmed.

## Integrated debugger and arithmetic workbench
Computer contains Debugger and Data & ALU tabs. Breakpoints stop continuous execution at pre-step PC; manual Step ignores breakpoints, Run resumes once past a hit. Reverse step restores registers and memory-write deltas, up to 512 recorded instructions. Successful external input/output clears reversible history, without resetting step count. Trace selection links to original ASM source line, CSV exports retained entries. ALU supports 4/8/12/16-bit input, BIN/OCT/DEC/HEX, signed/unsigned interpretation, arithmetic/logic/shifts/rotations and ripple carry stages; optional AC/DR/E snapshot. Teaching C/V/N/Z are not extra Mano hardware registers; E retains exact prior semantics. No timing-level CPU claims. Invalid RTL does not prevent opening independent Computer tools. Regression tests authored; runtime confirmation pending.

Number bases & ALU is directly accessible from Labs and opens the existing Computer inspector with Convert bases selected. Conversion-only mode shows one word in binary/octal/hex/unsigned and signed decimal; no arithmetic operation required. Fixed widths 4/8/12/16, base changes preserve valid values. The ALU still defaults to ADD when opened normally.

## Data codes
Existing Computer inspector now includes BCD/Gray/ASCII/Hamming conversion. Strict input domains, invalid results cleared, leading zeros preserved where applicable, even parity Hamming(7,4) single-bit correction only (not SECDED). No modifications to CPU, translator, or ALU semantics.
