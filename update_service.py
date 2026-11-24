"""Only explicit update checks may use the network; never on startup."""
import json
import re
from urllib.request import Request, urlopen

RELEASES_URL = "https://api.github.com/repos/mohammadrezamie/mano-studio/releases"
RELEASES_PAGE = "https://github.com/mohammadrezamie/mano-studio/releases"
VERSION = "0.3.0-dev"


def version_key(tag):
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)(?:-(dev|alpha|beta|rc)(?:\.(\d+))?)?", tag)
    if not match:
        raise ValueError("Unknown version format")
    a, b, c, stage, number = match.groups()
    return int(a), int(b), int(c), {"dev": 0, "alpha": 1, "beta": 2, "rc": 3, None: 4}[stage], int(number or 0)


def check_updates(*, explicit=False, opener=urlopen):
    if not explicit:
        raise PermissionError("Network access requires an explicit update check")
    request = Request(RELEASES_URL, headers={"Accept": "application/vnd.github+json", "User-Agent": "ManoStudio-UpdateCheck"})
    with opener(request, timeout=6) as response:
        data = json.loads(response.read(2_000_001))
    if not isinstance(data, list):
        raise ValueError("Invalid release response")
    candidates = []
    for item in data:
        if not isinstance(item, dict) or item.get("draft", True):
            continue
        tag = item.get("tag_name", "")
        if not isinstance(tag, str):
            continue
        try:
            key = version_key(tag)
        except ValueError:
            continue
        if key > version_key(VERSION):
            candidates.append((key, tag))
    return max(candidates)[1] if candidates else None
