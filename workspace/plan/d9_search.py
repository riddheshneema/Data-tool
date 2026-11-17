import json, multiprocessing as mp, warnings, numpy as np
warnings.filterwarnings('ignore')
import d8
from shapely import wkt
def run(a):
    th,y0,pw,pd=a
    try:
        r=d8.design(th,y0,pw,pd,'m12',0,return_geom=True,garden_streets=None,plain_entry=True,plain_drive=True)
        # identify the two streets bounding the V8|V1 double row (world x ~251 and ~316)
        cs=[(i,wkt.loads(g).centroid.x) for i,g in r['street_ids']]
        g4=min(cs,key=lambda t:abs(t[1]-251))[0]; g3=min(cs,key=lambda t:abs(t[1]-316))[0]
        r2=d8.design(th,y0,pw,pd,'m12',0,garden_streets={g4,g3},plain_entry=True,plain_drive=True)
        r2['gs']=[g4,g3]; return r2
    except Exception as e: return None
if __name__=='__main__':
    jobs=[(th,y0,pw,pd) for th in (95,100,105) for y0 in np.arange(-12,13,3) for (pw,pd) in ((45,90),(40,100))]
    with mp.Pool(4) as p: res=[r for r in p.imap_unordered(run,jobs) if r]
    res.sort(key=lambda r:-r['sale']); json.dump(res,open('d9.json','w'))
    for r in res[:5]: print(r)
