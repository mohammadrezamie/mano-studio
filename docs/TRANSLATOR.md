# Translator / راهنمای دفاع

**فایل تکلیف استاد: [rtl_translator.py](../rtl_translator.py).** فقط همین فایل شامل الگوریتم موردنیاز دفاع است؛ سایر ماژول‌ها امکانات اختیاری نرم‌افزار هستند. برای دفاع فایل را مستقیماً از سورس پروژه باز کنید؛ نیازی به نمایش سورس داخل نرم‌افزار نیست.
Run `python rtl_translator.py examples/add.rtl -o result.asm` with Python 3.10+. No runtime dependencies. Run `python -m pip install -r requirements-dev.txt` then `python -m pytest -q`.

The engine splits input into lines, removes comments, matches each full statement against 32 regular-expression rules (25 mnemonics plus seven indirect variants), validates and pads hexadecimal addresses, then returns instructions with their source line and diagnostics. `TranslationResult.assembly` refuses export if any diagnostic exists. The CLI reads UTF-8 (including BOM), writes ASM only on success and returns nonzero on error. Existing output is left unchanged on invalid input. GUI must call `translate()` rather than implement duplicate rules.

فارسی: ابتدا متن به خطوط جدا می‌شود؛ توضیحات حذف می‌شوند؛ هر خط با الگوی کامل دستورات مقایسه می‌شود؛ آدرس حافظه بررسی شده و دستور اسمبلی ساخته می‌شود. در صورت وجود خطا خروجی جدید تولید نمی‌شود. فایل اصلی مستقل `rtl_translator.py` است. عبارت‌های RTL در این نسخه خلاصه رفتار دستور هستند، نه تمام ریزعملیات سخت‌افزاری. پشتیبانی فعلی ۲۵ دستور نام‌دار است؛ ورودی استاد هنوز تأیید نشده است.

`instruction_catalog.py` provides canonical templates for guided input, separate from the translator. Each template is tested against the same engine.

## دفاع از فایل اصلی — مسیر پیشنهادی مطالعه

تمام تبدیل واقعی در `rtl_translator.py` انجام می‌شود. این فایل به Qt، اسمبلر، شبیه‌ساز، اینترنت یا فایل دیگری از پروژه وابسته نیست. فقط کتابخانه استاندارد پایتون لازم است. فایل را با Python 3.10 یا بالاتر اجرا کنید.

### هفت بخش کد
1. کلاس‌های Instruction، Diagnostic و TranslationResult: نگهداری نتیجه و شماره خط و خطاها.
2. الگوهای مشترک: ASSIGN علامت انتساب، ADDRESS ارقام هگز، REPEAT تکرار دقیق همان آدرس، PLUS و COMMA عملگر و جداکننده. توابع mem و skip قطعات الگو را می‌سازند.
3. memory_rules: هفت دستور حافظه‌ای، مستقیم و غیرمستقیم؛ مجموعاً ۱۴ الگو.
4. FIXED_RULES: دوازده دستور ثباتی و شش دستور ورودی/خروجی، بدون عملوند آدرس.
5. RULES: ترکیب و کامپایل ۳۲ الگو برای ۲۵ دستور نام‌دار.
6. translate(text): پیمایش خطوط، حذف توضیحات، تطبیق کامل عبارت، اعتبارسنجی آدرس و تولید نتیجه.
7. main(): خواندن فایل UTF-8، فراخوانی translate، بررسی خطا و نوشتن فایل ASM در صورت موفقیت. شرط __name__ باعث می‌شود هنگام import از رابط کاربری CLI اجرا نشود.

### مثال مرحله‌به‌مرحله
ورودی: `AC ← AC + M[101]`.
پس از حذف فاصله ابتدا و انتها، الگوی ADD با fullmatch تطبیق پیدا می‌کند. گروه address مقدار 101 را دریافت می‌کند. سه رقم هگز معتبر است. دستور تولیدشده ADD 101 و شماره خط اصلی در Instruction ثبت می‌شود.
ورودی `AC ← M[M[100]]` از الگوی غیرمستقیم استفاده می‌کند و LDA 100 I تولید می‌کند.
ورودی `AC ← M[1000]` با شکل دستور حافظه‌ای تطبیق دارد اما طول آدرس از سه رقم بیشتر است؛ ADDRESS_RANGE ثبت می‌شود.
ورودی `AR ← PC` با هیچ الگوی دستور مستقل تطبیق ندارد؛ UNSUPPORTED_RTL ثبت می‌شود.

### سوال‌های تمرینی استاد
- چرا fullmatch و نه search؟ چون کل عبارت باید معتبر باشد؛ وجود یک بخش درست در عبارت نامعتبر کافی نیست.
- چرا ۳۲ الگو برای ۲۵ دستور؟ هفت دستور حافظه‌ای دو حالت مستقیم و غیرمستقیم دارند؛ ۱۸ دستور دیگر فقط یک حالت دارند.
- چرا re.compile خارج از حلقه است؟ الگوها یک‌بار آماده می‌شوند و برای همه خطوط قابل استفاده هستند.
- چرا enumerate از ۱ شروع شده؟ شماره خط برای گزارش خطا و ارتباط با خروجی حفظ می‌شود.
- چرا zfill(3)؟ برای نمایش آدرس ۱۲ بیتی با سه رقم هگز.
- چرا break و for/else؟ پس از نخستین تطبیق از حلقه خارج می‌شویم؛ اگر هیچ تطبیقی وجود نداشته باشد else خطا را ثبت می‌کند.
- آیا هر RTL قابل تبدیل است؟ خیر؛ این نسخه رفتار سطح دستور را با دستورهای نام‌دار مانو تطبیق می‌دهد؛ ریزعملیات دلخواه لزوماً دستور اسمبلی متناظر ندارند.
- تفاوت مترجم و اسمبلر چیست؟ این فایل فقط RTL به ASM می‌دهد؛ تبدیل ASM به کد ماشین در assembler.py انجام می‌شود.
- آیا با وجود خطا فایل خروجی نیمه‌کاره تولید می‌شود؟ خیر؛ CLI و GUI خروجی جدید را نمی‌پذیرند. فایل خروجی قدیمی دست‌نخورده می‌ماند.

### تمرین عملی یک‌روزه
ابتدا یک فایل RTL با LDA، ADD، STA و HLT بنویسید و خروجی را با دست پیش‌بینی کنید. سپس اجرای CLI، حالت غیرمستقیم، آدرس کوتاه، توضیحات، و ورودی نامعتبر را تمرین کنید. در پایان تابع translate را خط‌به‌خط دنبال کنید و یک دستور ثباتی و یک دستور حافظه‌ای را از روی الگوهای واقعی توضیح دهید. قواعد ورودی استاد هنوز تأیید نشده؛ راهنما باید با نسخه نهایی قواعد و نمونه‌های استاد به‌روز بماند.

تست قرارداد استقلال: `python -m pytest -q tests/test_translator_isolation.py`. این تست کپی تنها فایل مترجم را با Python -I -S اجرا می‌کند و عدم وابستگی و عدم بازنویسی خروجی هنگام خطا را بررسی می‌کند.


## Academic address-matrix QA — 2026-11-25
Independent classroom regression on main 2f3807eabb5f0ca1d9c9f0206a1ce81fe7b00696. All 4096 addresses × seven memory-reference mnemonics × direct/indirect = 57,344 successful translations; 18 fixed mnemonics tested in three notation styles; invalid address 1000 rejected for all 14 memory forms. Covers case, padding, arrows/ASCII/equal assignment, tabs, inline comments, CRLF and line mapping. Standalone CLI copied by itself, run with Python -I -S, UTF-8 BOM, Persian filenames, invalid-input diagnostic and preservation of existing output. Local Python 3.13.5: 32 passed in 0.38s (rerun of exact committed formatting); exact translator blob dc495ca2bf2484a28fa9aa440e7868ea6932254c matched main. Independent expected mnemonics (not instruction_catalog). Test source blob edb2a8802b92f9762dfdeb07b70dec9ee595f84e matches the rerun local test. Reproduce from repository root: `python -m pytest -q tests/test_translator_address_matrix.py`. Test-only branch quality/academic-address-matrix; no translator/runtime changes. PR #15 exact-head CI 45557009008 remains queued at inspection; no changes to its head, no release or installer. These results validate the documented provisional dialect, not arbitrary textbook microoperations or instructor-specific input grammar.

فارسی: هر ۴۰۹۶ آدرس حافظه برای هفت دستور حافظه‌ای در دو حالت مستقیم و غیرمستقیم آزمایش شد. دستورات بدون آدرس، ورودی با نام فایل فارسی و BOM، و حفظ خروجی قبلی هنگام خطا نیز بررسی شدند. مترجم اصلی همچنان تنها فایل موردنیاز برای دفاع است؛ قواعد ورودی استاد هنوز باید تأیید شوند.
