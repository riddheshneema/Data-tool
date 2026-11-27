"""Pull each plot's front out to the road edge (fills the verge sliver left where a straight front meets a curved road)."""
import pickle, math, warnings; warnings.filterwarnings('ignore')
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
SP = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/eng2/'
D = pickle.load(open(SP + 'pol.pkl', 'rb')); roads = D['roads']; allowed = D['allowed'].buffer(0.02); SQFT = 10.7639
def big(g): return max(getattr(g, 'geoms', [g]), key=lambda x: x.area) if not g.is_empty else g
gs = [p['poly'] for p in D['plots']]
out = list(gs)
for i, g in enumerate(gs):
    cs = list(g.exterior.coords)[:-1]; n = len(cs)
    edges = [(k, (k + 1) % n) for k in range(n)]
    fi = min(edges, key=lambda e: LineString([cs[e[0]], cs[e[1]]]).centroid.distance(roads))
    a, b = fi
    # neighbours along the polygon: previous of a, next of b are the back ends of the side lines
    pa, nb_ = cs[(a - 1) % n], cs[(b + 1) % n]
    def push(p, q, d=3.0):
        vx, vy = p[0] - q[0], p[1] - q[1]; l = math.hypot(vx, vy) or 1
        return (p[0] + vx / l * d, p[1] + vy / l * d)
    A2, B2 = push(cs[a], pa), push(cs[b], nb_)
    ext = Polygon([A2, B2, cs[b], cs[a]]).buffer(0)
    others = unary_union([h for j, h in enumerate(out) if j != i and h.distance(g) < 4])
    add = ext.difference(roads).intersection(allowed).difference(others.buffer(0.01) if not others.is_empty else others)
    g2 = big(g.union(add).buffer(0.01, join_style=2).buffer(-0.01, join_style=2)).simplify(0.3, preserve_topology=True)
    if g2.area >= g.area: out[i] = g2
D['plots'] = [dict(poly=g, w=0, d=0) for g in out]
D['green'] = D['K'].difference(unary_union(out + [roads]))
pickle.dump(D, open(SP + 'ext.pkl', 'wb'))
fr = [g.boundary.intersection(roads.buffer(0.4)).length * 3.28084 for g in out]
nv = [len(g.exterior.coords) - 1 for g in out]
print('plots %d, %.1f%%, min frontage %.0f ft, <40ft: %d, vertices %s' % (len(out), sum(g.area for g in out) / D['K'].area * 100, min(fr), sum(f < 40 for f in fr), {k: nv.count(k) for k in sorted(set(nv))}))
