# MSI cache coherence / هماهنگی کش MSI

Chapter 13 educational model. Four processors share 16 memory words. Each cache has four direct-mapped single-word slots; index = address mod 4. M = modified, S = shared, I = invalid. A local M write or valid local read needs no bus request. Read miss broadcasts BusRd; a dirty owner writes back and becomes S. Write miss broadcasts BusRdX; shared or modified peer copies are invalidated, and any dirty owner writes back. A shared write broadcasts BusUpgr. Conflict eviction of M writes back first. Main RAM can lag behind the newest value only while one M owner exists. Bus and writeback fields describe the same atomic educational access, not physical timing.

فارسی: چهار پردازنده با حافظه مشترک، هرکدام چهار خط کش مستقیم دارند. M یعنی تغییر‌یافته، S یعنی مشترک و I یعنی نامعتبر. در نوشتن، نسخه‌های دیگر نامعتبر می‌شوند. اگر خط تغییر‌یافته از کش خارج شود یا پردازنده دیگری آن را درخواست کند، مقدار آن به حافظه بازگردانده می‌شود. مثال: P0 در آدرس 3 مقدار ABCD می‌نویسد؛ P1 همان آدرس را می‌خواند و ABCD دریافت می‌کند؛ هر دو خط S می‌شوند و RAM به‌روز می‌شود.

Limits: serialized transactions, no true parallel races, store buffers, cache hierarchy, MESI, timing or physical bus integration. Independent oracle and protocol invariant tests: 20 passed locally, 10,000 randomized accesses. GUI and curriculum route remain future work. First beta is unaffected.
