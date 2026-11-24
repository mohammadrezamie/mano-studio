# Mano curriculum coverage ledger — issue #13

Provisional chapter sequence: M. Morris Mano, Computer System Architecture, 3rd edition (1993). Bibliographic chapter overview: https://library.nu.edu.eg/cgi-bin/koha/opac-detail.pl?biblionumber=904 ; detailed chapter topics cross-checked against public table-of-contents information: https://www.academia.edu/38425107/Computer_system_architecture_mano . Instructor edition and exercise-specific notation still require confirmation. This is an original implementation checklist, not reproduced textbook content or a claim that every item is already catalogued.

For each component/algorithm record: mathematical model, valid inputs and domain, reference-based symbol or appropriate educational diagram, actual simulation, bilingual explanation, expected-output tests, limitations, and visual verification. A checkmark in one column never implies overall completion. Model ideal functional devices unless a real datasheet and full pinout are explicitly modeled. No decorative simulations.

| Chapter | Implemented or partial | Remaining major families |
|---|---|---|
| 1 Digital logic | Gates, adders, subtractor, ideal flip-flops | Boolean expression/minimization, K-map, sequential state synthesis |
| 2 Digital components | Decoder, encoder, MUX, DEMUX, register and counter | Expanded/selectable/active-low variants, shift/load registers, memory chips, physical device distinctions |
| 3 Data representation | Four bases, signed/unsigned words, two's complement | Other complements, BCD, Gray, ASCII, error-detecting codes, fixed/floating-point |
| 4 Register transfer and microoperations | Canonical RTL, arithmetic/logic/shifts, shared ALU | Controlled transfers, bus selection, tri-state behavior, memory transfer, combined arithmetic-logic-shift circuit |
| 5 Basic computer design | Instruction-level CPU, register/memory state, interrupts | Timing signals, microcycle control and common bus, exact control logic |
| 6 Programming | Two-pass assembler, debugger, examples | Broader worked-program exercises, subroutines, I/O, arithmetic routines |
| 7 Microprogrammed control | Not implemented | Control memory, microinstruction formats, sequencer |
| 8 CPU | Basic Computer only | General register organization, stack, addressing modes, instruction formats, RISC/CISC |
| 9 Pipeline and vector | Not implemented | Pipeline timing/hazards, vector and matrix processing |
| 10 Computer arithmetic | Fixed-width addition/subtraction/shift | Booth, multiplication/division, floating-point, decimal arithmetic |
| 11 I/O organization | Basic Computer flags/interrupt | Handshaking, priority, DMA, FIFO, serial transfer |
| 12 Memory organization | Basic Computer 4096-word memory | RAM/ROM mapping, cache, associative and virtual memory |
| 13 Multiprocessors | Not implemented | Interconnect, arbitration, synchronization, coherence |

## Delivery boundary
Full-book coverage is a long-term product goal, not a prerequisite for the next classroom Windows candidate. Prioritize a working offline translator and coherent Windows UX. New models must use existing lab surfaces and shared engines. No new public release or platform packages.

## Combinational increment
23 presets total (previous 15 plus eight): enabled 3-to-8 active-high decoder, enabled 2-to-4 active-low NAND decoder, 4-to-1 mux, 4-to-2 priority encoder, 2/4-bit unsigned comparators, full subtractor, 4-bit parity detector. All implemented as actual gate netlists; shared truth table, circuit editor, rendering and export work without duplicate simulators. Generated local Boolean equations from netlist (not minimized expressions); same selected circuit, separate results tab. Independent expected-value tests enumerate each truth table. Visual and exact-head CI pending.

## Sequential increment
11 clocked presets total: existing D/JK/T/SR, register and count plus serial shift, universal shift, synchronous clear/load up/down, ring and Johnson. Single pure transition(kind,q,p) computes preview and actual edge state; generated state preview uses same function. Ring reset seeds 0001; Johnson reset zero. Universal mode 00 hold, 01 numeric right (SR→Q3), 10 left (SL→Q0), 11 parallel load. Counter CLR > LOAD > EN, UP selects direction. Functional educational abstractions, not specific commercial packages (reference https://www.nexperia.com/products/analog-logic-ics/logic/flip-flops-latches-registers-counters-dividers/shift-registers/series/74HC194.html and https://www.allaboutcircuits.com/textbook/digital/chpt-12/ring-counters/). Mathematical equations, next-state preview and expanded pin layout/waveform in existing tab. Exhaustive transitions and GUI regression authored; CI pending. Arbitrary sequential circuits and memory chips remain open.

## Memory and representation increment
Logic Lab Memory devices: ideal RAM and ROM, 16×4, 16×8 and 256×8, explicit active-low CS/OE/WE and Z when output disabled; writes require an explicit cycle. ROM fixed demonstration pattern, no write pin. Separate input/output buses and functional rectangular drawing, not a commercial pinout or electrical timing model. Computer Data codes tab: 8421 BCD, reflected binary Gray code, 7-bit ASCII, even-parity Hamming(7,4) with single-error correction and clear multi-error caveat. Pure engines independent of GUI, exhaustive control/round-trip/error tests and GUI regression authored. References: https://www.allaboutcircuits.com/textbook/digital/chpt-15/digital-memory-terms-concepts/ and https://www.allaboutcircuits.com/textbook/digital/chpt-8/dont-care-cells-karnaugh-map/. Current CI/visual review pending. Cache, memory mapping, floating-point and SECDED remain future.

## Memory expansion and bus transfer
Added ideal word-addressed MemoryArray composed of actual MemoryChip instances, 1/2/4 banks and 1/2/4 parallel chips, 16/256 words per chip and 4/8 bits per chip. Upper address selects bank, lower selects local word; parallel lane 0 is LSB. Interactive bank table, active-low chip selects, enabled read/write and exact slices. Added three-register tri-state bus (4/8/16 bits), explicit Z and per-bit X, one-driver synchronous transfer with simultaneous load; multiple drivers blocked even if words agree. Source references: https://open-book-project.github.io/courses/csa_course/registers-shift-registers-and-memory.html and https://digisim.io/docs/tri-state-buffer. These are ideal models, not electrical timing or complete Mano common bus. Tests authored; native visual acceptance and exact-head CI pending.

## Basic Computer timing increment
Recorded actual T0–T6 timing groups in single CPU engine for 25 named instructions (32 forms), with before/after state, memory accesses and selectable bilingual inspection; interrupt service boundary approximation preserved. Not a live clock-level emulator: SC/R/control bus signals and arbitrary combined bits remain unmodeled. Independent tests for actual snapshot chains, ISZ, BSA wrap, interrupt and reversal. Reference https://open-book-project.github.io/courses/csa_course/timing-control-and-the-instruction-cycle.html . CI/visual verification pending.

## Live timing-group increment
Single resumable CPU implementation now executes one actual timing group or entire instruction. Real partial register and memory states, previous timing via bounded deterministic replay, boundary breakpoint and I/O guards. R/SC and physical bus timing remain open; no certified hardware equivalence. Regression cases cover each named form, partial finish, interrupt and rollback. New CI and native visual acceptance pending.


## Chapter 10: register arithmetic algorithms
Added signed radix-2 Booth multiplication and unsigned restoring division to the existing Data & ALU inspector (4/8/12/16-bit operands). Pure `arithmetic_algorithms.py` models actual register transitions; Booth uses n+1 accumulator bits to handle the most negative signed input, n iterations, 2n-bit result. Division displays shift, trial subtraction, restore decision, remainder and quotient; zero divisor is rejected. Existing ALU and CPU instruction semantics unchanged; these are educational algorithms, not Mano ISA opcodes. References: https://csg.csail.mit.edu/6.175/archive/2016/labs/lab2-multipliers.html and https://ebooks.inflibnet.ac.in/csp2/chapter/81/ . Authored exhaustive 4/8-bit tests, 12/16-bit boundaries and invalid inputs. Exact-head CI and native UI review pending. Signed division, non-restoring division, floating point and decimal arithmetic remain open. No installer or release work.


## Extended division algorithms
Added non-restoring unsigned division (old remainder sign selects addition/subtraction, new sign yields quotient bit; one final correction when negative) and signed restoring division (two's complement input, magnitude trace, quotient truncates toward zero, remainder follows dividend sign, explicit MIN/-1 overflow). Both reuse Data & ALU; no new ISA instructions, no CPU or academic translator changes. Reference: https://eclipse.umbc.edu/robucci/cmpeRSD/Lectures/Lecture18__Iterative_Implementations_of_Elementary_Arithmetic_Functions/ and https://ic.unicamp.br/en/~rodolfo/Cursos/mc732/2026s2/slides/C03-arithmetic/ . Exhaustive 4/8-bit cases, 12/16-bit boundaries, input guards and GUI integration regression authored; exact-head CI pending. Intermediate signed magnitude is displayed as a trace, not a physical hardware implementation. Decimal arithmetic, floating-point and SC/R remain open. No release or installer work.


## Decimal arithmetic checkpoint
Packed 8421 BCD ADD/SUB for 1–4 digits in existing Data & ALU. Input base represents the raw word (HEX recommended: 0099 encodes decimal 99). Shared data_codes.bcd_decode rejects invalid nibbles. Per-digit binary sum, +6 correction, decimal carry, nine's complement plus initial one for subtraction and explicit borrow; output wraps modulo 10^digits. No signed-decimal or fractional BCD claim. Exhaustive 1/2-digit independent expected-value tests, long carry/borrow chains, invalid input and GUI regression authored. Previous Booth/restoring arithmetic head 427a481 verified successful Actions run 45445236390; extended division and decimal exact-head CI pending. Next: floating-point representation and control timing. Academic translator unchanged, no installer or release.


## Floating-point checkpoint
Added IEEE binary16 decode and four arithmetic operations to Data & ALU: raw 16-bit fields, exact rational finite intermediates, nearest-even rounding with explicit scaling quantum/truncated/discarded/rounded significand, signed zero, subnormal, infinity and canonical quiet NaN. Width locks to 16 only in this mode. Modern IEEE format is a teaching extension, not historical Mano floating-point format or Basic Computer instructions; NaN payload/signaling and full exception flags are not modeled. Reference: IEEE 754-2019, https://doi.org/10.1145/3585515 . Authored exhaustive 65,536 encoding classification/finite round-trip tests against Python struct, deterministic finite-operation samples, tie/boundary cases, special values and GUI regression. Exact-head CI pending. Earlier Booth/restoring head 427a481 green; division/BCD results pending at inspection. Next: SC/R timing and historical floating-point algorithms. Translator unchanged; no release or installer.
