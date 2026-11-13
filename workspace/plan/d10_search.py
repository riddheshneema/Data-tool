import json, multiprocessing as mp, warnings, numpy as np
warnings.filterwarnings('ignore')
import d10
def run(a):
    try:
        r=d10.plan(*a); r.pop('per_street',None); r.pop('street_ids',None)
        return {k:(float(v) if isinstance(v,(np.floating,)) else (int(v) if isinstance(v,(np.integer,)) else v)) for k,v in r.items() if k not in ('drive','boul','bmed','drive_med')}
    except Exception as e: return None
if __name__=='__main__':
    jobs=[(th,float(y0),pw,pd,opt) for opt in (1,2) for th in (95,100,105) for y0 in np.arange(-12,13,3) for (pw,pd) in ((45,90),(40,100))]
    with mp.Pool(4) as p: res=[r for r in p.imap_unordered(run,jobs) if r]
    json.dump(res,open('d10.json','w'),default=float)
    for opt in (1,2):
        b=sorted([r for r in res if r['option']==opt],key=lambda r:-r['sale'])[:3]
        for r in b: print(opt,{k:r[k] for k in ('th','y0','pw','pd','n','sale','garden_facing','gf_pct','gs')})
