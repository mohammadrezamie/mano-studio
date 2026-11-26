"""Conservative source-family candidates for frozen Windows binaries; not license clearance."""
import argparse
import json
from pathlib import PurePosixPath
import re
import zipfile


QT_MODULES = {
    'core': 'qtbase', 'gui': 'qtbase', 'network': 'qtbase',
    'widgets': 'qtbase', 'opengl': 'qtbase', 'svg': 'qtsvg',
    'pdf': 'qtwebengine', 'qml': 'qtdeclarative', 'qmlmeta': 'qtdeclarative',
    'qmlmodels': 'qtdeclarative', 'qmlworkerscript': 'qtdeclarative', 'quick': 'qtdeclarative',
}
BASE_PLUGINS = {
    'generic/qtuiotouchplugin.dll', 'imageformats/qgif.dll', 'imageformats/qico.dll',
    'imageformats/qjpeg.dll', 'networkinformation/qnetworklistmanager.dll',
    'platforms/qdirect2d.dll', 'platforms/qminimal.dll', 'platforms/qoffscreen.dll',
    'platforms/qwindows.dll', 'styles/qmodernwindowsstyle.dll',
    'tls/qcertonlybackend.dll', 'tls/qopensslbackend.dll', 'tls/qschannelbackend.dll',
}
IMAGE_PLUGINS = {'qicns.dll', 'qtga.dll', 'qtiff.dll', 'qwbmp.dll', 'qwebp.dll'}


def family(relative):
    p = relative.lower()
    name = PurePosixPath(p).name
    if p == 'manostudio.exe':
        return 'pyinstaller-bootloader'
    if re.fullmatch(r'(?:api-ms-win-.*|ucrtbase|vcruntime140(?:_1)?|msvcp140(?:_[12])?)\.dll', name):
        return 'microsoft-runtime'
    if re.fullmatch(r'lib(?:ssl|crypto)-3(?:-x64)?\.dll', name):
        return 'openssl'
    if p == '_internal/libffi-8.dll':
        return 'libffi'
    if re.fullmatch(r'_internal/python(?:3|3\d{2})\.dll', p):
        return 'cpython'
    if p.startswith('_internal/') and '/' not in p[len('_internal/'):] and p.endswith('.pyd'):
        return 'cpython-extension'
    if p.startswith('_internal/shiboken6/') and name in {'shiboken.pyd', 'shiboken6.abi3.dll'}:
        return 'pyside-setup'
    if p.startswith('_internal/pyside6/'):
        leaf = p[len('_internal/pyside6/'):]
        if leaf == 'opengl32sw.dll':
            return 'software-opengl-review'
        if leaf == 'pyside6.abi3.dll' or re.fullmatch(r'qt[a-z]+\.pyd', leaf):
            return 'pyside-setup'
        match = re.fullmatch(r'qt6([a-z]+)\.dll', leaf)
        if match:
            return QT_MODULES.get(match.group(1), 'unmapped')
        if leaf.startswith('plugins/'):
            plugin = leaf[len('plugins/'):]
            if plugin in BASE_PLUGINS:
                return 'qtbase'
            if plugin in {'iconengines/qsvgicon.dll', 'imageformats/qsvg.dll'}:
                return 'qtsvg'
            if plugin == 'imageformats/qpdf.dll':
                return 'qtwebengine'
            if plugin.startswith('imageformats/') and name in IMAGE_PLUGINS:
                return 'qtimageformats'
    return 'unmapped'


def classify(paths):
    rows = []
    seen = set()
    for path in sorted(paths):
        if not path.startswith('ManoStudio/') or '\\' in path or '..' in path.split('/'):
            raise ValueError('Unexpected archive member')
        relative = path[len('ManoStudio/'):]
        if PurePosixPath(relative).suffix.lower() not in {'.exe', '.dll', '.pyd'}:
            continue
        if relative.lower() in seen:
            raise ValueError('Duplicate Windows binary path')
        seen.add(relative.lower())
        rows.append({'path': relative, 'source_family_candidate': family(relative)})
    if not rows:
        raise ValueError('No binaries found')
    counts = {}
    for row in rows:
        key = row['source_family_candidate']
        counts[key] = counts.get(key, 0) + 1
    return {'binary_count': len(rows), 'families': counts, 'binaries': rows,
            'unmapped_count': counts.get('unmapped', 0),
            'corresponding_source_verified': False, 'public_release_approved': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('portable_zip')
    args = parser.parse_args()
    with zipfile.ZipFile(args.portable_zip) as archive:
        result = classify(archive.namelist())
    print(json.dumps(result, indent=2))
    return 2 if result['unmapped_count'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
