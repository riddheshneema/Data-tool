import pickle, numpy as np, json, sys, math
from shapely.geometry import box
from shapely.ops import unary_union
from shapely import affinity, prepared
D='/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
G=pickle.load(open(D+'site/geo.pkl','rb')); P=G['P']; res=G['res']
dist=np.load(D+'site/dist.npy'); site=unary_union(P)
SET=float(sys.argv[1]); FT=0.3048; PW,PD=50*FT,100*FT; R9,R12=9.0,12.0
def rdist(x,y):
    r=int(-y/res); c=int(x/res)
    return float(dist[r,c]) if 0<=r<dist.shape[0] and 0<=c<dist.shape[1] else 0.0
# 50/50 split, resort to the north (river bend)
lo,hi=-551,-55
for _ in range(60):
    mid=(lo+hi)/2
    if site.intersection(box(0,-1000,1000,mid)).area<site.area/2: lo=mid
    else: hi=mid
CY=(lo+hi)/2; colony=site.intersection(box(0,-1000,1000,CY)); resort=site.difference(colony)
regions={'Main (Area-1 south + Area-2)':colony.difference(P[2]).buffer(0),'East strip (Area-3)':P[2].intersection(colony)}
O=(300,-400)
def solve(R):
    best=(0,)
    for th in range(0,180,10):
        Rr=affinity.rotate(R,-th,origin=O); Rp=prepared.prep(Rr.buffer(-0.5))
        minx,miny,maxx,maxy=Rr.bounds
        for xs in np.linspace(minx+20,maxx-20,9):
          for y0 in np.arange(0,PD*2+R9,6):
            for x0 in (0,PW/3,2*PW/3):
              plots=[];roads=[];yr=miny-PD+y0
              while yr<maxy:
                kept=[]
                for ya,yb in ((yr+R9,yr+R9+PD),(yr-PD,yr)):
                  xx=minx+x0
                  while xx+PW<=maxx:
                    if not (xx+PW>xs-R12/2 and xx<xs+R12/2):
                      b=box(xx,ya,xx+PW,yb)
                      if Rp.contains(b): kept.append(b)
                    xx+=PW
                if kept:
                  xa=min(min(b.bounds[0] for b in kept),xs-R12/2); xb=max(max(b.bounds[2] for b in kept),xs+R12/2)
                  roads.append(box(xa,yr,xb,yr+R9)); plots+=kept
                yr+=PD*2+R9
              # river setback check in world coords
              wp=[affinity.rotate(b,th,origin=O) for b in plots]
              ok=[b for b in wp if min(rdist(*p) for p in list(b.exterior.coords)[:4]+[b.centroid.coords[0]])>=SET]
              if len(ok)>best[0]:
                spine=box(xs-R12/2,miny-50,xs+R12/2,maxy+50)
                rd=[affinity.rotate(g,th,origin=O) for g in roads+[spine]]
                best=(len(ok),th,ok,unary_union(rd).intersection(R))
    return best
allp=[];allr=[]
for name,R in regions.items():
    n,th,pl,rd=solve(R); print(name,'plots',n,'angle',th); allp+=pl; allr.append(rd)
roads=unary_union(allr)
plots=unary_union(allp); left=colony.difference(roads).difference(plots)
json.dump(dict(CY=float(CY),n=len(allp),colony=colony.wkt,resort=resort.wkt,roads=roads.wkt,plots=[p.wkt for p in allp],left=left.wkt,setback=SET),open(D+f'plan/layout2_{int(SET)}.json','w'))
ac=lambda a:a/4046.86
print(f'colony {ac(colony.area):.2f} ac | plots {len(allp)} = {len(allp)*PW*PD:.0f} sq m ({100*len(allp)*PW*PD/colony.area:.1f}%) | roads {100*roads.area/colony.area:.1f}% | leftover {100*left.area/colony.area:.1f}%')
