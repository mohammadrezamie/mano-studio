import stat
from types import SimpleNamespace
import pytest
from installer.verify_installed import inventory, linked


@pytest.mark.parametrize('mode,attributes,expected', [
    (stat.S_IFDIR, 0, False),
    (stat.S_IFREG, 0, False),
    (stat.S_IFLNK, 0, True),
    (stat.S_IFDIR, stat.FILE_ATTRIBUTE_REPARSE_POINT, True),
    (stat.S_IFREG, stat.FILE_ATTRIBUTE_REPARSE_POINT, True),
])
def test_link_classification(mode, attributes, expected):
    assert linked(SimpleNamespace(st_mode=mode, st_file_attributes=attributes)) is expected


def test_linked_root_rejected(tmp_path):
    real = tmp_path / 'real'
    real.mkdir()
    alias = tmp_path / 'alias'
    try:
        alias.symlink_to(real, target_is_directory=True)
    except OSError:
        pytest.skip('Symlinks unavailable')
    with pytest.raises(ValueError, match='linked payload directory'):
        inventory(alias)


def test_directory_link_rejected_before_traversal(tmp_path):
    root = tmp_path / 'payload'
    root.mkdir()
    try:
        (root / 'loop').symlink_to(root, target_is_directory=True)
    except OSError:
        pytest.skip('Symlinks unavailable')
    with pytest.raises(ValueError, match='linked payload path'):
        inventory(root)


def test_reserved_uninstaller_directory(tmp_path):
    (tmp_path / 'UNINS000.EXE').mkdir()
    with pytest.raises(ValueError, match='Uninstaller path cannot be a directory'):
        inventory(tmp_path)


def test_nested_regular_files(tmp_path):
    (tmp_path / 'nested').mkdir()
    (tmp_path / 'nested' / 'a').write_bytes(b'a')
    assert set(inventory(tmp_path)) == {'nested/a'}
