import pickle, json, numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union, linemerge
D='/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/plan/'
B=pickle.load(open(D+'d2_base.pkl','rb')); R,C0,RS=B['river'],B['colony'],B['resort']
C=C0.buffer(1.5,join_style=2).buffer(-1.5,join_style=2)
FT=0.3048; SQFT=10.7639
PARK=R.buffer(15)                     # 15 m statutory river buffer = riverside promenade
def river_line(d):
    g=C.buffer(-0.1).intersection(R.buffer(d).exterior)
    g=linemerge(g) if g.geom_type=='MultiLineString' else g
    ls=[l for l in getattr(g,'geoms',[g]) if l.geom_type=='LineString']
    return max(ls,key=lambda l:l.length)
ENTRY=(336.0,-485.0)
roads_spec={
 'Entry boulevard (24 m)': (LineString([ENTRY,(334,-440)]),24),
 'Resort avenue (18 m)':   (LineString([(334,-440),(332,-360),(331,-262)]),18),
 'River drive (15 m)':     (river_line(56),15),
 'South link (15 m)':      (LineString([(334,-478),(300,-477),(266,-466)]),15),
 'East lane (13 m)':       (LineString([(334,-462),(372,-462),(404,-462)]),13),
 'Area-3 link (13 m)':     (LineString([(372,-462),(372,-500)]),13),
 'Area-3 river lane (13 m)':(LineString([(362,-500),(404,-500)]),13),
 'Area-2 river lane (13 m)':(LineString([(262,-468),(215,-478),(178,-468),(152,-447)]),13),
}
road_polys={k:l.buffer(w/2,cap_style=2,join_style=1).intersection(C) for k,(l,w) in roads_spec.items()}
# extend river drive ends to meet the network
roads=unary_union(list(road_polys.values())).buffer(0)
median=roads_spec['Entry boulevard (24 m)'][0].buffer(3,cap_style=2).intersection(C)
taken=unary_union([roads,PARK.intersection(C)])
def normals(L,t):
    a,b=L.interpolate(max(t-1,0)),L.interpolate(min(t+1,L.length)); dx,dy=b.x-a.x,b.y-a.y; n=np.hypot(dx,dy) or 1; return (-dy/n,dx/n)
FLEX=1.3
def frontage_plots(name,side,depth,width,group,gap,rng,kind,offset=None):
    global taken
    L,w=roads_spec[name]
    off=w/2+depth/2 if offset is None else offset
    try: G=L.offset_curve(off if side=='left' else -off)
    except Exception: return [],[]
    Ls=[g for g in getattr(G,'geoms',[G]) if g.length>10]
    out=[];gard=[]
    for M in Ls:
        s=gap/2;k=0
        while s+width<=M.length:
            pa,pb=M.interpolate(s),M.interpolate(s+width); na,nb=normals(M,s),normals(M,s+width); h=depth*FLEX+w/2+2
            q=Polygon([(pa.x+na[0]*h,pa.y+na[1]*h),(pb.x+nb[0]*h,pb.y+nb[1]*h),(pb.x-nb[0]*h,pb.y-nb[1]*h),(pa.x-na[0]*h,pa.y-na[1]*h)]).buffer(0)
            strip=L.buffer(w/2+depth*FLEX,cap_style=2).difference(L.buffer(w/2,cap_style=2))
            p=q.intersection(strip).intersection(C).difference(taken).buffer(0)
            if p.geom_type=='MultiPolygon': p=max(p.geoms,key=lambda g:g.area)
            a=p.area*SQFT
            front=p.buffer(0.8).intersection(roads).area/0.8 if not p.is_empty else 0
            mrr=p.minimum_rotated_rectangle if not p.is_empty else None
            okshape= mrr is not None and min(Point(mrr.exterior.coords[i]).distance(Point(mrr.exterior.coords[i+1])) for i in range(2))>=11
            if rng[0]<=a<=rng[1] and front>=10 and okshape:
                out.append((p,kind,name)); taken=taken.union(p.buffer(0.05))
            s+=width;k+=1
            if k%group==0: s+=gap
    return out
plots=[]
# 1. premium river-front villas: river side of river drive (front on drive, back on riverside park)
Ld=roads_spec['River drive (15 m)'][0]
dl=Ld.offset_curve(20).distance(R); dr=Ld.offset_curve(-20).distance(R)
RIVERSIDE='left' if Ld.offset_curve(20).centroid.distance(R)<Ld.offset_curve(-20).centroid.distance(R) else 'right'
INSIDE='right' if RIVERSIDE=='left' else 'left'
print('riverside of drive =',RIVERSIDE)
plots+=frontage_plots('River drive (15 m)',RIVERSIDE,33.5,60*FT,4,6,(5600,10500),'River-front villa')
# reserve the 8 m garden spine behind the inner villas later; inner side of river drive
inner=[]
inner+=frontage_plots('River drive (15 m)',INSIDE,30.5,45*FT,6,4,(3800,7500),'Villa')
plots+=inner
# garden spine behind river-drive inner villas
spine=unary_union([p.buffer(8) for p,_,_ in inner]).difference(unary_union([p for p,_,_ in plots])).difference(roads)

# river-facing premium plots on the new river lanes
plots+=frontage_plots('Area-3 river lane (13 m)','right',33.5,60*FT,4,6,(5500,10500),'River-front villa')
L2=roads_spec['Area-2 river lane (13 m)'][0]
s2='left' if L2.offset_curve(20).centroid.distance(R)<L2.offset_curve(-20).centroid.distance(R) else 'right'
plots+=frontage_plots('Area-2 river lane (13 m)',s2,33.5,60*FT,4,6,(5500,10500),'River-front villa')
plots+=frontage_plots('Area-2 river lane (13 m)','right' if s2=='left' else 'left',30.5,45*FT,6,4,(3800,7500),'Villa')
for nm in ['Resort avenue (18 m)','Entry boulevard (24 m)','South link (15 m)','East lane (13 m)']:
    for side in ('left','right'):
        plots+=frontage_plots(nm,side,30.5,50*FT,6,4,(3800,7500),'Villa')
plots+=frontage_plots('Area-3 river lane (13 m)','left',24,50*FT,6,4,(3500,7500),'Villa')
plots+=frontage_plots('East lane (13 m)','right',24,50*FT,6,4,(3500,7500),'Villa')
plotu=unary_union([p for p,_,_ in plots])
green=C.difference(roads).difference(plotu).buffer(0)
json.dump(dict(C=C.wkt,RS=RS.wkt,R=R.wkt,roads=roads.wkt,median=median.wkt,green=green.wkt,park=PARK.intersection(C).difference(roads).wkt,
   road_polys={k:v.wkt for k,v in road_polys.items()},plots=[(p.wkt,k,n) for p,k,n in plots]),open(D+'d4_layout.json','w'))
from collections import Counter
print(Counter(k for _,k,_ in plots)); print(Counter(n for _,_,n in plots))
ar=[p.area*SQFT for p,_,_ in plots]; print('sizes',int(min(ar)),int(max(ar)))
print('plots %.1f%% roads %.1f%% green %.1f%%'%(100*plotu.area/C.area,100*roads.area/C.area,100*green.area/C.area))
