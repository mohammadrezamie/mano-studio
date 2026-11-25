# Universal gate realization — Chapter 1

From Logic Lab → Karnaugh map, choose Mixed gates, NAND or NOR, then build the editable circuit. The original minimized SOP/POS solution and its deterministic don't-care completion stay the same; only the gate technology changes. Every output truth-table row is checked before the existing circuit is replaced. Cancellation, rejection and undo preserve the prior circuit.

در آزمایشگاه منطق، نقشه کارنو را باز کنید و خانواده گیت NAND یا NOR را انتخاب کنید. مدار حاصل تنها از گیت انتخاب‌شده ساخته می‌شود؛ جدول درستی باید با مدار اولیه برابر باشد.

For NAND, NOT(a)=NAND(a,a), AND is inversion of NAND, and OR uses NAND of inverted inputs. NOR is the dual construction. XOR uses four NANDs (or four NORs for XNOR, followed by inversion). Larger fan-in is reduced in binary steps. Shared commutative expressions reuse identical primitive gates. All output aliases and direct input connections are preserved, with new automatic placement and deterministic signal names. Reject expansion beyond the existing 96-gate document limit.

## Evidence and limitations

Exact new converter blob 72dc42dc8f575a5527f2db1f4cf04bbfea4ebbb8 was exercised locally against an independent Boolean evaluator with test-double CircuitDocument/Gate interfaces: 438 circuits and 6,740 input rows passed (38 primitive/arity combinations and 400 seeded multi-output circuits). This is not the full real-engine regression. Repository tests/test_universal_gates.py adds actual engine, library, serialization, 1,024 three-variable form/family cases, incomplete four-variable maps and limit tests; tests/test_universal_view.py adds four locale/family confirmation and undo cases. These integrated tests are authored, not yet executed; Qt is unavailable locally.

No global gate-count optimum, shared multi-output cover minimization, propagation delay, static/dynamic hazard analysis or physical electrical timing claim. This extends existing Karnaugh route without adding a duplicate tool. The textbook audit item C01.04 remains partial.
