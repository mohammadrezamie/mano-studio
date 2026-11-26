"""Exact instructor-capture coverage, using the shared PNG integrity reader."""
from pathlib import Path


def expected_captures():
    surfaces = {'workspace-1360': (1360, 900), 'workspace-1024': (1024, 768),
                'academic-source': None, 'splash': None}
    return {f'{language}-{theme}-{glass}-{surface}.png': size
            for language in ('en', 'fa') for theme in ('dark', 'light', 'night')
            for glass in ('glass', 'plain') for surface, size in surfaces.items()}


def validate(root, records, inspect_image=None):
    if inspect_image is None:
        from visual_review import image_info as inspect_image
    root = Path(root)
    expected = expected_captures()
    seen = set()
    for row in records:
        name = row['image']
        if name not in expected or name in seen:
            raise ValueError('Unexpected or duplicate instructor capture: ' + str(name))
        seen.add(name)
        actual = inspect_image(root, name)
        if actual != (row['width'], row['height'], row['sha256']):
            raise ValueError('Instructor capture integrity mismatch: ' + name)
        if expected[name] is not None and actual[:2] != expected[name]:
            raise ValueError('Instructor workspace does not fit requested size: ' + name)
    if seen != set(expected):
        raise ValueError('Missing instructor captures: ' + ', '.join(sorted(set(expected) - seen)))
    if {p.name for p in root.glob('*.png')} != seen:
        raise ValueError('Unexpected or missing PNG in instructor capture directory')
    return len(seen)
