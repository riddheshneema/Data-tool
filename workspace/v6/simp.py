import sys, pickle, json, warnings; warnings.filterwarnings('ignore')
from shapely.ops import unary_union
SP = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/eng2/'
P = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
D = pickle.load(open(SP + P.get('src', 'raw') + '.pkl', 'rb')); SQFT = 10.7639
def big(g): return max(getattr(g, 'geoms', [g]), key=lambda x: x.area) if not g.is_empty else g
allowed = D['allowed']; roads = D['roads']
src = sorted(D['plots'], key=lambda p: -p['poly'].area)
out = []
for p in src:
    g = p['poly'].simplify(P.get('tol', 1.5), preserve_topology=True)
    g = big(g.intersection(allowed.buffer(0.02)).buffer(0))
    for o in out: g = big(g.difference(o.buffer(0.01)))
    g = g.simplify(P.get('tol2', 0.4), preserve_topology=True)
    out.append(g)
keep = [g for g in out if g.area * SQFT >= P.get('minsq', 3000)]
nv = [len(g.exterior.coords) - 1 for g in keep]
D['plots'] = [dict(poly=g, w=0, d=0) for g in keep]
D['green'] = D['K'].difference(unary_union(keep + [roads]))
pickle.dump(D, open(SP + P.get('out', 'simp') + '.pkl', 'wb'))
A = sum(g.area for g in keep) * SQFT
print('plots %d | %.0f sq ft = %.1f%% | vertices %s' % (len(keep), A, A / SQFT / D['K'].area * 100, {k: nv.count(k) for k in sorted(set(nv))}))
