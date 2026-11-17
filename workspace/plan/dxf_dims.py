"""Dimensioned DXF of the colony (metres, north up) – every plot side as a real aligned dimension in feet,
road / median / garden / boundary dimensions in metres, plus the approach road from the main road."""
import sys, math, numpy as np, warnings; warnings.filterwarnings('ignore'); sys.path.insert(0, '.')
exec(open('dims.py').read().split("if __name__=='__main__':")[0])
import ezdxf
from ezdxf.enums import TextEntityAlignment
OUT = '/home/user/Data-tool/site_plans/'
INFO = {t: plot_info(t) for t in PL}
MED = medians_info(); AP = approach_info(); SPLAY = entry_splay(AP); CORN = corners_info()

doc = ezdxf.new('R2010', setup=True); doc.header['$INSUNITS'] = 6; doc.header['$MEASUREMENT'] = 1
msp = doc.modelspace()
LAY = {  # name: (ACI colour, description)
    'COLONY_BOUNDARY': (3, 'Colony boundary'), 'PLOTS': (1, 'Plot outlines'), 'PLOT_TEXT': (7, 'Plot number and area'),
    'ROADS': (8, 'Road right of way'), 'ROAD_CENTRELINE': (9, 'Road centre-lines'), 'ROAD_TEXT': (7, 'Road names, widths, lengths'),
    'MEDIANS': (94, 'Garden medians'), 'RIVERSIDE_GARDEN': (82, 'Riverside garden (open space)'), 'WALKWAY': (32, '7 ft walkway'),
    'SERVICES': (34, 'Services plot, STP, tank, waste point'), 'LANDSCAPE': (72, 'Landscaped corners'), 'TURNING_SPACE': (30, 'Turning spaces 12 x 11 m'),
    'RESORT': (42, 'Resort land'), 'ACCESS_ROAD': (8, 'Public access road 15 m'), 'ENTRY_SPLAY': (8, 'Entry splay at the main entry'),
    'APPROACH_ROAD': (8, 'Approach road 15 m (survey)'), 'EXISTING_ROAD': (250, 'Existing Jalkoti-Maheshwar road (survey)'),
    'BRIDGE': (1, 'Bridge over the stream (survey)'), 'STREAM': (5, 'Stream / river as surveyed'),
    'DIM_PLOTS': (5, 'Plot side dimensions (feet)'), 'DIM_PLOTS_ARC': (5, 'Curved plot sides (feet, along the curve)'),
    'DIM_ROADS': (4, 'Road width dimensions (m)'), 'DIM_MEDIANS': (94, 'Median dimensions (m)'), 'DIM_GARDEN': (82, 'Garden width (m)'),
    'DIM_BOUNDARY': (3, 'Colony boundary lengths (m)'), 'DIM_OTHER': (6, 'Walkway, services, turning space dimensions (m)'), 'NOTES': (7, 'Notes')}
for n, (c, d) in LAY.items():
    l = doc.layers.add(n, color=c); l.description = d
# dimension styles: FT shows metres drawn as feet (x 3.28084); M shows metres
for nm, fac, post, dec, h in (('PLOT_FT', FT, "<>'", 1, 0.75), ('ROAD_M', 1.0, '<> m', 1, 1.0), ('SMALL_M', 1.0, '<> m', 2, 0.6)):
    ds = doc.dimstyles.new(nm)
    ds.dxf.dimlfac = fac; ds.dxf.dimpost = post; ds.dxf.dimdec = dec; ds.dxf.dimtxt = h; ds.dxf.dimasz = h * 0.6
    ds.dxf.dimexe = h * 0.3; ds.dxf.dimexo = h * 0.25; ds.dxf.dimgap = h * 0.2; ds.dxf.dimtad = 1; ds.dxf.dimtih = 0; ds.dxf.dimtoh = 0
    ds.dxf.dimblk = 'ARCHTICK' if nm == 'PLOT_FT' else ''; ds.dxf.dimzin = 8; ds.dxf.dimclrd = 0; ds.dxf.dimclre = 0; ds.dxf.dimclrt = 0; ds.dxf.dimtxsty = 'OpenSans'
def poly(g, layer, closed=True):
    for p in getattr(g, 'geoms', [g]):
        if p.geom_type == 'Polygon' and not p.is_empty:
            msp.add_lwpolyline(list(p.exterior.coords), close=True, dxfattribs={'layer': layer})
            for h in p.interiors: msp.add_lwpolyline(list(h.coords), close=True, dxfattribs={'layer': layer})
        elif p.geom_type == 'LineString' and p.length > 0:
            msp.add_lwpolyline(list(p.coords), close=False, dxfattribs={'layer': layer})
def text(s, xy, h, layer, rot=0.0, align=TextEntityAlignment.MIDDLE_CENTER):
    msp.add_text(s, height=h, rotation=rot, dxfattribs={'layer': layer, 'style': 'OpenSans'}).set_placement(tuple(xy), align=align)
def upright(deg):
    deg = (deg + 180) % 360 - 180
    if deg > 90: deg -= 180
    if deg <= -90: deg += 180
    return deg
def adim(p1, p2, dist, style, layer, override=None):
    d = msp.add_aligned_dim(p1=tuple(p1), p2=tuple(p2), distance=dist, dimstyle=style, override=override or {}, dxfattribs={'layer': layer})
    d.render()
# ---------------- geometry layers
poly(R, 'STREAM'); poly(RS, 'RESORT'); poly(C, 'COLONY_BOUNDARY'); poly(row, 'ROADS'); poly(gard, 'MEDIANS'); poly(rpark, 'RIVERSIDE_GARDEN')
poly(walk, 'WALKWAY'); poly(svc, 'SERVICES')
for b in util.values(): poly(b, 'SERVICES')
for q in CORN: poly(q, 'LANDSCAPE')
for d in DE: poly(G(d['tbox']), 'TURNING_SPACE')
poly(access, 'ACCESS_ROAD'); poly(SPLAY, 'ENTRY_SPLAY'); poly(AP['poly'], 'APPROACH_ROAD'); poly(AP['exist_poly'], 'EXISTING_ROAD')
for l in getattr(AP['bridge'], 'geoms', [AP['bridge']]):
    if l.geom_type == 'LineString' and l.length > 1: poly(l, 'BRIDGE')
for n, L, l in edges: poly(l, 'ROAD_CENTRELINE')
poly(AP['cl'], 'ROAD_CENTRELINE')
for t, p in PL.items(): poly(p, 'PLOTS')
# ---------------- plot labels and side dimensions
n_dims = 0; n_arcs = 0
for t, p in PL.items():
    c = p.representative_point() if not p.centroid.within(p) else p.centroid
    text(t, (c.x, c.y + 0.9), 1.4, 'PLOT_TEXT'); text(f"{INFO[t]['sqft']:,.0f} sq ft", (c.x, c.y - 0.9), 0.9, 'PLOT_TEXT')
    for s_ in INFO[t]['sides']:
        if s_['len'] < 1.5: continue
        l = s_['line']
        if not s_['curved']:
            a, b = np.array(l.coords[0]), np.array(l.coords[-1])
            adim(a, b, -1.1, 'PLOT_FT', 'DIM_PLOTS'); n_dims += 1        # clockwise ring: negative = inside the plot
        else:
            m = l.interpolate(0.5, normalized=True); a = np.array(l.interpolate(0.46, normalized=True).coords[0]); b = np.array(l.interpolate(0.54, normalized=True).coords[0])
            dv = (b - a) / np.linalg.norm(b - a); nin = np.array([dv[1], -dv[0]]); q = np.array(m.coords[0]) + nin * 1.3
            if not p.contains(Point(q)): q = np.array(m.coords[0]) - nin * 1.3
            text(f"{s_['len'] * FT:.1f}' arc", q, 0.75, 'DIM_PLOTS_ARC', rot=upright(math.degrees(math.atan2(dv[1], dv[0])))); n_arcs += 1
# ---------------- roads: width dimension across each road + name / ROW / length
RD_ = roads_info()
for r_ in RD_:
    n = r_['name']; cand = sorted([(L, l) for nm, L, l in edges if nm == n], key=lambda x: -x[0])
    if not cand: continue
    L, l = cand[0]
    for f in ((0.5,) if n not in ('RD', 'S2', 'S3', 'S4') else ((0.25, 0.62) if n == 'RD' else (0.22,))):
        m = l.interpolate(f, normalized=True); a = np.array(l.interpolate(max(0, f - 0.03), normalized=True).coords[0]); b = np.array(l.interpolate(min(1, f + 0.03), normalized=True).coords[0])
        dv = (b - a) / np.linalg.norm(b - a); nr = np.array([-dv[1], dv[0]])
        cut = LineString([tuple(np.array(m.coords[0]) - nr * 12), tuple(np.array(m.coords[0]) + nr * 12)]).intersection(unary_union([row, access]).buffer(0.05))
        segs = [g_ for g_ in getattr(cut, 'geoms', [cut]) if g_.geom_type == 'LineString' and g_.distance(m) < 0.5]
        if not segs: continue
        sg = segs[0]; adim(sg.coords[0], sg.coords[-1], 0.0, 'ROAD_M', 'DIM_ROADS')
        ang = upright(math.degrees(math.atan2(dv[1], dv[0])))
        text(f"{n}  {r_['row']:.0f} m ROW  ~{r_['len']:.0f} m long", np.array(m.coords[0]) - dv * 10, 1.1, 'ROAD_TEXT', rot=ang)
# ---------------- garden medians: width across and length along
for m_ in MED:
    q = m_['geom']; mrr = list(q.minimum_rotated_rectangle.exterior.coords)[:4]
    e = [(np.array(mrr[i]), np.array(mrr[(i + 1) % 4])) for i in range(4)]; e.sort(key=lambda ab: -np.linalg.norm(ab[1] - ab[0]))
    a, b = e[0]; adim(a, b, 2.2, 'ROAD_M', 'DIM_MEDIANS')
    a, b = e[2] if np.linalg.norm(e[2][1] - e[2][0]) < 5 else e[3]
    c = q.centroid; dv = (e[0][1] - e[0][0]) / np.linalg.norm(e[0][1] - e[0][0])
    text(f"Garden median 3.0 m x {m_['len']:.1f} m", (c.x, c.y), 0.7, 'DIM_MEDIANS', rot=upright(math.degrees(math.atan2(dv[1], dv[0]))))
# ---------------- riverside garden width at intervals
mid = rpark.intersection(R.buffer(7.5).exterior)
for l in [g_ for g_ in getattr(mid, 'geoms', [mid]) if g_.geom_type == 'LineString' and g_.length > 20]:
    for f in np.arange(0.08, 1.0, 0.14):
        m = l.interpolate(f, normalized=True); a = np.array(l.interpolate(max(0, f - 0.01), normalized=True).coords[0]); b = np.array(l.interpolate(min(1, f + 0.01), normalized=True).coords[0])
        dv = (b - a) / np.linalg.norm(b - a); nr = np.array([-dv[1], dv[0]])
        cut = LineString([tuple(np.array(m.coords[0]) - nr * 9), tuple(np.array(m.coords[0]) + nr * 9)]).intersection(rpark)
        segs = [g_ for g_ in getattr(cut, 'geoms', [cut]) if g_.geom_type == 'LineString' and g_.distance(m) < 0.5]
        if segs: adim(segs[0].coords[0], segs[0].coords[-1], 0.0, 'ROAD_M', 'DIM_GARDEN')
g0 = rpark.representative_point(); text('RIVERSIDE GARDEN - 15 m wide (open space)', (g0.x, g0.y), 1.6, 'DIM_GARDEN')
# ---------------- colony boundary lengths (outside the boundary)
for s_ in sides(C, None, merge_deg=12.0, simp=0.3):
    if s_['len'] < 6: continue
    l = s_['line']; chord = LineString([l.coords[0], l.coords[-1]]); dev = max(chord.distance(Point(c)) for c in l.coords)
    on_stream = R.distance(l.interpolate(0.5, normalized=True)) < 3.0
    if not on_stream and dev < 1.5:
        adim(l.coords[0], l.coords[-1], 3.0, 'ROAD_M', 'DIM_BOUNDARY')          # clockwise ring: positive = outside
    else:
        m = l.interpolate(0.5, normalized=True); a = np.array(l.interpolate(0.48, normalized=True).coords[0]); b = np.array(l.interpolate(0.52, normalized=True).coords[0])
        dv = (b - a) / np.linalg.norm(b - a); nout = np.array([-dv[1], dv[0]])
        text(f"{s_['len']:.1f} m " + ('(along the stream edge)' if on_stream else '(along the boundary)'), np.array(m.coords[0]) + nout * 3, 1.0, 'DIM_BOUNDARY', rot=upright(math.degrees(math.atan2(dv[1], dv[0]))))
# ---------------- walkway, services plot, utilities, turning spaces
for g_ in [walk, svc] + list(util.values()) + [G(d['tbox']) for d in DE]:
    mrr = list(g_.minimum_rotated_rectangle.exterior.coords)[:4]
    adim(mrr[0], mrr[1], 0.8, 'SMALL_M', 'DIM_OTHER'); adim(mrr[1], mrr[2], 0.8, 'SMALL_M', 'DIM_OTHER')
for k, b in util.items(): text({'STP (sewage treatment)': 'STP', 'Overhead tank + tubewell': 'OHT + TUBEWELL', 'Waste point': 'WASTE'}[k], (b.centroid.x, b.centroid.y), 0.8, 'SERVICES')
text('SERVICES PLOT', (svc.centroid.x, svc.bounds[1] + 2), 1.0, 'SERVICES')
for d in DE: b = G(d['tbox']); text('TURNING SPACE 12 x 11 m', (b.centroid.x, b.centroid.y), 0.6, 'TURNING_SPACE')
text('COLONY GATE', (338, -258), 1.4, 'ROAD_TEXT')
# ---------------- approach road, existing road
m = AP['cl'].interpolate(0.5, normalized=True); a = np.array(AP['cl'].interpolate(0.49, normalized=True).coords[0]); b = np.array(AP['cl'].interpolate(0.51, normalized=True).coords[0])
dv = (b - a) / np.linalg.norm(b - a); nr = np.array([-dv[1], dv[0]])
adim(np.array(m.coords[0]) - nr * 7.6, np.array(m.coords[0]) + nr * 7.6, 0.0, 'ROAD_M', 'DIM_ROADS')
text(f"APPROACH ROAD 15 m ROW (2+1+9+1+2)  ~{AP['len']:.0f} m from the existing road to the main entry", np.array(m.coords[0]) + nr * 14, 2.0, 'ROAD_TEXT', rot=upright(math.degrees(math.atan2(dv[1], dv[0]))))
ex = AP['exist_poly'].bounds
text(f"EXISTING ROAD (to Jalkoti / to Maheshwar) ~{AP['exist_w']:.1f} m as surveyed", ((ex[0] + ex[2]) / 2, ex[1] - 4), 2.0, 'ROAD_TEXT')
text(f"ACCESS ROAD 15 m  ~{max(mrr_dims(access)):.0f} m (main entry to colony gate)", (352, -372), 1.6, 'ROAD_TEXT', rot=90)
text('MAIN ENTRY', (Point(AP['cl'].coords[0]).x - 14, Point(AP['cl'].coords[0]).y + 4), 1.8, 'ROAD_TEXT')
# ---------------- notes
for i, s_ in enumerate(['JALKOTI COLONY - DIMENSIONED LAYOUT (units: metres; plot side dimensions shown in feet)',
                        f'{len(PL)} plots - sellable {sum(p.area for p in PL.values()) * SQ:,.0f} sq ft - colony {C.area / 4046.86:.2f} acres - all colony roads 12 m',
                        'Measured from survey Drg SU/10/01 calibrated to its surveyed areas (+/- 0.5 m). Redraw on the CAD survey and verify on site before marking out.',
                        'Layers: DIM_PLOTS (aligned dims, ft) - DIM_PLOTS_ARC (curved sides) - DIM_ROADS / DIM_MEDIANS / DIM_GARDEN / DIM_BOUNDARY / DIM_OTHER (m)']):
    text(s_, (100, -300 - i * 4), 2.0 if i == 0 else 1.4, 'NOTES', align=TextEntityAlignment.LEFT)
path = OUT + 'Jalkoti_Colony_Dimensioned_Layout.dxf'
doc.saveas(path)
print('saved', path, '| plot side dims', n_dims, '| curved sides', n_arcs, '| entities', len(msp))
