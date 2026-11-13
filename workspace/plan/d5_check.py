import json,sys
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from shapely import wkt
D='/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/plan/'
L=json.load(open(D+sys.argv[1])); roads=wkt.loads(L['roads']); row=wkt.loads(L.get('row',L['roads']))
fig,ax=plt.subplots(figsize=(9,12))
def fill(g,**kw):
    for p in getattr(g,'geoms',[g]):
        if p.geom_type=='Polygon' and not p.is_empty:
            x,y=p.exterior.xy; ax.fill(x,y,**kw)
fill(wkt.loads(L['R']),fc='#90caf9'); fill(wkt.loads(L['RS']),fc='#f5f5f5',ec='k',lw=.5)
fill(wkt.loads(L['river_park']),fc='#c5e1a5'); fill(wkt.loads(L['garden']),fc='#7cb342'); fill(wkt.loads(L['left']),fc='#fff59d')
fill(roads,fc='#bdbdbd',ec='#757575',lw=.4)
bad=0
for i,(s,k) in enumerate(L['plots']):
    p=wkt.loads(s); fr=p.buffer(0.8).intersection(row).area/0.8; ok=fr>=8; bad+=not ok
    fill(p,fc=('#fff8e1' if k.startswith('River') else 'white') if ok else '#ef9a9a',ec='#b71c1c',lw=.5)
    ax.text(p.centroid.x,p.centroid.y,f'{i+1}\n{p.area*10.7639:.0f}',fontsize=4,ha='center',va='center')
print('no frontage:',bad)
ax.set_aspect('equal'); ax.set_xlim(100,420); ax.set_ylim(-570,-250)
plt.savefig(D+sys.argv[2],dpi=100,bbox_inches='tight')
