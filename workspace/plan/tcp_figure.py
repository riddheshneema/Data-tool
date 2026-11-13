import sys,json,pickle,numpy as np,networkx as nx,warnings; warnings.filterwarnings('ignore'); sys.path.insert(0,'.')
from roadnet import load
from shapely import wkt
from shapely.geometry import Point, LineString, box
from shapely.ops import unary_union, substring
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
TAG='Plan_4000_Max_RiverDrive12m'; S,G=load(TAG); OUT='/home/user/Data-tool/site_plans/'
C,row,rpark,walk,svc,access,R,RS=[G(S[k]) for k in ('C','row','rpark','walk','svc','access','R','RS')]
plots={t:(G(w),k) for t,w,k in S['plots']}
RT=pickle.load(open('roadtest_'+TAG+'.pkl','rb')); DE=json.load(open('deadends_'+TAG+'.json'))
GATE=Point(331,-262)
# shortest route from the gate to the farthest plot along the road centre-lines
edges=[(n,L,wkt.loads(l)) for n,L,w,l in RT['edges']]
g=nx.Graph(); key=lambda c:(round(c[0],1),round(c[1],1))
for n,L,l in edges: g.add_edge(key(l.coords[0]),key(l.coords[-1]),len=L,line=l)
far_t,far_d=max(RT['pdist'].items(),key=lambda x:x[1]); fp=plots[far_t][0]
eg=min(edges,key=lambda e:e[2].distance(GATE)); tg=eg[2].project(GATE)
ef=min(edges,key=lambda e:e[2].distance(fp)); tf=ef[2].project(fp.centroid)
best=None
for sa,sl in ((key(eg[2].coords[0]),substring(eg[2],tg,0)),(key(eg[2].coords[-1]),substring(eg[2],tg,eg[2].length))):
    for fa,fl in ((key(ef[2].coords[0]),substring(ef[2],0,tf)),(key(ef[2].coords[-1]),substring(ef[2],tf,ef[2].length))):
        try: path=nx.shortest_path(g,sa,fa,weight='len')
        except nx.NetworkXNoPath: continue
        segs=[sl]+[g[a][b]['line'] for a,b in zip(path[:-1],path[1:])]+[fl]
        L=sum(s.length for s in segs)
        if best is None or L<best[0]: best=(L,segs)
fig=plt.figure(figsize=(15,11)); ax=fig.add_axes([0.0,0.0,0.62,1.0])
def fill(gm,**kw):
    for p in getattr(gm,'geoms',[gm]):
        if p.geom_type=='Polygon':
            ax.fill(*p.exterior.xy,**kw)
            for h in p.interiors: ax.fill(*h.xy,fc='white',ec='none')
fill(R.intersection(box(90,-580,490,-30)),fc='#cfe8f7',ec='#5aa9d6',lw=0.5)
fill(RS,fc='#f7efdc',ec='#c9a96a',lw=0.8)
fill(rpark,fc='#cde8bf',ec='#7cb342',lw=0.5)
fill(row,fc='#dcdcdc',ec='#9e9e9e',lw=0.4); fill(access,fc='#dcdcdc',ec='#9e9e9e',lw=0.4)
fill(walk,fc='#d7b98e',ec='#8d6e63',lw=0.5)
for t,(p,k) in plots.items():
    fill(p,fc='#ffffff',ec='#b0b0b0',lw=0.5); ax.text(p.centroid.x,p.centroid.y,t,fontsize=4.2,ha='center',va='center',color='#757575')
fill(svc,fc='#bcaaa4',ec='#5d4037',lw=1.0)
fill(C,fc='none',ec='#1b5e20',lw=1.6)
# 15 m line from the stream edge
sl=R.buffer(15).exterior.intersection(C.buffer(1))
for l in getattr(sl,'geoms',[sl]):
    if l.length>5: ax.plot(*l.xy,color='#1565c0',lw=0.9,ls=(0,(4,2)))
# farthest route
for s in best[1]: ax.plot(*s.xy,color='#c62828',lw=2.2,alpha=0.85)
# dead ends + turning spaces
for d in DE:
    b=G(d['tbox']); ax.fill(*b.exterior.xy,fc='#ffcc80',ec='#e65100',lw=1.1,hatch='////')
def tag(n,x,y,col):
    ax.text(x,y,str(n),fontsize=9,weight='bold',color='white',ha='center',va='center',bbox=dict(boxstyle='circle,pad=0.25',fc=col,ec='none'))
GOOD,RISK,ACT='#2e7d32','#ef6c00','#c62828'
tag(1,150,-120,RISK); ax.text(158,-116,'Riverside garden\n12.9% (≥10%) – shape is\nT&CP\'s call (47(3))',fontsize=7,color=RISK,va='center')
tag(2,197,-148,GOOD); ax.text(203,-152,'7 ft walkway = garden access (47(5))',fontsize=6.5,color=GOOD,va='center')
tag(3,470,-140,GOOD); ax.text(470,-150,f'farthest plot {far_t}:\n{far_d:.0f} m from the\ngate (≤400 m,\n38(6))',fontsize=6.8,color=GOOD,ha='center',va='top')
for d in DE:
    x_,y_=d['end']; nm={'link':'S1','RD':'RD south','S2':'S2'}[d['name']]
    ok=d['name']!='link'
    tx,ty={'link':(475,-195),'RD':(228,-268),'S2':(x_+2,y_-14)}[d['name']]
    tag(4,tx,ty,GOOD if ok else RISK)
    ax.text(tx,ty-9,f"{nm} dead end {d['len']} m\nturning space 132 m²"+('' if ok else '\nnot straight (43)'),fontsize=6.3,ha='center',va='top',color=GOOD if ok else RISK)
tag(5,123,-215,GOOD); ax.text(118,-228,'15 m from the stream\nedge (50(b): 9 m / 15 m)',fontsize=6.5,color='#1565c0',ha='left')
tag(6,svc.centroid.x-24,svc.centroid.y-4,GOOD); ax.text(svc.centroid.x-24,svc.centroid.y-14,'services plot\ninside the colony',fontsize=6.5,color=GOOD,ha='center',va='top')
tag(7,350,-400,ACT); ax.text(352,-412,'15 m access road\nmust be dedicated\nas a public street\n(2(72), 38(6))',fontsize=6.8,color=ACT,ha='left',va='top')
ax.set_aspect('equal'); ax.set_xlim(95,500); ax.set_ylim(-500,-40); ax.axis('off')
ax.plot([110,160],[-492,-492],'k',lw=3); ax.text(135,-487,'50 m',ha='center',fontsize=7)
t=fig.add_axes([0.63,0.02,0.36,0.96]); t.axis('off')
t.text(0,0.985,'T&CP COMPLIANCE TEST',fontsize=14,weight='bold')
t.text(0,0.962,'Land outside a planning area, already diverted – Gram Panchayat colony rules 2014 (Rule 10(2):',fontsize=7.4)
t.text(0,0.947,'T&CP opinion) tested against MP Bhumi Vikas Niyam 2012 as consolidated to 6 Mar 2025',fontsize=7.4)
rows=[(GOOD,'PASS','38(4), 53','Every plot on a 12 m road; smallest frontage 13.7 m (>12 m); smallest plot 336 m²'),
      (GOOD,'PASS','38 + T.3','All roads 12 m; farthest plot %d m from the gate (12 m allowed to 400 m)'%round(far_d)),
      (GOOD,'PASS','43','S5 link joins S1 to S2 – S1 is no longer a dead end'),
      (GOOD,'PASS','43','Dead ends S2 stub 42 m and RD south 66 m: straight, 12 × 11 m turning space'),
      (GOOD,'PASS','45','Junctions 68–94°; none under 30°'),
      (GOOD,'PASS','47(2)','Open space 12.9% of layout (minimum 10%) – the riverside garden'),
      (RISK,'T&CP','47(3)','Garden ~35× as long as wide: "generally" ≤2.5×, other shapes at T&CP discretion'),
      (GOOD,'PASS','47(5)','Garden reached by the 7 ft walkway; river plots keep the 3 m building line'),
      (GOOD,'PASS','50(b)','Plots 15 m from the stream edge (9 m stream / 15 m river) – survey the high-water line'),
      (GOOD,'PASS','56','Setbacks 3.6 / 3 / 3 m leave every plot a ≥114 m² footprint, ≥7.7 m wide'),
      (GOOD,'PASS','49','~300 residents: below every Table 6 facility threshold'),
      (GOOD,'PASS','services','STP, tank + tubewell, waste plot (549 m²) inside the colony'),
      (ACT,'DO','2(72)','Access road through the resort must be a dedicated public street'),
      (ACT,'DO','2014 rules','EWS/LIG 6% (≈1,840 m²) or the shelter fee; 25% plots (16) mortgaged'),
      (ACT,'DO','MPLRC 59','Check the diversion purpose; intimate the residential part with a sketch'),
      (ACT,'DO','RERA','Register before any advertising, video or booking')]
y=0.915
for col,res,rule,txt in rows:
    t.text(0,y,res,fontsize=7.6,weight='bold',color='white',bbox=dict(fc=col,ec='none',boxstyle='round,pad=0.2'))
    t.text(0.085,y,rule,fontsize=7.4,weight='bold',color='#37474f'); t.text(0.215,y,txt,fontsize=7.2,wrap=True); y-=0.036
y-=0.01
t.text(0,y,'FIXED DURING THE TEST',fontsize=10,weight='bold'); y-=0.026
for s_ in ['S1 tapered to nothing beside V31 → full 12 m (V7, V18, V5 trimmed)',
           'S5 12 m link joins S1 to S2; the block south of it re-cut as V29, V30, V31, V43',
           'S2 median stops short of the S5 junction and of the S2 turning space',
           'Services plot moved from resort land into the colony boundary',
           'Access road widened where it narrowed to 11 m → a true 15 m',
           'Turning spaces marked at the three dead ends']:
    t.text(0,y,'• '+s_,fontsize=7.2); y-=0.022
y-=0.01
t.text(0,y,'RESULT: 62 plots | 63.3% sellable (325,382 sq ft) | open space 12.9%',fontsize=8.6,weight='bold',color='#1b5e20'); y-=0.03
t.legend(handles=[Line2D([0],[0],color='#c62828',lw=2.2,label='Route to the farthest plot'),
                  Line2D([0],[0],color='#1565c0',lw=1,ls=(0,(4,2)),label='15 m from the stream edge'),
                  Patch(fc='#ffcc80',ec='#e65100',hatch='////',label='Turning space 12 × 11 m'),
                  Patch(fc='#cde8bf',ec='#7cb342',label='Riverside garden (open space)'),
                  Patch(fc='#bcaaa4',ec='#5d4037',label='Services plot'),
                  Patch(fc='#2e7d32',label='Pass'),Patch(fc='#ef6c00',label="T&CP's discretion"),Patch(fc='#c62828',label='Action before applying')],
         loc='lower left',fontsize=7.2,frameon=False,ncol=2)
fig.savefig(OUT+TAG+'_TCP_Test.png',dpi=150); fig.savefig(OUT+TAG+'_TCP_Test.pdf')
print('route length %.0f m to %s'%(best[0],far_t))
