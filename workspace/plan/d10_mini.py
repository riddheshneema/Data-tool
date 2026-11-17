import multiprocessing as mp, warnings; warnings.filterwarnings('ignore')
import d10
from shapely import wkt
def run(a):
    th,y0=a
    try:
        r=d10.plan(th,y0,45,90,2,return_geom=True)
        ok=r['geom'].get('park') is not None and len(r['ids'])>=4
        return (th,y0,r['sale'],r['n'],ok)
    except Exception as e: return (th,y0,None,None,False)
if __name__=='__main__':
    jobs=[(th,y0) for th in (95,100,105) for y0 in (0,3,6,9,12)]
    with mp.Pool(4) as p: res=list(p.imap_unordered(run,jobs))
    for x in sorted([x for x in res if x[4]],key=lambda x:-x[2])[:5]: print(x)
