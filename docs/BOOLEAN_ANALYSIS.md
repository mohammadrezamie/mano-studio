# Canonical forms and static hazards — Chapter 1

In Logic Lab → Karnaugh map → Forms & hazards, inspect the canonical SOP/POS expansions, minterm and maxterm indices, original don't-care indices and potential static hazard edges. All canonical values refer to the deterministic completion selected by the current minimizer, not the original incomplete specification. Changing SOP/POS may change this completion. The original truth table is not edited by the analysis.

Use Consensus example in SOP mode to load F = A'B + AC. The adjacent cells m3 and m7 both equal 1, but no original product covers both. Adding BC covers their transition. In POS mode the button loads the complementary function, whose static-0 repair adds (B' + C'). The preview preserves every completed cell. A dedicated button keeps the original wrap-around example unchanged.

در نقشه کارنو، زبانه فرم‌ها و مخاطرات را باز کنید. مثال جمله اجماع، تداخل احتمالی گذار بین سلول‌های ۳ و ۷ را نشان می‌دهد. افزودن جمله BC در SOP یا جمله (B' + C') در POS، پوشش این گذار را کامل می‌کند، بدون تغییر جدول درستی.

## Mathematical scope

Enumerate adjacent target cells at Hamming distance one. A static-1 SOP or static-0 POS candidate exists when no shared cube covers the pair. Add the two-cell cube by omitting the differing bit. These cubes are legal in the already completed function; no new don't-care choice is made. This simple deterministic repair is not globally minimum. The repaired expression is a preview; the existing build button still builds the minimized cover. No gate-delay, dynamic hazard, multi-input transition or physical timing guarantee.

## Verification

Local pure Python: 8 pytest cases passed in 0.39s with the actual existing minimizer, no test doubles. 512 three-variable form/function cases, 256 seeded incomplete four-variable form/function cases, known SOP/POS consensus examples, canonical XOR/constant forms and invalid inputs. Exact Git blobs: boolean_minimizer.py 1476c3cdf69a9cd65b443e281d14a89c42d06d74; boolean_analysis.py 76504ae1eae77e63f00277a51555543d29f6ee1b; tests/test_boolean_analysis.py 469518254034205d60f7d1bdb15b3da14bd0feb7. Four Qt locale/form tests authored, not executed locally. No new route; 44 remain.

Run: python -m pytest -q tests/test_boolean_analysis.py
