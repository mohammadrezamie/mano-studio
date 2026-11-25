"""Offline developer-only gallery and integrity checks for actual Qt captures.

No network requests, no runtime UI dependency, no visual acceptance claims.
"""
import hashlib
import html
import json
from pathlib import Path
import struct
import zlib

from learning_catalog import CHAPTERS, TOOLS

LANGUAGES=("en","fa")
THEMES=("dark","light","night")
BASE_CAPTURES=("editor","pad","builder","reverse","logic","logic-edit",
               "sequential","computer","debugger","alu","bases",
               "karnaugh-corners","karnaugh-synthesized","state-design-clock",
               "karnaugh-verify","state-design-analysis","state-design-reduction")


def validate_base_captures(root):
    """Fail if a three-theme workflow or either Learning Center image is absent."""
    root=Path(root)
    names={f"{language}-{theme}-{mode}.png" for language in LANGUAGES
           for theme in THEMES for mode in BASE_CAPTURES}
    names.update(f"{language}-dark-learning-center.png" for language in LANGUAGES)
    return {name:image_info(root,name) for name in sorted(names)}

# Shared contract for each asserted demonstration, not a claim of visual acceptance.
ACTIVE_STATES=(
    ("live","fetch"), ("sequential","clocked"), ("cache","conflict"),
    ("virtual-memory","fault-reload"), ("serial","parity-error"),
    ("crossbar","parallel-grants"), ("synchronization","lost-update"),
    ("synchronization","atomic-lock"),
)


def validate_active(root,manifest):
    """Require exactly one verified active-state screenshot for each locale and scenario."""
    root=Path(root)
    expected={(language,route,state) for language in LANGUAGES for route,state in ACTIVE_STATES}
    records={}
    for row in manifest["active_states"]:
        key=(row["language"],row["route"],row["state"])
        if key not in expected or key in records:
            raise ValueError("Unexpected or duplicate active state: "+str(key))
        language,route,state=key
        name=f"{language}-dark-active-{route}-{state}.png"
        if row["theme"]!="dark" or row["image"]!=name:
            raise ValueError("Incorrect active screenshot mapping: "+str(key))
        if image_info(root,name)!=(row["width"],row["height"],row["sha256"]):
            raise ValueError("Active screenshot integrity mismatch: "+name)
        records[key]=row
    if records.keys()!=expected:
        raise ValueError("Missing active-state captures")
    return records


def image_info(root,name):
    if not isinstance(name,str) or Path(name).name!=name or "/" in name or "\\" in name or not name.endswith(".png"):
        raise ValueError("Invalid screenshot filename")
    data=(root/name).read_bytes()
    # Verify the PNG chunk envelope, including CRCs and a complete end marker.
    # This is structural integrity, not pixel decoding or visual acceptance.
    if len(data)<33 or data[:8]!=b"\x89PNG\r\n\x1a\n":
        raise ValueError("Invalid PNG header: "+name)
    offset=8
    width=height=0
    seen_data=False
    ended=False
    while offset<len(data):
        if len(data)-offset<12:
            raise ValueError("Truncated PNG chunk: "+name)
        length,kind=struct.unpack_from(">I4s",data,offset)
        end=offset+12+length
        if end>len(data):
            raise ValueError("Truncated PNG payload: "+name)
        payload=data[offset+8:end-4]
        crc,=struct.unpack_from(">I",data,end-4)
        if zlib.crc32(kind+payload)!=crc:
            raise ValueError("Invalid PNG chunk CRC: "+name)
        if offset==8:
            if kind!=b"IHDR" or length!=13:
                raise ValueError("Invalid PNG IHDR: "+name)
            width,height=struct.unpack_from(">II",payload)
            if not width or not height:
                raise ValueError("Invalid PNG dimensions: "+name)
        elif kind==b"IHDR":
            raise ValueError("Duplicate PNG IHDR: "+name)
        if kind==b"IDAT" and length:
            seen_data=True
        if kind==b"IEND":
            if length or not seen_data or end!=len(data):
                raise ValueError("Invalid PNG end: "+name)
            ended=True
            break
        offset=end
    if not ended:
        raise ValueError("Missing PNG end: "+name)
    return width,height,hashlib.sha256(data).hexdigest()


def validate_routes(root,manifest):
    """Require every catalog entry and both locales, correct routing and file identity."""
    root=Path(root)
    expected={(tool.id,language):tool for tool in TOOLS for language in LANGUAGES}
    records={};verified={}
    for row in manifest["entries"]:
        key=(row["entry"],row["language"])
        if key not in expected or key in records:raise ValueError("Unexpected or duplicate route: "+str(key))
        tool=expected[key]
        if (row["chapter"],row["lab"],row["route"],row["theme"])!=(tool.chapter,tool.lab,tool.route,"dark"):
            raise ValueError("Incorrect route mapping: "+str(key))
        name=f"{key[1]}-dark-route-{tool.lab}-{tool.route}.png"
        if row["image"]!=name:raise ValueError("Incorrect screenshot filename: "+str(key))
        if name not in verified:verified[name]=image_info(root,name)
        if verified[name]!=(row["width"],row["height"],row["sha256"]):
            raise ValueError("Screenshot integrity mismatch: "+name)
        records[key]=row
    if records.keys()!=expected.keys():raise ValueError("Missing catalog route captures")
    return records


def build_gallery(root):
    root=Path(root)
    manifest=json.loads((root/"route-manifest.json").read_text(encoding="utf-8"))
    records=validate_routes(root,manifest)
    active=validate_active(root,manifest)
    base=validate_base_captures(root)
    esc=html.escape
    out=['<!doctype html><html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         '<meta http-equiv="Content-Security-Policy" content="default-src &apos;none&apos;; img-src &apos;self&apos; file:; style-src &apos;unsafe-inline&apos;; base-uri &apos;none&apos;; form-action &apos;none&apos;">',
         '<title>Mano Studio — visual review</title>',
         '<style>body{font:15px system-ui,sans-serif;margin:0;background:#101722;color:#e7eff8}main{max-width:1400px;margin:auto;padding:24px}a{color:#a9dbff}a:focus-visible{outline:3px solid #a9dbff;outline-offset:4px}h1{font-size:28px}h2{margin-top:36px}nav{display:flex;flex-wrap:wrap;gap:14px}article{border-top:1px solid #425167;padding:16px 0}h3{font-size:16px;margin:0 0 12px}.pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}figure{margin:0;min-width:0}img{width:100%;height:auto;display:block;border:1px solid #425167;border-radius:6px}figcaption{color:#c1cddd;margin-top:6px;font-size:13px}code{overflow-wrap:anywhere} @media(max-width:720px){.pair{grid-template-columns:1fr}main{padding:16px}}</style></head><body><main>',
         '<h1>Mano Studio · Actual Qt captures</h1>',
         '<p>Offscreen CI evidence only. Images are not a claim of native visual acceptance or complete textbook coverage. Click an image to inspect original pixels.</p>',
         '<p lang="fa" dir="rtl">تصاویر واقعی اجرای خودکار Qt؛ نه تأیید نهایی ظاهر ویندوز یا پوشش کامل کتاب. برای مشاهده تصویر اصلی روی آن کلیک کنید.</p>',
         f'<p>{len(TOOLS)} learning entries · {len(records)} locale mappings · {len({r["image"] for r in records.values()})} distinct route images</p>',
         '<nav aria-label="Chapters">']
    for chapter in CHAPTERS:out.append(f'<a href="#ch{chapter.number}">{chapter.number} · {esc(chapter.title[0])}</a>')
    out.append('<a href="#active">Active demonstrations</a><a href="#other">Other captures</a></nav>')
    def figure(row,title,lang):
        name=esc(row["image"],quote=True);label=esc(title,quote=True)
        return (f'<figure><a href="{name}"><img loading="lazy" src="{name}" alt="{label}" '
                f'width="{row["width"]}" height="{row["height"]}"></a>'
                f'<figcaption lang="{lang}" dir="{"rtl" if lang=="fa" else "ltr"}">{label} · '
                f'<bdi>{row["width"]} × {row["height"]}</bdi></figcaption></figure>')
    for chapter in CHAPTERS:
        out.append(f'<section id="ch{chapter.number}"><h2>{chapter.number} · {esc(chapter.title[0])} / <span lang="fa" dir="rtl">{esc(chapter.title[1])}</span></h2>')
        for tool in TOOLS:
            if tool.chapter!=chapter.number:continue
            out.append(f'<article><h3>{esc(tool.title[0])} · <span lang="fa" dir="rtl">{esc(tool.title[1])}</span></h3><div class="pair">')
            for i,lang in enumerate(LANGUAGES):out.append(figure(records[(tool.id,lang)],tool.title[i],lang))
            out.append('</div></article>')
        out.append('</section>')
    out.append('<section id="active"><h2>Active demonstrations</h2><p>Each pair follows a model-state assertion during capture; visual review remains separate.</p>')
    for route,state in ACTIVE_STATES:
        label=esc(f"{route} / {state}")
        out.append(f'<article><h3>{label}</h3><div class="pair">')
        for lang in LANGUAGES:
            out.append(figure(active[(lang,route,state)],f"{route} / {state} ({lang})",lang))
        out.append('</div></article>')
    out.append('</section>')
    out.append('<section id="other"><h2>Other actual captures</h2><div class="pair">')
    route_images={r["image"] for r in records.values()} | {r["image"] for r in active.values()}
    for path in sorted(root.glob("*.png")):
        if path.name in route_images:continue
        width,height,digest=base[path.name] if path.name in base else image_info(root,path.name)
        out.append(figure({"image":path.name,"width":width,"height":height},path.stem,"en"))
    out.append('</div></section></main></body></html>')
    target=root/"index.html"
    target.write_text("\n".join(out),encoding="utf-8")
    return target
