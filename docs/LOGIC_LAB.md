# Mano Logic Lab — development preview
The required classroom deliverable remains the independent RTL-to-assembly translator. Logic Lab is an optional offline learning workspace, not a replacement.

## Current implementation
Chapter alignment: Morris Mano, Computer System Architecture (3rd ed.), ch. 1 Digital Logic Circuits (logic gates, half/full adder); ch. 2 Digital Components (decoder, encoder, multiplexer); ch. 4 Register Transfer and Microoperations (binary adder). Reference contents: https://www.academia.edu/38425107/Computer_system_architecture_mano ; textbook text: https://studylib.net/doc/27337396/computer-system-architecture-m.-morris-mano . The demultiplexer and half subtractor are useful supplementary circuits. These original netlists are not reproductions of textbook figures.

15 selectable circuits: NOT, AND, OR, XOR, NAND, NOR, XNOR, half adder, full adder, 2-to-4 decoder, one-hot 4-to-2 encoder (explicit Valid output), 2-to-1 MUX, 1-to-2 DEMUX, half subtractor, 4-bit ripple-carry adder. The engine can construct ripple adders of width 1–8, but the UI offers 4-bit only; truth-table generation caps input count at 10.

logic_engine.py contains pure Python acyclic gate netlists. A single evaluate() supplies each internal signal and output, truth tables and diagram colors. ui/logic_lab.py provides auto-layout by logical depth, labeled rectangular gates, binary input buttons, live output state, truth-table row selection and zoom/pan. Diagrams are simplified educational schematics, not optimized routing or arbitrary drag-and-drop circuit design. Signal colors show settled 0/1 values, not physical propagation delays. Persian and English labels and existing three themes; no network, no constant animations. Newly authored regression tests cover gate tables, invalid circuits, and all 512 combinations of a 4-bit adder with carry-in. Runtime and visual verification pending.

## Next development
- Create a general circuit canvas with draggable gates, ports, wires, validation, save/open JSON, undo, zoom, routing, SVG/PNG export and truth table export. Use the same logic engine; detect loops and unsupported states, do not evaluate arbitrary user code.
- Sequential logic (SR/D/JK/T flip-flops, edge-triggered clock, registers, shift registers, binary counters) with explicit clock events and waveform viewer, not combinational feedback hacks.
- Arithmetic and Logic Unit (ALU), adder-subtractor, incrementer, shifter, 16-bit bus, data representation, two's complement, Gray code, BCD. Integrate the same event-driven processor visualization with chapters 4–6.
- Optional learning modules for microprogrammed control, pipeline, computer arithmetic, I/O, cache and memory hierarchy, guided exercises and bilingual explanations, scoped by chapter rather than cluttering the main editor.
- Improve calm Mano Glass navigation with grouped labs, preserve focus on translator. No release or installer activity until owner requests it.
