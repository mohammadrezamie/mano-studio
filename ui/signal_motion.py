"""Pure geometry for display-only signal feedback, never hardware timing."""
from math import hypot, isfinite

BUS_REGISTERS = ("AR", "PC", "DR", "AC", "IR", "TR", "M")


def bus_motion_paths(source, targets):
    """Actual selected source stem, then only recorded destination branches."""
    if source not in BUS_REGISTERS:
        return ()
    sx = 83 + 139 * BUS_REGISTERS.index(source)
    stem = ((sx, 118), (sx, 145))
    paths = [stem]
    for target in dict.fromkeys(targets):
        if target not in BUS_REGISTERS:
            continue
        tx = 83 + 139 * BUS_REGISTERS.index(target)
        paths.append(((sx, 145), (tx, 145), (tx, 118)))
    return tuple(paths)


def point_along(points, progress):
    """Arc-length interpolation, including zero-length segments."""
    if not points or not isfinite(progress):
        raise ValueError("Invalid visual path or progress")
    p = max(0.0, min(1.0, float(progress)))
    segments = [(a, b, hypot(b[0]-a[0], b[1]-a[1]))
                for a, b in zip(points, points[1:])]
    distance = p * sum(length for _, _, length in segments)
    for a, b, length in segments:
        if length and distance <= length:
            t = distance / length
            return a[0] + (b[0]-a[0])*t, a[1] + (b[1]-a[1])*t
        distance -= length
    return points[-1]


def changed_routes(routes, previous, current, *, limit=96):
    """Emphasize only existing routes of nets with a changed evaluated bit."""
    if previous is None or previous.keys() != current.keys():
        return ()
    changed = {net for net, bit in current.items() if previous[net] != bit}
    return tuple((net, points) for net, points in routes
                 if net in changed and len(points) > 1)[:limit]
