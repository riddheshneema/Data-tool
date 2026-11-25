"""Sheet 1: the layout plan."""
exec(open('/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/v7/kit.py').read())
import random, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.path import Path; from matplotlib.patches import PathPatch, Ellipse, Circle, RegularPolygon
OUT = '/home/user/Data-tool/site_plans/v7_set_out/'; os.makedirs(OUT, exist_ok=True)
V = pickle.load(open(SP + 'v7/final.pkl', 'rb'))
K, roads, park, club, green, STRIP, L, CL, info = V['K'], V['roads'], V['park'], V['club'], V['green'], V['STRIP'], V['L'], V['CL'], V['info']
W = Fr(V['Wo'], V['Wth']); E = Fr(V['Eo'], V['Eth']); FR = dict(W=W, E=E); GU = V['GU']; VS = V['VS']
st = pickle.load(open(SP + 'brochure2/stream08.pkl', 'rb'))['stream']
mid = lambda k: (L[k][0] + L[k][1]) / 2
random.seed(11)
def draw_plan(ax, labels=True, plot_fill=None, small=False):
    def fp(g, z=1, **k):
        for q in parts(g):
            verts = []; codes = []
            for ring in [q.exterior] + list(q.interiors):
                c = np.array(ring.coords); verts += list(c); codes += [Path.MOVETO] + [Path.LINETO] * (len(c) - 2) + [Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(verts, codes), zorder=z, **k))
    def trees(g, every, r, z=5, inset=1.2):
        e = g.buffer(-r - inset)
        for q in parts(e):
            n = int(q.exterior.length / every)
            for i in range(n):
                pt = q.exterior.interpolate((i + random.uniform(-0.2, 0.2)) * every)
                ax.add_patch(Circle((pt.x, pt.y), r * random.uniform(0.8, 1.15), color=random.choice(['#4f8a3a', '#5b9744', '#6aa34f', '#3f7a33']), zorder=z, lw=0))
    ax.set_facecolor('#ffffff')
    fp(R, fc='#e3f0f8', ec='none'); fp(st, fc='#7db9de', ec='none')
    fp(unary_union([RS, C.difference(K)]), fc='#f1ead9', ec='none'); fp(access, fc='#c9c6c0', ec='none')
    gate = W.xy(GU, VS)
    ax.add_patch(PathPatch(Path([W.xy(GU - 6, VS), W.xy(GU + 6, VS), (337.5, -262), (324.5, -262), W.xy(GU - 6, VS)], [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]), fc='#c9c6c0', ec='none', zorder=1))
    fp(K, z=2, fc='#bfe0a6', ec='none')
    fp(park, z=3, fc='#a5d488', ec='none')
    fp(roads, z=3, fc='#b9b6b0', ec='#8d8a84', lw=0.35)
    fp(club, z=3, fc='#ecd9b4', ec='#9b7b4b', lw=0.6)
    for p in info:
        g = p['poly']; col = plot_fill(p) if plot_fill else ('#fdf6e4' if p['front'] == 'lo' else '#f6dcd5')
        ax.fill(*g.exterior.xy, color=col, ec='#9b7b4b', lw=0.55, zorder=4)
        fr = FR[p['grid']]; c = g.centroid; rot = fr.th
        dim = f"{round(p['front_w'] * FT)}×{round(p['depth'] * FT)}" if 'cross' not in p['shape'] else f"{round(p['area']):,} sf"
        if labels:
            dx, dy = fr.ev[0] * 3.2, fr.ev[1] * 3.2
            ax.text(c.x - dx, c.y - dy, str(p['no']), fontsize=6.4 if not small else 5.4, ha='center', va='center', zorder=7, weight='bold', color='#3d2f1b', rotation=rot)
            if not small: ax.text(c.x + dx, c.y + dy, dim, fontsize=4.0, ha='center', va='center', zorder=7, color='#7a6a52', rotation=rot)
    # landscape
    trees(STRIP, 8.5, 1.9, inset=0.3)
    for z_, ev, r in ((V['gardenN'].difference(STRIP), 9, 2.0), (V['lawnW'].difference(STRIP), 10, 2.1), (V['gardenE'], 9, 1.9), (park, 8.5, 1.9), (V['southE'], 9, 1.7)):
        trees(z_, ev, r)
    for vv in np.arange(L['A1'][0] + 5, VS - 4, 10.5):          # avenue trees
        if any(abs(vv - mid(k)) < 8 for k in ('s2', 's3')): continue
        for du in (-5.0, 5.0):
            x, y = W.xy(GU + du, vv); ax.add_patch(Circle((x, y), 1.25, color='#3f7a33', zorder=6, lw=0))
    # park furniture
    pc = park.centroid; ax.add_patch(Circle((pc.x, pc.y), 7.5, fc='#c5e6ad', ec='#ffffff', lw=0.8, zorder=4)); ax.add_patch(Circle((pc.x, pc.y), 2.2, fc='#e8a33d', ec='none', zorder=5))
    for g_, off in ((V['lawnW'], (0, 0)), (V['gardenE'], (0, 0))):
        q = big(g_.difference(STRIP).buffer(-6));
        if not q.is_empty:
            c_ = q.representative_point(); ax.add_patch(RegularPolygon((c_.x, c_.y), 6, radius=3.0, fc='#b5673e', ec='#7a4326', lw=0.5, zorder=6))
    dk = W.xy(GU, 3.0); ax.add_patch(PathPatch(Path([W.xy(GU - 5, 6.5), W.xy(GU + 5, 6.5), W.xy(GU + 5, -2.5), W.xy(GU - 5, -2.5), W.xy(GU - 5, 6.5)], [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]), fc='#c9a26b', ec='#8a6a3b', lw=0.5, zorder=6))
    # clubhouse building + pool
    cu0 = GU + 6 + 4; b1 = W.rect(cu0, cu0 + 15, L['C1'][0] + 5, L['C1'][0] + 17).intersection(club.buffer(-2)); fp(b1, z=5, fc='#b98d55', ec='#7a5a2e', lw=0.5)
    pl = W.rect(cu0 + 19, cu0 + 30, L['C1'][0] + 6.5, L['C1'][0] + 13).intersection(club.buffer(-2)); fp(pl, z=5, fc='#7ec8e3', ec='#ffffff', lw=0.6)
    ax.plot(*K.exterior.xy, color='#b3261e', lw=1.9, zorder=8)
    gx, gy = gate; ax.add_patch(PathPatch(Path([W.xy(GU - 7.5, VS - 1.2), W.xy(GU + 7.5, VS - 1.2), W.xy(GU + 7.5, VS + 1.2), W.xy(GU - 7.5, VS + 1.2), W.xy(GU - 7.5, VS - 1.2)], [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]), fc='#3d2f1b', ec='none', zorder=9))
    return fp
if __name__ == '__main__':
    import matplotlib.patheffects as pe
    halo = [pe.withStroke(linewidth=1.8, foreground='#eef7e4')]
    fig = plt.figure(figsize=(16.54, 11.69)); ax = fig.add_axes([0.008, 0.335, 0.725, 0.655])
    fp = draw_plan(ax)
    T = lambda fr, u, v, s, rot=None, **k: ax.text(*fr.xy(u, v), s, rotation=fr.th if rot is None else rot, ha='center', va='center', zorder=9, **k)
    rk = dict(fontsize=5.6, color='#ffffff', weight='bold')
    T(W, 52, mid('drive'), 'STREAM DRIVE   9 m', **rk); T(W, 60, mid('s2'), 'SECOND STREET   9 m', **rk); T(W, 78, mid('s3'), 'THIRD STREET   9 m', **rk)
    T(E, 120, mid('s2'), 'SECOND STREET', **rk); T(E, 128, mid('s3'), 'THIRD STREET', **rk)
    T(W, GU, 92, 'THE AVENUE   12 m', rot=W.th - 90, **rk); T(W, -23.7, 50, 'WEST LOOP', rot=W.th - 90, **rk)
    cx_ = CL['cross'][0].interpolate(0.36, normalized=True); ax.text(cx_.x, cx_.y, 'CROSS STREET', rotation=-73.3, ha='center', va='center', zorder=9, **rk)
    gk = dict(fontsize=6.3, color='#1e4a22', weight='bold', path_effects=halo)
    pc = park.centroid; ax.text(pc.x, pc.y - 12.5, f'CENTRAL PARK  {park.area:,.0f} m²', ha='center', va='center', zorder=9, rotation=W.th, **gk)
    T(W, 166, -1.5, f"STREAM GARDEN  {V['gardenN'].area:,.0f} m²", **gk)
    T(W, GU - 15.5, 1.5, 'viewing deck', fontsize=4.8, color='#3d2f1b', path_effects=halo)
    lw_ = big(V['lawnW'].difference(STRIP).buffer(-5)).representative_point(); ax.text(lw_.x - 2, lw_.y - 9, f"STREAM LAWN  {V['lawnW'].area:,.0f} m²", ha='center', va='center', zorder=9, **gk)
    ge = big(V['gardenE'].buffer(-5)).representative_point(); ax.text(ge.x + 4, ge.y - 7.5, f"NE GARDEN\n{V['gardenE'].area:,.0f} m²", ha='center', va='center', zorder=9, **gk)
    sv = V['svc'].representative_point(); ax.text(sv.x - 4, sv.y, 'SERVICES', fontsize=5.0, ha='center', va='center', zorder=9, color='#3d2f1b', rotation=E.th - 14, path_effects=halo)
    T(W, GU + 6 + 27, L['C1'][0] + 3.2, f'CLUBHOUSE  {club.area:,.0f} m²', fontsize=5.6, color='#6a4a20', weight='bold')
    gx, gy = W.xy(GU, VS); ax.text(gx + 12, gy - 5, 'GATE', fontsize=8, weight='bold', zorder=9, color='#3d2f1b')
    ax.annotate('', xy=(331, -266), xytext=(gx + 3.2, gy - 7), arrowprops=dict(arrowstyle='<|-', color='#3d2f1b', lw=1.0), zorder=9)
    ax.text(347, -252, 'approach from the resort\ngate and main road', fontsize=5.6, color='#5a4a32', zorder=9, va='center')
    ax.text(291, -252.5, 'kept with the resort — the club\nlawn and pool can extend here', fontsize=5.0, color='#7a6a42', zorder=9, ha='center', va='center', rotation=W.th)
    ax.text(150, -262, 'RESORT LAND', fontsize=8, color='#9a8a62', zorder=9)
    ax.text(186, -74, 'S T R E A M', fontsize=9, color='#3d7ea6', rotation=24, zorder=9, style='italic')
    ax.annotate('', xy=(462, -52), xytext=(462, -68), arrowprops=dict(arrowstyle='-|>', color='k', lw=1.6)); ax.text(462, -48.5, 'N', ha='center', fontsize=11, weight='bold')
    ax.plot([395, 445], [-262, -262], color='k', lw=2.2); ax.plot([395, 395], [-263.5, -260.5], color='k', lw=1); ax.plot([445, 445], [-263.5, -260.5], color='k', lw=1)
    ax.text(420, -267.5, '50 m  (164 ft)', ha='center', fontsize=7)
    ax.set_xlim(108, 474); ax.set_ylim(-275, -40); ax.set_aspect('equal'); ax.axis('off')
    exec(open(SP + 'v7/panel_v7.py').read())
    exec(open(SP + 'v7/band_v7.py').read())
    fig.savefig(OUT + 'Jalkoti_Colony_v7_Layout.pdf'); fig.savefig(OUT + 'Jalkoti_Colony_v7_Layout.png', dpi=170)
    print('sheet 1 saved')
