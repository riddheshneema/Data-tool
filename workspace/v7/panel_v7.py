# side panel for sheet 1 (runs inside render_v7.py)
from collections import Counter
NA = K.area; tot = sum(p['area'] for p in info)
gN, gW, gE, sE, svc, rest = V['gardenN'], V['lawnW'], V['gardenE'], V['southE'], V['svc'], V['rest']
prom = rest.area + sE.area - svc.area
pn = fig.add_axes([0.742, 0.03, 0.25, 0.94]); pn.axis('off'); pn.set_xlim(0, 1); pn.set_ylim(0, 1)
y = 0.995
pn.text(0, y, 'JALKOTI COLONY', fontsize=15, weight='bold', va='top', color='#1e3a2b'); y -= 0.030
pn.text(0, y, 'Layout v7 — set out from the road geometry', fontsize=8.6, va='top', color='#555'); y -= 0.040
def head(t):
    global y
    pn.text(0, y, t, fontsize=8.8, weight='bold', color='#1e3a2b'); y -= 0.006
    pn.plot([0, 0.98], [y, y], color='#1e3a2b', lw=0.6); y -= 0.019
def row3(a, b, c, bold=False):
    global y
    k = dict(fontsize=7.0, weight='bold' if bold else 'normal')
    pn.text(0, y, a, **k); pn.text(0.76, y, b, ha='right', **k); pn.text(0.98, y, c, ha='right', **k); y -= 0.0185
def line(t, **k):
    global y
    pn.text(0, y, t, fontsize=k.pop('fontsize', 6.9), **k); y -= 0.0178
head('AREA STATEMENT')
for nm, a in [(f'Plots ({len(info)})', tot / SQFT), ('Roads (12 m avenue, 9 m streets)', roads.area), ('Central park', park.area),
              ('Stream garden, stream lawn, NE garden', gN.area + gW.area + gE.area), ('Stream promenade and verges', prom), ('Clubhouse plot', club.area), ('Services yard', svc.area)]:
    row3(nm, f'{a:,.0f} m²', f'{a / NA * 100:.1f}%')
row3('Total colony land', f'{NA:,.0f} m²', f'{NA / 4046.86:.2f} ac', bold=True)
line(f'({(NA - club.area) / 4046.86:.2f} ac if the clubhouse plot is counted with the resort)', fontsize=6.2, color='#666'); y -= 0.012
head('PLOTS')
row3('Sellable area', f'{tot:,.0f} sq ft', f'{tot / SQFT / NA * 100:.1f}%', bold=True)
row3('Smallest / average / largest', f"{min(p['area'] for p in info):,.0f} / {tot / len(info):,.0f} / {max(p['area'] for p in info):,.0f}", 'sq ft')
y -= 0.004
pn.text(0, y, 'Row', fontsize=6.4, weight='bold'); pn.text(0.40, y, 'Plots', fontsize=6.4, weight='bold', ha='right'); pn.text(0.44, y, 'Typical size (ft)', fontsize=6.4, weight='bold'); pn.text(0.98, y, 'Faces', fontsize=6.4, weight='bold', ha='right'); y -= 0.017
for rk_, nm in (('A1', 'Stream Drive (stream side)'), ('A2', 'Second St, north side'), ('B1', 'Second St, south side'), ('B2', 'Third St, north side'), ('C1', 'Third St, south side')):
    ps = [p for p in info if p['row'] == rk_]
    wm = Counter(round(p['front_w'] * FT) for p in ps if 'cross' not in p['shape']).most_common(1)[0][0]
    pn.text(0, y, nm, fontsize=6.6); pn.text(0.40, y, str(len(ps)), fontsize=6.6, ha='right')
    pn.text(0.44, y, f"{wm} × 75   ({min(p['area'] for p in ps):,.0f}–{max(p['area'] for p in ps):,.0f} sf)", fontsize=6.6)
    pn.text(0.98, y, 'north' if ps[0]['front'] == 'lo' else 'south', fontsize=6.6, ha='right'); y -= 0.0172
y -= 0.004
nrect = sum(1 for p in info if p['shape'].startswith('rectangle')); ncross = len(info) - nrect
line(f'{nrect} rectangles, {ncross} corner plots on the Cross Street (one side 6° off square)')
line('Every plot shares its side and back walls with its neighbours')
line(f"{sum(1 for p in info if 'stream-facing' in p['tags'])} stream-facing · {sum(1 for p in info if 'park-facing' in p['tags'] or 'park-side' in p['tags'])} on the central park · {sum(1 for p in info if p['corner'])} corner plots")
line('Cream rows face north, pink rows face south')
line('Green strip along the stream = 9 m no-build promenade', color='#1e4a22'); y -= 0.012
head('RULE CHECKS (BVN 2012)')
far12 = max(p['d12'] for p in info); farg = max(p['gate_m'] for p in info)
ops = park.area + gN.area + gW.area + gE.area
for t in [f"All plots over 225 m², street front {min(p['front_w'] for p in info):.1f} m or more (Rule 53)",
          f'Parks and gardens {ops / NA * 100:.0f}% of the land in 4 places (Rule 47: 10%)',
          f'Farthest plot {far12:.0f} m from the 12 m avenue (9 m road limit 250 m)', f'Farthest plot {farg:.0f} m from the gate (limit 400 m)',
          'Three short closes (about 30, 80, 85 m; limit 150 m), two with turning circles', '9 m no-build strip along the stream throughout (Rule 50(b))',
          'To confirm on site: high-water line, levels for drainage and STP']:
    line(t, fontsize=6.6)
