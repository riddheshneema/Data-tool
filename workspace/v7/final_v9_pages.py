random.seed(5)
# ---------------- sheet 1: master plan with landscape
fig = plt.figure(figsize=(16.54, 11.69)); ax = fig.add_axes([0.006, 0.06, 0.74, 0.90]); S = Sheet(None); fp = base(ax, S, fs_no=6.2, dims=False, fs_dim=4.2, pretty=True)
def tree(x, y, r, c=None, z=7.5):
    ax.add_patch(Ellipse((x + r * 0.45, y - r * 0.45), r * 2.05, r * 2.05, color='#20351f', alpha=0.15, zorder=z - 0.2, lw=0))
    ax.add_patch(Circle((x, y), r, fc=c or random.choice(['#4f8a3a', '#5b9744', '#6aa34f', '#3f7a33']), ec='#2f5a2a', lw=0.25, zorder=z)); ax.add_patch(Circle((x - r * 0.25, y + r * 0.25), r * 0.55, fc='#fff', alpha=0.2, lw=0, zorder=z + 0.1))
lines_of = lambda g: [q for q in getattr(g, 'geoms', [g]) if q.geom_type == 'LineString' and q.length > 1]
track = [l for l in lines_of(K.buffer(-4.6, join_style=1).exterior.intersection(STRIP.buffer(0.3))) if l.length > 25]
for t in track: fp(t.simplify(1.0).buffer(1.0, cap_style=1), z=4.5, fc='#ecdcb3', ec='#b9a678', lw=0.3)
for off, ev, rr in ((-1.9, 8.5, 2.2), (-7.6, 10.5, 1.8)):
    for l in lines_of(K.buffer(off, join_style=1).exterior.intersection(STRIP.buffer(0.2))):
        for i in range(int(l.length / ev)):
            q = l.interpolate((i + random.uniform(0.15, 0.85)) * ev)
            if roads.distance(q) > rr + 0.4 and all(q.distance(t) > rr + 0.6 for t in track): tree(q.x, q.y, rr * random.uniform(0.85, 1.2), random.choice(['#3c7340', '#4a8249', '#2f6638']))
for vv in np.arange(46, VS - 14, 9.5):
    for du in (-4.75, 4.75): tree(*W.xy(GU + du, vv), 1.8, '#ee8f5a' if int(vv) % 2 else '#f1cb5c')
for nm, (l, w) in CL.items():
    if nm == 'avenue': continue
    for side in (1, -1):
        for seg in lines_of(l.offset_curve(side * (w / 2 - 0.8), join_style=1)):
            for i in range(int(seg.length / 13.5) + 1):
                q = seg.interpolate(6 + i * 13.5)
                if K.buffer(-2).contains(q) and not STRIP.buffer(1.5).contains(q) and CL['avenue'][0].distance(q) > 9 and q.distance(club) > 2: tree(q.x, q.y, 1.4, '#5f9c48', z=6.8)
pu, pv = W.uv(park.centroid.x, park.centroid.y)
ax.add_patch(Ellipse(W.xy(pu - 6, pv), 22, 15, angle=W.th, fc='#c9e9b2', ec='#fff', lw=0.6, zorder=3)); ax.add_patch(Circle(W.xy(pu + 14.5, pv), 4.4, fc='#ecdcae', ec='#b9a678', lw=0.4, zorder=4.6))
for dx, dy, c_ in ((-1.4, -0.8, '#e2574c'), (1.4, -0.9, '#3f8fc4'), (0, 1.5, '#f0b43c')): ax.add_patch(Circle(W.xy(pu + 14.5 + dx, pv + dy), 0.7, fc=c_, lw=0, zorder=4.8))
for uu in np.arange(pu - 20, pu + 21, 8): 
    for vv in (pv - 10.3, pv + 10.3): tree(*W.xy(uu, vv), 1.6, '#b7a0dc' if int(uu) % 2 else None)
for zone, ev in ((lawnW.difference(STRIP), 9), (grove, 7.5), (gardenN.difference(STRIP), 10), (svc, 5.5)):
    for q_ in parts(zone.buffer(-2.2)):
        if q_.area < 30: continue
        for i in range(int(q_.exterior.length / ev)):
            pt = q_.exterior.interpolate(i * ev + random.uniform(0, 2))
            if all(pt.distance(t) > 2.6 for t in track): tree(pt.x, pt.y, random.uniform(1.6, 2.2), '#e79ab3' if (zone is not svc and i % 5 == 0) else None)
lp = big(lawnW.difference(STRIP).buffer(-7)); 
if not lp.is_empty:
    c_ = lp.representative_point(); ax.add_patch(RegularPolygon((c_.x, c_.y), 6, radius=3.2, fc='#c0774b', ec='#7a4326', lw=0.5, zorder=6))
deck = W.rect(GU - 5.5, GU + 5.5, -1.5, 7.0); fp(deck, z=5, fc='#c79f6a', ec='#8a6a3b', lw=0.5)
cb = W.rect(GU + 9, GU + 22, VS - 18, VS - 5).intersection(club.buffer(-2)); fp(cb, z=5, fc='#b98d55', ec='#7a5a2e', lw=0.5); fp(W.rect(GU + 26, GU + 35, VS - 16, VS - 10.5).intersection(club.buffer(-2)), z=5, fc='#66c3e4', ec='#fff', lw=0.7)
fp(W.rect(GU - 7.5, GU + 7.5, VS - 1.1, VS + 1.1), z=9, fc='#3d2f1b', ec='none')
names(ax, S, fs=5.2, col='#ffffff'); ax.text(186, -74, 'S T R E A M', fontsize=9, color='#3d7ea6', rotation=24, zorder=9, style='italic'); ax.text(150, -262, 'RESORT LAND', fontsize=8, color='#9a8a62')
north(ax, S, 462, -66, 14); ax.plot([395, 445], [-262, -262], color='k', lw=2.2); ax.text(420, -267.5, '50 m  (164 ft)', ha='center', fontsize=7)
ax.set_xlim(108, 474); ax.set_ylim(-275, -40); ax.set_aspect('equal'); ax.axis('off')
pn = fig.add_axes([0.752, 0.03, 0.24, 0.94]); pn.axis('off'); pn.set_xlim(0, 1); pn.set_ylim(0, 1); y = 0.995
pn.text(0, y, 'JALKOTI COLONY', fontsize=15, weight='bold', va='top', color='#1e3a2b'); y -= 0.032; pn.text(0, y, 'Final layout v9 — no plot faces south.  Sheet 1 of 5', fontsize=8.4, va='top', color='#555'); y -= 0.045
def head(t):
    global y
    pn.text(0, y, t, fontsize=8.8, weight='bold', color='#1e3a2b'); y -= 0.007; pn.plot([0, 1], [y, y], color='#1e3a2b', lw=0.6); y -= 0.02
def row(a, b, c='', bold=False):
    global y
    k = dict(fontsize=6.9, weight='bold' if bold else 'normal'); pn.text(0, y, a, **k); pn.text(0.74, y, b, ha='right', **k); pn.text(1.0, y, c, ha='right', **k); y -= 0.0188
prom = green.area - gardenN.area - lawnW.area - grove.area - svc.area
head('AREA STATEMENT')
for nm, a in [(f'Plots ({len(plots)})', tot / SQFT), ('Roads (12 m Avenue, 9 m streets)', roads.area), ('Central Park', park.area), ('Stream Garden and Stream Lawn', gardenN.area + lawnW.area), ('East grove', grove.area),
              ('Stream promenade and verges', prom), ('Clubhouse plot', club.area), ('Services yard', svc.area)]: row(nm, f'{a:,.0f} m²', f'{a / NA * 100:.1f}%')
row('Total colony land', f'{NA:,.0f} m²', f'{NA / 4046.86:.2f} ac', bold=True); y -= 0.012
head('PLOTS'); row('Sellable area', f'{tot:,.0f} sq ft', f'{tot / SQFT / NA * 100:.1f}%', bold=True)
row('Smallest / average / largest', f"{min(p['area'] for p in plots):,.0f} / {tot / len(plots):,.0f} / {max(p['area'] for p in plots):,.0f}", 'sq ft')
for k_, l in (('N', 'Face north (on the stream)'), ('E', 'Face east'), ('W', 'Face west')):
    pn.add_patch(plt.Rectangle((0, y - 0.006), 0.035, 0.014, fc=COL[k_], ec='#5c4a2e', lw=0.4)); pn.text(0.05, y, l, fontsize=6.9); pn.text(0.74, y, str(fc[k_]), fontsize=6.9, ha='right'); y -= 0.0188
row('Face south', '0', '', bold=True); nrect = sum(1 for p in plots if p['rect'])
row('Rectangles', str(nrect)); row('Straight front, irregular back or side', str(len(plots) - nrect)); row('Standard depth', '75 ft (22.86 m)'); y -= 0.012
head('ROADS')
RL = [('Stream Drive', 'drive', 9), ('The Avenue', 'avenue', 12), ('First Street', 's0', 9), ('Second Street', 's1', 9), ('Third Street', 's2', 9)]
for nm, k_, w in RL: row(nm, f'{w} m wide', f"{CL[k_][0].intersection(K).length:.0f} m")
row('(Stream Drive includes West Street)', '', ''); row('Turning circles at 4 street ends', '7.5 m radius'); y -= 0.012
head('RULE CHECKS (BVN 2012)')
ops = park.area + gardenN.area + lawnW.area + grove.area
for t in [f"All plots over 225 m²; narrowest street front {min(p['w'] for p in plots) * FT:.1f} ft (Rule 53)", f'Parks and gardens {ops / NA * 100:.1f}% of the land in 4 places (Rule 47: 10%)',
          f"Farthest plot {max(p['d12'] for p in plots):.0f} m from the 12 m Avenue (9 m road limit 250 m)", f"Farthest plot {max(p['gate_m'] for p in plots):.0f} m from the gate (limit 400 m)",
          f"Dead-end streets up to {max(CL[k][0].length for k in ('s0', 's1', 's2')):.0f} m (limit 150 m), each with a turning circle", '9 m no-build strip along the stream throughout (Rule 50(b))', 'To confirm on site: high-water line, levels for drainage and STP']:
    pn.text(0, y, t, fontsize=6.5); y -= 0.0185
fig.text(0.006, 0.03, 'Number and area are shown on every plot. Trees, track and park features are a landscape concept on green land and road verges only.', fontsize=7, color='#444'); fig.text(0.006, 0.012, FOOT, fontsize=6.2, color='#666')
fig.savefig(OUTF + 'p1.pdf'); fig.savefig(OUTF + 'Final_1_Master_Plan.png', dpi=160); plt.close(fig)
# ---------------- sheets 2-4: dimensioned, drawn square to the streets
ZONES = [(2, 'West part', (-45, 92, -20, 158)), (3, 'Central part', (82, 212, -22, 158)), (4, 'East part', (196, 312, -22, 186))]
for n, nm, (ua, ub, va, vb) in ZONES:
    fig = plt.figure(figsize=(11.69, 16.54)); S = Sheet(W)
    fig.text(0.02, 0.982, f'JALKOTI COLONY — FINAL LAYOUT v9    Sheet {n} of 5', fontsize=13, weight='bold', color='#1e3a2b', va='top')
    fig.text(0.02, 0.965, f'{nm}: every plot with its number, area and side lengths in feet. Drawn square to the streets; see the north arrow.', fontsize=8.4, color='#444', va='top')
    ax = fig.add_axes([0.015, 0.075, 0.97, 0.875]); base(ax, S, fs_no=10, dims=True, fs_dim=6.2); names(ax, S, fs=7.0)
    ax.set_xlim(ua, ub); ax.set_ylim(-vb, -va); ax.set_aspect('equal'); ax.axis('off'); north(ax, S, ub - 12, -va - 16, 9)
    ax.plot([ua + 5, ua + 25], [-vb + 6, -vb + 6], color='k', lw=2.2); ax.text(ua + 15, -vb + 2.8, '20 m  (65.6 ft)', ha='center', fontsize=7)
    fig.text(0.02, 0.052, 'Red figures are side lengths in feet. A rectangle shows its street front and its depth; plots with an irregular back or side show every side.', fontsize=7)
    fig.text(0.02, 0.038, 'Blue plots face north, green face east, orange face west. Corner plots lose a small rounded piece at the junction; areas already allow for it. Dotted: 9 m no-build strip.', fontsize=7)
    fig.text(0.02, 0.018, FOOT, fontsize=6.2, color='#666'); fig.savefig(OUTF + f'p{n}.pdf'); fig.savefig(OUTF + f"Final_{n}_{nm.replace(' ', '_')}.png", dpi=150); plt.close(fig)
# ---------------- sheet 5: schedule + csv
fig = plt.figure(figsize=(16.54, 11.69)); fig.text(0.012, 0.975, 'JALKOTI COLONY — FINAL LAYOUT v9    Sheet 5 of 5', fontsize=13, weight='bold', color='#1e3a2b', va='top')
fig.text(0.012, 0.95, f'Plot schedule.  {len(plots)} plots, {tot:,.0f} sq ft.  No plot faces south.', fontsize=8.6, color='#444', va='top'); fig.text(0.988, 0.012, FOOT, fontsize=6.2, color='#666', ha='right')
tb = fig.add_axes([0.012, 0.03, 0.976, 0.895]); tb.axis('off'); tb.set_xlim(0, 2); tb.set_ylim(0, 1)
cols = [('No', 0.035, 'right'), ('Street', 0.05, 'left'), ('Faces', 0.17, 'left'), ('Front ft', 0.28, 'right'), ('Depth ft', 0.37, 'right'), ('Sq ft', 0.44, 'right'), ('m²', 0.50, 'right'), ('Notes', 0.52, 'left')]
per = (len(plots) + 1) // 2; rh = 0.0262; rowsout = []
for ci in range(2):
    for lbl, dx, ha in cols: tb.text(ci + dx, 0.985, lbl, fontsize=6.6, weight='bold', ha=ha, va='center')
    tb.plot([ci, ci + 0.97], [0.972, 0.972], color='#1e3a2b', lw=0.6)
    for ri, p in enumerate(plots[ci * per:(ci + 1) * per]):
        yv = 0.972 - (ri + 0.7) * rh
        if ri % 2 == 0: tb.add_patch(plt.Rectangle((ci, yv - rh / 2), 0.97, rh, fc='#f5f1e6', ec='none'))
        dep = f"{p['d'] * FT:.1f}" if p['rect'] else f"{p['dmin'] * FT:.0f}–{p['dmax'] * FT:.0f}"
        vals = [str(p['no']), p['street'], FACE[p['face']], f"{p['w'] * FT:.1f}", dep, f"{p['area']:,.0f}", f"{p['area'] / SQFT:.1f}", '; '.join(p['notes'])[:70]]
        for (lbl, dx, ha), v_ in zip(cols, vals): tb.text(ci + dx, yv, v_, fontsize=6.3, ha=ha, va='center', weight='bold' if lbl == 'No' else 'normal')
fig.savefig(OUTF + 'p5.pdf'); fig.savefig(OUTF + 'Final_5_Plot_Schedule.png', dpi=150); plt.close(fig)
with open(OUTF + 'Jalkoti_Colony_v9_Plot_Schedule.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['Plot', 'Street', 'Faces', 'Front (ft)', 'Depth (ft)', 'Area (sq ft)', 'Area (m2)', 'Shape', 'Notes', 'Drive from gate (m)'])
    for p in plots: w.writerow([p['no'], p['street'], FACE[p['face']], round(p['w'] * FT, 1), round(p['d'] * FT, 1) if p['rect'] else f"{p['dmin'] * FT:.0f}-{p['dmax'] * FT:.0f}", round(p['area']), round(p['area'] / SQFT, 1), 'rectangle' if p['rect'] else 'straight front, irregular back or side', '; '.join(p['notes']), round(p['gate_m'])])
import pymupdf, ezdxf
from ezdxf.enums import TextEntityAlignment
doc = pymupdf.open()
for i in range(1, 6): d = pymupdf.open(OUTF + f'p{i}.pdf'); doc.insert_pdf(d); d.close(); os.remove(OUTF + f'p{i}.pdf')
doc.save(OUTF + 'Jalkoti_Colony_v9_Final_Drawing_Set.pdf', deflate=True); doc.close()
dx = ezdxf.new('R2010', setup=True); dx.units = ezdxf.units.M; msp = dx.modelspace()
for nm, col in (('BOUNDARY', 1), ('PLOTS', 7), ('ROADS', 8), ('ROAD_CENTRE', 5), ('PARK', 3), ('CLUBHOUSE', 30), ('STREAM_STRIP_9M', 4), ('PLOT_NO', 2), ('PLOT_AREA', 6), ('DIMS_FT', 1)): dx.layers.add(nm, color=col)
def poly(g, layer):
    for q in parts(g):
        for ring in [q.exterior] + list(q.interiors): msp.add_lwpolyline(list(ring.coords)[:-1], close=True, dxfattribs={'layer': layer})
poly(K, 'BOUNDARY'); poly(roads, 'ROADS'); poly(park, 'PARK'); poly(club, 'CLUBHOUSE'); poly(STRIP, 'STREAM_STRIP_9M')
for l, w in CL.values(): msp.add_lwpolyline(list(l.coords), dxfattribs={'layer': 'ROAD_CENTRE'})
for p in plots:
    poly(p['poly'], 'PLOTS'); c = p['poly'].centroid; fr = frame_of(p); rot = up(fr.th + (90 if fr is W2 else 0))
    msp.add_text(str(p['no']), dxfattribs={'height': 2.4, 'layer': 'PLOT_NO', 'rotation': rot}).set_placement((c.x, c.y), align=TextEntityAlignment.MIDDLE_CENTER)
    for x, y_, a, t in labels(p): msp.add_text(t, dxfattribs={'height': 1.0, 'layer': 'DIMS_FT', 'rotation': up(a)}).set_placement((x, y_), align=TextEntityAlignment.MIDDLE_CENTER)
dx.saveas(OUTF + 'Jalkoti_Colony_v9_Final_Layout.dxf')
G = [p['poly'] for p in plots]
print('plots %d | %.0f sq ft | %.1f%% | faces %s | rect %d | parks %.1f%% | far12 %.0f gate %.0f | overlaps %d | in strip %.2f | on roads %.2f | min front %.1f ft min area %.0f' % (len(plots), tot, tot / SQFT / NA * 100, dict(fc), nrect, ops / NA * 100,
      max(p['d12'] for p in plots), max(p['gate_m'] for p in plots), sum(1 for i in range(len(G)) for j in range(i + 1, len(G)) if G[i].intersection(G[j]).area > 0.01), sum(g.intersection(R.buffer(9)).area for g in G), sum(g.intersection(roads).area for g in G), min(p['w'] for p in plots) * FT, min(p['area'] for p in plots)))
print('areas: gardenN %.0f lawn %.0f grove %.0f svc %.0f' % (gardenN.area, lawnW.area, grove.area, svc.area), sorted(os.listdir(OUTF)))
