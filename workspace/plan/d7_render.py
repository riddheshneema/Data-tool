import json, numpy as np, csv, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Patch, FancyArrow
from shapely import wkt, maximum_inscribed_circle
from shapely.geometry import box, Point
from shapely.ops import unary_union
import ezdxf
D='/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/plan/'
OUT='/home/user/Data-tool/site_plans/'; os.makedirs(OUT,exist_ok=True)
import sys; sys.path.insert(0,D); import d7
args=json.loads(sys.argv[1]); TAG=sys.argv[2]; TITLE=sys.argv[3]
res=d7.design(args['th'],args['y0'],args['pw'],args['pd'],args['style'],args['LG'],return_geom=True); g_=res['geom']
G=wkt.loads; SQFT=10.7639
C,RS,R,roads,row,rpark,garden=[G(g_[k]) for k in ['C','RESORT','R','roads','row','gardens','river_park']][0:7]
C,RS,R,roads,row,garden,rpark=G(g_['C']),G(g_['RESORT']),G(g_['R']),G(g_['roads']),G(g_['row']),G(g_['gardens']),G(g_['river_park'])
access=G(g_['access'])
plots=[[G(s),k] for s,k in g_['plots']]
left=C.difference(roads).difference(garden).difference(rpark).difference(unary_union([p for p,_ in plots])).buffer(0)
front=lambda p:p.buffer(0.8).intersection(row).area/0.8
# 1. merge any plot without frontage into the neighbour it shares the longest edge with
changed=True
while changed:
    changed=False
    for i,(p,k) in enumerate(plots):
        if front(p)<8:
            nb=[(p.buffer(0.3).intersection(q).area,j) for j,(q,_) in enumerate(plots) if j!=i]
            j=max(nb)[1]; plots[j][0]=unary_union([p,plots[j][0]]).buffer(0.01).buffer(-0.01); plots.pop(i); changed=True; break
# 2. clubhouse on the plot nearest the entry, east of the boulevard
GATEP=Point(331,-262)
cand=[(p.centroid.distance(GATEP),i) for i,(p,k) in enumerate(plots) if k!='River-front villa']
ci=min(cand)[1]; club=plots.pop(ci)[0]
# 3. utilities in leftover corners (largest inscribed circles)
lp=sorted([g for g in getattr(left,'geoms',[left]) if g.area>40],key=lambda g:-maximum_inscribed_circle(g).length)
util={}
names=['STP (sewage treatment)','Overhead tank + tubewell','Transformer','Waste point']
for nm,g in zip(names,lp):
    c=maximum_inscribed_circle(g); r=min(c.length*0.9,9); x,y=c.coords[0]
    util[nm]=box(x-r,y-r,x+r,y+r).intersection(g)
gate=box(325,-268,337,-262).intersection(row)
uu=unary_union(list(util.values()))
pocket=left.difference(uu)
# number plots: river-front first, top to bottom
plots.sort(key=lambda t:(t[1]!='River-front villa',-round(t[0].centroid.y/30),t[0].centroid.x))
# ---------------- figure ----------------
fig=plt.figure(figsize=(16.54,11.69)); ax=fig.add_axes([0.01,0.03,0.6,0.94])
def fill(g,**kw):
    for p in getattr(g,'geoms',[g]):
        if p.geom_type=='Polygon' and not p.is_empty:
            x,y=p.exterior.xy; ax.fill(x,y,**kw)
            for h in p.interiors: hx,hy=h.xy; ax.fill(hx,hy,fc='white',ec='none')
fill(R.intersection(box(90,-580,490,-30)),fc='#9fd3f2',ec='#5aa9d6',lw=0.6)
fill(RS,fc='#f6e6c3',ec='#a8781a',lw=1.3)
ax.text(260,-400,'RESORT\n(front, by the main entry)\n%.2f acres'%(RS.area/4046.86),ha='center',va='center',fontsize=12,weight='bold',color='#7a5410')
fill(access,fc='#d0d0d0',ec='#9e9e9e',lw=0.5)
ax.text(318,-380,'COLONY ACCESS ROAD 15 m (through resort)',rotation=90,fontsize=6.5,ha='center',va='center')
fill(rpark,fc='#b9dfa6'); fill(garden,fc='#7cb342'); fill(pocket,fc='#9ccc65')
pth=C.intersection(R.buffer(8).exterior)
for l in getattr(pth,'geoms',[pth]):
    if l.geom_type=='LineString': ax.plot(*l.xy,color='#d7ccc8',lw=2,solid_capstyle='round')
fill(roads,fc='#d0d0d0',ec='#9e9e9e',lw=0.4)
# trees in linear gardens and river park
for g,step,r in [(garden,7,1.7),(rpark,10,2.2)]:
    for p in getattr(g,'geoms',[g]):
        if p.geom_type!='Polygon' or p.area<20: continue
        sk=p.buffer(-1.0)
        for e in getattr(sk.boundary,'geoms',[sk.boundary]) if not sk.is_empty else []:
            for t in np.arange(0,e.length,step):
                q=e.interpolate(t); ax.add_patch(plt.Circle((q.x,q.y),r,fc='#558b2f',ec='#33691e',lw=0.3,alpha=0.8))
rows=[];nr=0;nv=0
for p,k in plots:
    if k=='River-front villa': nr+=1; tag=f'R{nr}'
    else: nv+=1; tag=f'V{nv}'
    a=p.area*SQFT; rows.append((tag,k,round(a),round(p.area,1),round(front(p),1)))
    fill(p,fc='#fff3d6' if k=='River-front villa' else '#ffffff',ec='#b71c1c',lw=0.7)
    ax.text(p.centroid.x,p.centroid.y,f'{tag}\n{a:,.0f}',fontsize=4.6,ha='center',va='center')
fill(club,fc='#ce93d8',ec='k',lw=0.7); ax.text(club.centroid.x,club.centroid.y,'CLUB-\nHOUSE',fontsize=5.5,ha='center',va='center',weight='bold')
ucol={'STP (sewage treatment)':'#a1887f','Overhead tank + tubewell':'#81d4fa','Transformer':'#ffd54f','Waste point':'#e0e0e0'}
for k,v in util.items():
    fill(v,fc=ucol[k],ec='k',lw=0.5); ax.annotate(k,v.centroid.coords[0],xytext=(-40,10),textcoords='offset points',fontsize=5.5,arrowprops=dict(arrowstyle='-',lw=0.4))
fill(gate,fc='#90a4ae',ec='k',lw=0.5)
fill(C,fc='none',ec='#1b5e20',lw=1.5)
ax.annotate('MAIN ENTRY',(336,-487),xytext=(345,-566),fontsize=7.5,weight='bold',arrowprops=dict(arrowstyle='->',lw=1))
ax.annotate('COLONY GATE',(331,-264),xytext=(360,-300),fontsize=7.5,weight='bold',arrowprops=dict(arrowstyle='->',lw=1))
ax.text(140,-120,'RIVER',color='#1f5f8b',fontsize=10,rotation=68,weight='bold')
ax.set_aspect('equal'); ax.set_xlim(95,480); ax.set_ylim(-575,-40); ax.axis('off')
ax.add_patch(FancyArrow(458,-525,0,28,width=4,head_width=12,head_length=9,color='k')); ax.text(458,-478,'N',ha='center',fontsize=12,weight='bold')
ax.plot([110,160],[-568,-568],'k',lw=3); ax.text(135,-563,'50 m',ha='center',fontsize=7)
# ---------------- statement ----------------
T=C.area
A=[('River-front villa plots',nr,sum(r[3] for r in rows if r[1]=='River-front villa')),
   ('Villa plots',nv,sum(r[3] for r in rows if r[1]!='River-front villa')),
   ('Roads (carriageways)','',roads.area),
   ('Riverside promenade (15 m river buffer)','',rpark.area),
   ('Linear gardens (drive garden, avenue verges, median)','',garden.area),
   ('Pocket gardens','',pocket.area),
   ('Clubhouse / community facility','',club.area),
   ('Utilities + gatehouse','',uu.area+gate.area)]
sale=A[0][2]+A[1][2]
t=fig.add_axes([0.63,0.03,0.36,0.94]); t.axis('off')
t.text(0,0.99,TITLE,fontsize=13.5,weight='bold')
t.text(0,0.968,'Colony (back half, river bend) + resort (front half, at the entry) | Survey Drg SU/10/01, 23.325 acres | '+TAG,fontsize=7.6)
y=0.935; t.text(0,y,'AREA STATEMENT – COLONY',fontsize=10,weight='bold'); y-=0.024
xs=[0,0.60,0.68,0.84,0.94]
for x,h in zip(xs,['Use','No.','sq ft','acre','%']): t.text(x,y,h,fontsize=7.6,weight='bold')
y-=0.02
for n,c,a in A:
    for x,v in zip(xs,[n,str(c),f'{a*SQFT:,.0f}',f'{a/4046.86:.2f}',f'{100*a/T:.1f}']): t.text(x,y,v,fontsize=7.2)
    y-=0.019
for x,v in zip(xs,['Total colony','',f'{T*SQFT:,.0f}',f'{T/4046.86:.2f}','100']): t.text(x,y,v,fontsize=7.6,weight='bold')
y-=0.021; t.text(0,y,f'SELLABLE: {sale*SQFT:,.0f} sq ft = {sale/4046.86:.2f} acres = {100*sale/T:.1f}% of colony',fontsize=8.5,weight='bold',color='#1b5e20')
y-=0.019; t.text(0,y,f'Open space: river promenade + gardens = {100*(rpark.area+garden.area+pocket.area)/T:.1f}% (BVN Rule 47(2) minimum 10%)',fontsize=7.4)
y-=0.019; t.text(0,y,f'Resort parcel: {RS.area*SQFT:,.0f} sq ft = {RS.area/4046.86:.2f} acres (not part of the colony sale)',fontsize=7.4)
pa=[r[2] for r in rows if r[1]=='River-front villa']; va=[r[2] for r in rows if r[1]!='River-front villa']
y-=0.035; t.text(0,y,'PLOT MIX',fontsize=10,weight='bold'); y-=0.021
t.text(0,y,f'{nr} river-front villa plots, {min(pa):,}–{max(pa):,} sq ft (avg {np.mean(pa):,.0f}): back onto the river promenade',fontsize=7); y-=0.018
t.text(0,y,f'{nv} villa plots, {min(va):,}–{max(va):,} sq ft (avg {np.mean(va):,.0f}): typical %d x %d ft (%s sq ft)'%(args['pw'],args['pd'],format(args['pw']*args['pd'],',')),fontsize=7); y-=0.018
t.text(0,y,'Every plot has direct frontage on a road right-of-way (checked: 0 without frontage)',fontsize=7); y-=0.035
t.text(0,y,'ROADS',fontsize=10,weight='bold'); y-=0.021
RD=(['Access road 15 m from the main entry, through the resort, to the colony gate',
     'Colony entry boulevard 24 m: 2 x 9 m carriageway + 6 m garden median']+
    (['River drive 9 m + %d m linear garden facing the inner plots'%args['LG'] if args['LG'] else 'River drive 9 m',
      'Internal streets 9 m (BVN 2012 Rule 38: 9 m up to 250 m length)'] if args['style']=='plain' else
     ['Every road divided: 5.5 m + 4 m garden median + 5.5 m = 15 m (garden between the lanes)',
      ('River drive 15 m divided, plus %d m linear garden'%args['LG']) if args['LG'] else 'River drive 15 m divided (garden median)']))
for s_ in RD:
    t.text(0,y,s_,fontsize=7); y-=0.018
y-=0.017; t.text(0,y,'DESIGN LOGIC',fontsize=10,weight='bold'); y-=0.021
for s_ in ['No gardens inside plots – a 5,000 sq ft plot has room for its own garden',
           'River-front plots face the river across a continuous 15 m riverside promenade',
           'Every inner plot faces a garden median in its road' if args['style']=='median' else ('Plots on the river drive face a linear garden across the road' if args['LG'] else 'Plain 9 m streets keep the most land for plots; greenery is in the river promenade'),
           'Internal streets run at an angle that fits the site, so few plots are wasted',
           'Odd corners become pocket gardens or utility sites; clubhouse at the entry']:
    t.text(0,y,s_,fontsize=7); y-=0.018
y-=0.017; t.text(0,y,'TO CONFIRM BEFORE APPROVAL',fontsize=10,weight='bold',color='#b71c1c'); y-=0.021
for s_ in ['River identity + HFL: if this is the Narmada, the 300 m rule leaves no buildable land',
           'T&CP to accept the 15 m river buffer as part of the 10% open space',
           'EWS/LIG: paid as shelter fee (no land) – confirm in-lieu option under 2014 rural rules',
           '25% of developed plots mortgaged to the Collector until completion',
           'Planning-area status and land use (T&CP); resort needs commercial use permission',
           'Scale calibrated to surveyed areas (~1:858); architect to redraw on CAD survey',
           'Concept for discussion only – not an approved drawing']:
    t.text(0,y,s_,fontsize=7,color='#b71c1c'); y-=0.018
LG=[Patch(fc='#fff3d6',ec='#b71c1c',label='River-front villa plot'),Patch(fc='white',ec='#b71c1c',label='Villa plot'),
    Patch(fc='#d0d0d0',ec='#9e9e9e',label='Road'),Patch(fc='#7cb342',label='Linear garden / median'),Patch(fc='#9ccc65',label='Pocket garden'),
    Patch(fc='#b9dfa6',label='Riverside promenade'),Patch(fc='#ce93d8',ec='k',label='Clubhouse'),Patch(fc='#f6e6c3',ec='#a8781a',label='Resort parcel')]
t.legend(handles=LG,loc='lower left',fontsize=7.4,frameon=False,ncol=2)
fig.savefig(OUT+TAG+'_Master_Plan.pdf'); fig.savefig(OUT+TAG+'_Master_Plan.png',dpi=140)
with open(OUT+TAG+'_Plot_Schedule.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['Plot','Type','Area (sq ft)','Area (sq m)','Road frontage (m)'])
    for r in rows: w.writerow(r)
doc=ezdxf.new('R2010'); msp=doc.modelspace()
for n,c in [('RESORT',2),('COLONY',3),('ROADS',8),('PLOTS',1),('GARDENS',82),('RIVER_PROMENADE',62),('AMENITIES',6),('TEXT',7)]: doc.layers.add(n,color=c)
def poly(g,layer):
    for p in getattr(g,'geoms',[g]):
        if p.geom_type=='Polygon' and not p.is_empty: msp.add_lwpolyline(list(p.exterior.coords),close=True,dxfattribs={'layer':layer})
poly(RS,'RESORT'); poly(C,'COLONY'); poly(roads,'ROADS'); poly(garden,'GARDENS'); poly(pocket,'GARDENS'); poly(rpark,'RIVER_PROMENADE')
for (p,k),r in zip(plots,rows): poly(p,'PLOTS'); msp.add_text(f'{r[0]} {r[2]} sqft',height=1.6,dxfattribs={'layer':'TEXT'}).set_placement(p.centroid.coords[0])
poly(club,'AMENITIES')
for k,v in util.items(): poly(v,'AMENITIES')
doc.saveas(OUT+TAG+'_Master_Plan.dxf')
for n,c,a in A: print(f'{n:52s} {str(c):>3s} {a*SQFT:10,.0f} {100*a/T:5.1f}%')
print('SELLABLE %.1f%%  %d plots  min frontage %.1f m'%(100*sale/T,len(rows),min(r[4] for r in rows)))
