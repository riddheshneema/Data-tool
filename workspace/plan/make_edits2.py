# S1 fix: keep S1 a full 12 m right-of-way to its end (it tapered to nothing along V31 and was ~10 m along V7/V18)
import sys,json,pickle,numpy as np,warnings; warnings.filterwarnings('ignore'); sys.path.insert(0,'.')
exec(open('island.py').read().split("free=C.difference")[0])     # P (current, post-edit plots), row, C, rpark, tidy, rangles, quality, front
from shapely.geometry import Polygon, LineString, box
E=json.load(open('edits_v1_backup.json'))
ext=list(C.exterior.coords)
i0=[i for i,c in enumerate(ext) if abs(c[0]-400.2)<0.2 and abs(c[1]+83.6)<0.2][0]
i1=[i for i,c in enumerate(ext) if abs(c[0]-446.6)<0.2 and abs(c[1]+191.8)<0.2][0]
bE=LineString(ext[i0:i1+1]) if i1>i0 else LineString(ext[i1:i0+1])
a=np.array([422.2,-188.4]); b=np.array([448.4,-183.7]); u=(b-a)/np.linalg.norm(b-a); n=np.array([-u[1],u[0]])
north=Polygon([tuple(a-u*300),tuple(b+u*300),tuple(b+u*300+n*300),tuple(a-u*300+n*300)])   # north of the V31/V30 line
corr=bE.buffer(12.0).intersection(C).intersection(north).difference(P['R5'].buffer(0.01)).buffer(0)
hit={t:p for t,p in P.items() if t!='R5' and p.intersection(corr).area>0.5}
print('plots cut by the 12 m S1 corridor:',{t:round(p.intersection(corr).area,1) for t,p in hit.items()})
newp={}
for t,p in hit.items():
    q=tidy(big(p.difference(corr).buffer(0)))
    newp[t]=q
# S1 is now: old road + corridor (minus every plot that keeps its land)
keep_all=unary_union([p for t,p in P.items() if t not in hit]+list(newp.values()))
road_add=corr.difference(keep_all).difference(rpark).buffer(0)
row2=unary_union([row,road_add]).buffer(0)
GATE=Point(331,-262); comps=[q for q in getattr(row2.buffer(0.4).buffer(-0.4),'geoms',[row2]) if q.area>5]; main2=min(comps,key=lambda q:q.distance(GATE))
for t,q in newp.items():
    fr=q.buffer(0.8).intersection(main2).area/0.8
    print(t,'%d -> %d sq ft | frontage %.1f m | fill %.2f | min corner %d | shape ok %s'%(P[t].area*SQ,q.area*SQ,fr,q.area/q.minimum_rotated_rectangle.area,min(a_ for a_,_ in rangles(q)),d8.good_shape(q)))
# merge into the edit set (edit coordinates refer to the plots before any edit; V5/V7/V18 are unchanged before this fix)
add={t_:(w_,k_) for w_,k_,t_ in E['add']}
for t,q in newp.items():
    if t not in add: E['remove'].append(list(P[t].representative_point().coords[0]))
    add[t]=(q.wkt,'Villa')
E['add']=[(w_,k_,t_) for t_,(w_,k_) in add.items()]
E['keep_tags']=[(pt,t_) for pt,t_ in E['keep_tags'] if t_ not in newp]
E['road_add']=road_add.wkt
json.dump(E,open('edits_Plan_4000_Max_RiverDrive12m.json','w'))
print('road land added to S1: %.0f m2 | edits saved'%road_add.area)
