# Assembly and live program laboratory
Development preview — not a release or clock-accurate simulator.

The original assignment remains RTL-to-ASM, using standalone rtl_translator.py. The optional Program Lab uses assembler.py (two-pass labels, ORG, END, DEC, HEX, 25 named instructions, direct/indirect memory operands) and simulator.py (pure Python instruction-level CPU). mano_isa.py centralizes machine encodings. No network or external service.

The assembler uses 12-bit hexadecimal addresses, case-insensitive labels, comma or colon label notation, and reports line-numbered errors. Labels take precedence over hexadecimal literals of the same spelling. DEC accepts -32768 through 65535; HEX accepts 1–4 hexadecimal digits. END is optional; content after END is rejected. Entry is the first instruction, not first data word. Sparse memory images are zero-filled. Only the 25 named instructions are supported, not arbitrary combined register-reference bits.

CPU state includes 4096 16-bit memory words, AC, E, PC, AR, DR, IR, TR and I/O flags/registers. Execution emits StepEvent with before/after registers, effective address and memory writes. Interrupts are approximated at instruction boundaries; this is not the exact hardware timing sequence. INP/OUT use explicit input and output controls. Unsupported opcodes stop execution with an error. The UI limits continuous execution to 10000 steps per loaded program.

Program Lab opens valid translated RTL in an editable ASM panel. Load example supplies data and labels. Machine listing, step/run/pause, speed and changed register highlighting are connected to actual CPU state. The existing animated four-instruction Live Lab is a separate simplified educational demo. Next: connect event-driven graphical datapath to arbitrary programs; improve register/memory navigation, bilingual explanations, breakpoints, history, and source mapping. Keep these independent from the assignment translator.

Reference: Morris Mano, Computer System Architecture, 3rd ed., chapters 5–6, table 5-2. Encoding cross-check: https://open-book-project.github.io/courses/csa_course/the-basic-computer-registers-bus-and-instruction-codes.html . Instructor-specific RTL syntax remains to be confirmed.
