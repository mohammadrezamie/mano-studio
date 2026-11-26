"""Remove the unused Qt Virtual Keyboard from a fresh Windows frozen tree.

Static imports are a conservative check, not proof of runtime independence.
The new candidate must still pass portable and installed smoke tests.
"""
import argparse
from pathlib import Path

TARGETS = frozenset({'qt6virtualkeyboard.dll', 'qtvirtualkeyboardplugin.dll'})


def pe_imports(path):
    import pefile  # Installed by PyInstaller on Windows; build-time only.
    pe = pefile.PE(str(path), fast_load=True)
    try:
        pe.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT'],
            pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT'],
        ])
        return {entry.dll.decode('ascii').lower()
                for attr in ('DIRECTORY_ENTRY_IMPORT', 'DIRECTORY_ENTRY_DELAY_IMPORT')
                for entry in getattr(pe, attr, ())}
    finally:
        pe.close()


def prune(root, imports=pe_imports):
    root = Path(root)
    if not (root / 'ManoStudio.exe').is_file():
        raise ValueError('Not a frozen Mano Studio application')
    files = sorted(p for p in root.rglob('*') if p.is_file())
    targets = [p for p in files if p.name.lower() in TARGETS]
    if any('virtualkeyboard' in p.relative_to(root).as_posix().lower() and p not in targets for p in files):
        raise ValueError('Unexpected Virtual Keyboard payload; inspect before pruning')
    if not targets:
        return []
    for path in files:
        if path not in targets and path.suffix.lower() in ('.exe', '.dll', '.pyd'):
            if TARGETS.intersection(name.lower() for name in imports(path)):
                raise ValueError('Retained binary imports Virtual Keyboard: ' + str(path))
    removed = [p.relative_to(root).as_posix() for p in targets]
    for path in targets:
        path.unlink()
    return removed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frozen_root')
    args = parser.parse_args()
    for path in prune(args.frozen_root):
        print('Removed unused Qt Virtual Keyboard payload:', path)


if __name__ == '__main__':
    main()
