import sys,json,pickle,numpy as np,warnings; warnings.filterwarnings('ignore'); sys.path.insert(0,'.')
src=open('make_edits2.py').read().split('# merge into the edit set')[0]
exec(src.replace("hit={t:p","hit0={t:p").replace("print('plots cut by","hit=hit0\nprint('plots cut by"))
from shapely.ops import split
exec(open('make_edits.py').read().split('def despike')[1].join(['def despike','']) if False else '')
def despike(p,lim=20):
    pts=list(p.exterior.coords)[:-1]; ch=True
    while ch and len(pts)>3:
        ch=False
        for i in range(len(pts)):
            a_,b_,c_=np.array(pts[i-1]),np.array(pts[i]),np.array(pts[(i+1)%len(pts)]); v1,v2=a_-b_,c_-b_
            if np.linalg.norm(v1)<0.3 or np.linalg.norm(v2)<0.3 or np.degrees(np.arccos(np.clip(v1@v2/np.linalg.norm(v1)/np.linalg.norm(v2),-1,1)))<lim:
                pts.pop(i); ch=True; break
    return Polygon(pts)
cut={t:P[t].intersection(corr).buffer(0) for t in hit}
road_add=unary_union(list(cut.values())).buffer(0.05).buffer(-0.05)       # only the slivers taken from plots
for t in ('V5','V7','V18'): newp[t]=despike(newp[t])
# re-split V29 + (V31 minus the corridor) with a line parallel to their old common edge, so both end up about equal
Z=unary_union([P['V29'].buffer(0.05),newp['V31'].buffer(0.05)]).buffer(-0.05)
sh=P['V29'].buffer(0.3).intersection(P['V31'].buffer(0.3)); cc=np.array(sh.minimum_rotated_rectangle.exterior.coords)[:4]
dv=max([cc[1]-cc[0],cc[3]-cc[0]],key=np.linalg.norm); dv/=np.linalg.norm(dv); nv=np.array([dv[1],-dv[0]])
if nv[0]>0: nv=-nv       # pointing west
mid=np.array(sh.centroid.coords[0])
best=None
for off in np.arange(0,6.01,0.1):
    L=LineString([tuple(mid+nv*off-dv*100),tuple(mid+nv*off+dv*100)])
    pp=sorted(split(Z,L).geoms,key=lambda q:q.centroid.x)
    if len(pp)!=2: continue
    w_,e_=despike(tidy(pp[0])),despike(tidy(pp[1]))
    d=abs(w_.area-e_.area)
    if best is None or d<best[0]: best=(d,off,w_,e_)
_,off,v29,v31=best; newp['V29']=v29; newp['V31']=v31
print('V29/V31 line moved west by %.1f m'%off)
row2=unary_union([row,road_add]).buffer(0)
comps=[q for q in getattr(row2.buffer(0.4).buffer(-0.4),'geoms',[row2]) if q.area>5]; main2=min(comps,key=lambda q:q.distance(Point(331,-262)))
for t,q in newp.items():
    fr=q.buffer(0.8).intersection(main2).area/0.8
    print(t,'%d -> %d sq ft | frontage %.1f m | fill %.2f | min corner %d | shape ok %s'%(P[t].area*SQ,q.area*SQ,fr,q.area/q.minimum_rotated_rectangle.area,min(a_ for a_,_ in rangles(q)),d8.good_shape(q)))
for t in list(newp): newp[t]=big(newp[t].difference(row2).buffer(0))
_others=[p for t,p in P.items() if t not in newp]
for t in list(newp):
    q=newp[t]
    for o in _others+[v for s_,v in newp.items() if s_!=t]:
        if q.intersection(o).area>0.01: q=big(q.difference(o).buffer(0))
    newp[t]=q
allp=[p for t,p in P.items() if t not in newp]+list(newp.values())
print('overlaps between plots: %.2f m2 | plots on road: %.2f m2'%(max(allp[i].intersection(allp[j]).area for i in range(len(allp)) for j in range(i+1,len(allp))),max(q.intersection(row2).area for q in newp.values())))
add={t_:(w_,k_) for w_,k_,t_ in E['add']}
for t,q in newp.items():
    if t not in add: E['remove'].append(list(P[t].representative_point().coords[0]))
    add[t]=(q.wkt,'Villa')
E['add']=[(w_,k_,t_) for t_,(w_,k_) in add.items()]
E['keep_tags']=[(pt,t_) for pt,t_ in E['keep_tags'] if t_ not in newp]
E['road_add']=road_add.wkt
# S1 cul-de-sac: stop the paved road 7.5 m short of the V31/V30 line so S1 is under 150 m from the S2 junction;
# the end piece is landscaped, and V30 keeps S2 as its only road
a2=a+n*7.5; b2=b+n*7.5
band=Polygon([tuple(a-u*300),tuple(b+u*300),tuple(b2+u*300),tuple(a2-u*300)])
endzone=band.difference(newp['V31'].buffer(0.05)).difference(unary_union(list(P.values())).difference(P['V31']).buffer(0.05)).intersection(box(430,-200,470,-170))
E['road_remove']=endzone.buffer(0).wkt
print('S1 end piece turned to landscaping: %.0f m2'%endzone.area)
json.dump(E,open('edits_Plan_4000_Max_RiverDrive12m.json','w'))
print('road land added to S1: %.0f m2 | edits saved: %d removes, %d adds'%(road_add.area,len(E['remove']),len(E['add'])))
