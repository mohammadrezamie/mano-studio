"""Shared localization of domain errors without coupling the engines to Qt."""
import re

EXACT = {
    "Content after END":"پس از END نباید دستور دیگری باشد.",
    "Label outside memory":"برچسب خارج از حافظه است.",
    "ORG requires an unlabeled 12-bit hexadecimal address":"ORG به آدرس هگزادسیمال ۱۲ بیتی بدون برچسب نیاز دارد.",
    "END takes no operands or label":"END عملوند یا برچسب نمی‌پذیرد.",
    "Address outside 000–FFF":"آدرس خارج از محدوده 000 تا FFF است.",
    "Overlapping memory address":"این آدرس حافظه قبلاً اشغال شده است.",
    "Expected address or label, optionally followed by I":"آدرس یا برچسب و در صورت نیاز I وارد کنید.",
    "Constant outside 16-bit range":"ثابت خارج از محدوده ۱۶ بیتی است.",
    "Input must be an 8-bit value":"ورودی باید مقدار ۸ بیتی باشد.",
    "Input register already contains unread data":"ثبات ورودی هنوز داده خوانده‌نشده دارد.",
    "Use a signal name with 1–24 letters, digits or underscores, starting with a letter.":"نام سیگنال باید ۱ تا ۲۴ نویسه انگلیسی، رقم یا زیرخط داشته باشد و با حرف آغاز شود.",
    "Circuit size outside supported limits (1–10 inputs, 96 gates, 1–16 outputs).":"مدار خارج از محدوده مجاز است: ۱ تا ۱۰ ورودی، حداکثر ۹۶ گیت و ۱ تا ۱۶ خروجی.",
    "Combinational feedback loop; sequential circuits require a clocked model.":"حلقه بازخورد ترکیبی مجاز نیست؛ مدار ترتیبی به مدل ساعت‌دار نیاز دارد.",
    "Unknown output pin.":"پایه خروجی ناشناخته است.",
    "Unknown gate pin.":"پایه گیت ناشناخته است.",
    "Circuit file too large.":"فایل مدار بیش از حد بزرگ است.",
    "Unsupported circuit file format.":"قالب فایل مدار پشتیبانی نمی‌شود.",
    "Expected arrays.":"ساختار آرایه مورد انتظار است.",
    "Circuit size outside supported limits.":"اندازه مدار خارج از محدوده مجاز است.",
    "Each output must be a name/source pair.":"هر خروجی باید شامل نام و سیگنال مبدأ باشد.",
    "Expected gate input array.":"آرایه ورودی‌های گیت لازم است.",
    "Invalid positions array.":"آرایه موقعیت اجزا نامعتبر است.",
    "Schematic export dimensions too large.":"ابعاد خروجی شماتیک بیش از حد بزرگ است.",
    "Cannot create SVG file.":"ساخت فایل SVG ممکن نیست.",
    "Input file too large":"فایل ورودی بیش از حد بزرگ است.",
}
PREFIX = {
    "Duplicate or reserved label: ":"برچسب تکراری یا رزروشده: ",
    "Unknown label or invalid hexadecimal address: ":"برچسب ناشناخته یا آدرس هگزادسیمال نامعتبر: ",
    "Unknown instruction: ":"دستور ناشناخته: ",
    "Duplicate signal: ":"سیگنال تکراری: ",
    "Invalid gate input count: ":"تعداد ورودی نامعتبر برای گیت: ",
    "Unconnected or unknown input: ":"ورودی بدون اتصال یا ناشناخته: ",
    "Duplicate or unconnected output: ":"خروجی تکراری یا بدون اتصال: ",
    "Invalid component position: ":"موقعیت نامعتبر جزء: ",
}

def error_text(error, fa=False):
    raw=str(error)
    if not fa:
        return raw
    if raw in EXACT:
        return EXACT[raw]
    for prefix,translation in PREFIX.items():
        if raw.startswith(prefix):
            return translation+raw[len(prefix):]
    if raw.startswith("Invalid circuit file: "):
        detail=raw[len("Invalid circuit file: "):]
        return "فایل مدار نامعتبر است. "+error_text(detail,True)
    match=re.fullmatch(r"([A-Z]+) takes no operand",raw)
    if match:
        return "دستور "+match[1]+" عملوند نمی‌پذیرد."
    match=re.fullmatch(r"Invalid (DEC|HEX) constant",raw)
    if match:
        return "ثابت "+match[1]+" نامعتبر است."
    match=re.fullmatch(r"Unsupported instruction ([0-9A-F]+) at ([0-9A-F]+)",raw)
    if match:
        return "دستور ماشین پشتیبانی‌نشده "+match[1]+" در آدرس "+match[2]
    if isinstance(error,PermissionError):
        return "اجازه دسترسی به فایل وجود ندارد."
    if isinstance(error,FileNotFoundError):
        return "فایل موردنظر یافت نشد."
    if isinstance(error,UnicodeError):
        return "رمزگذاری متن نامعتبر است؛ فایل UTF-8 انتخاب کنید."
    if isinstance(error,OSError):
        return "خواندن یا نوشتن فایل ممکن نیست. مسیر و مجوز دسترسی را بررسی کنید."
    return "عملیات ناموفق بود؛ داده‌ها و قالب ورودی را بررسی کنید."
