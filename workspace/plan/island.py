import sys,pickle,json,numpy as np,warnings; warnings.filterwarnings('ignore')
sys.path.insert(0,'.'); import d8
from shapely import wkt
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union, split
SQ=10.764
S=pickle.load(open('final_Plan_4000_Max_RiverDrive12m.pkl','rb')); G=wkt.loads
row,C,rpark=G(S['row']),G(S['C']),G(S['rpark']); P={t:G(w) for t,w,k in S['plots']}
GATE=Point(331,-262)
comps=[q for q in getattr(row.buffer(0.4).buffer(-0.4),'geoms',[row]) if q.area>5]; main=min(comps,key=lambda q:q.distance(GATE))
front=lambda p:p.buffer(0.8).intersection(main).area/0.8
big=lambda g:max(getattr(g,'geoms',[g]),key=lambda q:q.area)
def tidy(p):
    p=big(p.buffer(0.05).buffer(-0.05)).simplify(0.25)
    return Polygon(p.exterior.coords)
def rangles(p,s=3.0):
    """corner angle at each vertex, measured to points s metres along the boundary (ignores vertex noise)"""
    ring=p.exterior; L=ring.length; out=[]
    for c in list(ring.coords)[:-1]:
        d=ring.project(Point(c)); b=np.array(c)
        a=np.array(ring.interpolate((d-s)%L).coords[0]); e=np.array(ring.interpolate((d+s)%L).coords[0])
        v1,v2=a-b,e-b
        if min(np.linalg.norm(v1),np.linalg.norm(v2))<0.5*s: continue
        out.append((np.degrees(np.arccos(np.clip(v1@v2/np.linalg.norm(v1)/np.linalg.norm(v2),-1,1))),tuple(c)))
    return out
def chamfer(p,s=6.0,limit=75):
    """cut every corner sharper than `limit` degrees with a straight splay, s metres back along both edges"""
    for _ in range(3):
        a,c=min(rangles(p))
        if a>=limit: break
        ring=p.exterior; L=ring.length; d=ring.project(Point(c))
        A=np.array(ring.interpolate((d-s)%L).coords[0]); B=np.array(ring.interpolate((d+s)%L).coords[0]); u=(B-A)/np.linalg.norm(B-A)
        cut=LineString([tuple(A-u*50),tuple(B+u*50)])
        p=tidy(max(split(p,cut).geoms,key=lambda q:q.area))
    return p
def quality(p):
    mrr=p.minimum_rotated_rectangle; cc=list(mrr.exterior.coords); s1=Point(cc[0]).distance(Point(cc[1])); s2=Point(cc[1]).distance(Point(cc[2]))
    return dict(sqft=round(p.area*SQ),front=round(front(p),1),fill=round(p.area/mrr.area,2),minang=round(min(a for a,_ in rangles(p))),ratio=round(max(s1,s2)/min(s1,s2),2),
                ok=bool(d8.good_shape(p)))
free=C.difference(row).difference(rpark).difference(unary_union(list(P.values()))).buffer(-0.2).buffer(0.2)
T=max([x for x in getattr(free,'geoms',[free]) if x.buffer(0.6).intersects(P['V20'])],key=lambda x:x.area)
print('V19',quality(tidy(P['V19']))); print('V20',quality(tidy(P['V20']))); print('wedge raw',round(T.area*SQ))
Z=tidy(unary_union([P['V20'].buffer(0.2),T.buffer(0.2)]).buffer(-0.2))
# the V20/wedge line today, and the V19/V20 line
sh=P['V20'].buffer(0.4).intersection(T.buffer(0.4)); cc=np.array(sh.minimum_rotated_rectangle.exterior.coords)[:4]
dv=max([cc[1]-cc[0],cc[3]-cc[0]],key=np.linalg.norm); dv/=np.linalg.norm(dv); mid=np.array(sh.centroid.coords[0]); nv=np.array([-dv[1],dv[0]])
if nv[1]<0: nv=-nv   # northward
res=[]
for off in np.arange(-2,12.1,0.5):      # move the V20 / new plot line north by `off` metres
    L=LineString([tuple(mid+nv*off-dv*200),tuple(mid+nv*off+dv*200)])
    parts=sorted(split(Z,L).geoms,key=lambda q:-q.centroid.y)
    if len(parts)!=2: continue
    n_,s_=tidy(parts[0]),chamfer(tidy(parts[1]))
    qn,qs=quality(n_),quality(s_)
    res.append((off,qn,qs,n_,s_))
for off,qn,qs,_,_ in res: print('north-shift %4.1f m | V20 %s | new %s'%(off,qn,qs))
pickle.dump([(off,qn,qs,n_.wkt,s_.wkt) for off,qn,qs,n_,s_ in res],open('island_opts.pkl','wb'))
