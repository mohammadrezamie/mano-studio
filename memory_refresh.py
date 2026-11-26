"""Plan minimal updates for a read-only memory table."""


def refresh_plan(previous, current):
    """Return (reshape, changed row indices) for ordered address/word rows."""
    if len(previous) != len(current) or any(a[0] != b[0] for a, b in zip(previous, current)):
        return True, tuple(range(len(current)))
    return False, tuple(i for i, (a, b) in enumerate(zip(previous, current)) if a[1] != b[1])


def row_for_address(rows, address):
    """Find a selected address after a page or accessed-address change."""
    return next((i for i, row in enumerate(rows) if row[0] == address), None)
