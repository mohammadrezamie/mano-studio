import pytest
from installer.prune_pdf import TARGETS, plan, apply


@pytest.fixture
def tree(tmp_path):
    for relative in TARGETS | {'ManoStudio.exe', '_internal/PySide6/Qt6Core.dll'}:
        p = tmp_path / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b'fixture')
    return tmp_path


def test_plan_and_apply(tree):
    report = plan(tree, lambda p: [])
    assert report['removed_bytes'] == 14 and not report['public_release_approved']
    assert all((tree / p).exists() for p in TARGETS)
    assert apply(tree, lambda p: []) == report
    assert not any((tree / p).exists() for p in TARGETS)
    assert (tree / 'ManoStudio.exe').exists()


@pytest.mark.parametrize('dll', ['QT6PDF.DLL', 'qpdf.dll'])
def test_retained_import_blocks_all(tree, dll):
    with pytest.raises(ValueError, match='Retained binary'):
        apply(tree, lambda p: [dll])
    assert all((tree / p).exists() for p in TARGETS)


@pytest.mark.parametrize('relative', ['other/Qt6Pdf.dll', '_internal/PySide6/QtPdf.pyd', '_internal/PySide6/Qt6PdfWidgets.dll'])
def test_unexpected_payload(tree, relative):
    p = tree / relative
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b'fixture')
    with pytest.raises(ValueError):
        apply(tree, lambda p: [])
    assert all((tree / p).exists() for p in TARGETS)


def test_missing_pair(tree):
    (tree / sorted(TARGETS)[0]).unlink()
    with pytest.raises(ValueError):
        apply(tree, lambda p: [])
    assert (tree / sorted(TARGETS)[1]).exists()


def test_wrong_root(tmp_path):
    with pytest.raises(ValueError):
        plan(tmp_path, lambda p: [])
