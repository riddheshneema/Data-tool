import sys,json,warnings; warnings.filterwarnings('ignore'); sys.path.insert(0,'.')
from roadnet import load
from shapely import wkt
from shapely.geometry import box, Point
from shapely.ops import unary_union
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
TAG='Plan_4000_Max_RiverDrive12m'; S,G=load(TAG); OUT='/home/user/Data-tool/site_plans/'
C,row,rpark,gard,svc,access,RS,R=[G(S[k]) for k in ('C','row','rpark','gard','svc','access','RS','R')]
plots={t:(G(w),k) for t,w,k in S['plots']}; DE=json.load(open('deadends_'+TAG+'.json'))
GATE=Point(331,-262); comps=[q for q in getattr(row.buffer(0.4).buffer(-0.4),'geoms',[row]) if q.area>5]; main=min(comps,key=lambda q:q.distance(GATE))
left=C.difference(row).difference(rpark).difference(unary_union([p for p,_ in plots.values()])).difference(svc).buffer(-0.1).buffer(0.1)
views=[('SE block – S5 link road joins S1 to S2',(420,-176),46,['V29','V30','V31','V43','V18','V7','V5']),
       ('V42 – the triangle beside V19 / V20 (corner cut off)',(232,-190),40,['V42','V19','V20'])]
fig,axs=plt.subplots(1,2,figsize=(16,8.4))
for ax,(ttl,(cx,cy),r_,hi) in zip(axs,views):
    V=box(cx-r_,cy-r_,cx+r_,cy+r_)
    def fill(gm,**kw):
        gm=gm.intersection(V)
        for p in getattr(gm,'geoms',[gm]):
            if p.geom_type=='Polygon' and not p.is_empty:
                ax.fill(*p.exterior.xy,**kw)
                for h in p.interiors: ax.fill(*h.xy,fc='white',ec='none')
    fill(R,fc='#cfe8f7',ec='#5aa9d6',lw=0.5); fill(RS,fc='#f6e6c3',ec='#a8781a',lw=0.8)
    fill(left,fc='#c5e1a5',ec='#8bc34a',lw=0.5); fill(rpark,fc='#b9dfa6',ec='#558b2f',lw=0.5)
    fill(row,fc='#d0d0d0',ec='#757575',lw=0.6); fill(gard,fc='#2e7d32',ec='none'); fill(access,fc='#d0d0d0',ec='#757575',lw=0.6)
    for t,(p,k) in plots.items():
        if p.intersection(V).area<1: continue
        h=t in hi
        fill(p,fc='#fff3d6' if k!='Villa' else ('#e3f2fd' if h else 'white'),ec='#b71c1c',lw=1.2 if h else 0.6)
        c=p.intersection(V).representative_point() if not V.contains(p.centroid) else p.centroid
        fr=p.buffer(0.8).intersection(main).area/0.8
        ax.text(c.x,c.y,f'{t}\n{p.area*10.764:,.0f} sq ft'+(f'\n{fr:.1f} m on road' if h else ''),fontsize=8 if h else 6.5,ha='center',va='center',weight='bold' if h else 'normal')
    for d in DE:
        b=G(d['tbox'])
        if b.intersects(V): ax.fill(*b.exterior.xy,fc='none',ec='#e65100',lw=1.1,hatch='////'); ax.text(b.centroid.x,b.centroid.y,'T',color='#e65100',weight='bold',ha='center',va='center')
    fill(C.boundary.buffer(0.25),fc='#1b5e20',ec='none')
    ax.set_xlim(cx-r_,cx+r_); ax.set_ylim(cy-r_,cy+r_); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([]); ax.set_title(ttl,fontsize=11,weight='bold')
    ax.plot([cx-r_+4,cx-r_+14],[cy-r_+4,cy-r_+4],'k',lw=3); ax.text(cx-r_+9,cy-r_+5.5,'10 m',ha='center',fontsize=8)
axs[0].annotate('S5 – 12 m link road\n(S1 joined to S2, no dead end)',(425,-168),xytext=(432,-138),fontsize=8.5,ha='center',weight='bold',arrowprops=dict(arrowstyle='->',lw=0.8))
axs[0].annotate('S2',(384,-150),fontsize=10,weight='bold',ha='center'); axs[0].annotate('S1',(449,-140),fontsize=10,weight='bold',ha='center')
axs[1].annotate('49° tip cut off\n(corner splay)',(249,-206),xytext=(262,-222),fontsize=8,ha='center',arrowprops=dict(arrowstyle='->',lw=0.8))
fig.text(0.5,0.015,'T = 12 x 11 m turning space at a dead end (BVN Rule 43). Plots with a blue fill changed in this round. Areas from the calibrated survey scan – architect to redraw on the CAD survey.',ha='center',fontsize=8.5)
fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig(OUT+TAG+'_Detail_SE_and_V42.png',dpi=130)
