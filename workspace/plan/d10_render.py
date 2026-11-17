import json, sys, os, csv, warnings
import numpy as np
warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Patch, FancyArrow
from shapely import wkt, maximum_inscribed_circle
from shapely.geometry import box, Point
from shapely.ops import unary_union
import ezdxf
D='/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/plan/'
sys.path.insert(0,D); import d10
OUT='/home/user/Data-tool/site_plans/'; os.makedirs(OUT,exist_ok=True)
args=json.loads(sys.argv[1]); TAG=sys.argv[2]; TITLE=sys.argv[3]
OPT=args['option']
r=d10.plan(args['th'],args['y0'],args['pw'],args['pd'],OPT,return_geom=True); g=r['geom']
G=wkt.loads; SQFT=10.7639; ACRE=4046.86
C,RS,R,roads,row,gard,rpark,access=[G(g[k]) for k in ('C','RESORT','R','roads','row','gardens','river_park','access')]
park=G(g['park']) if g.get('park') else None
plots=[[G(s),k] for s,k in g['plots']]
front=lambda p:p.buffer(0.8).intersection(row).area/0.8
def too_irregular(p,k):
    if k=='River-front villa': return False
    n=len(p.simplify(0.6).exterior.coords)-1
    return n>6 or p.area/p.minimum_rotated_rectangle.area<0.70
dropped_odd=[p for p,k in plots if too_irregular(p,k)]
plots=[[p,k] for p,k in plots if not too_irregular(p,k)]
# merge any plot without road frontage into the neighbour it shares the longest edge with
changed=True
while changed:
    changed=False
    for i,(p,k) in enumerate(plots):
        if front(p)<8:
            nb=[(p.buffer(0.3).intersection(q).area,j) for j,(q,_) in enumerate(plots) if j!=i]
            j=max(nb)[1]; plots[j][0]=unary_union([p,plots[j][0]]).buffer(0.01).buffer(-0.01); plots.pop(i); changed=True; break
plotu=unary_union([p for p,_ in plots])
left=C.difference(roads).difference(gard).difference(rpark).difference(plotu)
if park is not None: left=left.difference(park)
left=left.buffer(-0.2).buffer(0.2)
def park_test(p):
    mrr=p.minimum_rotated_rectangle; c=list(mrr.exterior.coords)
    L=max(Point(c[0]).distance(Point(c[1])),Point(c[1]).distance(Point(c[2]))); w=p.area/L
    return p.area>=450 and w>=7.5 and (w>=24 or L<=2.5*w)
pieces=[p for p in getattr(left,'geoms',[left]) if p.geom_type=='Polygon' and p.area>15]
# utilities go into corners that are too small to count as parks; fall back to the smallest park
util={}
GATE=Point(331,-262)
riverplots=unary_union([p for p,k in plots if k=='River-front villa'])
def fits(p,need):
    return maximum_inscribed_circle(p).length>=need
for name,size,score in [('STP (sewage treatment)',(12,10),lambda p:-p.distance(riverplots)),
                        ('Overhead tank + tubewell',(8,8),lambda p:p.distance(GATE)),
                        ('Waste point',(5,4),lambda p:p.distance(GATE))]:
    need=np.hypot(*size)/2*0.95
    cands=[p for p in pieces if fits(p,need) and not any(p.intersects(u) for u in util.values())]
    cands.sort(key=lambda p:(park_test(p),score(p)))   # corners that fail the park test first
    if not cands: continue
    p=cands[0]
    if name.startswith('STP'):
        pick=min([p for p in cands if not park_test(p)] or cands,key=score); p=pick
    mic=maximum_inscribed_circle(p); x,y=mic.coords[0]
    util[name]=box(x-size[0]/2,y-size[1]/2,x+size[0]/2,y+size[1]/2).intersection(p)
uu=unary_union(list(util.values())) if util else box(0,0,0,0)
rest=left.difference(uu).buffer(-0.1).buffer(0.1)
rp=[p for p in getattr(rest,'geoms',[rest]) if p.geom_type=='Polygon' and p.area>5]
parks=unary_union([p for p in rp if park_test(p)]) if any(park_test(p) for p in rp) else box(0,0,0,0)
corners=unary_union([p for p in rp if not park_test(p)]) if rp else box(0,0,0,0)
boul=G(r['boul'])
big_green=unary_union([p for p in getattr(corners,'geoms',[corners]) if p.geom_type=='Polygon' and p.area>=150]) if not corners.is_empty else box(0,0,0,0)
parks_any=unary_union([x for x in [parks,park,big_green] if x is not None and not x.is_empty])
def other_view(p,k):
    if k=='River-front villa' and p.distance(rpark)<1.0: return True
    return (not parks_any.is_empty) and p.distance(parks_any)<=13.0
keep=[]
for (j,sw,mw) in r['per_street']:
    if j not in r['gs']: continue
    st=G(sw); med=gard.intersection(st.buffer(0.5)).difference(boul.buffer(2))
    for p,k in plots:
        if p.buffer(0.8).intersection(st).area>8 and not other_view(p,k):
            keep.append(med.intersection(p.buffer(9)))
medians=unary_union([x for x in keep if not x.is_empty]).buffer(0) if keep else box(0,0,0,0)
roads=unary_union([roads,gard.difference(medians)]).buffer(0)
gard=medians
# number plots: river-front first, then villas, top to bottom
plots.sort(key=lambda t:(t[1]!='River-front villa',-round(t[0].centroid.y/30),t[0].centroid.x))
parks_all=unary_union([x for x in [parks,park,big_green] if x is not None and not x.is_empty])
def faces(p,k):
    if k=='River-front villa' and p.distance(rpark)<1.0: return 'river promenade'
    if not gard.is_empty and p.distance(gard)<=5.5: return 'garden median'
    if not parks_all.is_empty and p.distance(parks_all)<=13.0: return 'park / landscaped green'
    return ''
# ---------------- drawing ----------------
fig=plt.figure(figsize=(16.54,11.69)); ax=fig.add_axes([0.01,0.03,0.6,0.94])
def fill(gm,**kw):
    for p in getattr(gm,'geoms',[gm]):
        if p.geom_type=='Polygon' and not p.is_empty:
            x,y=p.exterior.xy; ax.fill(x,y,**kw)
            for h in p.interiors: hx,hy=h.xy; ax.fill(hx,hy,fc='white',ec='none')
fill(R.intersection(box(90,-580,490,-30)),fc='#9fd3f2',ec='#5aa9d6',lw=0.6)
fill(RS,fc='#f6e6c3',ec='#a8781a',lw=1.3); fill(access,fc='#d0d0d0',ec='#9e9e9e',lw=0.5)
ax.text(255,-400,'RESORT\n(front, by the main entry)\n%.2f acres'%(RS.area/ACRE),ha='center',va='center',fontsize=12,weight='bold',color='#7a5410')
ax.text(318,-380,'PUBLIC ACCESS ROAD 15 m (through resort)',rotation=90,fontsize=6.3,ha='center',va='center')
fill(roads,fc='#d0d0d0',ec='#9e9e9e',lw=0.4)
fill(rpark,fc='#b9dfa6')
pth=C.intersection(R.buffer(8).exterior)
for l in getattr(pth,'geoms',[pth]):
    if l.geom_type=='LineString': ax.plot(*l.xy,color='#d7ccc8',lw=2,solid_capstyle='round')
fill(corners,fc='#c5e1a5'); fill(parks,fc='#7cb342')
if park is not None:
    fill(park,fc='#558b2f',ec='#33691e',lw=0.8)
    ax.text(park.representative_point().x,park.representative_point().y,'CENTRAL\nPARK\n%d m²'%park.area,ha='center',va='center',fontsize=7,weight='bold',color='white')
fill(gard,fc='#2e7d32')
# trees: medians, promenade, avenue trees in river-drive verges, parks
def trees(gm,step,rad,col='#558b2f',inset=0.9):
    for p in getattr(gm,'geoms',[gm]):
        if p.geom_type!='Polygon' or p.area<15: continue
        sk=p.buffer(-inset)
        if sk.is_empty: sk=p
        for e in getattr(sk.boundary,'geoms',[sk.boundary]):
            for t in np.arange(0,e.length,step):
                q=e.interpolate(t); ax.add_patch(plt.Circle((q.x,q.y),rad,fc=col,ec='#33691e',lw=0.3,alpha=0.85))
trees(gard,6,1.2,'#33691e',0.3); trees(rpark,10,2.1); trees(parks,8,1.8)
if park is not None: trees(park,7,1.9,'#33691e')
drive=G(r['drive']) if r.get('drive') else None
rows=[];nr=0;nv=0;gfc=0
for p,k in plots:
    if k=='River-front villa': nr+=1; tag=f'R{nr}'
    else: nv+=1; tag=f'V{nv}'
    a=p.area*SQFT; f=faces(p,k); gfc+=bool(f)
    rows.append((tag,k,round(a),round(p.area,1),round(front(p),1),'Yes' if f else 'No',f))
    fill(p,fc='#fff3d6' if k=='River-front villa' else '#ffffff',ec='#b71c1c',lw=0.7)
    ax.text(p.centroid.x,p.centroid.y,f'{tag}\n{a:,.0f}',fontsize=4.6,ha='center',va='center',color='k' if f else '#b71c1c')
ucol={'STP (sewage treatment)':'#a1887f','Overhead tank + tubewell':'#81d4fa','Waste point':'#e0e0e0'}
for k,v in util.items():
    fill(v,fc=ucol[k],ec='k',lw=0.5); ax.text(v.centroid.x,v.centroid.y,{'STP (sewage treatment)':'STP','Overhead tank + tubewell':'OHT','Waste point':'W'}[k],fontsize=4.6,ha='center',va='center',weight='bold')
ax.plot(337.5,-266,marker='s',ms=4,mfc='#ffd54f',mec='k'); ax.annotate('Transformer (pole-mounted)',(337.5,-266),xytext=(350,-282),fontsize=5.5,arrowprops=dict(arrowstyle='-',lw=0.4))
fill(C,fc='none',ec='#1b5e20',lw=1.5)
# road labels
has_med={j:(G(sw).buffer(0.5).intersection(gard).area>20) for (j,sw,mw) in r['per_street']}
for rk,i in enumerate(r['ids'],start=1):
    if rk>4: break
    w=12 if i in r['gs'] else 9
    gtxt=' + garden' if has_med.get(i) else ''
    for (j,s,m) in r['per_street']:
        if j==i:
            gs_=G(s); top=max(gs_.exterior.coords if gs_.geom_type=='Polygon' else max(gs_.geoms,key=lambda q:q.area).exterior.coords,key=lambda q:q[1])
            c=gs_.intersection(box(top[0]-15,top[1]-30,top[0]+15,top[1]-6)).representative_point()
            if c.is_empty: c=gs_.representative_point()
            ax.text(c.x,c.y,f'S{rk}\n{w} m{gtxt}',fontsize=5.6,ha='center',va='center',weight='bold',color='#263238',
                    bbox=dict(fc='white',ec='#607d8b',lw=0.4,alpha=0.85,boxstyle='round,pad=0.15'))
if drive is not None:
    c=max(getattr(drive,'geoms',[drive]),key=lambda x:x.area).intersection(box(290,-110,340,-70)).representative_point()
    ax.text(c.x,c.y,'RD – river drive 12 m',fontsize=5.6,ha='center',va='center',weight='bold',color='#263238',
            bbox=dict(fc='white',ec='#607d8b',lw=0.4,alpha=0.85,boxstyle='round,pad=0.15'))
ax.text(150,-118,'RIVERSIDE PROMENADE GARDEN (15 m)',color='#33691e',fontsize=7,rotation=52,weight='bold')
ax.annotate('MAIN ENTRY',(336,-487),xytext=(345,-566),fontsize=7.5,weight='bold',arrowprops=dict(arrowstyle='->',lw=1))
ax.annotate('COLONY GATE\n12 m entry road',(331,-262),xytext=(360,-305),fontsize=7.2,weight='bold',arrowprops=dict(arrowstyle='->',lw=1))
ax.text(118,-60,'RIVER',color='#1f5f8b',fontsize=10,weight='bold')
ax.set_aspect('equal'); ax.set_xlim(95,480); ax.set_ylim(-575,-40); ax.axis('off')
ax.add_patch(FancyArrow(458,-525,0,28,width=4,head_width=12,head_length=9,color='k')); ax.text(458,-478,'N',ha='center',fontsize=12,weight='bold')
ax.plot([110,160],[-568,-568],'k',lw=3); ax.text(135,-563,'50 m',ha='center',fontsize=7)
# ---------------- statement ----------------
T=C.area
pr=sum(x[3] for x in rows if x[1]=='River-front villa'); pv=sum(x[3] for x in rows if x[1]!='River-front villa'); sale=pr+pv
A=[('River-front villa plots',nr,pr),('Villa plots',nv,pv),
   ('Roads – carriageway and verges','',roads.area),('Garden medians (part of road land)','',gard.area),
   ('Riverside promenade garden (15 m river setback)','',rpark.area)]
if park is not None: A.append(('Central park (triangle block)','',park.area))
A+=[('Other parks that meet the open-space test','',parks.area),('Landscaped corners (too small to count as park)','',corners.area),
    ('Utilities (STP, tank + tubewell, waste point)','',uu.area)]
os_parks=parks.area+(park.area if park is not None else 0)
t=fig.add_axes([0.63,0.03,0.36,0.94]); t.axis('off')
t.text(0,0.99,TITLE,fontsize=13,weight='bold')
t.text(0,0.968,'Colony at the back (river bend) + resort at the front (main entry) | Survey Drg SU/10/01, 23.325 acres',fontsize=7.4)
y=0.935; t.text(0,y,'AREA STATEMENT – COLONY',fontsize=10,weight='bold'); y-=0.024
xs=[0,0.62,0.69,0.84,0.94]
for x,h in zip(xs,['Use','No.','sq ft','acre','%']): t.text(x,y,h,fontsize=7.5,weight='bold')
y-=0.02
for n,c,a in A:
    for x,v in zip(xs,[n,str(c),f'{a*SQFT:,.0f}',f'{a/ACRE:.2f}',f'{100*a/T:.1f}']): t.text(x,y,v,fontsize=7.0)
    y-=0.0185
for x,v in zip(xs,['Total colony','',f'{T*SQFT:,.0f}',f'{T/ACRE:.2f}','100']): t.text(x,y,v,fontsize=7.5,weight='bold')
y-=0.022; t.text(0,y,f'SELLABLE: {sale*SQFT:,.0f} sq ft = {sale/ACRE:.2f} acres = {100*sale/T:.1f}% of colony  ({len(rows)} plots)',fontsize=8.6,weight='bold',color='#1b5e20')
y-=0.02; t.text(0,y,f'OPEN SPACE meeting the BVN test (parks): {100*os_parks/T:.1f}%  |  with promenade garden: {100*(os_parks+rpark.area)/T:.1f}%  (minimum 10%)',fontsize=7.3,weight='bold')
y-=0.019; t.text(0,y,f'GARDEN VIEW: {gfc} of {len(rows)} plots face the river promenade, a garden median or a park',fontsize=7.3,weight='bold')
y-=0.019; t.text(0,y,f'Resort: {RS.area/ACRE:.2f} acres, incl. the 15 m public access road (~{access.area/ACRE:.2f} acre) to be dedicated as a public road',fontsize=7.0)
pa=[x[2] for x in rows if x[1]=='River-front villa']; va=[x[2] for x in rows if x[1]!='River-front villa']
y-=0.032; t.text(0,y,'PLOT MIX',fontsize=10,weight='bold'); y-=0.02
t.text(0,y,f'{nr} river-front plots {min(pa):,}–{max(pa):,} sq ft (avg {np.mean(pa):,.0f}), backing onto the promenade garden',fontsize=7); y-=0.0175
t.text(0,y,f'{nv} villa plots {min(va):,}–{max(va):,} sq ft (avg {np.mean(va):,.0f}), typical {args["pw"]} x {args["pd"]} ft; no clubhouse',fontsize=7); y-=0.0175
t.text(0,y,'Every plot has direct road frontage and a regular shape (plot numbers in red = no garden view)',fontsize=7); y-=0.03
t.text(0,y,'ROADS',fontsize=10,weight='bold'); y-=0.02
gnames=', '.join(f'S{rk}' for rk,i in enumerate(r['ids'],start=1) if i in r['gs'] and has_med.get(i))
for s_ in ['Public access road 15 m: main entry → through the resort → colony gate',
           'Gate entry road 12 m, plain (no plots on one side, so no median)',
           'RD river drive 12 m, plain, avenue trees in the verges (~400 m long → 12 m under BVN Rule 38)',
           f'Garden streets {gnames}: 12 m = 4.5 m lane + 3 m garden median + 4.5 m lane',
           'All other streets 9 m, plain']:
    t.text(0,y,s_,fontsize=7); y-=0.0175
y-=0.012; t.text(0,y,'DESIGN LOGIC',fontsize=10,weight='bold'); y-=0.02
logic=['River-front plots back onto the riverside promenade garden – no median needed in front of them',
       'A garden median runs only where it gives a plot its garden view – none at the gate entry, none on RD or S1']
logic+=(['Triangle block is the central park (counts as open space); the S4 plots face it, so S4 is a plain 9 m street'] if park is not None
        else ['S3 and S4 carry medians along the V1–V42 and V8–V37 lines'])
logic+=['Clubhouse and pool removed – they belong in the resort',
        'Utilities only in corners too small to count as parks; transformer pole-mounted at the gate']
for s_ in logic: t.text(0,y,s_,fontsize=7); y-=0.0175
y-=0.012; t.text(0,y,'TO CONFIRM BEFORE APPROVAL',fontsize=10,weight='bold',color='#b71c1c'); y-=0.02
conf=['River identity + HFL: if this is the Narmada, the 300 m rule leaves no buildable land',
      (f'Open space: parks give {100*os_parks/T:.1f}% – T&CP must accept the promenade garden to reach 10%' if os_parks<0.1*T
       else f'Open space: parks alone give {100*os_parks/T:.1f}% – meets 10% without the promenade'),
      'RD could be 9 m if T&CP measures road length between junctions (≈ +2% sellable)',
      'EWS/LIG by shelter fee (no land) – confirm in-lieu option under the 2014 rural rules',
      'Scale calibrated to surveyed areas (~1:858); architect to redraw on the CAD survey',
      'Concept for discussion only – not an approved drawing']
for s_ in conf: t.text(0,y,s_,fontsize=7,color='#b71c1c'); y-=0.0175
LG=[Patch(fc='#fff3d6',ec='#b71c1c',label='River-front plot'),Patch(fc='white',ec='#b71c1c',label='Villa plot'),
    Patch(fc='#d0d0d0',ec='#9e9e9e',label='Road'),Patch(fc='#2e7d32',label='Garden median (road land)'),
    Patch(fc='#b9dfa6',label='Riverside promenade garden'),Patch(fc='#558b2f',label='Park (counts as open space)'),
    Patch(fc='#c5e1a5',label='Landscaped corner'),Patch(fc='#ffffff',ec='#999',label='STP / OHT / W = sewage plant, water tank + tubewell, waste point'),Patch(fc='#f6e6c3',ec='#a8781a',label='Resort')]
t.legend(handles=LG,loc='lower left',fontsize=7.2,frameon=False,ncol=2)
fig.savefig(OUT+TAG+'.pdf'); fig.savefig(OUT+TAG+'.png',dpi=140)
with open(OUT+TAG+'_Plot_Schedule.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['Plot','Type','Area (sq ft)','Area (sq m)','Road frontage (m)','Garden view','Faces'])
    for x in rows: w.writerow(x)
doc=ezdxf.new('R2010'); msp=doc.modelspace()
for n,c in [('RESORT',2),('COLONY',3),('ROADS',8),('MEDIANS',94),('PLOTS',1),('PARKS',82),('PROMENADE',62),('CORNERS',52),('UTILITIES',6),('TEXT',7)]: doc.layers.add(n,color=c)
def poly(gm,layer):
    for p in getattr(gm,'geoms',[gm]):
        if p.geom_type=='Polygon' and not p.is_empty: msp.add_lwpolyline(list(p.exterior.coords),close=True,dxfattribs={'layer':layer})
poly(RS,'RESORT'); poly(C,'COLONY'); poly(roads,'ROADS'); poly(gard,'MEDIANS'); poly(rpark,'PROMENADE'); poly(parks,'PARKS'); poly(corners,'CORNERS')
if park is not None: poly(park,'PARKS')
for (p,k),x in zip(plots,rows): poly(p,'PLOTS'); msp.add_text(f'{x[0]} {x[2]} sqft',height=1.6,dxfattribs={'layer':'TEXT'}).set_placement(p.centroid.coords[0])
for k,v in util.items(): poly(v,'UTILITIES')
doc.saveas(OUT+TAG+'.dxf')
print(f'{TAG}: {len(rows)} plots, sellable {100*sale/T:.1f}%, parks {100*os_parks/T:.1f}%, +promenade {100*(os_parks+rpark.area)/T:.1f}%, garden view {gfc}/{len(rows)}, medians {100*gard.area/T:.1f}%, utilities placed {list(util)}')
