# Mano Studio
**Build. Translate. Simulate. Learn.**

An open-source bilingual offline desktop IDE for Morris Mano's Computer System Architecture, centered on the Basic Computer and the academic RTL-to-assembly assignment. Optional labs cover selected topics across the textbook.

**Status: Python translator supports all 25 named Mano instructions in the documented dialect; no downloadable desktop release yet.**

## Desktop development preview
```sh
python -m pip install -r requirements.txt -r requirements-dev.txt
python main.py
```
Three entry modes, three themes, Computer (assembler, CPU, reversible debugger, Data & ALU), and Digital Logic (editable combinational schematic, clocked components and waveform) are implemented. Optional canonical ASM-to-RTL import is available in the same editor. The **[Learning Center](docs/LEARNING_CENTER.md)** (Ctrl+K) connects 33 interactive learning entries across 12 of the 13 indexed chapters, with bilingual search, explicit coverage gaps and local personal practice progress. See [development candidate](docs/BUILD_CANDIDATE.md), [live Actions](https://github.com/mohammadrezamie/mano-studio/actions) and [status](docs/STATUS.md). No published release. Development artifacts are not stable releases.

## Academic assignment — فایل تکلیف استاد

**[rtl_translator.py](rtl_translator.py) — the only source file for the RTL-to-assembly assignment defense.**

این فایل مستقل، فقط الگوریتم تبدیل RTL به اسمبلی، اعتبارسنجی و خواندن/نوشتن فایل را در خود دارد. برای دفاع همین فایل را باز کنید. سایر فایل‌ها مربوط به امکانات اختیاری Mano Studio هستند و جزو این تکلیف نیستند. [راهنمای مطالعه و دفاع](docs/TRANSLATOR.md).

## Try the translator
Python 3.10+; no runtime dependencies.
```sh
python rtl_translator.py examples/add.rtl -o result.asm
python -m pip install -r requirements-dev.txt
python -m pytest -q
```
See [translator guide](docs/TRANSLATOR.md) and [supported RTL](docs/RTL.md).

## Development / continuation
Start with [AGENTS.md](AGENTS.md), [current status](docs/STATUS.md), [project specification](docs/PROJECT.md), [RTL dialect](docs/RTL.md), [roadmap](docs/ROADMAP.md), [references](docs/REFERENCES.md), [UI design](docs/UI_DESIGN.md), and [maintenance plan](docs/MAINTAINABILITY.md). Inspect open issues and PRs before making changes. Keep the translator independent of the GUI and update STATUS.md each time.

## فارسی
مانو استودیو محیط توسعه آموزشی معماری موریس مانو با هدف تبدیل RTL به اسمبلی، ساخت بصری برنامه و شبیه‌سازی پردازنده است. رابط فارسی و انگلیسی و نصب‌کننده مستقل ویندوز در برنامه توسعه قرار دارند. هسته مترجم از هر ۲۵ دستور نام‌دار مانو با قواعد ورودی مستندشده پشتیبانی می‌کند. برای ادامه توسعه کافی است ریپوی Mano Studio را در گیت‌هاب باز کنید و AGENTS.md و docs/STATUS.md را بخوانید. پروژه را از ابتدا شروع نکنید.

## License
MIT — see LICENSE.

## Current UX plan
[Integrated UX development plan](docs/UX_PLAN.md): keep the primary RTL-to-ASM workflow simple; combine CPU tools into one Computer workspace and share the digital logic canvas. No installer or release activity until the owner asks.
