"""Landscape plan for v8: same plots and roads, landscape drawn on the green land and the road verges only."""
import sys, os; os.environ.setdefault('TAG', '8'); sys.path.insert(0, '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/v7')
import render_v7 as rv
from render_v7 import *
from matplotlib.patches import Ellipse, Polygon as MPoly
import matplotlib.patheffects as pe
V = rv.V; info = rv.info; NA = K.area; green = V['green']; rest = V['rest']
random.seed(4)
GREENS = ['#4f8a3a', '#5b9744', '#6aa34f', '#3f7a33', '#77ad58']
RIP = ['#3c7340', '#4a8249', '#2f6638', '#5a9150']
def chaik(c, n=2):
    for _ in range(n):
        new = [c[0]]
        for p, q in zip(c[:-1], c[1:]): new += [(0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]), (0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1])]
        new.append(c[-1]); c = new
    return c
def lines_of(g): return [q for q in getattr(g, 'geoms', [g]) if q.geom_type == 'LineString' and q.length > 1]
fig = plt.figure(figsize=(16.54, 11.69)); ax = fig.add_axes([0.006, 0.285, 0.762, 0.705])
def fp(g, z=1, **k):
    for q in parts(g):
        verts = []; codes = []
        for ring in [q.exterior] + list(q.interiors):
            c = np.array(ring.coords); verts += list(c); codes += [Path.MOVETO] + [Path.LINETO] * (len(c) - 2) + [Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(verts, codes), zorder=z, **k))
def tree(x, y, r, cols=GREENS, z=7, flower=None):
    ax.add_patch(Ellipse((x + r * 0.45, y - r * 0.45), r * 2.05, r * 2.05, color='#20351f', alpha=0.16, zorder=z - 0.2, lw=0))
    c = flower or random.choice(cols)
    ax.add_patch(Circle((x, y), r, fc=c, ec='#2f5a2a' if not flower else '#ffffff', lw=0.25, zorder=z))
    ax.add_patch(Circle((x - r * 0.25, y + r * 0.25), r * 0.55, fc='#ffffff', alpha=0.20 if not flower else 0.35, lw=0, zorder=z + 0.1))
def path(line, w=1.8, col='#ecdcb3', z=4.5, ec='#b9a678'):
    fp(line.buffer(w / 2, cap_style=1, join_style=1), z=z, fc=col, ec=ec, lw=0.3)
FL = dict(pink='#e79ab3', gold='#f1cb5c', lilac='#b7a0dc', flame='#ee8f5a', white='#f6f1e4')
# ---------- base
ax.set_facecolor('#ffffff')
fp(R, fc='#dfeef7', ec='none'); fp(st, fc='#74b3db', ec='none'); fp(st.buffer(-3.5), fc='#8cc3e6', ec='none'); fp(st.buffer(-7), fc='#a3d0ec', ec='none')
fp(unary_union([RS, C.difference(K)]), fc='#f3eddd', ec='none'); fp(access, fc='#cfcbc3', ec='none')
ax.add_patch(PathPatch(Path([W.xy(GU - 6, VS), W.xy(GU + 6, VS), (337.5, -262), (324.5, -262), W.xy(GU - 6, VS)], [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]), fc='#cfcbc3', ec='none', zorder=1))
fp(K, z=2, fc='#b4d99a', ec='none')
fp(STRIP, z=2.1, fc='#a6cf8d', ec='none')
# ---------- roads: verge (paver footpath) + asphalt carriageway
carr = unary_union([l.buffer(3.5 if w >= 12 else 3.0, cap_style=2, join_style=1) for l, w in CL.values()] + [roads.buffer(-1.5)]).buffer(2.5, join_style=1).buffer(-2.5, join_style=1).intersection(roads.buffer(-1.2))
ave_line = CL['avenue'][0]; ave_band = ave_line.buffer(6.0, cap_style=2)
others = unary_union([l.buffer(3.0, cap_style=2, join_style=1) for nm, (l, w) in CL.items() if nm != 'avenue'])
carr = carr.difference(ave_band.difference(ave_line.buffer(3.5, cap_style=2)).difference(others.buffer(1.5)))
fp(roads, z=3, fc='#e3dccb', ec='#b9b09a', lw=0.3)
fp(carr, z=3.2, fc='#9b9a97', ec='none')
names = list(CL); jpts = []
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a, b = CL[names[i]][0], CL[names[j]][0]
        x = a.intersection(b)
        for q in getattr(x, 'geoms', [x]):
            if q.geom_type == 'Point': jpts.append(q)
        for e in (a.coords[0], a.coords[-1]):
            if b.distance(Point(e)) < 0.6: jpts.append(Point(e))
        for e in (b.coords[0], b.coords[-1]):
            if a.distance(Point(e)) < 0.6: jpts.append(Point(e))
jp = []
for q in jpts:
    if all(q.distance(o) > 6 for o in jp): jp.append(q)
for q in jp: fp(q.buffer(7.2).intersection(carr), z=3.4, fc='#cfa783', ec='#a88462', lw=0.3)
# entrance court at the gate
court = W.rect(GU - 6, GU + 6, VS - 17, VS).intersection(roads); fp(court, z=3.5, fc='#d2ab86', ec='#a88462', lw=0.3)
isl = Point(W.xy(GU, VS - 8.5)).buffer(1.0).union(Point(W.xy(GU, VS - 5.5)).buffer(1.0)).union(Point(W.xy(GU, VS - 11.5)).buffer(1.0)).convex_hull
fp(isl, z=3.6, fc='#9ccf7c', ec='#ffffff', lw=0.5)
# ---------- plots
for p in info:
    g = p['poly']; ax.fill(*g.exterior.xy, color='#fbf5e6' if p['front'] == 'lo' else '#f7e3dc', ec='#a58a5e', lw=0.45, zorder=4)
    c = g.centroid; ax.text(c.x, c.y, str(p['no']), fontsize=5.0, ha='center', va='center', zorder=6.5, color='#6b5a3e', rotation=FR[p['grid']].th)
fp(club, z=3.8, fc='#ecdcbc', ec='#a58a5e', lw=0.45)
# ---------- stream promenade: walking track with seats, riverside trees
inner = K.buffer(-4.6, join_style=1).exterior.intersection(STRIP.buffer(0.3))
track = []
for l in lines_of(inner):
    if l.length > 25:
        t = LineString(chaik(list(l.simplify(1.2).coords))); track.append(t); path(t, w=2.0)
for off, ev, rr in ((-1.9, 8.0, 2.3), (-7.6, 10.0, 1.9)):
    ln = K.buffer(off, join_style=1).exterior.intersection(STRIP.buffer(0.2))
    for l in lines_of(ln):
        n = int(l.length / ev)
        for i in range(n):
            q = l.interpolate((i + random.uniform(0.15, 0.85)) * ev)
            if roads.distance(q) > rr + 0.4 and all(q.distance(t) > rr + 0.6 for t in track): tree(q.x, q.y, rr * random.uniform(0.85, 1.2), RIP)
for t in track:
    for i in range(1, int(t.length / 55) + 1):
        q = t.interpolate(i * 55 - 20); ax.add_patch(Circle((q.x, q.y), 1.5, fc='#cfa783', ec='#8a6a4b', lw=0.4, zorder=5))
# ---------- stream garden (head of the Avenue)
gN = V['gardenN'].difference(STRIP)
lawnN = big(gN.buffer(-3.5, join_style=1)).buffer(1.5, join_style=1); fp(lawnN, z=2.5, fc='#c6e6ae', ec='#ffffff', lw=0.5)
deck = W.rect(GU - 5.5, GU + 5.5, -1.5, 7.0); fp(deck, z=5, fc='#c79f6a', ec='#8a6a3b', lw=0.5)
for k in range(1, 7): ax.plot(*zip(W.xy(GU - 5.5, -1.5 + k * 1.2), W.xy(GU + 5.5, -1.5 + k * 1.2)), color='#a8824f', lw=0.3, zorder=5.1)
for rr in (5.0, 7.2, 9.4):
    pts = [W.xy(GU + 27 + rr * math.cos(math.radians(a)), 5.5 + rr * math.sin(math.radians(a))) for a in range(205, 336, 6)]
    ax.plot(*zip(*pts), color='#b89a6c', lw=1.5, zorder=4.6, solid_capstyle='round')
ax.add_patch(Circle(W.xy(GU + 27, 4.2), 2.2, fc='#d9c39a', ec='#8a6a3b', lw=0.4, zorder=4.7))
for u_, v_, c_ in ((GU + 12, 2, 'pink'), (GU + 44, -1, 'gold'), (GU + 58, -3, 'pink'), (GU - 13, 4, 'gold')):
    x, y = W.xy(u_, v_)
    if gN.buffer(1).contains(Point(x, y)): tree(x, y, 2.3, flower=FL[c_])
# ---------- avenue: double row of flowering trees; streets: one tree at each plot line
for vv in np.arange(L['A1'][0] + 5.5, VS - 19, 9.5):
    if any(abs(vv - mid(k)) < 8.5 for k in ('s2', 's3')): continue
    for du in (-4.75, 4.75): tree(*W.xy(GU + du, vv), 1.9, flower=FL['flame'] if int(vv) % 2 else FL['gold'])
verge = roads.difference(carr.buffer(0.2))
for nm, (l, w) in CL.items():
    if nm == 'avenue': continue
    for side in (1, -1):
        oc = l.offset_curve(side * (w / 2 - 0.8), join_style=1)
        for seg in lines_of(oc):
            n = int(seg.length / 13.0)
            for i in range(n + 1):
                q = seg.interpolate(6 + i * 13.0)
                if not K.buffer(-2).contains(q) or any(q.distance(j) < 10.5 for j in jp): continue
                if STRIP.buffer(1.5).contains(q) or gN.buffer(2).contains(q) or ave_band.buffer(2).contains(q): continue
                tree(q.x, q.y, 1.45, ['#5f9c48', '#6aa652', '#559242'], z=6.8)
# ---------- central park
pu, pv = W.uv(park.centroid.x, park.centroid.y); PWd = park.area / (L['B2'][1] - L['B1'][0])
fp(park, z=2.6, fc='#aedb93', ec='none')
ring = W.rect(pu - PWd / 2 + 2.6, pu + PWd / 2 - 2.6, L['B1'][0] + 2.6, L['B2'][1] - 2.6).buffer(-1.5, join_style=1).buffer(1.5, join_style=1)
path(ring.exterior, w=1.6)
ax.add_patch(Ellipse(W.xy(pu, pv - 3), (PWd - 11) , 19, angle=W.th + 90, fc='#c9e9b2', ec='#ffffff', lw=0.6, zorder=3))
ax.add_patch(Circle(W.xy(pu, pv + 13.2), 4.6, fc='#ecdcae', ec='#b9a678', lw=0.4, zorder=4.6))
for dx, dy, c_ in ((-1.6, -0.8, '#e2574c'), (1.5, -1.0, '#3f8fc4'), (0, 1.6, '#f0b43c')): ax.add_patch(Circle(W.xy(pu + dx, pv + 13.2 + dy), 0.75, fc=c_, lw=0, zorder=4.8))
fp(W.rect(pu - 2.2, pu + 2.2, pv - 18.6, pv - 14.6), z=5, fc='#c79f6a', ec='#8a6a3b', lw=0.5)
for du in (-PWd / 2 + 1.4, PWd / 2 - 1.4):
    for k, vv in enumerate(np.arange(L['B1'][0] + 4, L['B2'][1] - 3, 7.6)): tree(*W.xy(pu + du, vv), 1.7, flower=FL['lilac'] if k % 2 else None)
# ---------- stream lawn (west): party lawn + gazebo
lw_ = V['lawnW'].difference(STRIP)
pl = big(lw_.buffer(-6, join_style=1))
if not pl.is_empty:
    pl = pl.buffer(3, join_style=1); fp(pl, z=2.5, fc='#c6e6ae', ec='#ffffff', lw=0.5)
    c_ = pl.representative_point(); ax.add_patch(RegularPolygon((c_.x, c_.y), 6, radius=3.2, fc='#c0774b', ec='#7a4326', lw=0.5, zorder=6)); ax.add_patch(Circle((c_.x, c_.y), 0.8, fc='#7a4326', lw=0, zorder=6.1))
    eb = big(big(lw_).buffer(-2.2)).exterior
    for i in range(int(eb.length / 8.5)):
        q = eb.interpolate(i * 8.5 + random.uniform(0, 3))
        if pl.distance(q) > 2.4 and all(q.distance(t) > 2.6 for t in track): tree(q.x, q.y, random.uniform(1.8, 2.4), flower=FL['pink'] if i % 4 == 0 else None)
# ---------- east grove and screen planting
grove = rest.intersection(E.rect(150, 300, L['s2'][1] - 2, L['s3'][0] + 2)).buffer(-2.2)
for uu in np.arange(150, 215, 6.4):
    for vv in np.arange(L['s2'][1], L['s3'][0], 6.4):
        q = Point(E.xy(uu, vv))
        if grove.contains(q): tree(q.x, q.y, 2.2, ['#4a8a3c', '#57963f'])
for zone, ev in ((V['southE'], 5.2), (rest.intersection(E.rect(100, 300, -40, L['s2'][0])), 6.5)):
    for q_ in parts(zone.buffer(-1.9)):
        for i in range(int(q_.exterior.length / ev)):
            pt = q_.exterior.interpolate(i * ev); tree(pt.x, pt.y, random.uniform(1.5, 2.0), RIP)
for q_ in parts(rest.intersection(W.rect(-40, 12, 16, 70)).buffer(-2.5)):
    if q_.area > 25:
        c_ = q_.representative_point(); tree(c_.x, c_.y, 2.6, flower=FL['gold']); 
# ---------- clubhouse
cu0 = GU + 6 + 3.5
bld = W.rect(cu0, cu0 + 13, L['C1'][0] + 5.5, L['C1'][0] + 18).intersection(club.buffer(-2)); fp(bld.buffer(0.6).difference(bld).union(bld), z=5, fc='#b98d55', ec='#7a5a2e', lw=0.5)
ax.plot(*zip(W.xy(cu0, L['C1'][0] + 11.75), W.xy(cu0 + 13, L['C1'][0] + 11.75)), color='#8f6a3c', lw=0.6, zorder=5.2)
dk = W.rect(cu0 + 14.5, cu0 + 27, L['C1'][0] + 3.8, L['C1'][0] + 12.2).intersection(club.buffer(-1.2)); fp(dk, z=4.9, fc='#e3cfa4', ec='#b9a678', lw=0.3)
pool = W.rect(cu0 + 16.5, cu0 + 25, L['C1'][0] + 5.5, L['C1'][0] + 10.5).intersection(club.buffer(-1.5)).buffer(-0.6, join_style=1).buffer(0.6, join_style=1); fp(pool, z=5, fc='#66c3e4', ec='#ffffff', lw=0.7)
for u_, v_ in ((cu0 + 30, 5), (cu0 + 34, 9), (cu0 + 15.5, 16)):
    x, y = W.xy(u_, L['C1'][0] + v_)
    if club.buffer(-1.6).contains(Point(x, y)): tree(x, y, 1.6, flower=FL['white'])
tree(*W.xy(GU, VS - 8.5), 1.5, flower=FL['flame'], z=7.5)
ax.plot(*K.exterior.xy, color='#b3261e', lw=1.7, zorder=8)
fp(W.rect(GU - 7.5, GU - 1.6, VS - 1.1, VS + 1.1).union(W.rect(GU + 1.6, GU + 7.5, VS - 1.1, VS + 1.1)), z=9, fc='#3d2f1b', ec='none')
exec(open('/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/v7/landscape_key.py').read())
fig.savefig(rv.OUT + 'Jalkoti_Colony_v8_Landscape.pdf'); fig.savefig(rv.OUT + 'Jalkoti_Colony_v8_Landscape.png', dpi=170)
print('landscape sheet saved | track length %.0f m | street+avenue trees drawn' % sum(t.length for t in track))
