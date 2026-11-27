"""v9: Stream Drive + north-facing stream row kept; inner streets run stream-to-gate so plots face east or west."""
exec(open('/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/v7/kit.py').read())
import numpy as np
P = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
D = 22.86; RW = 9.0; AW = 12.0; GB = 9.0; MINF = 12.19
W = Fr((144.0, -136.5), 22.94); E = Fr((258.4, -72.2), 10.40); W2 = Fr(W.o, W.th - 90)     # W2: u2 = v1, v2 = -u1
A0, A1v = GB + RW, GB + RW + D; VS = P.get('vs', 150.3); DM = GB + RW / 2
def isect(p, d, q, e):
    den = d[0] * e[1] - d[1] * e[0]; t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den; return (p[0] + d[0] * t, p[1] + d[1] * t)
X0 = isect(W.o, W.eu, E.o, E.eu); bis = (W.ev[0] + E.ev[0], W.ev[1] + E.ev[1]); bl = math.hypot(*bis); bis = (bis[0] / bl, bis[1] / bl)
nE = (-bis[1], bis[0]) if -bis[1] > 0 else (bis[1], -bis[0])
def hp(s):
    a = (X0[0] - bis[0] * 600, X0[1] - bis[1] * 600); b = (X0[0] + bis[0] * 600, X0[1] + bis[1] * 600)
    return Polygon([a, b, (b[0] + s * nE[0] * 900, b[1] + s * nE[1] * 900), (a[0] + s * nE[0] * 900, a[1] + s * nE[1] * 900)])
HPW, HPE = hp(-1), hp(1)
def hinge_u(fr, v): return fr.uv(*isect(fr.xy(0, v), fr.eu, X0, bis))[0]
south = W.rect(-200, 600, VS, VS + 400).intersection(box(0, -400, 343.6, 0))
K = big(C.difference(south).difference(box(299, -290, 323, -261.4)))
STRIP = K.intersection(R.buffer(GB)); BUILD = K.difference(R.buffer(GB))
# ---- roads
GU = P.get('gu', 111.76); PITCH = RW + 2 * D; UW = GU - (AW / 2 + 2 * D + RW / 2) - PITCH       # west street
US = [GU - (AW / 2 + 2 * D + RW / 2), GU + (AW / 2 + 2 * D + RW / 2), GU + (AW / 2 + 2 * D + RW / 2) + PITCH]   # 9 m streets either side of the Avenue
RB = 12.0; EDR = 103.4; VWEND = P.get('vwend', 100.0)
uHd, eHd = hinge_u(W, DM), hinge_u(E, DM)
drive = [E.xy(EDR, DM), E.xy(eHd + 8, DM), W.xy(uHd - 8, DM), W.xy(UW + RB + 0.01, DM)] + [W.xy(u, v) for u, v in W.arc(UW + RB, DM + RB, RB, 270, 180)[1:]] + [W.xy(UW, VWEND)]
CL = dict(drive=(LineString(drive), RW))
ends = {}
for i, u in enumerate(US + [GU]):
    w = AW if u == GU else RW
    # start on Stream Drive (which bends on the east side), run to the colony edge
    vs0 = DM if u < uHd else W.uv(*E.xy(E.uv(*W.xy(u, 40))[0], DM))[1]
    seg = W.line([(u, vs0), (u, 400)]).intersection(K.buffer(-1.0))
    seg = min(parts_l := [g for g in getattr(seg, 'geoms', [seg]) if g.geom_type == 'LineString'], key=lambda g: g.distance(Point(W.xy(u, vs0))))
    vend = max(W.uv(*c)[1] for c in seg.coords); ends[u] = (vs0, vend)
    CL['avenue' if u == GU else f's{i}'] = (W.line([(u, vs0), (u, vend if u != GU else VS)]), w)
UC = US[-1] + PITCH; VL = P.get('vl', 150.0)
if P.get('east', 1):
    seg = W.line([(UC, VL), (UC, -100)]).intersection(K.buffer(-1.0)); seg = min([g for g in getattr(seg, 'geoms', [seg]) if g.geom_type == 'LineString'], key=lambda g: g.distance(Point(W.xy(UC, VL))))
    vn = min(W.uv(*c)[1] for c in seg.coords) + 1.0
    CL['eastlink'] = (W.line([(US[-1], VL), (UC, VL)]), RW); CL['s_east'] = (W.line([(UC, VL + 4.5), (UC, vn)]), RW)
TH = [Point(W.xy(u, ends[u][1] - 7.0)).buffer(7.5) for u in US] + [Point(W.xy(UW, VWEND - 6.5)).buffer(7.5)]
roads = unary_union([l.buffer(w / 2, cap_style=2, join_style=1) for l, w in CL.values()] + TH).intersection(K)
roads = roads.buffer(4.5, join_style=1).buffer(-4.5, join_style=1).intersection(K).difference(R.buffer(GB))
# ---- reserved
PL = P.get('pl', 24.0); PV = P.get('pv', 84.0)
park = W.rect(US[0] + RW / 2, GU - AW / 2, PV, PV + PL).difference(roads)
club = big(W.rect(GU + AW / 2, US[1] - RW / 2, VS - D, VS).intersection(BUILD).difference(roads))
arow = unary_union([W.rect(-300, 700, A0, A1v).intersection(HPW), E.rect(-300, 700, A0, A1v).intersection(HPE)])
RB_ = roads.buffer(0.3); plots = []
def cut(fr, v0, v1, front, Wt, region, face, tag):
    dep = v1 - v0
    for q in parts(fr.rect(-400, 800, v0, v1).intersection(region)):
        if q.area < 150: continue
        us = [fr.uv(x, y)[0] for x, y in q.exterior.coords]; ua, ub = min(us), max(us); qb = q.buffer(0.03)
        fv_ = v0 - 1.2 if front == 'lo' else v1 + 1.2
        n = int((ub - ua) / 0.1) + 1
        ok = [fr.line([(ua + i * 0.1, v0), (ua + i * 0.1, v1)]).intersection(qb).length / dep >= 0.93 and RB_.contains(Point(fr.xy(ua + i * 0.1, fv_))) for i in range(n)]
        runs = []; i = 0
        while i < n:
            if ok[i]:
                j = i
                while j + 1 < n and ok[j + 1]: j += 1
                runs.append((ua + i * 0.1, ua + j * 0.1)); i = j + 1
            else: i += 1
        for a, b in runs:
            if b - a < MINF: continue
            isr = lambda u: RB_.buffer(0.3).contains(Point(fr.xy(u, (v0 + v1) / 2)))
            ca, cb = isr(a - 2), isr(b + 2); Lr = b - a; k = max(1, int(Lr / Wt + 0.02)); nc = ca + cb
            bonus = min(1.6, max(0, Lr - k * Wt) / nc) if nc and k >= 2 else 0.0
            wds = [(Lr - bonus * nc) / k] * k
            if k >= 2:
                if ca: wds[0] += bonus
                if cb: wds[-1] += bonus
            u = a
            for i_, w_ in enumerate(wds):
                ua_, ub_ = u, u + w_; u += w_; g = big(fr.rect(ua_, ub_, v0, v1).intersection(q)); special = ''
                # an end plot takes the small leftover beyond it (boundary or the meeting of the two grids)
                for cond, ext in ((i_ == 0 and not ca, fr.rect(ua - 1, ub_, v0, v1)), (i_ == len(wds) - 1 and not cb, fr.rect(ua_, ub + 1, v0, v1))):
                    if cond:
                        g2 = big(ext.intersection(q))
                        if g.area + 3 < g2.area <= g.area * 1.5 and g2.area / g2.convex_hull.area > 0.93: g = g2; special = 'end plot: one side follows the boundary'
                if g.area * SQFT < 3000 or g.boundary.intersection(RB_.buffer(0.2)).length < MINF: continue
                plots.append(dict(poly=g, face=face, tag=tag, fr=fr.th, front=front, w=w_, d=dep, v=(v0, v1), corner=(ca and i_ == 0) or (cb and i_ == len(wds) - 1), special=special))
free = BUILD.difference(roads).difference(park).difference(club)
cut(W, A0, A1v, 'lo', 14.2, free.intersection(HPW), 'N', 'stream row'); cut(E, A0, A1v, 'lo', 14.2, free.intersection(HPE), 'N', 'stream row')
inner = free.difference(arow.buffer(0.01))
WT = P.get('wt', 12.8)
for u, h in [(UW, RW / 2)] + [(x, RW / 2) for x in US] + [(GU, AW / 2)] + ([(UC, RW / 2)] if P.get('east', 1) else []):
    cut(W2, h - u, h - u + D, 'lo', WT, inner, 'E', f'street {u:.0f}')          # row west of the street, faces east
    cut(W2, -u - h - D, -u - h, 'hi', WT, inner, 'W', f'street {u:.0f}')       # row east of the street, faces west
used = unary_union([p['poly'] for p in plots] + [roads, park, club]); green = K.difference(used)
pickle.dump(dict(K=K, roads=roads, plots=plots, park=park, club=club, green=green, STRIP=STRIP, CL=CL, GU=GU, VS=VS, US=US, UW=UW, ends=ends, Wo=W.o, Wth=W.th, Eo=E.o, Eth=E.th), open(SP + 'v7/plan9.pkl', 'wb'))
A = [p['poly'].area * SQFT for p in plots]
from collections import Counter
print('K %.2f ac | plots %d | %.0f sq ft = %.1f%% | roads %.1f%% | park %.0f | club %.0f | green %.1f%% | min %.0f max %.0f' % (K.area / 4046.86, len(plots), sum(A), sum(A) / SQFT / K.area * 100, roads.area / K.area * 100, park.area, club.area, green.area / K.area * 100, min(A), max(A)))
print('facing', dict(Counter(p['face'] for p in plots)), '| specials', sum(1 for p in plots if p['special']), '| street ends', {round(k): (round(a), round(b)) for k, (a, b) in ends.items()}, '| roads in strip %.1f' % roads.intersection(R.buffer(GB)).area)
from shapely import contains_xy
from skimage.graph import MCP_Geometric
x0, y0, x1, y1 = K.bounds; xs = np.arange(x0 - 5, x1 + 5, 1.0); ys = np.arange(y0 - 5, y1 + 5, 1.0); XX, YY = np.meshgrid(xs, ys)
rm = contains_xy(roads.buffer(0.6), XX, YY); cost = np.where(rm, 1.0, np.inf)
gxy = W.xy(GU, VS - 1); g0 = min(zip(*np.nonzero(rm)), key=lambda rc: (xs[rc[1]] - gxy[0]) ** 2 + (ys[rc[0]] - gxy[1]) ** 2)
dg, _ = MCP_Geometric(cost).find_costs([g0]); d12, _ = MCP_Geometric(cost).find_costs(list(zip(*np.nonzero(rm & contains_xy(CL['avenue'][0].buffer(6.2), XX, YY)))))
far = far12 = 0
for p in plots:
    z = contains_xy(p['poly'].buffer(1.6).difference(p['poly']), XX, YY) & rm
    if z.any(): far = max(far, dg[z].min()); far12 = max(far12, d12[z].min())
gl = [g for g in parts(green.difference(STRIP)) if g.area > 300]
print('far from gate %.0f m | far from avenue %.0f m | green pieces outside strip (m2):' % (far, far12), sorted([round(g.area) for g in gl], reverse=True)[:8], '| widths ft', dict(Counter(round(p['w'] * FT) for p in plots)))
