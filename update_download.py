"""Explicit download of an official GitHub asset, without executing it.

The release's SHA-256 digest detects corruption; it is not a publisher
signature. No startup networking, automatic installation, or arbitrary URLs.
"""
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

REPO = "mohammadrezamie/mano-studio"
MAX_SIZE = 512 * 1024 * 1024
HOSTS = {"github.com", "release-assets.githubusercontent.com", "objects.githubusercontent.com"}


@dataclass(frozen=True)
class Asset:
    url: str
    name: str
    size: int
    digest: str


def asset_from_release(tag, item):
    """Accept only an exact named Windows x64 setup with GitHub SHA-256."""
    if not isinstance(tag, str) or not re.fullmatch(r"v?[0-9]+\.[0-9]+\.[0-9]+(?:-(?:dev|alpha|beta|rc)(?:\.[0-9]+)?)?", tag):
        return None
    version = tag.removeprefix("v")
    name = f"ManoStudio-Setup-v{version}-x64.exe"
    url = f"https://github.com/{REPO}/releases/download/{tag}/{name}"
    if not isinstance(item, dict) or item.get("name") != name or item.get("browser_download_url") != url:
        return None
    size, digest = item.get("size"), item.get("digest")
    if type(size) is not int or not 0 < size <= MAX_SIZE or not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        return None
    return Asset(url, name, size, digest[7:])


def allowed_url(url):
    p = urlsplit(url)
    return p.scheme == "https" and p.hostname in HOSTS and p.username is None and p.password is None and p.port in (None, 443)


class SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not allowed_url(newurl):
            raise ValueError("Untrusted download redirect")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(asset, destination, *, explicit=False, opener=None):
    if not explicit:
        raise PermissionError("Download requires explicit consent")
    if not isinstance(asset, Asset):
        raise ValueError("No verified asset metadata")
    prefix=f"https://github.com/{REPO}/releases/download/"
    if not asset.url.startswith(prefix):
        raise ValueError("Untrusted download source")
    tag=asset.url[len(prefix):].split("/",1)[0]
    if asset_from_release(tag, {"name":asset.name,"browser_download_url":asset.url,"size":asset.size,"digest":"sha256:"+asset.digest}) != asset:
        raise ValueError("Invalid asset metadata")
    path=Path(destination)
    if path.suffix.lower()!=".exe":
        raise ValueError("Expected EXE destination")
    if path.exists():
        raise FileExistsError("Choose a new filename")
    opener=opener or build_opener(SafeRedirect()).open
    temp=None
    try:
        with opener(Request(asset.url,headers={"User-Agent":"ManoStudio-UpdateDownload"}),timeout=15) as response:
            if not allowed_url(response.geturl()):
                raise ValueError("Untrusted download response")
            with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as stream:
                temp=Path(stream.name)
                h=hashlib.sha256()
                count=0
                while True:
                    chunk=response.read(65536)
                    if not chunk:
                        break
                    count+=len(chunk)
                    if count>asset.size:
                        raise ValueError("Download exceeds expected size")
                    h.update(chunk)
                    stream.write(chunk)
                if count!=asset.size or h.hexdigest()!=asset.digest:
                    raise ValueError("Download integrity check failed")
        # Hard-link creation fails if destination already exists. Never overwrite.
        os.link(temp,path)
        return path
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)
