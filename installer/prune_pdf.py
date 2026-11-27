"""Opt-in lean Windows candidate: remove only the unused Qt PDF binary pair.

The dependency scan is necessary, not sufficient. Require frozen smoke and
native acceptance before promoting this experimental payload.
"""
import argparse
import hashlib
import json
from pathlib import Path

TARGETS = frozenset({'_internal/PySide6/Qt6Pdf.dll',
                     '_internal/PySide6/plugins/imageformats/qpdf.dll'})
NAMES = frozenset({'qt6pdf.dll', 'qpdf.dll'})


def plan(root, imports):
    root = Path(root)
    if not (root / 'ManoStudio.exe').is_file():
        raise ValueError('Not a frozen Mano Studio application')
    files = {p.relative_to(root).as_posix(): p for p in root.rglob('*') if p.is_file()}
    candidates = {name for name, p in files.items() if p.name.lower() in NAMES}
    if candidates != TARGETS:
        raise ValueError('Expected exact Qt PDF pair; inspect changed payload')
    if any(p.name.lower().startswith(('qtpdf', 'qt6pdfwidgets')) for p in files.values()):
        raise ValueError('Unexpected Qt PDF binding or widget dependency')
    for relative, path in sorted(files.items()):
        if relative not in TARGETS and path.suffix.lower() in {'.exe', '.dll', '.pyd'}:
            if NAMES.intersection(x.lower() for x in imports(path)):
                raise ValueError('Retained binary imports Qt PDF: ' + relative)
    rows = []
    for relative in sorted(TARGETS):
        p = files[relative]
        rows.append({'path': relative, 'size': p.stat().st_size,
                     'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    return {'kind': 'lean-qt-pdf-experiment', 'targets': rows,
            'removed_bytes': sum(row['size'] for row in rows),
            'native_acceptance': False, 'public_release_approved': False}


def apply(root, imports):
    report = plan(root, imports)
    for row in report['targets']:
        (Path(root) / row['path']).unlink()
    return report


def main():
    from installer.prune_qt import pe_imports
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    report = (apply if args.apply else plan)(args.root, pe_imports)
    report['applied'] = args.apply
    if args.apply:
        (args.root / 'lean-pdf-experiment.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
