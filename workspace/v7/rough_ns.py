exec(open('/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/v7/kit.py').read())
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.path import Path; from matplotlib.patches import PathPatch
V = pickle.load(open(SP + 'v7/final8.pkl', 'rb')); K, STRIP, L, CL = V['K'], V['STRIP'], V['L'], V['CL']
W = Fr(V['Wo'], V['Wth']); E = Fr(V['Eo'], V['Eth']); GU = V['GU']; VS = V['VS']; X0, bis = V['X0'], V['bis']
st = pickle.load(open(SP + 'brochure2/stream08.pkl', 'rb'))['stream']
BUILD = K.difference(R.buffer(9)); D = 22.86
nE = (-bis[1], bis[0]) if -bis[1] > 0 else (bis[1], -bis[0])
def hp(s):
    a = (X0[0] - bis[0] * 600, X0[1] - bis[1] * 600); b = (X0[0] + bis[0] * 600, X0[1] + bis[1] * 600)
    return Polygon([a, b, (b[0] + s * nE[0] * 900, b[1] + s * nE[1] * 900), (a[0] + s * nE[0] * 900, a[1] + s * nE[1] * 900)])
HPW, HPE = hp(-1), hp(1)
drive = CL['loop'][0].buffer(4.5, cap_style=2).intersection(unary_union([W.rect(-40, 260, 0, 20), E.rect(40, 200, 0, 20)]))
cross = CL['cross'][0]; crossl = LineString([cross.coords[0], (cross.coords[0][0] + bis[0] * 140, cross.coords[0][1] + bis[1] * 140)])
streets = [W.line([(u, 13.5), (u, VS)]).buffer(4.5 if abs(u - GU) > 1 else 6, cap_style=2) for u in (10.8, 65.5, GU)] + [crossl.buffer(4.5, cap_style=2), E.line([(134, 13.5), (134, 150)]).buffer(4.5, cap_style=2)]
roads = unary_union([drive] + streets).intersection(K)
v0 = L['A1'][1]
north = unary_union([W.rect(-19, 260, L['A1'][0], v0).intersection(HPW), E.rect(40, 104, L['A1'][0], v0).intersection(HPE)]).intersection(BUILD).difference(roads)
east, west = [], []
for fr, hpz, us, vend in ((W, HPW, [(10.8, 4.5), (65.5, 4.5), (GU, 6)], VS), (E, HPE, [(134, 4.5)], 175)):
    for u, h in us:
        east.append(fr.rect(u - h - D, u - h, v0, vend).intersection(hpz)); west.append(fr.rect(u + h, u + h + D, v0, vend).intersection(hpz))
hu = lambda fr, v: fr.uv(*crossl.interpolate(crossl.project(Point(fr.xy(0, v)))).coords[0])[0]
east.append(W.rect(150, 260, v0, VS).intersection(HPW).intersection(crossl.buffer(4.5 + D, cap_style=2)))
west.append(E.rect(40, 134 - 4.5 - D, v0, 175).intersection(HPE).intersection(crossl.buffer(4.5 + D, cap_style=2)))
park = W.rect(GU - 6 - D, GU - 6, 75, 113)
clean = lambda gs: unary_union(gs).intersection(BUILD).difference(roads).difference(park).buffer(-0.4)
east, west = clean(east), clean(west).difference(clean(east).buffer(0.5))
fig, axs = plt.subplots(1, 2, figsize=(17, 6.6), dpi=130)
def fp(ax, g, **k):
    for q in parts(g):
        verts = []; codes = []
        for ring in [q.exterior] + list(q.interiors):
            c = np.array(ring.coords); verts += list(c); codes += [Path.MOVETO] + [Path.LINETO] * (len(c) - 2) + [Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(verts, codes), **k))
COL = dict(N='#9fd0f0', E='#a9dc8f', W='#f6c98b', S='#ef8f86')
for ax in axs:
    fp(ax, R, fc='#e3f0f8', ec='none'); fp(ax, st, fc='#7db9de', ec='none'); fp(ax, K, fc='#dfeecf', ec='#b3261e', lw=1.6)
    ax.set_xlim(108, 474); ax.set_ylim(-272, -42); ax.set_aspect('equal'); ax.axis('off'); ax.text(186, -74, 'S T R E A M', fontsize=9, color='#3d7ea6', rotation=24, style='italic')
    ax.annotate('', xy=(462, -52), xytext=(462, -68), arrowprops=dict(arrowstyle='-|>', color='k', lw=1.5)); ax.text(462, -48, 'N', ha='center', fontsize=10, weight='bold')
ax = axs[0]; fp(ax, V['roads'], fc='#bdbab4', ec='none'); fp(ax, V['park'], fc='#7fbf6a', ec='none'); fp(ax, V['club'], fc='#ecd9b4', ec='none')
for p in V['info']: ax.fill(*p['poly'].exterior.xy, color=COL['N'] if p['front'] == 'lo' else COL['S'], ec='#555', lw=0.4)
nS = sum(1 for p in V['info'] if p['front'] != 'lo'); ax.set_title(f"NOW: streets run along the stream  —  {nS} of {len(V['info'])} plots face south", fontsize=12, weight='bold', loc='left')
ax = axs[1]; fp(ax, roads, fc='#bdbab4', ec='none'); fp(ax, park.difference(roads), fc='#7fbf6a', ec='none'); fp(ax, V['club'], fc='#ecd9b4', ec='none')
fp(ax, north, fc=COL['N'], ec='#555', lw=0.5); fp(ax, east, fc=COL['E'], ec='#555', lw=0.5); fp(ax, west, fc=COL['W'], ec='#555', lw=0.5)
for g, t in ((east, 'E'), (west, 'W')):
    for q in parts(g):
        if q.area > 400: c = q.representative_point(); ax.text(c.x, c.y, t, fontsize=11, weight='bold', ha='center', va='center', color='#333')
for q in parts(north):
    if q.area > 400: c = q.representative_point(); ax.text(c.x, c.y, 'N', fontsize=11, weight='bold', ha='center', va='center', color='#333')
ax.text(*W.xy(GU - 6 - D / 2, 94), 'PARK', fontsize=7, ha='center', va='center', rotation=W.th - 90, weight='bold', color='#1e4a22')
ax.text(*W.xy(60, 13.5), 'STREAM DRIVE (kept)', fontsize=6.5, ha='center', va='center', rotation=W.th, color='#fff', weight='bold')
ax.text(*W.xy(GU, 100), 'AVENUE', fontsize=6.5, ha='center', va='center', rotation=W.th - 90, color='#fff', weight='bold')
gx, gy = W.xy(GU, VS); ax.text(gx + 8, gy - 6, 'GATE', fontsize=9, weight='bold')
ax.set_title('ROUGH IDEA: inner streets turned to run stream-to-gate  —  no plot faces south', fontsize=12, weight='bold', loc='left')
import matplotlib.patches as mp
fig.legend(handles=[mp.Patch(fc=COL[k], ec='#555', label=l) for k, l in (('N', 'faces north'), ('E', 'faces east'), ('W', 'faces west'), ('S', 'faces south'))] + [mp.Patch(fc='#bdbab4', label='road'), mp.Patch(fc='#7fbf6a', label='park')],
           loc='lower center', ncol=6, frameon=False, fontsize=10)
fig.text(0.5, 0.965, 'Rough sketch only: coloured bands are rows of plots, not individual plots. Nothing is set out or measured yet.', ha='center', fontsize=9, color='#666')
plt.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.08, wspace=0.02)
out = '/home/user/Data-tool/site_plans/final/Rough_Sketch_No_South_Facing.png'; plt.savefig(out); print(out)
