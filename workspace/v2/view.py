import sys, pickle, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
SP = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
D = pickle.load(open(sys.argv[1], 'rb'))
fig, ax = plt.subplots(figsize=(14, 7.6), dpi=110)
def fp(g, **k):
    for q in getattr(g, 'geoms', [g]):
        if q.geom_type == 'Polygon':
            ax.fill(*q.exterior.xy, **k)
            for h in q.interiors: ax.fill(*h.xy, color='#fbf6ea')
fp(D['K'], color='#fbf6ea'); fp(D['green'], color='#9ccc65'); fp(D['roads'], color='#a3a3a3')
for k in ('amenity', 'svc'):
    if k in D: fp(D[k], color='#d9b98a' if k == 'amenity' else '#b3c0c7')
for i, p in enumerate(D['plots']):
    g = p['poly']; ax.fill(*g.exterior.xy, color='#fdf1d6', ec='#8a6d3b', lw=0.6)
    c = g.centroid; ax.text(c.x, c.y, f"{p.get('no', i+1)}\n{round(p['w']*3.2808)}x{round(p['d']*3.2808)}", fontsize=3.8, ha='center', va='center')
ax.plot(*D['K'].exterior.xy, color='#1e3a2b', lw=1.5)
ax.set_aspect('equal'); ax.set_xlim(110, 470); ax.set_ylim(-260, -45); ax.grid(True, lw=0.2)
ax.set_title(sys.argv[3] if len(sys.argv) > 3 else '')
plt.tight_layout(); plt.savefig(sys.argv[2])
