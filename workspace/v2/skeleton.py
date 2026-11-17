"""v2 colony (about 10.5 ac): stream green walk, 9 m ring road, 12 m spine, distributed parks.
Builds the road skeleton and the land parcels; plots are cut in plots.py."""
import sys, os, json, math, pickle, numpy as np, warnings; warnings.filterwarnings('ignore')
SP = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
os.chdir(SP + 'plan'); sys.path.insert(0, SP + 'plan')
exec(open('dims.py').read().split("if __name__=='__main__':")[0])
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString, Point, box
from shapely.ops import unary_union, linemerge, nearest_points, substring
P = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
YC = P.get('yc', -230.0)          # south cut line (colony / resort)
BUF = P.get('buf', 9.0)           # green walk along the stream (BVN 50(b), from high-water line)
DS = P.get('ds', 25.0)            # streamside plot depth
DB = P.get('db', 22.0)            # depth of plots on the other boundaries
RW = P.get('rw', 9.0)             # ring road width
SW = P.get('sw', 12.0)            # spine width
GX = P.get('gx', 330.0)           # gate x
RR = P.get('rr', 14.0)            # ring corner rounding radius
N = C.intersection(box(0, YC, 600, 0))
N = max(getattr(N, 'geoms', [N]), key=lambda g: g.area)
ring = N.exterior
es = ring.intersection(R.buffer(1.5))
es = linemerge(es) if es.geom_type == 'MultiLineString' else es
eo = ring.difference(R.buffer(1.5))
walk_green = N.intersection(es.buffer(BUF, cap_style=2)).buffer(0)
Q = N.difference(es.buffer(BUF + DS + RW / 2, cap_style=2)).difference(eo.buffer(DB + RW / 2, cap_style=2))
Q = max(getattr(Q, 'geoms', [Q]), key=lambda g: g.area)
Q = Q.buffer(-RR, join_style=1).buffer(RR, join_style=1).buffer(RR * 0.6, join_style=1).buffer(-RR * 0.6, join_style=1)
ringline = Q.exterior
ringroad = ringline.buffer(RW / 2, cap_style=2, join_style=1).intersection(N)
# spine from the gate north to the far side of the ring
ys_top = max(c[1] for c in LineString([(GX, YC - 1), (GX, 0)]).intersection(Q).coords) if not LineString([(GX, YC - 1), (GX, 0)]).intersection(Q).is_empty else YC + 60
spine_line = LineString([(GX, YC - 0.1), (GX, ys_top + RW / 2)])
spine = spine_line.buffer(SW / 2, cap_style=2).intersection(N)
roads = unary_union([ringroad, spine])
core = Q.buffer(-RW / 2, join_style=1).difference(spine)
outer = N.difference(roads).difference(walk_green).difference(Q)
out = dict(N=N, es=es, eo=eo, walk_green=walk_green, Q=Q, ringline=ringline, ringroad=ringroad, spine=spine, spine_line=spine_line,
           roads=roads, core=core, outer=outer, P=dict(yc=YC, buf=BUF, ds=DS, db=DB, rw=RW, sw=SW, gx=GX, rr=RR))
pickle.dump(out, open(SP + 'v2/skeleton.pkl', 'wb'))
A = lambda g: g.area
print('N %.0f m2 (%.2f ac) | walk green %.0f | roads %.0f (ring %.0f m long) | core %.0f %s | outer %.0f %s' % (
    A(N), A(N) / 4046.86, A(walk_green), A(roads), ringline.length, A(core), [round(g.area) for g in getattr(core, 'geoms', [core])],
    A(outer), [round(g.area) for g in getattr(outer, 'geoms', [outer])]))
