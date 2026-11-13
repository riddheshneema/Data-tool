import pickle, json, numpy as np, sys, itertools, time
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union, linemerge, split
from shapely import affinity, set_precision, STRtree
from shapely.validation import make_valid
SP=lambda g: set_precision(make_valid(g),0.01)
D='/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/plan/'
B=pickle.load(open(D+'d2_base.pkl','rb')); R=SP(B['river'])
NORTH=SP(B['resort'].buffer(1.5,join_style=2).buffer(-1.5,join_style=2))   # back half = colony
SOUTH=SP(B['colony'].buffer(1.5,join_style=2).buffer(-1.5,join_style=2))   # front half = resort
FT=0.3048; SQFT=10.7639
ENTRY=(336.0,-485.0)
GATE=(331.0,-262.0)                 # where the access road enters the colony
access_line=LineString([ENTRY,(334,-440),(332,-360),GATE])
def ring(C,a,b): return C.intersection(R.buffer(b)).difference(R.buffer(a))
def normals(L,t):
    a,b=L.interpolate(max(t-1,0)),L.interpolate(min(t+1,L.length)); dx,dy=b.x-a.x,b.y-a.y; n=np.hypot(dx,dy) or 1; return (-dy/n,dx/n)
def merge_small(cells,MIN_A,MAX_A):
    cells=[c for c in cells if c.area>5]
    changed=True
    while changed:
        changed=False
        tree=STRtree(cells)
        for i,c in enumerate(cells):
            if c.area<MIN_A:
                cand=[j for j in tree.query(c.buffer(0.3)) if j!=i]
                nb=[(c.buffer(0.3).intersection(cells[j]).area,j) for j in cand]
                nb=[t for t in nb if t[0]>0.5]
                if nb:
                    j=max(nb)[1]; m=unary_union([c,cells[j]]).buffer(0.01).buffer(-0.01)
                    if m.area<=MAX_A:
                        cells[j]=m; cells.pop(i); changed=True; break
    return cells
def split_big(lst,cap,MIN_A):
    out=[]
    for p in lst:
        if p.area<=cap: out.append(p); continue
        c=list(p.minimum_rotated_rectangle.exterior.coords)
        e0=Point(c[0]).distance(Point(c[1])); e1=Point(c[1]).distance(Point(c[2]))
        a,b=(c[0],c[1]) if e0>e1 else (c[1],c[2])
        dx,dy=b[0]-a[0],b[1]-a[1]; n=np.hypot(dx,dy); ux,uy=dx/n,dy/n; cx,cy=p.centroid.x,p.centroid.y
        parts=list(split(p,LineString([(cx-uy*300,cy+ux*300),(cx+uy*300,cy-ux*300)])).geoms)
        out+= parts if len(parts)==2 and min(g.area for g in parts)>=MIN_A else [p]
    return out
STYLES={'p9':(9,0),'p12':(12,0),'m12':(12,3),'m15':(15,4),'plain':(9,0),'median':(15,4),'h12':(12,3),'h15':(15,4)}
HYBRID={'h12','h15'}
def good_shape(p):
    """sellable plot: near-rectangular, no sharp corners, buildable width, sane proportions"""
    if p.geom_type!='Polygon' or p.is_empty: return False
    mrr=p.minimum_rotated_rectangle; c=list(mrr.exterior.coords)
    a=Point(c[0]).distance(Point(c[1])); b=Point(c[1]).distance(Point(c[2]))
    short,long_=min(a,b),max(a,b)
    if short<11 or long_/short>3.2: return False
    if p.area/mrr.area<0.66: return False
    q=p.simplify(0.6); pts=list(q.exterior.coords)[:-1]; n=len(pts)
    if n>7: return False
    for i in range(n):
        p0,p1,p2=np.array(pts[i-1]),np.array(pts[i]),np.array(pts[(i+1)%n])
        v1,v2=p0-p1,p2-p1; den=np.linalg.norm(v1)*np.linalg.norm(v2)
        if den==0: continue
        ang=np.degrees(np.arccos(np.clip(np.dot(v1,v2)/den,-1,1)))
        if ang<55 and min(np.linalg.norm(v1),np.linalg.norm(v2))>2.5: return False
    return True
def design(th,y0,pw_ft,pd_ft,style,LG,return_geom=False,size=4000,quality=True,garden_streets=None,plain_entry=False,plain_drive=False,drive_w=None,triangle_park=False,park_rank=4):
    C=NORTH
    SWW,MW=STYLES[style]
    if size>=6000: MIN_A=5800/SQFT; MAX_A=10000/SQFT; PW_PREM=70*FT
    else: MIN_A=3500/SQFT; MAX_A=6500/SQFT; PW_PREM=60*FT
    SB=15; PREM_D=pd_ft*FT*1.1; DRIVE=SWW
    if style in HYBRID: DRIVE=9; LG=max(LG,3)
    if plain_drive: DRIVE=drive_w or 9
    d1=SB+PREM_D; d2=d1+DRIVE; d3=d2+LG
    rpark=C.intersection(R.buffer(SB)); prem_band=ring(C,SB,d1); drive=ring(C,d1,d2); lgard=ring(C,d2,d3)
    # colony entry boulevard (24 m with 6 m median) from the gate into the colony, 60 m
    bl=LineString([GATE,(332,-200)]); boul=SP(bl.buffer(6 if plain_entry else 12,cap_style=2).intersection(C)); bmed=SP(bl.buffer(0.01 if plain_entry else 3,cap_style=2).intersection(C))
    spine=SP(unary_union([drive,boul]).buffer(0))
    drive_med=None
    if MW and style not in HYBRID and not plain_drive:   # drive as divided road with a garden median
        drive_med=ring(C,d1+(SWW-MW)/2,d1+(SWW+MW)/2)
    interior=SP(C.difference(R.buffer(d3)).difference(spine).buffer(0.01).buffer(-0.01))
    # premium plots along the drive
    g=C.buffer(-0.1).intersection(R.buffer(d1-0.5).exterior); g=linemerge(g) if g.geom_type=='MultiLineString' else g
    prem=[]
    for L in [l for l in getattr(g,'geoms',[g]) if l.geom_type=='LineString' and l.length>15]:
        s=0;cells=[]; W=PW_PREM
        while s<L.length:
            e=min(s+W,L.length); pa,pb=L.interpolate(s),L.interpolate(e); na,nb=normals(L,s),normals(L,e); h=PREM_D+12
            q=Polygon([(pa.x+na[0]*h,pa.y+na[1]*h),(pb.x+nb[0]*h,pb.y+nb[1]*h),(pb.x-nb[0]*h,pb.y-nb[1]*h),(pa.x-na[0]*h,pa.y-na[1]*h)]).buffer(0)
            c=q.intersection(prem_band).difference(spine).buffer(0)
            if not c.is_empty:
                c=max(getattr(c,'geoms',[c]),key=lambda x:x.area); cells.append(c)
            s=e
        prem+=merge_small(cells,MIN_A,MAX_A*1.2)
    # interior grid
    O=(300,-150); pw=pw_ft*FT; pd=pd_ft*FT
    SW=SWW
    Rr=affinity.rotate(interior,-th,origin=O); minx,miny,maxx,maxy=Rr.bounds
    streets=[];meds=[];cells=[]
    y=miny-2*pd+y0; idx=0
    while y<maxy+2*pd:
        if garden_streets is None: w,mw=SW,MW
        else: w,mw=(12,3) if idx in garden_streets else (12,0)
        streets.append(box(minx-50,y,maxx+50,y+w))
        if mw: meds.append(box(minx-50,y+(w-mw)/2,maxx+50,y+(w+mw)/2))
        for ya,yb in ((y+w,y+w+pd),(y-pd,y)):
            x=minx-pw
            while x<maxx+pw: cells.append(box(x,ya,x+pw,yb)); x+=pw
        y+=w+2*pd; idx+=1
    street_ids=[(i,affinity.rotate(st,th,origin=O).intersection(C)) for i,st in enumerate(streets)]
    S=SP(unary_union(streets).intersection(Rr).buffer(0))
    out=[]
    for c in cells:
        try: gg=c.intersection(Rr).difference(S)
        except Exception: continue
        for p in getattr(gg,'geoms',[gg]):
            if p.geom_type=='Polygon' and p.area>5: out.append(p)
    out=merge_small(out,MIN_A,MAX_A)
    St=SP(affinity.rotate(S,th,origin=O))
    park=None
    if triangle_park:
        ranked=[]
        for i,st in enumerate(streets):
            gi=SP(affinity.rotate(st,th,origin=O)).intersection(St)
            if gi.area>200: ranked.append((gi.centroid.x,i,gi))
        ranked.sort(key=lambda t:-t[0])
        if len(ranked)>=park_rank:
            xref=ranked[park_rank-1][0]
            blocks=SP(interior.difference(St).buffer(0))
            cand=[b for b in getattr(blocks,'geoms',[blocks]) if b.geom_type=='Polygon' and b.centroid.x<xref and b.area>300]
            if cand: park=max(cand,key=lambda b:b.area)
    Mt=SP(affinity.rotate(unary_union(meds),th,origin=O).intersection(C)) if meds else None
    allrow=SP(unary_union([St,spine,boul]).buffer(0))
    inner=[affinity.rotate(p,th,origin=O) for p in out]
    plots=[]
    if park is not None:
        inner=[p for p in inner if p.intersection(park).area<0.5*p.area]
    for p,k in [(p,'River-front villa') for p in split_big(prem,MAX_A,MIN_A)]+[(p,'Villa') for p in split_big(inner,MAX_A,MIN_A)]:
        if MIN_A<=p.area<=MAX_A*1.2 and p.buffer(0.8).intersection(allrow).area>8 and (not quality or good_shape(p)): plots.append((p,k))
    pu=unary_union([p for p,_ in plots]) if plots else Polygon()
    sale=pu.area/C.area
    gardens=[lgard,bmed]+([drive_med] if drive_med is not None else [])+([Mt] if Mt is not None else [])
    gard=SP(unary_union([x for x in gardens if x is not None and not x.is_empty]))
    gf=0
    green_all=SP(unary_union([gard,rpark]))
    reach=(SWW-MW)/2+1.0 if MW else 1.0
    for p,k in plots:
        if k=='River-front villa' and p.distance(rpark)<1.0: gf+=1
        elif p.distance(gard)<=max(reach,LG and 1.0 or 0): gf+=1
        elif park is not None and p.distance(park)<=10.5: gf+=1
    res=dict(th=th,y0=y0,pw=pw_ft,pd=pd_ft,style=style,LG=LG,size=size,n=len(plots),sale=round(100*sale,2),garden_facing=gf,gf_pct=round(100*gf/max(len(plots),1)))
    if return_geom:
        roads=SP(unary_union([St,drive,boul]).difference(gard))
        per_street=[]
        for i,g in street_ids:
            gi=g.intersection(St)
            if gi.is_empty or gi.area<20: continue
            mi=gi.intersection(Mt) if Mt is not None else Polygon()
            per_street.append((i,gi.wkt,mi.wkt))
        res.update(per_street=per_street,drive=drive.wkt,boul=boul.wkt,bmed=bmed.wkt,drive_med=(drive_med.wkt if drive_med is not None else None),
                   street_ids=[(i,g.wkt) for i,g in street_ids if not g.is_empty],geom=dict(C=C.wkt,RESORT=SOUTH.wkt,R=R.wkt,access=access_line.buffer(7.5,cap_style=2).intersection(SOUTH).wkt,
            row=allrow.wkt,roads=roads.wkt,park=(park.wkt if park is not None else None),gardens=gard.wkt,river_park=rpark.wkt,plots=[(p.wkt,k) for p,k in plots]))
    return res
if __name__=='__main__':
    stage=sys.argv[1]
    t0=time.time(); results=[]
    if stage=='1':   # coarse: angle x offset, for each road style
        for style in ('plain','median'):
            for th in range(0,180,10):
                for y0 in (0,15,30,45):
                    try: r=design(th,y0,50,100,style,4)
                    except Exception as e: continue
                    results.append(r); print(r,flush=True)
    json.dump(results,open(D+f'd7_stage{stage}.json','w'))
    print('time',time.time()-t0)
