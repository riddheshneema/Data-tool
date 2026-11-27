# pages of the final set (runs inside final_set.py)
tot = sum(p['area'] for p in info)
loop_l, s3_l, ave_l, cr_l = CL['loop'][0], CL['s3'][0], CL['avenue'][0], CL['cross'][0]
d1 = loop_l.project(Point(W.xy(WU + RC, mid('drive')))); d2 = loop_l.project(Point(W.xy(WU + RB, mid('s2'))))
k1 = s3_l.project(Point(W.xy(SU + RB, mid('s3'))))
STREETS = [('Stream Drive', 9.0, d1), ('West Loop', 9.0, d2 - d1), ('Second Street', 9.0, loop_l.length - d2), ('Third Street', 9.0, s3_l.length - k1),
           ('South-west link', 9.0, k1), ('Cross Street', 9.0, cr_l.length), ('The Avenue', 12.0, ave_l.intersection(K).length)]
D_ = L['A1'][1] - L['A1'][0]; PWd = park.area / (L['B2'][1] - L['B1'][0])
# ---------------- sheet 2: key dimensions (north up)
fig = plt.figure(figsize=(16.54, 11.69)); title(fig, 2, 'Key dimensions', 'Roads, blocks, park and overall sizes. North is up.')
ax = fig.add_axes([0.008, 0.03, 0.735, 0.90]); S = Sheet(None); base(ax, S, dims=False, area=False); road_names(ax, S, fs=5.4)
for p in info:
    fr = FR[p['grid']]; c = p['poly'].centroid; s = -1 if p['front'] == 'lo' else 1
    ax.text(c.x + fr.ev[0] * s * 5.0, c.y + fr.ev[1] * s * 5.0, str(p['no']), fontsize=5.6, weight='bold', ha='center', va='center', zorder=7, color='#2b2014', rotation=up(fr.th))
for row in ('A1', 'A2', 'B1', 'B2', 'C1'):
    for gname in ('W', 'E'):
        fr = FR[gname]; ps = sorted([p for p in info if p['row'] == row and p['grid'] == gname], key=lambda p: fr.uv(p['poly'].centroid.x, p['poly'].centroid.y)[0])
        runs = []
        for p in ps:
            if runs and runs[-1][-1]['poly'].distance(p['poly']) < 0.6: runs[-1].append(p)
            else: runs.append([p])
        for r_ in runs:
            if len(r_) < 2: continue
            U = unary_union([p['poly'] for p in r_]); us = [fr.uv(x, y)[0] for x, y in U.convex_hull.exterior.coords]; vs = [fr.uv(x, y)[1] for x, y in U.convex_hull.exterior.coords]
            ln = sum((p['front_w'] + p['back_w']) / 2 if not p.get('special') else p['wide'] for p in r_); s = 1 if r_[0]['front'] == 'lo' else -1
            vm = (L[row][0] + L[row][1]) / 2 + s * 5.2
            ax.text(*fr.xy((min(us) + max(us)) / 2, vm), f"{len(r_)} plots · {ln * FT:.0f} ft ({ln:.1f} m)", fontsize=4.9, ha='center', va='center', zorder=7, color='#b3261e', rotation=up(fr.th))
north(ax, S, 462, -66, 14); ax.plot([395, 445], [-262, -262], color='k', lw=2.2); ax.text(420, -267.5, '50 m  (164 ft)', ha='center', fontsize=7)
ax.set_xlim(108, 474); ax.set_ylim(-275, -40); ax.set_aspect('equal'); ax.axis('off')
pn = fig.add_axes([0.75, 0.03, 0.242, 0.90]); pn.axis('off'); pn.set_xlim(0, 1); pn.set_ylim(0, 1); y = 0.985
def head(t):
    global y
    pn.text(0, y, t, fontsize=8.8, weight='bold', color='#1e3a2b'); y -= 0.008; pn.plot([0, 1], [y, y], color='#1e3a2b', lw=0.6); y -= 0.021
def row(a, b, c='', bold=False):
    global y
    k = dict(fontsize=6.9, weight='bold' if bold else 'normal'); pn.text(0, y, a, **k); pn.text(0.70, y, b, ha='right', **k); pn.text(1.0, y, c, ha='right', **k); y -= 0.0195
head('ROADS'); row('Road', 'Width', 'Length', bold=True)
for nm, w, ln in STREETS: row(nm, f'{w:.1f} m ({w * FT:.1f} ft)', f'{ln:.0f} m')
row('Total', '', f'{sum(s_[2] for s_ in STREETS):,.0f} m', bold=True); row('Kerb radius at junctions', '4.5 m'); row('West Loop bends (centre line)', f'{RC} m and {RB} m'); row('Turning circles (2)', '8.0 m radius'); y -= 0.012
head('SECTION, STREAM TO SOUTH LINE')
for nm, d in [('No-build strip from the stream', 9.0), ('Stream Drive', 9.0), ('Plot row (Stream Drive)', D_), ('Plot row (Second St, north)', D_), ('Second Street', 9.0), ('Plot row (Second St, south)', D_),
              ('Plot row (Third St, north)', D_), ('Third Street', 9.0), ('Plot row (Third St, south)', D_)]: row(nm, f'{d:.2f} m', f'{d * FT:.1f} ft')
row('Total depth', f'{rv.VS:.2f} m', f'{rv.VS * FT:.0f} ft', bold=True); y -= 0.012
head('PLOTS AND PLACES')
row('Plots', str(len(info)), f'{tot:,.0f} sq ft', bold=True); row('Standard plot depth', f'{D_:.2f} m', '75.0 ft'); row('Narrowest street front', f"{min(p['front_w'] for p in info):.2f} m", f"{min(p['front_w'] for p in info) * FT:.1f} ft")
row('Central Park', f"{PWd:.1f} × {L['B2'][1] - L['B1'][0]:.1f} m", f'{park.area:,.0f} m²'); row('Clubhouse plot', '', f'{club.area:,.0f} m²'); row('Stream Garden', '', f"{V['gardenN'].area:,.0f} m²")
row('Stream Lawn', '', f"{V['lawnW'].area:,.0f} m²"); row('Services yard', '', f"{V['svc'].area:,.0f} m²"); row('Colony land', f'{NA:,.0f} m²', f'{NA / 4046.86:.2f} ac', bold=True); row('Sellable', '', f'{tot / SQFT / NA * 100:.1f}%', bold=True); y -= 0.012
head('SETTING OUT')
for t_ in [f'West grid: streets run N {90 - W.th:.2f}° E', f'East grid: streets run N {90 - E.th:.2f}° E', 'The two grids meet on the centre line of Cross Street.', 'Red figures on the plan: plots in each run and the',
           'run length along the street.', 'Plot-by-plot side lengths are on sheets 3 to 5.']:
    pn.text(0, y, t_, fontsize=6.8); y -= 0.0185
fig.savefig(OUTF + 'p2.pdf'); fig.savefig(OUTF + 'Final_2_Key_Dimensions.png', dpi=150); plt.close(fig)
# ---------------- sheets 3-5: enlarged, every plot dimensioned (drawn square to the streets)
ZONES = [(3, 'West part', W, (-47, 88, -20, 158)), (4, 'Central part', W, (72, 207, -22, 156)), (5, 'East part', E, (58, 200, -24, 178))]
for n, nm, fr, (ua, ub, va, vb) in ZONES:
    fig = plt.figure(figsize=(11.69, 16.54)); S = Sheet(fr)
    fig.text(0.02, 0.982, f'JALKOTI COLONY — FINAL LAYOUT    Sheet {n} of 6', fontsize=13, weight='bold', color='#1e3a2b', va='top')
    fig.text(0.02, 0.965, f'{nm}: every plot with its number, area and side lengths in feet. Drawn square to the streets; see the north arrow.', fontsize=8.4, color='#444', va='top')
    ax = fig.add_axes([0.015, 0.075, 0.97, 0.875]); base(ax, S, fs_no=10, dims=True, fs_dim=6.3); road_names(ax, S, fs=7.2)
    ax.set_xlim(ua, ub); ax.set_ylim(-vb, -va); ax.set_aspect('equal'); ax.axis('off')
    north(ax, S, ub - 12, -va - 16, 9); scalebar(ax, ua + 5, -vb + 6)
    fig.text(0.02, 0.052, 'Red figures are side lengths in feet. A plain rectangle shows its street front and its depth; corner plots on Cross Street and the four larger plots show every side.', fontsize=7)
    fig.text(0.02, 0.038, 'Corner plots lose a small rounded piece at the junction (4.5 m kerb radius); their areas already allow for it. Dotted green: 9 m no-build strip from the stream.', fontsize=7)
    fig.text(0.02, 0.018, 'Concept layout for the owner. Dimensions are computed from the survey outline; a licensed surveyor must set out on site before any sale or submission.', fontsize=6.2, color='#666')
    fig.savefig(OUTF + f'p{n}.pdf'); fig.savefig(OUTF + f"Final_{n}_{nm.replace(' ', '_')}.png", dpi=150); plt.close(fig)
# ---------------- sheet 6: schedule
fig = plt.figure(figsize=(16.54, 11.69)); title(fig, 6, 'Plot schedule', f'{len(info)} plots, {tot:,.0f} sq ft.')
tb = fig.add_axes([0.012, 0.03, 0.976, 0.895]); tb.axis('off'); tb.set_xlim(0, 2); tb.set_ylim(0, 1)
cols = [('No', 0.035, 'right'), ('Street', 0.05, 'left'), ('Side', 0.175, 'left'), ('Faces', 0.26, 'left'), ('Front ft', 0.36, 'right'), ('Back ft', 0.42, 'right'), ('Depth ft', 0.50, 'right'), ('Sq ft', 0.565, 'right'), ('m²', 0.62, 'right'), ('Notes', 0.64, 'left')]
per = (len(info) + 1) // 2; rh = 0.0238
for ci in range(2):
    for lbl, dx, ha in cols: tb.text(ci + dx, 0.985, lbl, fontsize=6.6, weight='bold', ha=ha, va='center')
    tb.plot([ci + 0.0, ci + 0.97], [0.972, 0.972], color='#1e3a2b', lw=0.6)
    for ri, p in enumerate(sorted(info, key=lambda p: p['no'])[ci * per:(ci + 1) * per]):
        yv = 0.972 - (ri + 0.7) * rh
        if ri % 2 == 0: tb.add_patch(plt.Rectangle((ci, yv - rh / 2), 0.97, rh, fc='#f5f1e6', ec='none'))
        side = 'stream side' if p['row'] == 'A1' else ('north side' if p['row'] in ('A2', 'B2') else 'south side')
        sp = bool(p.get('special')); note = []
        if sp: note.append(p['shape'].split(':')[0].split(';')[0])
        elif 'cross' in p['shape']: note.append('corner on Cross Street, one side 6° off square')
        elif p['corner']: note.append('corner')
        for tg in ('stream-facing', 'park-facing', 'park-side', 'beside the stream lawn'):
            if tg in p['tags']: note.append(tg)
        if any('T-junction' in c for c in p['cautions']): note.append('faces a T-junction')
        if any('services' in c for c in p['cautions']): note.append('backs onto services yard')
        vals = [str(p['no']), p['street'], side, 'North' if p['front'] == 'lo' else 'South', f"{p['front_w'] * FT:.1f}", '' if sp else f"{p['back_w'] * FT:.1f}",
                (f"{p['dmin'] * FT:.0f}–{p['dmax'] * FT:.0f}" if sp else f"{p['depth'] * FT:.1f}"), f"{p['area']:,.0f}", f"{p['area'] / SQFT:.1f}", '; '.join(note)[:62]]
        for (lbl, dx, ha), v_ in zip(cols, vals): tb.text(ci + dx, yv, v_, fontsize=6.3, ha=ha, va='center', weight='bold' if lbl == 'No' else 'normal')
fig.savefig(OUTF + 'p6.pdf'); fig.savefig(OUTF + 'Final_6_Plot_Schedule.png', dpi=150); plt.close(fig)
# ---------------- one PDF + DXF
import pymupdf, shutil
doc = pymupdf.open()
for f in [rv.OUT + 'Jalkoti_Colony_v8_Landscape.pdf'] + [OUTF + f'p{i}.pdf' for i in (2, 3, 4, 5, 6)]:
    d = pymupdf.open(f); doc.insert_pdf(d); d.close()
doc.save(OUTF + 'Jalkoti_Colony_Final_Drawing_Set.pdf', deflate=True); doc.close()
for i in (2, 3, 4, 5, 6): os.remove(OUTF + f'p{i}.pdf')
shutil.copy(rv.OUT + 'Jalkoti_Colony_v8_Landscape.png', OUTF + 'Final_1_Master_Plan.png')
shutil.copy(rv.OUT + 'Jalkoti_Colony_v8_Plot_Schedule.csv', OUTF + 'Jalkoti_Colony_Final_Plot_Schedule.csv')
import ezdxf
from ezdxf.enums import TextEntityAlignment
dx = ezdxf.new('R2010', setup=True); dx.units = ezdxf.units.M; msp = dx.modelspace()
for nm, col in (('BOUNDARY', 1), ('PLOTS', 7), ('ROADS', 8), ('ROAD_CENTRE', 5), ('PARK', 3), ('CLUBHOUSE', 30), ('STREAM_STRIP_9M', 4), ('PLOT_NO', 2), ('PLOT_AREA', 6), ('DIMS_FT', 1)): dx.layers.add(nm, color=col)
def poly(g, layer):
    for q in parts(g):
        for ring in [q.exterior] + list(q.interiors): msp.add_lwpolyline(list(ring.coords)[:-1], close=True, dxfattribs={'layer': layer})
poly(K, 'BOUNDARY'); poly(roads, 'ROADS'); poly(park, 'PARK'); poly(club, 'CLUBHOUSE'); poly(STRIP, 'STREAM_STRIP_9M')
for l, w in CL.values(): msp.add_lwpolyline(list(l.coords), dxfattribs={'layer': 'ROAD_CENTRE'})
for p in info:
    poly(p['poly'], 'PLOTS'); c = p['poly'].centroid; rot = up(FR[p['grid']].th)
    msp.add_text(str(p['no']), dxfattribs={'height': 2.4, 'layer': 'PLOT_NO', 'rotation': rot}).set_placement((c.x, c.y + 1.5), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text(f"{p['area']:,.0f} sq ft", dxfattribs={'height': 1.2, 'layer': 'PLOT_AREA', 'rotation': rot}).set_placement((c.x, c.y - 2.0), align=TextEntityAlignment.MIDDLE_CENTER)
    for x, y_, a, t in labels(p): msp.add_text(t, dxfattribs={'height': 1.0, 'layer': 'DIMS_FT', 'rotation': up(a)}).set_placement((x, y_), align=TextEntityAlignment.MIDDLE_CENTER)
dx.saveas(OUTF + 'Jalkoti_Colony_Final_Layout.dxf')
print('final set saved:', sorted(os.listdir(OUTF)))
print('streets', [(a, round(c)) for a, b, c in STREETS])
