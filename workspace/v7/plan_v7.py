"""v7: architect's set-out. Roads first (constant block depth), then plots cut from the blocks."""
exec(open('/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/v7/kit.py').read())
P = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
D = P.get('D', 22.86); RW = 9.0; AW = 12.0; GB = 9.0
W = Fr((144.0, -136.5), 22.94)            # west grid: parallel to the stream between the west corner and the step
E = Fr((258.4, -72.2), P.get('the', 10.40))   # east grid: parallel to the stream along the north-east reach
# levels measured from the stream reference line of each grid
L = {}; v = GB
L['drive'] = (v, v + RW); v += RW
L['A1'] = (v, v + D); v += D; L['A2'] = (v, v + D); v += D
L['s2'] = (v, v + RW); v += RW
L['B1'] = (v, v + D); v += D; L['B2'] = (v, v + D); v += D
L['s3'] = (v, v + RW); v += RW
L['C1'] = (v, v + D); VS = v + D
mid = lambda k: (L[k][0] + L[k][1]) / 2
# hinge (mitre) line: bisector through the meeting point of the two reference lines
def isect(p, d, q, e):
    den = d[0] * e[1] - d[1] * e[0]; t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
    return (p[0] + d[0] * t, p[1] + d[1] * t)
X0 = isect(W.o, W.eu, E.o, E.eu)
bis = (W.ev[0] + E.ev[0], W.ev[1] + E.ev[1]); bl = math.hypot(*bis); bis = (bis[0] / bl, bis[1] / bl)
nE = (-bis[1], bis[0]) if -bis[1] > 0 else (bis[1], -bis[0])
def hp(sign):  # half plane west (-1) or east (+1) of the hinge
    a = (X0[0] - bis[0] * 600, X0[1] - bis[1] * 600); b = (X0[0] + bis[0] * 600, X0[1] + bis[1] * 600)
    return Polygon([a, b, (b[0] + sign * nE[0] * 900, b[1] + sign * nE[1] * 900), (a[0] + sign * nE[0] * 900, a[1] + sign * nE[1] * 900)])
HPW, HPE = hp(-1), hp(+1)
def hinge_u(fr, v):   # where the hinge crosses level v in a frame
    p = fr.xy(0, v); q = isect(p, fr.eu, X0, bis); return fr.uv(*q)[0]
# colony boundary: C without the tab and without the triangle south of the last west row
south = W.rect(-200, 600, VS, VS + 400).intersection(box(0, -400, 343.6, 0))
K = big(C.difference(south).difference(box(299, -290, 323, -261.4)))
STRIP = K.intersection(R.buffer(GB)); BUILD = K.difference(R.buffer(GB))
# ---------------- roads (centre lines) ----------------
GU = P.get('gu', 121.7)                   # avenue position in the west grid (through the gate)
WU = P.get('wu', -23.7)                   # west street centre line
SU = P.get('su', 24.5)                    # south-west street centre line
EU = P.get('eu', 109.1)                   # east street centre line (east grid)
RC = P.get('rc', 31.5); RB = P.get('rb', 12.0)
uHd, uH2, uH3 = hinge_u(W, mid('drive')), hinge_u(W, mid('s2')), hinge_u(W, mid('s3'))
eHd, eH2, eH3 = hinge_u(E, mid('drive')), hinge_u(E, mid('s2')), hinge_u(E, mid('s3'))
def poly_from(frpts):  # list of (frame, pts) -> xy list
    out = []
    for fr, pts in frpts: out += [fr.xy(u, v) for u, v in pts]
    return out
EDR = P.get('edr', 103.4); ES2 = P.get('es2', 158.5); ES3 = P.get('es3', 171.0)
loop = poly_from([(E, [(EDR, mid('drive')), (eHd + 8, mid('drive'))]),
                  (W, [(uHd - 8, mid('drive')), (WU + RC + 0.01, mid('drive'))] + W.arc(WU + RC, mid('drive') + RC, RC, 270, 180)[1:]
                      + [(WU, mid('s2') - RB)] + W.arc(WU + RB, mid('s2') - RB, RB, 180, 90)[1:] + [(uH2 - 8, mid('s2'))]),
                  (E, [(eH2 + 8, mid('s2')), (ES2, mid('s2'))])])
s3 = poly_from([(W, [(SU, mid('s2')), (SU, mid('s3') - RB)] + W.arc(SU + RB, mid('s3') - RB, RB, 180, 90)[1:] + [(uH3 - 8, mid('s3'))]),
                (E, [(eH3 + 8, mid('s3')), (ES3, mid('s3'))])])
def smooth_hinge(pts):   # the two points either side of the hinge become a gentle arc
    return pts
CL = dict(loop=(LineString(loop), RW), s3=(LineString(s3), RW),
          avenue=(W.line([(GU, mid('drive')), (GU, VS)]), AW),
          cross=(LineString([W.xy(uHd, mid('drive')), W.xy(uH3, mid('s3'))]), RW))
def road_poly(l, w): return l.buffer(w / 2, cap_style=2, join_style=1)
TH = [Point(E.xy(P.get('th2u', 151.0), mid('s2') - 3.5)).buffer(8.0), Point(E.xy(P.get('th3u', 165.5), mid('s3') + 3.5)).buffer(8.0)]
roads_raw = unary_union([road_poly(l, w) for l, w in CL.values()] + TH).intersection(K)
KR = P.get('kerb', 4.5)
roads = roads_raw.buffer(KR, join_style=1).buffer(-KR, join_style=1).intersection(K)     # kerb radii at junctions
roads = roads.difference(R.buffer(GB))      # the kerb never crosses the 9 m line (shaves a 0.2 m sliver at the drive's north-east end)
if __name__ == '__main__' and P.get('stage') == 'roads':
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(15, 9), dpi=90)
    for g, c in ((K, '#f3eede'), (STRIP, '#9ccc65'), (roads, '#999')):
        for q in parts(g): ax.fill(*q.exterior.xy, color=c)
    ax.plot(*K.exterior.xy, 'k', lw=1.2); ax.plot(*C.exterior.xy, 'b--', lw=0.5)
    a, b = (X0[0], X0[1]), (X0[0] + bis[0] * 170, X0[1] + bis[1] * 170); ax.plot([a[0], b[0]], [a[1], b[1]], 'r--', lw=0.8)
    for k, (v0, v1) in L.items():
        for fr, u0, u1, hpz in ((W, -40, 230, HPW), (E, 40, 200, HPE)):
            ln = fr.line([(u0, v0), (u1, v0)]).intersection(hpz).intersection(K)
            for q in getattr(ln, 'geoms', [ln]):
                if q.geom_type == 'LineString': ax.plot(*q.xy, color='#c33', lw=0.3)
    ax.set_aspect('equal'); ax.set_xlim(105, 475); ax.set_ylim(-275, -40); plt.tight_layout(); plt.savefig(SP + 'v7/roads.png')
    print('K %.2f ac | roads %.1f%% | strip %.1f%% | VS %.1f | hinge u(W) drive %.1f s2 %.1f s3 %.1f' % (K.area / 4046.86, roads.area / K.area * 100, STRIP.area / K.area * 100, VS, uHd, uH2, uH3))
# ---------------- reserved blocks ----------------
PW = P.get('pw', 33.8)                                    # central park width along the street
park = W.rect(GU - AW / 2 - PW, GU - AW / 2, L['B1'][0], L['B2'][1]).difference(roads)
# the clubhouse plot runs past the foot of Cross Street, so no house plot looks straight down that street
club = big(unary_union([W.rect(GU + AW / 2, 260, L['C1'][0], L['C1'][1]).intersection(HPW), E.rect(60, P.get('club_e', 87.0), L['C1'][0], L['C1'][1]).intersection(HPE)]).intersection(BUILD).difference(roads).buffer(0.05).buffer(-0.05))
reserved = unary_union([park, club])
hinge_line = LineString([(X0[0] - bis[0] * 50, X0[1] - bis[1] * 50), (X0[0] + bis[0] * 400, X0[1] + bis[1] * 400)])
# ---------------- plot rows ----------------
ROWS = [  # name, frame, level key, front side ('lo' = front at smaller v), target frontage, half plane
    ('A1', 'lo', P.get('wA1', 14.2)), ('A2', 'hi', P.get('wA2', 12.25)), ('B1', 'lo', P.get('wB', 12.25)),
    ('B2', 'hi', P.get('wB', 12.25)), ('C1', 'lo', P.get('wC', 13.5))]
MINF = 12.19; COV = P.get('cov', 0.93)
plots = []; RB_ = roads.buffer(0.3)
def cut_row(name, fr, hpz, side, front, Wt):
    v0, v1 = L[name]; dep = v1 - v0
    reg = fr.rect(-300, 700, v0, v1).intersection(hpz).intersection(BUILD).difference(roads).difference(reserved)
    for q in parts(reg):
        if q.area < 150: continue
        us = [fr.uv(x, y)[0] for x, y in q.exterior.coords]; ua, ub = min(us), max(us)
        qb = q.buffer(0.03)
        def cover(u):
            s = fr.line([(u, v0), (u, v1)]).intersection(qb); return s.length / dep
        # scan for the stretch where the row has (nearly) its full depth
        fv_ = v0 - 1.2 if front == 'lo' else v1 + 1.2
        def has_road(u): return RB_.contains(Point(fr.xy(u, fv_)))
        step = 0.1; n = int((ub - ua) / step) + 1; ok = [cover(ua + i * step) >= COV and has_road(ua + i * step) for i in range(n)]
        runs = []; i = 0
        while i < n:
            if ok[i]:
                j = i
                while j + 1 < n and ok[j + 1]: j += 1
                runs.append((ua + i * step, ua + j * step)); i = j + 1
            else: i += 1
        for a, b in runs:
            if b - a < MINF: continue
            touches_h = q.distance(hinge_line) < 5.2
            mitre_end = None
            if touches_h:
                hu = hinge_u(fr, (v0 + v1) / 2); off = (RW / 2) / math.cos(math.radians(abs(W.th - E.th) / 2))
                if abs(hu - off - b) < 6: mitre_end = 'b'; b = hu - off
                elif abs(hu + off - a) < 6: mitre_end = 'a'; a = hu + off
            def is_road(u): return roads.buffer(0.5).contains(Point(fr.xy(u, (v0 + v1) / 2)))
            ca, cb = is_road(a - 2.0), is_road(b + 2.0)
            Lr = b - a; k = max(1, int(Lr / Wt + 0.02)); extra = Lr - k * Wt
            if P.get('dbg'): print('%s %s run %.1f m -> %d plots (target %.2f) a %.1f b %.1f mitre %s piece u %.1f..%.1f' % (name, 'W' if fr is W else 'E', Lr, k, Wt, a, b, mitre_end, ua, ub))
            if extra < 0: wds = [Lr / k] * k
            else:
                nc = (1 if ca else 0) + (1 if cb else 0)
                bonus = min(P.get('cbonus', 1.6), extra / nc) if nc and k >= 2 else 0.0
                base = (Lr - bonus * nc) / k
                wds = [base] * k
                if k >= 2:
                    if ca: wds[0] += bonus
                    if cb: wds[-1] += bonus
            if mitre_end and front == 'hi' and len(wds) > 1:      # skew corner plot whose street front is its narrow side: keep that front above 12.2 m
                idx = len(wds) - 1 if mitre_end == 'b' else 0
                need = MINF + 1.45 - wds[idx]
                for j in sorted([j for j in range(len(wds)) if j != idx], key=lambda j: -wds[j]):   # take it from the widest neighbours
                    if need <= 1e-9: break
                    t_ = min(need, max(0.0, wds[j] - (MINF + 0.06)))
                    wds[j] -= t_; wds[idx] += t_; need -= t_
            u = a
            for i_, w_ in enumerate(wds):
                ua_, ub_ = u, u + w_
                if mitre_end == 'b' and i_ == len(wds) - 1: ub_ = ub + 8
                if mitre_end == 'a' and i_ == 0: ua_ = ua - 8
                g = big(fr.rect(ua_, ub_, v0, v1).intersection(q))
                u += w_
                fv = v0 if front == 'lo' else v1
                fl = g.boundary.intersection(RB_.buffer(0.2)).length      # all kerb contact, so a corner's rounded kerb counts
                fr_ok = fl >= MINF - 0.3 and roads.buffer(0.4).intersects(fr.line([(max(ua_, a), fv), (min(ub_, b), fv)]))
                if not fr_ok or g.area * SQFT < P.get('minsq', 3000):
                    if P.get('dbg'): print('   REJECT %s %s plot %d of %d: front %.1f m, area %.0f sq ft, w %.2f' % (name, 'W' if fr is W else 'E', i_ + 1, len(wds), fl, g.area * SQFT, w_))
                    continue
                plots.append(dict(poly=g, row=name, side=side, frame=fr, front=front, w=w_, d=dep, v=(v0, v1), u=(ua_, ub_),
                                  corner=(ca and i_ == 0) or (cb and i_ == len(wds) - 1), mitre=(mitre_end == 'b' and i_ == len(wds) - 1) or (mitre_end == 'a' and i_ == 0)))
for name, front, Wt in ROWS:
    cut_row(name, W, HPW, 'W', front, Wt)
    cut_row(name, E, HPE, 'E', front, P.get('wE_' + name, Wt))
if P.get('v8'):
    # (a) one more plot beside old plot 7, taken from the east end of the clubhouse land
    c1e = sorted([p for p in plots if p['row'] == 'C1' and p['frame'] is E], key=lambda p: p['u'][0])
    c1e = sorted(c1e, key=lambda p: p['poly'].centroid.x); u7 = min(E.uv(x, y)[0] for x, y in c1e[0]['poly'].exterior.coords); uw = P.get('new_uw', 72.0)
    npoly = big(E.rect(uw, u7, L['s3'][0] + 1.0, 220).intersection(BUILD).difference(roads)).simplify(0.05).intersection(BUILD.buffer(-0.02))
    club = big(club.difference(npoly.buffer(0.02)))
    plots.append(dict(poly=npoly, row='C1', side='E', frame=E, front='lo', w=npoly.boundary.intersection(RB_.buffer(0.2)).length - 1.0, d=L['C1'][1] - L['C1'][0], v=L['C1'], u=(uw, u7),
                      corner=False, mitre=False, special='beside the clubhouse: front follows the bend of Third Street, back follows the boundary', isnew=True))
    # (b) the north-east garden goes into the plots around it
    a1e = sorted([p for p in plots if p['row'] == 'A1' and p['frame'] is E], key=lambda p: p['u'][0])
    a2e = sorted([p for p in plots if p['row'] == 'A2' and p['frame'] is E], key=lambda p: p['u'][0])
    last, p60, p61 = a1e[-1], a2e[-2], a2e[-1]
    ext = big(E.rect(last['u'][0], p60['u'][0], L['A1'][0], L['A1'][1]).intersection(BUILD).difference(roads)).simplify(0.05).intersection(BUILD.buffer(-0.02))
    last['poly'] = ext; last['special'] = 'double-width plot at the end of Stream Drive; north-east corner cut by the boundary'
    for p_, txt in ((p60, 'extended back to the boundary: slanted back wall'), (p61, 'small extension at the back corner')):
        g_ = big(E.rect(p_['u'][0], p_['u'][1], -40, L['A2'][1]).intersection(BUILD).difference(roads).difference(ext.buffer(0.02))).simplify(0.05).intersection(BUILD.buffer(-0.02))
        p_['poly'] = g_; p_['special'] = txt
used = unary_union([p['poly'] for p in plots] + [roads, park, club])
green = K.difference(used)
res = dict(K=K, C=C, roads=roads, plots=plots, park=park, club=club, green=green, STRIP=STRIP, L=L, CL=CL, VS=VS, X0=X0, bis=bis, GU=GU, P=P,
           Wo=W.o, Wth=W.th, Eo=E.o, Eth=E.th)
for p in plots: p['frame'] = 'W' if p['frame'] is W else 'E'
pickle.dump(res, open(SP + 'v7/' + P.get('out', 'plan') + '.pkl', 'wb'))
A = [p['poly'].area * SQFT for p in plots]
from collections import Counter
print('K %.2f ac | plots %d | %.0f sq ft = %.1f%% | roads %.1f%% | park %.0f m2 | club %.0f m2 | green %.1f%% | min %.0f max %.0f' % (
    K.area / 4046.86, len(plots), sum(A), sum(A) / SQFT / K.area * 100, roads.area / K.area * 100, park.area, club.area, green.area / K.area * 100, min(A), max(A)))
print(dict(Counter(p['side'] + p['row'] for p in plots)))
