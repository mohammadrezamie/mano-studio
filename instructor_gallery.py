"""Create a local, bilingual visual review index without remote assets."""
from html import escape
from pathlib import Path


SURFACES = (
    ('workspace-1360', 'Large workspace', 'محیط اصلی بزرگ'),
    ('workspace-1024', 'Compact workspace', 'محیط اصلی کوچک'),
    ('splash', 'Startup screen', 'صفحه آغازین'),
)


def gallery_html(records):
    images = {row['image']: row for row in records}
    sections = []
    links = []
    for theme in ('dark', 'light', 'night'):
        for style in ('glass', 'plain'):
            section = f'{theme}-{style}'
            title = f'{theme.title()} / {style.title()}'
            links.append(f'<a href="#{section}">{title}</a>')
            panels = []
            for surface, en, fa in SURFACES:
                figures = []
                for language, label in (('en', 'English'), ('fa', 'فارسی')):
                    name = f'{language}-{section}-{surface}.png'
                    row = images[name]
                    caption = escape(f'{label} · {row["width"]} × {row["height"]}')
                    figures.append(f'<figure><a href="{name}"><img src="{name}" loading="lazy" alt="{escape(en)} — {escape(label)}"></a><figcaption>{caption}</figcaption></figure>')
                panels.append(f'<h3>{en} <span lang="fa" dir="rtl">— {fa}</span></h3><div class="pair">{"".join(figures)}</div>')
            sections.append(f'<section id="{section}"><h2>{title}</h2>{"".join(panels)}<a href="#top">Back to top</a></section>')
    return """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mano Studio — visual evidence</title>
<style>
*{box-sizing:border-box}body{max-width:1500px;margin:auto;padding:24px;background:#111827;color:#e5e7eb;font:16px system-ui,sans-serif}
a{color:#93c5fd}nav{display:flex;flex-wrap:wrap;gap:16px}section{border-top:1px solid #475569;margin-top:28px;padding-top:12px}
.pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}figure{margin:0;background:#1f2937;padding:8px;border-radius:8px}img{width:100%;height:auto;display:block}figcaption{padding-top:8px}
@media(max-width:760px){.pair{grid-template-columns:1fr}body{padding:12px}}a:focus-visible{outline:3px solid #fbbf24;outline-offset:3px}
</style><body id="top"><h1>Mano Studio — instructor visual evidence</h1><p>Actual Qt offscreen captures. Select an image for its original size. Native Windows acceptance remains separate.</p><p lang="fa" dir="rtl">تصاویر واقعی محیط برنامه؛ برای مشاهده در اندازه اصلی روی تصویر بزنید. تأیید نهایی روی ویندوز جداگانه انجام می‌شود.</p><nav>""" + ''.join(links) + '</nav>' + ''.join(sections) + '</body></html>'


def write_gallery(root, records):
    path = Path(root) / 'index.html'
    path.write_text(gallery_html(records), encoding='utf-8')
    return path
