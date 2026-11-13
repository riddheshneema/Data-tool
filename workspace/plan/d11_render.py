import json, sys, os, csv, warnings
import numpy as np
warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Patch, FancyArrow
from shapely import wkt, maximum_inscribed_circle
from shapely.geometry import box, Point, LineString, Polygon
from shapely.ops import unary_union
import ezdxf
D='/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/plan/'
sys.path.insert(0,D); import d10, d8
OUT='/home/user/Data-tool/site_plans/'; os.makedirs(OUT,exist_ok=True)
args=json.loads(sys.argv[1]); TAG=sys.argv[2]; TITLE=sys.argv[3]
OPT=args['option']
DW=args.get('drive_w',12)
r=d10.plan(args['th'],args['y0'],args['pw'],args['pd'],OPT,return_geom=True,drive_w=DW); g=r['geom']
G=wkt.loads; SQFT=10.7639; ACRE=4046.86
C,RS,R,roads,row,gard,rpark,access=[G(g[k]) for k in ('C','RESORT','R','roads','row','gardens','river_park','access')]
from shapely.geometry import Polygon as _Poly
_ae=[(338.5,-261.9),(337.4,-284.6),(335.7,-304.0),(334.8,-326.0),(336.7,-358.3)]
access=unary_union([access,_Poly(_ae+[(x-15.0,y) for x,y in _ae][::-1])]).buffer(0)   # public access road: uniform 15 m
park=G(g['park']) if g.get('park') else None
plots=[[G(s),k] for s,k in g['plots']]
front=lambda p:p.buffer(0.8).intersection(row).area/0.8
# merge any plot without road frontage into the neighbour it shares the longest edge with
changed=True
while changed:
    changed=False
    for i,(p,k) in enumerate(plots):
        if front(p)<12:
            nb=[(p.buffer(0.3).intersection(q).area,j) for j,(q,_) in enumerate(plots) if j!=i]
            j=max(nb)[1]; plots[j][0]=unary_union([p,plots[j][0]]).buffer(0.01).buffer(-0.01); plots.pop(i); changed=True; break
FT=0.3048
GATE=Point(331,-262)
def cap(k): return (10000 if k=='River-front villa' else 7500)/SQFT
def cap_ext(k): return (13000 if k=='River-front villa' else 9000)/SQFT
# 0) every road must connect to the colony gate: link any isolated street to the network
from shapely.ops import nearest_points
def components(g0): return [q for q in getattr(g0,'geoms',[g0]) if q.geom_type=='Polygon' and q.area>5]
def gate_network():
    comps=components(row.buffer(0.4).buffer(-0.4)); return min(comps,key=lambda q:q.distance(GATE)), comps
main,comps=gate_network(); links=[]
for q in sorted(comps,key=lambda q:q.distance(main)):
    if q.distance(main)<0.6: continue
    a_,b_=nearest_points(q,main)
    # a proper full-width link: join the end of the isolated street and the nearby end of the network
    qe=q.intersection(a_.buffer(14)); me=main.intersection(b_.buffer(14))
    lk=unary_union([qe,me]).convex_hull.intersection(C).difference(rpark).buffer(0)
    # make sure it is at least 9 m wide everywhere: widen inward if the boundary squeezed it
    if lk.buffer(-5.9).is_empty or lk.area<12*a_.distance(b_):
        lk=unary_union([lk,LineString([a_,b_]).buffer(6,cap_style=2)]).buffer(6).buffer(-6).intersection(C).difference(rpark).buffer(0)
    links.append(lk)
    main=unary_union([main,q,links[-1]])
if links:
    L_=unary_union(links).intersection(C).difference(rpark).buffer(0)
    row=unary_union([row,L_]).buffer(0); roads=unary_union([roads,L_]).buffer(0)
    newp=[]
    for p,k in plots:
        q=p.difference(L_.buffer(0.05)).buffer(0)
        for x in [x for x in getattr(q,'geoms',[q]) if x.geom_type=='Polygon' and x.area>5]:
            if x.area>=3500/SQFT and (d8.good_shape(x) or k=='River-front villa'): newp.append([x,k])
    plots=newp
print('isolated road pieces linked to the gate network:',len(links),'| road components before:',len(comps))
s1=[G(sw) for (j,sw,mw) in r['per_street'] if j==r['ids'][0]]
if s1:
    s1=s1[0]; c=np.array(s1.minimum_rotated_rectangle.exterior.coords)[:4]
    e=[c[1]-c[0],c[3]-c[0]]; Lx=max(e,key=np.linalg.norm); u=Lx/np.linalg.norm(Lx)
    if u[1]>0: u=-u                                  # point south
    Wd=min(np.linalg.norm(e[0]),np.linalg.norm(e[1]))
    pts=np.array(s1.exterior.coords); cen=np.array(s1.centroid.coords[0])
    c0=cen+u*((pts@u).max()-cen@u)
    ext_=LineString([tuple(c0-u*1.0),tuple(c0+u*70)]).buffer(Wd/2,cap_style=2).intersection(C).difference(rpark).buffer(0)
    ext_=max(getattr(ext_,'geoms',[ext_]),key=lambda q:q.area) if not ext_.is_empty else ext_
    if not ext_.is_empty and ext_.area>30:
        row=unary_union([row,ext_]).buffer(0); roads=unary_union([roads,ext_]).buffer(0)
        newp=[]
        for p,k in plots:
            q=p.difference(ext_.buffer(0.05)).buffer(0)
            for x in [x for x in getattr(q,'geoms',[q]) if x.geom_type=='Polygon' and x.area>5]:
                if x.area>=3500/SQFT and (d8.good_shape(x) or k=='River-front villa'): newp.append([x,k])
        plots=newp
        print('S1 extended south by about',round(ext_.area/Wd),'m')
# 1) one 7 ft walkway from the river drive to the promenade garden, between two river plots near the middle
promline=C.intersection(R.buffer(15).exterior)
promline=max(getattr(promline,'geoms',[promline]),key=lambda q:q.length)
rv=[(promline.project(p.centroid),i) for i,(p,k) in enumerate(plots) if k=='River-front villa']
rv.sort(); walk=box(0,0,0,0)
if len(rv)>=2:
    mid=promline.length/2
    pairs=[(abs((rv[q][0]+rv[q+1][0])/2-mid),rv[q][1],rv[q+1][1]) for q in range(len(rv)-1)]
    for _,i1,i2 in sorted(pairs):
        w_=plots[i1][0].buffer(7*FT/2).intersection(plots[i2][0].buffer(7*FT/2)).difference(rpark)
        if w_.area>20:
            walk=w_.buffer(0)
            plots[i1][0]=plots[i1][0].difference(walk).buffer(0); plots[i2][0]=plots[i2][0].difference(walk).buffer(0); break
# 2) utilities: one shared services plot on the resort side of the colony gate, next to the transformer
def free_space():
    pu=unary_union([p for p,_ in plots])
    return C.difference(row).difference(rpark).difference(pu).difference(walk).buffer(-0.2).buffer(0.2)
svc_site=box(300,-286,323,-264).intersection(RS).difference(access.buffer(0.5))
util={'STP (sewage treatment)':box(302,-284,312,-276).intersection(svc_site),
      'Overhead tank + tubewell':box(314,-283,321,-276).intersection(svc_site),
      'Waste point':box(302,-273,307,-269).intersection(svc_site)}
uu=box(0,0,0,0)          # nothing inside the colony
svc=svc_site
# 3a) re-cut: share leftover wedges among the neighbouring plots, adding a plot where it fits
from shapely.geometry import Polygon as _P, LineString as _L
from shapely.ops import linemerge as _lm
def relaxed_shape(p,pie=False):
    if p.geom_type!='Polygon' or p.is_empty: return False
    mrr=p.minimum_rotated_rectangle; c=list(mrr.exterior.coords)
    a_=Point(c[0]).distance(Point(c[1])); b_=Point(c[1]).distance(Point(c[2]))
    if min(a_,b_)<(9 if pie else 10) or max(a_,b_)/min(a_,b_)>3.5 or p.area/mrr.area<(0.55 if pie else 0.65): return False
    q=p.simplify(1.2); pts=list(q.exterior.coords)[:-1]; n=len(pts)
    if n>8: return False
    for i in range(n):
        p0,p1,p2=np.array(pts[i-1]),np.array(pts[i]),np.array(pts[(i+1)%n]); v1,v2=p0-p1,p2-p1
        l1,l2=np.linalg.norm(v1),np.linalg.norm(v2)
        if min(l1,l2)<2.5: continue
        if np.degrees(np.arccos(np.clip(np.dot(v1,v2)/(l1*l2),-1,1)))<(40 if pie else 50): return False
    return True
def frontage_line(Z):
    fr=Z.boundary.intersection(row.buffer(0.6))
    parts=[q for q in getattr(fr,'geoms',[fr]) if q.geom_type=='LineString' and not q.is_empty and q.length>0.3]
    if not parts: return None
    m=_lm(parts) if len(parts)>1 else parts[0]
    ls=[q for q in getattr(m,'geoms',[m]) if q.geom_type=='LineString']
    return max(ls,key=lambda q:q.length) if ls else None
def extend_line(L,ext=60):
    c=list(L.coords); a_,b_=np.array(c[0]),np.array(c[1]); y_,z_=np.array(c[-2]),np.array(c[-1])
    d0=(a_-b_)/(np.linalg.norm(a_-b_) or 1); d1=(z_-y_)/(np.linalg.norm(z_-y_) or 1)
    return _L([tuple(a_+d0*ext)]+c+[tuple(z_+d1*ext)])
def nrm_at(L,t):
    a_,b_=L.interpolate(max(t-1,0)),L.interpolate(min(t+1,L.length)); dx,dy=b_.x-a_.x,b_.y-a_.y; n=np.hypot(dx,dy) or 1
    return np.array([-dy/n,dx/n])
def slab(L,ta,tb,H=160):
    pa,pb=np.array(L.interpolate(ta).coords[0]),np.array(L.interpolate(tb).coords[0]); na,nb=nrm_at(L,ta),nrm_at(L,tb)
    return _P([tuple(pa+na*H),tuple(pb+nb*H),tuple(pb-nb*H),tuple(pa-na*H)]).buffer(0)
from shapely.ops import substring as _sub
from shapely import affinity as _aff
_dc=15+args['pd']*FT*1.1+DW/2
_CL=C.intersection(R.buffer(_dc).exterior); _CL=_lm(_CL) if _CL.geom_type=='MultiLineString' else _CL
_CL=max([q for q in getattr(_CL,'geoms',[_CL]) if q.geom_type=='LineString'],key=lambda q:q.length)
def river_guide(Z):
    t=[_CL.project(Point(c)) for c in Z.exterior.coords]
    a_,b_=max(min(t)-3,0),min(max(t)+3,_CL.length)
    return _sub(_CL,a_,b_) if b_-a_>12 else None
def recut(Z,n,kind):
    L=river_guide(Z) if kind=='River-front villa' else frontage_line(Z)
    if L is None or L.length<12: return None
    Le=extend_line(L); ts=np.arange(0.5,Le.length,0.5)
    cum=np.array([Z.intersection(slab(Le,0,t)).area for t in ts]); tot=Z.area
    cuts=[0.0]
    for k in range(1,n):
        cuts.append(float(ts[np.searchsorted(cum,tot*k/n)]) if np.searchsorted(cum,tot*k/n)<len(ts) else Le.length)
    cuts.append(Le.length)
    out=[]
    for ta,tb in zip(cuts[:-1],cuts[1:]):
        q=Z.intersection(slab(Le,ta,tb))
        parts=[x for x in getattr(q,'geoms',[q]) if x.geom_type=='Polygon' and x.area>1]
        if not parts: return None
        main=max(parts,key=lambda x:x.area)
        if main.area<0.97*q.area: return None
        ok=(3500/SQFT<=main.area<=(cap_ext(kind) if kind=='River-front villa' else cap(kind)) and front(main)>=12 and (relaxed_shape(main,pie=True) if kind=='River-front villa' else (d8.good_shape(main) or relaxed_shape(main))))
        if not ok: return None
        out.append(main)
    return out
def clean(m):
    m2=m.buffer(-1.2,join_style=2).buffer(1.2,join_style=2).buffer(0)
    if m2.is_empty: return m
    if m2.geom_type=='MultiPolygon': m2=max(m2.geoms,key=lambda q:q.area)
    return m2.intersection(C).difference(row).difference(rpark).difference(walk).buffer(0)
# 2b) balance the river-front plots along each continuous run (R1 smaller, R9 bigger), absorbing the wedges behind them
def river_runs():
    idx=[i for i,(p,k) in enumerate(plots) if k=='River-front villa']
    nb={i:set() for i in idx}
    for a in idx:
        for b in idx:
            if a<b and plots[a][0].buffer(0.6).intersects(plots[b][0]): nb[a].add(b); nb[b].add(a)
    seen=set(); runs=[]
    for i in idx:
        if i in seen: continue
        st=[i]; comp=[]
        while st:
            x=st.pop()
            if x in seen: continue
            seen.add(x); comp.append(x); st+=list(nb[x]-seen)
        runs.append(comp)
    return runs
done_sig=set(); bal=0
for it in range(12):
    runs=[rn for rn in river_runs() if len(rn)>=2 and tuple(np.round(unary_union([plots[i][0] for i in rn]).centroid.coords[0])) not in done_sig]
    if not runs: break
    run=runs[0]; sig=None
    fs=free_space()
    others=unary_union([plots[j][0] for j in range(len(plots)) if j not in run]) if len(plots)>len(run) else Polygon()
    wedges=[q for q in getattr(fs,'geoms',[fs]) if q.geom_type=='Polygon' and q.area>=10
            and any(q.buffer(0.6).intersects(plots[i][0]) for i in run) and q.buffer(0.6).intersection(others).area<1.0]
    Z=unary_union([plots[i][0].buffer(0.3) for i in run]+[w.buffer(0.3) for w in wedges]).buffer(-0.3)
    Z=Z.intersection(C).difference(row).difference(rpark).difference(walk).buffer(0)
    n0=len(run); best=None
    if Z.geom_type=='Polygon':
        for n in range(max(n0,int(Z.area//(6000/SQFT))),n0-1,-1):
            res=recut(Z,n,'River-front villa')
            if res: best=res; break
    if best and sum(x.area for x in best)>=sum(plots[i][0].area for i in run)-1:
        for i in sorted(run,reverse=True): plots.pop(i)
        for x in best: plots.append([x,'River-front villa'])
        bal+=len(best)-n0
        sig=tuple(np.round(unary_union(best).centroid.coords[0]))
    else:
        sig=tuple(np.round(unary_union([plots[i][0] for i in run]).centroid.coords[0]))
    done_sig.add(sig)
print('river runs re-balanced; plots gained',bal)
# 2c) island blocks (roads on several sides, e.g. the triangle): plots facing every side
blocks=C.difference(row).difference(rpark).difference(walk).buffer(-0.05).buffer(0.05)
isl=0
for Bk in [b for b in getattr(blocks,'geoms',[blocks]) if b.geom_type=='Polygon' and b.area>800]:
    inside=[i for i,(p,k) in enumerate(plots) if p.representative_point().within(Bk)]
    if any(plots[i][1]=='River-front villa' for i in inside): continue
    used=unary_union([plots[i][0] for i in inside]) if inside else Polygon()
    if Bk.difference(used).area<250: continue
    fr=Bk.boundary.intersection(row.buffer(0.6))
    parts=[q for q in getattr(fr,'geoms',[fr]) if q.geom_type=='LineString' and q.length>0.3]
    if not parts: continue
    mm=_lm(parts); sides=sorted([q for q in getattr(mm,'geoms',[mm]) if q.geom_type=='LineString' and q.length>=15],key=lambda q:-q.length)
    remaining=Bk; new=[]
    for sd in sides:
        strip=remaining.intersection(sd.buffer(90*FT+0.5)).buffer(0)
        cand=[q for q in getattr(strip,'geoms',[strip]) if q.geom_type=='Polygon']
        if not cand: continue
        strip=max(cand,key=lambda q:q.area)
        if strip.area<3500/SQFT: continue
        got=None
        for n in range(max(int(strip.area//(4500/SQFT)),1),0,-1):
            res=recut(strip,n,'Villa')
            if res: got=res; break
        if got:
            new+=got; remaining=remaining.difference(unary_union(got).buffer(0.01)).buffer(0)
    if len(new)>len(inside) or (len(new)==len(inside) and new and sum(x.area for x in new)>used.area):
        for i in sorted(inside,reverse=True): plots.pop(i)
        for x in new: plots.append([x,'Villa'])
        isl+=len(new)-len(inside)
print('island blocks re-planned; plots gained',isl)
def side_fill(region,depth=90*FT+0.5):
    fr=region.boundary.intersection(row.buffer(0.6))
    parts=[q for q in getattr(fr,'geoms',[fr]) if q.geom_type=='LineString' and q.length>0.3]
    if not parts: return []
    mm=_lm(parts); sides=sorted([q for q in getattr(mm,'geoms',[mm]) if q.geom_type=='LineString' and q.length>=14],key=lambda q:-q.length)
    remaining=region; new=[]
    for sd in sides:
        strip=remaining.intersection(sd.buffer(depth)).buffer(0)
        cand=[q for q in getattr(strip,'geoms',[strip]) if q.geom_type=='Polygon']
        if not cand: continue
        strip=max(cand,key=lambda q:q.area)
        if strip.area<3500/SQFT: continue
        for n in range(max(int(strip.area//(4300/SQFT)),1),0,-1):
            res=recut(strip,n,'Villa')
            if res:
                new+=res; remaining=remaining.difference(unary_union(res).buffer(0.01)).buffer(0); break
    return new
fp=0
fs=free_space()
for P in sorted([q for q in getattr(fs,'geoms',[fs]) if q.geom_type=='Polygon' and q.area>=320],key=lambda q:-q.area):
    for x in side_fill(P): plots.append([x,'Villa']); fp+=1
print('free pieces filled with plots:',fp)
# 2d) pairwise balancing of neighbouring river plots (R1 smaller / R9 bigger), absorbing any wedge between them,
#     and adding a plot when two neighbours plus the wedge are big enough for three
pb=0
for it in range(6):
    changed=False
    ridx=[i for i,(p,k) in enumerate(plots) if k=='River-front villa']
    pairs=sorted([(max(plots[a][0].area,plots[b][0].area)/min(plots[a][0].area,plots[b][0].area),a,b) for a in ridx for b in ridx
                  if a<b and plots[a][0].buffer(2.5).intersects(plots[b][0]) and plots[a][0].distance(plots[b][0])<2.0],reverse=True)
    fs=free_space()
    for ratio,a,b in pairs:
        wed=[q for q in getattr(fs,'geoms',[fs]) if q.geom_type=='Polygon' and q.area>=5 and q.buffer(0.6).intersects(plots[a][0]) and q.buffer(0.6).intersects(plots[b][0])]
        if ratio<1.3 and not wed: continue
        U=unary_union([plots[a][0].buffer(0.3),plots[b][0].buffer(0.3)]+[w.buffer(0.3) for w in wed]).buffer(-0.3)
        U=U.intersection(C).difference(row).difference(rpark).difference(walk).buffer(0)
        if U.geom_type!='Polygon': continue
        res=None
        for n in ((3,2) if U.area>=3*5200/SQFT else (2,)):
            res=recut(U,n,'River-front villa')
            if res: break
        if res and sum(x.area for x in res)>=plots[a][0].area+plots[b][0].area-1:
            for i in sorted([a,b],reverse=True): plots.pop(i)
            for x in res: plots.append([x,'River-front villa'])
            pb+=len(res)-2; changed=True; break
    if not changed: break
print('river neighbours balanced; plots gained',pb)
recut_gain=0
for it in range(6):
    fs=free_space()
    done=False
    for P in sorted([q for q in getattr(fs,'geoms',[fs]) if q.geom_type=='Polygon' and q.area>=60],key=lambda q:-q.area):
        adj=[i for i in range(len(plots)) if P.buffer(0.5).intersection(plots[i][0]).area>1.0]
        if not adj: continue
        kinds=[plots[i][1] for i in adj]; kind=max(set(kinds),key=kinds.count)
        adj=[i for i in adj if plots[i][1]==kind]
        # grow the zone by one neighbour on each side along the same street for room to re-balance
        Z=unary_union([P.buffer(0.3)]+[plots[i][0].buffer(0.3) for i in adj]).buffer(-0.3)
        Z=Z.intersection(C).difference(row).difference(rpark).difference(walk).buffer(0)
        if Z.geom_type!='Polygon': continue
        target=(6000 if kind=='River-front villa' else 4500)/SQFT
        res=None
        for n in sorted({max(len(adj)+1,int(Z.area//target)),len(adj)+1,len(adj)},reverse=True):
            if n<len(adj): continue
            res=recut(Z,n,kind)
            if res: break
        if res and (len(res)>len(adj) or sum(x.area for x in res)>sum(plots[i][0].area for i in adj)+20):
            for i in sorted(adj,reverse=True): plots.pop(i)
            for x in res: plots.append([x,kind])
            recut_gain+=len(res)-len(adj); done=True; break
    if not done: break
print('re-cut: plots gained',recut_gain)
# 3) infill: turn leftover land that fronts a road into plots
def frontage_dir(P):
    fr=P.boundary.intersection(row.buffer(0.6))
    from shapely.ops import linemerge as _lm
    if fr.geom_type in ('MultiLineString','GeometryCollection'):
        parts=[q for q in getattr(fr,'geoms',[fr]) if q.geom_type=='LineString' and not q.is_empty]
        fr=_lm(parts) if parts else fr
    ls=[q for q in getattr(fr,'geoms',[fr]) if q.geom_type=='LineString' and not q.is_empty and q.length>0.5]
    if not ls: return None,0
    Lm=max(ls,key=lambda q:q.length); tot=sum(q.length for q in ls)
    (x0,y0_),(x1,y1)=Lm.coords[0],Lm.coords[-1]; u=np.array([x1-x0,y1-y0_]); n_=np.linalg.norm(u)
    return (u/n_ if n_>0 else None),tot
added=0
for it in range(3):
    fs=free_space().difference(uu.buffer(0.5))
    for P in sorted([q for q in getattr(fs,'geoms',[fs]) if q.geom_type=='Polygon' and q.area>=300],key=lambda q:-q.area):
        u,tot=frontage_dir(P)
        if u is None or tot<12: continue
        river=P.distance(rpark)<1.0
        W=(60 if river else 45)*FT
        nv=np.array([-u[1],u[0]]); pts=np.array(P.exterior.coords)
        sv=pts@u; s0,s1=sv.min(),sv.max(); best=None
        for off in np.linspace(0,W,5,endpoint=False):
            cells=[]
            for s in np.arange(s0-off,s1,W):
                a_=u*s; b_=u*(s+W); big=500
                slab=Polygon([tuple(a_+nv*big),tuple(b_+nv*big),tuple(b_-nv*big),tuple(a_-nv*big)]) if False else None
                from shapely.geometry import Polygon as _P
                slab=_P([tuple(a_+nv*big),tuple(b_+nv*big),tuple(b_-nv*big),tuple(a_-nv*big)])
                c_=P.intersection(slab)
                for q in getattr(c_,'geoms',[c_]):
                    if q.geom_type=='Polygon' and q.area>5: cells.append(q)
            cells=d8.merge_small(cells,3500/SQFT,cap('River-front villa' if river else 'Villa'))
            cells=[clean(q) for q in cells]
            ok=[q for q in cells if q.geom_type=='Polygon' and 3500/SQFT<=q.area<=cap_ext('River-front villa' if river else 'Villa') and (d8.good_shape(q) or relaxed_shape(q,pie=river)) and front(q)>=12]
            if best is None or sum(q.area for q in ok)>sum(q.area for q in best): best=ok
        for q in best or []:
            plots.append([q,'River-front villa' if river else 'Villa']); added+=1
# 4) extend: merge remaining leftover pieces into the neighbouring plot when the plot stays regular
ext=0
for it in range(4):
    fs=free_space().difference(uu.buffer(0.5))
    changed=False
    for P in [q for q in getattr(fs,'geoms',[fs]) if q.geom_type=='Polygon' and q.area>=8]:
        nb=sorted([(P.buffer(0.4).intersection(plots[i][0]).area,i) for i in range(len(plots))],reverse=True)
        for sh,i in nb[:3]:
            if sh<1.0: break
            m=unary_union([plots[i][0],P.buffer(0.3)]).buffer(-0.3).buffer(0.0)
            m=clean(m.intersection(C).difference(row).difference(rpark).difference(walk).difference(uu).buffer(0))
            if m.geom_type!='Polygon': continue
            if m.area<=cap(plots[i][1]) and (d8.good_shape(m) or relaxed_shape(m)):
                plots[i][0]=m; ext+=1; changed=True; break
    if not changed: break
# 4b) grow plots straight outward (rectangular extensions) into any free land next to them
def prism_extend():
    cnt=0
    for it in range(4):
        fs=free_space(); changed=False
        for i in range(len(plots)):
            p,k=plots[i]
            c=np.array(p.minimum_rotated_rectangle.exterior.coords)[:4]
            e1=c[1]-c[0]; e2=c[3]-c[0]; best=None
            for ax_ in (e1,-e1,e2,-e2):
                u=ax_/np.linalg.norm(ax_)
                band=Polygon([tuple(x) for x in c]).buffer(0)
                sweep=unary_union([band,_aff.translate(band,u[0]*35,u[1]*35)]).convex_hull
                gain=sweep.intersection(fs).buffer(0)
                gl=[q for q in getattr(gain,'geoms',[gain]) if q.geom_type=='Polygon' and q.area>15 and q.buffer(0.5).intersects(p)]
                if not gl: continue
                m=unary_union([p]+[q.buffer(0.2) for q in gl]).buffer(-0.2)
                m=clean(m.intersection(C).difference(row).difference(rpark).difference(walk).buffer(0))
                if m.geom_type!='Polygon' or m.area>cap_ext(k) or m.area<p.area+15: continue
                if not (d8.good_shape(m) or relaxed_shape(m,pie=(k=='River-front villa'))): continue
                if best is None or m.area>best.area: best=m
            if best is not None:
                plots[i][0]=best; changed=True; cnt+=1; fs=free_space()
        if not changed: break
    return cnt
print('plots grown straight into free land:',prism_extend())
import pickle as _pk
_pk.dump(dict(plots=[(p.wkt,k) for p,k in plots],row=row.wkt,rpark=rpark.wkt,walk=walk.wkt,C=C.wkt),open(D+'state_'+TAG+'.pkl','wb'))
# 5) split each remaining piece among its neighbouring plots (nearest-plot partition) and enlarge them
from shapely import voronoi_polygons
from shapely.geometry import MultiPoint
part_ext=0
for it in range(3):
    fs=free_space()
    changed=False
    for P in sorted([q for q in getattr(fs,'geoms',[fs]) if q.geom_type=='Polygon' and q.area>=30],key=lambda q:-q.area):
        nb=[i for i in range(len(plots)) if P.buffer(0.6).intersection(plots[i][0]).area>1.0]
        if len(nb)<1: continue
        pts=[];lab=[]
        for i in nb:
            bd=plots[i][0].exterior
            for t in np.arange(0,bd.length,1.5): q=bd.interpolate(t); pts.append((q.x,q.y)); lab.append(i)
        if len(pts)<4: continue
        vd=voronoi_polygons(MultiPoint(pts),extend_to=P.buffer(50))
        cells={i:[] for i in nb}
        from shapely import STRtree
        tree=STRtree([Point(p) for p in pts])
        for cell in vd.geoms:
            hit=tree.query(cell,predicate='contains')
            if len(hit): cells[lab[int(hit[0])]].append(cell)
        new={}
        okall=True
        for i in nb:
            if not cells[i]: continue
            part=unary_union(cells[i]).intersection(P)
            if part.area<1: continue
            m=unary_union([plots[i][0],part.buffer(0.2)]).buffer(-0.2)
            m=clean(m.intersection(C).difference(row).difference(rpark).difference(walk).buffer(0))
            if m.geom_type!='Polygon' or m.area>cap_ext(plots[i][1]) or not (d8.good_shape(m) or relaxed_shape(m)):
                okall=False; break
            new[i]=m
        if okall and new:
            for i,m in new.items(): plots[i][0]=m
            part_ext+=len(new); changed=True
    if not changed: break
print('infill plots added',added,'| plots extended',ext,'| enlarged by splitting leftovers',part_ext,'| walkway m2',round(walk.area))
# 6) final check: every plot must front a road that connects to the colony gate
main,comps=gate_network()
noacc=[i for i,(p,k) in enumerate(plots) if p.buffer(0.8).intersection(main).area/0.8<12]
print('road network pieces:',len(comps),'| plots without access to the gate network:',len(noacc))
for i in sorted(noacc,reverse=True): plots.pop(i)
# let the neighbours take the land freed by any removed plot
print('plots grown into land freed by removed plots:',prism_extend())
# split extra-large villa plots into two normal plots, cutting across the road frontage
from shapely.ops import split as _split
def split_large():
    n_=0
    for i in range(len(plots)-1,-1,-1):
        p,k=plots[i]
        if k!='Villa' or p.area*SQFT<7200: continue
        cc=list(p.minimum_rotated_rectangle.exterior.coords); cx,cy=p.centroid.x,p.centroid.y
        for (a_,b_) in ((cc[0],cc[1]),(cc[1],cc[2])):
            dx,dy=b_[0]-a_[0],b_[1]-a_[1]; nn=np.hypot(dx,dy); ux,uy=dx/nn,dy/nn
            parts=list(_split(p,LineString([(cx-uy*300,cy+ux*300),(cx+uy*300,cy-ux*300)])).geoms)
            if len(parts)==2 and all(q.area>=3500/SQFT and front(q)>=12 and (d8.good_shape(q) or relaxed_shape(q,pie=True)) for q in parts):
                plots.pop(i); plots.extend([[q,'Villa'] for q in parts]); n_+=1; break
    return n_
sp=split_large()
print('large double-frontage plots split in two:',sp)
# leftover pieces that cannot be a plot on their own: give them to the neighbouring plots
#  - between two plots: cut with a straight line continuing their shared edge
#  - otherwise: the whole piece goes to the plot sharing the longest edge with it
#  every enlarged plot must still pass the shape rule
from shapely import voronoi_polygons as _vp, STRtree as _T
from shapely.geometry import MultiPoint as _MP
def valid_plot(q,kind='Villa'):
    return (q.geom_type=='Polygon' and 3500/SQFT<=q.area<=cap_ext(kind) and front(q)>=12 and (d8.good_shape(q) or relaxed_shape(q,pie=True)))
def grow(i,part,limit=12000):
    m=unary_union([plots[i][0],part.buffer(0.2)]).buffer(-0.2).intersection(C).difference(row).difference(rpark).difference(walk).buffer(0)
    if m.geom_type=='Polygon' and m.area*SQFT<=limit and (d8.good_shape(m) or relaxed_shape(m,pie=True)): return m
    return None
ll=0
fs=free_space()
for P in [q for q in getattr(fs,'geoms',[fs]) if q.geom_type=='Polygon' and q.area>=40 and not valid_plot(q)]:
    nb=[i for i in range(len(plots)) if P.buffer(0.6).intersection(plots[i][0]).area>1.0]
    if not nb: continue
    done_=False
    if len(nb)==2:
        sh=plots[nb[0]][0].buffer(0.4).intersection(plots[nb[1]][0].buffer(0.4))
        if sh.area>0.5:
            cc=np.array(sh.minimum_rotated_rectangle.exterior.coords)[:4]; ee=[cc[1]-cc[0],cc[3]-cc[0]]; dv=max(ee,key=np.linalg.norm); dv=dv/np.linalg.norm(dv)
            mid=np.array(sh.centroid.coords[0]); cut=LineString([tuple(mid-dv*200),tuple(mid+dv*200)])
            parts=[x for x in getattr(_split(P,cut),'geoms',[P]) if x.area>1]
            new_={}
            for x in parts:
                i=min(nb,key=lambda i:x.distance(plots[i][0]))
                base=new_.get(i,plots[i][0])
                m=unary_union([base,x.buffer(0.2)]).buffer(-0.2).intersection(C).difference(row).difference(rpark).difference(walk).buffer(0)
                if m.geom_type=='Polygon' and m.area*SQFT<=12000 and (d8.good_shape(m) or relaxed_shape(m,pie=True)): new_[i]=m
                else: new_=None; break
            if new_:
                for i,m in new_.items(): plots[i][0]=m
                ll+=1; done_=True
    if not done_:
        # whole piece to the neighbour that ends up with the cleanest shape
        opts=[(i,grow(i,P,limit=13000)) for i in nb]
        opts=[(i,m) for i,m in opts if m is not None]
        if opts:
            i,m=max(opts,key=lambda t:t[1].area/t[1].minimum_rotated_rectangle.area)
            plots[i][0]=m; ll+=1
print('land-locked pieces shared with neighbouring plots:',ll)
print('large plots split after merges:',split_large())
# manual edits agreed with the owner (re-cut plots, new plots), applied before parks and numbering
import os as _os, json as _js
FIX=[]
_ef=D+'edits_'+TAG+'.json'
if _os.path.exists(_ef):
    _E=_js.load(open(_ef))
    for pt in _E['remove']:
        plots=[pk for pk in plots if not pk[0].contains(Point(pt))]
    for w_,k_,t_ in _E['add']:
        q_=G(w_); plots.append([q_,k_]); FIX.append((q_.representative_point(),t_))
    if _E.get('road_add'):
        # road land taken from plots (e.g. S1 kept 12 m to its end): join it to the road, never over a plot
        _pu=unary_union([p for p,_ in plots]).buffer(0.01)
        _ra=G(_E['road_add']).buffer(0.05).intersection(C).difference(_pu).difference(rpark).buffer(0)
        row=unary_union([row,_ra]).buffer(0); roads=unary_union([roads,_ra]).buffer(0)
    if _E.get('road_remove'):
        _rr=G(_E['road_remove']); row=row.difference(_rr).buffer(0); roads=roads.difference(_rr).buffer(0)
    FIX+=[(Point(pt),t_) for pt,t_ in _E.get('keep_tags',[])]
    _main,_=gate_network()
    print('manual edits applied:',len(_E['remove']),'removed,',len(_E['add']),'added | plots without 12 m access now:',
          sum(p.buffer(0.8).intersection(_main).area/0.8<12 for p,_ in plots))
plotu=unary_union([p for p,_ in plots])
left=C.difference(roads).difference(gard).difference(rpark).difference(plotu).difference(walk).difference(uu)
if park is not None: left=left.difference(park)
left=left.buffer(-0.2).buffer(0.2)
def park_test(p):
    mrr=p.minimum_rotated_rectangle; c=list(mrr.exterior.coords)
    L=max(Point(c[0]).distance(Point(c[1])),Point(c[1]).distance(Point(c[2]))); w=p.area/L
    return p.area>=450 and w>=7.5 and (w>=24 or L<=2.5*w)
pieces=[p for p in getattr(left,'geoms',[left]) if p.geom_type=='Polygon' and p.area>15]
rest=left.buffer(-0.1).buffer(0.1)
rp=[p for p in getattr(rest,'geoms',[rest]) if p.geom_type=='Polygon' and p.area>5]
parks=unary_union([p for p in rp if park_test(p)]) if any(park_test(p) for p in rp) else box(0,0,0,0)
corners=unary_union([p for p in rp if not park_test(p)]) if rp else box(0,0,0,0)
boul=G(r['boul'])
big_green=unary_union([p for p in getattr(corners,'geoms',[corners]) if p.geom_type=='Polygon' and p.area>=150]) if not corners.is_empty else box(0,0,0,0)
parks_any=unary_union([x for x in [parks,park,big_green] if x is not None and not x.is_empty])
def other_view(p,k):
    if k=='River-front villa' and p.distance(rpark)<1.0: return True
    return (not parks_any.is_empty) and p.distance(parks_any)<=13.0
keep=[]
for (j,sw,mw) in r['per_street']:
    if j not in r['gs']: continue
    st=G(sw); med=gard.intersection(st.buffer(0.5)).difference(boul.buffer(2))
    for p,k in plots:
        if p.buffer(0.8).intersection(st).area>8 and not other_view(p,k):
            keep.append(med.intersection(p.buffer(9)))
medians=unary_union([x for x in keep if not x.is_empty]).buffer(0) if keep else box(0,0,0,0)
roads=unary_union([roads,gard.difference(medians)]).buffer(0)
gard=medians
try:
    import json as _jm
    _Em=_jm.load(open(D+'edits_'+TAG+'.json'))
    if _Em.get('median_remove'):
        _mr=gard.intersection(G(_Em['median_remove']))
        if not _mr.is_empty: gard=gard.difference(_mr).buffer(0); roads=unary_union([roads,_mr]).buffer(0)
except FileNotFoundError: pass
# no garden median inside a dead-end turning space (BVN Rule 43): the median stops short, the space is paved
try:
    import json as _jt
    for _d in _jt.load(open(D+'deadends_'+TAG+'.json')):
        if _d.get('tbox'):
            _rm=gard.intersection(unary_union([G(_d['tbox']).buffer(1.5),Point(_d['end']).buffer((_d.get('back') or 0)+13)]))   # from the turning space to the road end
            if not _rm.is_empty: gard=gard.difference(_rm).buffer(0); roads=unary_union([roads,_rm]).buffer(0)
    # median stubs left between a turning space and the road end are paved too
    _stubs=[q for q in getattr(gard,'geoms',[gard]) if q.geom_type=='Polygon' and q.area<25]
    if _stubs: _su=unary_union(_stubs); gard=gard.difference(_su.buffer(0.01)).buffer(0); roads=unary_union([roads,_su]).buffer(0)
except FileNotFoundError: pass
# number plots: river-front first, then villas, top to bottom
plots.sort(key=lambda t:(t[1]!='River-front villa',-round(t[0].centroid.y/30),t[0].centroid.x))
parks_all=unary_union([x for x in [parks,park,big_green] if x is not None and not x.is_empty])
def faces(p,k):
    if k=='River-front villa' and p.distance(rpark)<1.0: return 'river promenade'
    if not gard.is_empty and p.distance(gard)<=5.5: return 'garden median'
    if not parks_all.is_empty and p.distance(parks_all)<=13.0: return 'park / landscaped green'
    return ''
# ---------------- drawing ----------------
# the colony's services plot is part of the colony layout, so it can be handed to the Gram Panchayat with the roads
svc=box(300,-286,324,-250).intersection(RS).difference(access.buffer(0.5)).buffer(0)
svc=max(getattr(svc,'geoms',[svc]),key=lambda q:q.area)
RS=RS.difference(svc).buffer(0); C=unary_union([C,svc]).buffer(0)
fig=plt.figure(figsize=(16.54,11.69)); ax=fig.add_axes([0.01,0.03,0.6,0.94])
def fill(gm,**kw):
    for p in getattr(gm,'geoms',[gm]):
        if p.geom_type=='Polygon' and not p.is_empty:
            x,y=p.exterior.xy; ax.fill(x,y,**kw)
            for h in p.interiors: hx,hy=h.xy; ax.fill(hx,hy,fc='white',ec='none')
fill(R.intersection(box(90,-580,490,-30)),fc='#9fd3f2',ec='#5aa9d6',lw=0.6)
fill(RS,fc='#f6e6c3',ec='#a8781a',lw=1.3); fill(access,fc='#d0d0d0',ec='#9e9e9e',lw=0.5)
ax.text(255,-400,'RESORT\n(front, by the main entry)\n%.2f acres'%(RS.area/ACRE),ha='center',va='center',fontsize=12,weight='bold',color='#7a5410')
ax.text(318,-380,'PUBLIC ACCESS ROAD 15 m (through resort)',rotation=90,fontsize=6.3,ha='center',va='center')
fill(roads,fc='#d0d0d0',ec='#9e9e9e',lw=0.4)
fill(rpark,fc='#b9dfa6')
pth=C.intersection(R.buffer(8).exterior)
for l in getattr(pth,'geoms',[pth]):
    if l.geom_type=='LineString': ax.plot(*l.xy,color='#d7ccc8',lw=2,solid_capstyle='round')
fill(corners,fc='#c5e1a5'); fill(parks,fc='#7cb342'); fill(walk,fc='#d7b98e',ec='#8d6e63',lw=0.4)
fill(svc,fc='#efebe9',ec='#5d4037',lw=0.6,ls='--')
ax.annotate('COLONY SERVICES PLOT – part of the colony\n(STP + tank + tubewell + waste)\n~%d m², to the Gram Panchayat with the roads'%svc.area,(svc.centroid.x,svc.centroid.y),xytext=(205,-300),fontsize=6,arrowprops=dict(arrowstyle='-',lw=0.5))
if park is not None:
    fill(park,fc='#558b2f',ec='#33691e',lw=0.8)
    ax.text(park.representative_point().x,park.representative_point().y,'CENTRAL\nPARK\n%d m²'%park.area,ha='center',va='center',fontsize=7,weight='bold',color='white')
fill(gard,fc='#2e7d32')
# trees: medians, promenade, avenue trees in river-drive verges, parks
def trees(gm,step,rad,col='#558b2f',inset=0.9):
    for p in getattr(gm,'geoms',[gm]):
        if p.geom_type!='Polygon' or p.area<15: continue
        sk=p.buffer(-inset)
        if sk.is_empty: sk=p
        for e in getattr(sk.boundary,'geoms',[sk.boundary]):
            for t in np.arange(0,e.length,step):
                q=e.interpolate(t); ax.add_patch(plt.Circle((q.x,q.y),rad,fc=col,ec='#33691e',lw=0.3,alpha=0.85))
trees(gard,6,1.2,'#33691e',0.3); trees(rpark,10,2.1); trees(parks,8,1.8)
if park is not None: trees(park,7,1.9,'#33691e')
drive=G(r['drive']) if r.get('drive') else None
rows=[];nr=0;nv=0;gfc=0
_used={t_ for _,t_ in FIX}
def _next(prefix):
    n_=1
    while f'{prefix}{n_}' in _used: n_+=1
    _used.add(f'{prefix}{n_}'); return f'{prefix}{n_}'
for p,k in plots:
    if k=='River-front villa': nr+=1
    else: nv+=1
    tag=next((t_ for pt_,t_ in FIX if p.contains(pt_)),None)
    if tag is None: tag=_next('R' if k=='River-front villa' else 'V')
    a=p.area*SQFT; f=faces(p,k); gfc+=bool(f)
    rows.append((tag,k,round(a),round(p.area,1),round(front(p),1),'Yes' if f else 'No',f))
    fill(p,fc='#fff3d6' if k=='River-front villa' else '#ffffff',ec='#b71c1c',lw=0.7)
    ax.text(p.centroid.x,p.centroid.y,f'{tag}\n{a:,.0f}',fontsize=4.6,ha='center',va='center',color='k' if f else '#b71c1c')
ucol={'STP (sewage treatment)':'#a1887f','Overhead tank + tubewell':'#81d4fa','Waste point':'#e0e0e0','Services plot (STP + tank + tubewell + waste point)':'#bcaaa4'}
for k,v in util.items():
    fill(v,fc=ucol[k],ec='k',lw=0.5); ax.text(v.centroid.x,v.centroid.y,{'STP (sewage treatment)':'STP','Overhead tank + tubewell':'OHT','Waste point':'W','Services plot (STP + tank + tubewell + waste point)':'SERVICES\nSTP+OHT+W'}[k],fontsize=4.6,ha='center',va='center',weight='bold')
ax.plot(337.5,-266,marker='s',ms=4,mfc='#ffd54f',mec='k'); ax.annotate('Transformer (pole-mounted)',(337.5,-266),xytext=(350,-282),fontsize=5.5,arrowprops=dict(arrowstyle='-',lw=0.4))
fill(C,fc='none',ec='#1b5e20',lw=1.5)
import json as _j3
try:
    for _d in _j3.load(open(D+'deadends_'+TAG+'.json')):
        if _d.get('tbox'):
            _b=G(_d['tbox']); ax.fill(*_b.exterior.xy,fc='none',ec='#e65100',lw=0.9,hatch='////',ls='--')
            ax.text(_b.centroid.x,_b.centroid.y,'T',fontsize=6,weight='bold',color='#e65100',ha='center',va='center')
except FileNotFoundError: pass
# road labels
has_med={j:(G(sw).buffer(0.5).intersection(gard).area>20) for (j,sw,mw) in r['per_street']}
for rk,i in enumerate(r['ids'],start=1):
    if rk>4: break
    w=12
    gtxt=' + garden' if has_med.get(i) else ''
    for (j,s,m) in r['per_street']:
        if j==i:
            gs_=G(s); top=max(gs_.exterior.coords if gs_.geom_type=='Polygon' else max(gs_.geoms,key=lambda q:q.area).exterior.coords,key=lambda q:q[1])
            c=gs_.intersection(box(top[0]-15,top[1]-30,top[0]+15,top[1]-6)).representative_point()
            if c.is_empty: c=gs_.representative_point()
            ax.text(c.x,c.y,f'S{rk}\n{w} m{gtxt}',fontsize=5.6,ha='center',va='center',weight='bold',color='#263238',
                    bbox=dict(fc='white',ec='#607d8b',lw=0.4,alpha=0.85,boxstyle='round,pad=0.15'))
if drive is not None:
    c=max(getattr(drive,'geoms',[drive]),key=lambda x:x.area).intersection(box(290,-110,340,-70)).representative_point()
    ax.text(c.x,c.y,f'RD – river drive {DW} m',fontsize=5.6,ha='center',va='center',weight='bold',color='#263238',
            bbox=dict(fc='white',ec='#607d8b',lw=0.4,alpha=0.85,boxstyle='round,pad=0.15'))
ax.text(150,-118,'RIVERSIDE PROMENADE GARDEN (15 m)',color='#33691e',fontsize=7,rotation=52,weight='bold')
ax.text(418,-170.5,'S5  12 m (joins S1 to S2)',fontsize=5.6,ha='center',va='center',weight='bold',color='#263238',rotation=10,bbox=dict(fc='white',ec='#607d8b',lw=0.4,alpha=0.85,boxstyle='round,pad=0.15'))
ax.annotate('MAIN ENTRY',(336,-487),xytext=(345,-566),fontsize=7.5,weight='bold',arrowprops=dict(arrowstyle='->',lw=1))
ax.annotate('COLONY GATE\n12 m entry road',(331,-262),xytext=(360,-305),fontsize=7.2,weight='bold',arrowprops=dict(arrowstyle='->',lw=1))
ax.text(118,-60,'RIVER',color='#1f5f8b',fontsize=10,weight='bold')
ax.set_aspect('equal'); ax.set_xlim(95,480); ax.set_ylim(-575,-40); ax.axis('off')
ax.add_patch(FancyArrow(458,-525,0,28,width=4,head_width=12,head_length=9,color='k')); ax.text(458,-478,'N',ha='center',fontsize=12,weight='bold')
ax.plot([110,160],[-568,-568],'k',lw=3); ax.text(135,-563,'50 m',ha='center',fontsize=7)
# ---------------- statement ----------------
T=C.area
pr=sum(x[3] for x in rows if x[1]=='River-front villa'); pv=sum(x[3] for x in rows if x[1]!='River-front villa'); sale=pr+pv
A=[('River-front villa plots',nr,pr),('Villa plots',nv,pv),
   ('Roads – carriageway and verges','',roads.area),('Garden medians (part of road land)','',gard.area),
   ('Riverside promenade garden (15 m river setback)','',rpark.area)]
if park is not None: A.append(('Central park (triangle block)','',park.area))
A+=[('Other parks that meet the open-space test','',parks.area),('Landscaped corners (too small to count as park)','',corners.area),
    ('7 ft walkway to the promenade garden','',walk.area),('Services plot – STP, tank + tubewell, waste (public utility)','',svc.area)]
os_parks=parks.area+(park.area if park is not None else 0)
t=fig.add_axes([0.63,0.03,0.36,0.94]); t.axis('off')
t.text(0,0.99,TITLE,fontsize=13,weight='bold')
t.text(0,0.968,'Colony at the back (river bend) + resort at the front (main entry) | Survey Drg SU/10/01, 23.325 acres',fontsize=7.4)
y=0.935; t.text(0,y,'AREA STATEMENT – COLONY',fontsize=10,weight='bold'); y-=0.024
xs=[0,0.62,0.69,0.84,0.94]
for x,h in zip(xs,['Use','No.','sq ft','acre','%']): t.text(x,y,h,fontsize=7.5,weight='bold')
y-=0.02
for n,c,a in A:
    for x,v in zip(xs,[n,str(c),f'{a*SQFT:,.0f}',f'{a/ACRE:.2f}',f'{100*a/T:.1f}']): t.text(x,y,v,fontsize=7.0)
    y-=0.0185
for x,v in zip(xs,['Total colony','',f'{T*SQFT:,.0f}',f'{T/ACRE:.2f}','100']): t.text(x,y,v,fontsize=7.5,weight='bold')
y-=0.022; t.text(0,y,f'SELLABLE: {sale*SQFT:,.0f} sq ft = {sale/ACRE:.2f} acres = {100*sale/T:.1f}% of colony  ({len(rows)} plots)',fontsize=8.6,weight='bold',color='#1b5e20')
y-=0.02; t.text(0,y,f'OPEN SPACE meeting the BVN test (parks): {100*os_parks/T:.1f}%  |  with promenade garden: {100*(os_parks+rpark.area)/T:.1f}%  (minimum 10%)',fontsize=7.3,weight='bold')
y-=0.019; t.text(0,y,f'GARDEN VIEW: {gfc} of {len(rows)} plots face the river promenade, a garden median or a park',fontsize=7.3,weight='bold')
y-=0.019; t.text(0,y,f'Resort: {RS.area/ACRE:.2f} acres, incl. the 15 m public access road (~{access.area/ACRE:.2f} acre) to be dedicated as a public road',fontsize=7.0)
pa=[x[2] for x in rows if x[1]=='River-front villa']; va=[x[2] for x in rows if x[1]!='River-front villa']
y-=0.032; t.text(0,y,'PLOT MIX',fontsize=10,weight='bold'); y-=0.02
t.text(0,y,f'{nr} river-front plots {min(pa):,}–{max(pa):,} sq ft (avg {np.mean(pa):,.0f}), backing onto the promenade garden',fontsize=7); y-=0.0175
t.text(0,y,f'{nv} villa plots {min(va):,}–{max(va):,} sq ft (avg {np.mean(va):,.0f}), typical {args["pw"]} x {args["pd"]} ft; no clubhouse',fontsize=7); y-=0.0175
t.text(0,y,'Every plot has direct road frontage and a regular shape (plot numbers in red = no garden view)',fontsize=7); y-=0.03
t.text(0,y,'ROADS',fontsize=10,weight='bold'); y-=0.02
gnames=', '.join(f'S{rk}' for rk,i in enumerate(r['ids'],start=1) if i in r['gs'] and has_med.get(i))
import json as _j2, pickle as _p2
try: _far=max(_p2.load(open(D+'roadtest_'+TAG+'.pkl','rb'))['pdist'].values())
except Exception: _far=None
for s_ in ['Public access road 15 m: main entry → through the resort → colony gate (to be a public street)',
           'Gate entry road 12 m, plain (no plots on one side, so no median)',
           f'RD river drive {DW} m, plain, avenue trees in the verges',
           f'Garden streets {gnames}: 12 m = 4.5 m lane + 3 m garden median + 4.5 m lane',
           'All roads 12 m'+(f' – farthest plot {_far:.0f} m from the gate (12 m allowed up to 400 m, BVN 38)' if _far else ''),
           'S5 12 m link joins S1 to S2 – no bent dead end; S2 stub (V38) and RD south end are straight, each with a 12 x 11 m turning space']:
    t.text(0,y,s_,fontsize=7); y-=0.0175
y-=0.012; t.text(0,y,'DESIGN LOGIC',fontsize=10,weight='bold'); y-=0.02
logic=['River-front plots back onto the riverside promenade garden – no median needed in front of them',
       'A garden median runs only where it gives a plot its garden view – none at the gate entry, none on RD or S1']
logic+=(['Triangle block is the central park (counts as open space); the S4 plots face it, so S4 is a plain 9 m street'] if park is not None
        else ['Garden medians on S2, S3 and S4 give the inner plots their garden view'])
logic+=['Clubhouse and pool removed – they belong in the resort',
        'Leftover strips and corners filled with plots or added to the neighbouring plot',
        'STP, tank + tubewell and waste point in one services plot at the gate, beside the transformer (inside the colony layout)']
for s_ in logic: t.text(0,y,s_,fontsize=7); y-=0.0175
y-=0.012; t.text(0,y,'TO CONFIRM BEFORE APPROVAL',fontsize=10,weight='bold',color='#b71c1c'); y-=0.02
conf=['Narmada: confirm the site is beyond 300 m of the Narmada HFL (this stream is not the Narmada)',
      f'Open space: promenade garden {100*(os_parks+rpark.area)/T:.1f}% (min 10%) – its long shape counts only at T&CP discretion (BVN 47(3))',
      'Dedicate the 15 m access road as a public street before applying (BVN 2(72) + 38(6))',
      'Dedicate the 15 m approach road (main road → main entry) as a public road as well',
      'Stream: survey its highest water level; plots stay 9 m (stream) / 15 m (river) from it (BVN 50(b))',
      'EWS/LIG by shelter fee (no land) – confirm in-lieu option under the 2014 rural rules',
      'Scale calibrated to surveyed areas (~1:858); architect to redraw on the CAD survey',
      'Concept for discussion only – not an approved drawing']
for s_ in conf: t.text(0,y,s_,fontsize=7,color='#b71c1c'); y-=0.0175
LG=[Patch(fc='#fff3d6',ec='#b71c1c',label='River-front plot'),Patch(fc='white',ec='#b71c1c',label='Villa plot'),
    Patch(fc='#d0d0d0',ec='#9e9e9e',label='Road'),Patch(fc='#2e7d32',label='Garden median (road land)'),
    Patch(fc='#b9dfa6',label='Riverside promenade garden'),Patch(fc='#558b2f',label='Park (counts as open space)'),
    Patch(fc='#c5e1a5',label='Landscaped corner'),Patch(fc='#d7b98e',ec='#8d6e63',label='7 ft walkway to promenade'),Patch(fc='none',ec='#e65100',hatch='////',label='T = turning space 12 x 11 m (dead end)'),Patch(fc='#ffffff',ec='#999',label='STP / OHT / W = sewage plant, water tank + tubewell, waste point'),Patch(fc='#f6e6c3',ec='#a8781a',label='Resort')]
t.legend(handles=LG,loc='lower left',fontsize=7.2,frameon=False,ncol=2)
_ord=sorted(range(len(rows)),key=lambda i:(rows[i][0][0]!='R',int(rows[i][0][1:])))
plots=[plots[i] for i in _ord]; rows=[rows[i] for i in _ord]
_streets=[(f'S{rk}',unary_union([G(s_) for (j,s_,m_) in r['per_street'] if j==i]).wkt) for rk,i in enumerate(r['ids'],start=1)]
_pk.dump(dict(plots=[(x[0],p.wkt,k) for (p,k),x in zip(plots,rows)],row=row.wkt,C=C.wkt,rpark=rpark.wkt,
              roads=roads.wkt,gard=gard.wkt,walk=walk.wkt,parks=parks_all.wkt if not parks_all.is_empty else None,
              svc=svc.wkt,access=access.wkt,RS=RS.wkt,R=R.wkt,drive=r.get('drive'),streets=_streets,
              util={k_:v_.wkt for k_,v_ in util.items()}),open(D+'final_'+TAG+'.pkl','wb'))
fig.savefig(OUT+TAG+'.pdf'); fig.savefig(OUT+TAG+'.png',dpi=140)
with open(OUT+TAG+'_Plot_Schedule.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['Plot','Type','Area (sq ft)','Area (sq m)','Road frontage (m)','Garden view','Faces'])
    for x in rows: w.writerow(x)
doc=ezdxf.new('R2010'); msp=doc.modelspace()
for n,c in [('RESORT',2),('COLONY',3),('ROADS',8),('MEDIANS',94),('PLOTS',1),('PARKS',82),('PROMENADE',62),('CORNERS',52),('UTILITIES',6),('TEXT',7)]: doc.layers.add(n,color=c)
def poly(gm,layer):
    for p in getattr(gm,'geoms',[gm]):
        if p.geom_type=='Polygon' and not p.is_empty: msp.add_lwpolyline(list(p.exterior.coords),close=True,dxfattribs={'layer':layer})
doc.layers.add('WALKWAY',color=33); poly(walk,'WALKWAY'); poly(RS,'RESORT'); poly(C,'COLONY'); poly(roads,'ROADS'); poly(gard,'MEDIANS'); poly(rpark,'PROMENADE'); poly(parks,'PARKS'); poly(corners,'CORNERS')
if park is not None: poly(park,'PARKS')
for (p,k),x in zip(plots,rows): poly(p,'PLOTS'); msp.add_text(f'{x[0]} {x[2]} sqft',height=1.6,dxfattribs={'layer':'TEXT'}).set_placement(p.centroid.coords[0])
for k,v in util.items(): poly(v,'UTILITIES')
doc.saveas(OUT+TAG+'.dxf')
print(f'{TAG}: {len(rows)} plots, sellable {100*sale/T:.1f}%, parks {100*os_parks/T:.1f}%, +promenade {100*(os_parks+rpark.area)/T:.1f}%, garden view {gfc}/{len(rows)}, medians {100*gard.area/T:.1f}%, utilities placed {list(util)}')
