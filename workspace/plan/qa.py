import sys,pickle,numpy as np,warnings; warnings.filterwarnings('ignore')
from shapely import wkt
from shapely.geometry import Point
from shapely.ops import unary_union
D='/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/plan/'
S=pickle.load(open(D+'final_'+sys.argv[1]+'.pkl','rb')); G=wkt.loads
row=G(S['row']); C=G(S['C']); GATE=Point(331,-262)
comps=[q for q in getattr(row.buffer(0.4).buffer(-0.4),'geoms',[row]) if q.area>5]; main=min(comps,key=lambda q:q.distance(GATE))
print('road network pieces:',len(comps))
bad=[]
for tag,w,k in S['plots']:
    p=G(w); q=p.simplify(0.8); pts=list(q.exterior.coords)[:-1]; n=len(pts); angs=[]
    for i in range(n):
        a,b,c=np.array(pts[i-1]),np.array(pts[i]),np.array(pts[(i+1)%n]); v1,v2=a-b,c-b
        l1,l2=np.linalg.norm(v1),np.linalg.norm(v2)
        if min(l1,l2)<2.5: continue
        angs.append(np.degrees(np.arccos(np.clip(np.dot(v1,v2)/(l1*l2),-1,1))))
    mrr=p.minimum_rotated_rectangle; rect=p.area/mrr.area
    fr=p.buffer(0.8).intersection(main).area/0.8
    flag=[]
    if min(angs)<50: flag.append(f'sharp corner {min(angs):.0f}°')
    if rect<0.65: flag.append(f'irregular (fills {rect:.0%} of its rectangle)')
    if fr<12: flag.append(f'frontage {fr:.1f} m (BVN needs >12 m)')
    if p.area*10.764<3600: flag.append(f'small {p.area*10.764:.0f} sq ft')
    if flag: bad.append((tag,round(p.area*10.764),flag))
print('plots checked:',len(S['plots']),'| flagged:',len(bad))
for b in bad: print('  ',b)
