"""Vector artwork for the brochure, drawn from the real layout geometry (no dimensions, consumer style)."""
import sys, math, random, json, pickle, numpy as np, warnings; warnings.filterwarnings('ignore')
PLAN = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/plan/'
sys.path.insert(0, PLAN)
import os; os.chdir(PLAN)
exec(open('dims.py').read().split("if __name__=='__main__':")[0])
os.chdir('/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/brochure')
random.seed(7)
MED = medians_info(); CORN = corners_info()

class SVG:
    def __init__(s, x0, x1, y0, y1, scale):
        s.x0, s.x1, s.y0, s.y1, s.k = x0, x1, y0, y1, scale; s.W = (x1 - x0) * scale; s.H = (y1 - y0) * scale; s.parts = []
    def P(s, x, y): return ((x - s.x0) * s.k, (s.y1 - y) * s.k)
    def path(s, g, **st):
        d = []
        for p in getattr(g, 'geoms', [g]):
            if p.geom_type != 'Polygon' or p.is_empty: continue
            for ring in [p.exterior] + list(p.interiors):
                pts = [s.P(*c) for c in ring.coords]
                d.append('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + ' Z')
        if d: s.parts.append(f'<path d="{" ".join(d)}" fill-rule="evenodd" {s.st(st)}/>')
    def line(s, l, **st):
        for g in getattr(l, 'geoms', [l]):
            if g.geom_type == 'LineString' and g.length > 0:
                pts = [s.P(*c) for c in g.coords]; s.parts.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" {s.st(st)}/>')
    def circle(s, x, y, r, **st):
        X, Y = s.P(x, y); s.parts.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r * s.k:.1f}" {s.st(st)}/>')
    def raw(s, t): s.parts.append(t)
    def st(s, d): return ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in d.items())
    def save(s, fn, defs='', bg=None):
        head = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s.W:.0f} {s.H:.0f}" width="{s.W:.0f}" height="{s.H:.0f}">'
        body = (f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else '') + ''.join(s.parts)
        open(fn, 'w').write(head + f'<defs>{defs}</defs>' + body + '</svg>')

def trees_in(svg, poly, density, rmin, rmax, cols, shadow=True):
    minx, miny, maxx, maxy = poly.bounds; n = int(poly.area * density)
    pts = []
    tries = 0
    while len(pts) < n and tries < n * 30:
        tries += 1; x = random.uniform(minx, maxx); y = random.uniform(miny, maxy)
        if not poly.contains(Point(x, y)): continue
        r = random.uniform(rmin, rmax)
        if any((x - a) ** 2 + (y - b) ** 2 < (0.8 * (r + c)) ** 2 for a, b, c in pts[-60:]): continue
        pts.append((x, y, r))
    for x, y, r in pts:
        if shadow: svg.circle(x + r * 0.35, y - r * 0.35, r, fill='#2f4f2f', fill_opacity='0.18')
    for x, y, r in pts:
        svg.circle(x, y, r, fill=random.choice(cols))
        svg.circle(x - r * 0.3, y + r * 0.3, r * 0.45, fill='#ffffff', fill_opacity='0.16')
def avenue(svg, line, off, step, r, cols):
    for side in ('left', 'right'):
        try: ed = line.parallel_offset(off, side, join_style=2)
        except Exception: continue
        for g in getattr(ed, 'geoms', [ed]):
            if g.geom_type != 'LineString': continue
            for d in np.arange(step / 2, g.length, step):
                q = g.interpolate(d)
                if row.buffer(0.2).contains(q):
                    svg.circle(q.x + r * 0.3, q.y - r * 0.3, r, fill='#2f4f2f', fill_opacity='0.16'); svg.circle(q.x, q.y, r, fill=random.choice(cols))

GREENS = ['#5f8f4e', '#6e9f58', '#7fae63', '#86b46a', '#4f7f45']
# ------------------------------------------------------------------ cover / master-plan artwork
def layout_art(fn, labels=False, x0=92, x1=478, y0=-302, y1=-32, k=3.0, bg='#f3ead9'):
    s = SVG(x0, x1, y0, y1, k)
    defs = ('<linearGradient id="riv" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8ec5e0"/><stop offset="1" stop-color="#5f9fc6"/></linearGradient>'
            '<pattern id="field" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="14" height="14" fill="#efe3c9"/><line x1="0" y1="0" x2="0" y2="14" stroke="#e5d6b6" stroke-width="5"/></pattern>')
    V = box(x0, y0, x1, y1)
    s.path(V, fill='url(#field)')
    s.path(R.intersection(V), fill='url(#riv)')
    for d in (3, 7):
        s.line(R.intersection(V).boundary.intersection(V), stroke='#ffffff', stroke_opacity='0.35', stroke_width=f'{0.6 * k:.1f}', stroke_dasharray=f'{6 * k} {9 * k}')
    s.path(RS.intersection(V), fill='#eadcc0')
    trees_in(s, RS.intersection(V).buffer(-3), 0.0035, 2.2, 3.4, GREENS)
    s.path(C, fill='#f8f3e8')
    s.path(rpark, fill='#a8cf8c')
    trees_in(s, rpark.buffer(-1.0), 0.03, 1.6, 2.8, GREENS)
    for q in CORN: s.path(q, fill='#b9d99f')
    s.path(row, fill='#e3dccd')
    s.path(gard, fill='#7fae63')
    for m_ in MED: trees_in(s, m_['geom'].buffer(-0.2), 0.05, 1.0, 1.35, GREENS, shadow=False)
    for n, L, l in edges:
        if n in ('RD', 'S1', 'S5'): avenue(s, l, 4.6, 9.0, 1.25, GREENS)
        elif n in ('S2', 'S3', 'S4'): avenue(s, l, 5.1, 10.0, 0.95, GREENS)
    s.path(walk, fill='#d8bf94')
    s.path(svc, fill='#e7dccb', stroke='#c9b48e', stroke_width='1')
    for t, p in PL.items():
        s.path(p, fill='#fbf6ea' if KIND[t] == 'Villa' else '#f6e7c8', stroke='#cdb48a', stroke_width=f'{0.22 * k:.2f}')
    s.path(access.intersection(V), fill='#e3dccd')
    s.line(C.exterior, stroke='#3f6b3a', stroke_width=f'{0.55 * k:.1f}', stroke_opacity='0.85')
    if labels:
        def call(n_, x, y):
            X, Y = s.P(x, y); s.raw(f'<g><circle cx="{X:.0f}" cy="{Y:.0f}" r="24" fill="#1e3a2b" stroke="#ffffff" stroke-width="4"/><text x="{X:.0f}" y="{Y + 8.5:.0f}" text-anchor="middle" font-family="Inter" font-weight="700" font-size="24" fill="#ffffff">{n_}</text></g>')
        call(1, 336, -270); call(2, 160, -112); call(3, 300, -70); call(4, 330, -175); call(5, 300, -205); call(6, 214, -142); call(7, 412, -176); call(8, 312, -282)
    s.save(fn, defs, bg=bg)
layout_art('cover_art.svg', labels=False)
layout_art('plan_art.svg', labels=True, bg='#ffffff')

# ------------------------------------------------------------------ schematic location map (not to scale)
def lonlat(lat, lon):  # local equirectangular km
    return ((lon - 75.5894) * 111.32 * math.cos(math.radians(22.17)), (lat - 22.1716) * 110.57)
P_SITE = lonlat(22.1835, 75.5495); P_FORT = (0.0, 0.0)
W, H = 900, 640
def X(km): return 470 + km * 52
def Y(km): return 330 - km * 52
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
       '<defs><linearGradient id="nr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9fd0e8"/><stop offset="1" stop-color="#6fadd1"/></linearGradient></defs>',
       f'<rect width="{W}" height="{H}" rx="18" fill="#f6efe2"/>']
# the Narmada (schematic band along the south of the towns)
svg.append('<path d="M -20 470 C 120 430, 230 455, 330 430 S 520 390, 640 410 S 820 450, 920 420 L 920 520 C 800 545, 680 500, 600 505 S 420 520, 320 525 S 120 545, -20 560 Z" fill="url(#nr)"/>')
svg.append('<text x="640" y="470" font-family="Cormorant Garamond" font-style="italic" font-size="30" fill="#ffffff" fill-opacity="0.95">Narmada</text>')
# roads
fx, fy = X(P_FORT[0]), Y(P_FORT[1]); sx, sy = X(P_SITE[0]), Y(P_SITE[1])
jx, jy = sx - 150, sy + 40
dx, dy = fx - 250, 95
svg.append(f'<path d="M {jx} {jy} C {jx + 60} {jy - 8}, {sx - 40} {sy + 14}, {sx} {sy + 22} S {fx - 90} {fy + 10}, {fx} {fy}" fill="none" stroke="#c9a46c" stroke-width="7" stroke-linecap="round"/>')
svg.append(f'<path d="M {fx} {fy} C {fx - 40} {fy - 90}, {dx + 80} {dy + 60}, {dx} {dy}" fill="none" stroke="#c9a46c" stroke-width="7" stroke-linecap="round"/>')
svg.append(f'<path d="M {dx - 120} {dy + 70} L {dx} {dy} L {dx + 260} {dy - 110}" fill="none" stroke="#b9533a" stroke-width="9" stroke-linecap="round"/>')
svg.append(f'<path d="M {dx + 250} {dy - 105} L {dx + 300} {dy - 128}" stroke="#b9533a" stroke-width="9" stroke-linecap="round"/><polygon points="{dx + 318},{dy - 137} {dx + 290},{dy - 140} {dx + 302},{dy - 115}" fill="#b9533a"/>')
svg.append(f'<text x="{dx + 150}" y="{dy - 88}" font-family="Inter" font-weight="700" font-size="17" fill="#8f3b27" transform="rotate(-23 {dx + 150} {dy - 88})">NH-52 · to Indore ≈ 90 km</text>')
svg.append(f'<text x="{dx - 128}" y="{dy + 96}" font-family="Inter" font-size="14" fill="#8f3b27">Agra–Mumbai highway</text>')
# places
def town(x, y, name, sub=None, big=False, anchor='middle', dy_=-16):
    svg.append(f'<circle cx="{x}" cy="{y}" r="{9 if big else 6}" fill="#1e3a2b" stroke="#ffffff" stroke-width="3"/>')
    svg.append(f'<text x="{x}" y="{y + dy_}" text-anchor="{anchor}" font-family="Cormorant Garamond" font-weight="700" font-size="{30 if big else 22}" fill="#1e3a2b">{name}</text>')
    if sub: svg.append(f'<text x="{x}" y="{y + dy_ + 22}" text-anchor="{anchor}" font-family="Inter" font-size="13.5" fill="#5b6b62">{sub}</text>')
town(fx + 6, fy, 'Maheshwar', 'Ahilya Fort · ghats · temples', big=True, anchor='start', dy_=-20)
town(dx, dy, 'Dhamnod', '13.5 km from Maheshwar', anchor='end', dy_=-14)
town(jx, jy, 'Jalkoti', 'Sahastradhara', anchor='middle', dy_=34)
# fort icon
svg.append(f'<g transform="translate({fx - 30},{fy - 58})" fill="#b8692e"><rect x="0" y="22" width="44" height="16" rx="1"/><rect x="2" y="14" width="6" height="8"/><rect x="14" y="14" width="6" height="8"/><rect x="26" y="14" width="6" height="8"/><rect x="38" y="14" width="6" height="8"/><path d="M 18 22 L 18 6 Q 22 -2 26 6 L 26 22 Z"/></g>')
# the site
svg.append(f'<g><circle cx="{sx}" cy="{sy}" r="34" fill="#5f8f4e" fill-opacity="0.18"/><path d="M {sx} {sy + 2} C {sx - 16} {sy - 18}, {sx - 16} {sy - 40}, {sx} {sy - 44} C {sx + 16} {sy - 40}, {sx + 16} {sy - 18}, {sx} {sy + 2} Z" fill="#1e3a2b"/><circle cx="{sx}" cy="{sy - 29}" r="6" fill="#f6efe2"/></g>')
svg.append(f'<text x="{sx}" y="{sy - 56}" text-anchor="middle" font-family="Cormorant Garamond" font-weight="700" font-size="24" fill="#1e3a2b">Maheshwar Greens</text>')
svg.append(f'<path d="M {sx + 22} {sy + 4} Q {(sx + fx) / 2} {sy + 62}, {fx - 14} {fy + 6}" fill="none" stroke="#1e3a2b" stroke-width="2" stroke-dasharray="5 6"/>')
svg.append(f'<text x="{(sx + fx) / 2}" y="{sy + 64}" text-anchor="middle" font-family="Inter" font-weight="700" font-size="15" fill="#1e3a2b">≈ 4 km to Ahilya Fort</text>')
svg.append(f'<text x="{(sx + fx) / 2}" y="{sy + 82}" text-anchor="middle" font-family="Inter" font-size="12.5" fill="#5b6b62">(straight-line distance)</text>')
svg.append(f'<g transform="translate({W - 70},70)"><path d="M 0 -30 L 10 6 L 0 0 L -10 6 Z" fill="#1e3a2b"/><text x="0" y="26" text-anchor="middle" font-family="Inter" font-weight="700" font-size="15" fill="#1e3a2b">N</text></g>')
svg.append(f'<text x="24" y="{H - 22}" font-family="Inter" font-size="12.5" fill="#7a8a80">Schematic map – not to scale</text>')
svg.append('</svg>')
open('location_map.svg', 'w').write(''.join(svg))

# ------------------------------------------------------------------ heritage line art (decorative)
W2, H2 = 1600, 360
g = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W2} {H2}" width="{W2}" height="{H2}"><rect width="{W2}" height="{H2}" fill="#f3e6cf"/>']
ink = '#b8692e'
# ghat steps
for i in range(9):
    y = 250 + i * 8; g.append(f'<line x1="{80 + i * 18}" y1="{y}" x2="{W2 - 80 - i * 18}" y2="{y}" stroke="{ink}" stroke-width="2.2" stroke-opacity="{0.55 + i * 0.04}"/>')
# fort wall with battlements
g.append(f'<path d="M 140 250 L 140 150 ' + ' '.join(f'L {140 + j * 40} 150 L {140 + j * 40} 138 L {160 + j * 40} 138 L {160 + j * 40} 150' for j in range(9)) + f' L 500 150 L 500 250" fill="none" stroke="{ink}" stroke-width="3"/>')
for j in range(4): g.append(f'<path d="M {175 + j * 80} 250 L {175 + j * 80} 205 Q {195 + j * 80} 180 {215 + j * 80} 205 L {215 + j * 80} 250" fill="none" stroke="{ink}" stroke-width="2.5"/>')
# temple spires (shikhara)
def shikhara(cx, base, h, w):
    return (f'<path d="M {cx - w} {base} L {cx - w} {base - h * 0.35} Q {cx - w * 0.95} {base - h * 0.85} {cx} {base - h} Q {cx + w * 0.95} {base - h * 0.85} {cx + w} {base - h * 0.35} L {cx + w} {base}" fill="none" stroke="{ink}" stroke-width="3"/>'
            f'<line x1="{cx}" y1="{base - h}" x2="{cx}" y2="{base - h - 26}" stroke="{ink}" stroke-width="2.5"/><path d="M {cx} {base - h - 26} L {cx + 16} {base - h - 20} L {cx} {base - h - 14} Z" fill="{ink}"/>'
            + ''.join(f'<line x1="{cx - w * (1 - k_ * 0.12)}" y1="{base - h * (0.35 + k_ * 0.12)}" x2="{cx + w * (1 - k_ * 0.12)}" y2="{base - h * (0.35 + k_ * 0.12)}" stroke="{ink}" stroke-width="1.4" stroke-opacity="0.7"/>' for k_ in range(5)))
g.append(shikhara(720, 250, 190, 62)); g.append(shikhara(880, 250, 150, 50)); g.append(shikhara(1010, 250, 120, 40))
# chhatris (domed pavilions)
def chhatri(cx, base, w):
    return (f'<path d="M {cx - w} {base} L {cx - w} {base - 40} M {cx + w} {base} L {cx + w} {base - 40} M {cx - w - 8} {base - 40} L {cx + w + 8} {base - 40}" stroke="{ink}" stroke-width="3" fill="none"/>'
            f'<path d="M {cx - w} {base - 40} Q {cx - w} {base - 40 - w * 1.4} {cx} {base - 40 - w * 1.5} Q {cx + w} {base - 40 - w * 1.4} {cx + w} {base - 40}" fill="none" stroke="{ink}" stroke-width="3"/>'
            f'<line x1="{cx}" y1="{base - 40 - w * 1.5}" x2="{cx}" y2="{base - 52 - w * 1.5}" stroke="{ink}" stroke-width="2.5"/>')
g.append(chhatri(1180, 250, 34)); g.append(chhatri(1290, 250, 26)); g.append(chhatri(1390, 250, 30))
# river waves
for i in range(4):
    y = 312 + i * 12
    g.append(f'<path d="M 0 {y} ' + ' '.join(f'Q {40 + j * 80} {y - 7} {80 + j * 80} {y} T {160 + j * 80} {y}' for j in range(0, 21, 2)) + f'" fill="none" stroke="#5f9fc6" stroke-width="2" stroke-opacity="{0.8 - i * 0.15}"/>')
# sun
g.append(f'<circle cx="1480" cy="110" r="38" fill="none" stroke="{ink}" stroke-width="2.5"/>' + ''.join(f'<line x1="{1480 + 48 * math.cos(a)}" y1="{110 + 48 * math.sin(a)}" x2="{1480 + 60 * math.cos(a)}" y2="{110 + 60 * math.sin(a)}" stroke="{ink}" stroke-width="2"/>' for a in np.linspace(0, 2 * math.pi, 13)[:-1]))
g.append('</svg>'); open('heritage.svg', 'w').write(''.join(g))
stats = dict(plots=len(PL), nR=sum(1 for t in PL if KIND[t] != 'Villa'), nV=sum(1 for t in PL if KIND[t] == 'Villa'),
             rmin=min(p.area * SQ for t, p in PL.items() if KIND[t] != 'Villa'), rmax=max(p.area * SQ for t, p in PL.items() if KIND[t] != 'Villa'),
             vmin=min(p.area * SQ for t, p in PL.items() if KIND[t] == 'Villa'), vmax=max(p.area * SQ for t, p in PL.items() if KIND[t] == 'Villa'),
             garden_ac=rpark.area / 4046.86, colony_ac=C.area / 4046.86, n4050=sum(1 for t, p in PL.items() if abs(p.area * SQ - 4050) < 15))
json.dump(stats, open('stats.json', 'w')); print(stats)
