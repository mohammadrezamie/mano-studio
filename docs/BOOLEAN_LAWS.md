# Boolean identities and duality — Chapter 1

Open Logic Lab → Karnaugh map → Boolean laws. Choose an identity, toggle Dual form, and inspect all eight A/B/C rows of both expressions. Unused variables repeat rows. This is an independent educational inspector: the current map and circuit remain unchanged.

The 12 law families are identity, domination, idempotence, complement, double negation, commutativity, associativity, distributivity, absorption, De Morgan, consensus and combining. Duality recursively swaps AND/OR and 0/1; variable names and the NOT operator are preserved. For example, A + 0 = A becomes A · 1 = A. De Morgan's (A + B)' = A' · B' becomes (A · B)' = A' + B'. Duality is not simply complementing a displayed expression.

در زبانه قوانین بول، یک قانون انتخاب و گزینه فرم دوگان را فعال کنید. جابه‌جایی AND و OR و ثابت‌های ۰ و ۱، فرم دوگان را می‌سازد. هر دو طرف رابطه برای تمام ترکیب‌های ورودی محاسبه می‌شوند. برای نمونه، A+0=A به A·1=A تبدیل می‌شود.

## Evidence

Local pure Python: 27 pytest cases passed in 0.05s. 24 law/form combinations × 8 rows = 192 comparisons; double-dual structure and complement-input identity checked for both sides, with independently expected De Morgan/consensus results and invalid-input checks. Tested files match GitHub blobs boolean_laws.py 45d689fa3323b7c682d1e04dbb4e74181f1e6b1f and tests/test_boolean_laws.py ce6d14ff1f3511998690c17aefa46e89153eab6b.

Run: python -m pytest -q tests/test_boolean_laws.py

Two Qt locale cases and bilingual catalog search regression authored, not executed. State-asserted screenshots of dual De Morgan and static hazard examples in both locales are now required by the visual contract (four additional images; not generated yet). No new route or dependency. No arbitrary expression parser, general symbolic proof, derivation of every textbook axiom, or complete Chapter 1 claim. Exact edition mapping and real GUI acceptance remain open.
