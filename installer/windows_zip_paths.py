"""Validate a portable ZIP's Windows paths before auditing its payload."""
import stat

_INVALID = frozenset('<>:"\\|?*')
_RESERVED = {'CON', 'PRN', 'AUX', 'NUL', 'CONIN$', 'CONOUT$'} | {
    prefix + digit for prefix in ('COM', 'LPT') for digit in '123456789¹²³'
}


def validate_windows_paths(archive, prefix):
    """Reject ambiguous paths, aliases and special entries without extracting.

    Track implicit parent directories too, so differently cased parent names
    and file/directory conflicts cannot evade the duplicate-member check.
    Casefold is deliberately conservative, not an NTFS equivalence oracle.
    """
    nodes = {}
    explicit = set()
    for info in archive.infolist():
        name = info.filename
        if info.orig_filename != name or not name.startswith(prefix):
            raise ValueError('Unexpected archive path: ' + repr(name))
        parts = name.removesuffix('/').split('/')
        for part in parts:
            if (not part or part in ('.', '..') or part.endswith((' ', '.'))
                    or any(c in _INVALID or ord(c) < 32 for c in part)
                    or part.split('.')[0].rstrip(' ').upper() in _RESERVED):
                raise ValueError('Unsafe Windows archive path: ' + repr(name))
        mode = stat.S_IFMT(info.external_attr >> 16)
        if mode not in (0, stat.S_IFDIR if info.is_dir() else stat.S_IFREG):
            raise ValueError('Unexpected special ZIP entry: ' + repr(name))
        for depth in range(1, len(parts) + 1):
            path = '/'.join(parts[:depth])
            key = path.casefold()
            directory = depth < len(parts) or info.is_dir()
            previous = nodes.setdefault(key, (path, directory))
            if previous != (path, directory):
                raise ValueError('Ambiguous Windows archive path: ' + repr(name))
        if key in explicit:
            raise ValueError('Duplicate ZIP member: ' + repr(name))
        explicit.add(key)
