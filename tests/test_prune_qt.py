import pytest
from installer.prune_qt import prune


@pytest.fixture
def tree(tmp_path):
    for name in ('ManoStudio.exe', 'Qt6VirtualKeyboard.dll', 'plugins/qtvirtualkeyboardplugin.dll', 'Qt6Core.dll'):
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b'fixture')
    return tmp_path


def test_prune_only_targets(tree):
    assert prune(tree, lambda p: []) == ['Qt6VirtualKeyboard.dll', 'plugins/qtvirtualkeyboardplugin.dll']
    assert (tree / 'Qt6Core.dll').is_file()
    assert (tree / 'ManoStudio.exe').is_file()
    assert prune(tree, lambda p: []) == []


def test_dependency_blocks_all_removal(tree):
    with pytest.raises(ValueError, match='Retained binary imports'):
        prune(tree, lambda p: ['QT6VIRTUALKEYBOARD.DLL'])
    assert (tree / 'Qt6VirtualKeyboard.dll').is_file()
    assert (tree / 'plugins/qtvirtualkeyboardplugin.dll').is_file()


def test_unexpected_payload_blocks_removal(tree):
    (tree / 'qtvirtualkeyboard.qml').write_text('fixture')
    with pytest.raises(ValueError, match='Unexpected'):
        prune(tree, lambda p: [])
    assert (tree / 'Qt6VirtualKeyboard.dll').is_file()


def test_wrong_root(tmp_path):
    with pytest.raises(ValueError, match='Not a frozen'):
        prune(tmp_path, lambda p: [])
