import json
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from shapely import wkt
D='/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/plan/'
L=json.load(open(D+'d4_layout.json'))
roads=wkt.loads(L['roads'])
fig,ax=plt.subplots(figsize=(9,12))
def fill(g,**kw):
    for p in getattr(g,'geoms',[g]):
        if p.geom_type=='Polygon' and not p.is_empty:
            x,y=p.exterior.xy; ax.fill(x,y,**kw)
fill(wkt.loads(L['R']),fc='#90caf9'); fill(wkt.loads(L['RS']),fc='#f5f5f5',ec='k',lw=.5)
fill(wkt.loads(L['green']),fc='#c8e6c9'); fill(roads,fc='#bdbdbd',ec='#757575',lw=.4)
bad=0
for i,(s,k,*_) in enumerate(L['plots']):
    p=wkt.loads(s); front=p.buffer(0.6).intersection(roads.boundary).length
    ok=front>=8
    bad+=not ok
    fill(p,fc='#fff' if ok else '#ef9a9a',ec='#b71c1c',lw=.5)
    ax.text(p.centroid.x,p.centroid.y,f'{i+1}\n{front:.0f}',fontsize=4,ha='center',va='center')
print('plots without >=8 m road frontage:',bad)
ax.set_aspect('equal'); ax.set_xlim(100,420); ax.set_ylim(-570,-250)
plt.savefig(D+'d4_check.png',dpi=100,bbox_inches='tight')
