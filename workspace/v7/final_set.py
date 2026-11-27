"""Final drawing set for layout v8: key dimensions, three enlarged dimensioned sheets, plot schedule, DXF."""
import sys, os; os.environ.setdefault('TAG', '8'); sys.path.insert(0, '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/v7')
import render_v7 as rv
from render_v7 import *
from shapely.affinity import affine_transform
import matplotlib.patheffects as pe
V = rv.V; info = rv.info; NA = K.area; green = V['green']
OUTF = '/home/user/Data-tool/site_plans/final/'; os.makedirs(OUTF, exist_ok=True)
WU, RC, RB, SU = -23.7, 31.5, 12.0, 24.5
ft = lambda m: f"{m * FT:.1f}'"
SKEW = math.radians(abs(W.th - E.th) / 2)
def labels(p):
    """(x, y, angle, text) for the side lengths of one plot, in plan coordinates"""
    g = p['poly']; fr = FR[p['grid']]; out = []
    us = [fr.uv(x, y)[0] for x, y in g.exterior.coords]; vs = [fr.uv(x, y)[1] for x, y in g.exterior.coords]
    u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs); fv, bv = (v0, v1) if p['front'] == 'lo' else (v1, v0); s = 1 if p['front'] == 'lo' else -1
    if p.get('special'):
        q = g.simplify(0.35); cs = list(q.exterior.coords); ccw = q.exterior.is_ccw
        for a, b in zip(cs[:-1], cs[1:]):
            ln = math.dist(a, b)
            if ln < 2.6: continue
            ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])); nx, ny = -(b[1] - a[1]) / ln, (b[0] - a[0]) / ln
            if not ccw: nx, ny = -nx, -ny
            out.append(((a[0] + b[0]) / 2 + nx * 1.7, (a[1] + b[1]) / 2 + ny * 1.7, ang, ft(ln)))
        return out
    um = (u0 + u1) / 2; vm = (v0 + v1) / 2
    if 'cross' in p['shape']:
        dl, dr = fr.xy(u0, vm), fr.xy(u1, vm); skew_left = CL['cross'][0].distance(Point(dl)) < CL['cross'][0].distance(Point(dr))
        fw, bw = p['front_w'], p['back_w']
        # widths are measured from the straight side
        ust = u1 if skew_left else u0; sg = -1 if skew_left else 1
        out.append((*fr.xy(ust + sg * fw / 2, fv + s * 1.7), fr.th, ft(fw))); out.append((*fr.xy(ust + sg * bw / 2, bv - s * 1.7), fr.th, ft(bw)))
        out.append((*fr.xy(ust + sg * 1.7, vm), fr.th + 90, ft(p['depth'])))
        out.append((*fr.xy(ust + sg * ((fw + bw) / 2 - 1.9), vm), fr.th + 90, ft(p['depth'] / math.cos(SKEW))))
        return out
    out.append((*fr.xy(um, fv + s * 1.7), fr.th, ft(p['front_w'])))
    out.append((*fr.xy(u0 + 1.7, vm), fr.th + 90, ft(p['depth'])))
    return out
def up(a):
    a = (a + 90) % 180 - 90
    return a
class Sheet:
    def __init__(s, fr=None):
        s.fr = fr
        if fr is None: s.M = [1, 0, 0, 1, 0, 0]; s.rot = 0.0
        else:
            ox, oy = fr.o; s.M = [fr.eu[0], fr.eu[1], -fr.ev[0], -fr.ev[1], -(fr.eu[0] * ox + fr.eu[1] * oy), fr.ev[0] * ox + fr.ev[1] * oy]; s.rot = fr.th
    def g(s, geom): return affine_transform(geom, s.M)
    def pt(s, x, y): a, b, d, e, xo, yo = s.M; return (a * x + b * y + xo, d * x + e * y + yo)
def base(ax, S, fs_no=7.5, dims=True, fs_dim=5.0, area=True):
    def fp(g, z=1, **k):
        for q in parts(S.g(g)):
            verts = []; codes = []
            for ring in [q.exterior] + list(q.interiors):
                c = np.array(ring.coords); verts += list(c); codes += [Path.MOVETO] + [Path.LINETO] * (len(c) - 2) + [Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(verts, codes), zorder=z, **k))
    fp(R, fc='#e6f1f8', ec='none'); fp(st, fc='#8dc0e0', ec='none'); fp(unary_union([RS, C.difference(K)]), fc='#f4efe2', ec='none')
    fp(K, z=2, fc='#d3e9c0', ec='none'); fp(STRIP, z=2.1, fc='#c3e2ad', ec='#8dbb76', hatch='...', lw=0)
    fp(park, z=2.5, fc='#b3dc98', ec='#6a9a55', lw=0.5); fp(roads, z=3, fc='#d6d3cd', ec='#8d8a84', lw=0.4); fp(club, z=3, fc='#efdfc0', ec='#9b7b4b', lw=0.6)
    for p in info:
        q = S.g(p['poly']); ax.fill(*q.exterior.xy, color='#fffaf0' if p['front'] == 'lo' else '#fbe9e4', ec='#6b5332', lw=0.6, zorder=4)
        c = p['poly'].centroid; cx, cy = S.pt(c.x, c.y); rot = up(FR[p['grid']].th - S.rot)
        if area:
            ax.text(cx, cy + 1.6, str(p['no']), fontsize=fs_no, weight='bold', ha='center', va='center', zorder=7, color='#2b2014', rotation=rot)
            ax.text(cx, cy - 1.9, f"{p['area']:,.0f} sq ft", fontsize=fs_dim, ha='center', va='center', zorder=7, color='#2b2014', rotation=rot)
            ax.text(cx, cy - 4.0, f"{p['area'] / SQFT:.1f} m²", fontsize=fs_dim - 0.8, ha='center', va='center', zorder=7, color='#6b5a3e', rotation=rot)
        if dims:
            for x, y, a, t in labels(p):
                X, Y = S.pt(x, y); ax.text(X, Y, t, fontsize=fs_dim, ha='center', va='center', zorder=7, color='#b3261e', rotation=up(a - S.rot))
    kq = S.g(K); ax.plot(*kq.exterior.xy, color='#b3261e', lw=1.8, zorder=8)
    return fp
def road_names(ax, S, fs=6.5):
    def T(fr, u, v, s, extra=0, **k):
        X, Y = S.pt(*fr.xy(u, v)); ax.text(X, Y, s, rotation=up(fr.th + extra - S.rot), ha='center', va='center', zorder=9, fontsize=fs, weight='bold', color='#333', **k)
    T(W, 55, mid('drive'), 'STREAM DRIVE  9.0 m'); T(W, 162, mid('drive'), 'STREAM DRIVE  9.0 m'); T(W, 58, mid('s2'), 'SECOND STREET  9.0 m'); T(W, 158, mid('s2'), 'SECOND STREET  9.0 m')
    T(W, 75, mid('s3'), 'THIRD STREET  9.0 m'); T(W, 158, mid('s3'), 'THIRD STREET  9.0 m'); T(E, 118, mid('s2'), 'SECOND STREET  9.0 m'); T(E, 125, mid('s3'), 'THIRD STREET  9.0 m')
    T(W, GU, 95, 'THE AVENUE  12.0 m', extra=90); T(W, GU, 45, 'THE AVENUE  12.0 m', extra=90); T(W, WU, 50, 'WEST LOOP  9.0 m', extra=90); T(W, SU, 95, '9.0 m', extra=90)
    c = CL['cross'][0]
    for f in (0.25, 0.72):
        q = c.interpolate(f, normalized=True); X, Y = S.pt(q.x, q.y); ax.text(X, Y, 'CROSS STREET  9.0 m', rotation=up(-73.3 - S.rot), ha='center', va='center', zorder=9, fontsize=fs, weight='bold', color='#333')
    pu, pv = W.uv(park.centroid.x, park.centroid.y); PWd = park.area / (L['B2'][1] - L['B1'][0])
    X, Y = S.pt(*W.xy(pu, pv)); ax.text(X, Y, f"CENTRAL PARK\n{PWd:.1f} × {L['B2'][1] - L['B1'][0]:.1f} m\n({PWd * FT:.0f} × {(L['B2'][1] - L['B1'][0]) * FT:.0f} ft)\n{park.area:,.0f} m²", rotation=up(W.th - S.rot), ha='center', va='center', zorder=9, fontsize=fs, color='#1e4a22', weight='bold')
    cc = club.representative_point(); X, Y = S.pt(cc.x, cc.y); ax.text(X, Y, f'CLUBHOUSE\n{club.area:,.0f} m²', rotation=up(W.th - S.rot), ha='center', va='center', zorder=9, fontsize=fs, color='#6a4a20', weight='bold')
    X, Y = S.pt(*W.xy(GU + 30, 1.0)); ax.text(X, Y, 'STREAM GARDEN', rotation=up(W.th - S.rot), ha='center', va='center', zorder=9, fontsize=fs, color='#1e4a22', weight='bold')
    X, Y = S.pt(*W.xy(60, 4.5)); ax.text(X, Y, '9.0 m no-build strip from the stream (dotted)', rotation=up(W.th - S.rot), ha='center', va='center', zorder=9, fontsize=fs - 1.2, color='#1e4a22', style='italic')
    lw_ = big(V['lawnW'].difference(STRIP).buffer(-5)).representative_point(); X, Y = S.pt(lw_.x, lw_.y); ax.text(X, Y, 'STREAM\nLAWN', ha='center', va='center', zorder=9, fontsize=fs, color='#1e4a22', weight='bold', rotation=up(W.th - S.rot))
    sv = V['svc'].representative_point(); X, Y = S.pt(sv.x, sv.y); ax.text(X, Y, 'SERVICES', ha='center', va='center', zorder=9, fontsize=fs - 1, color='#333', rotation=up(E.th - S.rot))
    X, Y = S.pt(*W.xy(GU + 13, rv.VS + 3.5)); ax.text(X, Y, 'GATE', ha='center', va='center', zorder=9, fontsize=fs + 2, weight='bold', color='#2b2014', rotation=up(W.th - S.rot))
def north(ax, S, x, y, size=9):
    a = math.radians(90 - S.rot); dx, dy = math.cos(a) * size, math.sin(a) * size
    ax.annotate('', xy=(x + dx, y + dy), xytext=(x, y), arrowprops=dict(arrowstyle='-|>', color='k', lw=1.6), zorder=10); ax.text(x + dx * 1.25, y + dy * 1.25, 'N', ha='center', va='center', fontsize=11, weight='bold')
def scalebar(ax, x, y):
    ax.plot([x, x + 20], [y, y], color='k', lw=2.2); ax.plot([x, x], [y - 1, y + 1], color='k', lw=1); ax.plot([x + 20, x + 20], [y - 1, y + 1], color='k', lw=1); ax.text(x + 10, y - 3.2, '20 m  (65.6 ft)', ha='center', fontsize=7)
def title(fig, n, t, sub):
    fig.text(0.012, 0.975, f'JALKOTI COLONY — FINAL LAYOUT    Sheet {n} of 6', fontsize=13, weight='bold', color='#1e3a2b', va='top')
    fig.text(0.012, 0.95, t + '.  ' + sub, fontsize=8.6, color='#444', va='top')
    fig.text(0.988, 0.012, 'Concept layout for the owner. Dimensions are computed from the survey outline; a licensed surveyor must set out on site before any sale or submission.', fontsize=6.2, color='#666', ha='right')
exec(open('/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/v7/final_pages.py').read())
