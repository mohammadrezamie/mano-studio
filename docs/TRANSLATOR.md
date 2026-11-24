# Translator / راهنمای دفاع
Run `python rtl_translator.py examples/add.rtl -o result.asm` with Python 3.10+. No runtime dependencies. Run `python -m pip install -r requirements-dev.txt` then `python -m pytest -q`.

The engine splits input into lines, removes comments, matches each full statement against 32 regular-expression rules (25 mnemonics plus seven indirect variants), validates and pads hexadecimal addresses, then returns instructions with their source line and diagnostics. `TranslationResult.assembly` refuses export if any diagnostic exists. The CLI reads UTF-8 (including BOM), writes ASM only on success and returns nonzero on error. Existing output is left unchanged on invalid input. GUI must call `translate()` rather than implement duplicate rules.

فارسی: ابتدا متن به خطوط جدا می‌شود؛ توضیحات حذف می‌شوند؛ هر خط با الگوی کامل دستورات مقایسه می‌شود؛ آدرس حافظه بررسی شده و دستور اسمبلی ساخته می‌شود. در صورت وجود خطا خروجی جدید تولید نمی‌شود. فایل اصلی مستقل `rtl_translator.py` است. عبارت‌های RTL در این نسخه خلاصه رفتار دستور هستند، نه تمام ریزعملیات سخت‌افزاری. پشتیبانی فعلی ۲۵ دستور نام‌دار است؛ ورودی استاد هنوز تأیید نشده است.

`instruction_catalog.py` provides canonical templates for guided input, separate from the translator. Each template is tested against the same engine.
