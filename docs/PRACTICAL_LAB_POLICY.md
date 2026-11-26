# Practical laboratory and reusable samples — permanent owner requirement (2026-11-26)

Full coverage means more than reading the textbook or demonstrating isolated components. Each applicable section of Morris Mano must be useful for education AND actual experimentation. This is a next-generation requirement, not a reason to delay the already-frozen first Windows beta.

## Section acceptance contract

For each mapped textbook section, record:
- Exact edition/section reference and original bilingual teaching material, equations, pin behavior and limitations.
- An interactive experiment using the actual shared model, with editable inputs, observable outputs/internal state and reset/repeat.
- A curated library of famous or pedagogically useful ready-to-load samples, categorized in the relevant section. Each sample has a stable ID, localized title/task, original or licensed source/provenance, expected independent results, and a reproducible reset state.
- Editable and savable copies of experiments, with a versioned validated format; loading must never silently discard user work. Keep shipped originals immutable.
- For composable digital circuits, reusable blocks, explicit port mapping, signal width/polarity/clock semantics, validation, wiring, inspection, execution, undo and export. Connect real models, never merely draw links between disconnected simulations.
- Test independently and across combinations; verify examples, invalid connections, cancellation, file roundtrip, both locales, and real visual evidence.

## Staged implementation

1. Combinational blocks: insert existing circuit presets into one editable netlist, explicit inputs linked to existing signals or fresh pins, namespaced outputs and gate names, validate before mutation, undo and save. No hidden cross-model simulation.
2. Expand ready-to-load original circuit samples (canonical full adder using half adders, universal-gate implementations, MUX functions, arithmetic chains, decoders, comparators). Each sample gets a truth oracle and a saved circuit document in the repository.
3. Build typed composition for buses, sequential registers, clocks and memory. Specify event ordering, reset, bit widths, polarity, high impedance and contention. Reject unsupported feedback instead of pretending a combinational engine can simulate it.
4. Extend experiments and saved scenarios across every chapter: numbers/codes, RTL, Basic Computer, assembly programs, microprograms, CPU organization, pipelines, arithmetic, I/O, memory, multiprocessors. Cross-domain integration requires a documented interface and shared simulation semantics; not every theoretical topic is a wireable circuit.
5. Track exact section evidence, sample IDs, interface coverage, actual tests and gaps in the textbook audit and issue #13. No claim of complete coverage until all applicable gates are verified.

Permanent constraints: offline, Persian/English parity, shared engine and normal editor formats, internationally recognizable functional symbols, no unsupported physical-timing claims, no new dependencies without benefit. Preserve standalone rtl_translator.py. Release track remains independent.

Native project persistence: use the versioned .mano envelope for all future applicable lab documents; extend by explicitly validated kinds, preserve backward compatibility and independent sample oracles. Current kinds rtl/asm/circuit only. See NATIVE_FILES_AND_UPDATES.md.
