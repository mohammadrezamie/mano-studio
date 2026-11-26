# Combinational sample library and reusable blocks

In Logic Lab → Combinational → Library / blocks, choose a ready-made sample or Insert circuit block. For insertion, select a preset, assign a unique ASCII prefix, and map each input to an actual existing signal or a new input. Existing output aliases remain; new ones receive a prefix. Validate the result before mutation. Undo returns to the prior document, save/export uses the existing circuit editor. Layout regenerates, rather than attempting to preserve all manual coordinates. The supported scope is acyclic one-bit combinational blocks, at most 10 input pins, 96 gates and 16 output aliases; name collisions are rejected. Arbitrary saved-file block insertion and multi-bit/clocked/memory composition remain future work.

در آزمایشگاه منطق، از منوی نمونه‌ها / بلوک‌ها یک نمونه آماده باز کنید یا بلوک مدار درج کنید. ورودی‌های بلوک جدید را به سیگنال‌های موجود یا ورودی‌های جدید متصل کنید. پیشوند یکتا، نام‌ها را جدا نگه می‌دارد. مدار ترکیبی را آزمایش، ذخیره یا واگرد کنید.

| Original sample | Independent expected outcome |
|---|---|
| [Full adder from half adders](../examples/circuits/full-adder-halves.mano-logic.json) | S + 2×Cout = A+B+Cin |
| [Four-NAND XOR](../examples/circuits/nand-xor.mano-logic.json) | Y = A XOR B |
| [MUX majority](../examples/circuits/mux-majority.mano-logic.json) | Y=1 iff at least two inputs are 1 |

The JSON examples are original, editable, portable documents. The runtime catalog embeds identical definitions to avoid relying on external files in an installed build; a regression checks they match. To build an adder manually, start with half_adder, insert a second half_adder mapping A to sum and B to new input, then insert OR mapping its two inputs to carry and the second carry signal. Read the prefixed sum and OR output. Existing intermediate output aliases are intentionally retained.


## Practical laboratory checkpoint — 2026-11-26
Owner requires full-textbook educational and experimental coverage, useful composable circuits, and saved famous samples inside each applicable section. Permanent rules: AGENTS.md and PRACTICAL_LAB_POLICY.md. First combinational insertion plan maps preset inputs to existing one-bit signals or fresh namespaced inputs, keeps original outputs, enforces editor limits, validates actual documents before replacement and supports undo/save through existing editor. Original three samples are stored as editable JSON in examples/circuits and accessible from the Library / blocks menu. 10 local pure planner tests passed (0.04 s), exact blobs d911d4be61596ce503a2cc076d8e9ab46131ba53 / 84b3eec32bf2f6322314ee3532f2b38eeac8c260. Independently evaluated all 20 truth rows of the three saved JSON samples, exact Git hashes ecf9305920e2eeec3f90fa699445728cad0f0eaa / e61e10f437fed3c58aa218fb785a528a06e85634 / 6d9a7efd26c04687eac67394f2db56f5f460d2ef. Actual CircuitDocument integration and both-locale GUI tests authored, not executed. Layout regenerated; prefix collisions rejected, one-bit acyclic combinational insertion only, no arbitrary cross-model wiring or physical timing. Next: saved custom block import, sample metadata/section index and typed sequential/bus composition. No new route, no translator change. First beta remains separate #22 at ecb6647c38a93a4eb9c2171c99c10392abd15e72; its installer and tests were queued at inspection.
