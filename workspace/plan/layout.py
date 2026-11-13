import pickle, numpy as np, json, sys
from shapely.geometry import box, Polygon, LineString, Point
from shapely.ops import unary_union
D='/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/site/'
G=pickle.load(open(D+'geo.pkl','rb')); P=G['P']; res=G['res']
dist=np.load(D+'dist.npy')
site=unary_union(P)
def rdist(x,y):
    r=int(-y/res); c=int(x/res)
    if 0<=r<dist.shape[0] and 0<=c<dist.shape[1]: return float(dist[r,c])
    return 0.0
SET=float(sys.argv[1]) if len(sys.argv)>1 else 15.0   # river setback (m)
FT=0.3048; PW,PD=50*FT,100*FT          # 5,000 sq ft plot: 50' x 100'
R9,R12=9.0,12.0
# --- split: resort north, colony south, 50/50 by area -------------------
def colony_at(c): return site.intersection(box(0,-1000,1000,c))
lo,hi=-551,-55
for _ in range(60):
    mid=(lo+hi)/2
    if colony_at(mid).area<site.area/2: lo=mid
    else: hi=mid
CY=(lo+hi)/2; colony=colony_at(CY); resort=site.difference(colony)
ENTRY=(299.0,-471.0)
best=None
for xs in np.arange(270,330,3):           # spine x position
  spine=box(xs-R12/2,-1000,xs+R12/2,CY)
  for y0 in np.arange(0,70,2.5):
    for x0 in np.arange(0,PW,2.54):
      plots=[];roads=[]
      ystart=-560+y0
      k=0
      while ystart+k*(PD*2+R9)<CY:
        yr=ystart+k*(PD*2+R9); k+=1
        rows=[(yr+R9,yr+R9+PD),(yr-PD,yr)]
        kept=[]
        for (ya,yb) in rows:
          xx=x0+100
          while xx<480:
            b=box(xx,ya,xx+PW,yb); xx+=PW
            if b.intersects(spine): continue
            if not colony.buffer(-0.5).contains(b): continue
            pts=list(b.exterior.coords)[:4]+[b.centroid.coords[0]]
            if min(rdist(*p) for p in pts)<SET: continue
            kept.append(b)
        if kept:
          xa=min(min(b.bounds[0] for b in kept),xs); xb=max(max(b.bounds[2] for b in kept),xs)
          road=box(xa,yr,xb,yr+R9).intersection(colony)
          plots+=kept; roads.append(road)
      n=len(plots)
      if best is None or n>best[0]: best=(n,xs,y0,x0,plots,roads)
n,xs,y0,x0,plots,roads=best
spine_poly=box(xs-R12/2,ENTRY[1]-20,xs+R12/2,CY).intersection(site)
road_all=unary_union(roads+[spine_poly]).intersection(colony)
plot_all=unary_union(plots)
left=colony.difference(road_all).difference(plot_all)
out=dict(CY=float(CY),xs=float(xs),n=int(n),colony=colony.wkt,resort=resort.wkt,roads=road_all.wkt,
         plots=[p.wkt for p in plots],left=left.wkt,setback=SET)
json.dump(out,open(D+f'../plan/layout_{int(SET)}.json','w'))
ac=lambda a:a/4046.86
print(f'setback {SET} m | split y={CY:.1f} | colony {ac(colony.area):.2f} ac | resort {ac(resort.area):.2f} ac')
print(f'plots {n} x 464.5 sq m = {n*PW*PD:.0f} sq m ({100*n*PW*PD/colony.area:.1f}%) | roads {road_all.area:.0f} ({100*road_all.area/colony.area:.1f}%) | leftover {left.area:.0f} ({100*left.area/colony.area:.1f}%)')
