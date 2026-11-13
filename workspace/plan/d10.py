import warnings; warnings.filterwarnings('ignore')
import d8
from shapely import wkt
GARDEN_RANKS={1:[2,3,4],2:[2,3]}   # streets counted from the east: S1 = east edge (V6-V35), S2, S3, S4 (V8-V37)
def street_ranks(th,y0,pw,pd,drive_w=12):
    r=d8.design(th,y0,pw,pd,'m12',0,return_geom=True,garden_streets=set(),plain_entry=True,plain_drive=True,drive_w=drive_w)
    st=[(wkt.loads(s).centroid.x,i,wkt.loads(s).area) for i,s,m in r['per_street']]
    st=sorted([t for t in st if t[2]>200],key=lambda t:-t[0])
    return [int(i) for x,i,a in st]
def plan(th,y0,pw,pd,option,return_geom=False,drive_w=12):
    ids=street_ranks(th,y0,pw,pd,drive_w)
    gs={ids[k-1] for k in GARDEN_RANKS[option] if k-1<len(ids)}
    r=d8.design(th,y0,pw,pd,'m12',0,return_geom=return_geom,garden_streets=gs,plain_entry=True,plain_drive=True,drive_w=drive_w,
                triangle_park=(option==2))
    r.update(ids=ids,gs=sorted(int(g) for g in gs),option=option,th=float(th),y0=float(y0))
    return r
