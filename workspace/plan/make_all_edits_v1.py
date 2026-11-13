"""All owner-agreed edits on top of the optimiser's layout, built from the untouched base (base_original.pkl):
 1. SE block: V29 bigger with 25.9 m on S2, V30 runs to the SE corner with S2 frontage only, V31 smaller on S1 only
 2. V42: the triangle space beside V19/V20 becomes a plot, its 49-degree tip cut off with a corner splay
 3. S1 kept a full 12 m right-of-way to its end (it tapered to nothing along V31 and was ~10 m along V7/V18)
 4. S1 paved road stops 7.5 m short of V30 so the cul-de-sac stays under 150 m (BVN Rule 43); the end piece is landscaped"""
import sys,json,pickle,numpy as np,warnings; warnings.filterwarnings('ignore'); sys.path.insert(0,'.'); import d8
from shapely import wkt
from shapely.geometry import Point, LineString, Polygon, box
from shapely.ops import unary_union, split
SQ=10.764; G=wkt.loads
S=pickle.load(open('base_original.pkl','rb'))
row,C,rpark=G(S['row']),G(S['C']),G(S['rpark']); P={t:G(w) for t,w,k in S['plots']}
GATE=Point(331,-262)
def mainnet(r):
    comps=[q for q in getattr(r.buffer(0.4).buffer(-0.4),'geoms',[r]) if q.area>5]; return min(comps,key=lambda q:q.distance(GATE))
big=lambda g:max(getattr(g,'geoms',[g]),key=lambda q:q.area)
def tidy(p):
    p=big(p.buffer(0.05).buffer(-0.05)).simplify(0.25); return Polygon(p.exterior.coords)
def rangles(p,s=3.0):
    ring=p.exterior; L=ring.length; out=[]
    for c in list(ring.coords)[:-1]:
        d=ring.project(Point(c)); b=np.array(c); a=np.array(ring.interpolate((d-s)%L).coords[0]); e=np.array(ring.interpolate((d+s)%L).coords[0])
        v1,v2=a-b,e-b
        if min(np.linalg.norm(v1),np.linalg.norm(v2))<0.5*s: continue
        out.append((np.degrees(np.arccos(np.clip(v1@v2/np.linalg.norm(v1)/np.linalg.norm(v2),-1,1))),tuple(c)))
    return out
def despike(p,lim=20):
    pts=list(p.exterior.coords)[:-1]; ch=True
    while ch and len(pts)>3:
        ch=False
        for i in range(len(pts)):
            a_,b_,c_=np.array(pts[i-1]),np.array(pts[i]),np.array(pts[(i+1)%len(pts)]); v1,v2=a_-b_,c_-b_
            if np.linalg.norm(v1)<0.3 or np.linalg.norm(v2)<0.3 or np.degrees(np.arccos(np.clip(v1@v2/np.linalg.norm(v1)/np.linalg.norm(v2),-1,1)))<lim:
                pts.pop(i); ch=True; break
    return Polygon(pts)
def chamfer(p,s=6.0,limit=75):
    for _ in range(3):
        a,c=min(rangles(p))
        if a>=limit: break
        ring=p.exterior; L=ring.length; d=ring.project(Point(c))
        A=np.array(ring.interpolate((d-s)%L).coords[0]); B=np.array(ring.interpolate((d+s)%L).coords[0]); u=(B-A)/np.linalg.norm(B-A)
        p=tidy(max(split(p,LineString([tuple(A-u*50),tuple(B+u*50)])).geoms,key=lambda q:q.area))
    return p
def edge_dir(p1,p2):
    sh=p1.buffer(0.4).intersection(p2.buffer(0.4)); cc=np.array(sh.minimum_rotated_rectangle.exterior.coords)[:4]
    dv=max([cc[1]-cc[0],cc[3]-cc[0]],key=np.linalg.norm); return dv/np.linalg.norm(dv),np.array(sh.centroid.coords[0])
new={}
OFF=9.0    # V29/V30 line moved 9 m south: V30 keeps ~15.5 m on S2, of which >12 m faces the full 12 m road (the boundary cuts the S2 end at an angle)
# 1) SE block
Z=unary_union([P['V29'].buffer(0.2),P['V30'].buffer(0.2),P['V31'].buffer(0.2)]).buffer(-0.2)
dv,mid=edge_dir(P['V29'],P['V30']); nv=np.array([-dv[1],dv[0]]); nv=-nv if nv[1]>0 else nv
L=LineString([tuple(mid+nv*OFF-dv*200),tuple(mid+nv*OFF+dv*200)])
south=max([q for q in split(Z,L).geoms if (np.array(q.centroid.coords[0])-mid)@nv>OFF-0.01],key=lambda q:q.area)
north=Z.difference(south).buffer(0)
# 3) S1 corridor: everything within 12 m of the colony's east boundary, north of the V31/V30 line
ext=list(C.exterior.coords)
i0=min(range(len(ext)),key=lambda i:Point(ext[i]).distance(Point(400.2,-83.6))); i1=min(range(len(ext)),key=lambda i:Point(ext[i]).distance(Point(446.6,-191.8)))
bE=LineString(ext[min(i0,i1):max(i0,i1)+1])
cv,m2=edge_dir(P['V29'],P['V31'])
w0,e0=sorted([q for q in split(north,LineString([tuple(m2-cv*200),tuple(m2+cv*200)])).geoms if q.area>5],key=lambda q:q.centroid.x)
lineV=list(south.buffer(0.3).intersection(e0.buffer(0.3)).minimum_rotated_rectangle.exterior.coords)
a=np.array(e0.exterior.coords[0]); 
# the V31/V30 line: shared edge of the east-north part and the south part
dvl,ml=edge_dir(e0,south); u=dvl if dvl[0]>0 else -dvl; n=np.array([-u[1],u[0]]); n=n if n[1]>0 else -n
northside=Polygon([tuple(ml-u*300),tuple(ml+u*300),tuple(ml+u*300+n*300),tuple(ml-u*300+n*300)])
corr=bE.buffer(12.0).intersection(C).intersection(northside).difference(P['R5'].buffer(0.01)).buffer(0)
cut={}
for t in ('V5','V7','V17','V18'):
    if P[t].intersection(corr).area>0.5:
        cut[t]=P[t].intersection(corr); new[t]=despike(tidy(big(P[t].difference(corr).buffer(0))))
cut['V31']=e0.intersection(corr); e1=big(e0.difference(corr).buffer(0))
# rebalance V29 / V31 with a line parallel to their common edge
Z2=unary_union([w0.buffer(0.05),e1.buffer(0.05)]).buffer(-0.05); wv=np.array([cv[1],-cv[0]]); wv=wv if wv[0]<0 else -wv
best=None
for off in np.arange(0,6.01,0.1):
    pp=sorted(split(Z2,LineString([tuple(m2+wv*off-cv*100),tuple(m2+wv*off+cv*100)])).geoms,key=lambda q:q.centroid.x)
    if len(pp)!=2: continue
    d=abs(pp[0].area-pp[1].area)
    if best is None or d<best[0]: best=(d,off,pp[0],pp[1])
new['V29'],new['V31'],new['V30']=despike(tidy(best[2])),despike(tidy(best[3])),despike(tidy(south))
print('V29/V31 line moved west by %.1f m to balance them'%best[1])
# 2) V42 from the triangle space beside V19/V20 (the small park), tip cut with a 6 m splay
free=C.difference(row).difference(rpark).difference(unary_union(list(P.values()))).buffer(-0.2).buffer(0.2)
T=max([x for x in getattr(free,'geoms',[free]) if x.buffer(0.6).intersects(P['V20'])],key=lambda x:x.area)
new['V42']=chamfer(tidy(T))
# roads: corridor slivers join S1; S1 paving stops 7.5 m short of the V31/V30 line
_allp=unary_union(list(new.values())+[p for t,p in P.items() if t not in new and t not in ('V29','V30','V31')]).buffer(0.01)
road_add=unary_union(list(cut.values())).buffer(0.4).intersection(corr).difference(_allp).buffer(0)   # slivers + the hairline gaps beside them, inside the corridor only
row2=unary_union([row,road_add]).buffer(0)
band=Polygon([tuple(ml-u*300),tuple(ml+u*300),tuple(ml+u*300+n*7.5),tuple(ml-u*300+n*7.5)])
endzone=band.intersection(box(430,-200,470,-170)).intersection(C).difference(new['V31'].buffer(0.05)).buffer(0)
row2=row2.difference(endzone).buffer(0); road_add=road_add.difference(endzone).buffer(0)
# clean: no plot on a road, no overlaps
keep={t:p for t,p in P.items() if t not in new and t not in ('V29','V30','V31')}
for t in list(new): new[t]=big(new[t].difference(row2).buffer(0))
for t in list(new):
    q=new[t]
    for o in list(keep.values())+[v for s_,v in new.items() if s_!=t]:
        if q.intersection(o).area>0.01: q=big(q.difference(o).buffer(0))
    new[t]=q
mn=mainnet(row2)
print('plot   before -> after (sq ft) | frontage on the gate network | rect fill | sharpest corner | shape rule')
for t,q in sorted(new.items(),key=lambda x:int(x[0][1:])):
    b_=round(P[t].area*SQ) if t in P else 0
    print('%-5s %6d -> %6d | %5.1f m | %.2f | %3d deg | %s'%(t,b_,q.area*SQ,q.buffer(0.8).intersection(mn).area/0.8,q.area/q.minimum_rotated_rectangle.area,min(a_ for a_,_ in rangles(q)),d8.good_shape(q)))
E=dict(remove=[list(P[t].representative_point().coords[0]) for t in new if t in P],
       add=[(q.wkt,'Villa',t) for t,q in new.items()],
       keep_tags=[(list(p.representative_point().coords[0]),t) for t,p in keep.items()],
       road_add=road_add.wkt, road_remove=endzone.wkt)
json.dump(E,open('edits_Plan_4000_Max_RiverDrive12m.json','w'))
print('S1 slivers added to road %.0f m2 | S1 end piece landscaped %.0f m2 | edits: %d removed, %d added'%(road_add.area,endzone.area,len(E['remove']),len(E['add'])))
