"""Clean concept sheet + plot schedule for the v2 (10.5 ac, distributed greens) colony."""
import sys, os, csv, math, pickle, random, warnings; warnings.filterwarnings('ignore')
SP = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
OUT = '/home/user/Data-tool/site_plans/v2_distributed_greens/'
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, SP + 'v2'); sys.path.insert(0, SP + 'plan'); os.chdir(SP + 'plan')
exec(open('dims.py').read().split("if __name__=='__main__':")[0])
from plots import frontage_len, min_width, SQFT
from shapely.geometry import Point, box, Polygon
from shapely.ops import unary_union
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
D = pickle.load(open(SP + 'v2/layout10.pkl', 'rb'))
AM = D['amenity']
st = pickle.load(open(SP + 'brochure2/stream08.pkl', 'rb'))['stream']
Nn, ring, roads, spine = D['N'], D['ringline'], D['roads'], D['spine']
pp = D['park_parts']; plots = D['plots']; svc = D['svc']; links = D['links']; walkg = D['walk_green']
YC = D['P']['yc']; GX = D['P']['gx']
resort = unary_union([RS, C.difference(Nn)]).difference(box(GX - 7.5, -270, GX + 7.5, YC))
acc = box(GX - 7.5, -262, GX + 7.5, YC).union(access)
random.seed(4)
fig = plt.figure(figsize=(16.54, 11.69))   # A3 landscape
ax = fig.add_axes([0.02, 0.06, 0.70, 0.86])
def fp(g, z=1, **k):
    for q in getattr(g, 'geoms', [g]):
        if q.geom_type == 'Polygon' and not q.is_empty:
            ax.fill(*q.exterior.xy, zorder=z, **k)
            for h in q.interiors: ax.fill(*h.xy, color='#f4f1e8', zorder=z)
def lp(g, z=3, **k):
    for q in getattr(g, 'geoms', [g]):
        if hasattr(q, 'exterior'): ax.plot(*q.exterior.xy, zorder=z, **k)
def trees(g, n_per, rmin, rmax):
    if g.is_empty: return
    x0, y0, x1, y1 = g.bounds; n = int(g.area * n_per); pts = []
    for _ in range(n * 30):
        if len(pts) >= n: break
        x, y = random.uniform(x0, x1), random.uniform(y0, y1); r = random.uniform(rmin, rmax)
        if g.buffer(-r * 0.6).contains(Point(x, y)) and all((x - a) ** 2 + (y - b) ** 2 > (r + c) ** 2 * 0.8 for a, b, c in pts): pts.append((x, y, r))
    for x, y, r in pts: ax.add_patch(plt.Circle((x, y), r, color=random.choice(['#4f8a3a', '#5b9744', '#6aa34f']), zorder=4, lw=0))
ax.set_facecolor('#f4f1e8')
fp(R, color='#d6ebf5'); fp(st, color='#58a6d3')
fp(resort, color='#ede6d2'); fp(acc, color='#9a9a9a')
fp(Nn, color='#fbf6ea')
fp(roads, z=2, color='#a7a7a7')
fp(walkg, z=2, color='#8fbf55'); trees(walkg, 0.006, 1.6, 2.4)
for k, g in pp.items():
    if g.is_empty: continue
    fp(g, z=2, color='#a9d17a' if k != 'garden_walk' else '#b9da8f'); trees(g, 0.004 if k != 'garden_walk' else 0.01, 1.5, 2.6)
fp(svc, z=2, color='#b9c4ca'); fp(AM, z=2, color='#e8d3ad')
for t, g in plots.items():
    fp(g, z=3, color='#fdf1d6'); lp(g, z=3, color='#9a7a46', lw=0.6)
    c = g.representative_point(); ax.text(c.x, c.y + 1.2, t, fontsize=6.2, ha='center', va='center', zorder=6, color='#4a3a22', weight='bold')
    ax.text(c.x, c.y - 2.4, f'{g.area * SQFT:,.0f}', fontsize=4.3, ha='center', va='center', zorder=6, color='#7a6a52')
lp(Nn, z=5, color='#1e3a2b', lw=2.2)
# club house, pool, play in the club lawn (west half)
c = AM.representative_point()
ax.add_patch(plt.Rectangle((c.x - 13, c.y + 1), 18, 10, color='#c8a77a', zorder=5)); ax.text(c.x - 4, c.y + 6, 'CLUBHOUSE', fontsize=5.5, ha='center', va='center', zorder=6)
ax.add_patch(plt.Rectangle((c.x - 12, c.y - 11), 14, 7, color='#7ec8e3', zorder=5)); ax.text(c.x - 5, c.y - 7.5, 'pool', fontsize=5, ha='center', va='center', zorder=6)
lab = {k: k.replace('pocket_', 'P') for k in pp if k.startswith('pocket_')}; lab.update({'tip_lawn': 'TIP LAWN', 'stream_green': 'STREAM\nGREEN'})
ax.text(c.x - 4, c.y - 16, 'CLUB PLOT\n' + f'{AM.area:,.0f} m²', fontsize=6.5, ha='center', va='center', zorder=6, weight='bold', color='#6a4a20')
for k, t in lab.items():
    g = pp[k]
    if g.is_empty: continue
    q = max(getattr(g, 'geoms', [g]), key=lambda x: x.area).representative_point()
    ax.text(q.x, q.y, t + f'\n{g.area:,.0f} m²', fontsize=6.5, ha='center', va='center', zorder=6, color='#1e3a2b', weight='bold')
q = svc.representative_point(); ax.text(q.x, q.y, 'SERVICES\nSTP · tank · waste', fontsize=5.5, ha='center', va='center', zorder=6)
ax.text(285, -60, 'STREAM WALK 9 m (green, from the high-water line)', fontsize=7, rotation=8, color='#2e5e1e', zorder=6)
ax.text(GX + 9, -150, '12 m SPINE', fontsize=6.5, rotation=90, ha='center', va='center', zorder=6, color='#333')
ax.text(212, -203.8, '9 m RING ROAD', fontsize=6.5, ha='center', va='center', zorder=6, color='#333')
ax.text(GX, YC - 12, 'GATE  ▲\naccess road through the resort', fontsize=7, ha='center', va='top', zorder=6, weight='bold')
ax.text(150, -262, 'RESORT LAND (separate project) — gains the 1.3 ac strip south of y=−230', fontsize=7.5, color='#7a6a42', zorder=6)
ax.annotate('', xy=(458, -48), xytext=(458, -62), arrowprops=dict(arrowstyle='-|>', color='k', lw=1.5)); ax.text(458, -44, 'N', ha='center', fontsize=10, weight='bold')
ax.plot([340, 390], [-262, -262], color='k', lw=2); ax.text(365, -266, '50 m', ha='center', fontsize=7)
ax.set_xlim(108, 472); ax.set_ylim(-272, -38); ax.set_aspect('equal'); ax.axis('off')
# ---- side panel
NA = Nn.area; A = sorted(g.area * SQFT for g in plots.values()); tot = sum(A)
pk = sum(g.area for g in pp.values() if not g.is_empty)
pkts = sum(g.area for k, g in pp.items() if k.startswith('pocket_') and k != 'pocket_greens')
rows = [('Plots (' + str(len(A)) + ')', tot / SQFT), ('Roads (9 m ring, 12 m spine)', roads.area), ('Stream walk 9 m', walkg.area), ('10 pocket lawns', pkts)] + \
       [(k.replace('_', ' ').capitalize(), g.area) for k, g in pp.items() if not g.is_empty and g.area > 1 and not k.startswith('pocket_')] + [('Club plot (clubhouse, pool)', AM.area), ('Services plot', svc.area)]
p = fig.add_axes([0.73, 0.06, 0.26, 0.86]); p.axis('off')
p.set_xlim(0, 1); p.set_ylim(0, 1)
p.text(0, 1.0, 'JALKOTI COLONY — CONCEPT v3', fontsize=13, weight='bold', va='top', color='#1e3a2b')
p.text(0, 0.968, 'Pocket lawns · 10.5 acres · plots from 3,000 sq ft', fontsize=9, va='top', color='#555')
y = 0.92; p.text(0, y, 'AREA STATEMENT', fontsize=9, weight='bold'); y -= 0.025
for nm, a in rows:
    p.text(0, y, nm, fontsize=7.5); p.text(0.66, y, f'{a:,.0f} m²', fontsize=7.5, ha='right'); p.text(0.86, y, f'{a / NA * 100:.1f}%', fontsize=7.5, ha='right'); y -= 0.0195
p.plot([0, 0.9], [y + 0.012, y + 0.012], color='#999', lw=0.6)
p.text(0, y - 0.004, 'Colony total', fontsize=7.5, weight='bold'); p.text(0.66, y - 0.004, f'{NA:,.0f} m²', fontsize=7.5, ha='right', weight='bold'); p.text(0.86, y - 0.004, f'{NA / 4046.86:.2f} ac', fontsize=7.5, ha='right', weight='bold')
y -= 0.05
p.text(0, y, 'PLOTS', fontsize=9, weight='bold'); y -= 0.024
for t in [f'{len(A)} plots, {tot:,.0f} sq ft sellable ({tot / SQFT / NA * 100:.1f}%)', f'Smallest {A[0]:,.0f} · average {tot / len(A):,.0f} · largest {A[-1]:,.0f} sq ft',
          f'3,000–4,000 sq ft: {sum(a < 4000 for a in A)} · 4,000–5,500: {sum(4000 <= a < 5500 for a in A)} · over 5,500: {sum(a >= 5500 for a in A)}',
          'All detached (BVN 53: >225 m², frontage >12 m)']:
    p.text(0, y, t, fontsize=7.5); y -= 0.0195
y -= 0.022; p.text(0, y, 'GREEN SPACE', fontsize=9, weight='bold'); y -= 0.024
comp = sum(g.area for k, g in pp.items() if k.startswith('pocket_') or k == 'tip_lawn')
for t in [f'{(pk + walkg.area) / NA * 100:.1f}% of the colony is green', f'{sum(k.startswith("pocket_") and k != "pocket_greens" for k in pp)} pocket lawns + tip lawn: {comp / NA * 100:.1f}% (BVN 47: 10%,', '  pockets allowed by Rule 47(1)(b); each fronts a road)', 'Stream-side pockets open onto the stream walk', 'Paired pockets across the ring = raised crossings', 'Garden walks run behind the inner plots', 'Clubhouse on its own plot (Rule 47(4))']:
    p.text(0, y, t, fontsize=7.5); y -= 0.0195
y -= 0.022; p.text(0, y, 'ROAD CHECKS (BVN Table 3)', fontsize=9, weight='bold'); y -= 0.024
for t in ['9 m ring road: longest run to the spine 189 m (limit 250 m)', '12 m spine: farthest plot 317 m from the gate (limit 400 m)',
          'Loop road, no dead ends; junctions at about 90°', 'Front setback 3.0 m on 9 m roads, 3.6 m on the spine']:
    p.text(0, y, t, fontsize=7.5); y -= 0.0195
y -= 0.022; p.text(0, y, 'TO CONFIRM', fontsize=9, weight='bold', color='#a33'); y -= 0.024
for t in ['Stream walk is 9 m from the site edge: needs the high-', '  water-level survey (BVN 50(b): 9 m from HWL of a stream)',
          'Access road through the resort to be a public street', 'Concept only: redraw on the CAD survey before approval']:
    p.text(0, y, t, fontsize=7.5); y -= 0.0195
p.text(0, 0.0, 'Plot numbers in bold; areas in sq ft. Scale bar 50 m.', fontsize=7, color='#777')
fig.savefig(OUT + 'Jalkoti_Colony_v3_Pockets.pdf'); fig.savefig(OUT + 'Jalkoti_Colony_v3_Pockets.png', dpi=150)
with open(OUT + 'Jalkoti_Colony_v3_Plot_Schedule.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['Plot', 'Area (sq ft)', 'Area (m2)', 'Road frontage (m)', 'Faces', 'Next to (back or side)'])
    for t, g in sorted(plots.items(), key=lambda x: int(x[0])):
        inner = D['Q'].contains(g.centroid)
        gr = unary_union([x for x in pp.values() if not x.is_empty]); back = 'stream walk' if g.distance(walkg) < 0.6 else ('garden walk / lawn' if g.distance(gr) < 0.6 else ('boundary' if not inner else 'plots'))
        w.writerow([t, round(g.area * SQFT), round(g.area, 1), round(frontage_len(g, roads), 1), '9 m ring road' + (' + 12 m spine' if g.distance(spine) < 0.6 else ''), back])
print('saved', OUT, len(plots), 'plots', round(tot), 'sq ft')
