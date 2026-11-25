"""Colony on the engineer's Option 6 road network (north half), plots re-laid to BVN sizes."""
import sys, os, json, math, pickle, warnings; warnings.filterwarnings('ignore')
SP = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
os.chdir(SP + 'plan'); sys.path.insert(0, SP + 'plan')
exec(open('dims.py').read().split("if __name__=='__main__':")[0])
from shapely.geometry import LineString, Point, Polygon, MultiLineString, box
from shapely.ops import unary_union, linemerge, nearest_points
from shapely.prepared import prep
P = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
SQFT = 10.7639; BUF = P.get('buf', 9.0)
K = C if not P.get('yc') else C.intersection(box(0, P['yc'], 600, 0))
K = max(getattr(K, 'geoms', [K]), key=lambda g: g.area)
net = pickle.load(open(SP + 'eng2/net.pkl', 'rb'))['keep']
lines = [(l, 12.0 if w >= 10 else 9.0) for l, w in net if (w >= 7 and l.length > 6) or l.length > 25]
# snap: extend dangling ends to the nearest other line if within SNAP m
SNAP = P.get('snap', 16.0)
allg = unary_union([l for l, _ in lines])
fixed = []
for l, w in lines:
    cs = list(l.coords)
    for end in (0, -1):
        p = Point(cs[end])
        others = allg.difference(l.buffer(0.5))
        if others.is_empty: continue
        q = nearest_points(p, others)[1]
        deg = sum(1 for m, _ in lines if m is not l and m.distance(p) < 1.0)
        if deg == 0 and p.distance(q) < SNAP:
            if end == 0: cs = [(q.x, q.y)] + cs
            else: cs = cs + [(q.x, q.y)]
    fixed.append((LineString(cs), w))
extra = [(LineString(x), w) for x, w in P.get('add', [[[[228, -252], [265, -250], [322, -252]], 9.0]])]
def chaikin(l, n=3):
    c = list(l.coords)
    for _ in range(n):
        new = [c[0]]
        for p, q in zip(c[:-1], c[1:]): new += [(0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]), (0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1])]
        new.append(c[-1]); c = new
    return LineString(c)
lines = [(chaikin(l.simplify(P.get('simp', 2.5))), w) for l, w in fixed] + extra
if P.get('ids'):
    print([(i, round(l.length), round(l.centroid.x), round(l.centroid.y)) for i, (l, w) in enumerate(lines)])
lines = [lw for i, lw in enumerate(lines) if i not in set(P.get('drop', []))]
if P.get('outer'):
    Q = K.difference(R.buffer(BUF + 4.5 + P.get('og', 0.5)))
    Q = max(getattr(Q, 'geoms', [Q]), key=lambda g: g.area)
    edge = Q.exterior.intersection(R.buffer(BUF + 4.5 + P.get('og', 0.5) + 0.3))
    from shapely.ops import linemerge
    edge = linemerge(edge) if edge.geom_type == 'MultiLineString' else edge
    segs = [g for g in getattr(edge, 'geoms', [edge]) if g.length > 40]
    for g in segs:
        lines.append((chaikin(g.simplify(3.0), 4), 9.0))
    if P.get('dbg'): print('outer segs', [round(g.length) for g in segs])
roads = unary_union([l.buffer(w / 2, cap_style=1, join_style=1) for l, w in lines]).intersection(K)
roads = unary_union([roads, box(331 - 6, -263, 331 + 6, -240).intersection(K)])
allowed = K.difference(R.buffer(BUF)).difference(roads)
ap = prep(allowed.buffer(0.1))
QUADS = {}; META = {}
def walk(ring, outward, taken, W, D, step=0.5, RMIN=0.85, minsq=2450):
    L = ring.length; out = []; t = 0.0
    ccw = Polygon(ring).exterior.is_ccw
    def pt(s): return ring.interpolate(s % L)
    def nrm(s):
        a, b = pt(s - 0.8), pt(s + 0.8); tx, ty = b.x - a.x, b.y - a.y; n = math.hypot(tx, ty) or 1
        nx, ny = (ty / n, -tx / n) if ccw else (-ty / n, tx / n)
        return (nx, ny) if outward else (-nx, -ny)
    occ = unary_union(taken) if taken else Polygon()
    while t < L - W * 0.5:
        p0, p1 = pt(t), pt(t + W); n0, n1 = nrm(t), nrm(t + W)
        rb = math.dist((p0.x + n0[0] * D, p0.y + n0[1] * D), (p1.x + n1[0] * D, p1.y + n1[1] * D)) / (p0.distance(p1) or 1)
        if P.get('fan') and not (0.8 < rb < 1.25): t += step; continue
        if not P.get('fan') and not (1.02 < rb <= P.get('rmax', 1.25)):
            fx, fy = p1.x - p0.x, p1.y - p0.y; fl = math.hypot(fx, fy) or 1
            nm = (-fy / fl, fx / fl)
            if nm[0] * (n0[0] + n1[0]) + nm[1] * (n0[1] + n1[1]) < 0: nm = (-nm[0], -nm[1])
            n0 = n1 = nm
        q = Polygon([(p0.x, p0.y), (p1.x, p1.y), (p1.x + n1[0] * D, p1.y + n1[1] * D), (p0.x + n0[0] * D, p0.y + n0[1] * D)])
        ok = False
        if q.is_valid:
            q2 = q.difference(roads)
            if not q2.is_empty:
                q2 = max(getattr(q2, 'geoms', [q2]), key=lambda g: g.area)
                ok = (q2.area > 0.97 * q.area and q2.area * SQFT >= minsq and q2.area / q2.minimum_rotated_rectangle.area >= RMIN
                      and ap.contains(q2) and q2.intersection(occ).area < 0.5 and not any(q2.intersection(x).area > 0.5 for x in out[-3:]))
        if ok:
            QUADS[q2.wkb] = (p0.distance(p1), math.dist(q.exterior.coords[2], q.exterior.coords[3]), D); META[q2.wkb] = ((p0.x, p0.y), (p1.x, p1.y), n0, n1, D)
            out.append(q2); occ = occ.union(q2); t += W
        else: t += step
    return out
rings = []
for g in getattr(roads, 'geoms', [roads]):
    rings.append((g.exterior, True))
    for h in g.interiors: rings.append((h, False))
plots = []
for W, D in P.get('sizes', [[12.8, 18.29], [14.95, 15.24]]):
    for ring, outw in rings:
        if ring.length < 20: continue
        got = walk(ring, outw, plots, W, D); plots += got
        if P.get('dbg'): print('ring len %.0f outward %s -> %d' % (ring.length, outw, len(got)))
# grow all plots back from the road together (round-robin) so back-to-back rows meet near the block middle
from shapely.strtree import STRtree
def mk(m, d):
    p0, p1, n0, n1, _ = m
    q = Polygon([p0, p1, (p1[0] + n1[0] * d, p1[1] + n1[1] * d), (p0[0] + n0[0] * d, p0[1] + n0[1] * d)])
    q = q.difference(roads)
    return max(getattr(q, 'geoms', [q]), key=lambda g: g.area) if not q.is_empty else q
metas = [META[q.wkb] for q in plots]; dep = [m[4] for m in metas]; cur = plots[:]
nb = [[j for j in range(len(plots)) if j != i and plots[j].distance(plots[i]) < 2 * P.get('dmax', 30.5)] for i in range(len(plots))]
STEP = 0.5; WHY = {}; active = set(range(len(plots)))
while active:
    for i in sorted(active):
        d = dep[i] + STEP
        if d > P.get('dmax', 30.5): active.discard(i); continue
        qx = mk(metas[i], d)
        if not qx.is_empty and P.get('noclip') and any(qx.intersection(cur[j]).area > 0.3 for j in nb[i]):
            WHY['ov'] = WHY.get('ov', 0) + 1; active.discard(i); continue
        if not qx.is_empty and not P.get('noclip'):
            nbu = unary_union([cur[j] for j in nb[i] if cur[j].distance(qx) < 0.5])
            if not nbu.is_empty:
                qx = qx.difference(nbu); qx = max(getattr(qx, 'geoms', [qx]), key=lambda g: g.area) if not qx.is_empty else qx
        why = 'empty' if qx.is_empty or qx.geom_type != 'Polygon' else 'ap' if not ap.contains(qx) else 'rect' if qx.area / qx.minimum_rotated_rectangle.area < P.get('rgrow', 0.92) or not (0.78 < math.dist((metas[i][0][0]+metas[i][2][0]*d, metas[i][0][1]+metas[i][2][1]*d), (metas[i][1][0]+metas[i][3][0]*d, metas[i][1][1]+metas[i][3][1]*d)) / math.dist(metas[i][0], metas[i][1]) < 1.3) else 'small' if qx.area < cur[i].area + 1 else ''
        if why:
            WHY[why] = WHY.get(why, 0) + 1; active.discard(i); continue
        dep[i] = d; cur[i] = qx
plots = cur
for q, m, d in zip(plots, metas, dep):
    QUADS[q.wkb] = (math.dist(m[0], m[1]), None, d)
print(WHY, 'dep', sorted(round(x,1) for x in dep)[:20]); minf = P.get('minfinal', 3000)
MET = {q.wkb: (m, d) for q, m, d in zip(plots, metas, dep)}
plots = [q for q in plots if q.area * SQFT >= minf]
green = K.difference(unary_union(plots + [roads]))
A_ = [q.area * SQFT for q in plots]
res = dict(allowed=allowed, K=K, N=K, roads=roads, plots=[dict(poly=q, w=QUADS[q.wkb][0], d=QUADS[q.wkb][2], quad=QUADS[q.wkb], meta=MET[q.wkb]) for q in plots], green=green, lines=lines)
pickle.dump(res, open(SP + 'eng2/' + P.get('out', 'plan2') + '.pkl', 'wb'))
rect = [q.area / q.minimum_rotated_rectangle.area for q in plots]
print('colony %.2f ac | plots %d | %.0f sq ft = %.1f%% | roads %.1f%% | green %.1f%% | min %.0f max %.0f | rect>0.98: %d' % (
    K.area / 4046.86, len(plots), sum(A_), sum(A_) / SQFT / K.area * 100, roads.area / K.area * 100, green.area / K.area * 100, min(A_), max(A_), sum(r > 0.98 for r in rect)))
