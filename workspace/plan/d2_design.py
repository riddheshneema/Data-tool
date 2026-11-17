import pickle, json, numpy as np
from shapely.geometry import LineString, Point, Polygon, box, MultiLineString
from shapely.ops import unary_union, linemerge
D='/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/plan/'
B=pickle.load(open(D+'d2_base.pkl','rb')); R,C,RS,P=B['river'],B['colony'],B['resort'],B['P']
C=C.buffer(1.5,join_style=2).buffer(-1.5,join_style=2)   # close drawing gaps between parcels
FT=0.3048; SQFT=10.7639
band=lambda a,b: C.intersection(R.buffer(b)).difference(R.buffer(a)) if a>0 else C.intersection(R.buffer(b))
ENTRY=(336.0,-483.0)
# ---- design bands (metres from river edge) ----
RIVER_PARK=(0,25); PREM=(25,58.5); DRIVE=(58.5,71.5); RING_B=(71.5,102); SPINE=(102,110); RING_C=(110,140.5); CORE_RD=(140.5,153.5)
# ---- primary movement: boulevard, south link, resort link ----
boulevard_line=LineString([ENTRY,(352,-448),(368,-418)])
boulevard=boulevard_line.buffer(12,cap_style=2,join_style=2).intersection(C)          # 24 m reserve
median=boulevard_line.buffer(3,cap_style=2).intersection(C)                             # 6 m garden median
south_link=LineString([ENTRY,(300,-479),(268,-470)]).buffer(6.5,cap_style=2,join_style=2).intersection(C)
drive=band(*DRIVE); core_rd=band(*CORE_RD)
roads=unary_union([boulevard,south_link,drive,core_rd]).buffer(0)
core_park=C.difference(R.buffer(CORE_RD[1])).difference(roads)
def lines_at(d):
    g=C.buffer(-0.1).intersection(R.buffer(d).exterior)
    if g.geom_type=='LineString': return [g]
    g=linemerge(g) if g.geom_type=='MultiLineString' else g
    return [l for l in getattr(g,'geoms',[g]) if l.geom_type=='LineString' and l.length>10]
def subdivide(zone,dmid,depth,width,group,gap,target,kind,label):
    plots=[];gardens=[]
    for L in lines_at(dmid):
        s=gap/2; k=0
        while s+width<=L.length:
            s0,s1=s,s+width
            pa,pb=L.interpolate(s0),L.interpolate(s1)
            # normals
            def nrm(t):
                a,b=L.interpolate(max(t-1,0)),L.interpolate(min(t+1,L.length))
                dx,dy=b.x-a.x,b.y-a.y; n=np.hypot(dx,dy); return (-dy/n,dx/n)
            na,nb=nrm(s0),nrm(s1); h=depth
            q=Polygon([(pa.x+na[0]*h,pa.y+na[1]*h),(pb.x+nb[0]*h,pb.y+nb[1]*h),(pb.x-nb[0]*h,pb.y-nb[1]*h),(pa.x-na[0]*h,pa.y-na[1]*h)]).buffer(0)
            p=q.intersection(zone).difference(roads).buffer(0)
            if p.geom_type=='MultiPolygon': p=max(p.geoms,key=lambda g:g.area)
            a=p.area*SQFT
            mrr=p.minimum_rotated_rectangle; ex=list(mrr.exterior.coords); e=sorted([Point(ex[i]).distance(Point(ex[i+1])) for i in range(2)])
            if target[0]<=a<=target[1] and e[0]>=11: plots.append((p,kind))
            elif p.area>30: gardens.append(p)
            s+=width; k+=1
            if k%group==0:
                g=Polygon([(L.interpolate(s).x+nrm(s)[0]*h,L.interpolate(s).y+nrm(s)[1]*h),(L.interpolate(s+gap).x+nrm(s+gap)[0]*h,L.interpolate(s+gap).y+nrm(s+gap)[1]*h),
                           (L.interpolate(s+gap).x-nrm(s+gap)[0]*h,L.interpolate(s+gap).y-nrm(s+gap)[1]*h),(L.interpolate(s).x-nrm(s)[0]*h,L.interpolate(s).y-nrm(s)[1]*h)]).buffer(0)
                gardens.append(g.intersection(zone)); s+=gap
    return plots,gardens
prem,g1=subdivide(band(*PREM),(PREM[0]+PREM[1])/2,20,66*FT,2,10,(5800,9500),'River-front villa plot',None)
rb,g2=subdivide(band(*RING_B),(RING_B[0]+RING_B[1])/2,18,45*FT,3,6,(3900,5600),'Garden villa plot',None)
rc,g3=subdivide(band(*RING_C),(RING_C[0]+RING_C[1])/2,18,45*FT,3,6,(3900,5600),'Garden villa plot',None)
allplots=prem+rb+rc
plotu=unary_union([p for p,_ in allplots])
green=C.difference(roads).difference(plotu).buffer(0)
river_park=band(*RIVER_PARK).difference(roads)
out=dict(C=C.wkt,RS=RS.wkt,R=R.wkt,roads=roads.wkt,boulevard=boulevard.wkt,median=median.wkt,core_park=core_park.wkt,
  river_park=river_park.wkt,green=green.wkt,plots=[(p.wkt,k) for p,k in allplots])
json.dump(out,open(D+'d2_layout.json','w'))
A=lambda g:g.area
print('premium',len(prem),'ringB',len(rb),'ringC',len(rc))
for name,lst in [('premium',prem),('ringB',rb),('ringC',rc)]:
    if lst: ar=[p.area*SQFT for p,_ in lst]; print(name,'sqft min %.0f avg %.0f max %.0f'%(min(ar),np.mean(ar),max(ar)))
print('colony %.0f | plots %.1f%% | roads %.1f%% | green %.1f%%'%(C.area,100*plotu.area/C.area,100*roads.area/C.area,100*green.area/C.area))
