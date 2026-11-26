"""Navigate 16-word memory pages without changing the CPU."""
from memory_inspector import page_addresses


def adjacent_page(address, direction):
    """Return adjacent page start, or None at a boundary; no wraparound."""
    if type(direction) is not int or direction not in (-1, 1):
        raise ValueError('Expected previous or next page')
    if address is None:
        return 0 if direction == 1 else None
    start = page_addresses(address)[0] + 16 * direction
    return start if 0 <= start < 4096 else None
