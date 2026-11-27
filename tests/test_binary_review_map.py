import hashlib
import io
import json
import zipfile

import pytest
from installer.binary_review_map import category, map_payload, compare


def fixture(files, tamper=False):
    out = io.BytesIO()
    inventory = {"kind":"build-license-evidence", "packages": [], "warnings": [],
                 "binaries":[{"path":name, "size":len(data),
                              "sha256":hashlib.sha256(data).hexdigest()}
                             for name, data in files.items()]}
    with zipfile.ZipFile(out, "w") as z:
        for name, data in files.items():
            z.writestr("ManoStudio/"+name, data + (b"x" if tamper else b""))
        z.writestr("ManoStudio/third-party-notices/inventory.json", json.dumps(inventory))
    out.seek(0)
    return zipfile.ZipFile(out)


@pytest.mark.parametrize("path,group", [
    ("ManoStudio.exe","pyinstaller/application"),
    ("_internal/PySide6/Qt6Qml.dll","qtdeclarative"),
    ("_internal/PySide6/plugins/imageformats/qwebp.dll","qtimageformats"),
    ("_internal/PySide6/plugins/iconengines/qsvgicon.dll","qtsvg"),
    ("_internal/PySide6/QtCore.pyd","pyside-shiboken"),
    ("_internal/shiboken6/Shiboken.pyd","pyside-shiboken"),
    ("_internal/PySide6/MSVCP140.dll","microsoft-runtime"),
    ("_internal/libssl-3.dll","openssl"),
    ("_internal/libffi-8.dll","libffi"),
    ("_internal/PySide6/opengl32sw.dll","qt-opengl-software-review"),
    ("_internal/PySide6/Qt6Core.dll","qtbase-candidate-review"),
    ("_internal/python314.dll","cpython"),
    ("_internal/unexpected.dll","unmapped"),
])
def test_review_groups(path, group):
    assert category(path) == group


def test_map_and_comparison():
    with fixture({"ManoStudio.exe":b"one","_internal/old.dll":b"old"}) as a:
        old = map_payload(a)
    with fixture({"ManoStudio.exe":b"two","_internal/new.dll":b"new"}) as b:
        new = map_payload(b)
    result = compare(old,new)
    assert result["changed"] == ["ManoStudio.exe"]
    assert result["added"] == ["_internal/new.dll"]
    assert result["removed"] == ["_internal/old.dll"]
    assert new["groups"]["unmapped"] == 1
    assert not result["public_release_approved"]


def test_invalid_payload_rejected():
    with fixture({"ManoStudio.exe":b"one"}, tamper=True) as archive:
        with pytest.raises(ValueError,match="Binary evidence mismatch"):
            map_payload(archive)
