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
