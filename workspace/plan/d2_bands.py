import pickle, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
D='/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/plan/'
B=pickle.load(open(D+'d2_base.pkl','rb')); R,C,RS,P=B['river'],B['colony'],B['resort'],B['P']
edges=[0,25,58.5,71.5,102,110,140.5,153.5,400]
cols=['#a5d6a7','#ffcc80','#bdbdbd','#fff59d','#c5e1a5','#ffe082','#bdbdbd','#ce93d8']
fig,ax=plt.subplots(figsize=(9,12))
def fill(g,**kw):
    for p in getattr(g,'geoms',[g]):
        if p.geom_type=='Polygon' and not p.is_empty:
            x,y=p.exterior.xy; ax.fill(x,y,**kw)
fill(R,fc='#90caf9'); fill(RS,fc='#f5f5f5',ec='k',lw=0.5)
for i in range(len(edges)-1):
    band=C.intersection(R.buffer(edges[i+1])).difference(R.buffer(edges[i]))
    fill(band,fc=cols[i],ec='none')
fill(C,fc='none',ec='green',lw=1)
for p in P: fill(p,fc='none',ec='k',lw=0.4)
ax.plot(336,-483,'r*',ms=14)
ax.set_aspect('equal'); ax.set_xlim(100,480); ax.set_ylim(-570,-40); ax.grid(alpha=.3)
plt.savefig(D+'bands.png',dpi=90,bbox_inches='tight')
