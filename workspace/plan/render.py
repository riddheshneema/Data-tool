import json, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Patch, FancyArrow
from shapely import wkt
from shapely.ops import unary_union
import ezdxf
D='/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
OUT='/home/user/Data-tool/site_plans/'
import os; os.makedirs(OUT,exist_ok=True)
F=json.load(open(D+'plan/final.json'))
river=np.load(D+'site/river.npy'); res=0.5
G=lambda s:wkt.loads(s)
colony,resort,green=G(F['colony']),G(F['resort']),G(F['green'])
roads=G(F['roads']).buffer(2.5,join_style=2).buffer(-2.5,join_style=2).intersection(colony.buffer(2.5).buffer(-2.5))
plots=[G(s) for s in F['plots']]; ews=[G(s) for s in F['ews']]; amen={k:G(v) for k,v in F['amen'].items()}
fig=plt.figure(figsize=(16.54,11.69))  # A3 landscape
ax=fig.add_axes([0.02,0.04,0.58,0.92])
ys,xs=np.nonzero(river[::3,::3]); ax.scatter(xs*3*res,-ys*3*res,s=0.6,c='#8ec5e8',marker='s',lw=0)
def fill(g,**kw):
    for p in getattr(g,'geoms',[g]):
        if p.geom_type=='Polygon' and not p.is_empty:
            x,y=p.exterior.xy; ax.fill(x,y,**kw)
            for h in p.interiors: hx,hy=h.xy; ax.fill(hx,hy,fc='white',ec='none')
fill(resort,fc='#f7e7c1',ec='#a8781a',lw=1.4)
ax.text(*resort.representative_point().coords[0],'RESORT / FUTURE DEVELOPMENT\n(premium river-bend land)\n%.2f acres'%(resort.area/4046.86),ha='center',va='center',fontsize=11,weight='bold',color='#7a5410')
fill(green,fc='#cfe8c4',ec='none')
fill(roads,fc='#c9c9c9',ec='#8a8a8a',lw=0.4)
for i,p in enumerate(plots):
    fill(p,fc='white',ec='#b71c1c',lw=0.6); c=p.centroid; ax.text(c.x,c.y,f'P{i+1}',fontsize=4.8,ha='center',va='center')
for i,p in enumerate(ews):
    fill(p,fc='#ffe0b2',ec='#e65100',lw=0.5); c=p.centroid; ax.text(c.x,c.y,f'E{i+1}',fontsize=3.6,ha='center',va='center')
cols={'Transformer':'#ffd54f','Clubhouse':'#ce93d8','Overhead':'#81d4fa','STP':'#a1887f','Waste':'#e0e0e0'}
for k,v in amen.items():
    c=[cl for n,cl in cols.items() if k.startswith(n)][0]; fill(v,fc=c,ec='k',lw=0.5)
    ax.annotate(k.split(' (')[0].split(' /')[0].split(' &')[0],v.centroid.coords[0],xytext=(8,8),textcoords='offset points',fontsize=5.5,arrowprops=dict(arrowstyle='-',lw=0.4))
fill(colony,fc='none',ec='#2e7d32',lw=1.4)
ax.annotate('ENTRY from approach road\n(to Jalkoti / Maheshwar road)',(336,-485),xytext=(360,-560),fontsize=7,arrowprops=dict(arrowstyle='->',lw=0.8))
ax.text(150,-300,'RIVER',color='#2b6c9e',fontsize=9,rotation=70)
ax.set_aspect('equal'); ax.set_xlim(95,480); ax.set_ylim(-575,-40); ax.axis('off')
ax.add_patch(FancyArrow(455,-520,0,30,width=4,head_width=12,head_length=10,color='k')); ax.text(455,-470,'N',ha='center',fontsize=12,weight='bold')
ax.plot([110,160],[-565,-565],'k',lw=3); ax.text(135,-560,'50 m',ha='center',fontsize=7)
# right panel
t=fig.add_axes([0.62,0.04,0.36,0.92]); t.axis('off')
t.text(0,0.985,'CONCEPT LAYOUT – RESIDENTIAL COLONY + RESORT',fontsize=13,weight='bold')
t.text(0,0.96,'Survey: "Maheshwar Dhamnod" survey plan, Drg SU/10/01 (12-02-2023), total 23.325 acres',fontsize=7.5)
A=F['A']; rows=F['rows']; FT2=10.7639
y=0.92; t.text(0,y,'AREA STATEMENT – COLONY (south half)',fontsize=9.5,weight='bold'); y-=0.025
hdr=['Use','No.','sq ft','acre','%']; xs_=[0,0.60,0.68,0.83,0.93]
for x,h in zip(xs_,hdr): t.text(x,y,h,fontsize=7.5,weight='bold')
y-=0.02
for n,c,a in rows:
    for x,v in zip(xs_,[n,str(c),f'{a*FT2:,.0f}',f'{a/4046.86:.2f}',f'{100*a/A["colony"]:.1f}']): t.text(x,y,v,fontsize=7)
    y-=0.019
for x,v in zip(xs_,['Total colony','',f'{A["colony"]*FT2:,.0f}',f'{A["colony"]/4046.86:.2f}','100.0']): t.text(x,y,v,fontsize=7.5,weight='bold')
y-=0.02; t.text(0,y,f'Resort parcel (north half): {A["resort"]*FT2:,.0f} sq ft = {A["resort"]/4046.86:.2f} acres',fontsize=7.5,weight='bold')
y-=0.04
t.text(0,y,'PLANNING BASIS',fontsize=9.5,weight='bold'); y-=0.022
notes=[
'Split: 50% resort (north, river-bend frontage) / 50% colony (south, next to the entry).',
'Plots: 50 x 100 ft (5,000 sq ft) detached – above the 225 sq m BVN minimum.',
'Roads: 12 m main road from the entry, 12 m link to the resort, 9 m internal roads',
'   (BVN 2012 Rule 38: 9 m up to 250 m length, 12 m up to 400 m).',
'Open space: parks + river green buffer = %.1f%% (BVN Rule 47(2) minimum 10%%).'%(100*A['green']/A['colony']),
'EWS/LIG: 16 plots of 25 x 50 ft = %.1f%% of saleable area'%(100*A['ews']/(A['ews']+A['plots'])),
'   (MP Gram Panchayat Colony Rules 2014: 6%, inside colony if < 2 ha).',
'River setback assumed 15 m from the river edge; no plot inside it.',
'Utilities: transformer near entry, overhead tank + tubewell, STP at low point,',
'   waste point; clubhouse/community facility near the entry.',
'25% of developed plots (about 12) will be mortgaged to the Collector until completion.',
]
for n in notes: t.text(0,y,n,fontsize=7.2); y-=0.019
y-=0.02; t.text(0,y,'MUST CONFIRM BEFORE APPROVAL',fontsize=9.5,weight='bold',color='#b71c1c'); y-=0.022
for n in ['Which river this is. If it is the Narmada, the 300 m rule leaves NO buildable land here',
          '   (no part of the site is more than about 180 m from the river).',
          'High flood level (HFL) line and river setback in writing (WRD / T&CP).',
          'Planning-area status and land use (T&CP Khargone); resort needs commercial use.',
          'Scale was calibrated to the surveyed areas (drawing plotted at about 1:858);',
          '   final layout must be redrawn on the CAD survey by a licensed architect.',
          'Concept for discussion only – not an approved or approvable drawing.']:
    t.text(0,y,n,fontsize=7.2,color='#b71c1c' if not n.startswith('   ') else '#b71c1c'); y-=0.019
y-=0.02
L=[Patch(fc='white',ec='#b71c1c',label='5,000 sq ft plot'),Patch(fc='#ffe0b2',ec='#e65100',label='EWS / LIG plot'),Patch(fc='#c9c9c9',ec='#8a8a8a',label='Road'),
   Patch(fc='#cfe8c4',label='Park / open space / river buffer'),Patch(fc='#f7e7c1',ec='#a8781a',label='Resort parcel'),Patch(fc='#8ec5e8',label='River')]
t.legend(handles=L,loc='lower left',fontsize=7.5,frameon=False,ncol=2)
fig.savefig(OUT+'Colony_Resort_Concept_Layout.pdf'); fig.savefig(OUT+'Colony_Resort_Concept_Layout.png',dpi=130)
# DXF export (metres)
doc=ezdxf.new('R2010'); msp=doc.modelspace()
for n,c in [('RESORT',2),('COLONY',3),('ROADS',8),('PLOTS',1),('EWS_LIG',30),('GREEN',62),('AMENITIES',6),('TEXT',7)]: doc.layers.add(n,color=c)
def poly(g,layer):
    for p in getattr(g,'geoms',[g]):
        if p.geom_type=='Polygon' and not p.is_empty: msp.add_lwpolyline(list(p.exterior.coords),close=True,dxfattribs={'layer':layer})
poly(resort,'RESORT'); poly(colony,'COLONY'); poly(roads,'ROADS'); poly(green,'GREEN')
for i,p in enumerate(plots): poly(p,'PLOTS'); msp.add_text(f'P{i+1}',height=2,dxfattribs={'layer':'TEXT'}).set_placement(p.centroid.coords[0])
for i,p in enumerate(ews): poly(p,'EWS_LIG'); msp.add_text(f'E{i+1}',height=1.2,dxfattribs={'layer':'TEXT'}).set_placement(p.centroid.coords[0])
for k,v in amen.items(): poly(v,'AMENITIES'); msp.add_text(k,height=1.5,dxfattribs={'layer':'TEXT'}).set_placement(v.centroid.coords[0])
doc.saveas(OUT+'Colony_Resort_Concept_Layout.dxf')
import shutil; shutil.copy(D+'plan/plot_schedule.csv',OUT+'Plot_Schedule.csv')
print('ok')
