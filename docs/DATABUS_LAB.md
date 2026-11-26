# Shared RAM/register bus laboratory

Open Logic Lab → Memory & bus → RAM + registers (next to Register bus). The four-bit bus connects three four-bit register states (AR, R0, R1), a 16×4 RAM, and an external four-bit word. Source enables are explicit; destination load controls sample the old bus value on an ideal clock edge. The memory address is the old AR, even if AR is loaded on the same edge. The RAM read, register transition and bus resolution reuse the actual existing engines, not duplicated demo equations.

A single enabled driver is required for any load, even when multiple drivers agree. Zero drivers resolve to Z; conflicting bits resolve to X. Without a destination load, idle or contending buses can be observed and recorded. Rejected transfers leave registers, RAM and history unchanged. The UI exposes all 16 words of RAM and the last 64 accepted cycles. No propagation delay, device-specific electrical behavior, recovery/removal or multi-clock scheduling is modeled.

در آزمایشگاه منطق، بخش حافظه و گذرگاه و سپس RAM و ثبات‌ها را باز کنید. مبدأ داده و مقصدها را انتخاب و یک لبه ساعت اعمال کنید. اگر AR هم‌زمان بارگذاری شود، نوشتن حافظه همچنان در آدرس قبلی انجام می‌شود. با چند راه‌انداز یا نبود راه‌انداز، بارگذاری رد می‌شود. جدول حافظه و تاریخچه انتقال قابل مشاهده‌اند.

## Saved examples

| Sample | Expected result from reset |
|---|---|
| [RAM write/read](../examples/databus/ram-roundtrip.mano-databus.json) | AR=3, R0=0, R1=A, M[3]=A |
| [Parallel load and old address](../examples/databus/parallel-load.mano-databus.json) | AR=6, R0=6, R1=6, M[9]=6, M[6]=0 |
| [Bus contention](../examples/databus/bus-contention.mano-databus.json) | AR=0, R0=5, R1=6, bus=01XX, RAM unchanged |

Load example resets to zero after confirmation if an accepted cycle exists. Next example step applies the actual saved controls, one edge per press. Manual accepted edge leaves scripted replay. The originals are available as versioned JSON in the repo and embedded in the offline catalog; automated tests compare them. User-defined scenario file import/export and arbitrary typed block wiring are not implemented yet. This is an initial fixed-topology experiment, not a full datapath editor.

## Verified evidence

Run `python -m pytest -q tests/test_databus_lab.py tests/test_databus_samples.py`. Local actual 18 passed in 0.11 s with exact sources:
| File | Git blob |
|---|---|
| databus_lab.py | 59a083db2c4b5997672987928952a1b464f051ab |
| bus_model.py | d8358393860497f0074a46414c9a563551b2a033 |
| memory_model.py | e0a227bb42b709e8add7a7fe83292b5560540d3c |
| memory_organization.py | fa324ced8d3989d7988a28f3a2b17364cb0bb672 |
| sequential_logic.py | b5fb70ca291e6cfb94f2ab443448bff195f11e96 |
| tests/test_databus_lab.py | 2fd37a70a552bdb4405cb1fad8d032bedcdfaf00 |
| databus_samples.py | 6ab5f20fdd3eeb3d7555e256f4989f91f0dcf0aa |
| tests/test_databus_samples.py | 4bdc5bd7006923ee29f2ffe2e8abc62bb2088a4a |
| bus-contention JSON | 98a35bed1b61c7e4a6340a6b08dad00adc700739 |
| parallel-load JSON | db6335552514652f124f96a3b1ae0c656a02fb5f |
| ram-roundtrip JSON | 6a6c1923e4f3f1f0ab131e96678e74840a6bafb8 |

Eleven exact blobs matched (five engines, two tests, sample catalog, three JSONs). All five sources × 16 words × 16 destination masks; atomic invalid input, reset, Z/X and old-address behavior; exact three full-memory sample results. Both-locale Qt cases authored, not executed. 44 learning routes unchanged; no claim of arbitrary composition or full textbook coverage.

Next: versioned user scenario codec with validation, typed reusable stateful blocks, ALU and bus composition with explicit widths, native screenshot verification.
