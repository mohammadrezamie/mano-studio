from wire_notation import analyze_wires

def test_same_net_branch():
    dots,conflicts=analyze_wires([("A",((0,0),(100,0))),("A",((50,0),(50,40)))])
    assert dots==(("A",50,0),) and not conflicts

def test_different_net_interior_crossing():
    assert analyze_wires([("A",((0,0),(100,0))),("B",((50,-40),(50,40)))])==((),())

def test_different_net_touch_or_overlap():
    dots,conflicts=analyze_wires([("A",((0,0),(100,0))),("B",((40,0),(60,0)))])
    assert not dots and conflicts==((50,0),)
    dots,conflicts=analyze_wires([("A",((0,0),(100,0))),("B",((50,0),(50,40)))])
    assert not dots and conflicts==((50,0),)

def test_plain_bend_not_junction():
    assert analyze_wires([("A",((0,0),(50,0),(50,40)))])==((),())

def test_shared_net_four_way():
    dots,conflicts=analyze_wires([("A",((0,0),(100,0))),("A",((50,-40),(50,40)))])
    assert dots==(("A",50,0),) and not conflicts

def test_foreign_crossing_suppresses_ambiguous_dot():
    dots,conflicts=analyze_wires([("A",((0,0),(100,0))),("A",((50,0),(50,40))),("B",((50,-40),(50,40)))])
    assert not dots and (50,0) in conflicts
