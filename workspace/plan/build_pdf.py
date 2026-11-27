"""Dimensioned PDF set for the Jalkoti colony:
 1 Overall map – from the Jalkoti–Maheshwar road to the colony (approach road, main entry, access road)
 2 Colony layout map (A2)
 3 Big dimensioned layout (A0) – every plot side, road, garden median, garden, walkway, services
 4-7 Dimension sheets (A3, 1:500) – the four quarters of the colony
 8 Plot dimension schedule
 9 Roads, garden medians, open spaces, services, area statement, notes"""
import sys, json, math, numpy as np, warnings, datetime; warnings.filterwarnings('ignore'); sys.path.insert(0, '.')
exec(open('dims.py').read().split("if __name__=='__main__':")[0])
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Patch, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D

OUT = '/home/user/Data-tool/site_plans/'
PDF = OUT + 'Jalkoti_Colony_Dimensioned_Layout.pdf'
MM = 1 / 25.4
A0L = (1189 * MM, 841 * MM); A2L = (594 * MM, 420 * MM); A3L = (420 * MM, 297 * MM); A3P = (297 * MM, 420 * MM)
TODAY = '12 Nov 2026'
INFO = {t: plot_info(t) for t, _, _ in plots}
ROADS_ = roads_info(); MED = medians_info(); GARD = garden_info(); CORN = corners_info()
AP = approach_info(); SPLAY = entry_splay(AP)
ORDER = sorted(INFO, key=lambda t: (t[0] != 'R', int(t[1:])))
COL = dict(river='#cfe8f7', resort='#f6ecd4', road='#d5d5d5', med='#2e7d32', garden='#cde8bf', rplot='#fff3d6',
           vplot='#ffffff', walk='#d7b98e', svc='#d7ccc8', corner='#e3f1d4', edge='#b71c1c', bnd='#1b5e20', dim='#0d47a1')
SALE = sum(p.area for p in PL.values()); TOT = C.area
ACC_LEN = max(mrr_dims(access))
nR = sum(1 for t in PL if KIND[t] != 'Villa'); nV = len(PL) - nR

def fill(ax, g, **kw):
    for p in getattr(g, 'geoms', [g]):
        if p.geom_type == 'Polygon' and not p.is_empty:
            ax.fill(*p.exterior.xy, **kw)
            for h in p.interiors: ax.fill(*h.xy, fc='white', ec=kw.get('ec', 'none'), lw=kw.get('lw', 0))
def map_axes(fig, rect, center, N):
    ax = fig.add_axes(rect); W, H = fig.get_size_inches()
    dw = rect[2] * W * 0.0254 * N; dh = rect[3] * H * 0.0254 * N; cx, cy = center
    ax.set_xlim(cx - dw / 2, cx + dw / 2); ax.set_ylim(cy - dh / 2, cy + dh / 2); ax.set_aspect('equal', adjustable='datalim'); ax.axis('off')
    return ax
def upright(deg):
    deg = (deg + 180) % 360 - 180
    if deg > 90: deg -= 180
    if deg <= -90: deg += 180
    return deg
def dir_at(line, f=0.5, h=0.04):
    a = np.array(line.interpolate(max(0, f - h), normalized=True).coords[0]); b = np.array(line.interpolate(min(1, f + h), normalized=True).coords[0])
    d = b - a; n = np.linalg.norm(d); return d / n if n > 0 else np.array([1.0, 0])
def scalebar(ax, x, y, L, step, fs, unit='m'):
    for i in range(int(L / step)):
        ax.add_patch(Rectangle((x + i * step, y), step, L / 60, fc='k' if i % 2 == 0 else 'white', ec='k', lw=0.6))
    for i in range(int(L / step) + 1): ax.text(x + i * step, y + L / 60 * 1.6, f'{int(i * step)}', ha='center', va='bottom', fontsize=fs)
    ax.text(x + L + step * 0.3, y, unit, va='bottom', fontsize=fs)
def north(ax, x, y, s, fs):
    ax.add_patch(FancyArrowPatch((x, y), (x, y + s), arrowstyle='-|>', mutation_scale=fs * 2.2, color='k', lw=1.5))
    ax.text(x, y + s * 1.12, 'N', ha='center', va='bottom', fontsize=fs, weight='bold')
def title_block(fig, title, sub, sheet, scale, rect=(0.012, 0.012, 0.976, 0.045), fs=9):
    t = fig.add_axes(rect); t.axis('off'); t.add_patch(Rectangle((0, 0), 1, 1, fc='white', ec='#37474f', lw=0.8, transform=t.transAxes))
    t.text(0.008, 0.62, 'JALKOTI COLONY – MAHESHWAR (Khargone, MP)', fontsize=fs + 1, weight='bold', va='center', transform=t.transAxes)
    t.text(0.008, 0.25, 'Survey Drg SU/10/01 · 23.325 acres · colony 11.80 ac + resort 11.63 ac', fontsize=fs - 1.5, va='center', transform=t.transAxes)
    t.text(0.45, 0.62, title, fontsize=fs + 1, weight='bold', va='center', transform=t.transAxes)
    t.text(0.45, 0.25, sub, fontsize=fs - 1.5, va='center', transform=t.transAxes)
    t.text(0.80, 0.62, f'Sheet {sheet}', fontsize=fs, weight='bold', va='center', transform=t.transAxes)
    t.text(0.80, 0.25, f'Scale {scale}  ·  {TODAY}', fontsize=fs - 1.5, va='center', transform=t.transAxes)
    t.text(0.992, 0.45, 'Concept – not an approved drawing', fontsize=fs - 1.5, color='#b71c1c', ha='right', va='center', transform=t.transAxes)

# ---------------------------------------------------------------- base layers
def draw_colony(ax, clip, lw=0.6, trees=False, labels=True, fs=5.0, dims=False, dfs=4.2, lab_area=True):
    V = clip
    fill(ax, R.intersection(V), fc=COL['river'], ec='#5aa9d6', lw=0.4)
    fill(ax, RS.intersection(V), fc=COL['resort'], ec='#a8781a', lw=0.6)
    fill(ax, C.intersection(V), fc='white', ec='none')
    for q in CORN:
        if q.intersects(V): fill(ax, q.intersection(V), fc=COL['corner'], ec='#9ccc65', lw=0.3)
    fill(ax, rpark.intersection(V), fc=COL['garden'], ec='#7cb342', lw=0.4)
    fill(ax, row.intersection(V), fc=COL['road'], ec='#8e8e8e', lw=0.4)
    fill(ax, access.intersection(V), fc=COL['road'], ec='#8e8e8e', lw=0.4)
    fill(ax, SPLAY.intersection(V), fc=COL['road'], ec='#8e8e8e', lw=0.4)
    fill(ax, gard.intersection(V), fc=COL['med'], ec='none')
    fill(ax, walk.intersection(V), fc=COL['walk'], ec='#8d6e63', lw=0.4)
    fill(ax, svc.intersection(V), fc=COL['svc'], ec='#5d4037', lw=0.6)
    for k, b in util.items():
        if b.intersects(V): fill(ax, b, fc='white', ec='#5d4037', lw=0.4)
    for d in DE:
        b = G(d['tbox'])
        if b.intersects(V): ax.fill(*b.exterior.xy, fc='none', ec='#e65100', lw=0.7, hatch='////', ls='--')
    if trees:
        for q in getattr(rpark, 'geoms', [rpark]):
            mid = q.intersection(R.buffer(7.5).exterior)
            for l in getattr(mid, 'geoms', [mid]):
                if l.geom_type != 'LineString': continue
                for s_ in np.arange(4, l.length, 9):
                    p_ = l.interpolate(s_)
                    if V.contains(p_): ax.add_patch(plt.Circle((p_.x, p_.y), 1.8, fc='#7cb342', ec='#558b2f', lw=0.3, alpha=0.8))
    for t, p in PL.items():
        if not p.intersects(V): continue
        fill(ax, p, fc=COL['rplot'] if KIND[t] != 'Villa' else COL['vplot'], ec=COL['edge'], lw=lw)
    bl = C.exterior.intersection(V)
    for l in getattr(bl, 'geoms', [bl]):
        if l.geom_type == 'LineString': ax.plot(*l.xy, color=COL['bnd'], lw=lw * 2.4, solid_capstyle='butt')
    if labels:
        for t, p in PL.items():
            c = p.representative_point() if not p.centroid.within(p) else p.centroid
            if not V.contains(c): continue
            txt = f'{t}\n{INFO[t]["sqft"]:,.0f} sq ft' if lab_area else t
            ax.text(c.x, c.y, txt, ha='center', va='center', fontsize=fs, weight='bold', color='#212121', linespacing=1.15)
    if dims:
        for t, p in PL.items():
            if not p.intersects(V): continue
            for s_ in INFO[t]['sides']:
                if s_['len'] < 2.5: continue
                line = s_['line']; m = line.interpolate(0.5, normalized=True)
                if not V.contains(m): continue
                d = dir_at(line); ang = math.degrees(math.atan2(d[1], d[0])); nin = np.array([d[1], -d[0]])   # clockwise ring: inside is to the right
                off = 1.15 if s_['len'] > 6 else 0.9
                q = np.array(m.coords[0]) + nin * off
                if not p.contains(Point(q)): q = np.array(m.coords[0]) - nin * off
                ax.text(q[0], q[1], f"{s_['len'] * FT:.1f}'" + (' arc' if s_['curved'] else ''), rotation=upright(ang), rotation_mode='anchor',
                        ha='center', va='center', fontsize=dfs, color=COL['dim'])

def road_dims(ax, V, fs=5.5, show_len=True, arrow_lw=0.6):
    """a width dimension across each named road + name, width and length"""
    done = set()
    for r in ROADS_:
        n = r['name']
        cand = sorted([(L, l) for nm, L, l in edges if nm == n], key=lambda x: -x[0])
        for L, l in cand[:1]:
            for f in ((0.5,) if n not in ('RD', 'S2', 'S3', 'S4') else ((0.25, 0.62) if n == 'RD' else (0.22,))):   # keep clear of the median labels
                m = l.interpolate(f, normalized=True)
                if not V.contains(m): continue
                d = dir_at(l, f); nrm = np.array([-d[1], d[0]])
                cut = LineString([tuple(np.array(m.coords[0]) - nrm * 12), tuple(np.array(m.coords[0]) + nrm * 12)]).intersection(unary_union([row, access]).buffer(0.05))
                segs = [g_ for g_ in getattr(cut, 'geoms', [cut]) if g_.geom_type == 'LineString' and g_.distance(m) < 0.5]
                if not segs: continue
                sg = segs[0]; a, b = np.array(sg.coords[0]), np.array(sg.coords[-1])
                ax.add_patch(FancyArrowPatch(tuple(a), tuple(b), arrowstyle='<|-|>', mutation_scale=5, color=COL['dim'], lw=arrow_lw, shrinkA=0, shrinkB=0))
                ang = upright(math.degrees(math.atan2(d[1], d[0])))
                ax.text(*(np.array(m.coords[0]) + d * 3.2), f'{sg.length:.1f} m', rotation=ang + 90 if abs(ang) < 45 else ang - 90, rotation_mode='anchor', ha='center', va='center', fontsize=fs * 0.85, color=COL['dim'], weight='bold')
                if n not in done:
                    lab = f"{n}  ·  {r['row']:.0f} m ROW" + (f"  ·  {r['len']:.0f} m long" if show_len else '')
                    ax.text(*(np.array(m.coords[0]) - d * 9), lab, rotation=ang, rotation_mode='anchor', ha='center', va='center', fontsize=fs, weight='bold', color='#263238',
                            bbox=dict(fc='white', ec='#90a4ae', lw=0.4, boxstyle='round,pad=0.18', alpha=0.9))
                    done.add(n)
def median_dims(ax, V, fs=4.2):
    for m_ in MED:
        q = m_['geom']
        if not q.intersects(V): continue
        mrr = list(q.minimum_rotated_rectangle.exterior.coords); e1 = np.array(mrr[1]) - np.array(mrr[0]); e2 = np.array(mrr[2]) - np.array(mrr[1])
        e = e1 if np.linalg.norm(e1) > np.linalg.norm(e2) else e2; ang = upright(math.degrees(math.atan2(e[1], e[0])))
        c = q.centroid
        if V.contains(c):
            ax.text(c.x, c.y, f"garden median 3.0 m × {m_['len']:.1f} m", rotation=ang, rotation_mode='anchor', ha='center', va='center', fontsize=fs, color='white', weight='bold')
def garden_dims(ax, V, fs=5.5, every=None):
    mid = rpark.intersection(R.buffer(7.5).exterior)
    lines = [l for l in getattr(mid, 'geoms', [mid]) if l.geom_type == 'LineString' and l.length > 20]
    for l in lines:
        for f in (every or (0.18, 0.5, 0.82)):
            m = l.interpolate(f, normalized=True)
            if not V.contains(m): continue
            d = dir_at(l, f); nrm = np.array([-d[1], d[0]])
            cut = LineString([tuple(np.array(m.coords[0]) - nrm * 9), tuple(np.array(m.coords[0]) + nrm * 9)]).intersection(rpark)
            segs = [g_ for g_ in getattr(cut, 'geoms', [cut]) if g_.geom_type == 'LineString' and g_.distance(m) < 0.5]
            if not segs: continue
            sg = segs[0]; a, b = np.array(sg.coords[0]), np.array(sg.coords[-1])
            ax.add_patch(FancyArrowPatch(tuple(a), tuple(b), arrowstyle='<|-|>', mutation_scale=5, color='#33691e', lw=0.6, shrinkA=0, shrinkB=0))
            ang = upright(math.degrees(math.atan2(d[1], d[0])))
            ax.text(*(np.array(m.coords[0]) + d * 4.5), f'{sg.length:.1f} m', rotation=ang + 90 if abs(ang) < 45 else ang - 90, rotation_mode='anchor', ha='center', va='center', fontsize=fs * 0.85, color='#33691e', weight='bold')
def boundary_dims(ax, V, fs=5.0):
    bs = sides(C, None, merge_deg=12.0, simp=0.3)
    for s_ in bs:
        if s_['len'] < 8: continue
        l = s_['line']; m = l.interpolate(0.5, normalized=True)
        if not V.contains(m): continue
        d = dir_at(l); nout = np.array([-d[1], d[0]])
        q = np.array(m.coords[0]) + nout * 2.6
        if C.contains(Point(q)): q = np.array(m.coords[0]) - nout * 2.6
        ax.text(q[0], q[1], f"{s_['len']:.1f} m" + (' (river edge, arc)' if s_['curved'] and s_['nb'] in ('Boundary',) and R.distance(m) < 2 else (' arc' if s_['curved'] else '')),
                rotation=upright(math.degrees(math.atan2(d[1], d[0]))), rotation_mode='anchor', ha='center', va='center', fontsize=fs, color=COL['bnd'], weight='bold')
def misc_labels(ax, V, fs=5.0):
    L_, W_ = mrr_dims(walk); c = walk.centroid
    if V.contains(c):
        mrr = list(walk.minimum_rotated_rectangle.exterior.coords); e1 = np.array(mrr[1]) - np.array(mrr[0]); e2 = np.array(mrr[2]) - np.array(mrr[1]); e = e1 if np.linalg.norm(e1) > np.linalg.norm(e2) else e2
        ax.annotate(f'7 ft walkway\n{W_:.2f} m × {L_:.1f} m', (c.x, c.y), xytext=(c.x - 16, c.y + 10), fontsize=fs, ha='center', color='#5d4037', arrowprops=dict(arrowstyle='-', lw=0.5, color='#5d4037'))
    c = svc.centroid
    if V.contains(c):
        L_, W_ = mrr_dims(svc)
        ax.annotate(f'SERVICES PLOT {L_:.1f} × {W_:.1f} m ({svc.area:,.0f} m²)\nSTP 10 × 8 m · tank + tubewell 7 × 7 m · waste point 5 × 4 m', (c.x, c.y), xytext=(c.x - 70, c.y - 14), fontsize=fs, ha='center', color='#4e342e', arrowprops=dict(arrowstyle='-', lw=0.5, color='#4e342e'))
        for k, b in util.items():
            lab = {'STP (sewage treatment)': 'STP', 'Overhead tank + tubewell': 'OHT', 'Waste point': 'W'}[k]
            ax.text(b.centroid.x, b.centroid.y, lab, ha='center', va='center', fontsize=fs * 0.8, weight='bold')
    for d in DE:
        b = G(d['tbox'])
        if V.contains(b.centroid): ax.text(b.centroid.x, b.centroid.y, 'T\n12 × 11 m', ha='center', va='center', fontsize=fs * 0.8, color='#e65100', weight='bold')
    if V.contains(GATE): ax.annotate('COLONY GATE', (331, -262), xytext=(352, -275), fontsize=fs * 1.1, weight='bold', arrowprops=dict(arrowstyle='->', lw=0.7))

def legend(ax_or_fig, loc, fs, ncol=1, fig=None, bbox=None):
    H = [Patch(fc=COL['rplot'], ec=COL['edge'], label='River-front plot'), Patch(fc='white', ec=COL['edge'], label='Villa plot'),
         Patch(fc=COL['road'], ec='#8e8e8e', label='Road (right of way)'), Patch(fc=COL['med'], label='Garden median (road land)'),
         Patch(fc=COL['garden'], ec='#7cb342', label='Riverside garden (open space)'), Patch(fc=COL['corner'], ec='#9ccc65', label='Landscaped corner'),
         Patch(fc=COL['walk'], ec='#8d6e63', label='7 ft walkway'), Patch(fc=COL['svc'], ec='#5d4037', label='Services plot'),
         Patch(fc='none', ec='#e65100', hatch='////', label='T = turning space 12 × 11 m'), Patch(fc=COL['resort'], ec='#a8781a', label='Resort'),
         Line2D([0], [0], color=COL['bnd'], lw=2, label='Colony boundary')]
    return ax_or_fig.legend(handles=H, loc=loc, fontsize=fs, frameon=False, ncol=ncol, bbox_to_anchor=bbox)

pdf = PdfPages(PDF)
md = pdf.infodict(); md['Title'] = 'Jalkoti colony – dimensioned layout'; md['Subject'] = 'Overall map, colony layout, dimensioned layout and schedules'

# ================================================================ 1. OVERALL MAP (A3 portrait, 1:3000)
fig = plt.figure(figsize=A3P)
N1 = 3000
ax = map_axes(fig, (0.03, 0.075, 0.94, 0.80), (360, -490), N1)
V = box(*ax.get_xlim()[:1], ax.get_ylim()[0], ax.get_xlim()[1], ax.get_ylim()[1])
fill(ax, R.intersection(V), fc=COL['river'], ec='#5aa9d6', lw=0.5)
riv_lines = wkt.loads(A['river']).intersection(box(300, -960, 700, -540))
for l in getattr(riv_lines, 'geoms', [riv_lines]):
    if l.geom_type == 'LineString' and l.length > 3: ax.plot(*l.xy, color='#5aa9d6', lw=0.5)
fill(ax, RS, fc=COL['resort'], ec='#a8781a', lw=0.8)
fill(ax, C, fc='white', ec='none'); fill(ax, rpark, fc=COL['garden'], ec='none')
fill(ax, row, fc='#9e9e9e', ec='none'); fill(ax, gard, fc=COL['med'], ec='none')
for t, p in PL.items(): fill(ax, p, fc=COL['rplot'] if KIND[t] != 'Villa' else 'white', ec='#c62828', lw=0.25)
fill(ax, svc, fc=COL['svc'], ec='#5d4037', lw=0.4)
ax.plot(*C.exterior.xy, color=COL['bnd'], lw=1.6)
fill(ax, AP['exist_poly'], fc='#757575', ec='#424242', lw=0.6)
fill(ax, AP['poly'], fc='#9e9e9e', ec='#616161', lw=0.5)
fill(ax, SPLAY, fc='#9e9e9e', ec='none'); fill(ax, access, fc='#9e9e9e', ec='#616161', lw=0.5)
# avenue trees along the approach road edges
for side in ('left', 'right'):
    try: ed = AP['cl'].parallel_offset(8.6, side, join_style=2)
    except Exception: ed = None
    for l in getattr(ed, 'geoms', [ed]) if ed is not None else []:
        for s_ in np.arange(6, l.length, 14):
            p_ = l.interpolate(s_); ax.add_patch(plt.Circle((p_.x, p_.y), 2.6, fc='#7cb342', ec='#33691e', lw=0.3))
for l in getattr(AP['bridge'], 'geoms', [AP['bridge']]):
    if l.geom_type == 'LineString' and l.length > 2: ax.plot(*l.xy, color='#d32f2f', lw=1.4)
if AP['mandir'] is not None and not AP['mandir'].is_empty:
    mb = AP['mandir'].bounds; ax.add_patch(Rectangle((mb[0], mb[1]), mb[2] - mb[0], mb[3] - mb[1], fc='#ffe0b2', ec='#e65100', lw=0.6))
    ax.text(mb[2] + 4, mb[3], 'Mandir', fontsize=6, va='center')
PARC = pickle.load(open('../site/geo.pkl', 'rb'))['P']
for pp in PARC: ax.plot(*pp.exterior.xy, color='#33691e', lw=0.6, ls=(0, (5, 2)))
# labels
ax.text(478, -150, 'COLONY', fontsize=12, weight='bold', color=COL['bnd'], ha='left')
ax.text(478, -164, f'{TOT / 4046.86:.2f} acres · {len(PL)} plots\nall roads 12 m', fontsize=8, color=COL['bnd'], ha='left', va='top')
ax.text(240, -400, f'RESORT\n{RS.area / 4046.86:.2f} acres', fontsize=11, weight='bold', color='#7a5410', ha='center', va='center')
ax.text(368, -690, 'STREAM', fontsize=8, color='#1f5f8b', rotation=-35, ha='center')
c_ = AP['cl']; m_ = c_.interpolate(0.55, normalized=True); d_ = dir_at(c_, 0.55)
ax.text(m_.x + 26, m_.y, f"APPROACH ROAD\n15 m right of way\n(2 + 1 + 9 m carriageway + 1 + 2)\n≈ {AP['len']:.0f} m long, tree-lined",
        fontsize=7.2, weight='bold', color='#263238', va='center', bbox=dict(fc='white', ec='#90a4ae', lw=0.5, boxstyle='round,pad=0.3'))
bc = AP['bridge'].centroid if not AP['bridge'].is_empty else Point(390, -600)
ax.annotate('Bridge over the stream', (bc.x, bc.y), xytext=(bc.x - 120, bc.y - 25), fontsize=7, color='#c62828', weight='bold', arrowprops=dict(arrowstyle='->', lw=0.7, color='#c62828'))
ex = AP['exist_poly'].bounds
ax.text(ex[0] - 3, (ex[1] + ex[3]) / 2, '← to Jalkoti', fontsize=7, va='center', ha='right')
ax.text(ex[2] + 3, (ex[1] + ex[3]) / 2, 'to Maheshwar →', fontsize=7, va='center', ha='left')
ax.text((ex[0] + ex[2]) / 2 - 10, (ex[1] + ex[3]) / 2 - 24, f"EXISTING ROAD (main road) · ≈ {AP['exist_w']:.1f} m wide as surveyed", fontsize=7.4, weight='bold', ha='center', va='top')
ae = Point(AP['cl'].coords[0])
ax.annotate('MAIN ENTRY', (ae.x + 6, ae.y + 4), xytext=(ae.x - 95, ae.y - 30), fontsize=8, weight='bold', arrowprops=dict(arrowstyle='->', lw=0.9))
ax.text(352, -372, f'ACCESS ROAD\n15 m · {ACC_LEN:.0f} m\nthrough the resort', fontsize=7, weight='bold', color='#263238', va='center',
        bbox=dict(fc='white', ec='#90a4ae', lw=0.5, boxstyle='round,pad=0.25'))
ax.annotate('COLONY GATE', (331, -262), xytext=(380, -250), fontsize=8, weight='bold', arrowprops=dict(arrowstyle='->', lw=0.9))
route = round((AP['len'] + Point(AP['cl'].coords[0]).distance(Point(335.5, -484)) + ACC_LEN) / 5) * 5
print('approach starts at', [round(v, 1) for v in AP['cl'].coords[0]], '| route to the gate', route)
north(ax, 600, -120, 40, 10); scalebar(ax, 470, -50, 200, 50, 6.5)
fig.text(0.03, 0.965, 'SHEET 1 – OVERALL MAP: FROM THE MAIN ROAD TO THE COLONY', fontsize=13, weight='bold')
fig.text(0.03, 0.947, f"Existing Jalkoti–Maheshwar road → {AP['len']:.0f} m approach road (15 m, over the bridge) → main entry → {ACC_LEN:.0f} m access road through the resort (15 m) → colony gate.", fontsize=7.6)
fig.text(0.03, 0.933, f'Total from the main road to the colony gate ≈ {route:.0f} m. All colony roads are 12 m; the farthest plot (V43) is 360 m inside the gate.', fontsize=7.6)
fig.text(0.03, 0.919, 'The approach road and the access road should both be dedicated as public roads (gift deed / record) before the colony application.', fontsize=7.6, color='#b71c1c')
fig.text(0.03, 0.904, 'Approach road, bridge, existing road and mandir traced from the survey (Drg SU/10/01, 1:1000); widths read off its road lines and road section.', fontsize=6.8, color='#455a64')
title_block(fig, 'Overall map – main road to colony', 'Approach road, main entry, access road and colony', '1 of 9', f'1:{N1} on A3', rect=(0.02, 0.012, 0.96, 0.05), fs=8)
pdf.savefig(fig); fig.savefig('/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/plan/pg1.png', dpi=70); plt.close(fig)

# ================================================================ helpers for the panels
def table(ax, x0, y0, cols, rows, header, fs, rh, shade=True, bold_first=True, head_fc='#eceff1'):
    """cols: list of (width, align); rows: list of tuples of strings. Axes coords."""
    x = x0; W = sum(w for w, _ in cols)
    ax.add_patch(Rectangle((x0, y0 - rh), W, rh, fc=head_fc, ec='#90a4ae', lw=0.4, transform=ax.transAxes))
    for (w, al), h in zip(cols, header):
        ax.text(x + (0.004 if al == 'left' else w - 0.004 if al == 'right' else w / 2), y0 - rh / 2, h, ha=al, va='center', fontsize=fs, weight='bold', transform=ax.transAxes); x += w
    y = y0 - rh
    for i, r in enumerate(rows):
        if shade and i % 2 == 1: ax.add_patch(Rectangle((x0, y - rh), W, rh, fc='#f7f9fa', ec='none', transform=ax.transAxes))
        x = x0
        for j, ((w, al), v) in enumerate(zip(cols, r)):
            ax.text(x + (0.004 if al == 'left' else w - 0.004 if al == 'right' else w / 2), y - rh / 2, v, ha=al, va='center', fontsize=fs,
                    weight='bold' if (bold_first and j == 0) else 'normal', transform=ax.transAxes); x += w
        y -= rh
    ax.add_patch(Rectangle((x0, y), W, y0 - y, fc='none', ec='#90a4ae', lw=0.5, transform=ax.transAxes))
    return y
AREA_ROWS = [('River-front plots', f'{nR}', sum(p.area for t, p in PL.items() if KIND[t] != 'Villa')),
             ('Villa plots', f'{nV}', sum(p.area for t, p in PL.items() if KIND[t] == 'Villa')),
             ('Roads – carriageway and verges', '', roads.intersection(C).area), ('Garden medians (road land)', '', gard.area),
             ('Riverside garden (open space)', '', rpark.area), ('Services plot', '', svc.area),
             ('Landscaped corners', '', sum(q.area for q in CORN)), ('7 ft walkway', '', walk.area)]
def area_table(ax, x0, y0, fs, rh, W=0.96):
    cols = [(W * 0.46, 'left'), (W * 0.08, 'center'), (W * 0.18, 'right'), (W * 0.14, 'right'), (W * 0.14, 'right')]
    rows = [(n, c, f'{a * SQ:,.0f}', f'{a:,.0f}', f'{100 * a / TOT:.1f}') for n, c, a in AREA_ROWS]
    rows.append(('Total colony', f'{len(PL)}', f'{TOT * SQ:,.0f}', f'{TOT:,.0f}', '100.0'))
    return table(ax, x0, y0, cols, rows, ('Use', 'No.', 'sq ft', 'm²', '%'), fs, rh)

# ================================================================ 2. COLONY LAYOUT (A2 landscape, 1:1000)
fig = plt.figure(figsize=A2L); N2 = 1000
ax = map_axes(fig, (0.012, 0.075, 0.68, 0.90), (282, -163), N2)
V = box(ax.get_xlim()[0], ax.get_ylim()[0], ax.get_xlim()[1], ax.get_ylim()[1])
draw_colony(ax, V, lw=0.5, trees=True, labels=True, fs=4.4)
road_dims(ax, V, fs=5.2); misc_labels(ax, V, fs=5.0)
ax.text(150, -105, 'RIVERSIDE GARDEN – 15 m wide', color='#33691e', fontsize=7, rotation=52, weight='bold')
ax.text(120, -60, 'STREAM', color='#1f5f8b', fontsize=8, weight='bold')
north(ax, 455, -265, 14, 9); scalebar(ax, 110, -282, 100, 25, 6)
P_ = fig.add_axes((0.70, 0.075, 0.29, 0.90)); P_.axis('off')
P_.text(0, 0.985, 'COLONY LAYOUT', fontsize=15, weight='bold', transform=P_.transAxes)
P_.text(0, 0.962, f'{len(PL)} plots · all roads 12 m · S1 joined to S2 by the S5 link road', fontsize=8.5, transform=P_.transAxes)
y = 0.93; P_.text(0, y, 'AREA STATEMENT', fontsize=10, weight='bold', transform=P_.transAxes)
y = area_table(P_, 0, y - 0.008, 7.2, 0.0205)
y -= 0.022; P_.text(0, y, f'SELLABLE {SALE * SQ:,.0f} sq ft = {SALE / 4046.86:.2f} acres = {100 * SALE / TOT:.1f}% of the colony', fontsize=9, weight='bold', color='#1b5e20', transform=P_.transAxes)
y -= 0.02; P_.text(0, y, f'Open space: riverside garden {100 * rpark.area / TOT:.1f}% (BVN minimum 10%)', fontsize=8, transform=P_.transAxes)
pa = [INFO[t]['sqft'] for t in PL if KIND[t] != 'Villa']; va = [INFO[t]['sqft'] for t in PL if KIND[t] == 'Villa']
y -= 0.035; P_.text(0, y, 'PLOTS', fontsize=10, weight='bold', transform=P_.transAxes)
for s_ in [f'{nR} river-front plots {min(pa):,.0f}–{max(pa):,.0f} sq ft (average {np.mean(pa):,.0f}), backing onto the riverside garden',
           f'{nV} villa plots {min(va):,.0f}–{max(va):,.0f} sq ft (average {np.mean(va):,.0f}); typical 45 × 90 ft',
           'Every plot fronts a 12 m road; every frontage is above 12 m (BVN Rule 53)', 'Full side dimensions: Sheets 3–7 and the schedule on Sheet 8']:
    y -= 0.019; P_.text(0, y, '• ' + s_, fontsize=7.4, transform=P_.transAxes)
y -= 0.035; P_.text(0, y, 'ROADS', fontsize=10, weight='bold', transform=P_.transAxes)
for r_ in ROADS_:
    y -= 0.019; P_.text(0, y, f"• {r_['name']}: {r_['row']:.0f} m, about {r_['len'] if r_['name'] != 'Access road' else ACC_LEN:.0f} m – {r_['desc'].split(' – ')[-1]}", fontsize=7.2, transform=P_.transAxes)
y -= 0.019; P_.text(0, y, f"• Garden medians 3.0 m wide on S2, S3, S4 ({', '.join(f'{m_['len']:.0f} m' for m_ in MED)})", fontsize=7.2, transform=P_.transAxes)
y -= 0.019; P_.text(0, y, '• Dead ends: S2 stub (V38) 42 m and RD south end 66 m – straight, with a 12 × 11 m turning space', fontsize=7.2, transform=P_.transAxes)
y -= 0.035; P_.text(0, y, 'SERVICES AND OPEN SPACE', fontsize=10, weight='bold', transform=P_.transAxes)
for s_ in [f'Riverside garden 15 m wide, about {GARD["len_inner"]:.0f} m along the plots, {rpark.area:,.0f} m²',
           f'7 ft walkway from RD between R10 and R11: {mrr_dims(walk)[1]:.2f} × {mrr_dims(walk)[0]:.1f} m',
           f'Services plot at the gate {mrr_dims(svc)[0]:.1f} × {mrr_dims(svc)[1]:.1f} m ({svc.area:,.0f} m²): STP, overhead tank + tubewell, waste point']:
    y -= 0.019; P_.text(0, y, '• ' + s_, fontsize=7.2, transform=P_.transAxes)
legend(P_, 'lower left', 7.2, ncol=2, bbox=(0, 0.0))
title_block(fig, 'Colony layout', 'Plot numbers and areas, roads and open spaces', '2 of 9', f'1:{N2} on A2', rect=(0.012, 0.012, 0.976, 0.05), fs=9)
pdf.savefig(fig); fig.savefig('pg2.png', dpi=50); plt.close(fig)

# ================================================================ 3. BIG DIMENSIONED LAYOUT (A0 landscape, 1:400)
fig = plt.figure(figsize=A0L); N3 = 400
ax = map_axes(fig, (0.008, 0.06, 0.80, 0.93), (282, -162), N3)
V = box(ax.get_xlim()[0], ax.get_ylim()[0], ax.get_xlim()[1], ax.get_ylim()[1])
draw_colony(ax, V, lw=0.6, labels=True, fs=6.2, dims=True, dfs=5.0)
road_dims(ax, V, fs=7.0, arrow_lw=0.8); median_dims(ax, V, fs=5.2); garden_dims(ax, V, fs=6.5); boundary_dims(ax, V, fs=5.8); misc_labels(ax, V, fs=6.2)
ax.text(150, -103, 'RIVERSIDE GARDEN – 15 m wide (open space, 12.9%)', color='#33691e', fontsize=9, rotation=52, weight='bold')
north(ax, 458, -268, 10, 14); scalebar(ax, 105, -282, 50, 10, 8)
P_ = fig.add_axes((0.815, 0.06, 0.18, 0.93)); P_.axis('off')
P_.text(0, 0.985, 'DIMENSIONED LAYOUT', fontsize=22, weight='bold', transform=P_.transAxes)
P_.text(0, 0.968, f'Every plot side, road, garden median and open space · {len(PL)} plots', fontsize=11, transform=P_.transAxes)
y = 0.94
for h, lines in [('HOW TO READ', ['Blue figures inside each plot: side lengths in feet (1 m = 3.281 ft)', '"arc" = curved side, length measured along the curve',
                                  'Bold figure: plot number and area in sq ft', 'Road arrows: right-of-way width across the road (m)',
                                  'White text on green: garden median width × length (m)', 'Green arrows across the riverside garden: its width (m)',
                                  'Dark-green figures outside the boundary: colony boundary lengths (m)', 'T = turning space 12 × 11 m at a dead end']),
                 ('ROADS (all 12 m inside the colony)', [f"{r_['name']}: {r_['row']:.0f} m ROW, about {(r_['len'] if r_['name'] != 'Access road' else ACC_LEN):.0f} m long" for r_ in ROADS_] +
                  ['Plain 12 m road: 2.25 m verge + 7.5 m carriageway + 2.25 m verge', 'Garden street 12 m: 1.0 m footpath + 3.5 m lane + 3.0 m median + 3.5 m lane + 1.0 m footpath']),
                 ('GARDEN MEDIANS', [f"On {m_['road']}: 3.0 m × {m_['len']:.1f} m ({m_['area']:,.0f} m²)" for m_ in MED]),
                 ('OPEN SPACE AND SERVICES', [f'Riverside garden: 15 m wide, {GARD["len_inner"]:.0f} m along the plots, {rpark.area:,.0f} m²',
                                              f'Walkway: {mrr_dims(walk)[1]:.2f} m (7 ft) × {mrr_dims(walk)[0]:.1f} m, between R10 and R11',
                                              f'Services plot: {mrr_dims(svc)[0]:.1f} × {mrr_dims(svc)[1]:.1f} m ({svc.area:,.0f} m²)',
                                              'STP 10 × 8 m · tank + tubewell 7 × 7 m · waste point 5 × 4 m',
                                              f'Landscaped corners: {len(CORN)} pieces, {sum(q.area for q in CORN):,.0f} m² in all']),
                 ('SETBACKS (BVN 2012, Rule 56)', ['Front 3.6 m on a 12 m road · rear 3.0 m · sides 3.0 m each (detached)', 'River-front plots: 15 m from the stream edge + 3 m rear setback']),
                 ('ACCURACY', ['Measured from the survey scan (Drg SU/10/01) calibrated to its surveyed areas', 'Expect ±0.5 m. Redraw on the CAD survey and', 'verify on site before marking out or selling'])]:
    P_.text(0, y, h, fontsize=11.5, weight='bold', transform=P_.transAxes); y -= 0.016
    for l in lines: P_.text(0, y, '• ' + l, fontsize=8.6, transform=P_.transAxes); y -= 0.0135
    y -= 0.012
y -= 0.005; P_.text(0, y, 'AREA STATEMENT', fontsize=11.5, weight='bold', transform=P_.transAxes)
y = area_table(P_, 0, y - 0.006, 8.4, 0.0125, W=0.98)
y -= 0.016; P_.text(0, y, f'SELLABLE {SALE * SQ:,.0f} sq ft · {100 * SALE / TOT:.1f}%', fontsize=12, weight='bold', color='#1b5e20', transform=P_.transAxes)
legend(P_, 'lower left', 8.6, ncol=1, bbox=(0, 0.0))
title_block(fig, 'Dimensioned layout – big map', 'All plot sides in feet; roads, medians, garden and boundary in metres', '3 of 9', f'1:{N3} on A0', rect=(0.008, 0.008, 0.984, 0.04), fs=13)
pdf.savefig(fig); fig.savefig('pg3.png', dpi=24); plt.close(fig)

# ================================================================ 4-7. QUARTER SHEETS (A3 landscape, 1:500)
Q = [('North-west', (190, -105)), ('North-east', (373, -105)), ('South-west', (190, -224)), ('South-east', (373, -224))]
N4 = 500
for qi, (qn, cen) in enumerate(Q):
    fig = plt.figure(figsize=A3L)
    ax = map_axes(fig, (0.008, 0.075, 0.984, 0.915), cen, N4)
    V = box(ax.get_xlim()[0], ax.get_ylim()[0], ax.get_xlim()[1], ax.get_ylim()[1])
    draw_colony(ax, V, lw=0.6, labels=True, fs=5.4, dims=True, dfs=4.6)
    road_dims(ax, V, fs=6.0); median_dims(ax, V, fs=4.6); garden_dims(ax, V, fs=5.6, every=(0.1, 0.3, 0.5, 0.7, 0.9)); boundary_dims(ax, V, fs=5.2); misc_labels(ax, V, fs=5.4)
    # key map
    k = fig.add_axes((0.86, 0.80, 0.13, 0.18)); k.set_aspect('equal'); k.axis('off')
    k.fill(*C.exterior.xy, fc='#eeeeee', ec=COL['bnd'], lw=0.8); fill(k, row, fc='#bdbdbd', ec='none')
    vx = ax.get_xlim(); vy = ax.get_ylim(); k.add_patch(Rectangle((vx[0], vy[0]), vx[1] - vx[0], vy[1] - vy[0], fc='#ff8f00', alpha=0.25, ec='#e65100', lw=1))
    b_ = C.bounds; k.set_xlim(b_[0] - 5, b_[2] + 5); k.set_ylim(b_[1] - 5, b_[3] + 5); k.set_title(f'{qn} quarter', fontsize=7)
    fig.text(0.012, 0.975, f'SHEET {4 + qi} – DIMENSIONS, {qn.upper()} QUARTER', fontsize=11, weight='bold')
    fig.text(0.012, 0.958, "Plot sides in feet (blue, inside each plot) · road widths, garden medians, garden and boundary in metres · areas in sq ft", fontsize=7)
    ax2 = fig.add_axes((0.012, 0.08, 0.3, 0.05)); ax2.axis('off'); ax2.set_xlim(0, 1); ax2.set_ylim(0, 1)
    title_block(fig, f'Dimension sheet – {qn.lower()} quarter', 'Plot sides (ft), roads, medians, garden and boundary (m)', f'{4 + qi} of 9', f'1:{N4} on A3', rect=(0.008, 0.01, 0.984, 0.055), fs=8)
    pdf.savefig(fig)
    if qi == 3: fig.savefig('pg7.png', dpi=60)
    if qi == 0: fig.savefig('pg4.png', dpi=60)
    plt.close(fig)

# ================================================================ 8. PLOT DIMENSION SCHEDULE (A3 portrait)
def side_txt(sd, unit):
    out = []
    for s_ in sd:
        v = s_['len'] * FT if unit == 'ft' else s_['len']
        t = f'{v:.1f}' if unit == 'ft' else f'{v:.2f}'
        if s_['road']: t += f" {s_['nb']}"
        if s_['curved']: t += ' arc'
        out.append(t)
    return ' · '.join(out)
fig = plt.figure(figsize=A3P)
T_ = fig.add_axes((0.03, 0.07, 0.94, 0.90)); T_.axis('off')
T_.text(0, 0.995, 'SHEET 8 – PLOT DIMENSION SCHEDULE', fontsize=13, weight='bold', transform=T_.transAxes, va='top')
T_.text(0, 0.977, 'Sides run clockwise from the main road side (the front). Road sides carry the road name; "arc" = curved side measured along the curve.', fontsize=6.6, transform=T_.transAxes, va='top')
T_.text(0, 0.966, 'Areas and lengths are measured from the calibrated survey scan (±0.5 m) – redraw on the CAD survey and verify on site before marking out.', fontsize=6.6, transform=T_.transAxes, va='top', color='#b71c1c')
cols = [(0.045, 'left'), (0.075, 'left'), (0.06, 'right'), (0.055, 'right'), (0.095, 'left'), (0.335, 'left'), (0.335, 'left')]
rows = []
for t in ORDER:
    i_ = INFO[t]
    fr = f"{i_['front']:.1f} m · {'+'.join(i_['roads'])}"
    rows.append((t, 'River-front' if KIND[t] != 'Villa' else 'Villa', f"{i_['sqft']:,.0f}", f"{i_['sqm']:,.1f}", fr, side_txt(i_['sides'], 'ft'), side_txt(i_['sides'], 'm')))
y = table(T_, 0, 0.955, cols, rows, ('Plot', 'Type', 'sq ft', 'm²', 'Road frontage', 'Sides in feet (clockwise from the front)', 'Sides in metres'), 5.2, 0.0142)
T_.text(0, y - 0.012, f'Total {len(PL)} plots · {SALE * SQ:,.0f} sq ft ({SALE:,.0f} m²) · {100 * SALE / TOT:.1f}% of the colony', fontsize=7.5, weight='bold', transform=T_.transAxes, va='top')
title_block(fig, 'Plot dimension schedule', 'Area, frontage and every side of all 62 plots', '8 of 9', 'n/a', rect=(0.02, 0.012, 0.96, 0.045), fs=8)
pdf.savefig(fig); fig.savefig('pg8.png', dpi=70); plt.close(fig)

# ================================================================ 9. ROADS, MEDIANS, OPEN SPACE, SERVICES, AREA STATEMENT
fig = plt.figure(figsize=A3P)
T_ = fig.add_axes((0.03, 0.07, 0.94, 0.90)); T_.axis('off')
T_.text(0, 0.995, 'SHEET 9 – ROADS, GARDEN MEDIANS, OPEN SPACE AND SERVICES', fontsize=13, weight='bold', transform=T_.transAxes, va='top')
y = 0.965; T_.text(0, y, 'ROADS', fontsize=10, weight='bold', transform=T_.transAxes)
cols = [(0.11, 'left'), (0.36, 'left'), (0.07, 'right'), (0.30, 'left'), (0.08, 'right'), (0.08, 'right')]
rr = []
for r_ in ROADS_:
    L_ = ACC_LEN if r_['name'] == 'Access road' else r_['len']
    rr.append((r_['name'], r_['desc'].split(' – ')[-1], f"{r_['row']:.0f} m", r_['section'], f'{L_:.0f}', f"{r_['area']:,.0f}"))
rr.append(('Approach road', 'Existing main road → bridge → main entry (outside the site, as surveyed)', '15 m', '2 m + 1 m + 9 m carriageway + 1 m + 2 m (survey)', f"{AP['len']:.0f}", f"{AP['poly'].area:,.0f}"))
rr.append(('Entry splay', 'Joins the approach road to the access road at the main entry', '—', 'paved', '—', f'{SPLAY.area:,.0f}'))
rr.append(('Existing road', 'Jalkoti ← main road → Maheshwar (survey)', f"{AP['exist_w']:.1f} m", 'existing carriageway', '—', '—'))
y = table(T_, 0, y - 0.006, cols, rr, ('Road', 'Runs', 'ROW', 'Cross-section', 'Length m', 'Area m²'), 5.6, 0.0155)
T_.text(0, y - 0.01, 'Road lengths are along the centre-line; junction areas are counted once. Every colony road is 12 m; the farthest plot (V43) is 360 m from the colony gate (BVN 38: 12 m roads up to 400 m).', fontsize=6.2, transform=T_.transAxes, va='top')
# cross-sections
y -= 0.045; T_.text(0, y, 'ROAD CROSS-SECTIONS (metres)', fontsize=10, weight='bold', transform=T_.transAxes)
secs = [('12 m plain road (RD, S1, S5, gate road)', [(2.25, 'verge', '#a5d6a7'), (7.5, 'carriageway', '#9e9e9e'), (2.25, 'verge', '#a5d6a7')]),
        ('12 m garden street (S2, S3, S4)', [(1.0, 'path', '#cfd8dc'), (3.5, 'lane', '#9e9e9e'), (3.0, 'median', '#2e7d32'), (3.5, 'lane', '#9e9e9e'), (1.0, 'path', '#cfd8dc')]),
        ('15 m access road (through the resort)', [(3.0, 'verge', '#a5d6a7'), (9.0, 'carriageway', '#9e9e9e'), (3.0, 'verge', '#a5d6a7')]),
        ('15 m approach road (survey section)', [(2.0, '', '#a5d6a7'), (1.0, '', '#cfd8dc'), (9.0, 'carriageway', '#9e9e9e'), (1.0, '', '#cfd8dc'), (2.0, '', '#a5d6a7')])]
y -= 0.012
for k_, (nm, parts) in enumerate(secs):
    x0 = 0.0 if k_ % 2 == 0 else 0.5; yy = y - (k_ // 2) * 0.062
    T_.text(x0, yy, nm, fontsize=6.8, weight='bold', transform=T_.transAxes, va='top')
    tot = sum(p[0] for p in parts); sc = 0.42 / tot; xx = x0
    for w, lab, c in parts:
        T_.add_patch(Rectangle((xx, yy - 0.032), w * sc, 0.016, fc=c, ec='#455a64', lw=0.4, transform=T_.transAxes))
        T_.text(xx + w * sc / 2, yy - 0.024, f'{w:g}', ha='center', va='center', fontsize=6, color='white' if c in ('#9e9e9e', '#2e7d32') else 'k', weight='bold', transform=T_.transAxes)
        if lab: T_.text(xx + w * sc / 2, yy - 0.037, lab, ha='center', va='top', fontsize=5.2, transform=T_.transAxes)
        xx += w * sc
    T_.text(x0 + 0.43, yy - 0.024, f'= {tot:g} m', va='center', fontsize=6.6, weight='bold', transform=T_.transAxes)
y -= 0.135
T_.text(0, y, 'GARDEN MEDIANS (garden in the middle of the road)', fontsize=10, weight='bold', transform=T_.transAxes)
cols = [(0.14, 'left'), (0.12, 'right'), (0.12, 'right'), (0.12, 'right'), (0.46, 'left')]
mr = [(f"Median on {m_['road']}", '3.0', f"{m_['len']:.1f}", f"{m_['area']:,.0f}", 'Stops 4 m short of junctions and before turning spaces') for m_ in MED]
mr.append(('Total', '', f"{sum(m_['len'] for m_ in MED):.1f}", f"{sum(m_['area'] for m_ in MED):,.0f}", 'Counted as road land, not open space'))
y = table(T_, 0, y - 0.006, cols, mr, ('Median', 'Width m', 'Length m', 'Area m²', 'Note'), 5.8, 0.0155)
y -= 0.025; T_.text(0, y, 'OPEN SPACE, WALKWAY, SERVICES AND TURNING SPACES', fontsize=10, weight='bold', transform=T_.transAxes)
L_w, W_w = mrr_dims(walk); L_s, W_s = mrr_dims(svc)
orows = [('Riverside garden', f'15 m wide (stream edge to the river-front plots); {GARD["len_inner"]:.0f} m along the plots, {GARD["len_mid"]:.0f} m on its centre-line', f'{rpark.area:,.0f}', f'{100 * rpark.area / TOT:.1f}%'),
         ('7 ft walkway', f'{W_w:.2f} m (7 ft) × {L_w:.1f} m, from RD between R10 and R11 to the riverside garden', f'{walk.area:,.0f}', f'{100 * walk.area / TOT:.1f}%'),
         ('Services plot', f'{L_s:.1f} × {W_s:.1f} m at the colony gate, beside the transformer', f'{svc.area:,.0f}', f'{100 * svc.area / TOT:.1f}%'),
         ('  STP', '10.0 × 8.0 m (sewage treatment plant)', '80', ''), ('  Overhead tank + tubewell', '7.0 × 7.0 m', '49', ''), ('  Waste point', '5.0 × 4.0 m', '20', ''),
         ('Turning spaces', f'{len(DE)} × 12.0 × 11.0 m (132 m² each) at the S2 stub and the RD south end – paved, no median', f'{132 * len(DE)}', 'in roads'),
         ('Landscaped corners', f'{len(CORN)} pieces: ' + ', '.join(f'{q.area:,.0f}' for q in sorted(CORN, key=lambda q: -q.area)) + ' m²', f'{sum(q.area for q in CORN):,.0f}', f'{100 * sum(q.area for q in CORN) / TOT:.1f}%')]
cols = [(0.17, 'left'), (0.57, 'left'), (0.10, 'right'), (0.10, 'right')]
y = table(T_, 0, y - 0.006, cols, orows, ('Item', 'Dimensions', 'Area m²', 'Share'), 5.8, 0.0155)
y -= 0.025; T_.text(0, y, 'AREA STATEMENT – COLONY', fontsize=10, weight='bold', transform=T_.transAxes)
y = area_table(T_, 0, y - 0.006, 6.4, 0.0155, W=0.7)
y -= 0.012; T_.text(0, y, f'SELLABLE {SALE * SQ:,.0f} sq ft = {SALE / 4046.86:.2f} acres = {100 * SALE / TOT:.1f}% of the colony ({len(PL)} plots)', fontsize=8.5, weight='bold', color='#1b5e20', transform=T_.transAxes, va='top')
y -= 0.03; T_.text(0, y, 'NOTES', fontsize=10, weight='bold', transform=T_.transAxes)
for s_ in ['Plot dimensions are in feet (1 m = 3.281 ft) on Sheets 3–8; roads, medians, garden, services and boundary in metres.',
           'All figures are measured from the survey drawing (Drg SU/10/01) calibrated to its surveyed areas: expect ±0.5 m.',
           'The approach road, bridge and existing road are traced from the same survey; the road section 2 + 1 + 9 + 1 + 2 m is the surveyor\'s.',
           'Before marking out: redraw on the CAD survey, fix the stream\'s high-water line on site, and check the 15 m garden width against it.',
           'Concept for discussion and T&CP pre-application only – not an approved layout.']:
    y -= 0.016; T_.text(0, y, '• ' + s_, fontsize=6.6, transform=T_.transAxes, va='top')
title_block(fig, 'Roads, medians, open space and services', 'Lengths, widths, cross-sections and areas', '9 of 9', 'n/a', rect=(0.02, 0.012, 0.96, 0.045), fs=8)
pdf.savefig(fig); fig.savefig('pg9.png', dpi=70); plt.close(fig)
