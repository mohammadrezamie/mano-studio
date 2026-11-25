# MSI cache coherence / هماهنگی کش MSI

Chapter 13 educational model. Four processors share 16 memory words. Each cache has four direct-mapped single-word slots; index = address mod 4. M = modified, S = shared, I = invalid. A local M write or valid local read needs no bus request. Read miss broadcasts BusRd; a dirty owner writes back and becomes S. Write miss broadcasts BusRdX; shared or modified peer copies are invalidated, and any dirty owner writes back. A shared write broadcasts BusUpgr. Conflict eviction of M writes back first. Main RAM can lag behind the newest value only while one M owner exists. Bus and writeback fields describe the same atomic educational access, not physical timing.

فارسی: چهار پردازنده با حافظه مشترک، هرکدام چهار خط کش مستقیم دارند. M یعنی تغییر‌یافته، S یعنی مشترک و I یعنی نامعتبر. در نوشتن، نسخه‌های دیگر نامعتبر می‌شوند. اگر خط تغییر‌یافته از کش خارج شود یا پردازنده دیگری آن را درخواست کند، مقدار آن به حافظه بازگردانده می‌شود. مثال: P0 در آدرس 3 مقدار ABCD می‌نویسد؛ P1 همان آدرس را می‌خواند و ABCD دریافت می‌کند؛ هر دو خط S می‌شوند و RAM به‌روز می‌شود.

Limits: serialized transactions, no true parallel races, store buffers, cache hierarchy, MESI, timing or physical bus integration. Independent oracle and protocol invariant tests: 20 passed locally, 10,000 randomized accesses. GUI and curriculum route are implemented on the isolated next-beta branch; Qt execution and native visual review remain pending. First beta is unaffected.

## Interactive lesson / تمرین تعاملی

Learning Center → Chapter 13 → MSI cache coherence, or Computer → Multiprocessors → Cache coherence. Write ABCD from P0 to address 3: P0 owns M and RAM remains 0000. Read from P1: both lines become S, RAM becomes ABCD, and BusRd/writeback appear. Write from P1 to observe BusUpgr and invalidation of P0. Reset clears RAM, caches and the bounded 128-event trace.

مرکز آموزش ← فصل ۱۳ ← هماهنگی کش MSI. ابتدا در P0 بنویسید و در P1 بخوانید؛ سپس تغییر حالت‌ها و بازنویسی حافظه را بررسی کنید.

The view reuses MSICache and does not alter the Basic Computer CPU. No new dependency or network access. Bilingual GUI regressions and asserted dirty-owner/shared-read screenshot contracts are authored, not executed locally. No public release.
