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

## Additional saved samples and reuse
| Sample | Provisional section | Independent expected output |
|---|---|---|
| [Enabled active-low decoder](../examples/circuits/decoder-enabled-low.mano-logic.json) | C02.02 | EN=0 all high; EN=1 selected output low |
| [Two-bit comparator](../examples/circuits/comparator-two-bit.mano-logic.json) | C02.05 | Exactly one of LT, EQ, GT |
| [Two-bit adder/subtractor](../examples/circuits/adder-subtractor-two-bit.mano-logic.json) | C02.04 | M=0 addition; M=1 subtraction modulo four, Cout=1 iff no borrow |

The library groups examples by chapter. Insert circuit block → Load saved circuit can import your own existing circuit document. Choose the file, map each input, set a unique prefix and insert. The original file is never modified. Imported placement is regenerated in the combined design. Invalid file/cancel preserves previous selection. Names remain limited to 24 ASCII identifier characters; prefix 1–12. Same-name signal/output aliases are allowed for newly created identical signals. Other name collisions are rejected. This does not yet implement hierarchical reusable subcircuits or stateful bus wiring.

از منوی نمونه‌ها / بلوک‌ها، درج بلوک و سپس بارگذاری مدار ذخیره‌شده را انتخاب کنید. فایل اصلی تغییر نمی‌کند؛ ورودی‌ها را نگاشت و پیشوند یکتا تعیین کنید. چیدمان مدار ترکیبی دوباره ایجاد می‌شود.



## Reusable saved blocks and chapter sample expansion — 2026-11-26
Block dialog now accepts presets, built-in saved samples and user .mano-logic.json files; bounded 200,000-byte UTF-8 read, existing CircuitDocument validation, explicit pin mapping and namespaced insertion. Invalid/canceled file choice preserves staged selection. Same-name output aliases on newly introduced signals now supported; unrelated collisions still rejected. Local 14/14 pure tests passed (0.05s), exact source/test blobs: circuit_file eefac033ace3981d3a4fee8d23842eaf80266ad0 / b6739062bcdbfc03e06015838c839e0037f3ae92; block_composition b29478ff3ccb2a20aaeec863d36cf141ab2cefda / ee6c7ec12c91ca71c09fd7bc907e6d97db2c0723. Three new original saved circuits, independently evaluated from retrieved GitHub JSON by separate Boolean evaluator, all 56 input rows: active-low enabled decoder (67561052), two-bit comparator (06163433), two-bit add/subtract (a02fb0cd). Six total catalog samples and 76 truth rows across prior and current checks; chapter-grouped menu and provisional audit section IDs. Actual-engine sample regression and two-locale import tests authored, not executed locally; PySide6 unavailable. No new route, dependency, or physical timing claim; typed sequential/memory composition remains open. Release #22 unchanged.
