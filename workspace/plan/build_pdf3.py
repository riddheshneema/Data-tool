"""Portrait drawing set: cover + 7 sheets, every sheet portrait with the same frame and title block."""
src2 = open('build_pdf2.py').read()
exec(src2.split("\npdf = PdfPages(PDF)")[0])          # data, drawing helpers, tables, sections
PDF = OUT + 'Jalkoti_Colony_Dimensioned_Layout.pdf'
A3P_ = (297, 420); A0P_ = (841, 1189)
NS = 7
SH = [(1, 'Location and approach', 'From the Jalkoti–Maheshwar road to the colony gate', '1:3500', 'A3'),
      (2, 'Colony layout', 'Plot numbers and areas, roads, open space, services', '1:1400', 'A3'),
      (3, 'Dimensioned layout', 'Whole colony: every plot side, road, median and garden', '1:500', 'A0'),
      (4, 'Plot dimension schedule', 'Area, frontage and every side of all 62 plots', '—', 'A3'),
      (5, 'Roads, medians, open space, services', 'Widths, lengths, cross-sections, area statement', '—', 'A3'),
      (6, 'Dimension sheet – west half', 'River-front plots R6–R19, S3 and S4 blocks, the bend', '1:700', 'A3'),
      (7, 'Dimension sheet – east half', 'R1–R5, S1, S2, S5 and the gate area', '1:700', 'A3')]
def sheetp(size_mm, num, title, desc, scale, paper):
    W, H = size_mm; f = W / 297.0
    fig = plt.figure(figsize=(W * MM, H * MM))
    fr = fig.add_axes((0, 0, 1, 1)); fr.axis('off'); fr.set_xlim(0, W); fr.set_ylim(0, H)
    m = 8 * f; tb = 21 * f
    fr.add_patch(Rectangle((m, m), W - 2 * m, H - 2 * m, fc='none', ec=INK, lw=1.0 * f))
    fr.add_patch(Rectangle((m, m), W - 2 * m, tb, fc='#fafafa', ec=INK, lw=0.8 * f))
    xa = m + (W - 2 * m) * 0.40; xb = m + (W - 2 * m) * 0.76; ym = m + tb * 0.5
    for x in (xa, xb): fr.plot([x, x], [m, m + tb], color=INK, lw=0.5 * f)
    fr.plot([xb, W - m], [ym, ym], color=INK, lw=0.4 * f)
    fr.text(m + 2.5 * f, m + tb * 0.70, 'JALKOTI COLONY · MAHESHWAR', fontsize=8.6 * f, weight='bold', color=INK, va='center')
    fr.text(m + 2.5 * f, m + tb * 0.42, 'Khargone, Madhya Pradesh', fontsize=6.4 * f, color=MUTE, va='center')
    fr.text(m + 2.5 * f, m + tb * 0.18, 'Survey Drg SU/10/01 · 23.325 acres', fontsize=6.4 * f, color=MUTE, va='center')
    fr.text(xa + 2.5 * f, m + tb * 0.66, title, fontsize=8.6 * f, weight='bold', color=INK, va='center')
    fr.text(xa + 2.5 * f, m + tb * 0.30, desc if len(desc) < 58 else desc[:56] + '…', fontsize=6.0 * f, color=MUTE, va='center')
    fr.text(xb + 2.5 * f, m + tb * 0.76, (f'Sheet {num} of {NS}' if num else 'Cover') + f'  ·  {paper} portrait', fontsize=7.2 * f, weight='bold', color=INK, va='center')
    fr.text(xb + 2.5 * f, m + tb * 0.25, f'Scale {scale}  ·  {TODAY}', fontsize=6.2 * f, color=MUTE, va='center')
    fr.text(W - m - 2.5 * f, m + tb * 0.25, 'Concept', fontsize=6.2 * f, color='#b71c1c', va='center', ha='right')
    if num:
        fr.text(m + 3 * f, H - m - 6.5 * f, f'{num:02d}', fontsize=17 * f, weight='bold', color=ACC, va='center')
        fr.text(m + 15 * f, H - m - 5.0 * f, title.upper(), fontsize=11 * f, weight='bold', color=INK, va='center')
        fr.text(m + 15 * f, H - m - 10.2 * f, desc, fontsize=7.0 * f, color=MUTE, va='center')
    content = (m + 3 * f, m + tb + 3 * f, W - m - 3 * f, H - m - (15 * f if num else 3 * f))
    return fig, fr, content, f
pdf = PdfPages(PDF)
md = pdf.infodict(); md['Title'] = 'Jalkoti colony – dimensioned layout drawings (portrait)'

# ===================================================== COVER
fig, fr, cb, f = sheetp(A3P_, 0, 'Drawing set – cover and index', 'Dimensioned layout drawings for the colony', 'as noted', 'A3'); x0, y0, x1, y1 = cb
p = panel(fig, (x0 + 4, y1 - 62, x1 - 4, y1 - 4), A3P_)
p.text(0, 0.98, 'JALKOTI COLONY', fontsize=30, weight='bold', color=ACC, va='top')
p.text(0, 0.50, 'Maheshwar · Khargone · Madhya Pradesh', fontsize=12, color=INK, va='top')
p.text(0, 0.22, 'Dimensioned layout drawings · portrait set', fontsize=9.5, color=MUTE, va='top')
kax = map_in(fig, (x0 + 2, y1 - 62 - 182, x1 - 2, y1 - 64), A3P_, (283, -166), 1450)
V = box(kax.get_xlim()[0], kax.get_ylim()[0], kax.get_xlim()[1], kax.get_ylim()[1])
draw_colony(kax, V, lw=0.35, trees=True, labels=False)
north(kax, 462, -272, 13, 9); scalebar(kax, 112, -296, 100, 25, 5.5)
p2 = panel(fig, (x0 + 4, y0 + 2, x1 - 4, y1 - 62 - 186), A3P_)
kp = [(f'{len(PL)}', 'plots'), (f'{TOT / 4046.86:.2f}', 'acres'), (f'{100 * SALE / TOT:.1f}%', 'sellable'), ('12 m', 'all roads'), (f'{100 * rpark.area / TOT:.1f}%', 'open space')]
for i, (v, l) in enumerate(kp):
    xx = i * 0.2
    p2.add_patch(FancyBboxPatch((xx, 0.80), 0.185, 0.17, boxstyle='round,pad=0.006,rounding_size=0.02', fc='#f1f8e9', ec='#c5e1a5', lw=0.6))
    p2.text(xx + 0.015, 0.935, v, fontsize=15, weight='bold', color=ACC, va='top'); p2.text(xx + 0.015, 0.845, l, fontsize=7.5, color=INK, va='top')
p2.text(0, 0.72, 'SHEET INDEX', fontsize=10, weight='bold', color=INK, va='top')
yy = 0.64
for n, t, d, s_, pap in SH:
    p2.text(0.0, yy, f'{n:02d}', fontsize=8.2, weight='bold', color=ACC, va='top'); p2.text(0.06, yy, t, fontsize=8.2, weight='bold', color=INK, va='top')
    p2.text(0.47, yy, d if len(d) < 50 else d[:48] + '…', fontsize=6.4, color=MUTE, va='top'); p2.text(1.0, yy, f'{pap} · {s_}', fontsize=6.4, color=MUTE, va='top', ha='right'); yy -= 0.085
pdf.savefig(fig); fig.savefig('p_cover.png', dpi=50); plt.close(fig)

# ===================================================== 1. LOCATION AND APPROACH (1:3500)
fig, fr, cb, f = sheetp(A3P_, *SH[0][:4], 'A3'); x0, y0, x1, y1 = cb
ax = map_in(fig, (x0, y0, x0 + 172, y1), A3P_, (362, -488), 3500)
V = box(ax.get_xlim()[0], ax.get_ylim()[0], ax.get_xlim()[1], ax.get_ylim()[1])
fill(ax, R.intersection(V), fc=COL['river'], ec='#5aa9d6', lw=0.5)
riv_lines = wkt.loads(A['river']).intersection(box(300, -960, 700, -540))
for l in getattr(riv_lines, 'geoms', [riv_lines]):
    if l.geom_type == 'LineString' and l.length > 3: ax.plot(*l.xy, color='#5aa9d6', lw=0.45)
fill(ax, RS, fc=COL['resort'], ec='#a8781a', lw=0.7); fill(ax, C, fc='white', ec='none'); fill(ax, rpark, fc=COL['garden'], ec='none')
fill(ax, row, fc='#9e9e9e', ec='none'); fill(ax, gard, fc=COL['med'], ec='none')
for t, pp in PL.items(): fill(ax, pp, fc=COL['rplot'] if KIND[t] != 'Villa' else 'white', ec='#c62828', lw=0.2)
fill(ax, svc, fc=COL['svc'], ec='#5d4037', lw=0.4); ax.plot(*C.exterior.xy, color=COL['bnd'], lw=1.3)
for pp in pickle.load(open('../site/geo.pkl', 'rb'))['P']: ax.plot(*pp.exterior.xy, color='#33691e', lw=0.5, ls=(0, (5, 2)))
fill(ax, AP['exist_poly'], fc='#757575', ec='#424242', lw=0.6); fill(ax, AP['poly'], fc='#9e9e9e', ec='#616161', lw=0.4)
fill(ax, SPLAY, fc='#9e9e9e', ec='none'); fill(ax, access, fc='#9e9e9e', ec='#616161', lw=0.4)
for side in ('left', 'right'):
    try: ed = AP['cl'].parallel_offset(8.6, side, join_style=2)
    except Exception: ed = None
    for l in getattr(ed, 'geoms', [ed]) if ed is not None else []:
        for s_ in np.arange(6, l.length, 15):
            q = l.interpolate(s_); ax.add_patch(plt.Circle((q.x, q.y), 2.8, fc='#7cb342', ec='#33691e', lw=0.3))
for l in getattr(AP['bridge'], 'geoms', [AP['bridge']]):
    if l.geom_type == 'LineString' and l.length > 2: ax.plot(*l.xy, color='#d32f2f', lw=1.2)
if AP['mandir'] is not None and not AP['mandir'].is_empty:
    mb = AP['mandir'].bounds; ax.add_patch(Rectangle((mb[0], mb[1]), mb[2] - mb[0], mb[3] - mb[1], fc='#ffe0b2', ec='#e65100', lw=0.5)); ax.text(mb[2] + 4, mb[3], 'Mandir', fontsize=5.5, va='center')
def tag(n, x, y): ax.text(x, y, str(n), fontsize=7.5, weight='bold', color='white', ha='center', va='center', bbox=dict(boxstyle='circle,pad=0.22', fc=ACC, ec='none'))
ex = AP['exist_poly'].bounds; ae = Point(AP['cl'].coords[0]); bc = AP['bridge'].centroid
tag(1, (ex[0] + ex[2]) / 2, ex[1] - 22); tag(2, AP['cl'].interpolate(0.7, normalized=True).x + 22, AP['cl'].interpolate(0.7, normalized=True).y)
tag(3, bc.x + 28, bc.y + 8); tag(4, ae.x - 22, ae.y - 10); tag(5, 360, -372); tag(6, 352, -248)
ax.text(ex[0] - 3, (ex[1] + ex[3]) / 2, '← Jalkoti', fontsize=6, va='center', ha='right'); ax.text(ex[2] + 3, (ex[1] + ex[3]) / 2, 'Maheshwar →', fontsize=6, va='center', ha='left')
ax.text(258, -165, 'COLONY', fontsize=9, weight='bold', color=ACC, ha='center'); ax.text(235, -400, 'RESORT', fontsize=9, weight='bold', color='#7a5410', ha='center')
ax.text(370, -700, 'stream', fontsize=6, color='#1f5f8b', rotation=-35, ha='center', style='italic')
vx = ax.get_xlim(); vy = ax.get_ylim()
north(ax, vx[1] - 30, vy[1] - 120, 45, 9); scalebar(ax, vx[0] + 25, vy[0] + 25, 200, 50, 5.5)
pn = panel(fig, (x0 + 178, y0 + 2, x1, y1 - 2), A3P_)
yy = h(pn, 0.995, 'THE ROUTE FROM THE MAIN ROAD', 9.5)
steps = [('1', 'Existing Jalkoti–Maheshwar road', f"main road, about {AP['exist_w']:.1f} m wide"),
         ('2', f"Approach road · about {AP['len']:.0f} m", '15 m ROW, 9 m carriageway, avenue trees'),
         ('3', 'Bridge over the stream', 'on the approach road, as surveyed'),
         ('4', 'Main entry', 'entry splay joins the access road'),
         ('5', f'Access road · about {ACC_LEN:.0f} m', '15 m, through the resort land'),
         ('6', 'Colony gate', f'{len(PL)} plots inside; all roads 12 m')]
for n_, t_, d_ in steps:
    pn.text(0.0, yy, n_, fontsize=7.5, weight='bold', color='white', va='top', bbox=dict(boxstyle='circle,pad=0.25', fc=ACC, ec='none'))
    pn.text(0.11, yy + 0.003, t_, fontsize=7.6, weight='bold', color=INK, va='top'); pn.text(0.11, yy - 0.020, d_, fontsize=6.2, color='#455a64', va='top'); yy -= 0.055
yy -= 0.01
pn.add_patch(FancyBboxPatch((0, yy - 0.075), 1.0, 0.075, boxstyle='round,pad=0.005,rounding_size=0.015', fc='#f1f8e9', ec='#c5e1a5', lw=0.6))
pn.text(0.04, yy - 0.012, 'Main road → colony gate', fontsize=7.4, color=INK, va='top'); pn.text(0.04, yy - 0.034, f'about {ROUTE:.0f} m', fontsize=12, weight='bold', color=ACC, va='top')
yy -= 0.10
yy = h(pn, yy, 'ROAD SECTIONS (m)', 8.5)
xsection(pn, 0.0, yy - 0.022, 0.78, SEC['approach'], 'Approach road (survey)', fs=5.6); xsection(pn, 0.0, yy - 0.10, 0.78, SEC['access'], 'Access road', fs=5.6)
yy -= 0.19
yy = h(pn, yy, 'AREAS', 8.5)
for l in ['Site as surveyed: 23.325 acres', f'Colony: {TOT / 4046.86:.2f} acres', f'Resort: {RS.area / 4046.86:.2f} acres']:
    pn.text(0, yy, '•  ' + l, fontsize=6.6, color='#37474f', va='top'); yy -= 0.026
yy -= 0.012
for l in ['Dedicate the approach road and', 'the access road as public roads', 'before the colony application', '(BVN Rules 2(72), 38(6)).']:
    pn.text(0, yy, l, fontsize=6.4, color='#b71c1c', va='top'); yy -= 0.022
pn.text(0, 0.0, 'Approach road, bridge, existing\nroad and mandir traced from the\nsurvey (Drg SU/10/01, 1:1000).', fontsize=5.6, color=MUTE, va='bottom')
pdf.savefig(fig); fig.savefig('p_s1.png', dpi=50); plt.close(fig)

# ===================================================== 2. COLONY LAYOUT (1:1400)
fig, fr, cb, f = sheetp(A3P_, *SH[1][:4], 'A3'); x0, y0, x1, y1 = cb
mh = 190
ax = map_in(fig, (x0, y1 - mh, x1, y1), A3P_, (282, -166), 1400)
V = box(ax.get_xlim()[0], ax.get_ylim()[0], ax.get_xlim()[1], ax.get_ylim()[1])
draw_colony(ax, V, lw=0.4, trees=True, labels=True, fs=3.3)
road_dims(ax, V, fs=4.2, arrow_lw=0.5)
ax.text(150, -103, 'RIVERSIDE GARDEN – 15 m', color='#33691e', fontsize=5, rotation=52, weight='bold')
ax.annotate('COLONY GATE', (331, -262), xytext=(352, -280), fontsize=5.2, weight='bold', arrowprops=dict(arrowstyle='->', lw=0.6))
north(ax, 462, -272, 13, 8); scalebar(ax, 108, -292, 100, 25, 5)
pl_ = panel(fig, (x0, y0, x0 + 140, y1 - mh - 6), A3P_)
yy = h(pl_, 0.995, 'AREA STATEMENT', 9)
yy = area_table(pl_, 0, yy - 0.004, 6.0, 0.052, W=1.0)
yy -= 0.03; pl_.text(0, yy, f'SELLABLE {SALE * SQ:,.0f} sq ft', fontsize=9, weight='bold', color=ACC, va='top'); yy -= 0.05
pl_.text(0, yy, f'{SALE / 4046.86:.2f} acres · {100 * SALE / TOT:.1f}% of the colony', fontsize=7.2, color=INK, va='top')
pr_ = panel(fig, (x0 + 148, y0, x1, y1 - mh - 6), A3P_)
yy = h(pr_, 0.995, 'PLOTS', 9)
for l in [f'{nR} river-front plots, {min(pa):,.0f}–{max(pa):,.0f} sq ft', f'{nV} villa plots, {min(va):,.0f}–{max(va):,.0f} sq ft', 'Typical villa plot 45 × 90 ft (4,050 sq ft)', 'Every frontage above 12 m (BVN 53)']:
    pr_.text(0, yy, '•  ' + l, fontsize=6.6, color='#37474f', va='top'); yy -= 0.045
yy -= 0.02; yy = h(pr_, yy, 'ROADS – ALL 12 m', 9)
for l in ['RD river drive · S1 east street', 'S2, S3, S4 garden streets (3 m median)', 'S5 link road joins S1 to S2', f'Access road 15 m · {ACC_LEN:.0f} m to the main entry', 'Dead ends: S2 stub, RD south (turning space)']:
    pr_.text(0, yy, '•  ' + l, fontsize=6.6, color='#37474f', va='top'); yy -= 0.045
legend(pr_, 'lower left', 5.6, ncol=2, bbox=(0, 0.0))
pdf.savefig(fig); fig.savefig('p_s2.png', dpi=50); plt.close(fig)

# ===================================================== 3. DIMENSIONED LAYOUT + SCHEDULES (A0 portrait, 1:500)
fig, fr, cb, f = sheetp(A0P_, *SH[2][:4], 'A0'); x0, y0, x1, y1 = cb
mh = 530
ax = map_in(fig, (x0, y1 - mh, x1, y1), A0P_, (282, -165), 500)
V = box(ax.get_xlim()[0], ax.get_ylim()[0], ax.get_xlim()[1], ax.get_ylim()[1])
draw_colony(ax, V, lw=0.6, labels=True, fs=5.8, dims=True, dfs=4.8)
road_dims(ax, V, fs=6.6, arrow_lw=0.8); median_dims(ax, V, fs=5.0); garden_dims(ax, V, fs=6.2); boundary_dims(ax, V, fs=5.6); misc_labels(ax, V, fs=6.0)
ax.text(150, -103, 'RIVERSIDE GARDEN – 15 m wide (open space, 12.9%)', color='#33691e', fontsize=8.5, rotation=52, weight='bold')
north(ax, 462, -270, 10, 13); scalebar(ax, 105, -290, 50, 10, 8)
lowtop = y1 - mh - 16
L_ = panel(fig, (x0, y0, x0 + 250, lowtop), A0P_)
yy = 0.995
for hd, lines in [('HOW TO READ THIS SHEET', ['Blue figures inside each plot: side lengths in feet (1 m = 3.281 ft)', '"arc": curved side, measured along the curve', 'Bold: plot number and area in sq ft',
                                             'Blue arrows across roads: right-of-way width in metres', 'White text on green: garden median width × length (m)', 'Green arrows: riverside garden width (m)',
                                             'Dark green outside the boundary: boundary lengths (m)', 'T: turning space 12 × 11 m at a dead end']),
                  ('SETBACKS (BVN 2012, Rule 56)', ['Front 3.6 m on a 12 m road', 'Rear 3.0 m · sides 3.0 m each (detached)', 'River-front plots: 15 m garden + 3 m rear setback']),
                  ('ACCURACY', ['Measured from the survey scan (Drg SU/10/01), ±0.5 m', 'Redraw on the CAD survey and verify on site', 'before marking out or selling']),
                  ('SCHEDULES', ['Every plot side in feet and metres: Sheet 4', 'Roads, medians, open space, areas: Sheet 5', 'The same plan in two halves for A3 printing: Sheets 6–7'])]:
    L_.text(0, yy, hd, fontsize=14, weight='bold', color=INK, va='top'); yy -= 0.036
    for l in lines: L_.text(0, yy, '•  ' + l, fontsize=10.5, color='#37474f', va='top'); yy -= 0.029
    yy -= 0.022
M_ = panel(fig, (x0 + 262, y0, x0 + 540, lowtop), A0P_)
M_.text(0, 0.995, 'ROAD CROSS-SECTIONS (metres)', fontsize=14, weight='bold', color=INK, va='top')
for k_, (nm, key) in enumerate([('12 m plain road – RD, S1, S5, gate road', 'plain'), ('12 m garden street – S2, S3, S4', 'garden'), ('15 m access road – through the resort', 'access'), ('15 m approach road – survey section', 'approach')]):
    xsection(M_, 0.0, 0.90 - k_ * 0.17, 0.80, SEC[key], nm, fs=10)
M_.text(0, 0.18, f'Every colony road is 12 m. The farthest plot (V43) is 360 m from the colony gate.', fontsize=10, color='#37474f', va='top')
M_.text(0, 0.13, f'Garden medians: 3.0 m wide on S2 ({MED[0]["len"]:.0f} m), S3 ({MED[1]["len"]:.0f} m), S4 ({MED[2]["len"]:.0f} m).', fontsize=10, color='#37474f', va='top')
M_.text(0, 0.08, f'Riverside garden: 15 m wide, about {GARD["len_inner"]:.0f} m along the plots ({rpark.area:,.0f} m²).', fontsize=10, color='#37474f', va='top')
R_ = panel(fig, (x0 + 552, y0, x1, lowtop), A0P_)
R_.text(0, 0.995, 'KEY FIGURES', fontsize=14, weight='bold', color=INK, va='top')
kf = [(f'{len(PL)}', 'plots'), (f'{SALE * SQ:,.0f}', 'sq ft sellable'), (f'{100 * SALE / TOT:.1f}%', 'of the colony'), (f'{TOT / 4046.86:.2f}', 'acres in the colony'), (f'{100 * rpark.area / TOT:.1f}%', 'open space')]
for k_, (v, l) in enumerate(kf):
    yk = 0.93 - k_ * 0.095
    R_.add_patch(FancyBboxPatch((0, yk - 0.075), 1.0, 0.075, boxstyle='round,pad=0.004,rounding_size=0.02', fc='#f1f8e9', ec='#c5e1a5', lw=0.8))
    R_.text(0.05, yk - 0.0375, v, fontsize=20, weight='bold', color=ACC, va='center'); R_.text(0.55, yk - 0.0375, l, fontsize=10.5, color=INK, va='center')
legend(R_, 'lower left', 10, ncol=1, bbox=(0, 0.0))
pdf.savefig(fig); fig.savefig('p_s3.png', dpi=20); plt.close(fig)

# ===================================================== 6. PLOT SCHEDULE (one A3 portrait sheet)
fig, fr, cb, f = sheetp(A3P_, *SH[3][:4], 'A3'); x0, y0, x1, y1 = cb
T_ = panel(fig, (x0, y0, x1, y1), A3P_)
T_.text(0, 0.997, 'Sides clockwise from the front (main road side). Road sides carry the road name; "arc" = curved side measured along the curve.', fontsize=5.8, color='#37474f', va='top')
cols = [(0.05, 'left'), (0.075, 'left'), (0.06, 'right'), (0.055, 'right'), (0.10, 'left'), (0.33, 'left'), (0.33, 'left')]
rows = [(t, 'River-front' if KIND[t] != 'Villa' else 'Villa', f"{INFO[t]['sqft']:,.0f}", f"{INFO[t]['sqm']:,.1f}", f"{INFO[t]['front']:.1f} m · {'+'.join(INFO[t]['roads'])}", side_txt(INFO[t]['sides'], 'ft'), side_txt(INFO[t]['sides'], 'm')) for t in ORDER]
yy = table(T_, 0, 0.978, cols, rows, ('Plot', 'Type', 'sq ft', 'm²', 'Frontage', 'Sides in feet', 'Sides in metres'), 4.9, 0.0150)
T_.text(0, yy - 0.006, f'Total {len(PL)} plots · {SALE * SQ:,.0f} sq ft ({SALE:,.0f} m²) · {100 * SALE / TOT:.1f}% of the colony', fontsize=6.8, weight='bold', color=ACC, va='top')
T_.text(1.0, yy - 0.006, 'Measured from the survey scan (±0.5 m) – verify on site.', fontsize=5.4, color='#b71c1c', va='top', ha='right')
pdf.savefig(fig); fig.savefig('p_s4.png', dpi=60); plt.close(fig)

# ===================================================== 7. ROADS, MEDIANS, OPEN SPACE, SERVICES
fig, fr, cb, f = sheetp(A3P_, *SH[4][:4], 'A3'); x0, y0, x1, y1 = cb
P_ = panel(fig, (x0, y0, x1, y1), A3P_)
yy = h(P_, 0.995, 'ROADS', 9)
rc = [(0.13, 'left'), (0.47, 'left'), (0.09, 'right'), (0.15, 'right'), (0.16, 'right')]
rr = [(r_['name'], r_['desc'].split(' – ')[-1], f"{r_['row']:.0f} m", f"{(ACC_LEN if r_['name'] == 'Access road' else r_['len']):.0f}", f"{r_['area']:,.0f}") for r_ in ROADS_]
rr += [('Approach road', 'Main road → bridge → main entry (survey)', '15 m', f"{AP['len']:.0f}", f"{AP['poly'].area:,.0f}"),
       ('Entry splay', 'Approach road to access road at the main entry', '—', '—', f'{SPLAY.area:,.0f}'),
       ('Existing road', 'Jalkoti ← main road → Maheshwar (survey)', f"{AP['exist_w']:.1f} m", '—', '—')]
yy = table(P_, 0, yy - 0.002, rc, rr, ('Road', 'Runs', 'ROW', 'Length m', 'Area m²'), 5.4, 0.0175)
P_.text(0, yy - 0.006, 'Lengths along the centre-line, junctions counted once. Farthest plot (V43) is 360 m from the colony gate (BVN 38: 12 m roads up to 400 m).', fontsize=5.2, color='#455a64', va='top')
yy -= 0.03; yy = h(P_, yy, 'ROAD CROSS-SECTIONS (metres)', 9)
for k_, (nm, key) in enumerate([('12 m plain road – RD, S1, S5, gate road', 'plain'), ('12 m garden street – S2, S3, S4', 'garden'), ('15 m access road – through the resort', 'access'), ('15 m approach road – survey section', 'approach')]):
    xx = 0.0 if k_ % 2 == 0 else 0.52; yk = yy - 0.02 - (k_ // 2) * 0.06
    xsection(P_, xx, yk, 0.36, SEC[key], nm, fs=5.2)
yy -= 0.145; yy = h(P_, yy, 'GARDEN MEDIANS', 9)
mc = [(0.22, 'left'), (0.12, 'right'), (0.15, 'right'), (0.15, 'right'), (0.36, 'left')]
mr = [(f"Median on {m_['road']}", '3.0', f"{m_['len']:.1f}", f"{m_['area']:,.0f}", 'stops 4 m short of junctions') for m_ in MED]
mr.append(('Total', '', f"{sum(m_['len'] for m_ in MED):.1f}", f"{sum(m_['area'] for m_ in MED):,.0f}", 'road land, not open space'))
yy = table(P_, 0, yy - 0.002, mc, mr, ('Median', 'Width m', 'Length m', 'Area m²', 'Note'), 5.4, 0.0175)
yy -= 0.018; ytop = yy
L_w, W_w = mrr_dims(walk); L_s, W_s = mrr_dims(svc)
orows = [('Riverside garden', f'15 m wide · {GARD["len_inner"]:.0f} m along plots', f'{rpark.area:,.0f}'), ('7 ft walkway', f'{W_w:.2f} × {L_w:.1f} m (R10/R11)', f'{walk.area:,.0f}'),
         ('Services plot', f'{L_s:.1f} × {W_s:.1f} m at the gate', f'{svc.area:,.0f}'), ('   STP', '10.0 × 8.0 m', '80'), ('   Tank + tubewell', '7.0 × 7.0 m', '49'), ('   Waste point', '5.0 × 4.0 m', '20'),
         ('Turning spaces', f'{len(DE)} × 12 × 11 m (in roads)', f'{132 * len(DE)}'), ('Landscaped corners', f'{len(CORN)} pieces', f'{sum(q.area for q in CORN):,.0f}')]
P_.text(0, ytop, 'OPEN SPACE, WALKWAY, SERVICES', fontsize=9, weight='bold', color=INK, va='top')
table(P_, 0, ytop - 0.03, [(0.155, 'left'), (0.23, 'left'), (0.085, 'right')], orows, ('Item', 'Dimensions', 'Area m²'), 5.2, 0.0175)
P_.text(0.52, ytop, 'AREA STATEMENT – COLONY', fontsize=9, weight='bold', color=INK, va='top')
cols_a = [(0.48 * 0.44, 'left'), (0.48 * 0.08, 'center'), (0.48 * 0.17, 'right'), (0.48 * 0.15, 'right'), (0.48 * 0.16, 'right')]
rows_a = [(n, c, f'{a * SQ:,.0f}', f'{a:,.0f}', f'{100 * a / TOT:.1f}') for n, c, a in AREA_ROWS] + [('Total colony', f'{len(PL)}', f'{TOT * SQ:,.0f}', f'{TOT:,.0f}', '100.0')]
ya = table(P_, 0.52, ytop - 0.03, cols_a, rows_a, ('Use', 'No.', 'sq ft', 'm²', '%'), 5.2, 0.0175)
P_.text(0.52, ya - 0.012, f'SELLABLE {SALE * SQ:,.0f} sq ft = {SALE / 4046.86:.2f} acres = {100 * SALE / TOT:.1f}%', fontsize=7.4, weight='bold', color=ACC, va='top')
P_.text(1.0, 0.0, 'Plot sides in feet (1 m = 3.281 ft); everything else in metres. Measured from the survey scan (±0.5 m). Concept only.', fontsize=5.2, color='#455a64', va='bottom', ha='right')
pdf.savefig(fig); fig.savefig('p_s5.png', dpi=60); plt.close(fig)
# ===================================================== 4-5. WEST / EAST HALVES (1:700)
for hi, cen in enumerate([(189, -165), (378, -165)]):
    fig, fr, cb, f = sheetp(A3P_, *SH[5 + hi][:4], 'A3'); x0, y0, x1, y1 = cb
    ax = map_in(fig, (x0, y0, x1, y1), A3P_, cen, 700)
    V = box(ax.get_xlim()[0], ax.get_ylim()[0], ax.get_xlim()[1], ax.get_ylim()[1])
    draw_colony(ax, V, lw=0.5, labels=True, fs=4.4, dims=True, dfs=3.9)
    road_dims(ax, V, fs=5.0); median_dims(ax, V, fs=3.9); garden_dims(ax, V, fs=4.8, every=(0.1, 0.3, 0.5, 0.7, 0.9)); boundary_dims(ax, V, fs=4.5); misc_labels(ax, V, fs=4.6)
    vx = ax.get_xlim(); vy = ax.get_ylim()
    kb = (x1 - 52, y1 - 38, x1 - 2, y1 - 2) if hi == 1 else (x0 + 2, y0 + 2, x0 + 52, y0 + 38)
    k = fig.add_axes(ax_mm(fig, kb, A3P_)); k.set_aspect('equal'); k.axis('off')
    k.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle='round,pad=0.02', fc='white', ec='#90a4ae', lw=0.5, transform=k.transAxes))
    k.fill(*C.exterior.xy, fc='#eeeeee', ec=COL['bnd'], lw=0.7); fill(k, row, fc='#bdbdbd', ec='none')
    k.add_patch(Rectangle((vx[0], vy[0]), vx[1] - vx[0], vy[1] - vy[0], fc='#ff8f00', alpha=0.22, ec='#e65100', lw=0.9))
    b_ = C.bounds; k.set_xlim(b_[0] - 8, b_[2] + 8); k.set_ylim(b_[1] - 8, b_[3] + 8)
    north(ax, vx[1] - 10, vy[0] + 12 if hi == 0 else vy[0] + 12, 9, 7)
    pdf.savefig(fig); fig.savefig(f'p_s{6 + hi}.png', dpi=50); plt.close(fig)

pdf.close(); print('saved', PDF)
