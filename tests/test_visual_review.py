import hashlib
import json
import struct
import zlib

import pytest

from learning_catalog import TOOLS
from visual_review import build_gallery,validate_routes


def png():
    # Actual 1x1 grayscale PNG, used only for a deterministic integrity fixture.
    def chunk(kind,data):
        payload=kind+data
        return struct.pack(">I",len(data))+payload+struct.pack(">I",zlib.crc32(payload))
    return (b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",1,1,8,0,0,0,0))
            +chunk(b"IDAT",zlib.compress(b"\x00\x00"))+chunk(b"IEND",b""))


@pytest.fixture
def captures(tmp_path):
    rows=[];data=png()
    for language in ("en","fa"):
        for t in TOOLS:
            name=f"{language}-dark-route-{t.lab}-{t.route}.png"
            (tmp_path/name).write_bytes(data)
            rows.append(dict(entry=t.id,chapter=t.chapter,language=language,theme="dark",lab=t.lab,
                             route=t.route,image=name,width=1,height=1,sha256=hashlib.sha256(data).hexdigest()))
    return tmp_path,{"entries":rows}


def test_offline_gallery(captures):
    root,manifest=captures
    (root/"route-manifest.json").write_text(json.dumps(manifest),encoding="utf-8")
    assert len(validate_routes(root,manifest))==2*len(TOOLS)
    html=build_gallery(root).read_text(encoding="utf-8")
    assert 'id="ch13"' in html and 'lang="fa" dir="rtl"' in html
    assert "Offscreen CI evidence only" in html
    assert '<script' not in html and 'https://' not in html
    assert html.count('loading="lazy"')==2*len(TOOLS)


@pytest.mark.parametrize("defect",["missing","duplicate","wrong-route","wrong-image","hash","size","missing-file"])
def test_reject_invalid_evidence(captures,defect):
    root,manifest=captures;rows=manifest["entries"]
    if defect=="missing":rows.pop()
    elif defect=="duplicate":rows.append(rows[0])
    elif defect=="wrong-route":rows[0]["route"]="unknown"
    elif defect=="wrong-image":rows[0]["image"]="../bad.png"
    elif defect=="hash":rows[0]["sha256"]="bad"
    elif defect=="size":rows[0]["width"]=2
    else:(root/rows[0]["image"]).unlink()
    with pytest.raises((ValueError,FileNotFoundError)):validate_routes(root,manifest)
