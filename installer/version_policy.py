"""Internal build versions are not release approvals."""
import re
import sys


def allowed(version):
    return isinstance(version, str) and (re.fullmatch(r"1\.0\.[1-9][0-9]*", version) is not None or re.fullmatch(
        r"0\.[0-9]+\.[0-9]+-(dev|alpha|beta|rc)(\.[0-9]+)?", version) is not None)


if __name__ == "__main__":
    if len(sys.argv) != 2 or not allowed(sys.argv[1]):
        raise SystemExit("Expected a supported internal candidate version")
