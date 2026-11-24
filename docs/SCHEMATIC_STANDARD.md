# Schematic conventions and validation

Owner requirement, 2026-11-24: internationally recognizable engineering notation, not arbitrary decorative shapes.

## References reviewed
- https://mbaillif.github.io/Logisim-evolution-documentation/en/html/guide/prefs/pref-intl.html — ANSI distinctive and IEC rectangular conventions.
- https://github.com/logisim-evolution/logisim-evolution/blob/main/src/main/resources/doc/en/html/libs/gates/basic.html — elementary gate appearance and input counts.
- https://mbaillif.github.io/Logisim-evolution-documentation/en/html/libs/gates/xor.html — ambiguity of multi-input XOR, parity alternatives.
- https://docs.kicad.org/10.0/en/eeschema/eeschema.html — wire crossings and junction dots.
- https://www.ti.com/product/SN74HC74 — example of an actual positive-edge D flip-flop with complementary outputs and additional preset/clear pins. Mano models ideal functional devices, not this physical IC.

## Required conventions
- ANSI-style distinctive gate geometry remains default. An inverter has a triangle and inversion bubble; AND/NAND use D shape; OR/NOR curved; XOR/XNOR extra input curve. Bubble means inversion, never a wire junction. Pin count must equal the simulation model; multi-input XOR/XNOR explicitly identified as odd/even parity.
- Functional terminals have signal names, bit states, and direction; no fictitious package pin numbers or power pins. Clock triangle denotes rising edge; complementary output uses Q with overbar, not an invented extra input.
- Wire junction dots only where same-net branches connect. Different-net crossings are not connections. Flag collinear overlap, touching or ambiguous junction crossings rather than silently implying shorts.
- Colors aid inspection but do not encode connectivity alone. Maintain readable symbols, line hierarchy, actual logical state and accessibility across Light/Dark/Night.
- Reference-based original drawing, not formal certification of IEEE 91 or IEC 60617. Do not copy proprietary or GPL drawing assets into the MIT application. Keep exact physical pinout/datasheet libraries out of scope until modeled faithfully.

## Current work
Audit existing symbol geometry, improve terminal labeling, compute junction and ambiguity marks from routed net identity, clarify sequential complementary output and parity. Add pure geometry and Qt regression tests. Preserve academic translator and Windows-first priorities.

## Implementation checkpoint
Added wire_notation.py: derives junctions and ambiguous contacts from routed segments grouped by actual net identity, not color. Same-net branching receives filled dots; simple bends and different-net interior crossings do not. Distinct-net collinear overlap and endpoint contacts are marked with outlined warning rings; a foreign crossing at a same-net junction suppresses the dot. Geometry is cached until routes change. Multi-input parity gates explicitly labeled ODD/EVEN; sequential Qbar displayed as Q with overbar in diagram/waveform while internal signal identifier unchanged. Existing functional port labels improved. Six pure geometry tests authored. Remaining: routing itself can still overlap, and markers do not solve all dense layouts; actual screenshot review and formal standards compliance not established.

### Optional rectangular convention
Settings now persists ANSI-style distinctive (default) or IEC-style rectangular gate rendering. Same scene coordinates, terminal anchors, netlist and truth table. IEC-style qualifiers: &, ≥1, 1, =1 for two-input XOR/XNOR, 2k+1 for multi-input parity; inversion bubbles denote complemented outputs. Reference: https://truthtablekit.com/logic-gate-symbols/symbols-xor-ieee-vs-iec/ and https://mbaillif.github.io/Logisim-evolution-documentation/en/html/guide/prefs/pref-intl.html. Original drawing, no copied code/assets. UI regression checks persisted style, pin count and unchanged parity behavior. This does not imply complete IEC 60617 certification or rectangular symbols for every physical device.
