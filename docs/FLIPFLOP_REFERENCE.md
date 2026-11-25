# Flip-flop characteristic and excitation tables — Chapter 1

Open Logic Lab → Sequential → Flip-flop tables. Select D, T, JK or clocked active-high SR. The reference panel follows the selected model and does not modify its state, inputs, clock or recorded waveform. For multibit components it explains that these tables describe one-bit flip-flops only. The original event waveform remains in its own tab.

The characteristic table maps present Q and actual inputs to next Q at a rising edge. The excitation table reverses that relation, deriving all admissible input choices for a desired transition; X means either binary value is valid, not an unknown physical output. Compact patterns are checked against the exact set of admissible inputs. SR=11 is forbidden; the existing model rejects a rising edge in that state. Characteristic equations are taken from sequential_logic.RULES.

در آزمایشگاه منطق، بخش مدارهای ترتیبی و سپس جدول‌های فلیپ‌فلاپ را باز کنید. جدول مشخصه حالت بعد را از ورودی‌ها و حالت فعلی تعیین می‌کند. جدول تحریک ورودی‌های لازم برای گذار مورد نظر را نشان می‌دهد. X به معنای مجاز بودن هر دو مقدار است؛ نه خروجی نامعلوم.

| Q → Q′ | D | T | JK | SR |
|---|---|---|---|---|
| 0 → 0 | 0 | 0 | 0X | 0X |
| 0 → 1 | 1 | 1 | 1X | 10 |
| 1 → 0 | 0 | 1 | X1 | 01 |
| 1 → 1 | 1 | 0 | X0 | X0 |

## Verification

11 local pytest cases passed in 0.07 s using the actual clocked engine, not a test double. All 24 characteristic rows (including two forbidden SR cases), all 16 excitation rows and their expanded binary choices, independent transition oracles, actual rising-edge state and atomic forbidden-edge rejection. Tested Git hashes match remote: sequential_logic.py b5fb70ca291e6cfb94f2ab443448bff195f11e96; flipflop_reference.py d8b549a1955ff9978db8aeba4974bed07f6d01f6; tests/test_flipflop_reference.py 8a3f4fa65014a3df8d243d3150b39b5e4326f568.

Run python -m pytest -q tests/test_flipflop_reference.py.

Two Qt locale cases, search regression and four active-state screenshot requirements (JK and SR × EN/FA) authored, not executed. This is an ideal synchronous teaching model. Level-sensitive latches, setup/hold, clock-to-Q delay, metastability, asynchronous preset/clear and physical race behavior remain open. No new learning route or dependency; 44 entries retained. No change to the academic translator or frozen beta.
