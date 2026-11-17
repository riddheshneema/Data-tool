import json, numpy as np, csv, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Patch, FancyArrow
from shapely import wkt
from shapely.geometry import box, Point, LineString
from shapely.ops import unary_union
import ezdxf
D='/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/plan/'
OUT='/home/user/Data-tool/site_plans/'; os.makedirs(OUT,exist_ok=True)
for f in os.listdir(OUT): os.remove(OUT+f)
L=json.load(open(D+'d3_layout.json')); G=wkt.loads; SQFT=10.7639
C,RS,R,roads,median,green,park=[G(L[k]) for k in ['C','RS','R','roads','median','green','park']]
plots=[(G(s),k,n) for s,k,n in L['plots']]
# order & number: river-front first (R1..), then garden villas (G1..)
plots.sort(key=lambda t:(t[1]!='River-front villa',-round(t[0].centroid.y/25),t[0].centroid.x))
gp=[g for g in getattr(green,'geoms',[green]) if g.area>5]
def place(near,size,avoid=(),maxroad=20):
    best=None
    for g in gp:
        if g.distance(Point(near))>80: continue
        for dx in np.arange(-50,51,2.5):
            for dy in np.arange(-50,51,2.5):
                b=box(near[0]+dx-size[0]/2,near[1]+dy-size[1]/2,near[0]+dx+size[0]/2,near[1]+dy+size[1]/2)
                if g.buffer(0.01).contains(b.buffer(1)) and not any(b.buffer(2).intersects(a) for a in avoid) and b.distance(roads)<maxroad:
                    d=Point(near).distance(b.centroid)
                    if best is None or d<best[0]: best=(d,b)
    return best[1] if best else None
amen={}
amen['Clubhouse + pool']=place((387,-415),(22,16),[],40)
for name,near,size in [('Transformer',(345,-490),(8,8)),
                       ('Overhead tank + tubewell',(270,-410),(12,12)),('STP',(235,-500),(18,14)),('Waste point',(350,-440),(6,5)),
                       ('Gatehouse',(322,-486),(5,5))]:
    b=place(near,size,list(amen.values()))
    if b is not None: amen[name]=b
amen_u=unary_union(list(amen.values()))
green=green.difference(amen_u)
riverpark=park.difference(amen_u)
gardens=green.difference(riverpark.buffer(0.01)).buffer(0)
# ---------------- figure ----------------
fig=plt.figure(figsize=(16.54,11.69)); ax=fig.add_axes([0.01,0.03,0.6,0.94])
def fill(g,**kw):
    for p in getattr(g,'geoms',[g]):
        if p.geom_type=='Polygon' and not p.is_empty:
            x,y=p.exterior.xy; ax.fill(x,y,**kw)
            for h in p.interiors: hx,hy=h.xy; ax.fill(hx,hy,fc='white',ec='none')
fill(R.intersection(box(90,-580,490,-30)),fc='#9fd3f2',ec='#5aa9d6',lw=0.6)
fill(RS,fc='#f6e6c3',ec='#a8781a',lw=1.3)
ax.text(330,-150,'RESORT\n(future planning)\n%.2f acres'%(RS.area/4046.86),ha='center',va='center',fontsize=13,weight='bold',color='#7a5410')
fill(riverpark,fc='#b9dfa6',ec='none'); fill(gardens,fc='#9ccc65',ec='none',alpha=0.9)
# promenade path inside river park
for d in (12,):
    pth=C.intersection(R.buffer(d).exterior)
    for l in getattr(pth,'geoms',[pth]):
        if l.geom_type=='LineString': ax.plot(*l.xy,color='#d7ccc8',lw=2.2,solid_capstyle='round')
fill(roads,fc='#cfcfcf',ec='#9e9e9e',lw=0.5); fill(median,fc='#7cb342',ec='none')
# avenue trees along road edges
rng=np.random.default_rng(3)
for k,v in L['road_polys'].items():
    edge=G(v).buffer(-1.2).boundary
    for l in getattr(edge,'geoms',[edge]):
        for t in np.arange(0,l.length,9):
            p=l.interpolate(t)
            if C.buffer(-1).contains(p) and not any(q[0].buffer(0.5).contains(p) for q in plots):
                ax.add_patch(plt.Circle((p.x,p.y),1.9,fc='#558b2f',ec='#33691e',lw=0.3,alpha=0.85))
ml=median.boundary
for t in np.arange(0,ml.length,7):
    p=ml.interpolate(t); ax.add_patch(plt.Circle((p.x,p.y),1.6,fc='#33691e',ec='none',alpha=0.8))
# scattered trees in gardens / river park
for g in getattr(green,'geoms',[green]):
    if g.area<60: continue
    n=int(g.area/180)
    minx,miny,maxx,maxy=g.bounds
    for _ in range(n*4):
        x,y=rng.uniform(minx,maxx),rng.uniform(miny,maxy)
        if g.buffer(-2).contains(Point(x,y)): ax.add_patch(plt.Circle((x,y),rng.uniform(1.6,2.6),fc='#689f38',ec='#33691e',lw=0.3,alpha=0.75)); n-=1
        if n<=0: break
rows=[]
for i,(p,k,n) in enumerate(plots):
    tag=('R%d' if k=='River-front villa' else 'G%d')%(i+1 if k=='River-front villa' else i+1-sum(1 for q in plots if q[1]=='River-front villa'))
    a=p.area*SQFT; rows.append((tag,k,round(a),round(p.area,1),n))
    fill(p,fc='#fff8e1' if k=='River-front villa' else '#ffffff',ec='#b71c1c',lw=0.7)
    ax.text(p.centroid.x,p.centroid.y,f'{tag}\n{a:,.0f}',fontsize=4.8,ha='center',va='center')
acol={'Clubhouse + pool':'#ce93d8','Transformer':'#ffd54f','Overhead tank + tubewell':'#81d4fa','STP':'#a1887f','Waste point':'#e0e0e0','Gatehouse':'#90a4ae'}
for k,v in amen.items():
    fill(v,fc=acol[k],ec='k',lw=0.6)
    ax.annotate(k,v.centroid.coords[0],xytext=(10,-12),textcoords='offset points',fontsize=5.8,arrowprops=dict(arrowstyle='-',lw=0.4))
fill(C,fc='none',ec='#1b5e20',lw=1.5)
ax.annotate('MAIN ENTRY\nfrom approach road',(336,-488),xytext=(352,-566),fontsize=7.5,weight='bold',arrowprops=dict(arrowstyle='->',lw=1))
ax.text(150,-290,'RIVER',color='#1f5f8b',fontsize=10,rotation=68,weight='bold')
ax.text(168,-410,'RIVERSIDE PROMENADE PARK',color='#33691e',fontsize=6.5,rotation=-40)
ax.set_aspect('equal'); ax.set_xlim(95,480); ax.set_ylim(-575,-40); ax.axis('off')
ax.add_patch(FancyArrow(458,-525,0,28,width=4,head_width=12,head_length=9,color='k')); ax.text(458,-478,'N',ha='center',fontsize=12,weight='bold')
ax.plot([110,160],[-568,-568],'k',lw=3); ax.text(135,-563,'50 m',ha='center',fontsize=7)
# ---------------- statement ----------------
A=dict(prem=sum(r[3] for r in rows if r[1]=='River-front villa'),gv=sum(r[3] for r in rows if r[1]=='Garden villa'),
       roads=roads.area,park=riverpark.area,gardens=gardens.area,club=amen.get('Clubhouse + pool',box(0,0,0,0)).area,
       util=amen_u.area-amen.get('Clubhouse + pool',box(0,0,0,0)).area)
tot=C.area; npr=sum(1 for r in rows if r[1]=='River-front villa'); ngv=len(rows)-npr
st=[('River-front villa plots',npr,A['prem']),('Garden villa plots',ngv,A['gv']),('Roads (boulevard, avenue, drive, lanes)','',A['roads']),
    ('Riverside promenade park (25 m)','',A['park']),('Pocket gardens, garden spines, central lawn','',A['gardens']),
    ('Clubhouse + pool','',A['club']),('Utilities (transformer, tank, STP, waste, gate)','',A['util'])]
t=fig.add_axes([0.63,0.03,0.36,0.94]); t.axis('off')
t.text(0,0.99,'RIVER GARDEN VILLAS – CONCEPT MASTER PLAN',fontsize=13.5,weight='bold')
t.text(0,0.968,'Colony (south half) + resort parcel (north half) | Survey Drg SU/10/01, total 23.325 acres',fontsize=7.6)
y=0.935; t.text(0,y,'AREA STATEMENT – COLONY',fontsize=10,weight='bold'); y-=0.024
xs=[0,0.60,0.68,0.84,0.94]
for x,h in zip(xs,['Use','No.','sq ft','acre','%']): t.text(x,y,h,fontsize=7.6,weight='bold')
y-=0.02
for n,c,a in st:
    for x,v in zip(xs,[n,str(c),f'{a*SQFT:,.0f}',f'{a/4046.86:.2f}',f'{100*a/tot:.1f}']): t.text(x,y,v,fontsize=7.2)
    y-=0.019
for x,v in zip(xs,['Total colony','',f'{tot*SQFT:,.0f}',f'{tot/4046.86:.2f}','100']): t.text(x,y,v,fontsize=7.6,weight='bold')
y-=0.02; t.text(0,y,f'Resort parcel: {RS.area*SQFT:,.0f} sq ft = {RS.area/4046.86:.2f} acres',fontsize=7.6,weight='bold')
pa=[r[2] for r in rows if r[1]=='River-front villa']; ga=[r[2] for r in rows if r[1]=='Garden villa']
y-=0.035; t.text(0,y,'PLOT MIX',fontsize=10,weight='bold'); y-=0.021
t.text(0,y,f'River-front villas R1–R{npr}: {min(pa):,}–{max(pa):,} sq ft (avg {np.mean(pa):,.0f}), front the river drive, back onto the river park',fontsize=7); y-=0.018
t.text(0,y,f'Garden villas: {min(ga):,}–{max(ga):,} sq ft (avg {np.mean(ga):,.0f}), every plot fronts a road and sides/backs onto a garden',fontsize=7); y-=0.035
t.text(0,y,'ROADS',fontsize=10,weight='bold'); y-=0.021
for s_ in ['Entry boulevard 24 m: 2 x 6 m carriageway + 6 m garden median + 3 m tree verges',
           'Resort avenue 15 m: 9 m carriageway + 3 m tree verges – continues into the resort',
           'River drive, south link, lanes 13 m: 9 m carriageway + 2 m green verges',
           'All exceed BVN 2012 Rule 38 (9 m up to 250 m length, 12 m up to 400 m)']:
    t.text(0,y,s_,fontsize=7); y-=0.018
y-=0.017; t.text(0,y,'DESIGN IDEAS',fontsize=10,weight='bold'); y-=0.021
for s_ in ['Gardens sit between plots, not inside them: a pocket garden after every 2 river villas',
           '   (view corridors to the river) and every 3 garden villas; an 8 m garden spine behind rows',
           'Continuous riverside promenade (25 m wide) with walking path, linking colony to resort',
           'Tree-lined roads with green verges and a garden median make every street read wider',
           'Clubhouse and central lawn at the heart; open space far above the 10% BVN minimum']:
    t.text(0,y,s_,fontsize=7); y-=0.018
y-=0.017; t.text(0,y,'TO CONFIRM BEFORE APPROVAL',fontsize=10,weight='bold',color='#b71c1c'); y-=0.021
for s_ in ['River identity + HFL: if this is the Narmada, the 300 m rule leaves no buildable land',
           'EWS/LIG 6% of saleable area (2014 rules): on-site pocket or within 2 km (colonies > 2 ha)',
           '25% of developed plots mortgaged to the Collector until completion',
           'Planning-area status and land use (T&CP); resort needs commercial use permission',
           'Drawing scale calibrated to surveyed areas (~1:858); redraw on CAD survey by an architect',
           'Concept for discussion only – not an approved drawing']:
    t.text(0,y,s_,fontsize=7,color='#b71c1c'); y-=0.018
LG=[Patch(fc='#fff8e1',ec='#b71c1c',label='River-front villa plot'),Patch(fc='white',ec='#b71c1c',label='Garden villa plot'),
    Patch(fc='#cfcfcf',ec='#9e9e9e',label='Road'),Patch(fc='#9ccc65',label='Gardens / central lawn'),Patch(fc='#b9dfa6',label='Riverside promenade park'),
    Patch(fc='#f6e6c3',ec='#a8781a',label='Resort parcel'),Patch(fc='#9fd3f2',label='River')]
t.legend(handles=LG,loc='lower left',fontsize=7.4,frameon=False,ncol=2)
fig.savefig(OUT+'River_Garden_Villas_Master_Plan.pdf'); fig.savefig(OUT+'River_Garden_Villas_Master_Plan.png',dpi=140)
with open(OUT+'Plot_Schedule.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['Plot','Type','Area (sq ft)','Area (sq m)','Fronts on'])
    for r in rows: w.writerow(r)
doc=ezdxf.new('R2010'); msp=doc.modelspace()
for n,c in [('RESORT',2),('COLONY',3),('ROADS',8),('PLOTS',1),('GARDENS',82),('RIVER_PARK',62),('AMENITIES',6),('TEXT',7)]: doc.layers.add(n,color=c)
def poly(g,layer):
    for p in getattr(g,'geoms',[g]):
        if p.geom_type=='Polygon' and not p.is_empty: msp.add_lwpolyline(list(p.exterior.coords),close=True,dxfattribs={'layer':layer})
poly(RS,'RESORT'); poly(C,'COLONY'); poly(roads,'ROADS'); poly(gardens,'GARDENS'); poly(riverpark,'RIVER_PARK')
for (p,k,n),r in zip(plots,rows): poly(p,'PLOTS'); msp.add_text(f'{r[0]} {r[2]} sqft',height=1.6,dxfattribs={'layer':'TEXT'}).set_placement(p.centroid.coords[0])
for k,v in amen.items(): poly(v,'AMENITIES'); msp.add_text(k,height=1.6,dxfattribs={'layer':'TEXT'}).set_placement(v.centroid.coords[0])
doc.saveas(OUT+'River_Garden_Villas_Master_Plan.dxf')
print('placed',list(amen)); 
for n,c,a in st: print(f'{n:48s} {str(c):>3s} {a*SQFT:10,.0f} sqft {100*a/tot:5.1f}%')
print('plots',len(rows),'saleable %.1f%%'%(100*(A['prem']+A['gv'])/tot))
