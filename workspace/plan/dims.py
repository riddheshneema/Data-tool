"""Dimension extraction for the final colony layout: plots (every side), roads, garden medians, garden, walkway,
services, turning spaces, approach + access roads. All lengths in metres; FT converts."""
import sys,json,pickle,math,numpy as np,warnings; warnings.filterwarnings('ignore'); sys.path.insert(0,'.')
from roadnet import load
from shapely import wkt
from shapely.geometry import Point, LineString, Polygon, box, MultiLineString
from shapely.ops import unary_union, linemerge, substring
FT=3.28084; SQ=10.764
TAG='Plan_4000_Max_RiverDrive12m'
S,G=load(TAG)
C,row,roads,gard,rpark,walk,svc,access,RS,R=[G(S[k]) for k in ('C','row','roads','gard','rpark','walk','svc','access','RS','R')]
drive=G(S['drive']); streets={n:G(w) for n,w in S['streets']}
E=json.load(open('edits_'+TAG+'.json')); S5=G(E['s5'])
DE=json.load(open('deadends_'+TAG+'.json'))
RT=pickle.load(open('roadtest_'+TAG+'.pkl','rb'))
A=pickle.load(open('approach.pkl','rb'))
plots=[(t,G(w),k) for t,w,k in S['plots']]
PL={t:p for t,p,k in plots}; KIND={t:k for t,p,k in plots}
util={k:G(v) for k,v in S['util'].items()}
GATE=Point(331,-262)
# ---------------- road polygons by name ----------------
RP={'RD':drive.intersection(row).buffer(0),'S5':S5.intersection(row).buffer(0)}
for n,p in streets.items(): RP[n]=p.intersection(row).buffer(0)
RP['Access road']=access
def road_name_at(pt):
    for n in ('S5','S1','S2','S3','S4','RD','Access road'):
        if n in RP and RP[n].buffer(0.3).contains(pt): return n
    # junction pieces / the link from RD into S1: nearest named road
    return min((n for n in RP if n!='Access road'),key=lambda n:RP[n].distance(pt))
# skeleton edges renamed: anything not inside a named polygon goes to the nearest one ('link' = RD→S1 bend belongs to S1)
def edge_name(l):
    best,bv=None,0
    for n,p in RP.items():
        v=l.intersection(p.buffer(1.0)).length
        if v>bv: best,bv=n,v
    if bv<0.5*l.length:
        m=l.interpolate(0.5,normalized=True); best=road_name_at(m)
    return best
edges=[(edge_name(wkt.loads(lw)),L,wkt.loads(lw)) for n,L,w,lw in RT['edges']]
# ---------------- what lies just outside a plot side ----------------
def what_at(pt,self_t=None):
    for t,p in PL.items():
        if t!=self_t and p.buffer(0.05).contains(pt): return t
    if rpark.buffer(0.05).contains(pt): return 'Riverside garden'
    if walk.buffer(0.05).contains(pt): return 'Walkway'
    if svc.buffer(0.05).contains(pt): return 'Services plot'
    if gard.buffer(0.05).contains(pt) or row.buffer(0.1).contains(pt) or access.contains(pt): return road_name_at(pt)
    if not C.buffer(0.05).contains(pt): return 'Boundary'
    return 'Landscaped'
def sides(p,t=None,merge_deg=9.0,simp=0.12):
    q=p.simplify(simp); pts=list(q.exterior.coords)[:-1]
    if q.exterior.is_ccw: pts=pts[::-1]                 # clockwise
    n=len(pts); dirs=[]
    for i in range(n):
        a,b=np.array(pts[i]),np.array(pts[(i+1)%n]); dirs.append(math.degrees(math.atan2(*(b-a)[::-1])))
    turn=[abs(((dirs[i]-dirs[i-1]+180)%360)-180) for i in range(n)]   # turn at vertex i
    corners=[i for i in range(n) if turn[i]>=merge_deg]
    if not corners: corners=[0]
    out=[]
    for j,ci in enumerate(corners):
        cj=corners[(j+1)%len(corners)]
        idx=[ci]; k=ci
        while k!=cj: k=(k+1)%n; idx.append(k)
        line=LineString([pts[i] for i in idx])
        if line.length<0.05: continue
        chord=LineString([line.coords[0],line.coords[-1]])
        dev=max(chord.distance(Point(c)) for c in line.coords)
        # neighbour: sample 3 points 0.9 m outside the side
        votes={}
        for f in (0.25,0.5,0.75):
            m=line.interpolate(f,normalized=True); m2=line.interpolate(min(f+0.01,1),normalized=True)
            d=np.array(m2.coords[0])-np.array(m.coords[0]); 
            if np.linalg.norm(d)<1e-9: continue
            d/=np.linalg.norm(d); out_n=np.array([-d[1],d[0]])            # left of travel = outside for a clockwise ring
            pt=Point(np.array(m.coords[0])+out_n*0.9)
            if p.contains(pt): pt=Point(np.array(m.coords[0])-out_n*0.9)
            w=what_at(pt,t); votes[w]=votes.get(w,0)+1
        nb=max(votes,key=votes.get) if votes else '?'
        out.append(dict(line=line,len=line.length,curved=dev>0.35,nb=nb,road=nb in RP,parts=[line.length]))
    def join(a,b):
        L=linemerge([a['line'],b['line']]); L=L if L.geom_type=='LineString' else LineString(list(a['line'].coords)+list(b['line'].coords)[1:])
        return dict(line=L,len=a['len']+b['len'],curved=True if (a['curved'] or b['curved']) else False,nb=a['nb'] if a['len']>=b['len'] else b['nb'],road=a['road'] or b['road'],parts=a['parts']+b['parts'])
    changed=True
    while changed and len(out)>3:
        changed=False
        for i in range(len(out)):
            a,b=out[i],out[(i+1)%len(out)]
            ca=list(a['line'].coords); cb=list(b['line'].coords)
            da=np.array(ca[-1])-np.array(ca[-2]); db_=np.array(cb[1])-np.array(cb[0])
            tn=abs(((math.degrees(math.atan2(db_[1],db_[0]))-math.degrees(math.atan2(da[1],da[0]))+180)%360)-180)
            if (a['nb']==b['nb'] and tn<35) or b['len']<1.0 or a['len']<1.0:   # same neighbour round a gentle bend, or a sliver
                m=join(a,b) if i+1<len(out) else join(a,b)
                if i+1<len(out): out[i:i+2]=[m]
                else: out[i]=m; out.pop(0)
                changed=True; break
    for d in out:
        chord=LineString([d['line'].coords[0],d['line'].coords[-1]]); d['curved']=max(chord.distance(Point(c)) for c in d['line'].coords)>0.35
    return out
ROADS=set(RP)
def plot_info(t):
    p=PL[t]; sd=sides(p,t)
    fr=[s for s in sd if s['road']]
    # start the list at the longest road side (the front), then clockwise
    if fr:
        i0=sd.index(max(fr,key=lambda s:s['len'])); sd=sd[i0:]+sd[:i0]
    return dict(plot=t,kind=KIND[t],sqm=p.area,sqft=p.area*SQ,sides=sd,front=sum(s['len'] for s in fr),
                roads=sorted(set(s['nb'] for s in fr)),corner=len(set(s['nb'] for s in fr))>1)
def mrr_dims(g):
    m=g.minimum_rotated_rectangle; c=list(m.exterior.coords)
    a=Point(c[0]).distance(Point(c[1])); b=Point(c[1]).distance(Point(c[2])); return max(a,b),min(a,b)
def roads_info():
    out=[]
    tot={}
    order=('S5','S1','S2','S3','S4','RD','Access road')
    for n0,L,l in edges:
        rest=l
        for n in order:
            if n not in RP: continue
            part=rest.intersection(RP[n].buffer(0.5))
            if part.length>0.05:
                tot[n]=tot.get(n,0)+part.length; rest=rest.difference(RP[n].buffer(0.5))
            if rest.is_empty: break
        if not rest.is_empty and rest.length>0.05:
            for g_ in getattr(rest,'geoms',[rest]):
                if g_.length<0.05: continue
                nm=road_name_at(g_.interpolate(0.5,normalized=True)); tot[nm]=tot.get(nm,0)+g_.length
    desc={'RD':'River drive – along the river-front plots, from S1 round the bend to the south end',
          'S1':'East street – from RD (via the bend at V5/V7) down the east boundary to S5',
          'S2':'Garden street – from RD south to the boundary (V38 stub)',
          'S3':'Garden street – from RD south to the colony gate',
          'S4':'Garden street – from RD south to the RD south loop',
          'S5':'Link road – joins S1 to S2 along V16/V18 (new)',
          'Access road':'Public access road through the resort – colony gate to the main entry'}
    sec={'RD':'7.5 m carriageway + 2.25 m verge with avenue trees each side',
         'S1':'7.5 m carriageway + 2.25 m verge each side','S5':'7.5 m carriageway + 2.25 m verge each side',
         'S2':'3.5 m lane + 1.0 m footpath/drain each side of a 3.0 m garden median','S3':'3.5 m lane + 1.0 m footpath/drain each side of a 3.0 m garden median',
         'S4':'3.5 m lane + 1.0 m footpath/drain each side of a 3.0 m garden median',
         'Access road':'9 m carriageway + 3 m verge each side (matches the approach road)'}
    for n in ('RD','S1','S2','S3','S4','S5','Access road'):
        if n not in tot: continue
        w=15.0 if n=='Access road' else 12.0
        out.append(dict(name=n,row=w,len=(max(mrr_dims(access)) if n=='Access road' else tot[n]),desc=desc.get(n,''),section=sec.get(n,''),area=(RP[n].area if n in RP else 0)))
    return out
def medians_info():
    out=[]
    for q in getattr(gard,'geoms',[gard]):
        if q.geom_type!='Polygon' or q.area<5: continue
        L,W=mrr_dims(q); n=road_name_at(q.representative_point())
        out.append(dict(road=n,len=L,wid=q.area/L,area=q.area,geom=q))
    out.sort(key=lambda d:d['road']); return out
def garden_info():
    mid=rpark.intersection(R.buffer(7.5).exterior)
    L=sum(g_.length for g_ in getattr(mid,'geoms',[mid]) if g_.geom_type=='LineString')
    inner=rpark.boundary.difference(R.buffer(1.0)).intersection(C.buffer(0.5))
    Li=sum(g_.length for g_ in getattr(inner,'geoms',[inner]) if g_.geom_type in ('LineString',))
    return dict(area=rpark.area,len_mid=L,len_inner=Li,width=15.0)
def corners_info():
    rest=C.difference(unary_union([row,rpark,walk,svc]+list(PL.values()))).buffer(-0.05).buffer(0.05)
    return [q for q in getattr(rest,'geoms',[rest]) if q.geom_type=='Polygon' and q.area>=5]
# ---------------- approach road (survey) and the entry splay ----------------
def approach_info():
    cl=wkt.loads(A['cl'])
    c=list(cl.coords)
    def ext(p0,p1,d): v=np.array(p0)-np.array(p1); v/=np.linalg.norm(v); return tuple(np.array(p0)+v*d)
    clx=LineString([ext(c[0],c[1],25)]+c+[ext(c[-1],c[-2],30)])
    site=unary_union([RS,C]).buffer(0)
    ex=wkt.loads(A['exist']).intersection(box(540,-950,660,-910))
    exl=[g_ for g_ in getattr(ex,'geoms',[ex]) if g_.length>3]
    # existing road: band between its two blue lines
    exist_poly=None
    if exl:
        pts=[pt for g_ in exl for pt in g_.coords]
        exist_poly=MultiLineString([g_.coords for g_ in exl]).convex_hull.buffer(0)
    # existing road: north edge ~y -927.8, south edge ~y -933.6 (two blue lines on the survey)
    north=LineString(sorted({pt for g_ in exl for pt in g_.coords if pt[1]>-931},key=lambda q:q[0]))
    south=LineString(sorted({pt for g_ in exl for pt in g_.coords if pt[1]<=-931},key=lambda q:q[0]))
    exist_poly=Polygon(list(north.coords)+list(south.coords)[::-1]).buffer(0)
    exist_w=exist_poly.area/north.length
    # centre-line: from the site boundary (extend the surveyed line north) to the existing road's north edge
    # road mouth at the site boundary = middle of the surveyed outer road lines where they meet the boundary
    rl=wkt.loads(A['road']); tops=[max(l.coords,key=lambda q:q[1]) for l in getattr(rl,'geoms',[rl]) if max(q[1] for q in l.coords)>-500]
    xa=min(tops,key=lambda q:q[0]); xb=max(tops,key=lambda q:q[0]); s0=((xa[0]+xb[0])/2,(xa[1]+xb[1])/2)
    c=c[1:]                                              # the first surveyed station sits off-centre at the mouth
    endp=min(north.coords,key=lambda q:Point(q).distance(Point(c[-1])))
    endp=north.interpolate(north.project(Point(c[-1])))
    seg=LineString([s0]+c+[endp.coords[0]])
    poly=seg.buffer(7.6,cap_style=2).difference(site).difference(exist_poly).buffer(0)
    bridge=wkt.loads(A['bridge']).intersection(box(350,-650,440,-545))
    mandir=wkt.loads(A['mandir']).intersection(box(620,-925,650,-900)) if A.get('mandir') else None
    return dict(cl=seg,poly=poly,len=seg.length,row=15.2,exist=exl,exist_poly=exist_poly,exist_w=exist_w,bridge=bridge,mandir=mandir)
def entry_splay(ap):
    site=unary_union([RS,C]).buffer(0)
    a_end=ap['cl'].coords[0] if Point(ap['cl'].coords[0]).distance(Point(336,-487))<Point(ap['cl'].coords[-1]).distance(Point(336,-487)) else ap['cl'].coords[-1]
    mouth=ap['poly'].intersection(Point(a_end).buffer(9))
    acc_bot=access.intersection(box(300,-500,360,-470))
    sp=unary_union([mouth,acc_bot]).convex_hull.intersection(site).difference(access).buffer(0)
    return sp
if __name__=='__main__':
    for t in ('V11','R1','V43','V42','R10','V7'):
        pi=plot_info(t); print(t,'%.0f sq ft'%pi['sqft'],'front %.1f m'%pi['front'],pi['roads'],' | '.join('%.2f m (%.1f ft)%s → %s'%(s['len'],s['len']*FT,' arc' if s['curved'] else '',s['nb']) for s in pi['sides']))
    for r in roads_info(): print('road',r['name'],'%.0f m long, %.0f m ROW, %.0f m2'%(r['len'],r['row'],r['area']))
    for m in medians_info(): print('median on',m['road'],'%.1f m x %.2f m, %.0f m2'%(m['len'],m['wid'],m['area']))
    g=garden_info(); print('garden %.0f m2, centre-line %.0f m, inner edge %.0f m'%(g['area'],g['len_mid'],g['len_inner']))
    print('walkway',['%.2f'%v for v in mrr_dims(walk)],'services',['%.2f'%v for v in mrr_dims(svc)],{k:['%.1f'%v for v in mrr_dims(v_)] for k,v_ in util.items()})
    print('corners',[round(q.area) for q in corners_info()])
    ap=approach_info(); print('approach road %.0f m long (site boundary → existing road), poly %.0f m2 | existing road %.1f m wide'%(ap['len'],ap['poly'].area,ap['exist_w']))
    sp=entry_splay(ap); print('entry splay %.0f m2'%sp.area, [round(v) for v in sp.bounds])
    print('access road length %.0f m'%max(mrr_dims(access)))
