"""Release metadata; network checks require manual or opt-in UI authorization."""
from dataclasses import dataclass
import json
from release_channel import version_key, channel, eligible_release
from urllib.request import Request, HTTPRedirectHandler, build_opener
from update_download import Asset, asset_from_release

RELEASES_URL = "https://api.github.com/repos/mohammadrezamie/mano-studio/releases"
RELEASES_PAGE = "https://github.com/mohammadrezamie/mano-studio/releases"
VERSION = "1.0.1"
CHANNEL = channel(VERSION)


@dataclass(frozen=True)
class ReleaseInfo:
    tag: str
    notes: str
    installer_size: int | None
    asset: Asset | None = None


class NoMetadataRedirect(HTTPRedirectHandler):
    """Metadata must come directly from the configured official API endpoint."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Unexpected release metadata redirect")


def release_info(*, explicit=False, opener=None):
    if not explicit:
        raise PermissionError("Network access requires an explicit update check")
    request = Request(RELEASES_URL, headers={"Accept": "application/vnd.github+json", "User-Agent": "ManoStudio-UpdateCheck"})
    opener = opener if opener is not None else build_opener(NoMetadataRedirect()).open
    with opener(request, timeout=6) as response:
        payload = response.read(2_000_001)
    return parse_release_payload(payload)


def parse_release_payload(payload):
    """Shared bounded metadata parser; performs no network requests."""
    if len(payload) > 2_000_000:
        raise ValueError("Release response too large")
    data = json.loads(payload)
    if not isinstance(data, list):
        raise ValueError("Invalid release response")
    candidates = []
    for item in data:
        key = eligible_release(item, VERSION)
        if key is None:
            continue
        tag = item["tag_name"]
        notes = item.get("body")
        notes = notes[:8000] if isinstance(notes, str) else ""
        assets = item.get("assets", [])
        size = None
        asset = None
        # Metadata only: never trust a release asset as an executable.
        # A single setup asset gives an indicative download size.
        if isinstance(assets, list):
            setups = [a for a in assets if isinstance(a, dict)
                      and isinstance(a.get("name"), str)
                      and a["name"].lower().startswith("manostudio")
                      and "setup" in a["name"].lower()
                      and a["name"].lower().endswith(".exe")
                      and type(a.get("size")) is int and a["size"] > 0]
            if len(setups) == 1:
                size = setups[0]["size"]
                asset = asset_from_release(tag, setups[0])
        candidates.append((key, ReleaseInfo(tag, notes, size, asset)))
    return max(candidates, key=lambda candidate: candidate[0])[1] if candidates else None


def check_updates(*, explicit=False, opener=None):
    """Compatibility API for callers needing only the version tag."""
    release = release_info(explicit=explicit, opener=opener)
    return release.tag if release else None

