"""Place the colony layout on the land in Google Earth: fit the surveyed site outline (true scale) to the
owner's hand-drawn Google Earth outline (KML shape #20), then export every layer as KML."""
import sys, os, re, math, json, pickle, numpy as np, warnings; warnings.filterwarnings('ignore')
PLAN = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/plan/'
sys.path.insert(0, PLAN); os.chdir(PLAN)
exec(open('dims.py').read().split("if __name__=='__main__':")[0])
from shapely import affinity
from shapely.geometry import Polygon, MultiPolygon, LineString
KML_IN = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/kml_in/places.kml'
OUT = '/home/user/Data-tool/brochure/flow_references/'
s = open(KML_IN, encoding='utf-8', errors='ignore').read()
pms = re.findall(r'<Placemark[^>]*>(.*?)</Placemark>', s, re.S)
cs = re.findall(r'<coordinates>(.*?)</coordinates>', pms[20], re.S)[0]
ll = [tuple(map(float, c.split(',')[:2])) for c in cs.split() if c.count(',') >= 1]
lat0 = sum(c[1] for c in ll) / len(ll); lon0 = sum(c[0] for c in ll) / len(ll)
KX = 111320 * math.cos(math.radians(lat0)); KY = 110574
K = Polygon([((x - lon0) * KX, (y - lat0) * KY) for x, y in ll]).buffer(0)
Ps = unary_union([p.buffer(0.5) for p in pickle.load(open('../site/geo.pkl', 'rb'))['P']]).buffer(-0.5)
pc = Ps.centroid
def place(g, th, dx, dy):
    return affinity.translate(affinity.rotate(affinity.translate(g, -pc.x, -pc.y), th, origin=(0, 0)), dx, dy)
def iou(th, dx, dy):
    q = place(Ps, th, dx, dy); return q.intersection(K).area / q.union(K).area
best = (0, 0, 0, 0)
kc = K.centroid
for th in np.arange(-25, 25.1, 1.0):
    for dx in np.arange(kc.x - 60, kc.x + 61, 10):
        for dy in np.arange(kc.y - 60, kc.y + 61, 10):
            v = iou(th, dx, dy)
            if v > best[0]: best = (v, th, dx, dy)
v, th, dx, dy = best
for step_t, step_d in ((0.5, 4), (0.25, 2), (0.1, 1), (0.05, 0.5)):
    improved = True
    while improved:
        improved = False
        for t2, x2, y2 in ((th + step_t, dx, dy), (th - step_t, dx, dy), (th, dx + step_d, dy), (th, dx - step_d, dy), (th, dx, dy + step_d), (th, dx, dy - step_d)):
            v2 = iou(t2, x2, y2)
            if v2 > v: v, th, dx, dy, improved = v2, t2, x2, y2, True
print('fit (true survey scale): rotation %.2f deg, overlap with the Google Earth outline IoU %.3f' % (th, v))
# also report how a free scale would fit, for information
bs = max(((iou_s, sc) for sc in np.arange(0.9, 1.25, 0.01) for iou_s in [affinity.scale(place(Ps, th, dx, dy), sc, sc, origin=(dx, dy)).intersection(K).area / affinity.scale(place(Ps, th, dx, dy), sc, sc, origin=(dx, dy)).union(K).area]))
print('for comparison, best uniform scale %.2f gives IoU %.3f (the hand-drawn outline is larger than the survey)' % (bs[1], bs[0]))
def to_ll(g):
    g = place(g, th, dx, dy)
    return affinity.affine_transform(g, [1 / KX, 0, 0, 1 / KY, lon0, lat0])
def coords(ring): return ' '.join(f'{x:.7f},{y:.7f},0' for x, y in ring.coords)
def poly_kml(g, name, style, desc=''):
    out = []
    for p in getattr(g, 'geoms', [g]):
        if p.geom_type != 'Polygon' or p.is_empty: continue
        inner = ''.join(f'<innerBoundaryIs><LinearRing><coordinates>{coords(h)}</coordinates></LinearRing></innerBoundaryIs>' for h in p.interiors)
        out.append(f'<Placemark><name>{name}</name><description>{desc}</description><styleUrl>#{style}</styleUrl><Polygon><tessellate>1</tessellate><outerBoundaryIs><LinearRing><coordinates>{coords(p.exterior)}</coordinates></LinearRing></outerBoundaryIs>{inner}</Polygon></Placemark>')
    return ''.join(out)
def line_kml(l, name, style):
    out = []
    for g in getattr(l, 'geoms', [l]):
        if g.geom_type == 'LineString' and g.length > 0:
            out.append(f'<Placemark><name>{name}</name><styleUrl>#{style}</styleUrl><LineString><tessellate>1</tessellate><coordinates>{coords(g)}</coordinates></LineString></Placemark>')
    return ''.join(out)
def st(i, line, w, fill, op=None):  # KML colours are aabbggrr
    def k(c, a): return f'{a}{c[5:7]}{c[3:5]}{c[1:3]}'
    return f'<Style id="{i}"><LineStyle><color>{k(line, "ff")}</color><width>{w}</width></LineStyle><PolyStyle><color>{k(fill, op or "b3")}</color></PolyStyle></Style>'
styles = (st('boundary', '#1b5e20', 3, '#ffffff', '00') + st('plot', '#c62828', 1.2, '#fff3d6', 'a0') + st('rplot', '#c62828', 1.2, '#ffe0a8', 'a0') +
          st('road', '#757575', 1, '#d5d5d5', 'cc') + st('median', '#2e7d32', 1, '#2e7d32', 'e6') + st('garden', '#558b2f', 1, '#9ccc65', 'b0') +
          st('walk', '#8d6e63', 1, '#d7b98e', 'e6') + st('svc', '#5d4037', 1.5, '#bcaaa4', 'cc') + st('resort', '#a8781a', 2, '#f6e6c3', '70') +
          st('access', '#616161', 1, '#9e9e9e', 'cc') + st('outline', '#fdd835', 2.5, '#ffffff', '00') + st('approach', '#616161', 1, '#9e9e9e', 'cc'))
AP = approach_info(); SPLAY = entry_splay(AP)
f = [f'<Folder><name>Colony boundary</name>{poly_kml(to_ll(C), "Colony 11.80 acres", "boundary")}</Folder>',
     '<Folder><name>Plots</name>' + ''.join(poly_kml(to_ll(p), t, 'rplot' if KIND[t] != 'Villa' else 'plot', f'{p.area * SQ:,.0f} sq ft') for t, p in sorted(PL.items(), key=lambda x: (x[0][0] != 'R', int(x[0][1:])))) + '</Folder>',
     f'<Folder><name>Roads (12 m)</name>{poly_kml(to_ll(row), "Colony roads 12 m", "road")}</Folder>',
     f'<Folder><name>Garden medians</name>{poly_kml(to_ll(gard), "Garden median 3 m", "median")}</Folder>',
     f'<Folder><name>Riverside garden</name>{poly_kml(to_ll(rpark), "Riverside garden 15 m", "garden")}</Folder>',
     f'<Folder><name>Walkway</name>{poly_kml(to_ll(walk), "7 ft walkway", "walk")}</Folder>',
     f'<Folder><name>Services plot</name>{poly_kml(to_ll(svc), "Services plot (STP, tank, waste)", "svc")}</Folder>',
     f'<Folder><name>Resort</name>{poly_kml(to_ll(RS), "Resort 11.63 acres", "resort")}</Folder>',
     f'<Folder><name>Access road 15 m</name>{poly_kml(to_ll(access), "Access road 15 m", "access")}{poly_kml(to_ll(SPLAY), "Entry splay", "access")}</Folder>',
     f'<Folder><name>Approach road 15 m (survey)</name>{poly_kml(to_ll(AP["poly"]), "Approach road 15 m", "approach")}</Folder>',
     f'<Folder><name>Your Google Earth outline (hand-drawn)</name>{poly_kml(affinity.affine_transform(K, [1 / KX, 0, 0, 1 / KY, lon0, lat0]), "Hand-drawn outline", "outline")}</Folder>']
doc = (f'<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>Jalkoti colony layout (indicative overlay)</name>'
       f'<description>Layout placed on the land by fitting the surveyed outline (Drg SU/10/01, true scale) to the owner\'s Google Earth outline. Overlap IoU {v:.2f}; position about +/- 20-30 m. Indicative only.</description>'
       f'{styles}{"".join(f)}</Document></kml>')
open(OUT + 'colony_layout_google_earth.kml', 'w').write(doc)
c_ll = to_ll(Point(pc.x, pc.y)); gate_ll = to_ll(Point(331, -262)); entry_ll = to_ll(Point(*AP['cl'].coords[0])); road_ll = to_ll(Point(*AP['cl'].coords[-1]))
meta = dict(fit_rotation_deg=round(th, 2), iou=round(v, 3), site_centre=[round(c_ll.y, 6), round(c_ll.x, 6)], colony_gate=[round(gate_ll.y, 6), round(gate_ll.x, 6)],
            main_entry=[round(entry_ll.y, 6), round(entry_ll.x, 6)], approach_meets_main_road=[round(road_ll.y, 6), round(road_ll.x, 6)])
json.dump(meta, open(OUT + 'site_coordinates.json', 'w'), indent=1); print(meta)
