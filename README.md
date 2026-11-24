# Mano Studio
**Build. Translate. Simulate. Learn.**

An open-source bilingual desktop IDE for Morris Mano's Basic Computer. Planned: visual RTL builder, RTL-to-Assembly translator, assembler, CPU simulator and Windows installer.

**Status: initial Python translator implemented; no downloadable desktop release yet.**

## Try the translator
Python 3.10+; no runtime dependencies.
```sh
python rtl_translator.py examples/add.rtl -o result.asm
python -m pip install -r requirements-dev.txt
python -m pytest -q
```
See [translator guide](docs/TRANSLATOR.md) and [supported RTL](docs/RTL.md).

## Development / continuation
Start with [AGENTS.md](AGENTS.md), [current status](docs/STATUS.md), [project specification](docs/PROJECT.md), [RTL dialect](docs/RTL.md), [roadmap](docs/ROADMAP.md), and [references](docs/REFERENCES.md). Inspect open issues and PRs before making changes. Keep the translator independent of the GUI and update STATUS.md each time.

## فارسی
مانو استودیو محیط توسعه آموزشی معماری موریس مانو با هدف تبدیل RTL به اسمبلی، ساخت بصری برنامه و شبیه‌سازی پردازنده است. رابط فارسی و انگلیسی و نصب‌کننده مستقل ویندوز در برنامه توسعه قرار دارند. هسته اولیه مترجم ساخته شده است. برای ادامه توسعه کافی است ریپوی Mano Studio را در گیت‌هاب باز کنید و AGENTS.md و docs/STATUS.md را بخوانید. پروژه را از ابتدا شروع نکنید.

## License
MIT — see LICENSE.
