"""v4: rectangular plots in parallel bands (engineer's method). Plots first; gardens are what is left.
Usage: grid.py '{"th":15,"D":22.86,"W":13.716,...}'  -> prints stats, writes v4/grid.pkl"""
import sys, os, json, math, pickle, warnings; warnings.filterwarnings('ignore')
SP = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
os.chdir(SP + 'plan'); sys.path.insert(0, SP + 'plan')
exec(open('dims.py').read().split("if __name__=='__main__':")[0])
from shapely.geometry import box, Point, LineString, Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity
P = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
TH = P.get('th', 15.0)               # band direction (deg from +x)
D = P.get('D', 22.86)                # plot depth 75 ft
W = P.get('W', 13.716)               # plot width 45 ft
RW = P.get('rw', 9.0); SW = P.get('sw', 12.0)
AREA = P.get('area', 10.5) * 4046.86
SET = P.get('set', 9.0)              # stream setback
MAXEXTRA = P.get('maxextra', 6.1)    # corner plots up to 45+20 ft wide
SQFT = 10.7639
O = (0, 0)
rot = lambda g: affinity.rotate(g, -TH, origin=O)      # to grid frame (bands along x')
unrot = lambda g: affinity.rotate(g, TH, origin=O)
Cg = rot(C); Rg = rot(R); gate = rot(Point(331, -262))
# colony = C above a band-parallel south line, sized to AREA
y0, y1 = Cg.bounds[1], Cg.bounds[3]
lo, hi = y0, y1
for _ in range(60):
    m = (lo + hi) / 2
    if Cg.intersection(box(-1e4, m, 1e4, 1e4)).area > AREA: lo = m
    else: hi = m
VS = (lo + hi) / 2 + P.get('vshift', 0.0)
K = Cg.intersection(box(-1e4, VS, 1e4, 1e4))
K = max(getattr(K, 'geoms', [K]), key=lambda g: g.area)
B = K.difference(Rg.buffer(SET))                      # buildable
ux0, ux1 = K.bounds[0] - 5, K.bounds[2] + 5
# band stack from the south: row(back on boundary) | road | row row | road | row row | ...
rows, roads_v = [], []
v = VS
rows.append((v, v + D, 'S')); v += D
while True:
    if v + RW + D > K.bounds[3] - P.get('topmargin', 0): break
    roads_v.append((v, v + RW)); v += RW
    rows.append((v, v + D, 'N')); v += D           # faces road below
    if v + D > K.bounds[3]: break
    rows.append((v, v + D, 'S')); v += D           # faces road above
def fit_intervals(v1, v2, region):
    strip = box(ux0, v1 + 0.05, ux1, v2 - 0.05)
    bad = strip.difference(region)
    cuts = sorted((g.bounds[0], g.bounds[2]) for g in getattr(bad, 'geoms', [bad]) if g.area > 0.05)
    out, x = [], ux0
    for a, b in cuts:
        if a > x: out.append((x, a))
        x = max(x, b)
    if x < ux1: out.append((x, ux1))
    return [(a, b) for a, b in out if b - a >= W - 0.01]
# roads: each band road spans the union of the rows it serves
road_polys = []
for (a, b) in roads_v:
    served = [r for r in rows if abs(r[1] - a) < 1e-6 or abs(r[0] - b) < 1e-6]
    iv = [i for r in served for i in fit_intervals(r[0], r[1], B)]
    if not iv: continue
    u0, u1 = min(i[0] for i in iv), max(i[1] for i in iv)
    road_polys.append(box(u0 - (RW if P.get('endcap', 1) else 0), a, u1 + (RW if P.get('endcap', 1) else 0), b).intersection(K))
# spine from the gate (perpendicular to the bands) up to the top road
UG = gate.x if 'ug' not in P else P['ug']
top = max(b for a, b in roads_v)
spine = box(UG - SW / 2, VS - 60, UG + SW / 2, top).intersection(K)
# end connectors between consecutive roads (west and east ends, where both roads exist)
conn = []
rp = sorted([g for g in road_polys if not g.is_empty], key=lambda g: g.bounds[1])
for g1, g2 in zip(rp[:-1], rp[1:]):
    for side in ('w', 'e'):
        if side == 'w': u = max(g1.bounds[0], g2.bounds[0])
        else: u = min(g1.bounds[2], g2.bounds[2])
        uc = u + RW / 2 if side == 'w' else u - RW / 2
        c = box(uc - RW / 2, g1.bounds[3] - 0.1, uc + RW / 2, g2.bounds[1] + 0.1)
        if c.within(K.buffer(0.5)): conn.append(c)
ROADS = unary_union(road_polys + [spine] + conn).intersection(K)
# plots
B2 = B.difference(ROADS.buffer(0.01))
plots = []
for (v1, v2, f) in rows:
    for a, b in fit_intervals(v1, v2, B2):
        L = b - a; n = int(L // W)
        if n == 0 or (n == 1 and P.get('noorphan', 1)): continue
        r = L - n * W
        widths = [W] * n
        if n == 1: widths[0] += min(r, MAXEXTRA)
        else:
            widths[0] += min(r / 2, MAXEXTRA); widths[-1] += min(r / 2, MAXEXTRA)
        # centre the run so leftovers sit at the ends
        used = sum(widths); x = a + (L - used) / 2
        for w_ in widths:
            plots.append(dict(poly=box(x, v1, x + w_, v2), w=w_, d=v2 - v1)); x += w_
# keep only plots with road frontage
def front(pl):
    return pl.boundary.intersection(ROADS.buffer(0.3)).length
plots = [p for p in plots if front(p['poly']) >= 12.0]
PL = unary_union([p['poly'] for p in plots])
GREEN = K.difference(ROADS).difference(PL)
A = [p['poly'].area * SQFT for p in plots]
res = dict(P=P, TH=TH, K=unrot(K), roads=unrot(ROADS), plots=[dict(p, poly=unrot(p['poly'])) for p in plots], green=unrot(GREEN), gate=unrot(gate), rows=rows, roads_v=roads_v)
pickle.dump(res, open(SP + 'v4/grid.pkl', 'wb'))
from collections import Counter
sizes = Counter(f"{round(p['w'] * 3.2808)}x{round(p['d'] * 3.2808)}" for p in plots)
print('th %.1f | colony %.2f ac | plots %d | %.0f sq ft = %.1f%% | roads %.1f%% | green %.1f%% | sizes %s' % (
    TH, K.area / 4046.86, len(plots), sum(A), sum(A) / SQFT / K.area * 100, ROADS.area / K.area * 100, GREEN.area / K.area * 100, dict(sizes.most_common(6))))
