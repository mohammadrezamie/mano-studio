"""Orthogonal schematic wire routing for manually positioned components.

Coordinates are continuous scene units. Try short routes first; if blocked,
try outer channels. Return a clearly flagged fallback if no candidate fits.
"""
def segment_hits(a,b,rect):
    l,t,r,bottom=rect
    if a[0]==b[0]:
        return l<a[0]<r and max(min(a[1],b[1]),t)<min(max(a[1],b[1]),bottom)
    if a[1]==b[1]:
        return t<a[1]<bottom and max(min(a[0],b[0]),l)<min(max(a[0],b[0]),r)
    raise ValueError("Non-orthogonal route")


def wire_route(start,end,obstacles,lane=0):
    sx,sy=start
    ex,ey=end
    lead=14+lane%5*4
    a=(sx+lead,sy)
    z=(ex-lead,ey)
    # The first/last stubs always leave the correct side of the pin.
    left=min([a[0],z[0]]+[r[0] for r in obstacles])-20-lane*5
    right=max([a[0],z[0]]+[r[2] for r in obstacles])+20+lane*5
    top=min([sy,ey]+[r[1] for r in obstacles])-20-lane*5
    bottom=max([sy,ey]+[r[3] for r in obstacles])+20+lane*5
    xs=[(a[0]+z[0])/2,a[0],z[0],left,right]
    xs += [v for l,t,r,b in obstacles for v in (l-8,r+8)]
    ys=[(sy+ey)/2,top,bottom]
    ys += [v for l,t,r,b in obstacles for v in (t-8,b+8)]
    candidates=[]
    for x in xs:
        candidates.append([start,a,(x,sy),(x,ey),z,end])
    for y in ys:
        candidates.append([start,a,(a[0],y),(z[0],y),z,end])
    def clear(points):
        return not any(segment_hits(p,q,rect) for p,q in zip(points,points[1:]) for rect in obstacles)
    def length(points):
        return sum(abs(p[0]-q[0])+abs(p[1]-q[1]) for p,q in zip(points,points[1:]))
    valid=[p for p in candidates if clear(p)]
    return (min(valid,key=length),True) if valid else (candidates[0],False)
