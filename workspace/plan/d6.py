import pickle, json, numpy as np, sys
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union, linemerge
from shapely import affinity, prepared, set_precision
from shapely.validation import make_valid
SP=lambda g: set_precision(make_valid(g),0.01)
D='/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/plan/'
B=pickle.load(open(D+'d2_base.pkl','rb')); R,C0,RS=B['river'],B['colony'],B['resort']
C=SP(C0.buffer(1.5,join_style=2).buffer(-1.5,join_style=2)); R=SP(R)
FT=0.3048; SQFT=10.7639; MIN_A=3500/SQFT; MAX_A=8000/SQFT
ENTRY=(336.0,-485.0)
SB=15; PREM_D=33.5; DRIVE_W=9; LG=4          # setback, premium depth, drive, linear garden
d1=SB+PREM_D; d2=d1+DRIVE_W; d3=d2+LG
def ring(a,b): return C.intersection(R.buffer(b)).difference(R.buffer(a))
river_park=C.intersection(R.buffer(SB))
prem_band=ring(SB,d1); drive=ring(d1,d2); lin_garden=ring(d2,d3)
# east avenue (18 m: 9 m carriageway + 4.5 m garden verges) and 24 m entry boulevard
av_line=LineString([(334,-470),(332,-360),(331,-262)])
avenue=av_line.buffer(7.5,cap_style=2).intersection(C)
av_gardens=avenue.difference(av_line.buffer(4.5,cap_style=2))
bv_line=LineString([ENTRY,(334,-455)])
boulevard=bv_line.buffer(12,cap_style=2).intersection(C); bv_median=bv_line.buffer(3,cap_style=2).intersection(C)
spine_roads=SP(unary_union([drive,avenue,boulevard]).buffer(0))
interior=C.difference(R.buffer(d3)).difference(spine_roads).buffer(0.01).buffer(-0.01)
def normals(L,t):
    a,b=L.interpolate(max(t-1,0)),L.interpolate(min(t+1,L.length)); dx,dy=b.x-a.x,b.y-a.y; n=np.hypot(dx,dy) or 1; return (-dy/n,dx/n)
def merge_small(cells):
    """merge cells below MIN_A into the neighbour they share the longest edge with"""
    cells=[c for c in cells if c.area>5]
    changed=True
    while changed:
        changed=False
        for i,c in enumerate(cells):
            if c.area<MIN_A:
                nb=[(c.intersection(o.buffer(0.3)).length if False else c.buffer(0.3).intersection(o).area,j) for j,o in enumerate(cells) if j!=i]
                nb=[t for t in nb if t[0]>0.5]
                if nb:
                    j=max(nb)[1]; m=unary_union([c,cells[j]]).buffer(0.01).buffer(-0.01)
                    if m.area<=MAX_A*1.15:
                        cells[j]=m; cells.pop(i); changed=True; break
    return cells
# ---- premium river-front plots: cut the band by normals along the drive edge ----
def edge_lines(d):
    g=C.buffer(-0.1).intersection(R.buffer(d).exterior)
    g=linemerge(g) if g.geom_type=='MultiLineString' else g
    return [l for l in getattr(g,'geoms',[g]) if l.geom_type=='LineString' and l.length>15]
prem=[];view=[]
for L in edge_lines(d1-0.5):
    s=0;k=0;W=60*FT
    cuts=[]
    while s<L.length:
        cuts.append(s); s+=W; k+=1
        if k%4==0: cuts.append(('g',s)); s+=6
    cells=[]; t0=0
    pts=[c for c in cuts if not isinstance(c,tuple)]+[L.length]
    seq=[]
    s=0;k=0
    while s<L.length:
        e=min(s+W,L.length); seq.append(('p',s,e)); s=e; k+=1
        if k%4==0 and s<L.length: e=min(s+6,L.length); seq.append(('g',s,e)); s=e
    for typ,a,b in seq:
        pa,pb=L.interpolate(a),L.interpolate(b); na,nb=normals(L,a),normals(L,b); h=PREM_D+10
        q=Polygon([(pa.x+na[0]*h,pa.y+na[1]*h),(pb.x+nb[0]*h,pb.y+nb[1]*h),(pb.x-nb[0]*h,pb.y-nb[1]*h),(pa.x-na[0]*h,pa.y-na[1]*h)]).buffer(0)
        c=q.intersection(prem_band).difference(spine_roads).buffer(0)
        if c.geom_type=='MultiPolygon': c=max(c.geoms,key=lambda g:g.area)
        (cells if typ=='p' else view).append(c)
    prem+=merge_small(cells)
prem=[p for p in prem if p.area>=MIN_A and p.buffer(0.8).intersection(drive).area>8]
# ---- interior: oriented grid of double-loaded streets, flexible end plots ----
O=(300,-420)
def grid(region,th,y0,pw):
    Rr=affinity.rotate(region,-th,origin=O); minx,miny,maxx,maxy=Rr.bounds
    streets=[];cells=[]
    y=miny-61+y0
    while y<maxy+61:
        st=box(minx-50,y,maxx+50,y+9); streets.append(st)
        for ya,yb in ((y+9,y+9+30.48),(y-30.48,y)):
            x=minx-pw
            while x<maxx+pw:
                cells.append(box(x,ya,x+pw,yb)); x+=pw
        y+=9+61
    S=unary_union(streets).intersection(Rr).buffer(0)
    Rr=Rr.buffer(0); Sp=S
    out=[]
    for c in cells:
        try: g=c.intersection(Rr).difference(Sp)
        except Exception:
            try: g=c.buffer(0.001).intersection(Rr.buffer(0.001)).difference(Sp.buffer(0.001))
            except Exception: continue
        for p in getattr(g,'geoms',[g]):
            if p.geom_type=='Polygon' and p.area>5: out.append(p)
    out=merge_small(out)
    St=SP(affinity.rotate(S,th,origin=O)); allroads=SP(unary_union([SP(St.buffer(0)),spine_roads]))
    res=[]
    for p in out:
        pw_=affinity.rotate(p,th,origin=O)
        if MIN_A<=pw_.area<=MAX_A*1.15 and pw_.buffer(0.8).intersection(allroads).area>8: res.append(pw_)
    return res,St
best=None
for th in range(0,180,5):
    for y0 in np.arange(0,70,7):
        pl,st=grid(interior,th,y0,50*FT)
        a=sum(p.area for p in pl)
        if best is None or a>best[0]: best=(a,th,y0,pl,st)
a,th,y0,inner,streets=best
print('grid angle',th,'offset',y0)
roads=unary_union([drive,avenue.difference(av_gardens),boulevard.difference(bv_median),streets.intersection(C)]).buffer(0)
row=unary_union([roads,avenue,boulevard])  # full right-of-way incl. verges
def split_big(lst,cap=8500/SQFT):
    out=[]
    for p in lst:
        if p.area<=cap: out.append(p); continue
        mrr=p.minimum_rotated_rectangle; c=list(mrr.exterior.coords)
        e0=Point(c[0]).distance(Point(c[1])); e1=Point(c[1]).distance(Point(c[2]))
        # cut across the longer side through the centroid
        if e0>e1: a,b=c[0],c[1]
        else: a,b=c[1],c[2]
        dx,dy=b[0]-a[0],b[1]-a[1]; n=np.hypot(dx,dy); ux,uy=dx/n,dy/n
        cx,cy=p.centroid.x,p.centroid.y
        cut=LineString([(cx-uy*200,cy+ux*200),(cx+uy*200,cy-ux*200)])
        from shapely.ops import split
        parts=[g for g in split(p,cut).geoms]
        out+= parts if len(parts)==2 and min(g.area for g in parts)>=MIN_A else [p]
    return out
prem=split_big(prem); inner=split_big(inner)
plots=[(p,'River-front villa') for p in prem]+[(p,'Villa') for p in inner]
plotu=unary_union([p for p,_ in plots])
garden=unary_union([lin_garden,av_gardens,bv_median]).difference(plotu).intersection(C)
open_left=C.difference(roads).difference(plotu).difference(garden).difference(river_park).buffer(0)
json.dump(dict(row=row.wkt,C=C.wkt,RS=RS.wkt,R=R.wkt,roads=roads.wkt,river_park=river_park.wkt,garden=garden.wkt,left=open_left.wkt,
   plots=[(p.wkt,k) for p,k in plots]),open(D+'d6_layout.json','w'))
T=C.area; f=lambda g:100*g.area/T
print('plots %d (%d river-front) | plots %.1f%% | roads %.1f%% | river park %.1f%% | linear gardens %.1f%% | leftover %.1f%%'%(len(plots),len(prem),f(plotu),f(roads),f(river_park),f(garden),f(open_left)))
ar=[p.area*SQFT for p,_ in plots]; print('sizes %d–%d'%(min(ar),max(ar)))
