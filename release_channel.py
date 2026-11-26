"""Select only public updates belonging to the installed product channel."""
import re


def version_key(tag):
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)(?:-(dev|alpha|beta|rc)(?:\.(\d+))?)?", tag)
    if not match:
        raise ValueError("Unknown version format")
    a, b, c, stage, number = match.groups()
    return int(a), int(b), int(c), {"dev": 0, "alpha": 1, "beta": 2, "rc": 3, None: 4}[stage], int(number or 0)


def channel(version):
    return "stable" if version_key(version)[3] == 4 else "beta"


def eligible_release(item, current):
    """Return an ordered version key or None; fail closed on missing release flags."""
    installed = version_key(current)
    if not isinstance(item, dict) or item.get("draft") is not False:
        return None
    tag = item.get("tag_name")
    if not isinstance(tag, str):
        return None
    try:
        key = version_key(tag)
    except ValueError:
        return None
    if key <= installed:
        return None
    stage = key[3]
    if installed[3] == 4:
        return key if stage == 4 and item.get("prerelease") is False else None
    return key if stage in (2, 3) and item.get("prerelease") is True else None
