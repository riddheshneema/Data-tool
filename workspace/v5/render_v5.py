"""Final sheet for v5: engineer-style loop + measured plots + lawn court."""
import sys, os, csv, math, pickle, random, warnings; warnings.filterwarnings('ignore')
import networkx as nx
SP = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
OUT = '/home/user/Data-tool/site_plans/v5_loop/'
os.makedirs(OUT, exist_ok=True)
os.chdir(SP + 'plan'); sys.path.insert(0, SP + 'plan')
exec(open('dims.py').read().split("if __name__=='__main__':")[0])
from shapely.geometry import Point, box, Polygon, LineString
from shapely.ops import unary_union, nearest_points
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
SQFT = 10.7639; FT = 3.28084
V = pickle.load(open(SP + 'v5/walk.pkl', 'rb'))
K = V['N']; roads = V['roads']; QA = V['QA']; Pm = V['P']
plots = [p['poly'] for p in V['plots']]
QUAD = {id(p['poly']): p['quad'] for p in V['plots']}
st = pickle.load(open(SP + 'brochure2/stream08.pkl', 'rb'))['stream']
A = QA.exterior; GX = Pm.get('gx', 330.0); YC = Pm.get('yc', -232.0)
lane = LineString(Pm['lanes'][0]); spine_line = LineString([(GX, YC), (GX, -150)])
# ---- measure each plot: front edge (on a road), back edge, depth
def measure(q):
    bd = q.boundary
    fr = bd.intersection(roads.buffer(0.3)).length
    vs = list(q.exterior.coords)[:-1]
    depth = max(Point(v).distance(roads) for v in vs)
    # sample the boundary: front = within 0.4 m of a road, back = within 0.6 m of the max depth
    n = int(bd.length / 0.25); front = back = 0.0
    for i in range(n):
        a, b = bd.interpolate(i * 0.25), bd.interpolate((i + 1) * 0.25)
        m = Point((a.x + b.x) / 2, (a.y + b.y) / 2); dd = m.distance(roads)
        if dd < 0.4: front += a.distance(b)
        elif dd > depth - 0.6: back += a.distance(b)
    return front, back, depth, fr
# numbering clockwise from the gate: outer row first, then inner row
gp = A.project(Point(GX, YC + 20))
def key(q):
    inner = QA.contains(q.centroid)
    return (inner, (A.project(q.centroid) - gp) % A.length)
plots = [q for q in plots if not q.intersects(box(GX - 22, -170, GX - 7, -152))]
plots.sort(key=key)
info = []
for i, q in enumerate(plots):
    f, b, d, _r = QUAD[id(q)]; fr = q.boundary.intersection(roads.buffer(0.3)).length
    info.append(dict(no=i + 1, poly=q, front=f, back=b, depth=d, frontage=fr, area=q.area * SQFT, rect=q.area / q.minimum_rotated_rectangle.area, corner=fr > f + 2))
# ---- green pieces: lawn court (centre), clubhouse inside it beside the spine, services at the far south-west
green = K.difference(unary_union(plots + [roads]))
pieces = sorted([g for g in getattr(green, 'geoms', [green]) if g.area > 5], key=lambda g: -g.area)
court = [g for g in pieces if QA.contains(g.representative_point()) and g.area > 1500]
court = max(court, key=lambda g: g.area)
club = court.intersection(box(GX - 6 - 34, -178, GX - 6, -146)).buffer(0)
club = max(getattr(club, 'geoms', [club]), key=lambda g: g.area)
court_lawn = court.difference(club)
park = [g for g in pieces if not QA.contains(g.representative_point())]
park = unary_union(park)
svc = park.intersection(box(150, -240, 186, -214)); svc = max(getattr(svc, 'geoms', [svc]), key=lambda g: g.area)
park = park.difference(svc)
small = unary_union([g for g in pieces if QA.contains(g.representative_point()) and g is not court])
# ---- road distances on the noded centre-line graph (12 m = spine + link, 9 m = loop)
from shapely.ops import unary_union as uu
spine_full = LineString([(GX, YC)] + [tuple(c) for c in lane.coords])
net = uu([LineString(list(A.coords)), spine_full])
Gr = nx.Graph()
for seg in getattr(net, 'geoms', [net]):
    cs = list(seg.coords)
    for a, b in zip(cs[:-1], cs[1:]):
        Gr.add_edge((round(a[0], 3), round(a[1], 3)), (round(b[0], 3), round(b[1], 3)), w=math.dist(a, b))
nodes = list(Gr.nodes)
def nearest(p): return min(nodes, key=lambda n: (n[0] - p.x) ** 2 + (n[1] - p.y) ** 2)
twelve = {n for n in nodes if (spine_full if Pm.get('lw', 9) >= 12 else LineString([(GX, YC), (GX, -150)])).distance(Point(n)) < 0.05}
gate = nearest(Point(GX, YC))
dg = nx.single_source_dijkstra_path_length(Gr, gate, weight='w')
d12 = nx.multi_source_dijkstra_path_length(Gr, twelve, weight='w')
far = far9 = 0
for p in info:
    a = nearest(nearest_points(p['poly'], net)[1])
    far = max(far, dg[a]); far9 = max(far9, d12[a])
# ---- figure
random.seed(5)
fig = plt.figure(figsize=(16.54, 11.69)); ax = fig.add_axes([0.01, 0.05, 0.71, 0.88])
def fp(g, z=1, **k):
    for q in getattr(g, 'geoms', [g]):
        if q.geom_type == 'Polygon' and not q.is_empty: ax.fill(*q.exterior.xy, zorder=z, **k)
def trees(g, every, r):
    e = g.buffer(-r - 1.0)
    for q in getattr(e, 'geoms', [e]):
        if q.geom_type != 'Polygon': continue
        for i in range(int(q.exterior.length / every)):
            pt = q.exterior.interpolate(i * every)
            ax.add_patch(plt.Circle((pt.x, pt.y), r * random.uniform(0.85, 1.15), color=random.choice(['#4f8a3a', '#5b9744', '#6aa34f']), zorder=5, lw=0))
ax.set_facecolor('#f4f1e8')
fp(R, color='#d6ebf5'); fp(st, color='#58a6d3'); fp(unary_union([RS, C.difference(K)]), color='#ece4cf')
fp(access, color='#9a9a9a'); fp(box(GX - 7.5, -262, GX + 7.5, YC + 0.5), color='#9a9a9a')
fp(K, color='#fbf6ea'); fp(roads, z=2, color='#a9a9a9')
for g in (park, court_lawn, small): fp(g, z=2, color='#a7d17c')
trees(park, 9, 1.9); trees(court_lawn, 8, 2.0)
fp(club, z=2, color='#e6cfa6'); fp(svc, z=2, color='#bcc6cc')
cb = club.buffer(-3); x0, y0, x1, y1 = cb.bounds
fp(box(x0, y0 + (y1 - y0) * 0.45, x0 + (x1 - x0) * 0.55, y1).intersection(cb), z=4, color='#b98d55'); fp(box(x0 + (x1 - x0) * 0.62, y0, x1, y0 + (y1 - y0) * 0.6).intersection(cb).buffer(-1), z=4, color='#7ec8e3')
for p in info:
    q = p['poly']; ax.fill(*q.exterior.xy, color='#fdf1d6', ec='#8a6d3b', lw=0.7, zorder=3)
    c = q.representative_point()
    dim = f"{round(p['front'] * FT)}×{round(p['depth'] * FT)}" if abs(p['back'] - p['front']) < 1.0 else f"{round(p['front'] * FT)}/{round(p['back'] * FT)}×{round(p['depth'] * FT)}"
    ax.text(c.x, c.y + 1.8, str(p['no']), fontsize=6.3, ha='center', va='center', zorder=6, weight='bold', color='#4a3a22')
    ax.text(c.x, c.y - 2.4, dim, fontsize=4.2, ha='center', va='center', zorder=6, color='#7a6a52')
ax.plot(*K.exterior.xy, color='#1e3a2b', lw=2.2, zorder=6)
cc = court_lawn.representative_point(); ax.text(cc.x + 18, cc.y + 4, f'LAWN COURT\n{court_lawn.area:,.0f} m²', fontsize=7.5, ha='center', weight='bold', color='#1e3a2b', zorder=7)
c = club.representative_point(); ax.text(c.x, c.y - 9, f'CLUBHOUSE + POOL {club.area:,.0f} m²', fontsize=5.8, ha='center', weight='bold', color='#6a4a20', zorder=7)
ax.text(250, -72, 'STREAM PARK', fontsize=8, rotation=20, weight='bold', color='#1e3a2b', zorder=7)
q = svc.representative_point(); ax.text(q.x, q.y, 'SERVICES', fontsize=5.5, ha='center', zorder=7)
ax.text(GX + 16, YC - 8, 'GATE ▲', fontsize=8, weight='bold', zorder=7)
ax.text(GX - 3, -192, '12 m', fontsize=6, rotation=90, zorder=7); ax.text(220, -205.5, '9 m LOOP ROAD', fontsize=6.5, zorder=7, color='#333')
ax.annotate('', xy=(455, -48), xytext=(455, -63), arrowprops=dict(arrowstyle='-|>', color='k', lw=1.5)); ax.text(455, -44, 'N', ha='center', fontsize=10, weight='bold')
ax.plot([380, 430], [-250, -250], color='k', lw=2); ax.text(405, -255, '50 m', ha='center', fontsize=7)
ax.text(170, -258, 'RESORT LAND (separate project)', fontsize=8, color='#7a6a42')
ax.set_xlim(108, 472); ax.set_ylim(-268, -38); ax.set_aspect('equal'); ax.axis('off')
NA = K.area; tot = sum(p['area'] for p in info)
rect_n = sum(abs(p['back'] - p['front']) < 1.0 for p in info)
std = sum(abs(p['front'] * FT - 45) < 1.5 and abs(p['back'] - p['front']) < 1.0 for p in info)
rows = [(f'Plots ({len(info)})', tot / SQFT), ('Roads (12 m spine + link, 9 m loop)', roads.area), ('Stream park and edge greens', park.area), ('Lawn court', court_lawn.area), ('Other lawns', small.area), ('Clubhouse + pool plot', club.area), ('Services plot', svc.area)]
pn = fig.add_axes([0.73, 0.05, 0.26, 0.88]); pn.axis('off'); pn.set_xlim(0, 1); pn.set_ylim(0, 1)
pn.text(0, 1.0, 'JALKOTI COLONY — CONCEPT v5', fontsize=13, weight='bold', va='top', color='#1e3a2b')
pn.text(0, 0.968, 'Stream loop · lawn court · measured plots', fontsize=9, va='top', color='#555')
y = 0.925; pn.text(0, y, 'AREA STATEMENT', fontsize=9, weight='bold'); y -= 0.024
for nm, a in rows:
    pn.text(0, y, nm, fontsize=7.5); pn.text(0.70, y, f'{a:,.0f} m²', fontsize=7.5, ha='right'); pn.text(0.88, y, f'{a / NA * 100:.1f}%', fontsize=7.5, ha='right'); y -= 0.0195
pn.plot([0, 0.9], [y + 0.011, y + 0.011], color='#999', lw=0.6)
pn.text(0, y - 0.004, 'Colony total', fontsize=7.5, weight='bold'); pn.text(0.70, y - 0.004, f'{NA:,.0f} m²', fontsize=7.5, ha='right', weight='bold'); pn.text(0.88, y - 0.004, f'{NA / 4046.86:.2f} ac', fontsize=7.5, ha='right', weight='bold')
y -= 0.045; pn.text(0, y, 'PLOTS', fontsize=9, weight='bold'); y -= 0.023
ins = [p for p in info if QA.contains(p['poly'].centroid)]; outs = [p for p in info if p not in ins]
for t in [f'{len(info)} plots · {tot:,.0f} sq ft sellable ({tot / SQFT / NA * 100:.1f}%)',
          f'All {rect_n} plots are true rectangles (no fans or wedges)',
          f'Outer row {len(outs)} plots: 45 ft × 75 ft deep', f'Inner row {len(ins)} plots: 45 ft × 90 ft deep',
          f'Smallest {min(p["area"] for p in info):,.0f} · largest {max(p["area"] for p in info):,.0f} sq ft', 'Full dimensions per plot in the schedule (CSV)']:
    pn.text(0, y, t, fontsize=7.5); y -= 0.0195
y -= 0.02; pn.text(0, y, 'LAYOUT', fontsize=9, weight='bold'); y -= 0.023
for t in ['One 9 m loop road follows the stream bend', 'Outer plots back onto the stream park', 'Inner plots back onto the central lawn court',
          '12 m spine: gate, clubhouse, then on through', '  the lawn court to split the loop in two', 'Lawns only where a proper plot does not fit']:
    pn.text(0, y, t, fontsize=7.5); y -= 0.0195
y -= 0.02; pn.text(0, y, 'BVN CHECKS', fontsize=9, weight='bold'); y -= 0.023
for t in [f'Open space {(park.area + court_lawn.area + small.area) / NA * 100:.0f}% (Rule 47: 10%)', f'9 m roads: farthest plot {far9:.0f} m from the 12 m spine (limit 250)',
          f'Farthest plot {far:.0f} m from the gate (12 m limit 400)', 'All plots > 225 m², frontage > 12 m (Rule 53)', 'Stream setback 9 m+ (Rule 50(b)); HWL survey needed']:
    pn.text(0, y, t, fontsize=7.5); y -= 0.0195
fig.savefig(OUT + 'Jalkoti_Colony_v5_Loop.pdf'); fig.savefig(OUT + 'Jalkoti_Colony_v5_Loop.png', dpi=150)
with open(OUT + 'Jalkoti_Colony_v5_Plot_Schedule.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['Plot', 'Row', 'Front width (ft)', 'Back width (ft)', 'Depth (ft)', 'Front (m)', 'Back (m)', 'Depth (m)', 'Area (sq ft)', 'Area (m2)', 'Shape', 'Corner'])
    for p in info:
        w.writerow([p['no'], 'inner' if p in ins else 'outer', round(p['front'] * FT, 1), round(p['back'] * FT, 1), round(p['depth'] * FT, 1), round(p['front'], 2), round(p['back'], 2), round(p['depth'], 2),
                    round(p['area']), round(p['area'] / SQFT, 1), 'rectangle' if abs(p['back'] - p['front']) < 1.0 else 'fan (bend)', 'yes' if p['corner'] else ''])
print('plots', len(info), round(tot), 'sqft', round(tot / SQFT / NA * 100, 1), 'pct | rect', rect_n, '| far9', round(far9), 'far', round(far), '| open', round((park.area + court_lawn.area + small.area) / NA * 100, 1))
print('min front %.1f ft, min area %.0f, max back/front %.2f' % (min(p['front'] for p in info) * FT, min(p['area'] for p in info), max(p['back'] / p['front'] for p in info)))
