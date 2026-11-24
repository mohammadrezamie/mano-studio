from schematic_routing import wire_route, segment_hits


def test_obstacle_route():
    obstacle=(40,-20,80,20)
    points,ok=wire_route((0,0),(130,0),[obstacle])
    assert ok and points[0]==(0,0) and points[-1]==(130,0)
    assert all(not segment_hits(a,b,obstacle) for a,b in zip(points,points[1:]))


def test_blocked_route_is_flagged():
    points,ok=wire_route((0,0),(130,0),[(-2,-2,20,2)])
    assert not ok


def test_backward_route_avoids_component_bodies():
    obstacles=[(200,0,308,84),(20,0,128,84)]
    points,ok=wire_route((308,42),(20,42),obstacles)
    assert ok and all(not segment_hits(a,b,r) for a,b in zip(points,points[1:]) for r in obstacles)
