import json, sys, itertools, multiprocessing as mp, warnings
warnings.filterwarnings('ignore')
import d8 as d7
def run(args):
    try: return d7.design(*args)
    except Exception as e: return None
if __name__=='__main__':
    stage=sys.argv[1]
    DIMS={4000:[(40,100),(45,90),(50,80)],7000:[(50,140),(60,120),(70,100)]}
    if stage=='1':
        jobs=[(th,y0,pw,pd,st,0,False,sz) for sz in (4000,7000) for st in ('p9','p12','m12','m15') for (pw,pd) in DIMS[sz] for th in range(0,180,10) for y0 in (0,20,40)]
    else:
        prev=json.load(open('d8_stage1.json'))
        jobs=[]
        for sz in (4000,7000):
          for st in ('p9','p12','m12','m15','h12','h15'):
            seed={'h12':'m12','h15':'m15'}.get(st,st)
            top=sorted([r for r in prev if r and r['style']==seed and r['size']==sz],key=lambda r:-r['sale'])[:3]
            for r in top:
                for dth in (-5,0,5):
                    for dy in (-8,0,8):
                        jobs.append((r['th']+dth,r['y0']+dy,r['pw'],r['pd'],st,0,False,sz))
        jobs=list(dict.fromkeys(jobs))
    print('jobs',len(jobs),flush=True)
    with mp.Pool(mp.cpu_count()) as pool:
        res=[r for r in pool.imap_unordered(run,jobs,chunksize=2) if r]
    json.dump(res,open(f'd8_stage{stage}.json','w'))
    for sz in (4000,7000):
      for st in ('p9','p12','m12','m15','h12','h15'):
        b=sorted([r for r in res if r['style']==st and r['size']==sz],key=lambda r:-r['sale'])[:1]
        print(sz,st,b)
