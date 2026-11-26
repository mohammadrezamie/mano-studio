# Carry look-ahead adder — Chapter 2

Open Logic Lab → Combinational → 4-bit carry look-ahead adder. This preset uses the same structural netlist, existing gate shapes, equations, pin values, truth table and editable document workflow as the ripple adder. Nine inputs (A0–A3, B0–B3, Cin), five outputs (S0–S3, Cout); all 512 truth rows. The pure network generator also supports widths 2 and 3; only width 4 is exposed as a preset.

For each bit i, p_i = A_i XOR B_i, g_i = A_i AND B_i. S_i = p_i XOR C_i. For each prefix ending at i, group P is the product of its propagate bits; group G is the OR of every generated carry propagated through all higher bits in that prefix. C_(i+1) = G OR (P AND Cin), without depending on any earlier carry gate. No gate has more than four inputs. The group expansion is not optimized for minimum gate count.

| Four-bit network | Gates | Ideal Cout gate levels |
| --- | ---: | ---: |
| Existing ripple | 20 | 9 |
| Look-ahead | 32 | 4 |

The level comparison counts each gate as one stage regardless of fan-in. It is structural, not a physical nanosecond delay or measured hardware speedup. Actual gate delays, load, routing, fan-out and device characteristics differ. The look-ahead generator computes all four prefix carries even though some are internal.

در آزمایشگاه منطق، جمع‌کننده نقلی پیش‌بین ۴ بیتی را انتخاب کنید. هر بیت انتشار p و تولید g را دارد؛ نقلی هر پیشوند مستقیماً از Cin و معادلات گروهی به دست می‌آید. برای نمونه A=15، B=0، Cin=1، حاصل جمع چهار بیت صفر و Cout=1 است. تعداد سطوح منطقی فقط مقایسه ساختاری است و زمان فیزیکی را نشان نمی‌دهد.

## Evidence
Local execution: 10 pytest cases passed (0.05s), with the actual generator and a separate Boolean evaluator, not the application's Circuit engine. Exhaustive 672 binary input combinations across widths 2/3/4 (32+128+512), every prefix carry independently compared to masked integer addition, topological/arity checks and invalid widths. Exact remote blobs match local tested files: carry_lookahead.py d0c9c93e61f96a0646d68af43a19b39ad7ff1813 and tests/test_carry_lookahead.py 178b8b541b05fecc29004b9c360f547c1dc99feb. Run: python -m pytest -q tests/test_carry_lookahead.py.

Shared engine preset integration, ripple equivalence and document roundtrip cases, two Qt locale cases, catalog search and two state-asserted screenshots authored, not executed locally. No new learning route (44 entries); 24 circuit presets on next-beta. Release PR #22 and academic translator remain independent. Chapter 2 audit is partial; physical IC pinouts and physical timing are not claimed.
