"""Number the plots, read each one (size, facing, street, premiums, cautions), name the greens, run the checks."""
exec(open('/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/v7/kit.py').read())
import numpy as np, csv
from shapely import contains_xy
from skimage.graph import MCP_Geometric
V = pickle.load(open(SP + 'v7/plan.pkl', 'rb'))
K, roads, park, club, green, STRIP, L, CL = V['K'], V['roads'], V['park'], V['club'], V['green'], V['STRIP'], V['L'], V['CL']
W = Fr(V['Wo'], V['Wth']); E = Fr(V['Eo'], V['Eth']); FR = dict(W=W, E=E)
plots = V['plots']; RBUF = roads.buffer(0.5)
ROWNAME = dict(A1='Stream Drive', A2='Second Street', B1='Second Street', B2='Third Street', C1='Third Street')
order = ['C1', 'B2', 'B1', 'A2', 'A1']
def ukey(p):
    fr = FR[p['frame']]; c = p['poly'].centroid
    return (order.index(p['row']), 0 if p['frame'] == 'W' else 1, fr.uv(c.x, c.y)[0])
plots.sort(key=ukey)
def bearing(vx, vy):
    b = (math.degrees(math.atan2(vx, vy))) % 360
    names = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    return names[int((b + 11.25) // 22.5) % 16], b
# zones
gardenN = green.intersection(W.rect(GUh := V['GU'] - 20, 205, -40, 9.0)).buffer(0)
lawnW = green.intersection(W.rect(-60, 33.5, L['s2'][1], 200)).buffer(0)
gardenE = green.intersection(E.rect(100, 260, -40, L['s2'][0])).buffer(0)
southE = green.intersection(E.rect(60, 260, L['s3'][1], 260)).buffer(0)
rest = green.difference(unary_union([gardenN, lawnW, gardenE, southE])).buffer(0)
svc = big(southE.intersection(E.rect(128, 260, L['C1'][1], 260)))
# road distances on the road surface
x0, y0, x1, y1 = K.bounds; xs = np.arange(x0 - 5, x1 + 5, 1.0); ys = np.arange(y0 - 5, y1 + 5, 1.0); XX, YY = np.meshgrid(xs, ys)
rmask = contains_xy(roads.buffer(0.6), XX, YY); cost = np.where(rmask, 1.0, np.inf)
gate_xy = W.xy(V['GU'], V['VS'] - 1.0)
g0 = min(zip(*np.nonzero(rmask)), key=lambda rc: (xs[rc[1]] - gate_xy[0]) ** 2 + (ys[rc[0]] - gate_xy[1]) ** 2)
dgate, _ = MCP_Geometric(cost).find_costs([g0])
ave = CL['avenue'][0].buffer(6.2)
d12, _ = MCP_Geometric(cost).find_costs(list(zip(*np.nonzero(rmask & contains_xy(ave, XX, YY)))))
# T-junction heads: where a street ends on another street, the plot straight ahead gets the headlights
theads = []
for nm, (l, w) in CL.items():
    cs = list(l.coords)
    for a, b in ((cs[1], cs[0]), (cs[-2], cs[-1])):
        dx, dy = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dy)
        theads.append(Point(b[0] + dx / n * 12.5, b[1] + dy / n * 12.5))
info = []
for i, p in enumerate(plots):
    g = p['poly']; fr = FR[p['frame']]; v0, v1 = p['v']
    sgn = -1 if p['front'] == 'lo' else 1
    face, brg = bearing(sgn * fr.ev[0], sgn * fr.ev[1])
    kerb = g.boundary.intersection(RBUF.buffer(0.1))
    us = [fr.uv(x, y)[0] for x, y in g.exterior.coords]; vs = [fr.uv(x, y)[1] for x, y in g.exterior.coords]
    fv = v0 if p['front'] == 'lo' else v1; bv = v1 if p['front'] == 'lo' else v0
    fpts = [u for u, v in zip(us, vs) if abs(v - fv) < 0.6]; bpts = [u for u, v in zip(us, vs) if abs(v - bv) < 0.6]
    front_w = (max(fpts) - min(fpts)) if len(fpts) > 1 else p['w']; back_w = (max(bpts) - min(bpts)) if len(bpts) > 1 else p['w']
    c = g.centroid
    zone = contains_xy(g.buffer(1.6).difference(g), XX, YY) & rmask
    tags = []; cautions = []
    if p['row'] == 'A1': tags.append('stream-facing')
    across = Point(fr.xy(fr.uv(c.x, c.y)[0], fv + sgn * (RW := 9.0) + sgn * 6))
    if park.buffer(1).contains(across): tags.append('park-facing')
    if g.distance(park) < 0.6: tags.append('park-side')
    if p['corner']: tags.append('corner')
    if g.distance(CL['avenue'][0]) < 8: tags.append('on the avenue')
    for nm, zz in (('beside the stream lawn', lawnW), ('garden-side', gardenE), ('stream garden opposite', gardenN)):
        if g.distance(zz) < (0.6 if nm != 'stream garden opposite' else 10): tags.append(nm)
    if any(g.buffer(0.5).contains(t) for t in theads): cautions.append('faces a T-junction (set the gate off-axis)')
    if g.distance(svc) < 1: cautions.append('next to services yard')
    if g.distance(club) < 1: tags.append('next to clubhouse')
    if face in ('SSE', 'S', 'SSW'): cautions.append('south-facing')
    on_cross = g.distance(CL['cross'][0]) < 6.0
    if on_cross:
        shape = 'corner plot, one side follows the cross street'
        def width_at(t):   # plot width measured t metres in from the front
            vv = fv - sgn * t; s_ = fr.line([(min(us) - 5, vv), (max(us) + 5, vv)]).intersection(g); return s_.length
        w5, wD = width_at(5.5), width_at(p['d'] - 5.5); k_ = (wD - w5) / (p['d'] - 11.0)
        front_w = w5 - k_ * 5.5; back_w = wD + k_ * 5.5
    else:
        front_w = back_w = p['w']; shape = 'rectangle' + (' (rounded kerb corner)' if p['corner'] else '')
    info.append(dict(no=i + 1, poly=g, row=p['row'], grid=p['frame'], street=ROWNAME[p['row']], front=p['front'], face=face, bearing=brg,
                     front_w=front_w, back_w=back_w, depth=p['d'], area=g.area * SQFT, kerb=kerb.length, corner=p['corner'], mitre=p['mitre'],
                     tags=tags, cautions=cautions, shape=shape, gate_m=float(dgate[zone].min()) if zone.any() else float('nan'),
                     d12=float(d12[zone].min()) if zone.any() else float('nan')))
def cls(a):
    return '3,000-3,200' if a < 3200 else '3,200-3,500' if a < 3500 else '3,500-4,000' if a < 4000 else '4,000+'
for p in info: p['cls'] = cls(p['area'])
greens_all = unary_union([park, gardenN, lawnW, gardenE])
for p in info: p['park_m'] = p['poly'].centroid.distance(greens_all)
road_len = sum(l.intersection(K).length for l, w in CL.values())
out = dict(V); out.update(road_len=road_len, info=info, gardenN=gardenN, lawnW=lawnW, gardenE=gardenE, southE=southE, svc=svc, rest=rest, gate_xy=gate_xy)
pickle.dump(out, open(SP + 'v7/final.pkl', 'wb'))
tot = sum(p['area'] for p in info); NA = K.area
from collections import Counter
print('colony %.2f ac (%.0f m2) | without club plot %.2f ac' % (NA / 4046.86, NA, (NA - club.area) / 4046.86))
print('plots %d | %.0f sq ft | %.1f%% | avg %.0f | min %.0f max %.0f' % (len(info), tot, tot / SQFT / NA * 100, tot / len(info), min(p['area'] for p in info), max(p['area'] for p in info)))
print('roads %.0f (%.1f%%) | central park %.0f | stream garden %.0f | stream lawn %.0f | NE garden %.0f | south-east %.0f (services %.0f) | rest of green %.0f | strip %.0f | club %.0f' % (
    roads.area, roads.area / NA * 100, park.area, gardenN.area, lawnW.area, gardenE.area, southE.area, svc.area, rest.area, STRIP.area, club.area))
ops = park.area + gardenN.area + lawnW.area + gardenE.area
print('open space in 4 parks %.0f m2 = %.1f%% | all green %.1f%%' % (ops, ops / NA * 100, (green.area + park.area) / NA * 100))
print('road length %.0f m = %.1f m per plot | farthest plot centre from a park/garden %.0f m' % (road_len, road_len / len(info), max(p['park_m'] for p in info)))
print('facing', dict(Counter(p['face'] for p in info)), '| size classes', dict(Counter(p['cls'] for p in info)))
print('tags', dict(Counter(t for p in info for t in p['tags'])), '| cautions', dict(Counter(t for p in info for t in p['cautions'])))
print('min frontage %.1f ft | min kerb %.1f m | far from avenue %.0f m | far from gate %.0f m | shapes %s' % (min(p['front_w'] for p in info) * FT, min(p['kerb'] for p in info), max(p['d12'] for p in info), max(p['gate_m'] for p in info), dict(Counter(p['shape'] for p in info))))
