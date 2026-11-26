import pytest
from module_sources import classify, family


@pytest.mark.parametrize('path,expected', [
    ('ManoStudio.exe', 'pyinstaller-bootloader'),
    ('_internal/python314.dll', 'cpython'),
    ('_internal/_ssl.pyd', 'cpython-extension'),
    ('_internal/libcrypto-3-x64.dll', 'openssl'),
    ('_internal/PySide6/Qt6Core.dll', 'qtbase'),
    ('_internal/PySide6/Qt6Pdf.dll', 'qtwebengine'),
    ('_internal/PySide6/Qt6Quick.dll', 'qtdeclarative'),
    ('_internal/PySide6/plugins/imageformats/qpdf.dll', 'qtwebengine'),
    ('_internal/PySide6/plugins/imageformats/qwebp.dll', 'qtimageformats'),
    ('_internal/PySide6/plugins/imageformats/qsvg.dll', 'qtsvg'),
    ('_internal/PySide6/QtCore.pyd', 'pyside-setup'),
    ('_internal/shiboken6/Shiboken.pyd', 'pyside-setup'),
    ('_internal/PySide6/MSVCP140.dll', 'microsoft-runtime'),
    ('_internal/PySide6/opengl32sw.dll', 'software-opengl-review'),
    ('_internal/PySide6/Qt6Unknown.dll', 'unmapped'),
])
def test_family(path, expected):
    assert family(path) == expected


def test_report():
    result = classify(['ManoStudio/ManoStudio.exe', 'ManoStudio/_internal/new.dll', 'ManoStudio/README.md'])
    assert result['binary_count'] == 2 and result['unmapped_count'] == 1
    assert not result['corresponding_source_verified'] and not result['public_release_approved']


@pytest.mark.parametrize('paths', [['ManoStudio/A.dll', 'ManoStudio/a.DLL'], ['Other/A.dll'], ['ManoStudio/../x.dll'], ['ManoStudio/README.md']])
def test_invalid(paths):
    with pytest.raises(ValueError):
        classify(paths)
