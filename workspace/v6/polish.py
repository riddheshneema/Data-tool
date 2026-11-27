import sys, pickle, json, warnings; warnings.filterwarnings('ignore')
from shapely.ops import unary_union
SP = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/eng2/'
P = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
D = pickle.load(open(SP + P.get('src', 'simp22') + '.pkl', 'rb')); SQFT = 10.7639
def big(g): return max(getattr(g, 'geoms', [g]), key=lambda x: x.area) if not g.is_empty else g
allowed = D['allowed'].buffer(0.02)
gs = [p['poly'] for p in D['plots']]
def nv(g): return len(g.exterior.coords) - 1
def rect(g): return g.area / g.minimum_rotated_rectangle.area
for it in range(2):
    for i, g in enumerate(gs):
        others = unary_union([h for j, h in enumerate(gs) if j != i and h.distance(g) < 1])
        # 1) fill notches up to the convex hull where the land is free
        c = big(g.convex_hull.intersection(allowed).difference(others.buffer(0.01)).buffer(0))
        c = c.simplify(0.4, preserve_topology=True)
        if c.area >= g.area - 0.1 and (nv(c) < nv(g) or rect(c) > rect(g) + 0.01): gs[i] = g = c
        # 2) still notched: drop the notch by taking the best of "hull minus neighbours" variants trimmed to 4-5 corners
        if nv(g) > 5 or rect(g) < 0.9:
            best = g
            cs = list(g.exterior.coords)[:-1]
            from itertools import combinations
            from shapely.geometry import Polygon
            if len(cs) <= 9:
                for k in (4, 5):
                    for sub in combinations(range(len(cs)), k):
                        q = Polygon([cs[j] for j in sub])
                        if not q.is_valid or q.area < 0.9 * g.area: continue
                        if not g.buffer(0.05).contains(q): continue
                        if rect(q) > rect(best) + 0.02 or (nv(q) < nv(best) and q.area > 0.97 * g.area):
                            best = q
            gs[i] = best
keep = [g for g in gs if g.area * SQFT >= P.get('minsq', 3000)]
D['plots'] = [dict(poly=g, w=0, d=0) for g in keep]
D['green'] = D['K'].difference(unary_union(keep + [D['roads']]))
pickle.dump(D, open(SP + P.get('out', 'pol') + '.pkl', 'wb'))
A = sum(g.area for g in keep) * SQFT; v = [nv(g) for g in keep]; r = [rect(g) for g in keep]
print('plots %d | %.0f sq ft = %.1f%% | vertices %s | rect<0.9: %d, min %.2f' % (len(keep), A, A / SQFT / D['K'].area * 100, {k: v.count(k) for k in sorted(set(v))}, sum(x < 0.9 for x in r), min(r)))
