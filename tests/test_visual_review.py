import hashlib
import json
import struct
import zlib

import pytest

from learning_catalog import TOOLS
from visual_review import (ACTIVE_STATES,BASE_CAPTURES,THEMES,build_gallery,image_info,
                           validate_active,validate_base_captures,validate_routes)


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
    active=[]
    for language in ("en","fa"):
        for route,state in ACTIVE_STATES:
            name=f"{language}-dark-active-{route}-{state}.png"
            (tmp_path/name).write_bytes(data)
            active.append(dict(language=language,theme="dark",route=route,state=state,image=name,
                               width=1,height=1,sha256=hashlib.sha256(data).hexdigest()))
    for language in ("en","fa"):
        for theme in THEMES:
            for mode in BASE_CAPTURES:
                (tmp_path/f"{language}-{theme}-{mode}.png").write_bytes(data)
        (tmp_path/f"{language}-dark-learning-center.png").write_bytes(data)
    return tmp_path,{"entries":rows,"active_states":active}


def test_offline_gallery(captures):
    root,manifest=captures
    (root/"route-manifest.json").write_text(json.dumps(manifest),encoding="utf-8")
    assert len(validate_routes(root,manifest))==2*len(TOOLS)
    html=build_gallery(root).read_text(encoding="utf-8")
    assert 'id="ch13"' in html and 'lang="fa" dir="rtl"' in html
    assert "Offscreen CI evidence only" in html
    assert '<script' not in html and 'https://' not in html
    assert len(validate_active(root,manifest))==2*len(ACTIVE_STATES)
    assert 'id="active"' in html
    assert len(validate_base_captures(root))==2*(len(THEMES)*len(BASE_CAPTURES)+1)
    assert html.count('loading="lazy"')==2*(len(TOOLS)+len(ACTIVE_STATES)+len(THEMES)*len(BASE_CAPTURES)+1)


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


@pytest.mark.parametrize("defect",["missing","duplicate","state","locale","theme","image","hash","size","missing-file"])
def test_reject_invalid_active_evidence(captures,defect):
    root,manifest=captures;rows=manifest["active_states"]
    if defect=="missing":rows.pop()
    elif defect=="duplicate":rows.append(rows[0])
    elif defect=="state":rows[0]["state"]="unknown"
    elif defect=="locale":rows[0]["language"]="xx"
    elif defect=="theme":rows[0]["theme"]="light"
    elif defect=="image":rows[0]["image"]="../bad.png"
    elif defect=="hash":rows[0]["sha256"]="bad"
    elif defect=="size":rows[0]["height"]=2
    else:(root/rows[0]["image"]).unlink()
    with pytest.raises((ValueError,FileNotFoundError)):validate_active(root,manifest)


@pytest.mark.parametrize("defect",["header-only","truncated","crc","no-end","trailing","no-data","duplicate-header"])
def test_reject_structurally_invalid_png(tmp_path,defect):
    data=png()
    if defect=="header-only":data=data[:24]
    elif defect=="truncated":data=data[:-1]
    elif defect=="crc":data=data[:29]+bytes([data[29]^1])+data[30:]
    elif defect=="no-end":data=data[:-12]
    elif defect=="trailing":data+=b"extra"
    elif defect=="no-data":data=data[:33]+data[-12:]
    else:data=data[:33]+data[8:]
    (tmp_path/"bad.png").write_bytes(data)
    with pytest.raises(ValueError):image_info(tmp_path,"bad.png")


@pytest.mark.parametrize("name",["fa-night-builder.png","en-light-alu.png","fa-dark-learning-center.png",
                                 "en-light-karnaugh-verify.png","fa-night-state-design-analysis.png",
                                 "fa-dark-state-design-reduction.png","fa-light-about.png","en-night-about.png"])
def test_require_all_base_captures(captures,name):
    root,manifest=captures
    (root/name).unlink()
    (root/"route-manifest.json").write_text(json.dumps(manifest),encoding="utf-8")
    with pytest.raises(FileNotFoundError):build_gallery(root)
