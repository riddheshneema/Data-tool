import json, sys, numpy as np, pickle
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from shapely import wkt
D='/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
L=json.load(open(sys.argv[1])); out=sys.argv[2]
river=np.load(D+'site/river.npy'); res=0.5
fig,ax=plt.subplots(figsize=(9,12))
ys,xs=np.nonzero(river[::4,::4]); ax.scatter(xs*4*res,-ys*4*res,s=1,c='#7fb3d5',marker='s',lw=0)
def fill(g,**kw):
    gs=getattr(g,'geoms',[g])
    for p in gs:
        if p.geom_type=='Polygon' and not p.is_empty:
            x,y=p.exterior.xy; ax.fill(x,y,**kw)
fill(wkt.loads(L['resort']),fc='#f6e3b4',ec='#b8860b',lw=1.2)
fill(wkt.loads(L['colony']),fc='#d9f0d3',ec='#2e7d32',lw=1.2)
fill(wkt.loads(L['roads']),fc='#bdbdbd',ec='none')
for i,s in enumerate(L['plots']):
    p=wkt.loads(s); fill(p,fc='#fff',ec='#c62828',lw=0.5)
    c=p.centroid; ax.text(c.x,c.y,str(i+1),fontsize=4.5,ha='center',va='center')
ax.set_aspect('equal'); ax.set_xlim(100,480); ax.set_ylim(-570,-40); ax.set_title(sys.argv[3] if len(sys.argv)>3 else '')
plt.savefig(out,dpi=110,bbox_inches='tight')
