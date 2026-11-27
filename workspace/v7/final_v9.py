"""Final set for layout v9 (no south-facing plots): master plan, dimension sheets, schedule, CSV, DXF."""
exec(open('/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/v7/kit.py').read())
import numpy as np, csv, random, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.path import Path; from matplotlib.patches import PathPatch, Circle, Ellipse, RegularPolygon
from shapely.affinity import affine_transform
from shapely import contains_xy
from skimage.graph import MCP_Geometric
from collections import Counter
V = pickle.load(open(SP + 'v7/plan9.pkl', 'rb')); K, roads, park, club, green, STRIP, CL = V['K'], V['roads'], V['park'], V['club'], V['green'], V['STRIP'], V['CL']
W = Fr(V['Wo'], V['Wth']); E = Fr(V['Eo'], V['Eth']); W2 = Fr(W.o, W.th - 90); GU, VS, US, UW = V['GU'], V['VS'], V['US'], V['UW']; D = 22.86
st = pickle.load(open(SP + 'brochure2/stream08.pkl', 'rb'))['stream']
OUTF = '/home/user/Data-tool/site_plans/final_v9/'; os.makedirs(OUTF, exist_ok=True)
frame_of = lambda p: W if abs(p['fr'] - W.th) < 0.01 else E if abs(p['fr'] - E.th) < 0.01 else W2
SNAME = {f'street {UW:.0f}': 'West Street', f'street {US[0]:.0f}': 'First Street', f'street {GU:.0f}': 'The Avenue', f'street {US[1]:.0f}': 'Second Street', f'street {US[2]:.0f}': 'Third Street', 'stream row': 'Stream Drive'}
SORD = ['Stream Drive', 'West Street', 'First Street', 'The Avenue', 'Second Street', 'Third Street']
FACE = dict(N='North', E='East', W='West')
plots = V['plots']
for p in plots:
    p['street'] = SNAME[p['tag']]; c = p['poly'].centroid; p['uv'] = W.uv(c.x, c.y)
plots.sort(key=lambda p: (SORD.index(p['street']), 0 if p['face'] != 'W' else 1, p['uv'][0] if p['face'] == 'N' else p['uv'][1]))
RBUF = roads.buffer(0.5)
gardenN = green.intersection(W.rect(GU - 25, 240, -40, 9.0)).buffer(0); lawnW = green.intersection(W.rect(-80, US[0] - 4.5 - D - 0.3, 41, 220)).buffer(0)
grove = green.intersection(W.rect(US[2] + 4.5 + D, 400, 20, 220)).difference(STRIP).buffer(0); svc = big(green.intersection(W.rect(US[1] - 4.5 - D, US[2] - 4.5, VS - 12, 220)).buffer(-1).buffer(1))
x0, y0, x1, y1 = K.bounds; xs = np.arange(x0 - 5, x1 + 5, 1.0); ys = np.arange(y0 - 5, y1 + 5, 1.0); XX, YY = np.meshgrid(xs, ys)
rm = contains_xy(roads.buffer(0.6), XX, YY); cost = np.where(rm, 1.0, np.inf); gxy = W.xy(GU, VS - 1)
g0 = min(zip(*np.nonzero(rm)), key=lambda rc: (xs[rc[1]] - gxy[0]) ** 2 + (ys[rc[0]] - gxy[1]) ** 2)
dg, _ = MCP_Geometric(cost).find_costs([g0]); d12, _ = MCP_Geometric(cost).find_costs(list(zip(*np.nonzero(rm & contains_xy(CL['avenue'][0].buffer(6.2), XX, YY)))))
for i, p in enumerate(plots):
    g = p['poly']; p['no'] = i + 1; p['area'] = g.area * SQFT; fr = frame_of(p)
    z = contains_xy(g.buffer(1.6).difference(g), XX, YY) & rm; p['gate_m'] = float(dg[z].min()); p['d12'] = float(d12[z].min())
    us = [fr.uv(x, y)[0] for x, y in g.exterior.coords]; vs = [fr.uv(x, y)[1] for x, y in g.exterior.coords]; p['box'] = (min(us), max(us), min(vs), max(vs))
    ds = [fr.line([(u, -400), (u, 400)]).intersection(g).length for u in np.linspace(min(us) + 0.7, max(us) - 0.7, 7)]; p['dmin'], p['dmax'] = min(ds), max(ds)
    p['rect'] = (not p['special']) and (p['dmax'] - p['dmin'] < 0.8 or p['corner'])
    notes = []
    if p['special']: notes.append(p['special'])
    elif not p['rect']: notes.append('irregular'); 
    if p['corner']: notes.append('corner')
    if p['face'] == 'N': notes.append('stream-facing')
    if g.distance(park) < 10.5: notes.append('on the Central Park')
    if g.distance(lawnW.difference(STRIP)) < 1 or g.distance(grove) < 1: notes.append('garden behind')
    if g.distance(svc) < 1: notes.append('next to services yard')
    if g.distance(club) < 1: notes.append('next to clubhouse')
    p['notes'] = notes
tot = sum(p['area'] for p in plots); NA = K.area; fc = Counter(p['face'] for p in plots)
ft = lambda m: f"{m * FT:.1f}'"
def up(a): return (a + 90) % 180 - 90
def labels(p):
    g = p['poly']; fr = frame_of(p); out = []; u0, u1, v0, v1 = p['box']
    if p['rect']:
        v0n, v1n = p['v']; fv, s = (v0n, 1) if p['front'] == 'lo' else (v1n, -1)
        out.append((*fr.xy((u0 + u1) / 2, fv + s * 1.7), fr.th, ft(p['w']))); out.append((*fr.xy(u0 + 1.7, (v0n + v1n) / 2), fr.th + 90, ft(p['d']))); return out
    q = g.simplify(0.35); cs = list(q.exterior.coords); ccw = q.exterior.is_ccw
    for a, b in zip(cs[:-1], cs[1:]):
        ln = math.dist(a, b)
        if ln < 2.6: continue
        nx, ny = -(b[1] - a[1]) / ln, (b[0] - a[0]) / ln
        if not ccw: nx, ny = -nx, -ny
        out.append(((a[0] + b[0]) / 2 + nx * 1.7, (a[1] + b[1]) / 2 + ny * 1.7, math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])), ft(ln)))
    return out
class Sheet:
    def __init__(s, fr=None):
        if fr is None: s.M = [1, 0, 0, 1, 0, 0]; s.rot = 0.0
        else: ox, oy = fr.o; s.M = [fr.eu[0], fr.eu[1], -fr.ev[0], -fr.ev[1], -(fr.eu[0] * ox + fr.eu[1] * oy), fr.ev[0] * ox + fr.ev[1] * oy]; s.rot = fr.th
    def g(s, geom): return affine_transform(geom, s.M)
    def pt(s, x, y): a, b, d, e, xo, yo = s.M; return (a * x + b * y + xo, d * x + e * y + yo)
COL = dict(N='#cfe6f7', E='#dcefd0', W='#fbe6c8')
def mk_fp(ax, S):
    def fp(g, z=1, **k):
        for q in parts(S.g(g)):
            verts = []; codes = []
            for ring in [q.exterior] + list(q.interiors):
                c = np.array(ring.coords); verts += list(c); codes += [Path.MOVETO] + [Path.LINETO] * (len(c) - 2) + [Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(verts, codes), zorder=z, **k))
    return fp
def base(ax, S, fs_no=7.5, dims=True, fs_dim=5.0, area=True, pretty=False):
    fp = mk_fp(ax, S)
    fp(R, fc='#e3f0f8', ec='none'); fp(st, fc='#7db9de', ec='none'); fp(unary_union([RS, C.difference(K)]), fc='#f4efe2', ec='none')
    fp(K, z=2, fc='#cfe7ba', ec='none'); fp(STRIP, z=2.1, fc='#bfe0a8', ec='#8dbb76', hatch='...' if not pretty else None, lw=0)
    fp(park, z=2.5, fc='#a9d98e', ec='#6a9a55', lw=0.5); fp(roads, z=3, fc='#d2cfc9' if not pretty else '#b9b6b0', ec='#8d8a84', lw=0.4); fp(club, z=3, fc='#efdfc0', ec='#9b7b4b', lw=0.6)
    for p in plots:
        q = S.g(p['poly']); ax.fill(*q.exterior.xy, color=COL[p['face']], ec='#5c4a2e', lw=0.6, zorder=4)
        c = p['poly'].representative_point() if not p['rect'] else p['poly'].centroid; cx, cy = S.pt(c.x, c.y); fr = frame_of(p); rot = up((fr.th + (90 if fr is W2 else 0)) - S.rot)
        if area:
            a_ = math.radians(rot + 90); dx, dy = math.cos(a_), math.sin(a_)
            ax.text(cx + dx * 1.7, cy + dy * 1.7, str(p['no']), fontsize=fs_no, weight='bold', ha='center', va='center', zorder=7, color='#2b2014', rotation=rot, clip_on=True)
            ax.text(cx - dx * 1.9, cy - dy * 1.9, f"{p['area']:,.0f} sq ft", fontsize=fs_dim, ha='center', va='center', zorder=7, color='#2b2014', rotation=rot, clip_on=True)
        if dims:
            for x, y, a, t in labels(p):
                X, Y = S.pt(x, y); ax.text(X, Y, t, fontsize=fs_dim, ha='center', va='center', zorder=7, color='#b3261e', rotation=up(a - S.rot), clip_on=True)
    ax.plot(*S.g(K).exterior.xy, color='#b3261e', lw=1.8, zorder=8); return fp
def names(ax, S, fs=6.5, col='#333'):
    def T(u, v, s, extra=0, **k):
        X, Y = S.pt(*W.xy(u, v)); ax.text(X, Y, s, rotation=up(W.th + extra - S.rot), ha='center', va='center', zorder=9, clip_on=True, fontsize=k.pop('fontsize', fs), weight='bold', color=k.pop('color', col), **k)
    T(35, 13.5, 'STREAM DRIVE  9 m'); T(140, 13.5, 'STREAM DRIVE  9 m')
    for u, nm in ((UW, 'WEST STREET  9 m'), (US[0], 'FIRST STREET  9 m'), (GU, 'THE AVENUE  12 m'), (US[1], 'SECOND STREET  9 m'), (US[2], 'THIRD STREET  9 m')):
        T(u, 72 if u != UW else 62, nm, extra=90)
        if u not in (UW,): T(u, 122 if u != US[1] else 118, nm, extra=90)
    pu, pv = W.uv(park.centroid.x, park.centroid.y); T(pu, pv, 'CENTRAL PARK\n150 × 79 ft  (45.7 × 24.0 m)\n%s m²' % f'{park.area:,.0f}', color='#12360f')
    cc = club.representative_point(); T(*W.uv(cc.x, cc.y), f'CLUBHOUSE\n{club.area:,.0f} m²', color='#6a4a20')
    T(GU + 45, 0.5, 'STREAM GARDEN', color='#1e4a22'); lp = big(lawnW.difference(STRIP).buffer(-4)).representative_point(); T(*W.uv(lp.x, lp.y), 'STREAM\nLAWN', color='#1e4a22')
    gp = big(grove.buffer(-4)).representative_point(); T(*W.uv(gp.x, gp.y), 'EAST\nGROVE', color='#1e4a22'); sp = svc.representative_point(); T(*W.uv(sp.x, sp.y), 'SERVICES', fontsize=fs - 1)
    T(GU + 14, VS + 3.5, 'GATE', fontsize=fs + 2, color='#2b2014')
def north(ax, S, x, y, size=9):
    a = math.radians(90 - S.rot); dx, dy = math.cos(a) * size, math.sin(a) * size
    ax.annotate('', xy=(x + dx, y + dy), xytext=(x, y), arrowprops=dict(arrowstyle='-|>', color='k', lw=1.6), zorder=10); ax.text(x + dx * 1.25, y + dy * 1.25, 'N', ha='center', va='center', fontsize=11, weight='bold')
FOOT = 'Concept layout for the owner. Dimensions are computed from the survey outline; a licensed surveyor must set out on site before any sale or submission.'
exec(open(SP + 'v7/final_v9_pages.py').read())
