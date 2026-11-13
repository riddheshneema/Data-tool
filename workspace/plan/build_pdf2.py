"""Polished, all-landscape drawing set (cover + 10 sheets), same frame and title block on every sheet."""
src = open('build_pdf.py').read()
exec(src.split("pdf = PdfPages(PDF)")[0])
exec(src.split("# ================================================================ helpers for the panels")[1].split("# ================================================================ 2. COLONY LAYOUT")[0])
from matplotlib.patches import FancyBboxPatch
pa = [INFO[t]['sqft'] for t in PL if KIND[t] != 'Villa']; va = [INFO[t]['sqft'] for t in PL if KIND[t] == 'Villa']
def side_txt(sd, unit):
    out = []
    for s_ in sd:
        v = s_['len'] * FT if unit == 'ft' else s_['len']
        t = f'{v:.1f}' if unit == 'ft' else f'{v:.2f}'
        if s_['road']: t += f" {s_['nb']}"
        if s_['curved']: t += ' arc'
        out.append(t)
    return ' · '.join(out)
PDF = OUT + 'Jalkoti_Colony_Dimensioned_Layout.pdf'
A3 = (420, 297); A0 = (1189, 841)
NSHEETS = 10
INK = '#263238'; ACC = '#1b5e20'; MUTE = '#607d8b'
SHEETS = [(1, 'Location and approach', 'From the Jalkoti–Maheshwar road to the colony gate', '1:4000', 'A3'),
          (2, 'Colony layout', 'Plot numbers and areas, roads, open space, services', '1:1250', 'A3'),
          (3, 'Dimensioned layout', 'Every plot side (ft); roads, medians, garden, boundary (m)', '1:400', 'A0'),
          (4, 'Dimension sheet – north-west', 'River-front plots R6–R14, the bend, S4 block', '1:500', 'A3'),
          (5, 'Dimension sheet – north-east', 'River-front plots R1–R5, S2/S3 blocks, S1', '1:500', 'A3'),
          (6, 'Dimension sheet – south-west', 'R15–R19, S4 and S3 blocks, RD south end', '1:500', 'A3'),
          (7, 'Dimension sheet – south-east', 'S5 link plots, gate, services plot', '1:500', 'A3'),
          (8, 'Plot schedule – R1 to V12', 'Area, frontage and every side of each plot', '—', 'A3'),
          (9, 'Plot schedule – V13 to V43', 'Area, frontage and every side of each plot', '—', 'A3'),
          (10, 'Roads, medians, open space, services', 'Widths, lengths, cross-sections, area statement', '—', 'A3')]
def sheet(size_mm, num, title, desc, scale, paper):
    W, H = size_mm; f = W / 420.0          # scale factor relative to A3
    fig = plt.figure(figsize=(W * MM, H * MM))
    fr = fig.add_axes((0, 0, 1, 1)); fr.axis('off'); fr.set_xlim(0, W); fr.set_ylim(0, H)
    m = 8 * f; tb = 17 * f
    fr.add_patch(Rectangle((m, m), W - 2 * m, H - 2 * m, fc='none', ec=INK, lw=1.0 * f))
    fr.add_patch(Rectangle((m, m), W - 2 * m, tb, fc='#fafafa', ec=INK, lw=0.8 * f))
    cols = [0.0, 0.30, 0.62, 0.74, 0.86, 1.0]; xs = [m + (W - 2 * m) * c for c in cols]
    for x in xs[1:-1]: fr.plot([x, x], [m, m + tb], color=INK, lw=0.5 * f)
    def cell(i, top, bot, fs1=8.5, fs2=6.5):
        fr.text(xs[i] + 2.5 * f, m + tb * 0.66, top, fontsize=fs1 * f, weight='bold', color=INK, va='center')
        fr.text(xs[i] + 2.5 * f, m + tb * 0.28, bot, fontsize=fs2 * f, color=MUTE, va='center')
    cell(0, 'JALKOTI COLONY · MAHESHWAR', 'Khargone, Madhya Pradesh · Survey Drg SU/10/01 · 23.325 acres')
    cell(1, title, desc)
    cell(2, f'Sheet {num} of {NSHEETS}' if num else 'Cover', paper + ' landscape')
    cell(3, f'Scale {scale}', 'Units: m; plot sides in ft')
    cell(4, TODAY, 'Concept – not an approved drawing')
    if num:
        fr.text(m + 3 * f, H - m - 6.5 * f, f'{num:02d}', fontsize=17 * f, weight='bold', color=ACC, va='center')
        fr.text(m + 15 * f, H - m - 5.0 * f, title.upper(), fontsize=11.5 * f, weight='bold', color=INK, va='center')
        fr.text(m + 15 * f, H - m - 10.2 * f, desc, fontsize=7.2 * f, color=MUTE, va='center')
    content = (m + 3 * f, m + tb + 3 * f, W - m - 3 * f, H - m - (15 * f if num else 3 * f))   # x0, y0, x1, y1 in mm
    return fig, fr, content, f
def ax_mm(fig, box_mm, size_mm):
    W, H = size_mm; x0, y0, x1, y1 = box_mm
    return (x0 / W, y0 / H, (x1 - x0) / W, (y1 - y0) / H)
def map_in(fig, box_mm, size_mm, center, N):
    return map_axes(fig, ax_mm(fig, box_mm, size_mm), center, N)
def panel(fig, box_mm, size_mm):
    a = fig.add_axes(ax_mm(fig, box_mm, size_mm)); a.axis('off'); a.set_xlim(0, 1); a.set_ylim(0, 1); return a
def h(a, y, s, fs=9.5, col=INK): a.text(0, y, s, fontsize=fs, weight='bold', color=col, transform=a.transAxes, va='top'); return y - fs * 0.0042
def section_box(a, x, y, w, hgt, fc='#f1f8e9'):
    a.add_patch(FancyBboxPatch((x, y), w, hgt, boxstyle='round,pad=0.004,rounding_size=0.01', fc=fc, ec='none', transform=a.transAxes))
def xsection(a, x0, y0, w, parts, title, fs=6.2):
    a.text(x0, y0, title, fontsize=fs + 0.6, weight='bold', transform=a.transAxes, va='bottom', color=INK)
    tot = sum(p[0] for p in parts); sc = w / tot; xx = x0
    for wd, lab, c in parts:
        a.add_patch(Rectangle((xx, y0 - 0.05), wd * sc, 0.035, fc=c, ec='#455a64', lw=0.4, transform=a.transAxes))
        a.text(xx + wd * sc / 2, y0 - 0.0325, f'{wd:g}', ha='center', va='center', fontsize=fs, weight='bold', color='white' if c in ('#9e9e9e', '#2e7d32') else 'k', transform=a.transAxes)
        if lab: a.text(xx + wd * sc / 2, y0 - 0.058, lab, ha='center', va='top', fontsize=fs - 1, transform=a.transAxes, color='#455a64')
        xx += wd * sc
    a.text(x0 + w + 0.01, y0 - 0.0325, f'= {tot:g} m', va='center', fontsize=fs + 0.4, weight='bold', transform=a.transAxes)
SEC = {'plain': [(2.25, 'verge', '#a5d6a7'), (7.5, 'carriageway', '#9e9e9e'), (2.25, 'verge', '#a5d6a7')],
       'garden': [(1.0, 'path', '#cfd8dc'), (3.5, 'lane', '#9e9e9e'), (3.0, 'median', '#2e7d32'), (3.5, 'lane', '#9e9e9e'), (1.0, 'path', '#cfd8dc')],
       'access': [(3.0, 'verge', '#a5d6a7'), (9.0, 'carriageway', '#9e9e9e'), (3.0, 'verge', '#a5d6a7')],
       'approach': [(2.0, 'trees', '#a5d6a7'), (1.0, '', '#cfd8dc'), (9.0, 'carriageway', '#9e9e9e'), (1.0, '', '#cfd8dc'), (2.0, 'trees', '#a5d6a7')]}
ROUTE = round((AP['len'] + Point(AP['cl'].coords[0]).distance(Point(335.5, -484)) + ACC_LEN) / 5) * 5
pdf = PdfPages(PDF)
md = pdf.infodict(); md['Title'] = 'Jalkoti colony – dimensioned layout drawings'; md['Subject'] = 'Location, layout, dimensioned layout and schedules'

# ===================================================== COVER
fig, fr, cb, f = sheet(A3, 0, 'Drawing set – cover and index', 'Dimensioned layout drawings for the colony', 'as noted', 'A3')
x0, y0, x1, y1 = cb
p = panel(fig, (x0 + 6, y0 + 4, x0 + 170, y1 - 6), A3)
p.text(0, 0.985, 'JALKOTI COLONY', fontsize=30, weight='bold', color=ACC, va='top')
p.text(0, 0.885, 'Maheshwar · Khargone · Madhya Pradesh', fontsize=12, color=INK, va='top')
p.text(0, 0.835, 'Dimensioned layout drawings', fontsize=10, color=MUTE, va='top')
kp = [(f'{len(PL)}', 'plots'), (f'{TOT / 4046.86:.2f}', 'acres'), (f'{100 * SALE / TOT:.1f}%', 'sellable'), ('12 m', 'all roads'), (f'{100 * rpark.area / TOT:.1f}%', 'open space')]
for i, (v, l) in enumerate(kp):
    xx = (i % 3) * 0.33; yy = 0.70 - (i // 3) * 0.14
    p.add_patch(FancyBboxPatch((xx, yy - 0.10), 0.30, 0.105, boxstyle='round,pad=0.006,rounding_size=0.02', fc='#f1f8e9', ec='#c5e1a5', lw=0.6))
    p.text(xx + 0.02, yy - 0.025, v, fontsize=17, weight='bold', color=ACC, va='top'); p.text(xx + 0.02, yy - 0.072, l, fontsize=8, color=INK, va='top')
p.text(0, 0.40, 'SHEET INDEX', fontsize=10, weight='bold', color=INK, va='top')
yy = 0.355
for n, t, d, s_, pap in SHEETS:
    p.text(0.0, yy, f'{n:02d}', fontsize=8.2, weight='bold', color=ACC, va='top'); p.text(0.07, yy, t, fontsize=8.2, weight='bold', color=INK, va='top')
    p.text(0.55, yy, d if len(d) < 52 else d[:50] + '…', fontsize=6.6, color=MUTE, va='top'); p.text(1.0, yy, f'{pap} · {s_}', fontsize=6.6, color=MUTE, va='top', ha='right'); yy -= 0.034
kax = map_in(fig, (x0 + 182, y0 + 4, x1 - 2, y1 - 2), A3, (283, -166), 1900)
V = box(*kax.get_xlim()[:1], kax.get_ylim()[0], kax.get_xlim()[1], kax.get_ylim()[1])
draw_colony(kax, V, lw=0.35, trees=True, labels=False)
kax.text(150, -100, 'riverside garden', color='#33691e', fontsize=6, rotation=52)
north(kax, 470, -275, 14, 9); scalebar(kax, 120, -300, 100, 25, 5.5)
pdf.savefig(fig); fig.savefig('v2_cover.png', dpi=55); plt.close(fig)

# ===================================================== 1. LOCATION AND APPROACH (1:4000)
fig, fr, cb, f = sheet(A3, *SHEETS[0][:4], 'A3'); x0, y0, x1, y1 = cb
N1 = 4000
ax = map_in(fig, (x0, y0, x0 + 165, y1), A3, (360, -492), N1)
V = box(ax.get_xlim()[0], ax.get_ylim()[0], ax.get_xlim()[1], ax.get_ylim()[1])
fill(ax, R.intersection(V), fc=COL['river'], ec='#5aa9d6', lw=0.5)
riv_lines = wkt.loads(A['river']).intersection(box(300, -960, 700, -540))
for l in getattr(riv_lines, 'geoms', [riv_lines]):
    if l.geom_type == 'LineString' and l.length > 3: ax.plot(*l.xy, color='#5aa9d6', lw=0.45)
fill(ax, RS, fc=COL['resort'], ec='#a8781a', lw=0.7); fill(ax, C, fc='white', ec='none'); fill(ax, rpark, fc=COL['garden'], ec='none')
fill(ax, row, fc='#9e9e9e', ec='none'); fill(ax, gard, fc=COL['med'], ec='none')
for t, pp in PL.items(): fill(ax, pp, fc=COL['rplot'] if KIND[t] != 'Villa' else 'white', ec='#c62828', lw=0.2)
fill(ax, svc, fc=COL['svc'], ec='#5d4037', lw=0.4); ax.plot(*C.exterior.xy, color=COL['bnd'], lw=1.3)
PARC = pickle.load(open('../site/geo.pkl', 'rb'))['P']
for pp in PARC: ax.plot(*pp.exterior.xy, color='#33691e', lw=0.5, ls=(0, (5, 2)))
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
def tag(n, x, y):
    ax.text(x, y, str(n), fontsize=7.5, weight='bold', color='white', ha='center', va='center', bbox=dict(boxstyle='circle,pad=0.22', fc=ACC, ec='none'))
ex = AP['exist_poly'].bounds; ae = Point(AP['cl'].coords[0]); bc = AP['bridge'].centroid
tag(1, (ex[0] + ex[2]) / 2, ex[1] - 22); tag(2, AP['cl'].interpolate(0.7, normalized=True).x + 22, AP['cl'].interpolate(0.7, normalized=True).y)
tag(3, bc.x + 28, bc.y + 8); tag(4, ae.x - 22, ae.y - 10); tag(5, 360, -372); tag(6, 352, -248)
ax.text(ex[0] - 3, (ex[1] + ex[3]) / 2, '← Jalkoti', fontsize=6, va='center', ha='right'); ax.text(ex[2] + 3, (ex[1] + ex[3]) / 2, 'Maheshwar →', fontsize=6, va='center', ha='left')
ax.text(258, -165, 'COLONY', fontsize=9, weight='bold', color=ACC, ha='center'); ax.text(235, -400, 'RESORT', fontsize=9, weight='bold', color='#7a5410', ha='center')
ax.text(370, -700, 'stream', fontsize=6, color='#1f5f8b', rotation=-35, ha='center', style='italic')
north(ax, 640, -175, 45, 9); scalebar(ax, 430, -55, 200, 50, 5.5)
pn = panel(fig, (x0 + 172, y0 + 2, x1, y1 - 2), A3)
yy = h(pn, 0.995, 'THE ROUTE FROM THE MAIN ROAD', 10)
steps = [('1', 'Existing Jalkoti–Maheshwar road', f"the main road, about {AP['exist_w']:.1f} m wide as surveyed"),
         ('2', f"Approach road – about {AP['len']:.0f} m", '15 m right of way, 9 m carriageway, avenue trees both sides'),
         ('3', 'Bridge over the stream', 'on the approach road, as surveyed'),
         ('4', 'Main entry', 'an entry splay joins the approach road to the access road'),
         ('5', f'Access road – about {ACC_LEN:.0f} m', '15 m, through the resort land to the colony gate'),
         ('6', 'Colony gate', f'{len(PL)} plots inside; all colony roads 12 m')]
for n_, t_, d_ in steps:
    pn.text(0.0, yy, n_, fontsize=8, weight='bold', color='white', va='top', bbox=dict(boxstyle='circle,pad=0.25', fc=ACC, ec='none'))
    pn.text(0.06, yy + 0.004, t_, fontsize=8.4, weight='bold', color=INK, va='top'); pn.text(0.06, yy - 0.027, d_, fontsize=6.8, color='#455a64', va='top'); yy -= 0.066
yy -= 0.005
pn.add_patch(FancyBboxPatch((0, yy - 0.075), 1.0, 0.075, boxstyle='round,pad=0.005,rounding_size=0.015', fc='#f1f8e9', ec='#c5e1a5', lw=0.6))
pn.text(0.03, yy - 0.020, f'Main road to the colony gate: about {ROUTE:.0f} m', fontsize=9.5, weight='bold', color=ACC, va='top')
pn.text(0.03, yy - 0.050, 'Farthest plot (V43) is a further 360 m along the 12 m colony roads.', fontsize=7, color=INK, va='top')
yy -= 0.11
yy = h(pn, yy, 'ROAD SECTIONS (metres)', 9)
xsection(pn, 0.0, yy - 0.025, 0.40, SEC['approach'], 'Approach road (survey section)'); xsection(pn, 0.52, yy - 0.025, 0.36, SEC['access'], 'Access road through the resort')
yy -= 0.13
yy = h(pn, yy, 'AREAS', 9)
for l in [f'Site as surveyed: 23.325 acres', f'Colony: {TOT / 4046.86:.2f} acres (incl. services plot)', f'Resort: {RS.area / 4046.86:.2f} acres (incl. the 15 m access road)']:
    pn.text(0, yy, '•  ' + l, fontsize=7.0, color='#37474f', va='top'); yy -= 0.03
yy -= 0.008
pn.text(0, yy, 'Both the approach road and the access road should be dedicated as public roads before the colony application (BVN Rules 2(72) and 38(6)).', fontsize=6.6, color='#b71c1c', va='top', wrap=True)
pn.text(0, 0.0, 'Approach road, bridge, existing road and mandir are traced from the survey (Drg SU/10/01, 1:1000); widths from its road lines and road section.', fontsize=5.8, color=MUTE, va='bottom')
pdf.savefig(fig); fig.savefig('v2_s1.png', dpi=55); plt.close(fig)

# ===================================================== 2. COLONY LAYOUT (1:1250)
fig, fr, cb, f = sheet(A3, *SHEETS[1][:4], 'A3'); x0, y0, x1, y1 = cb
N2 = 1250
ax = map_in(fig, (x0, y0, x0 + 304, y1), A3, (283, -164), N2)
V = box(ax.get_xlim()[0], ax.get_ylim()[0], ax.get_xlim()[1], ax.get_ylim()[1])
draw_colony(ax, V, lw=0.4, trees=True, labels=True, fs=3.6)
road_dims(ax, V, fs=4.4, arrow_lw=0.5)
ax.text(150, -103, 'RIVERSIDE GARDEN – 15 m', color='#33691e', fontsize=5.5, rotation=52, weight='bold')
ax.annotate('COLONY GATE', (331, -262), xytext=(352, -276), fontsize=5.5, weight='bold', arrowprops=dict(arrowstyle='->', lw=0.6))
north(ax, 458, -266, 12, 8); scalebar(ax, 110, -286, 100, 25, 5)
pn = panel(fig, (x0 + 310, y0, x1, y1), A3)
yy = h(pn, 0.995, 'AREA STATEMENT', 8.5)
yy = area_table(pn, 0, yy - 0.004, 5.6, 0.031, W=1.0)
yy -= 0.02; pn.text(0, yy, f'SELLABLE {SALE * SQ:,.0f} sq ft', fontsize=8.5, weight='bold', color=ACC, va='top'); yy -= 0.032
pn.text(0, yy, f'{SALE / 4046.86:.2f} acres · {100 * SALE / TOT:.1f}% of the colony', fontsize=7, color=INK, va='top'); yy -= 0.05
yy = h(pn, yy, 'PLOTS', 8.5)
for l in [f'{nR} river-front plots, {min(pa):,.0f}–{max(pa):,.0f} sq ft', f'{nV} villa plots, {min(va):,.0f}–{max(va):,.0f} sq ft', 'Typical villa plot 45 × 90 ft (4,050 sq ft)', 'Every frontage above 12 m (BVN 53)']:
    pn.text(0, yy, '•  ' + l, fontsize=6.4, color='#37474f', va='top'); yy -= 0.03
yy -= 0.015; yy = h(pn, yy, 'ROADS – ALL 12 m', 8.5)
for l in ['RD river drive · S1 east street', 'S2, S3, S4 garden streets (3 m median)', 'S5 link road joins S1 to S2', f'Access road 15 m · {ACC_LEN:.0f} m to the main entry', 'Dead ends: S2 stub, RD south – turning space']:
    pn.text(0, yy, '•  ' + l, fontsize=6.4, color='#37474f', va='top'); yy -= 0.03
legend(pn, 'lower left', 5.6, ncol=1, bbox=(0, 0.0))
pdf.savefig(fig); fig.savefig('v2_s2.png', dpi=55); plt.close(fig)

# ===================================================== 3. DIMENSIONED LAYOUT (A0, 1:400)
fig, fr, cb, f = sheet(A0, *SHEETS[2][:4], 'A0'); x0, y0, x1, y1 = cb
N3 = 400
ax = map_in(fig, (x0, y0, x0 + 955, y1), A0, (282, -163), N3)
V = box(ax.get_xlim()[0], ax.get_ylim()[0], ax.get_xlim()[1], ax.get_ylim()[1])
draw_colony(ax, V, lw=0.6, labels=True, fs=6.2, dims=True, dfs=5.0)
road_dims(ax, V, fs=7.0, arrow_lw=0.8); median_dims(ax, V, fs=5.2); garden_dims(ax, V, fs=6.5); boundary_dims(ax, V, fs=5.8); misc_labels(ax, V, fs=6.2)
ax.text(150, -103, 'RIVERSIDE GARDEN – 15 m wide (open space, 12.9%)', color='#33691e', fontsize=9, rotation=52, weight='bold')
north(ax, 458, -266, 10, 14); scalebar(ax, 105, -284, 50, 10, 8)
pn = panel(fig, (x0 + 965, y0, x1, y1), A0)
yy = 0.995
for hd, lines in [('HOW TO READ', ['Blue figures inside each plot: side lengths in feet', '"arc": curved side, measured along the curve', 'Bold: plot number and area in sq ft',
                                   'Blue arrows across roads: right-of-way width (m)', 'White text on green: median width × length (m)', 'Green arrows: riverside garden width (m)',
                                   'Dark green outside the boundary: boundary lengths (m)', 'T: turning space 12 × 11 m']),
                  ('ROADS', [f"{r_['name']}: {r_['row']:.0f} m, about {(r_['len'] if r_['name'] != 'Access road' else ACC_LEN):.0f} m" for r_ in ROADS_]),
                  ('GARDEN MEDIANS', [f"{m_['road']}: 3.0 m × {m_['len']:.1f} m" for m_ in MED]),
                  ('OPEN SPACE, SERVICES', [f'Riverside garden 15 m × ~{GARD["len_inner"]:.0f} m, {rpark.area:,.0f} m²', f'Walkway {mrr_dims(walk)[1]:.2f} × {mrr_dims(walk)[0]:.1f} m (R10/R11)',
                                            f'Services plot {mrr_dims(svc)[0]:.1f} × {mrr_dims(svc)[1]:.1f} m', 'STP 10 × 8 · tank 7 × 7 · waste 5 × 4 m']),
                  ('SETBACKS (BVN Rule 56)', ['Front 3.6 m · rear 3 m · sides 3 m', 'River-front: 15 m garden + 3 m rear']),
                  ('ACCURACY', ['From the survey scan, ±0.5 m', 'Redraw on CAD and verify on site'])]:
    pn.text(0, yy, hd, fontsize=12, weight='bold', color=INK, va='top'); yy -= 0.022
    for l in lines: pn.text(0, yy, '•  ' + l, fontsize=8.8, color='#37474f', va='top'); yy -= 0.0165
    yy -= 0.012
yy = area_table(pn, 0, yy - 0.004, 7.6, 0.0155, W=1.0)
yy -= 0.012; pn.text(0, yy, f'SELLABLE {SALE * SQ:,.0f} sq ft · {100 * SALE / TOT:.1f}%', fontsize=12, weight='bold', color=ACC, va='top')
legend(pn, 'lower left', 8.6, ncol=1, bbox=(0, 0.0))
pdf.savefig(fig); fig.savefig('v2_s3.png', dpi=22); plt.close(fig)

# ===================================================== 4-7. QUARTER SHEETS (1:500)
Q = [(190, -105), (373, -105), (190, -224), (373, -224)]
N4 = 500
for qi, cen in enumerate(Q):
    fig, fr, cb, f = sheet(A3, *SHEETS[3 + qi][:4], 'A3'); x0, y0, x1, y1 = cb
    ax = map_in(fig, (x0, y0, x1, y1), A3, cen, N4)
    V = box(ax.get_xlim()[0], ax.get_ylim()[0], ax.get_xlim()[1], ax.get_ylim()[1])
    draw_colony(ax, V, lw=0.6, labels=True, fs=5.4, dims=True, dfs=4.6)
    road_dims(ax, V, fs=6.0); median_dims(ax, V, fs=4.6); garden_dims(ax, V, fs=5.6, every=(0.1, 0.3, 0.5, 0.7, 0.9)); boundary_dims(ax, V, fs=5.2); misc_labels(ax, V, fs=5.4)
    k = fig.add_axes(ax_mm(fig, (x1 - 46, y1 - 34, x1 - 2, y1 - 2), A3)); k.set_aspect('equal'); k.axis('off')
    k.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle='round,pad=0.02', fc='white', ec='#90a4ae', lw=0.5, transform=k.transAxes))
    k.fill(*C.exterior.xy, fc='#eeeeee', ec=COL['bnd'], lw=0.7); fill(k, row, fc='#bdbdbd', ec='none')
    vx = ax.get_xlim(); vy = ax.get_ylim(); k.add_patch(Rectangle((vx[0], vy[0]), vx[1] - vx[0], vy[1] - vy[0], fc='#ff8f00', alpha=0.25, ec='#e65100', lw=0.9))
    b_ = C.bounds; k.set_xlim(b_[0] - 8, b_[2] + 8); k.set_ylim(b_[1] - 8, b_[3] + 8)
    north(ax, vx[1] - 8, vy[0] + 8, 8, 7)
    pdf.savefig(fig)
    if qi in (0, 3): fig.savefig(f'v2_s{4 + qi}.png', dpi=55)
    plt.close(fig)

# ===================================================== 8-9. PLOT SCHEDULE (two sheets)
half = [ORDER[:31], ORDER[31:]]
cols = [(0.05, 'left'), (0.075, 'left'), (0.06, 'right'), (0.055, 'right'), (0.10, 'left'), (0.33, 'left'), (0.33, 'left')]
for si, part in enumerate(half):
    fig, fr, cb, f = sheet(A3, *SHEETS[7 + si][:4], 'A3'); x0, y0, x1, y1 = cb
    T_ = panel(fig, (x0, y0, x1, y1), A3)
    T_.text(0, 0.995, 'Sides run clockwise from the front (the main road side). Road sides carry the road name; "arc" = curved side measured along the curve.', fontsize=6.8, color='#37474f', va='top')
    rows = []
    for t in part:
        i_ = INFO[t]
        rows.append((t, 'River-front' if KIND[t] != 'Villa' else 'Villa', f"{i_['sqft']:,.0f}", f"{i_['sqm']:,.1f}", f"{i_['front']:.1f} m · {'+'.join(i_['roads'])}", side_txt(i_['sides'], 'ft'), side_txt(i_['sides'], 'm')))
    yy = table(T_, 0, 0.955, cols, rows, ('Plot', 'Type', 'sq ft', 'm²', 'Frontage', 'Sides in feet (clockwise from the front)', 'Sides in metres'), 6.6, 0.0288)
    if si == 1: T_.text(0, yy - 0.02, f'Total {len(PL)} plots · {SALE * SQ:,.0f} sq ft ({SALE:,.0f} m²) · {100 * SALE / TOT:.1f}% of the colony', fontsize=8, weight='bold', color=ACC, va='top')
    T_.text(1.0, 0.0, 'Measured from the calibrated survey scan (±0.5 m) – redraw on the CAD survey and verify on site before marking out.', fontsize=6, color='#b71c1c', ha='right', va='bottom')
    pdf.savefig(fig); fig.savefig(f'v2_s{8 + si}.png', dpi=55); plt.close(fig)

# ===================================================== 10. ROADS, MEDIANS, OPEN SPACE, SERVICES
fig, fr, cb, f = sheet(A3, *SHEETS[9][:4], 'A3'); x0, y0, x1, y1 = cb
L_ = panel(fig, (x0, y0, x0 + 236, y1), A3)
yy = h(L_, 0.995, 'ROADS', 9)
rc = [(0.13, 'left'), (0.40, 'left'), (0.08, 'right'), (0.13, 'right'), (0.12, 'right')]
rr = [(r_['name'], r_['desc'].split(' – ')[-1], f"{r_['row']:.0f} m", f"{(ACC_LEN if r_['name'] == 'Access road' else r_['len']):.0f}", f"{r_['area']:,.0f}") for r_ in ROADS_]
rr += [('Approach road', 'Main road → bridge → main entry (survey)', '15 m', f"{AP['len']:.0f}", f"{AP['poly'].area:,.0f}"),
       ('Entry splay', 'Approach road to access road at the main entry', '—', '—', f'{SPLAY.area:,.0f}'),
       ('Existing road', 'Jalkoti ← main road → Maheshwar (survey)', f"{AP['exist_w']:.1f} m", '—', '—')]
yy = table(L_, 0, yy - 0.004, rc, rr, ('Road', 'Runs', 'ROW', 'Length m', 'Area m²'), 6.0, 0.03)
L_.text(0, yy - 0.012, 'Lengths along the centre-line, junctions counted once. Farthest plot (V43) is 360 m from the colony gate (BVN 38: 12 m roads up to 400 m).', fontsize=5.8, color='#455a64', va='top')
yy -= 0.055; yy = h(L_, yy, 'ROAD CROSS-SECTIONS (metres)', 9)
for k_, (nm, key) in enumerate([('12 m plain road – RD, S1, S5, gate road', 'plain'), ('12 m garden street – S2, S3, S4', 'garden'), ('15 m access road – through the resort', 'access'), ('15 m approach road – survey section', 'approach')]):
    xx = 0.0 if k_ % 2 == 0 else 0.52; yk = yy - 0.03 - (k_ // 2) * 0.10
    xsection(L_, xx, yk, 0.36, SEC[key], nm, fs=5.8)
yy -= 0.235; yy = h(L_, yy, 'GARDEN MEDIANS', 9)
mc = [(0.20, 'left'), (0.12, 'right'), (0.14, 'right'), (0.14, 'right'), (0.26, 'left')]
mr = [(f"Median on {m_['road']}", '3.0', f"{m_['len']:.1f}", f"{m_['area']:,.0f}", 'stops 4 m short of junctions') for m_ in MED]
mr.append(('Total', '', f"{sum(m_['len'] for m_ in MED):.1f}", f"{sum(m_['area'] for m_ in MED):,.0f}", 'road land, not open space'))
yy = table(L_, 0, yy - 0.004, mc, mr, ('Median', 'Width m', 'Length m', 'Area m²', 'Note'), 6.0, 0.03)
R_ = panel(fig, (x0 + 244, y0, x1, y1), A3)
yy = h(R_, 0.995, 'OPEN SPACE, WALKWAY, SERVICES', 9)
L_w, W_w = mrr_dims(walk); L_s, W_s = mrr_dims(svc)
orows = [('Riverside garden', f'15 m wide · {GARD["len_inner"]:.0f} m along the plots', f'{rpark.area:,.0f}'),
         ('7 ft walkway', f'{W_w:.2f} × {L_w:.1f} m, R10/R11 to the garden', f'{walk.area:,.0f}'),
         ('Services plot', f'{L_s:.1f} × {W_s:.1f} m at the colony gate', f'{svc.area:,.0f}'),
         ('   STP', '10.0 × 8.0 m', '80'), ('   Tank + tubewell', '7.0 × 7.0 m', '49'), ('   Waste point', '5.0 × 4.0 m', '20'),
         ('Turning spaces', f'{len(DE)} × 12.0 × 11.0 m (in the roads)', f'{132 * len(DE)}'),
         ('Landscaped corners', f'{len(CORN)} pieces', f'{sum(q.area for q in CORN):,.0f}')]
yy = table(R_, 0, yy - 0.004, [(0.32, 'left'), (0.50, 'left'), (0.18, 'right')], orows, ('Item', 'Dimensions', 'Area m²'), 6.0, 0.036)
yy -= 0.04; yy = h(R_, yy, 'AREA STATEMENT – COLONY', 9)
yy = area_table(R_, 0, yy - 0.004, 6.0, 0.036, W=1.0)
yy -= 0.02; R_.text(0, yy, f'SELLABLE {SALE * SQ:,.0f} sq ft = {SALE / 4046.86:.2f} acres = {100 * SALE / TOT:.1f}%', fontsize=8.2, weight='bold', color=ACC, va='top')
R_.text(0, 0.0, 'Plot sides in feet (1 m = 3.281 ft); everything else in metres.\nMeasured from the survey scan (±0.5 m). Concept for discussion and T&CP pre-application only.', fontsize=5.8, color='#455a64', va='bottom')
pdf.savefig(fig); fig.savefig('v2_s10.png', dpi=55); plt.close(fig)
pdf.close(); print('saved', PDF)
