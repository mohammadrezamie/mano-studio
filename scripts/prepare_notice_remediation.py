"""Prepare a narrowly changed internal portable review payload.

Frozen application code remains unchanged. Remove only the reviewed Mesa DLL,
add the original upstream review notice ZIP, and update the binary inventory.
This does not approve distribution, change any draft, or prove GPU support.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import zipfile

MESA = "_internal/PySide6/opengl32sw.dll"
MESA_SHA = "18aedc7a4b610f53bcc7b7a5c5ed9293c7e86f030e3273ad54ed3bb1ebd36702"
NOTICE_SHA = "e0d723b4a78cadc46609c86a14093b3840109c554a18f55b430660033b7dcc65"
NOTICE = "third-party-notices/qt-upstream"
INVENTORY = "third-party-notices/inventory.json"


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def icon_from_exe(exe, output):
    import pefile
    pe = pefile.PE(str(exe))
    try:
        types = {e.id:e for e in pe.DIRECTORY_ENTRY_RESOURCE.entries if e.id is not None}
        groups = types[14].directory.entries
        if len(groups) != 1:
            raise ValueError("Expected one original executable icon group")
        group = groups[0].directory.entries[0].data.struct
        raw = pe.get_data(group.OffsetToData, group.Size)
        reserved, kind, count = struct.unpack_from("<HHH",raw)
        if (reserved,kind)!=(0,1) or not 1<=count<=32 or len(raw)!=6+14*count:
            raise ValueError("Invalid group icon")
        images = {e.id:e for e in types[3].directory.entries}
        header, payload = bytearray(raw[:6]), bytearray()
        offset = 6+16*count
        for i in range(count):
            entry = raw[6+i*14:6+(i+1)*14]
            size, ident = struct.unpack_from("<IH",entry,8)
            resource = images[ident].directory.entries[0].data.struct
            data = pe.get_data(resource.OffsetToData,resource.Size)
            if len(data)!=size:
                raise ValueError("Icon resource size mismatch")
            header.extend(entry[:12]+struct.pack("<I",offset))
            payload.extend(data)
            offset+=size
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_bytes(header+payload)
    finally:
        pe.close()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("candidate",type=Path)
    p.add_argument("portable",type=Path)
    p.add_argument("portable_sha")
    p.add_argument("notice",type=Path)
    p.add_argument("report",type=Path)
    a=p.parse_args()
    sys.path.insert(0,str(a.candidate.resolve()))
    from installer.windows_zip_paths import validate_windows_paths
    from installer.verify_installed import inventory
    import pefile
    if sha(a.portable)!=a.portable_sha or sha(a.notice)!=NOTICE_SHA:
        raise ValueError("Wrong input archive")
    dist=a.candidate/"dist"
    if dist.exists():
        raise ValueError("Expected fresh output directory")
    with zipfile.ZipFile(a.portable) as z:
        validate_windows_paths(z,"ManoStudio/")
        if z.testzip() is not None:
            raise ValueError("Corrupt original portable")
        z.extractall(dist)
    root=dist/"ManoStudio"
    before=inventory(root)
    if before.get(MESA,{}).get("sha256")!=MESA_SHA or (root/NOTICE).exists():
        raise ValueError("Unexpected reviewed payload")
    for name in before:
        if name==MESA or Path(name).suffix.lower() not in (".exe",".pyd",".dll"):
            continue
        pe=pefile.PE(str(root/name),fast_load=True)
        try:
            pe.parse_data_directories(directories=[1,13])
            for key in ("DIRECTORY_ENTRY_IMPORT","DIRECTORY_ENTRY_DELAY_IMPORT"):
                if any(e.dll.lower()==b"opengl32sw.dll" for e in getattr(pe,key,())):
                    raise ValueError("Retained binary directly imports Mesa: "+name)
        finally:
            pe.close()
    inv_path=root/INVENTORY
    inv=json.loads(inv_path.read_text(encoding="utf-8-sig"))
    rows=inv["binaries"]
    matches=[x for x in rows if x["path"]==MESA and x["sha256"]==MESA_SHA]
    if len(matches)!=1 or len([x for x in rows if x["path"]==MESA])!=1:
        raise ValueError("Mesa inventory mismatch")
    (root/MESA).unlink()
    inv["binaries"]=[x for x in rows if x["path"]!=MESA]
    inv_path.write_text(json.dumps(inv,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    from expand_qt_notices import expand
    notice_count = expand(a.notice, root/NOTICE)
    if notice_count != 236:
        raise ValueError('Unexpected notice count')
    expected_additions = {str(p.relative_to(root)).replace('\\', '/') for p in (root/NOTICE).rglob('*') if p.is_file()}
    if len(expected_additions) != notice_count + 2:
        raise ValueError('Unexpected expanded notice membership')
    after=inventory(root)
    removed=set(before)-set(after)
    added=set(after)-set(before)
    changed={k for k in set(before)&set(after) if before[k]!=after[k]}
    if (removed,added,changed)!=({MESA},expected_additions,{INVENTORY}):
        raise ValueError("Unintended payload change")
    icon_from_exe(root/"ManoStudio.exe",a.candidate/"build/mano-studio.ico")
    report={"kind":"internal-notice-remediation-pilot","original_portable_sha256":a.portable_sha,
        "removed":{k:before[k] for k in removed},"added":{k:after[k] for k in added},
        "changed":{k:{"before":before[k],"after":after[k]} for k in changed},
        "unchanged_files":len(before)-len(removed)-len(changed),"original_application_sha256":before["ManoStudio.exe"]["sha256"],
        "native_gpu_acceptance":False,"redistribution_approved":False,"public_release_approved":False}
    a.report.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
