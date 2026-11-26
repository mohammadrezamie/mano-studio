# Academic handoff contingency — Monday 30 November 2026

**Purpose:** preserve the instructor's requested single-file RTL-to-Assembly deliverable if the Windows public-release gates are not all cleared by class. This is an academic source-only demonstration, NOT a replacement public release, a new version, or authorization to redistribute the bundled Qt binaries.

## Exact source and test fixtures

Use the original v1 candidate root [rtl_translator.py](../../rtl_translator.py), Git blob dc495ca2bf2484a28fa9aa440e7868ea6932254c (also confirmed on this documentation branch). Copy just that file and these fixtures from this directory. Python 3.10+ must already be available on the demonstration machine; no third-party Python packages needed for this standalone exercise. The normal Windows installer remains designed to supply its own runtime without separate prerequisites.

Run from an ordinary user terminal in the clean folder:

    python -I -S rtl_translator.py demo.rtl -o demo.asm

Expected: 32 lines exactly equal to demo.expected.asm, all 25 named Basic Computer instructions and seven indirect forms. The translation showcase is not an executable CPU program. Then:

    python -I -S rtl_translator.py invalid.rtl -o demo.asm

Expected exit 1, ADDRESS_RANGE and two UNSUPPORTED_RTL diagnostics, previous demo.asm unchanged. The single Python file is the conversion implementation; examples are input/output teaching material.

## Verified actual run

2026-11-26: copied source out of the successful license-bundle portable artifact 15125485979 (run 45832491036), normalized CRLF, matched exact Git blob. Copied fixtures from visual branch 0cc7c4c; local Git hashes demo.rtl 59b6f94edc84db5b92cd661b36f4dbb48a3e8779, demo.expected.asm 49c62c7b1c4e6251581d0fc812e9693aeab307ce, invalid.rtl 3c3d2dfb46fb12ae592100ba6ae52f5a7158ef18. Isolated actual CLI produced all 32 expected lines byte-for-byte, invalid run exit 1 and no output change. No GUI or Windows-native acceptance claim for this source-only check. The Python installation used in this test is the local existing interpreter.

## فارسی — ترتیب ارائه

۱. فایل rtl_translator.py را باز کنید و توضیح دهید که همه منطق تبدیل در همین فایل است.
۲. نمونه RTL را نشان دهید و تبدیل را با دستور بالا اجرا کنید.
۳. خروجی را با نمونه اسمبلی تطبیق دهید؛ آدرس‌ها هگز هستند و I حالت غیرمستقیم است.
۴. نمونه خطادار را اجرا کنید و نشان دهید فایل معتبر قبلی تغییر نمی‌کند.
۵. برای استاد توضیح دهید که این مترجم از الگوهای RTL در سطح دستورهای کامپیوتر پایه مانو پشتیبانی می‌کند، نه سنتز RTL دلخواه یا اجرای هر کلمه حافظه.
۶. در صورت آماده نبودن مجوز انتشار نصاب، نتایج آزمون‌ها و تصاویر واقعی ثبت‌شده در GitHub را جدا از فایل کد نشان دهید. نسخه عمومی را آماده اعلام نکنید.

## Release dependency

Official Python 3.14 schedule (https://peps.python.org/pep-0745/) lists 3.14.11 for 8 December 2026, after the class deadline. Schedule can change; this is not a claim that the next version contains the specific OpenSSL fix. Current published 3.14.10 (https://www.python.org/downloads/release/python-31410/) and PySide6 6.12.0 (https://pypi.org/project/PySide6/) listings do not establish a patched compatible Windows replacement. OpenSSL advisory baseline remains 3.5.10 (https://openssl-library.org/news/vulnerabilities-3.5/). Keep the security, corresponding-source/license, native clean/pre-equipped Windows acceptance and final exact-revision regression gates independent. No public release approval.
