"""Final sheet for v4: rectangular plots in bands, gardens from leftovers."""
import sys, os, csv, math, pickle, random, warnings; warnings.filterwarnings('ignore')
SP = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
OUT = '/home/user/Data-tool/site_plans/v4_rectangular/'
os.makedirs(OUT, exist_ok=True)
os.chdir(SP + 'plan'); sys.path.insert(0, SP + 'plan')
exec(open('dims.py').read().split("if __name__=='__main__':")[0])
from shapely.geometry import Point, box, Polygon, LineString
from shapely.ops import unary_union
from shapely import affinity
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
SQFT = 10.7639; FT = 3.28084
G = pickle.load(open(SP + 'v4/grid.pkl', 'rb'))
TH = G['TH']; K = G['K']; roads = G['roads']; plots = G['plots']
st = pickle.load(open(SP + 'brochure2/stream08.pkl', 'rb'))['stream']
# ---- classify leftover green
pieces = sorted([q for q in getattr(G['green'], 'geoms', [G['green']]) if q.area > 5], key=lambda q: -q.area)
def near(pt): return min(pieces, key=lambda q: q.distance(Point(*pt)))
stream_park = unary_union([q for q in pieces if q.distance(R) < 12 and q.area > 200 and q.centroid.y > -150] + [near((128, -188))])
club = near((340, -203))
westp = near((171, -224))
# services: south-west end of the west lawn (about 550 m2), squared to the band direction
rot = lambda g: affinity.rotate(g, -TH, origin=(0, 0)); unrot = lambda g: affinity.rotate(g, TH, origin=(0, 0))
wr = rot(westp); x0, y0, x1, y1 = wr.bounds
lo, hi = y0, y1
for _ in range(40):
    m = (lo + hi) / 2
    if wr.intersection(box(x0 - 1, y0 - 1, x1 + 1, m)).area < 550: lo = m
    else: hi = m
svc = unrot(wr.intersection(box(x0 - 1, y0 - 1, x1 + 1, lo)))
west_lawn = westp.difference(svc)
ne_lawn = near((443, -131)); n_lawn = near((386, -86)); sw_green = near((222, -251))
gardens = dict(stream_park=stream_park, west_lawn=west_lawn, ne_lawn=ne_lawn, north_lawn=n_lawn, corner_green=sw_green)
# ---- numbering: south to north, west to east in band order
def bandkey(p):
    c = rot(p['poly']).centroid; return (round(c.y / 10), c.x)
plots = sorted(plots, key=bandkey)
for i, p in enumerate(plots): p['no'] = i + 1
# ---- road distances (BVN Table 3) in the band frame
spine_u = rot(G['gate']).x
gate_v = rot(K).bounds[1]
far = 0; far9 = 0
for p in plots:
    c = rot(p['poly']).centroid
    du = abs(c.x - spine_u); far9 = max(far9, du); far = max(far, du + (c.y - gate_v))
# ---- figure
random.seed(3)
fig = plt.figure(figsize=(16.54, 11.69))
ax = fig.add_axes([0.01, 0.05, 0.71, 0.88])
def fp(g, z=1, **k):
    for q in getattr(g, 'geoms', [g]):
        if q.geom_type == 'Polygon' and not q.is_empty:
            ax.fill(*q.exterior.xy, zorder=z, **k)
def trees(g, every, r):
    if g.is_empty: return
    edge = g.buffer(-r - 1.0)
    for q in getattr(edge, 'geoms', [edge]):
        if q.geom_type != 'Polygon': continue
        ln = q.exterior; n = int(ln.length / every)
        for i in range(n):
            pt = ln.interpolate(i * every)
            ax.add_patch(plt.Circle((pt.x, pt.y), r * random.uniform(0.85, 1.15), color=random.choice(['#4f8a3a', '#5b9744', '#6aa34f']), zorder=5, lw=0))
ax.set_facecolor('#f4f1e8')
fp(R, color='#d6ebf5'); fp(st, color='#58a6d3')
resort = unary_union([RS, C.difference(K)])
fp(resort, color='#ece4cf')
mouth = roads.intersection(K.exterior.buffer(0.5))
mouth = min(getattr(mouth, 'geoms', [mouth]), key=lambda g: g.distance(Point(331, -262))).centroid
gx, gy = mouth.x, mouth.y
fp(access, color='#9a9a9a'); fp(LineString([(gx, gy), (330, -262), (330, -270)]).buffer(7.5, cap_style=2, join_style=2).difference(K), color='#9a9a9a')
fp(K, color='#fbf6ea')
fp(roads, z=2, color='#a9a9a9')
for k, g in gardens.items():
    fp(g, z=2, color='#a7d17c'); trees(g, 9 if k == 'stream_park' else 8, 1.9)
fp(club, z=2, color='#e6cfa6'); fp(svc, z=2, color='#bcc6cc')
c = club.representative_point()
cr = rot(club); cx0, cy0, cx1, cy1 = cr.bounds
inner = cr.buffer(-3)
bld = inner.intersection(box(cx0, cy0, cx0 + (cx1 - cx0) * 0.45, cy1)); pool = inner.intersection(box(cx0 + (cx1 - cx0) * 0.55, cy0, cx0 + (cx1 - cx0) * 0.85, cy1)).buffer(-2)
for g_, col in ((bld, '#b98d55'), (pool, '#7ec8e3')):
    for q_ in getattr(unrot(g_), 'geoms', [unrot(g_)]):
        if q_.geom_type == 'Polygon' and q_.area > 5: ax.add_patch(plt.Polygon(list(q_.exterior.coords), color=col, zorder=4))
for p in plots:
    g = p['poly']; ax.fill(*g.exterior.xy, color='#fdf1d6', ec='#8a6d3b', lw=0.7, zorder=3)
    cc = g.centroid
    ax.text(cc.x, cc.y + 2.0, str(p['no']), fontsize=6.5, ha='center', va='center', zorder=6, weight='bold', color='#4a3a22', rotation=TH)
    ax.text(cc.x, cc.y - 2.6, f"{round(p['w'] * FT)}×{round(p['d'] * FT)}", fontsize=4.6, ha='center', va='center', zorder=6, color='#7a6a52', rotation=TH)
ax.plot(*K.exterior.xy, color='#1e3a2b', lw=2.2, zorder=6)
lab = {'stream_park': 'STREAM PARK', 'west_lawn': 'WEST LAWN', 'ne_lawn': 'NE LAWN', 'north_lawn': 'NORTH\nLAWN'}
for k, t in lab.items():
    q = max(getattr(gardens[k], 'geoms', [gardens[k]]), key=lambda x: x.area).representative_point()
    ax.text(q.x, q.y, t + f'\n{gardens[k].area:,.0f} m²', fontsize=7, ha='center', va='center', zorder=7, weight='bold', color='#1e3a2b', rotation=TH if k == 'stream_park' else 0)
ax.text(c.x, c.y - 9, f'CLUBHOUSE + POOL  {club.area:,.0f} m²', fontsize=6.5, ha='center', zorder=7, weight='bold', color='#6a4a20', rotation=TH)
q = svc.representative_point(); ax.text(q.x, q.y, 'SERVICES', fontsize=5.5, ha='center', va='center', zorder=7)
ax.text(gx + 14, gy - 8, 'GATE ▲', fontsize=8, ha='center', weight='bold', zorder=7)
ax.text(200, -275, 'RESORT LAND (separate project)', fontsize=8, color='#7a6a42')
ax.annotate('', xy=(455, -48), xytext=(455, -63), arrowprops=dict(arrowstyle='-|>', color='k', lw=1.5)); ax.text(455, -44, 'N', ha='center', fontsize=10, weight='bold')
ax.plot([380, 430], [-262, -262], color='k', lw=2); ax.text(405, -267, '50 m', ha='center', fontsize=7)
ax.set_xlim(108, 472); ax.set_ylim(-282, -38); ax.set_aspect('equal'); ax.axis('off')
# ---- panel
NA = K.area; A = sorted(p['poly'].area * SQFT for p in plots); tot = sum(A)
from collections import Counter
sz = Counter(f"{round(p['w'] * FT)}×{round(p['d'] * FT)}" for p in plots)
std = sz.get('45×75', 0)
gsum = sum(g.area for g in gardens.values())
rows = [(f'Plots ({len(A)})', tot / SQFT), ('Roads (12 m spine, 9 m streets)', roads.area)] + [(k.replace('_', ' ').capitalize(), g.area) for k, g in gardens.items()] + [('Clubhouse + pool plot', club.area), ('Services plot', svc.area)]
pn = fig.add_axes([0.73, 0.05, 0.26, 0.88]); pn.axis('off'); pn.set_xlim(0, 1); pn.set_ylim(0, 1)
pn.text(0, 1.0, 'JALKOTI COLONY — CONCEPT v4', fontsize=13, weight='bold', va='top', color='#1e3a2b')
pn.text(0, 0.968, 'Rectangular plots in bands · gardens from the edges', fontsize=9, va='top', color='#555')
y = 0.925; pn.text(0, y, 'AREA STATEMENT', fontsize=9, weight='bold'); y -= 0.024
for nm, a in rows:
    pn.text(0, y, nm, fontsize=7.5); pn.text(0.66, y, f'{a:,.0f} m²', fontsize=7.5, ha='right'); pn.text(0.86, y, f'{a / NA * 100:.1f}%', fontsize=7.5, ha='right'); y -= 0.0195
pn.plot([0, 0.9], [y + 0.011, y + 0.011], color='#999', lw=0.6)
pn.text(0, y - 0.004, 'Colony total', fontsize=7.5, weight='bold'); pn.text(0.66, y - 0.004, f'{NA:,.0f} m²', fontsize=7.5, ha='right', weight='bold'); pn.text(0.86, y - 0.004, f'{NA / 4046.86:.2f} ac', fontsize=7.5, ha='right', weight='bold')
y -= 0.045; pn.text(0, y, 'PLOTS', fontsize=9, weight='bold'); y -= 0.023
lines = [f'{len(A)} plots · {tot:,.0f} sq ft sellable ({tot / SQFT / NA * 100:.1f}%)', 'Every plot a true rectangle, all 75 ft deep',
         f'{std} standard 45×75 ft (3,375 sq ft)', f'{len(A) - std} corner plots 48–65 ft wide (3,600–4,900 sq ft)']
for t in lines: pn.text(0, y, t, fontsize=7.5); y -= 0.0195
y -= 0.005
for k_, v_ in sorted(sz.items(), key=lambda x: -x[1]):
    pn.text(0.04, y, f'{k_} ft', fontsize=7); pn.text(0.40, y, f'{v_} plots', fontsize=7); y -= 0.0165
y -= 0.02; pn.text(0, y, 'GREEN AND AMENITY', fontsize=9, weight='bold'); y -= 0.023
for t in [f'Gardens {gsum / NA * 100:.1f}% (BVN Rule 47: 10%), none taken from plots', 'Stream park: 9 m+ from the stream, walking track', 'Stream road: plots face the park and the water',
          'Clubhouse + pool on its own plot at the arrival']:
    pn.text(0, y, t, fontsize=7.5); y -= 0.0195
y -= 0.02; pn.text(0, y, 'ROAD CHECKS (BVN Table 3)', fontsize=9, weight='bold'); y -= 0.023
for t in [f'9 m streets: farthest plot {far9:.0f} m from the spine (limit 250 m)', f'12 m spine: farthest plot about {far:.0f} m from the gate (limit 400 m)',
          'Every street loops back; T-junctions at 90°', 'Front setback 3.0 m (9 m roads), 3.6 m (spine)']:
    pn.text(0, y, t, fontsize=7.5); y -= 0.0195
y -= 0.02; pn.text(0, y, 'TO CONFIRM', fontsize=9, weight='bold', color='#a33'); y -= 0.023
for t in ['High-water survey for the 9 m stream setback', 'Access road through the resort as a public street', 'Concept: redraw on the CAD survey before approval']:
    pn.text(0, y, t, fontsize=7.5); y -= 0.0195
fig.savefig(OUT + 'Jalkoti_Colony_v4_Rectangular.pdf'); fig.savefig(OUT + 'Jalkoti_Colony_v4_Rectangular.png', dpi=150)
with open(OUT + 'Jalkoti_Colony_v4_Plot_Schedule.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['Plot', 'Width (ft)', 'Depth (ft)', 'Width (m)', 'Depth (m)', 'Area (sq ft)', 'Area (m2)', 'Corner plot', 'Road frontage (m)'])
    for p in plots:
        fr = p['poly'].boundary.intersection(roads.buffer(0.3)).length
        w.writerow([p['no'], round(p['w'] * FT, 1), round(p['d'] * FT, 1), round(p['w'], 2), round(p['d'], 2), round(p['poly'].area * SQFT), round(p['poly'].area, 1), 'yes' if fr > p['w'] + 1 else '', round(fr, 1)])
pickle.dump(dict(G, plots=plots, gardens=gardens, club=club, svc=svc), open(SP + 'v4/final.pkl', 'wb'))
print('plots', len(A), round(tot), 'sqft', round(tot / SQFT / NA * 100, 1), 'pct | gardens', round(gsum / NA * 100, 1), '| far9', round(far9), 'far', round(far), '| sizes', dict(sz))
