"""v2 pass 5: every lawn edge cut square to the ring road; compact club lawn on both sides of the spine;
narrow central green spine; leftovers merged into plots."""
import sys, json, math, pickle, warnings; warnings.filterwarnings('ignore')
SP = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
sys.path.insert(0, SP + 'v2')
from plots import cut_piece_area, frontage_len, min_width, SQFT, _normal, centreline
from shapely.geometry import Point, LineString, MultiLineString, Polygon, MultiPolygon, box
from shapely.ops import unary_union, split
K = pickle.load(open(SP + 'v2/skeleton.pkl', 'rb'))
P = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
OUTP = P.get('out', 'layout10')
WMIN = P.get('w', 12.8); MIN = P.get('min', 3000) / SQFT; AT = P.get('at', 3080) / SQFT
GW = P.get('gw', 12.0); DI = P.get('di', 24.0)
N, ring, roads, core, outer, Q, walkg = K['N'], K['ringline'], K['roads'], K['core'], K['outer'], K['Q'], K['walk_green']
RW = K['P']['rw']; GX = K['P']['gx']; YC = K['P']['yc']; SWD = K['P']['sw']
L = ring.length; reach = RW / 2 + 1.0
def big(g): return max(getattr(g, 'geoms', [g]), key=lambda x: x.area) if not g.is_empty else g
def perp(s, out=True, ln=75.0):
    s %= L; p = ring.interpolate(s); nx_, ny_ = _normal(ring, s, True)
    sg = 1 if not Q.contains(Point(p.x + nx_ * 10, p.y + ny_ * 10)) else -1
    if not out: sg = -sg
    return LineString([(p.x + sg * nx_ * (RW / 2 - 0.5), p.y + sg * ny_ * (RW / 2 - 0.5)), (p.x + sg * nx_ * ln, p.y + sg * ny_ * ln)])
def inrange(s, a, b):
    s %= L; a %= L; b %= L
    return a <= s <= b if a <= b else (s >= a or s <= b)
def band_between(region, a, b, out=True):
    """Pieces of `region` whose ring position lies between ring params a and b (square cuts at a and b)."""
    parts = split(region, MultiLineString([perp(a, out), perp(b, out)]))
    return unary_union([g for g in parts.geoms if inrange(ring.project(g.representative_point()), a, b)])
def strip_at(s, width, region, out=True):
    p = perp(s, out); return p.buffer(width / 2, cap_style=2).intersection(region)
# ---- outer band features (ring parameter intervals)
F = P.get('feat', {})
west_lawn = Polygon()
kink = band_between(outer, *F.get('kink', (142, 156)))
ne_lawn = Polygon()
svc = band_between(outer, *F.get('svc', (368, 379)))
entry = unary_union([big(outer.intersection(box(GX + SWD / 2 - 1, YC - 1, GX + 22, YC + 30))),
                     big(outer.intersection(box(GX - SWD / 2 - P.get('ew', 24), YC - 1, GX - SWD / 2 + 1, YC + P.get('eh', 26))))])
links = Polygon()
# ---- core: compact club lawn either side of the spine + narrow green spine in the west core
rows_zone = ring.buffer(RW / 2 + DI, join_style=1)
middle = core.difference(rows_zone)
club_lawn = big(middle.intersection(box(GX - SWD / 2 - P.get('cw', 34), -400, GX - SWD / 2 + 0.5, 0)))
cores = sorted(getattr(core, 'geoms', [core]), key=lambda g: g.centroid.x)
west_core = cores[0]
cl = centreline(west_core)
tip = P.get('tipgap', 20.0)
green_spine = Polygon()
def extend(line, d=40.0):
    c = list(line.coords)
    def ext(p, q):
        dx, dy = p[0] - q[0], p[1] - q[1]; n = math.hypot(dx, dy) or 1.0
        return (p[0] + dx / n * d, p[1] + dy / n * d)
    return LineString([ext(c[0], c[1])] + c + [ext(c[-1], c[-2])])
XW = P.get('wtip', 214.0)
def ymid(poly, x):
    seg = poly.intersection(LineString([(x, -400), (x, 0)]))
    ys = [c[1] for g in getattr(seg, 'geoms', [seg]) for c in g.coords]
    return (min(ys) + max(ys)) / 2
west_lawn = west_core.intersection(box(0, -400, XW, 0))
xc = GX - SWD / 2 - P.get('cw', 48)
walk_line = LineString([(XW - 6, ymid(west_core, XW)), (xc + 6, ymid(west_core, xc))])
garden_walk = walk_line.buffer(P.get('gww', 6.0) / 2, cap_style=2).intersection(west_core).difference(west_lawn)
east_core = cores[-1]
ex0, ex1 = east_core.bounds[0], east_core.bounds[2]
walk_e = LineString([(ex0 - 2, ymid(east_core, ex0 + 4)), (ex1 - 14, ymid(east_core, ex1 - 14))])
garden_walk_e = walk_e.buffer(P.get('gww', 6.0) / 2, cap_style=2).intersection(east_core)
garden_walk = unary_union([garden_walk, garden_walk_e])
splitters = [walk_line, walk_e]
central = unary_union([club_lawn, west_lawn, garden_walk])
# ---- plot regions
outer_pl = outer.difference(unary_union([west_lawn, kink, ne_lawn, svc, entry, links]))
core_pl = core.difference(central)
core_pl = unary_union([g for g in split(core_pl, MultiLineString(splitters)).geoms])
pieces = [g for g in list(getattr(outer_pl, 'geoms', [outer_pl])) + list(getattr(core_pl, 'geoms', [core_pl])) if g.area > 5]
pl = []
for pc in pieces: pl += cut_piece_area(pc, ring, AT, WMIN, reach, 60, closed=True)
# ---- merge leftovers (too small, or no 12.2 m road frontage) into the neighbour with the longest shared edge
def bad(g): return g.area < MIN or frontage_len(g, roads) < 12.2
changed = True
while changed:
    changed = False
    for i, g in enumerate(sorted(pl, key=lambda x: x.area)):
        if not bad(g): continue
        cands = [(g.boundary.intersection(h.boundary.buffer(0.05)).length, h) for h in pl if h is not g]
        cands = [c for c in cands if c[0] > 1.5]
        if not cands: continue
        l, h = max(cands, key=lambda c: c[0])
        m = unary_union([g, h]).buffer(0.01).buffer(-0.01)
        pl = [x for x in pl if x is not g and x is not h] + [m]; changed = True; break

# ---- re-split oversized plots; adopt unassigned land
def valid(g): return g.area >= MIN and frontage_len(g, roads) >= 12.2
changed = True
while changed:
    changed = False
    for g in sorted(pl, key=lambda x: -x.area):
        if g.area < 2.0 * AT or frontage_len(g, roads) < 2 * WMIN: continue
        parts = cut_piece_area(g, ring, AT, WMIN, reach, 60, closed=True)
        if not (len(parts) > 1 and all(valid(x) for x in parts)):
            parts = cut_piece_area(g, K['spine_line'], AT, WMIN, SWD / 2 + 1.0, 60, closed=False)
        if len(parts) > 1 and all(valid(x) for x in parts):
            pl = [x for x in pl if x is not g] + parts; changed = True; break
used = unary_union(pl + [central, kink, ne_lawn, svc, entry, links, roads, walkg])
gap = N.difference(used)
for g in [x for x in getattr(gap, 'geoms', [gap]) if x.area > 5]:
    if valid(g): pl.append(g); continue
    cands = [(g.boundary.intersection(h.boundary.buffer(0.05)).length, h) for h in pl]
    l, h = max(cands, key=lambda c: c[0])
    if l > 1.5: pl = [x for x in pl if x is not h] + [unary_union([g, h]).buffer(0.01).buffer(-0.01)]
leftover = [g for g in pl if bad(g)]
pl = [g for g in pl if not bad(g)]

# ---- pocket lawns: turn chosen plots into pockets (pairs across the ring where possible)
def pick(s, inner):
    c = [g for g in pl if bool(Q.contains(g.centroid)) == inner]
    def d(g):
        t = ring.project(g.centroid); return min(abs(t - s), L - abs(t - s))
    return min(c, key=d)
pockets = []
for s, side in P.get('pockets', [[40, 'o'], [100, 'o'], [100, 'i'], [200, 'o'], [335, 'o'], [300, 'i'], [400, 'o'], [400, 'i'], [560, 'o'], [560, 'i']]):
    g = pick(s, side == 'i')
    if g not in pockets: pockets.append(g)
pl = [g for g in pl if g not in pockets]
def key(g):
    t = ring.project(g.centroid) - ring.project(Point(GX + 10, YC + 25))
    return (0 if not Q.contains(g.centroid) else 1, t % L)
pl.sort(key=key)
plots = {str(i + 1): g for i, g in enumerate(pl)}
parks = dict(**{f'pocket_{i+1}': g for i, g in enumerate(sorted(pockets, key=lambda g: ring.project(g.centroid)))}, tip_lawn=west_lawn, stream_green=kink, garden_walk=garden_walk, entry_green=entry,
             pocket_greens=unary_union(leftover) if leftover else Polygon())
res = dict(K, amenity=club_lawn, plots=plots, parks=unary_union([g for g in parks.values() if not g.is_empty]), park_parts=parks, svc=svc, links=links, centreline=cl)
res['labels'] = [(g.representative_point().x, g.representative_point().y, n.replace('_', ' ')) for n, g in parks.items() if not g.is_empty and n not in ('pocket_greens', 'entry_green', 'garden_walk')] + [(svc.centroid.x, svc.centroid.y, 'services')]
pickle.dump(res, open(SP + f'v2/{OUTP}.pkl', 'wb'))
A = [g.area * SQFT for g in pl]; NA = N.area
pk = sum(g.area for g in parks.values() if not g.is_empty); print('amenity (club) %.0f m2' % club_lawn.area)
print('plots %d | %.0f sq ft = %.1f%% | min %.0f | max %.0f | avg %.0f | under 4k: %d' % (len(pl), sum(A), sum(A) / SQFT / NA * 100, min(A), max(A), sum(A) / len(A), sum(a < 4000 for a in A)))
print('parks:', ', '.join(f'{k} {v.area:.0f}' for k, v in parks.items() if not v.is_empty), '| total %.0f m2 = %.1f%%' % (pk, pk / NA * 100))
print('walk %.1f%% | roads %.1f%% | services %.0f | links %.0f | check sum %.1f%%' % (walkg.area / NA * 100, roads.area / NA * 100, svc.area, links.area,
      (sum(A) / SQFT + pk + walkg.area + roads.area + svc.area + club_lawn.area) / NA * 100))
print('largest', sorted([round(a) for a in A], reverse=True)[:8], '| min frontage %.1f m' % min(frontage_len(g, roads) for g in pl))
