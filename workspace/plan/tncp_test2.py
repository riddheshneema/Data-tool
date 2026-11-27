import sys,json,math,pickle,numpy as np,warnings; warnings.filterwarnings('ignore')
sys.path.insert(0,'.'); from roadnet import load
from shapely.geometry import Point, LineString
from shapely.ops import unary_union, substring
TAG=sys.argv[1]; S,G=load(TAG); SQ=10.764
C,row,rpark,walk,svc,access,R=[G(S[k]) for k in ('C','row','rpark','walk','svc','access','R')]
plots=[(t,G(w),k) for t,w,k in S['plots']]
net=unary_union([row,access]).buffer(0.3).buffer(-0.3)
GATE=Point(331,-262)
comps=[q for q in getattr(row.buffer(0.4).buffer(-0.4),'geoms',[row]) if q.area>5]; main=min(comps,key=lambda q:q.distance(GATE))
def frontage_widths(p,step=1.0):
    """ROW width measured square off the plot's road edge, every metre along its frontage"""
    ring=p.exterior; out=[]
    for d in np.arange(0.5,ring.length,step):
        a=ring.interpolate(d); b=ring.interpolate(min(d+0.3,ring.length)); 
        if a.distance(main)>0.8: continue
        t=np.array(b.coords[0])-np.array(a.coords[0]); 
        if np.linalg.norm(t)<1e-6: continue
        t/=np.linalg.norm(t); n=np.array([t[1],-t[0]])
        if p.contains(Point(np.array(a.coords[0])+n*0.5)): n=-n
        ray=LineString([tuple(np.array(a.coords[0])+n*0.2),tuple(np.array(a.coords[0])+n*40)])
        x=ray.intersection(net)
        segs=[s for s in getattr(x,'geoms',[x]) if s.length>0 and s.distance(Point(np.array(a.coords[0])))<1.0]
        if segs: out.append((segs[0].length+0.2,d))
    return out
rows=[]; 
riv=R.buffer(0)
for t,p,k in plots:
    fw=frontage_widths(p); ws=sorted(w for w,_ in fw)
    # drop the metre at each end of a frontage run (corner splays / junction mouths read wide or short)
    wmin=np.percentile(ws,10) if ws else 0
    f12=sum(1.0 for w,_ in fw if w>=11.5); f75=sum(1.0 for w,_ in fw if w>=7.5)
    fr=p.buffer(0.8).intersection(main).area/0.8
    # building envelope: 3.6 m off the road edge (12 m street), 3 m off every other edge (rear + both sides, detached)
    env=p.buffer(-3.0).difference(net.buffer(3.6)).buffer(0)
    env=max(getattr(env,'geoms',[env]),key=lambda q:q.area) if not env.is_empty else env
    mrr=env.minimum_rotated_rectangle if not env.is_empty else None
    ew=min(LineString(mrr.exterior.coords[:2]).length,LineString(mrr.exterior.coords[1:3]).length) if mrr is not None else 0
    rows.append(dict(plot=t,kind=k,sqm=round(p.area,1),sqft=round(p.area*SQ),front=round(fr,1),road_w=round(wmin,1),f12=f12,f75=f75,
                     env_sqm=round(env.area,1),env_w=round(ew,1),river_m=round(p.distance(riv),1),
                     bldg_to_os=round(env.distance(rpark),1) if not env.is_empty else None))
json.dump(rows,open('plottest_'+TAG+'.json','w'),indent=0)
import collections
print('plots:',len(rows))
print('min area %.0f m2 (%s) | all detached >225 m2: %s'%(min(r['sqm'] for r in rows),min(rows,key=lambda r:r['sqm'])['plot'],all(r['sqm']>225 for r in rows)))
print('min frontage %.1f m (%s) | all >12 m: %s'%(min(r['front'] for r in rows),min(rows,key=lambda r:r['front'])['plot'],all(r['front']>12 for r in rows)))
lw=sorted(rows,key=lambda r:r['f75'])[:6]; print('frontage on a street at least 7.5 m wide (Rule 38 + 53 need >12 m): lowest',[(r['plot'],r['f75']) for r in lw])
l12=sorted(rows,key=lambda r:r['f12'])[:6]; print('frontage on a full 12 m street: lowest',[(r['plot'],r['f12']) for r in l12])
le=sorted(rows,key=lambda r:r['env_sqm'])[:5]; print('smallest building envelope after setbacks:',[(r['plot'],r['env_sqm'],'w',r['env_w']) for r in le])
lr=sorted(rows,key=lambda r:r['river_m'])[:5]; print('closest plots to the river edge (m):',[(r['plot'],r['river_m']) for r in lr])
lb=sorted([r for r in rows if r['bldg_to_os'] is not None],key=lambda r:r['bldg_to_os'])[:3]; print('closest building line to the promenade (m):',[(r['plot'],r['bldg_to_os']) for r in lb])
print('FAR 1.25: largest permissible built-up %.0f sq ft (%s), smallest %.0f sq ft'%(max(r['sqft'] for r in rows)*1.25,max(rows,key=lambda r:r['sqft'])['plot'],min(r['sqft'] for r in rows)*1.25))
# open space
def os_test(poly,name):
    from roadnet import network, simplify_graph
    g,_,_=network(poly,prune=20.0); 
    L=sum(d['len'] for a,b,d in g.edges(data=True)); W=poly.area/L if L>0 else 0
    touch=poly.buffer(0.6).intersection(main).area/0.6; tw=poly.buffer(0.6).intersection(walk.buffer(0.3)).area/0.6 if not walk.is_empty else 0
    print(f'{name}: {poly.area:,.0f} m2 = {poly.area/C.area:.1%} of layout | centre-line length {L:,.0f} m | average width {W:.1f} m | length/width {L/W if W else 0:.0f}x | edge on a road {touch:.0f} m | walkway links {tw:.0f} m')
    return dict(area=poly.area,L=L,W=W,road_edge=touch)
o=os_test(rpark,'Riverside promenade')
p_=G(S['parks']) if S.get('parks') else None
print('compact parks:',0 if p_ is None else round(p_.area),'m2')
print('services plot inside the colony boundary:',round(svc.intersection(C).area),'of',round(svc.area),'m2')
json.dump(dict(os=o),open('ostest_'+TAG+'.json','w'))
