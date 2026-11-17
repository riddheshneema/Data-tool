"""v5b: plots laid by walking along road edges (fixed 45 ft frontage, 75 ft depth, square to the road)."""
import sys, os, json, math, pickle, warnings; warnings.filterwarnings('ignore')
SP = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
os.chdir(SP + 'plan'); sys.path.insert(0, SP + 'plan')
exec(open('dims.py').read().split("if __name__=='__main__':")[0])
from shapely.geometry import box, Point, LineString, Polygon, LinearRing
from shapely.ops import unary_union
from shapely.prepared import prep
P = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
YC = P.get('yc', -232.0); BUF = P.get('buf', 9.0); D = P.get('D', 22.86); W = P.get('W', 13.716)
RW = 9.0; SW = 12.0; RR = P.get('rr', 22.0); GX = P.get('gx', 330.0); EDGE = P.get('edge', 0.5); SQFT = 10.7639
N = C.intersection(box(0, YC, 600, 0)); N = max(getattr(N, 'geoms', [N]), key=lambda g: g.area)
es = N.exterior.intersection(R.buffer(1.5)); eo = N.exterior.difference(R.buffer(1.5))
def smooth(p, r): return p.buffer(-r, join_style=1).buffer(r, join_style=1).buffer(r * 0.7, join_style=1).buffer(-r * 0.7, join_style=1)
def main(g): return max(getattr(g, 'geoms', [g]), key=lambda x: x.area)
QA = smooth(main(N.difference(es.buffer(BUF + D + RW / 2 + P.get('m', 1.5), cap_style=2)).difference(eo.buffer(EDGE + D + RW / 2 + P.get('m', 1.5), cap_style=2))), RR)
A = QA.exterior
spine_top = P.get('spine_top', -150.0)
spine = box(GX - SW / 2, YC - 1, GX + SW / 2, spine_top).intersection(N)
roadA = A.buffer(RW / 2, join_style=1)
extra_roads = []
for seg in P.get('lanes', []):          # extra 9 m lanes [[x1,y1],[x2,y2],...]
    extra_roads.append(LineString(seg).buffer(P.get('lw', RW) / 2, cap_style=2, join_style=1))
roads = unary_union([roadA, spine] + extra_roads).intersection(N)
allowed = N.difference(R.buffer(BUF)).difference(roads)
ap = prep(allowed.buffer(P.get('tol', 0.6)))
def frontage_rings(poly, side):
    g = poly.buffer(RW / 2 if side == 'out' else -RW / 2, join_style=1)
    return [q.exterior for q in getattr(g, 'geoms', [g])]
def walk(ring, outward, taken, step=0.5, D=D, RMIN=0.85):
    L = ring.length; out = []; t = 0.0
    ccw = Polygon(ring).exterior.is_ccw
    def pt(s): return ring.interpolate(s % L)
    def nrm(s):
        a, b = pt(s - 0.8), pt(s + 0.8); tx, ty = b.x - a.x, b.y - a.y; n = math.hypot(tx, ty) or 1
        nx, ny = (ty / n, -tx / n) if ccw else (-ty / n, tx / n)       # outward of the ring polygon
        return (nx, ny) if outward else (-nx, -ny)
    start = 0.0; tries = 0
    while t < L - W * 0.5:
        p0, p1 = pt(t), pt(t + W); n0, n1 = nrm(t), nrm(t + W)
        if P.get('rectonly', 1):
            fx, fy = p1.x - p0.x, p1.y - p0.y; fl = math.hypot(fx, fy) or 1
            nm = (-fy / fl, fx / fl)
            if nm[0] * (n0[0] + n1[0]) + nm[1] * (n0[1] + n1[1]) < 0: nm = (-nm[0], -nm[1])
            n0 = n1 = nm
        q = Polygon([(p0.x, p0.y), (p1.x, p1.y), (p1.x + n1[0] * D, p1.y + n1[1] * D), (p0.x + n0[0] * D, p0.y + n0[1] * D)])
        q2 = q.difference(roads) if q.is_valid else q
        q2 = max(getattr(q2, 'geoms', [q2]), key=lambda g: g.area) if not q2.is_empty else q2
        if q.is_valid and not q2.is_empty and q2.area > 0.97 * q.area and q2.area / q2.minimum_rotated_rectangle.area >= RMIN and ap.contains(q2) and not any(q2.intersection(x).area > 0.5 for x in taken[-60:] + out[-3:]):
            QUADS[q2.wkb] = (p0.distance(p1), Point(p0.x + n0[0] * D, p0.y + n0[1] * D).distance(Point(p1.x + n1[0] * D, p1.y + n1[1] * D)), D, q2.area / q.area); out.append(q2); t += W
        else: t += step
    return out
QUADS = {}
taken = []
plots = []
for ring in frontage_rings(QA, 'out'):
    plots += walk(ring, True, taken, RMIN=P.get('rout', 0.85))
taken = plots[:]
for ring in frontage_rings(QA, 'in'):
    plots += walk(ring, False, taken, D=P.get('Din', D), RMIN=P.get('rin', 0.92))
for i, lr in enumerate(extra_roads):
    for side in (1, -1):
        pass
# spine frontage
for s in P.get('spine_rows', []):
    pass
plots = [q for q in plots if q.area * SQFT >= 3000 and QUADS[q.wkb][3] > P.get('keep', 0.995)]
def rect(q): return q.area / q.minimum_rotated_rectangle.area
green = N.difference(unary_union(plots + [roads]))
pickle.dump(dict(N=N, K=N, roads=roads, plots=[dict(poly=q, w=W, d=D, quad=QUADS[q.wkb]) for q in plots], green=green, QA=QA, spine=spine, P=P), open(SP + 'v5/walk.pkl', 'wb'))
A_ = [q.area * SQFT for q in plots]; rs = [rect(q) for q in plots]
print('colony %.2f ac | plots %d | %.0f sq ft = %.1f%% | roads %.1f%% | green %.1f%% | rect avg %.3f min %.3f | %d plots >0.98' % (
    N.area / 4046.86, len(plots), sum(A_), sum(A_) / SQFT / N.area * 100, roads.area / N.area * 100, green.area / N.area * 100, sum(rs) / len(rs), min(rs), sum(r > 0.98 for r in rs)))
