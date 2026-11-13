"""Consumer master plan for the brochure: the same plan as 08_master_plan.png in the final zip (same geometry,
same colours, north up, the zip's stream), without the technical labels and with the correct plot count."""
import sys, os, math, random, pickle, numpy as np, warnings; warnings.filterwarnings('ignore')
SP = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
PLAN = SP + 'plan/'; OUT = SP + 'brochure2/'
sys.path.insert(0, PLAN); os.chdir(PLAN)
exec(open('dims.py').read().split("if __name__=='__main__':")[0])
from shapely import affinity
from shapely.geometry import Point, LineString, box
random.seed(11)
S08 = pickle.load(open(OUT + 'stream08.pkl', 'rb')); TH = S08['fit'][0]
pc = C.centroid
def G(g): return affinity.rotate(affinity.translate(g, -pc.x, -pc.y), TH, origin=(0, 0))
def GP(x, y):
    q = G(Point(x, y)); return q.x, q.y
MED = medians_info(); CORN = corners_info(); AP = approach_info(); SPLAY = entry_splay(AP)
c = G(C); bx0, by0, bx1, by1 = c.bounds
X0, X1, Y0, Y1 = bx0 - 30, bx1 + 22, by0 - 62, by1 + 40      # view window, metres, north up
K = 4.0                                                     # px per metre in the viewBox
VIEW = box(X0, Y0, X1, Y1)
Wd, Ht = (X1 - X0) * K, (Y1 - Y0) * K
parts = []
def P(x, y): return ((x - X0) * K, (Y1 - y) * K)
def st(d): return ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in d.items())
def path(g, **s):
    d = []
    for p in getattr(g, 'geoms', [g]):
        if p.geom_type != 'Polygon' or p.is_empty: continue
        for ring in [p.exterior] + list(p.interiors):
            d.append('M' + ' L'.join('%.1f,%.1f' % P(*xy) for xy in ring.coords) + ' Z')
    if d: parts.append(f'<path d="{" ".join(d)}" fill-rule="evenodd" {st(s)}/>')
def line(g, **s):
    for l in getattr(g, 'geoms', [g]):
        if l.geom_type == 'LineString' and l.length > 0:
            parts.append(f'<polyline points="{" ".join("%.1f,%.1f" % P(*xy) for xy in l.coords)}" fill="none" {st(s)}/>')
def text(x, y, t, size, **s):
    X, Y = P(x, y); parts.append(f'<text x="{X:.1f}" y="{Y:.1f}" font-size="{size * K:.1f}" {st(s)}>{t}</text>')
def trees(poly, n_per_m2, rmin, rmax, cols):
    minx, miny, maxx, maxy = poly.bounds; n = int(poly.area * n_per_m2); pts = []; tries = 0
    while len(pts) < n and tries < n * 40:
        tries += 1; x = random.uniform(minx, maxx); y = random.uniform(miny, maxy)
        if not poly.contains(Point(x, y)): continue
        r = random.uniform(rmin, rmax)
        if any((x - a) ** 2 + (y - b) ** 2 < (0.9 * (r + q)) ** 2 for a, b, q in pts): continue
        pts.append((x, y, r))
    for x, y, r in pts:
        X, Y = P(x + r * .3, y - r * .3); parts.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r * K:.1f}" fill="#2f4f2f" fill-opacity=".16"/>')
    for x, y, r in pts:
        X, Y = P(x, y); parts.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r * K:.1f}" fill="{random.choice(cols)}"/>')
TREE = ['#4f8a3a', '#5b9744', '#467c33', '#6aa34f']
# ---------------------------------------------------------------- ground, resort, stream
parts.append(f'<rect width="{Wd:.0f}" height="{Ht:.0f}" fill="#f4f1e8"/>')
rs = G(RS).intersection(VIEW)
path(rs, fill='#e7eed8', stroke='#c3d3a8', stroke_width='2')
trees(rs.buffer(-6), 0.0016, 2.4, 3.6, ['#a9c58c', '#9dbd7f', '#b3cc97'])
ap = G(AP['poly']).intersection(VIEW); path(ap, fill='#8e8e8e')
path(G(access).intersection(VIEW), fill='#8e8e8e'); path(G(SPLAY).intersection(VIEW), fill='#8e8e8e')
sm = G(S08['stream']).intersection(VIEW)
path(sm.buffer(2.2), fill='#a9d3ea'); path(sm, fill='#58a6d3')
# ---------------------------------------------------------------- colony
path(G(C), fill='#fbf6ea')
path(G(rpark), fill='#7fb446')
trees(G(rpark).buffer(-1.6), 0.010, 1.9, 2.7, TREE)
for q in CORN: path(G(q), fill='#b3d48e')
path(G(row), fill='#a3a3a3')
path(G(gard), fill='#2f7d33')
for m_ in MED: trees(G(m_['geom']).buffer(-0.25), 0.05, 0.95, 1.2, ['#5b9744', '#6aa34f', '#77ae5b'])
path(G(walk), fill='#c9a46a')
path(G(svc), fill='#b3c0c7', stroke='#8a9aa3', stroke_width='1.5')
for t, p in PL.items():
    path(G(p), fill='#fcf1d6' if KIND[t] == 'Villa' else '#f3d8ab', stroke='#a5854f', stroke_width='1.1')
line(G(C).exterior, stroke='#1e3a2b', stroke_width='3.2', stroke_linejoin='round')
for t, p in PL.items():
    q = G(p).representative_point() if not G(p).contains(G(p).centroid) else G(p).centroid
    text(q.x, q.y - 1.2, t, 3.4, text_anchor='middle', font_family='Inter', font_weight='600', fill='#8a7046')
# ---------------------------------------------------------------- labels
def call(n, x, y):
    X, Y = P(*GP(x, y))
    parts.append(f'<g><circle cx="{X:.1f}" cy="{Y:.1f}" r="{6.2 * K:.1f}" fill="#1e3a2b" stroke="#ffffff" stroke-width="{1.1 * K:.1f}"/>'
                 f'<text x="{X:.1f}" y="{Y + 2.45 * K:.1f}" text-anchor="middle" font-family="Inter" font-weight="700" font-size="{7.0 * K:.1f}" fill="#ffffff">{n}</text></g>')
def callG(n, q):
    X, Y = P(q.x, q.y)
    parts.append(f'<g><circle cx="{X:.1f}" cy="{Y:.1f}" r="{6.2 * K:.1f}" fill="#1e3a2b" stroke="#ffffff" stroke-width="{1.1 * K:.1f}"/>'
                 f'<text x="{X:.1f}" y="{Y + 2.45 * K:.1f}" text-anchor="middle" font-family="Inter" font-weight="700" font-size="{7.0 * K:.1f}" fill="#ffffff">{n}</text></g>')
from shapely.ops import nearest_points
wk = G(walk); rr = G(row)
mrr = wk.minimum_rotated_rectangle; cs_ = list(mrr.exterior.coords)[:4]
sides = sorted([LineString([cs_[i], cs_[(i + 1) % 4]]) for i in range(4)], key=lambda l: l.length)[:2]
ends = sorted([sd.centroid for sd in sides], key=lambda q: q.distance(rr))
road_end, garden_end = ends[0], ends[1]
dx, dy = road_end.x - garden_end.x, road_end.y - garden_end.y; L = math.hypot(dx, dy)
callG(2, Point(road_end.x + dx / L * 8.5, road_end.y + dy / L * 8.5))
callG(1, Point(*GP(336, -272)))
callG(3, G(svc).centroid)
rc = rs.representative_point()
text(rc.x + 5, rc.y - 6, 'RESORT', 5.2, text_anchor='middle', font_family='Inter', font_weight='600', letter_spacing='6', fill='#7d8f63')
text(rc.x + 5, rc.y - 13.5, 'separate project', 4.4, text_anchor='middle', font_family='Cormorant Garamond', font_style='italic', fill='#7d8f63')
# stream label above the north reach, following its direction
xm = (bx0 + bx1) / 2 + 30
cut = sm.intersection(LineString([(xm, Y0), (xm, Y1)]))
ytop = max(c_[1] for g_ in getattr(cut, 'geoms', [cut]) for c_ in g_.coords)
xa, xb = xm - 25, xm + 25
def ytop_at(x):
    cc = sm.intersection(LineString([(x, Y0), (x, Y1)])); return max(c_[1] for g_ in getattr(cc, 'geoms', [cc]) for c_ in g_.coords)
ang = -math.degrees(math.atan2(ytop_at(xb) - ytop_at(xa), xb - xa))
def ybot_at(x):
    cc = sm.intersection(LineString([(x, Y0), (x, Y1)])); return min(c_[1] for g_ in getattr(cc, 'geoms', [cc]) for c_ in g_.coords)
xm = bx0 + 62; xa, xb = xm - 22, xm + 22
ang = -math.degrees(math.atan2(ytop_at(xb) - ytop_at(xa), xb - xa))
X, Y = P(xm, ytop_at(xm) + 3.5)
parts.append(f'<text x="{X:.1f}" y="{Y:.1f}" transform="rotate({ang:.1f} {X:.1f} {Y:.1f})" text-anchor="middle" font-family="Cormorant Garamond" font-style="italic" font-weight="600" font-size="{7.5 * K:.1f}" fill="#2f78a6">seasonal stream</text>')
# approach road: arrow towards the main road at the bottom edge
apv = unary_union([G(AP['poly']), G(access)]).intersection(VIEW)
lowx = apv.intersection(box(X0, Y0, X1, Y0 + 14)).centroid.x if not apv.intersection(box(X0, Y0, X1, Y0 + 14)).is_empty else apv.centroid.x
X, Y = P(lowx + 9, Y0 + 13)
parts.append(f'<text x="{X:.1f}" y="{Y:.1f}" font-family="Inter" font-weight="500" font-size="{4.6 * K:.1f}" fill="#5f6d66">entrance road · about 800 m to the main road</text>')
parts.append(f'<path d="M{X - 5 * K:.1f},{Y - 9 * K:.1f} v{12 * K:.1f} m-{2.6 * K:.1f},-{3.4 * K:.1f} l{2.6 * K:.1f},{3.4 * K:.1f} l{2.6 * K:.1f},-{3.4 * K:.1f}" fill="none" stroke="#5f6d66" stroke-width="{0.8 * K:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
# north arrow, top right
nx, ny = Wd - 16 * K, 20 * K
parts.append(f'<g transform="translate({nx:.0f},{ny:.0f})"><path d="M0,{-9 * K:.0f} L{4 * K:.0f},{5 * K:.0f} L0,{2.5 * K:.0f} L{-4 * K:.0f},{5 * K:.0f} Z" fill="#1e3a2b"/>'
             f'<text x="0" y="{13 * K:.0f}" text-anchor="middle" font-family="Inter" font-weight="700" font-size="{5 * K:.0f}" fill="#1e3a2b">N</text></g>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wd:.0f} {Ht:.0f}" width="{Wd:.0f}" height="{Ht:.0f}">' + ''.join(parts) + '</svg>')
open(OUT + 'plan_consumer.svg', 'w').write(svg)
print('plan svg', round(Wd), 'x', round(Ht), 'aspect %.3f' % (Wd / Ht), 'window m', round(X1 - X0), round(Y1 - Y0), 'rot', TH)
