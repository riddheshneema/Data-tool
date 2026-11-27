exec(open('/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/v7/kit.py').read())
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.patches as mp
from matplotlib.path import Path; from matplotlib.patches import PathPatch
D = pickle.load(open(SP + 'v7/plan9.pkl', 'rb')); K = D['K']; W = Fr(D['Wo'], D['Wth']); E = Fr(D['Eo'], D['Eth'])
st = pickle.load(open(SP + 'brochure2/stream08.pkl', 'rb'))['stream']
fig = plt.figure(figsize=(16.54, 10.2), dpi=140); ax = fig.add_axes([0.005, 0.07, 0.76, 0.86])
def fp(g, **k):
    for q in parts(g):
        verts = []; codes = []
        for ring in [q.exterior] + list(q.interiors):
            c = np.array(ring.coords); verts += list(c); codes += [Path.MOVETO] + [Path.LINETO] * (len(c) - 2) + [Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(verts, codes), **k))
COL = dict(N='#9fd0f0', E='#a9dc8f', W='#f6c98b')
fp(R, fc='#e3f0f8', ec='none'); fp(st, fc='#7db9de', ec='none'); fp(unary_union([RS, C.difference(K)]), fc='#f3eddd', ec='none')
fp(K, fc='#dcecc9', ec='none'); fp(D['STRIP'], fc='#c3e2ad', ec='none'); fp(D['roads'], fc='#b9b6b0', ec='#8d8a84', lw=0.3); fp(D['park'], fc='#79bb63', ec='#4d8a3c', lw=0.6); fp(D['club'], fc='#ecd9b4', ec='#9b7b4b', lw=0.6)
for i, p in enumerate(D['plots']):
    g = p['poly']; ax.fill(*g.exterior.xy, color=COL[p['face']], ec='#4a4a4a', lw=0.5, zorder=4)
    c = g.representative_point(); rot = p['fr'] if p['face'] == 'N' else p['fr'] + 90
    rot = (rot + 90) % 180 - 90
    ax.text(c.x, c.y, f"{g.area * SQFT:,.0f}", fontsize=4.6, ha='center', va='center', rotation=rot, zorder=5, color='#222')
ax.plot(*K.exterior.xy, color='#b3261e', lw=1.8, zorder=6)
T = lambda u, v, s, r=0, **k: ax.text(*W.xy(u, v), s, rotation=((W.th + r) + 90) % 180 - 90, ha='center', va='center', zorder=7, **k)
T(60, 13.5, 'STREAM DRIVE  9 m', color='#fff', fontsize=6.5, weight='bold'); T(D['GU'], 60, 'THE AVENUE  12 m', r=90, color='#fff', fontsize=6.5, weight='bold')
for u in D['US']: T(u, 70, '9 m', r=90, color='#fff', fontsize=6, weight='bold')
pc = D['park'].centroid; ax.text(pc.x, pc.y, 'CENTRAL PARK\n150 × 79 ft\n(45.7 × 24 m)', ha='center', va='center', fontsize=6.3, weight='bold', color='#12360f', rotation=W.th, zorder=7)
cc = D['club'].representative_point(); ax.text(cc.x, cc.y, 'CLUBHOUSE', ha='center', va='center', fontsize=6, weight='bold', color='#6a4a20', rotation=W.th, zorder=7)
gx, gy = W.xy(D['GU'], D['VS']); ax.text(gx + 4, gy - 7, 'GATE', fontsize=9, weight='bold')
ax.text(186, -74, 'S T R E A M', fontsize=9, color='#3d7ea6', rotation=24, style='italic')
ax.annotate('', xy=(462, -52), xytext=(462, -68), arrowprops=dict(arrowstyle='-|>', color='k', lw=1.6)); ax.text(462, -48, 'N', ha='center', fontsize=11, weight='bold')
ax.plot([395, 445], [-262, -262], color='k', lw=2.2); ax.text(420, -267.5, '50 m  (164 ft)', ha='center', fontsize=7)
ax.set_xlim(108, 474); ax.set_ylim(-272, -42); ax.set_aspect('equal'); ax.axis('off')
from collections import Counter
fc = Counter(p['face'] for p in D['plots']); tot = sum(p['poly'].area for p in D['plots']) * SQFT; NA = K.area
pn = fig.add_axes([0.775, 0.07, 0.22, 0.86]); pn.axis('off'); pn.set_xlim(0, 1); pn.set_ylim(0, 1)
pn.text(0, 0.99, 'JALKOTI COLONY', fontsize=15, weight='bold', va='top', color='#1e3a2b'); pn.text(0, 0.945, 'Draft v9: no south-facing plots', fontsize=9.5, va='top', color='#555')
rows = [('', 'Final (v8)', 'This draft'), ('Plots', '77', str(len(D['plots']))), ('Sellable sq ft', '262,115', f'{tot:,.0f}'), ('Sellable share', '54.4%', f'{tot / SQFT / NA * 100:.1f}%'),
        ('Face north', '43', str(fc['N'])), ('Face east', '0', str(fc['E'])), ('Face west', '0', str(fc['W'])), ('Face south', '34', '0'), ('Roads share', '23.2%', f"{D['roads'].area / NA * 100:.1f}%"), ('Central Park', '1,089 m²', f"{D['park'].area:,.0f} m²")]
y = 0.87
for i, (a, b, c) in enumerate(rows):
    k = dict(fontsize=8.6, weight='bold' if i == 0 or a in ('Face south', 'Sellable share') else 'normal')
    pn.text(0, y, a, **k); pn.text(0.66, y, b, ha='right', **k); pn.text(1.0, y, c, ha='right', **k); y -= 0.043
    if i == 0: pn.plot([0, 1], [y + 0.018, y + 0.018], color='#1e3a2b', lw=0.6)
y -= 0.02
for k_, l in (('N', 'faces north (stream row)'), ('E', 'faces east'), ('W', 'faces west')):
    pn.add_patch(mp.Rectangle((0, y - 0.012), 0.06, 0.026, fc=COL[k_], ec='#555', lw=0.5)); pn.text(0.09, y, l, fontsize=8.4, va='center'); y -= 0.043
y -= 0.01
for t in ['Number on each plot = area in sq ft.', 'Draft for your decision: plot numbers,', 'dimension sheets and landscaping are', 'not redone yet.']:
    pn.text(0, y, t, fontsize=7.6, color='#444'); y -= 0.032
out = '/home/user/Data-tool/site_plans/final/Draft_v9_No_South_Facing.png'; fig.savefig(out); print(out)
