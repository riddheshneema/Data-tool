import sys,pickle,json,numpy as np,warnings; warnings.filterwarnings('ignore')
sys.path.insert(0,'.')
exec(open('island.py').read().split("free=C.difference")[0])   # helpers: tidy, rangles, chamfer, quality, front
E0=json.load(open('edits_Plan_4000_Max_RiverDrive12m.json'))
v29,v31,v30=[tidy(G(w)) for w,*_ in E0["add"][:3]]
free=C.difference(row).difference(rpark).difference(unary_union(list(P.values()))).buffer(-0.2).buffer(0.2)
T=max([x for x in getattr(free,'geoms',[free]) if x.buffer(0.6).intersects(P['V20'])],key=lambda x:x.area)
v42=chamfer(tidy(T))
new={'V29':v29,'V31':v31,'V30':v30,'V42':v42}
for t,p in new.items(): print(t,quality(p),'corners',sorted(round(a) for a,_ in rangles(p))[:4])
# no overlaps with each other or with any kept plot / road / promenade
keep={t:p for t,p in P.items() if t not in ('V29','V30','V31')}
for t,p in new.items():
    ov=max([p.intersection(q).area for q in list(keep.values())+[v for s,v in new.items() if s!=t]])
    print(t,'overlap with other plots m2 %.2f | with roads %.2f | with promenade %.2f'%(ov,p.intersection(row).area,p.intersection(rpark).area))
json.dump(dict(remove=[list(P[t].representative_point().coords[0]) for t in ('V29','V30','V31')],
               add=[(p.wkt,'Villa',t) for t,p in new.items()],
               keep_tags=[(list(p.representative_point().coords[0]),t) for t,p in keep.items()]),
          open('edits_Plan_4000_Max_RiverDrive12m.json','w'))
print('saved; old V29 %d, V30 %d, V31 %d sq ft'%tuple(P[t].area*SQ for t in ('V29','V30','V31')))
# ---- clean-up pass: remove spikes, keep plots off the road, no overlaps ----
def despike(p,lim=20):
    pts=list(p.exterior.coords)[:-1]
    changed=True
    while changed and len(pts)>3:
        changed=False
        for i in range(len(pts)):
            a,b,c=np.array(pts[i-1]),np.array(pts[i]),np.array(pts[(i+1)%len(pts)])
            v1,v2=a-b,c-b
            if np.linalg.norm(v1)<1e-6 or np.linalg.norm(v2)<1e-6 or np.degrees(np.arccos(np.clip(v1@v2/np.linalg.norm(v1)/np.linalg.norm(v2),-1,1)))<lim:
                pts.pop(i); changed=True; break
    return Polygon(pts)
Z=unary_union([P[t] for t in ('V29','V30','V31')])
v31=despike(new['V31']); v29=new['V29']; v30=tidy(new['V30'].difference(v31).difference(v29).buffer(0))
v42=big(tidy(new['V42']).difference(row).buffer(0))
new={'V29':v29,'V31':v31,'V30':v30,'V42':v42}
for t,p in new.items(): print(t,quality(p),'corners',sorted(round(a) for a,_ in rangles(p))[:4])
print('SE block land not in a plot after re-cut: %.2f m2'%Z.difference(unary_union([v29,v30,v31])).area)
for t,p in new.items():
    ov=max([p.intersection(q).area for q in list(keep.values())+[v for s,v in new.items() if s!=t]])
    print(t,'overlap other plots %.2f | roads %.2f | promenade %.2f'%(ov,p.intersection(row).area,p.intersection(rpark).area))
json.dump(dict(remove=[list(P[t].representative_point().coords[0]) for t in ('V29','V30','V31')],
               add=[(p.wkt,'Villa',t) for t,p in new.items()],
               keep_tags=[(list(p.representative_point().coords[0]),t) for t,p in keep.items()]),
          open('edits_Plan_4000_Max_RiverDrive12m.json','w'))
print('saved clean edits')
