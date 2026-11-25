import pytest
from ui.signal_motion import BUS_REGISTERS, bus_motion_paths, point_along, changed_routes


@pytest.mark.parametrize("source", BUS_REGISTERS)
@pytest.mark.parametrize("target", BUS_REGISTERS)
def test_bus_path_endpoints(source, target):
    stem, branch = bus_motion_paths(source, (target,))
    sx = 83 + 139 * BUS_REGISTERS.index(source)
    tx = 83 + 139 * BUS_REGISTERS.index(target)
    assert stem == ((sx, 118), (sx, 145))
    assert branch == ((sx, 145), (tx, 145), (tx, 118))
    assert point_along(branch, 0) == branch[0]
    assert point_along(branch, 1) == branch[-1]


def test_no_inferred_routes():
    assert bus_motion_paths(None, ("PC",)) == ()
    assert bus_motion_paths("unknown", ("PC",)) == ()
    assert bus_motion_paths("AR", ()) == (((83, 118), (83, 145)),)
    assert bus_motion_paths("AR", ("PC", "unknown", "PC")) == bus_motion_paths("AR", ("PC",))


@pytest.mark.parametrize("progress,expected", [(0,(0,0)),(.25,(5,0)),(.5,(10,0)),(.75,(10,5)),(1,(10,10))])
def test_arc_length(progress, expected):
    assert point_along(((0,0),(10,0),(10,0),(10,10)), progress) == expected


def test_path_bounds_and_invalid():
    assert point_along(((1,2),(3,4)), -5) == (1,2)
    assert point_along(((1,2),(3,4)), 5) == (3,4)
    assert point_along(((1,2),(1,2)), .5) == (1,2)
    with pytest.raises(ValueError):
        point_along((), 0)
    with pytest.raises(ValueError):
        point_along(((0,0),), float("nan"))


def test_changed_routes_only_and_bounded():
    routes = (("A", ((0,0),(1,0))), ("B", ((1,0),(2,0))),
              ("A", ((1,0),(1,1))), ("C", ((0,0),)))
    old, new = {"A":0,"B":1,"C":0}, {"A":1,"B":1,"C":1}
    assert changed_routes(routes, old, new) == (routes[0],routes[2])
    assert changed_routes(routes, old, new, limit=1) == (routes[0],)
    assert changed_routes(routes, new, new) == ()
    assert changed_routes(routes, None, new) == ()
    assert changed_routes(routes, {"A":0}, new) == ()
