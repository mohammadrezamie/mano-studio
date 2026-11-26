# Instructor demonstration and typography review

The mandatory academic deliverable remains the unchanged 198-line [rtl_translator.py](../../rtl_translator.py), Git blob dc495ca2bf2484a28fa9aa440e7868ea6932254c. It needs Python 3.10+ and no non-standard libraries. Copy the single Python file and the three demonstration fixtures into a clean folder. Run:

    python -I -S rtl_translator.py demo.rtl -o demo.asm

Compare the result with demo.expected.asm: 32 translated instruction lines representing 25 named Basic Computer mnemonics and seven indirect forms. This is a translation showcase, NOT an executable CPU program. Then run:

    python -I -S rtl_translator.py invalid.rtl -o demo.asm

Expect one ADDRESS_RANGE and two UNSUPPORTED_RTL diagnostics, exit 1, unchanged previous valid output. Explain result records, shared regular expressions, seven memory patterns in direct/indirect modes, eighteen fixed rules, full-line matching and address range, then file I/O. This is a documented instruction-level dialect, not arbitrary RTL synthesis or binary assembly.

## فارسی
فقط فایل rtl_translator.py پیاده‌سازی مترجم است. سه فایل نمونه برای ارائه هستند. با دستور بالا، ۳۲ سطر اسمبلی شامل همه ۲۵ دستور نام‌دار و هفت حالت غیرمستقیم تولید می‌شود. این نمونه برای ترجمه است، نه اجرا روی پردازنده. نمونه نامعتبر باید بدون تغییر خروجی قبلی رد شود. برای توضیح به استاد، ساختار نتیجه، الگوهای مشترک، دستورات حافظه‌ای و ثابت، تطبیق کامل سطر، اعتبارسنجی آدرس و خواندن/نوشتن فایل را شرح دهید.

## Exact visual review — 2026-11-26
v1 candidate at 3ed419e3a37d9e233a4a908c08f9eccbbe80bf83 built and passed automated installer/portable smoke, verified SHA-256 assets and 48 actual Qt captures. All capture dimensions and hashes validated; 12 compact views at 1024×768 reviewed as a contact sheet, representative full-size Persian/English views inspected. Persian control labels appeared small. Short-lived development feature branch develop/visual-polish increases UI font size (en 10, fa 11 pt), chooses installed Arabic-supporting fonts using Qt font database and slightly increases caption/heading sizes. Code editors remain 12 pt and LTR. No bundled/downloaded fonts and no new dependency. New 12 pure typography cases and one isolated demo regression passed locally (13/13); exact Git hashes match. Real Qt compact-size tests and screenshots required before promotion. Existing v1 and next-beta running CI refs not modified. No auto-merge.
