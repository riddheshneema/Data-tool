import json, numpy as np, csv
from shapely import wkt
from shapely.geometry import box, Polygon, LineString, Point
from shapely.ops import unary_union
D='/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
L=json.load(open(D+'plan/layout3_15.json'))
colony=wkt.loads(L['colony']); resort=wkt.loads(L['resort']); roads=wkt.loads(L['roads'])
plots=[wkt.loads(s) for s in L['plots']]
# 12 m link road from the main-road junction up the east edge to the resort
best=None
for x in np.arange(300,339,1.0):
    for yb in np.arange(-480,-300,2.0):
        ln=LineString([(x,yb),(x,-262)]).buffer(6,cap_style=2).intersection(colony)
        if ln.is_empty or not ln.buffer(0.5).intersects(roads.buffer(-0.5)) : continue
        # must start on an existing road at its south end
        if not Point(x,yb).buffer(3).intersects(roads): continue
        n=sum(1 for p in plots if p.intersection(ln).area>1)
        key=(n,-yb)
        if best is None or key<best[0]: best=(key,ln,x,yb)
link=best[1]; print('link road x=%.0f from y=%.0f, plots lost %d'%(best[2],best[3],best[0][0]))
hit=[p for p in plots if p.intersection(link).area>1]
plots=[p for p in plots if p.intersection(link).area<=1]
roads=unary_union([roads,link]).intersection(colony)
# order plots for numbering: top-to-bottom, left-to-right
plots.sort(key=lambda p:(-round(p.centroid.y/20),p.centroid.x))
# EWS/LIG pocket: convert the 4 east-strip plots furthest south
east=[p for p in plots if p.centroid.x>355]
east.sort(key=lambda p:p.centroid.y)
ews_src=east[:4]; plots=[p for p in plots if p not in ews_src]
ews=[]
for p in ews_src:
    x0,y0,x1,y1=p.bounds; w,h=x1-x0,y1-y0
    # split each 50'x100' plot into four 25'x50' (116 sq m) plots
    for i in range(2):
        for j in range(2):
            ews.append(box(x0+i*w/2,y0+j*h/2,x0+(i+1)*w/2,y0+(j+1)*h/2))
built=unary_union(plots+ews+[roads])
left=colony.difference(built).buffer(0)
pieces=sorted([g for g in getattr(left,'geoms',[left]) if g.area>20],key=lambda g:-g.area)
# amenity siting in leftover land
def place(near,size,avoid):
    best=None
    for g in pieces:
        for dx in np.arange(-60,61,3):
            for dy in np.arange(-60,61,3):
                b=box(near[0]+dx-size[0]/2,near[1]+dy-size[1]/2,near[0]+dx+size[0]/2,near[1]+dy+size[1]/2)
                if g.buffer(0.01).contains(b) and not any(b.intersects(a) for a in avoid):
                    d=Point(near).distance(b.centroid)
                    if best is None or d<best[0]: best=(d,b)
    return best[1] if best else None
amen={}
amen['Transformer / electric sub-station']=place((350,-470),(10,10),[])
amen['Clubhouse & community facility']=place((365,-380),(22,22),[a for a in amen.values() if a]) or place((250,-300),(22,22),[a for a in amen.values() if a])
amen['Overhead tank & tubewell']=place((300,-280),(14,14),[a for a in amen.values() if a])
amen['STP (sewage treatment)']=place((150,-470),(20,15),[a for a in amen.values() if a])
amen['Waste collection point']=place((320,-470),(8,6),[a for a in amen.values() if a])
amen={k:v for k,v in amen.items() if v is not None}
util=unary_union([v for k,v in amen.items() if 'Clubhouse' not in k])
club=amen.get('Clubhouse & community facility')
green=left.difference(unary_union(list(amen.values()))).buffer(0)
FT2=10.7639
A=dict(colony=colony.area,resort=resort.area,plots=sum(p.area for p in plots),ews=sum(p.area for p in ews),roads=roads.area,
       util=util.area,club=club.area if club else 0,green=green.area)
ac=lambda a:a/4046.86
rows=[('Residential plots (50 x 100 ft = 5,000 sq ft)',len(plots),A['plots']),
      ('EWS / LIG plots (25 x 50 ft = 1,250 sq ft)',len(ews),A['ews']),
      ('Roads (12 m main, 12 m resort link, 9 m internal)','',A['roads']),
      ('Parks, open space & river green buffer','',A['green']),
      ('Clubhouse / community facility','',A['club']),
      ('Utilities (transformer, tank, STP, waste point)','',A['util'])]
tot=sum(r[2] for r in rows)
print('removed for link road:',len(hit))
print(f"{'Use':52s} {'No.':>4s} {'sq m':>9s} {'sq ft':>10s} {'acre':>6s} {'%':>6s}")
for n,c,a in rows: print(f"{n:52s} {str(c):>4s} {a:9.0f} {a*FT2:10.0f} {ac(a):6.2f} {100*a/A['colony']:6.1f}")
print(f"{'TOTAL COLONY':52s} {'':>4s} {tot:9.0f} {tot*FT2:10.0f} {ac(tot):6.2f} {100*tot/A['colony']:6.1f}")
print(f"Resort parcel: {A['resort']:.0f} sq m = {ac(A['resort']):.2f} ac")
print('EWS share of saleable: %.1f%%'%(100*A['ews']/(A['ews']+A['plots'])))
json.dump(dict(colony=colony.wkt,resort=resort.wkt,roads=roads.wkt,plots=[p.wkt for p in plots],ews=[p.wkt for p in ews],
  green=green.wkt,amen={k:v.wkt for k,v in amen.items()},rows=rows,A=A),open(D+'plan/final.json','w'))
with open(D+'plan/plot_schedule.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['Plot no','Type','Size (ft)','Area (sq ft)','Area (sq m)','Centroid x (m)','Centroid y (m)'])
    for i,p in enumerate(plots): w.writerow([f'P{i+1}','Residential','50 x 100',5000,round(p.area,1),round(p.centroid.x,1),round(p.centroid.y,1)])
    for i,p in enumerate(ews): w.writerow([f'E{i+1}','EWS' if i<len(ews)//2 else 'LIG','25 x 50',1250,round(p.area,1),round(p.centroid.x,1),round(p.centroid.y,1)])
