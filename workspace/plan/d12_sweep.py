import multiprocessing as mp, warnings; warnings.filterwarnings('ignore')
import d10
def run(a):
    th,y0=a
    try:
        r=d10.plan(th,y0,45,90,1)
        return (th,y0,r['sale'],r['n'],len(r['ids']))
    except Exception as e: return (th,y0,None,None,None)
if __name__=='__main__':
    jobs=[(th,y0) for th in (95,100,105) for y0 in (0,3,6,9,12,15,18)]
    with mp.Pool(4) as p: res=list(p.imap_unordered(run,jobs))
    for x in sorted([x for x in res if x[2] and x[4]>=4],key=lambda x:-x[2])[:6]: print(x)
