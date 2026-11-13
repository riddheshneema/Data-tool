import sys,pickle,json,numpy as np,warnings; warnings.filterwarnings('ignore')
sys.path.insert(0,'.'); from roadnet import load
from shapely import wkt
from shapely.geometry import Point, LineString, box
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
TAG='Plan_4000_Max_RiverDrive12m'; S,G=load(TAG)
C,row,rpark,walk,svc,access,R=[G(S[k]) for k in ('C','row','rpark','walk','svc','access','R')]
RT=pickle.load(open('roadtest_'+TAG+'.pkl','rb'))
views=[('S1 / V31 / V30',(445,-175),45),('V7 / S1 north',(440,-110),45),('V39 / RD south end',(290,-245),40),
       ('Promenade NE end',(400,-60),45),('Promenade SW end',(250,-255),45),('Gate / access road',(330,-300),60)]
fig,axs=plt.subplots(2,3,figsize=(18,12))
for ax,(ttl,(cx,cy),r_) in zip(axs.ravel(),views):
    for g,fc,ec in ((R,'#9fd3f2','#5aa9d6'),(G(S['RS']),'#f6e6c3','#a8781a'),(C,'#ffffff','#2e7d32'),(rpark,'#b9dfa6','#558b2f'),(row,'#d0d0d0','#555'),(access,'#bdbdbd','#555'),(walk,'#d7b98e','#8d6e63'),(svc,'#bcaaa4','#5d4037')):
        for q in getattr(g,'geoms',[g]):
            if q.geom_type=='Polygon':
                ax.fill(*q.exterior.xy,fc=fc,ec=ec,lw=0.8)
                for h in q.interiors: ax.fill(*h.xy,fc='#ffffff',ec=ec,lw=0.5)
    for t,w,k in S['plots']:
        p=wkt.loads(w); ax.fill(*p.exterior.xy,fc='#fff3d6' if k!='Villa' else 'white',ec='#b71c1c',lw=0.8)
        ax.text(p.centroid.x,p.centroid.y,t,fontsize=8,ha='center',va='center')
    for n,L,wmin,lw in RT['edges']:
        l=wkt.loads(lw); ax.plot(*l.xy,color='#1565c0',lw=1)
    for n,L,xy in RT['dead']: ax.plot(*xy,'rx',ms=10,mew=2)
    ax.set_xlim(cx-r_,cx+r_); ax.set_ylim(cy-r_,cy+r_); ax.set_aspect('equal'); ax.set_title(ttl)
    ax.grid(True,lw=0.3)
fig.tight_layout(); fig.savefig('zoom_tests.png',dpi=80)
