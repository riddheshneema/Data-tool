"""Final sheet v6: engineer's Option 6 road pattern on our colony land, plots re-laid for sale."""
import sys, os, csv, math, pickle, random, warnings; warnings.filterwarnings('ignore')
import networkx as nx
SP = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
OUT = '/home/user/Data-tool/site_plans/v6_engineer/'
os.makedirs(OUT, exist_ok=True)
os.chdir(SP + 'plan'); sys.path.insert(0, SP + 'plan')
exec(open('dims.py').read().split("if __name__=='__main__':")[0])
from shapely.geometry import Point, box, Polygon, LineString
from shapely.ops import unary_union, nearest_points
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
SQFT = 10.7639; FT = 3.28084
V = pickle.load(open(SP + 'eng2/' + (sys.argv[1] if len(sys.argv) > 1 else 'pol') + '.pkl', 'rb'))
K = V['K']; roads = V['roads']; lines = V['lines']
plots = [p['poly'] for p in V['plots']]
st = pickle.load(open(SP + 'brochure2/stream08.pkl', 'rb'))['stream']
GATE = Point(331, -262)
# ---------- measure plots
def measure(q):
    bd = q.boundary
    fg = bd.intersection(roads.buffer(0.4))
    parts = sorted([g for g in getattr(fg, 'geoms', [fg]) if g.length > 0.5], key=lambda g: -g.length)
    F = parts[0]; total = sum(g.length for g in parts)
    vs = list(q.exterior.coords)[:-1]
    depth = max(Point(v).distance(F) for v in vs)
    cs = vs + [vs[0]]; E = [(cs[k], cs[k + 1]) for k in range(len(vs))]
    isf = [LineString(e).centroid.distance(F) < 0.5 for e in E]
    nE = len(E); fidx = [k for k in range(nE) if isf[k]]
    # sides = the first non-front edge on each end of the front chain; back = everything else
    side = set()
    for k in fidx:
        for d_ in (1, -1):
            j = (k + d_) % nE
            if not isf[j]: side.add(j)
    back = sum(math.dist(*E[k]) for k in range(nE) if not isf[k] and k not in side)
    sides = [math.dist(*E[k]) for k in side]
    corner = len([g for g in parts if g.length > 3]) > 1
    return dict(front=F.length, back=back, depth=(sum(sides) / len(sides)) if len(sides) == 2 and not corner else q.area / F.length, frontage=total, n=len(vs), corner=corner)
# ---------- numbering: walk round the colony clockwise starting at the gate
cx, cy = K.centroid.x, K.centroid.y
def ang(p):
    a = math.atan2(p.y - cy, p.x - cx); a0 = math.atan2(GATE.y - cy, GATE.x - cx)
    return (a0 - a) % (2 * math.pi)
ring = K.exterior
def key(q):
    c = q.centroid
    outer = c.distance(ring) < 40
    return (0 if outer else 1, ang(c))
plots.sort(key=key)
info = []
for i, q in enumerate(plots):
    m = measure(q); m.update(no=i + 1, poly=q, area=q.area * SQFT, rect=q.area / q.minimum_rotated_rectangle.area)
    info.append(m)
# ---------- greens
green = K.difference(unary_union(plots + [roads]))
pieces = [g for g in getattr(green, 'geoms', [green]) if g.area > 2]
def pick(x, y): return min(pieces, key=lambda g: g.distance(Point(x, y)))
club_piece = pick(183, -178); kids = pick(314, -137); cop_c = pick(322, -165); cop_e = pick(448, -140); cop_s = pick(300, -245)
cz = club_piece.intersection(Point(192, -176).buffer(19)); club = max(getattr(cz, 'geoms', [cz]), key=lambda g: g.area)
club_rest = club_piece.difference(club)
stream_park = unary_union([g for g in pieces if g.intersects(R.buffer(9.5))])
named = [club_piece, kids, cop_c, cop_e, cop_s]
others = unary_union([g for g in pieces if all(not g.equals(n) for n in named) and not g.intersects(R.buffer(9.5))] + [club_rest])
parks = dict(COP1=cop_c, COP2=cop_e, COP3=cop_s)
# ---------- road distances measured on the road surface itself (1 m grid)
import numpy as np
from skimage.graph import MCP_Geometric
from shapely import contains_xy
x0, y0, x1, y1 = K.bounds; RES = 1.0
xs = np.arange(x0 - 5, x1 + 5, RES); ys = np.arange(y0 - 5, y1 + 5, RES)
XX, YY = np.meshgrid(xs, ys)
rmask = contains_xy(roads.buffer(0.6), XX, YY)
cost = np.where(rmask, 1.0, np.inf)
def cell(x, y): return (int(round((y - ys[0]) / RES)), int(round((x - xs[0]) / RES)))
g0 = min(zip(*np.nonzero(rmask)), key=lambda rc: (xs[rc[1]] - GATE.x) ** 2 + (ys[rc[0]] - GATE.y) ** 2)
m = MCP_Geometric(cost); dgate, _ = m.find_costs([g0])
r12 = unary_union([l.buffer(w / 2) for l, w in lines if w >= 12]).intersection(roads)
src12 = list(zip(*np.nonzero(rmask & contains_xy(r12.buffer(0.5), XX, YY))))
m2 = MCP_Geometric(cost); d12g, _ = m2.find_costs(src12)
far = far9 = 0
for p in info:
    zone = contains_xy(p['poly'].buffer(1.5).difference(p['poly']), XX, YY) & rmask
    if zone.any():
        p['gate_m'] = float(dgate[zone].min()); p['d12'] = float(d12g[zone].min())
    else:
        p['gate_m'] = p['d12'] = float('nan')
    far = max(far, p['gate_m']); far9 = max(far9, p['d12'])
# ---------- figure
random.seed(7)
fig = plt.figure(figsize=(16.54, 11.69)); ax = fig.add_axes([0.01, 0.05, 0.71, 0.88])
def fp(g, z=1, **k):
    for q in getattr(g, 'geoms', [g]):
        if q.geom_type == 'Polygon' and not q.is_empty:
            ax.fill(*q.exterior.xy, zorder=z, **k)
            for h in q.interiors: ax.fill(*h.xy, zorder=z, color='#fbf6ea')
def trees(g, every, r):
    e = g.buffer(-r - 0.8)
    for q in getattr(e, 'geoms', [e]):
        if q.geom_type != 'Polygon': continue
        for i in range(int(q.exterior.length / every)):
            pt = q.exterior.interpolate(i * every)
            ax.add_patch(plt.Circle((pt.x, pt.y), r * random.uniform(0.85, 1.15), color=random.choice(['#4f8a3a', '#5b9744', '#6aa34f']), zorder=5, lw=0))
ax.set_facecolor('#f4f1e8')
fp(R, color='#d6ebf5'); fp(st, color='#58a6d3'); fp(unary_union([RS, C.difference(K)]), color='#ece4cf')
fp(access, color='#9a9a9a')
fp(K, color='#fbf6ea')
fp(roads, z=2, color='#a9a9a9')
for g in [stream_park, cop_c, cop_e, cop_s, kids, others]: fp(g, z=3, color='#a7d17c')
trees(stream_park, 9, 1.9); trees(cop_e, 8, 2.0); trees(cop_c, 8, 1.8); trees(cop_s, 8, 1.8)
fp(club, z=3, color='#e6cfa6')
cb = club.buffer(-3)
if not cb.is_empty:
    x0, y0, x1, y1 = cb.bounds
    fp(box(x0, y0 + (y1 - y0) * 0.5, x0 + (x1 - x0) * 0.6, y1).intersection(cb), z=4, color='#b98d55')
    fp(box(x0 + (x1 - x0) * 0.45, y0, x1, y0 + (y1 - y0) * 0.45).intersection(cb).buffer(-1), z=4, color='#7ec8e3')
# kids play: a few play dots
kc = kids.representative_point()
for dx in (-8, 0, 8): ax.add_patch(plt.Circle((kc.x + dx, kc.y), 1.6, color='#e8a33d', zorder=5))
# water body in the east garden (as in the engineer's COP-4)
wc = cop_e.buffer(-10)
if not wc.is_empty:
    w0 = max(getattr(wc, 'geoms', [wc]), key=lambda g: g.area).representative_point()
    ax.add_patch(matplotlib.patches.Ellipse((w0.x, w0.y), 16, 9, angle=25, color='#7ec8e3', zorder=5))
for p in info:
    q = p['poly']; ax.fill(*q.exterior.xy, color='#fdf1d6', ec='#8a6d3b', lw=0.7, zorder=6)
    c = q.representative_point()
    if p['corner'] or not (0.6 < p['back'] / p['front'] < 1.6):
        dim = f"{round(p['area']):,} sf"
    elif abs(p['front'] - p['back']) < 0.9:
        dim = f"{round(p['front'] * FT)}×{round(p['depth'] * FT)}"
    else:
        dim = f"{round(p['front'] * FT)}/{round(p['back'] * FT)}×{round(p['depth'] * FT)}"
    ax.text(c.x, c.y + 1.8, str(p['no']), fontsize=6.3, ha='center', va='center', zorder=7, weight='bold', color='#4a3a22')
    ax.text(c.x, c.y - 2.3, dim, fontsize=4.1, ha='center', va='center', zorder=7, color='#7a6a52')
ax.plot(*K.exterior.xy, color='#1e3a2b', lw=2.2, zorder=8)
def lab(g, t, dx=0, dy=0, **k):
    c = g.representative_point(); ax.text(c.x + dx, c.y + dy, t, ha='center', va='center', zorder=9, weight='bold', color=k.pop('color', '#1e3a2b'), **k)
ax.text(188, -177, f'CLUBHOUSE\n+ POOL\n{club.area:,.0f} m²', ha='center', va='center', zorder=9, weight='bold', color='#6a4a20', fontsize=5.2)
lab(kids, 'KIDS PLAY', fontsize=5.5, dy=4)
lab(cop_c, f'COP-1\n{cop_c.area:,.0f} m²', fontsize=6)
lab(cop_e, f'COP-2  EAST GARDEN\n{cop_e.area:,.0f} m²', fontsize=6, dy=-10)
ax.text(306, -241, f'COP-3  {cop_s.area:,.0f} m²', ha='center', va='center', zorder=9, weight='bold', color='#1e3a2b', fontsize=6)
ax.text(205, -97, 'STREAM PARK', fontsize=8, rotation=22, weight='bold', color='#1e3a2b', zorder=9)
ax.text(GATE.x + 12, GATE.y - 4, 'GATE ▲', fontsize=8, weight='bold', zorder=9)
ax.annotate('', xy=(455, -48), xytext=(455, -63), arrowprops=dict(arrowstyle='-|>', color='k', lw=1.5)); ax.text(455, -44, 'N', ha='center', fontsize=10, weight='bold')
ax.plot([380, 430], [-252, -252], color='k', lw=2); ax.text(405, -258, '50 m', ha='center', fontsize=7)
ax.text(165, -262, 'RESORT LAND (separate project)', fontsize=8, color='#7a6a42')
ax.set_xlim(108, 472); ax.set_ylim(-272, -38); ax.set_aspect('equal'); ax.axis('off')
NA = K.area; tot = sum(p['area'] for p in info)
op = sum(g.area for g in parks.values()) + kids.area + stream_park.area
rows = [(f'Plots ({len(info)})', tot / SQFT), ('Roads (12 m spine, 9 m loops)', roads.area), ('Stream park (incl. 9 m no-build strip)', stream_park.area),
        ('Gardens COP-1, 2, 3', sum(g.area for g in parks.values())), ('Kids play', kids.area), ('Clubhouse + pool plot', club.area), ('Other green verges', others.area)]
pn = fig.add_axes([0.73, 0.05, 0.26, 0.88]); pn.axis('off'); pn.set_xlim(0, 1); pn.set_ylim(0, 1)
pn.text(0, 1.0, 'JALKOTI COLONY — v6', fontsize=13, weight='bold', va='top', color='#1e3a2b')
pn.text(0, 0.968, "Engineer's Option 6 pattern on our colony land", fontsize=9, va='top', color='#555')
y = 0.925; pn.text(0, y, 'AREA STATEMENT', fontsize=9, weight='bold'); y -= 0.024
for nm, a in rows:
    pn.text(0, y, nm, fontsize=7.3); pn.text(0.74, y, f'{a:,.0f} m²', fontsize=7.3, ha='right'); pn.text(0.92, y, f'{a / NA * 100:.1f}%', fontsize=7.3, ha='right'); y -= 0.0195
pn.plot([0, 0.92], [y + 0.011, y + 0.011], color='#999', lw=0.6)
pn.text(0, y - 0.004, 'Colony total', fontsize=7.5, weight='bold'); pn.text(0.74, y - 0.004, f'{NA:,.0f} m²', fontsize=7.5, ha='right', weight='bold'); pn.text(0.92, y - 0.004, f'{NA / 4046.86:.2f} ac', fontsize=7.5, ha='right', weight='bold')
rectn = sum(1 for p in info if abs(p['front'] - p['back']) < 0.9); taper = sum(1 for p in info if abs(p['front'] - p['back']) >= 0.9 and not p['corner'])
rectn = sum(1 for p in info if abs(p['front'] - p['back']) < 0.9 and not p['corner']); cornern = sum(1 for p in info if p['corner'])
y -= 0.045; pn.text(0, y, 'PLOTS', fontsize=9, weight='bold'); y -= 0.023
fr = [p['frontage'] * FT for p in info]
for t in [f'{len(info)} plots · {tot:,.0f} sq ft sellable ({tot / SQFT / NA * 100:.1f}%)',
          f'Smallest {min(p["area"] for p in info):,.0f} · largest {max(p["area"] for p in info):,.0f} sq ft · avg {tot / len(info):,.0f}',
          f'{rectn} rectangular, {taper} tapered on bends, {cornern} corner',
          f'Road fronts {min(fr):.0f}–{max(fr):.0f} ft; plots on bends taper',
          'Every plot measured in the schedule (CSV)']:
    pn.text(0, y, t, fontsize=7.3); y -= 0.0195
y -= 0.02; pn.text(0, y, 'WHAT WE KEPT FROM OPTION 6', fontsize=9, weight='bold'); y -= 0.023
for t in ['His road pattern: curved 9 m loops, the', '  diagonal to the west court, the 12 m spine', 'Plots back-to-back between the loops',
          'Distributed gardens: east garden with water', '  body, central lawn, kids strip, clubhouse west']:
    pn.text(0, y, t, fontsize=7.3); y -= 0.0195
y -= 0.02; pn.text(0, y, 'WHAT WE CHANGED', fontsize=9, weight='bold'); y -= 0.023
for t in ['Resort part removed (hotel, shops, parking)', 'Stream road moved out to the 9 m green line,', '  turning his wide stream lawn into a plot row',
          'Two duplicate road links removed', 'Plots ≥ 3,000 sq ft (his were 2,000–2,520)']:
    pn.text(0, y, t, fontsize=7.3); y -= 0.0195
y -= 0.02; pn.text(0, y, 'BVN CHECKS', fontsize=9, weight='bold'); y -= 0.023
for t in [f'Open space {op / NA * 100:.0f}% incl. stream park; gardens alone {(op - stream_park.area) / NA * 100:.0f}% (Rule 47: 10%)',
          f'Farthest plot {far9:.0f} m along 9 m roads from a 12 m road (limit 250)', f'Farthest plot {far:.0f} m from the gate (12 m limit 400)',
          'All plots > 225 m² with frontage > 12 m (Rule 53)', 'Stream setback 9 m (Rule 50(b)); HWL survey needed']:
    pn.text(0, y, t, fontsize=7.0); y -= 0.0195
fig.savefig(OUT + 'Jalkoti_Colony_v6_Engineer_Pattern.pdf'); fig.savefig(OUT + 'Jalkoti_Colony_v6_Engineer_Pattern.png', dpi=150)
with open(OUT + 'Jalkoti_Colony_v6_Plot_Schedule.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['Plot', 'Front (ft)', 'Back (ft)', 'Avg depth (ft)', 'Front (m)', 'Back (m)', 'Avg depth (m)', 'Area (sq ft)', 'Area (m2)', 'Shape', 'Corner plot', 'Total road frontage (ft)', 'Drive from gate (m)'])
    for p in info:
        shape = 'corner' if p['corner'] else ('irregular (bend)' if not (0.6 < p['back'] / p['front'] < 1.6) else ('rectangle' if abs(p['front'] - p['back']) < 0.9 else 'tapered (on a bend)'))
        bk = round(p['back'] * FT) if shape in ('rectangle', 'tapered (on a bend)') else ''
        w.writerow([p['no'], round(p['front'] * FT), bk, round(p['depth'] * FT), round(p['front'], 2), round(p['back'], 2) if bk != '' else '', round(p['depth'], 2), round(p['area']), round(p['area'] / SQFT, 1), shape, 'yes' if p['corner'] else '', round(p['frontage'] * FT), round(p['gate_m'])])
print('plots', len(info), round(tot), 'sqft', round(tot / SQFT / NA * 100, 1), '% | rect', rectn, 'taper', taper, 'corner', cornern, '| far9', round(far9), 'far', round(far), '| open', round(op / NA * 100, 1), 'gardens', round((op - stream_park.area) / NA * 100, 1))
print('min front %.1f ft' % min(fr), 'min area', round(min(p['area'] for p in info)))
