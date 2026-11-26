# Detailed textbook topic audit

Owner mandate: aim for every teachable concept, component, algorithm, diagram family and exercise type, not merely chapter presence. Provisional scope: M. Morris Mano, Computer System Architecture, third edition (1993). Chapter order verified against [Nile University library catalog](https://library.nu.edu.eg/cgi-bin/koha/opac-detail.pl?biblionumber=904). The [Pearson revised third edition](https://www.pearsoned.co.in/prc/book/m-morris-mano-computer-system-architecture-3e--3/9789332585607) is a different edition and must not silently redefine the assignment. The instructor's exact edition is unconfirmed. This is an original topic-family audit, not a transcription of the book, not yet a page-by-page reconciliation, and not a guarantee that no topic is missing.

## Acceptance contract

For each stable ID below, record source edition/section/page, precise scope, model or explanation as appropriate, valid inputs, reference-based diagram if relevant, bilingual worked example, independent expected results, tests, exact commit/run, and limitations. Use existing tools rather than duplicates. Assign status per item only after inspecting evidence: `unreviewed`, `partial`, `implemented-unverified`, `verified`, or `not-applicable` with rationale. A route is a lead, not proof. Every item below starts unchecked pending item-level reconciliation. Add sub-items for all figures, equations, edge cases and exercise families during the edition audit; don't copy textbook prose or copyrighted problem sets. Track errata and notation differences. No completion percentage until the scope denominator is stable.

## 1. Digital logic

Existing candidate routes: `gates, sequential, karnaugh, state-design` (partial evidence; not verified per item).

- [ ] C01.01 — Gate truth tables and Boolean identities; De Morgan and duality
- [ ] C01.02 — Canonical SOP/POS; minterms and maxterms; algebraic reduction
- [ ] C01.03 — Karnaugh adjacency, wrap-around and don't-care conditions
- [ ] C01.04 — NAND/NOR-only implementations; shared logic and hazards
- [ ] C01.05 — Combinational specification, synthesis and equivalence
- [ ] C01.06 — Latch/flip-flop excitation, characteristic equations and clocks
- [ ] C01.07 — Sequential state tables/graphs, reduction, assignment and synthesis
- [ ] C01.08 — Timing constraints, asynchronous behavior and race limitations

### Chapter 1 evidence reconciliation — 2026-11-25

| Item | Status | Existing evidence and remaining gaps |
|---|---|---|
| C01.01 | partial | logic_engine.py (e09e56f6), tests/test_logic_engine.py (30a6a610): gate truth tables and 2–4 input variants. 12 Boolean law families and recursive duality implemented in BOOLEAN_LAWS.md; 27 local tests passed, two Qt locale cases and visual evidence pending. Edition mapping and step-by-step symbolic derivation remain open. |
| C01.02 | partial | boolean_minimizer.py (1476c3cd), boolean_synthesis.py (d5c997ef): minimized SOP/POS with constants and deterministic completion. Canonical SOP/POS expansion and index lists now implemented; eight exact-engine local tests include known expressions. Algebraic derivation and edition reconciliation remain open. |
| C01.03 | partial | Existing K-map Gray indexing, legal cubes, both forms and don't-care handling; prior real-engine workflow tests (381d96a4). Exact edition figures and full visual review open. |
| C01.04 | partial | universal_gates.py (72dc42dc), NAND/NOR-only build in existing Karnaugh UI; isolated exact-converter oracle passed 438 circuits/6,740 rows. Real-engine and Qt regressions authored but unexecuted; static-1 SOP/static-0 POS edge detection and consensus preview now implemented (BOOLEAN_ANALYSIS.md). Physical/dynamic hazards and shared multi-output minimization open. |
| C01.05 | partial | CircuitDocument (2bf0d9f9), validated netlists, truth tables, synthesis and serialization. More worked designs and independent visual review open. |
| C01.06 | partial | Actual clocked model sequential_logic.py (b5fb70ca), derived characteristic and excitation reference (d8b549a1): 11 local tests passed using real engine, all 24 characteristic and 16 excitation rows. Bilingual tables and pending Qt evidence; SR NOR/NAND, level-sensitive D latch and abstract asynchronous D controls now implemented (STORAGE_ELEMENTS.md; 12 exact local tests). Schematic-level feedback visualization, physical timing, GUI and edition reconciliation remain open. |
| C01.07 | partial | Prior workflow suite includes state reduction, encoding, synthesis and clock equivalence. Edition-specific examples and remaining encoding domains open. |
| C01.08 | partial | Existing waveform records actual event order (not physical time); sequential_logic rejects forbidden SR edges, local verified. Ideal setup/hold constraint model and independent waveform exercise implemented (TIMING_CONSTRAINTS.md; 11 actual local tests, 12,288 combinations). Ideal latch forbidden release and asynchronous control priority modeled in STORAGE_ELEMENTS.md; propagation, recovery/removal timing, physical races and metastability remain open; Qt verification pending. |

No checklist box closed: edition-specific reconciliation and per-item acceptance remain necessary. See [Universal gate realization](UNIVERSAL_GATES.md). The local isolated oracle is not a full application test.

## 2. Digital components

Existing candidate routes: `components, registers-counter` (partial evidence; not verified per item).

- [ ] C02.01 — Integrated-circuit families and functional versus physical pinout
- [ ] C02.02 — Decoder/encoder, priority, enable and polarity
- [ ] C02.03 — Multiplexing/demultiplexing and logic realization
- [ ] C02.04 — Half/full adders, subtractors, carry propagation and look-ahead
- [ ] C02.05 — Magnitude comparison and arithmetic circuit composition
- [ ] C02.06 — Parallel registers, load/hold, serial/parallel shifts
- [ ] C02.07 — Binary, modulo-N, ripple/synchronous, ring/Johnson counters
- [ ] C02.08 — RAM/ROM organization, read/write controls and address selection

### Chapter 2 evidence review (partial, not closed)
| ID | Status | Evidence / remaining scope |
| --- | --- | --- |
| C02.01 | unreviewed | Functional gate shapes and pin anchors exist; device families, actual manufacturer pinouts and electrical limits still open. |
| C02.02 | partial | logic_engine presets include 2-to-4, 3-to-8 enabled decoders, active-low 2-to-4, one-hot and priority encoders. Existing test_enabled_decoder, test_encoder_validity and test_priority_encoder; wider variants and device-specific enables/polarities remain. |
| C02.03 | partial | 2-to-1 and 4-to-1 MUX, 1-to-2 DEMUX, existing exhaustive tests; Shannon MUX synthesis for 2–4 variables implemented (MUX_SYNTHESIS.md, nine exact local generator tests); shared-engine/UI checks pending, physical packages and broader selection remain. |
| C02.04 | partial | Half/full adders/subtractors and ripple4 existing tests; new lookahead4 structural generator, 10 exact local tests/672 vectors (CARRY_LOOKAHEAD.md), real engine and Qt cases pending. Physical timing and broader arithmetic composition open. |
| C02.05 | partial | 2/4-bit unsigned comparator with test_magnitude_comparator; signed/cascaded variants and physical IC detail open. |
| C02.06 | partial | sequential_logic contains REG4, SHIFT4, UNIVERSAL4 and clocked tests; more register variants and timing remain. |
| C02.07 | partial | COUNT4, UPDOWN4, RING4, JOHNSON4 implemented and existing tests; arbitrary modulus, ripple counter, physical timing remain. |
| C02.08 | partial | Inspected memory_model.py (e0a227bb), memory_organization.py (fa324ced), both UI routes and 18 existing array organization test cases. Ideal RAM/ROM active-low controls and RAM bank/word expansion implemented; source/test inspection only, no new integrated run. ROM programming, physical pinouts and timing remain. |

This review identifies existing source/test cases, not new integrated execution of those cases. Exact edition mapping and acceptance remain open.

## 3. Data representation

Existing candidate routes: `bases, codes` (partial evidence; not verified per item).

- [ ] C03.01 — Radix conversion including fractional values
- [ ] C03.02 — Binary, octal, hexadecimal and decimal representation
- [ ] C03.03 — Unsigned, sign-magnitude, ones' and twos' complement
- [ ] C03.04 — Radix and diminished-radix complements; end-around carry
- [ ] C03.05 — Fixed point, binary point scaling, range and overflow
- [ ] C03.06 — Textbook floating-point representation and normalization; modern IEEE comparison
- [ ] C03.07 — 8421 BCD, weighted and nonweighted codes, Gray conversion
- [ ] C03.08 — Character encoding, parity, Hamming distance and error detection/correction

## 4. Register transfer and microoperations

Existing candidate routes: `translator, alu, bus` (partial evidence; not verified per item).

- [ ] C04.01 — RTL grammar, conditional control and simultaneous transfers
- [ ] C04.02 — Register loading and common-bus selection
- [ ] C04.03 — Memory read/write and address/data transfers
- [ ] C04.04 — Adder/subtractor, increment/decrement and arithmetic microoperations
- [ ] C04.05 — Logic microoperations, selective set/clear/complement and masking
- [ ] C04.06 — Logical, circular and arithmetic shifts; rotate through carry
- [ ] C04.07 — Integrated arithmetic-logic-shift circuit and control word
- [ ] C04.08 — Timing, hardware resource conflicts and unsupported RTL diagnostics

## 5. Basic Computer design

Existing candidate routes: `basic-cpu, cpu-state, cycles` (partial evidence; not verified per item).

- [ ] C05.01 — 16-bit word, 12-bit address and register roles
- [ ] C05.02 — Instruction formats, opcode decoding and direct/indirect addressing
- [ ] C05.03 — Common bus data sources and destination loads
- [ ] C05.04 — Timing signals, sequence counter, fetch/decode/indirect cycle
- [ ] C05.05 — Seven memory-reference instructions and all documented addressing forms
- [ ] C05.06 — Register-reference instruction bits and combined-control cases
- [ ] C05.07 — I/O instructions, flags, interrupt request and return cycle
- [ ] C05.08 — Complete control functions, memory control, ALU and accumulator hardware

## 6. Programming the Basic Computer

Existing candidate routes: `debugger` (partial evidence; not verified per item).

- [ ] C06.01 — Machine code versus symbolic assembly, numeric constants and labels
- [ ] C06.02 — Assembler passes, symbol table, directives and diagnostics
- [ ] C06.03 — Arithmetic/logic program construction and independent results
- [ ] C06.04 — Conditional/unconditional branching and loop invariants
- [ ] C06.05 — Multiplication, division and multiword arithmetic software routines
- [ ] C06.06 — Subroutine call/return, BSA and parameter passing
- [ ] C06.07 — Programmed input/output, polling and interrupt-service examples
- [ ] C06.08 — Original worked exercises, trace-based debugging and memory bounds

## 7. Microprogrammed control

Existing candidate routes: `microprogram, microbuilder` (partial evidence; not verified per item).

- [ ] C07.01 — Control-store and control-memory organization
- [ ] C07.02 — Microinstruction word, field encoding and legal combinations
- [ ] C07.03 — Microoperation selection and conditional branch fields
- [ ] C07.04 — Microaddress sequencing, increment, branch and subroutine
- [ ] C07.05 — Opcode mapping, dispatch and instruction fetch microprogram
- [ ] C07.06 — Symbolic microprogram assembly and address resolution
- [ ] C07.07 — Control-unit hardware, mapping logic and control memory examples
- [ ] C07.08 — Trace/reverse, illegal codes and comparison with hardwired control

## 8. CPU organization

Existing candidate routes: `general-registers, stacks, addressing, formats` (partial evidence; not verified per item).

- [ ] C08.01 — Register file and ALU control-word selection
- [ ] C08.02 — Register and memory stack organization, overflow/underflow
- [ ] C08.03 — Expression translation and postfix evaluation
- [ ] C08.04 — Zero-, one-, two- and three-address instruction structures
- [ ] C08.05 — Effective addresses, immediate/direct/indirect/indexed/relative modes
- [ ] C08.06 — Data transfer, arithmetic, logic and program-control instruction families
- [ ] C08.07 — Status flags, conditional branches and program interrupts
- [ ] C08.08 — RISC/CISC design principles, representative encoding and instruction sequences

## 9. Pipeline and vector processing

Existing candidate routes: `pipeline, vector, floating-pipeline` (partial evidence; not verified per item).

- [ ] C09.01 — Parallelism taxonomy, throughput versus latency and speedup
- [ ] C09.02 — General pipeline timing, fill/drain and resource use
- [ ] C09.03 — Arithmetic pipelines and floating-point stages
- [ ] C09.04 — Instruction pipeline phases and data/control/structural hazards
- [ ] C09.05 — Forwarding, stalls, branch handling and variable latency
- [ ] C09.06 — RISC pipeline design and pipeline scheduling
- [ ] C09.07 — Vector instructions, memory access, dot product and matrix operations
- [ ] C09.08 — Array processors, attached versus SIMD arrangements and limitations

## 10. Computer arithmetic

Existing candidate routes: `booth, division, decimal, floating` (partial evidence; not verified per item).

- [ ] C10.01 — Signed-magnitude addition/subtraction and sign control
- [ ] C10.02 — Twos' complement addition/subtraction and overflow
- [ ] C10.03 — Unsigned multiplication, shift/add and signed Booth algorithm
- [ ] C10.04 — Restoring/non-restoring and signed division; zero and overflow
- [ ] C10.05 — Textbook floating-point add/subtract, multiply/divide and normalization
- [ ] C10.06 — IEEE comparison, rounding, special values and error bounds
- [ ] C10.07 — Decimal arithmetic unit, BCD correction and carries
- [ ] C10.08 — Decimal multiplication/division and decimal sign/overflow conventions

## 11. Input/output organization

Existing candidate routes: `handshake, interrupt, dma, fifo, serial` (partial evidence; not verified per item).

- [ ] C11.01 — Peripheral device classes and interface register roles
- [ ] C11.02 — I/O addressing, isolated versus memory-mapped interfaces
- [ ] C11.03 — Asynchronous strobe and handshake protocols
- [ ] C11.04 — Programmed I/O, polling and interrupt-driven transfers
- [ ] C11.05 — Priority interrupts, daisy chain, masks and nesting
- [ ] C11.06 — DMA ownership, burst/cycle stealing, address/count and completion
- [ ] C11.07 — I/O processor organization, CPU communication and channel examples
- [ ] C11.08 — Serial synchronous/asynchronous transfer, framing, baud and errors

## 12. Memory organization

Existing candidate routes: `memory-chip, memory-array, interleaving, cache, cam, virtual-memory` (partial evidence; not verified per item).

- [ ] C12.01 — Memory hierarchy, access time, cost and capacity tradeoffs
- [ ] C12.02 — Main memory chip selection, width/depth expansion and address decoding
- [ ] C12.03 — Secondary storage organization and access models
- [ ] C12.04 — Associative-memory match logic, masks and read/write
- [ ] C12.05 — Cache direct/associative/set-associative mapping and replacement
- [ ] C12.06 — Write policies, dirty lines, locality, hit/miss and timing
- [ ] C12.07 — Virtual-memory address translation, paging, replacement and TLB
- [ ] C12.08 — Memory protection, permissions, address bounds and page faults

## 13. Multiprocessors

Existing candidate routes: `multiprocessor, crossbar, synchronization, coherence, omega` (partial evidence; not verified per item).

- [ ] C13.01 — Multiprocessor characteristics, shared versus distributed organization
- [ ] C13.02 — Shared bus, arbitration, priority and fairness
- [ ] C13.03 — Multiport memory and crossbar switch contention
- [ ] C13.04 — Multistage networks, shuffle wiring, blocking and other topologies
- [ ] C13.05 — Communication mechanisms, shared memory and messages
- [ ] C13.06 — Synchronization, atomic operations, locks, semaphores and deadlock
- [ ] C13.07 — Cache coherence, invalidation/writeback and consistency distinctions
- [ ] C13.08 — Concurrent timing, performance and comparison of interconnects

## Practical laboratory and sample coverage
Every applicable section must also satisfy [PRACTICAL_LAB_POLICY.md](PRACTICAL_LAB_POLICY.md): reusable experiment, ready-to-load sample, independent expected output, edit/save/reset, and supported composability evidence. First combinational examples and block insertion are documented in CIRCUIT_LIBRARY.md; not full section or cross-model acceptance.

## Cross-cutting closure gates

- [ ] Reconcile exact instructor edition, sections, figures, formulas, examples and exercise categories with stable IDs.
- [ ] Identify historical versus modern extensions and unsupported variants explicitly.
- [ ] Verify each model independently, with exhaustive small-domain and boundary tests where feasible.
- [ ] Audit both locales, accessible controls, real screenshots and native Windows behavior.
- [ ] Keep README, curriculum ledger, issue #13 and this audit synchronized at each meaningful change.
- [ ] Preserve release isolation and the single-file academic translator contract.

Current inventory: 104 topic families across 13 chapters, plus six closure gates. This count is an audit starting point, not the total number of topics in the textbook. Existing 44 interactive entries on next-beta are not 44 verified textbook sections.
