import sys,json,math,pickle,numpy as np,networkx as nx,warnings; warnings.filterwarnings('ignore')
sys.path.insert(0,'.'); from roadnet import *
TAG=sys.argv[1]; S,G=load(TAG); SQ=10.764; AC=4046.86
C,row,rpark,walk,svc,access,R=[G(S[k]) for k in ('C','row','rpark','walk','svc','access','R')]
roads,gard=G(S['roads']),G(S['gard']); parks=G(S['parks']) if S.get('parks') else None
plots=[(t,G(w),k) for t,w,k in S['plots']]
streets={n:G(w) for n,w in S['streets']}; drive=G(S['drive']) if S.get('drive') else None
GATE=Point(331,-262); MAIN=Point(336,-487)
T=C.area; out={}
# ---------- areas ----------
pl=sum(p.area for _,p,_ in plots); rest=C.difference(unary_union([row,rpark,walk]+[p for _,p,_ in plots]))
print(f'layout (colony) area {T:,.0f} m2 = {T/AC:.2f} ac = {T/1e4:.3f} ha')
print(f'plots {pl/T:.1%} | road ROW {row.intersection(C).area/T:.1%} (of which garden medians {gard.area/T:.1%}) | promenade {rpark.area/T:.1%} | walkway {walk.area/T:.2%} | other green/leftover {rest.area/T:.2%}')
# ---------- road network ----------
net=unary_union([row,access]).buffer(0.3).buffer(-0.3)
g,Dm,(xs,ys)=network(net); H=simplify_graph(g)
def nearest(pt): return min(H.nodes,key=lambda n:Point(H.nodes[n]['xy']).distance(pt))
nm=nearest(MAIN)
ends=[n for n in H if H.degree(n)==1 and n!=nm]
ART=[]   # skeleton spurs at bends / road-edge jogs, not real dead ends

print('\nROAD NETWORK: junctions',sum(1 for n in H if H.degree(n)>=3),'| dead ends',len(ends))
def name_of(line):
    best,bv=None,0
    for n,poly in list(streets.items())+([('RD',drive)] if drive is not None else [])+[('ACCESS',access)]:
        v=line.intersection(poly.buffer(1.0)).length
        if v>bv: best,bv=n,v
    return best if bv>0.5*line.length else 'link'
edges=[]
for a,b,d in H.edges(data=True):
    ws=np.array(d['w']); core=ws[int(len(ws)*0.15):max(int(len(ws)*0.85),int(len(ws)*0.15)+1)]
    edges.append(dict(a=a,b=b,len=d['len'],name=name_of(d['line']),wmin=float(np.percentile(core,5)) if len(core) else float(ws.min()),line=d['line']))
for e in sorted(edges,key=lambda e:e['name']):
    print(f"  {e['name']:6s} segment {e['len']:6.1f} m | width (5th pct, mid-segment) {e['wmin']:5.1f} m | ends: {'dead-end' if (e['a'] in ends or e['b'] in ends) else 'junction'}")
tot={}
for e in edges: tot[e['name']]=tot.get(e['name'],0)+e['len']
print('  road totals:',{k:round(v) for k,v in tot.items()})
# dead ends: length from the end to the nearest junction (+ half width for the road end)
dead=[]
for n in ends:
    e=[x for x in edges if n in (x['a'],x['b'])][0]
    (dead if e['len']>=25 else ART).append((e['name'],round(e['len']+6),H.nodes[n]['xy']))
print('  dead ends (name, length from the junction centre-line to the road end, end point):',[(a,b,tuple(round(v) for v in c)) for a,b,c in dead])
print('  ignored skeleton spurs (bends, edge jogs):',[(a,b,tuple(round(v) for v in c)) for a,b,c in ART])
# travel distance along the road network from the colony gate to each plot's frontage
Gw=nx.Graph()
for e in edges: Gw.add_edge(e['a'],e['b'],len=e['len'])
eg=min(edges,key=lambda e:e['line'].distance(GATE)); tg=eg['line'].project(GATE)
da_=nx.single_source_dijkstra_path_length(Gw,eg['a'],weight='len'); db_=nx.single_source_dijkstra_path_length(Gw,eg['b'],weight='len')
dist={n:min(tg+da_.get(n,1e9),eg['len']-tg+db_.get(n,1e9)) for n in Gw}
def plot_dist(p):
    best=1e9
    for e in edges:
        L=e['line']
        if L.distance(p)>9: continue
        t=L.project(p.centroid)
        if e is eg: best=min(best,abs(t-tg)); continue
        best=min(best,dist.get(e['a'],1e9)+t,dist.get(e['b'],1e9)+(L.length-t))
    return best
gate_node=eg['a']
pdist={t:plot_dist(p) for t,p,k in plots}
far=sorted(pdist.items(),key=lambda x:-x[1])[:5]
print('  farthest plots from the colony gate along 12 m roads (m):',[(t,round(d)) for t,d in far])
pickle.dump(dict(edges=[(e['name'],e['len'],e['wmin'],e['line'].wkt) for e in edges],dead=dead,pdist=pdist,gate=gate_node),open('roadtest_'+TAG+'.pkl','wb'))
