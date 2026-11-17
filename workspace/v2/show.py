"""Quick look at a v2 pickle (skeleton or layout)."""
import sys, pickle, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
SP = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
D = pickle.load(open(sys.argv[1], 'rb')); out = sys.argv[2]
fig, ax = plt.subplots(figsize=(14, 7.6), dpi=110)
def fp(g, **k):
    for q in getattr(g, 'geoms', [g]):
        if q.geom_type == 'Polygon':
            ax.fill(*q.exterior.xy, **k)
            for h in q.interiors: ax.fill(*h.xy, color='white')
def lp(g, **k):
    for q in getattr(g, 'geoms', [g]):
        if hasattr(q, 'exterior'): ax.plot(*q.exterior.xy, **k)
        elif q.geom_type == 'LineString': ax.plot(*q.xy, **k)
fp(D['N'], color='#fbf6ea')
if 'outer' in D: fp(D['outer'], color='#f3e2c4')
if 'core' in D: fp(D['core'], color='#f7ecd6')
fp(D['roads'], color='#a3a3a3'); fp(D['walk_green'], color='#7fb446')
if 'amenity' in D: fp(D['amenity'], color='#d9b98a')
for k, c in (('parks', '#9ccc65'), ('svc', '#b3c0c7')):
    if k in D: fp(D[k], color=c)
if 'plots' in D:
    for t, g in D['plots'].items():
        lp(g, color='#8a6d3b', lw=0.6)
        c = g.representative_point(); ax.text(c.x, c.y, t, fontsize=4.5, ha='center', va='center', color='#5a4630')
if 'labels' in D:
    for (x, y, t) in D['labels']: ax.text(x, y, t, fontsize=7, ha='center', va='center', color='#1e3a2b', weight='bold')
lp(D['N'], color='#1e3a2b', lw=1.6)
ax.set_xticks(range(110, 471, 10)); ax.set_yticks(range(-240, -40, 10)); ax.grid(True, lw=0.25, alpha=0.4)
ax.set_xlim(110, 470); ax.set_ylim(-240, -45); ax.set_aspect('equal'); ax.tick_params(labelsize=6)
if len(sys.argv) > 3: ax.set_title(sys.argv[3], fontsize=10)
plt.tight_layout(); plt.savefig(out)
