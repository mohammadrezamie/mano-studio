"""Build a conservative Qt upstream notice review inventory, not legal clearance.

Only reads regular files from hash-pinned source archives; never extracts code.
Retains original attribution bytes including malformed upstream JSON.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
import zipfile
import io
import re

SOURCE_SHA = "e8ad1e1e7c1ca7b7e5e793e54007fe85ad1e3ed95b215c4dba507c8feb9ef129"
MODULES = {
    "qtbase/qtbase-everywhere-src-6.12.0.tar.xz": "a951bd163c7b80fc6b8c88d7668fb56abf91c152373e13c10666763238131307",
    "qtsvg/qtsvg-everywhere-src-6.12.0.tar.xz": "e4ab39534ec97987b1b9b60ef7f4d3253d5912a69f8c713a01753174a4029331",
    "qtimageformats-everywhere-src-6.12.0.tar.xz": "0943132b5db8de6b6a7f1d162682173e8763c7ed94e80fd39113292845f67762",
    "pyside/pyside-setup-everywhere-src-6.12.0.tar.xz": "099c1a597cf33c1b000e11cf68a0b82d216fb802bf81726efc720394f10c7751",
    "qtshadertools/qtshadertools-everywhere-src-6.12.0.tar.xz": "c7d84f436e1aaef39fdcadebf2bd71bdf24dc69497e13f2e0198873cbbfea2ab",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(name):
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts or "\\" in name or any(":" in x for x in p.parts):
        raise ValueError("Unsafe archive path: " + name)
    return p


def inventory(raw):
    # First pass preserves attribution documents and finds explicitly referenced
    # notice paths; second pass retains those and broadly named notice files.
    attributions, references, files, warnings = {}, set(), {}, []
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r|xz") as tar:
        for member in tar:
            if not member.isfile() or PurePosixPath(member.name).name != "qt_attribution.json":
                continue
            p = safe_path(member.name)
            data = tar.extractfile(member).read()
            if str(p) in attributions:
                raise ValueError("Duplicate attribution path")
            attributions[str(p)] = data
            try:
                doc = json.loads(data)
            except ValueError:
                warnings.append({"path": str(p), "kind": "invalid_json_original_retained"})
                try:
                    doc = json.loads(data, strict=False)
                except ValueError:
                    continue
            rows = doc if isinstance(doc, list) else [doc]
            for row in rows:
                if not isinstance(row, dict):
                    warnings.append({"path": str(p), "kind": "invalid_entry"})
                    continue
                ref = row.get("LicenseFile")
                if not isinstance(ref, str) or not ref:
                    warnings.append({"path": str(p), "kind": "no_explicit_license_file", "name": row.get("Name")})
                    continue
                # Some upstream paths contain ..; normalize only within the archive root.
                parts = list(p.parent.parts)
                if ref.startswith("/") or "\\" in ref or ":" in ref:
                    warnings.append({"path": str(p), "kind": "unsupported_license_reference", "reference": ref})
                    continue
                for part in PurePosixPath(ref).parts:
                    if part == "..":
                        if len(parts) <= 1:
                            raise ValueError("License reference escapes source root")
                        parts.pop()
                    else:
                        parts.append(part)
                references.add("/".join(parts))
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r|xz") as tar:
        for member in tar:
            if not member.isfile():
                continue
            p = safe_path(member.name)
            lower = p.name.lower()
            selected = str(p) in references or str(p) in attributions or any(x.lower()=="licenses" for x in p.parts) or bool(re.match(r"^(license|licence|copying|copyright|notice)([._-]|$)", lower))
            if not selected:
                continue
            if str(p) in files:
                raise ValueError("Duplicate notice path")
            if member.size > 4*1024*1024:
                warnings.append({"path":str(p),"kind":"oversize_notice_review_required"})
                continue
            files[str(p)] = tar.extractfile(member).read()
    for ref in sorted(references - set(files)):
        warnings.append({"path":ref,"kind":"referenced_file_not_retained"})
    return files, {"attribution_files":len(attributions),"notice_files":len(files),"explicit_references":len(references),"warnings":warnings}


def build(source, output):
    source = Path(source)
    with source.open("rb") as stream:
        if hashlib.file_digest(stream,"sha256").hexdigest() != SOURCE_SHA:
            raise ValueError("Wrong source review archive")
    report = {"kind":"conservative-upstream-notice-review","source_archive_sha256":SOURCE_SHA,"applicability_review_complete":False,"redistribution_approved":False,"modules":[]}
    with zipfile.ZipFile(source) as z, zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED) as out:
        if len(z.namelist()) != len(set(z.namelist())):
            raise ValueError("Duplicate source archive paths")
        for name, expected in MODULES.items():
            raw = z.read(name)
            if digest(raw) != expected:
                raise ValueError("Wrong source module: "+name)
            files, info = inventory(raw)
            for p,data in sorted(files.items()):
                out.writestr(p,data)
            report["modules"].append({"archive":name,"sha256":expected,**info,"files":[{"path":p,"sha256":digest(data)} for p,data in sorted(files.items())]})
        out.writestr("REVIEW-MANIFEST.json",json.dumps(report,indent=2,ensure_ascii=False)+"\n")
        out.writestr("README.txt","Original upstream notices for review, including non-shipped components. Not a final attribution list, complete corresponding source offer, or permission to redistribute.\n")
    return report


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_zip")
    parser.add_argument("output_zip")
    args=parser.parse_args()
    result=build(args.source_zip,args.output_zip)
    for module in result["modules"]:
        print(module["archive"],module["attribution_files"],module["notice_files"],len(module["warnings"]))
