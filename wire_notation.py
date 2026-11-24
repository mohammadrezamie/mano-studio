"""Net-aware schematic geometry. Never infer electrical connections from pixels.

Coordinates are scene units. A crossing between two different signals is not
a connection; a shared branch of a single net receives a junction dot.
"""
from collections import defaultdict


def _segments(routes):
    for net, points in routes:
        for a,b in zip(points,points[1:]):
            if a==b:
                continue
            if a[0]!=b[0] and a[1]!=b[1]:
                raise ValueError("Expected orthogonal segment")
            yield net, *sorted((tuple(a),tuple(b)))


def analyze_wires(routes):
    """Return ((net, x, y) junctions, (x, y) ambiguous-contact markers).

    A normal perpendicular interior crossing of different nets is allowed.
    Collinear contact/overlap and different-net endpoint contacts are flagged.
    A junction crossed by another net is flagged and its dot suppressed.
    """
    segments=list(dict.fromkeys(_segments(routes)))
    directions=defaultdict(set)
    conflicts=set()
    foreign_crossings=set()
    for i,(net,a,b) in enumerate(segments):
        horizontal=a[1]==b[1]
        for other,c,d in segments[i+1:]:
            other_horizontal=c[1]==d[1]
            if horizontal==other_horizontal:
                axis=0 if horizontal else 1
                fixed=1-axis
                if a[fixed]!=c[fixed]:
                    continue
                lo=max(a[axis],c[axis])
                hi=min(b[axis],d[axis])
                if lo>hi or net==other:
                    continue
                middle=(lo+hi)/2
                conflicts.add((middle,a[fixed]) if horizontal else (a[fixed],middle))
                continue
            h0,h1,v0,v1=(a,b,c,d) if horizontal else (c,d,a,b)
            point=(v0[0],h0[1])
            if not h0[0]<=point[0]<=h1[0] or not v0[1]<=point[1]<=v1[1]:
                continue
            if net!=other:
                foreign_crossings.add(point)
                if point in (a,b,c,d):
                    conflicts.add(point)
                continue
            x,y=point
            branch=directions[(net,x,y)]
            if h0[0]<x:branch.add("L")
            if h1[0]>x:branch.add("R")
            if v0[1]<y:branch.add("U")
            if v1[1]>y:branch.add("D")
    junctions=set()
    for net,x,y in directions:
        if len(directions[(net,x,y)])>=3:
            if (x,y) in foreign_crossings:
                conflicts.add((x,y))
            else:
                junctions.add((net,x,y))
    return tuple(sorted(junctions)),tuple(sorted(conflicts))
