# Storage elements — Chapter 1

Open Logic Lab → Sequential → Latches / async. Four independent models demonstrate level-sensitive versus rising-edge behavior and asynchronous controls. Select a component, stage its pins and apply one atomic input vector; the lesson records the last 32 input/output events. It never modifies the existing live clocked model. Active-low pins have a bar suffix and start inactive (1).

| Component | Behavior |
|---|---|
| NOR SR latch | S=1 sets, R=1 resets, 00 holds, 11 drives Q/Qbar to 00 |
| NAND SR latch | Sbar=0 sets, Rbar=0 resets, 11 holds, 00 drives Q/Qbar to 11 |
| D latch | EN=1 transparent, EN=0 holds |
| Abstract D flip-flop | PREbar=0 or CLRbar=0 overrides clock; both asserted yields unknown; otherwise samples D only on rising edge |

Releasing both forbidden SR inputs simultaneously leaves both outputs unknown, rather than inventing a stable state. A deterministic set/reset restores a known complementary output. The abstract DFF treats simultaneous active controls as unknown; recovery/removal timing is not modeled and simultaneous release and a rising edge are resolved only by the documented ideal event rule. No analog metastability duration, propagation delay, physical race prediction or universal device-specific asynchronous behavior is claimed. The table is an event history, not a circuit-level timing diagram.

در زبانه لچ و ناهمگام، ابتدا ورودی‌ها را انتخاب و سپس یک رویداد هم‌زمان اعمال کنید. لچ D در سطح فعال EN داده را عبور می‌دهد؛ فلیپ‌فلاپ لبه‌ای فقط در لبه بالارونده داده را نمونه‌برداری می‌کند مگر اینکه کنترل ناهمگام فعال باشد. در رهاسازی هم‌زمان ورودی‌های ممنوع SR، حالت نامعلوم نمایش داده می‌شود.

## Verification
12 local pytest cases passed in 0.04 s. Includes both SR polarity tables, forbidden release and recovery, all 8 binary D latch combinations, 96 asynchronous DFF state/input/previous-clock combinations and invalid inputs. Exact Git blobs matched: storage_elements.py d5800eb06386c18a76d114463be14ca25b7062a4; tests/test_storage_elements.py 8dabdb73391a0fadaf648af6f88f4a38c27a7ef3. Run `python -m pytest -q tests/test_storage_elements.py`. Two bilingual Qt cases, search and four actual-state screenshot requirements authored, not executed. No additional route or dependency; 44 entries retained. Textbook audit remains partial until exact edition mapping and real GUI verification; physical timing and schematic-level gate feedback visualization remain open.
