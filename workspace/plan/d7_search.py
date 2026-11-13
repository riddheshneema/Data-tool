import json, sys, itertools, multiprocessing as mp, warnings
warnings.filterwarnings('ignore')
import d7
def run(args):
    try: return d7.design(*args)
    except Exception as e: return None
if __name__=='__main__':
    stage=sys.argv[1]
    if stage=='1':
        jobs=[(th,y0,50,100,st,4) for st in ('plain','median') for th in range(0,180,5) for y0 in (0,12,24,36,48)]
    else:
        prev=json.load(open('d7_stage1.json'))
        jobs=[]
        for st in ('plain','median'):
            top=sorted([r for r in prev if r and r['style']==st],key=lambda r:-r['sale'])[:4]
            for r in top:
                for pw in (40,45,50):
                    for pd in (90,100):
                        for LG in ((0,4,6) if st=='plain' else (0,4)):
                            for dy in (-4,0,4):
                                jobs.append((r['th'],r['y0']+dy,pw,pd,st,LG))
        jobs=list(dict.fromkeys(jobs))
    print('jobs',len(jobs),flush=True)
    with mp.Pool(mp.cpu_count()) as pool:
        res=[r for r in pool.imap_unordered(run,jobs,chunksize=2) if r]
    json.dump(res,open(f'd7_stage{stage}.json','w'))
    for st in ('plain','median'):
        b=sorted([r for r in res if r['style']==st],key=lambda r:-r['sale'])[:3]
        print(st,b)
