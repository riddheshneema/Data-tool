"""Road network of the layout: skeleton centre-lines, widths, junctions, dead ends, lengths, travel distance from the gate."""
import pickle,numpy as np,networkx as nx,warnings; warnings.filterwarnings('ignore')
from shapely import wkt
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union
from skimage.morphology import skeletonize
from scipy import ndimage
import matplotlib.path as mpath
RES=0.25
def load(tag):
    S=pickle.load(open('final_'+tag+'.pkl','rb')); G=lambda w: wkt.loads(w) if w else None
    return S,G
def raster(poly,bounds):
    x0,y0,x1,y1=bounds; nx_=int((x1-x0)/RES)+1; ny_=int((y1-y0)/RES)+1
    xs=x0+np.arange(nx_)*RES; ys=y0+np.arange(ny_)*RES; X,Y=np.meshgrid(xs,ys); pts=np.c_[X.ravel(),Y.ravel()]
    m=np.zeros(len(pts),bool)
    for p in getattr(poly,'geoms',[poly]):
        if p.geom_type!='Polygon': continue
        inside=mpath.Path(np.array(p.exterior.coords)).contains_points(pts)
        for h in p.interiors: inside&=~mpath.Path(np.array(h.coords)).contains_points(pts)
        m|=inside
    return m.reshape(ny_,nx_),xs,ys
def network(net_poly,prune=9.0):
    b=net_poly.bounds; bounds=(b[0]-3,b[1]-3,b[2]+3,b[3]+3)
    M,xs,ys=raster(net_poly,bounds)
    D=ndimage.distance_transform_edt(M)*RES          # distance to road edge (m)
    SK=skeletonize(M)
    iy,ix=np.nonzero(SK); idx={(a,b):i for i,(a,b) in enumerate(zip(iy,ix))}
    g=nx.Graph()
    for i,(a,b) in enumerate(zip(iy,ix)):
        g.add_node(i,xy=(xs[b],ys[a]),w=2*D[a,b])
        for da in (-1,0,1):
            for db in (-1,0,1):
                j=idx.get((a+da,b+db))
                if j is not None and j>i: g.add_edge(i,j,len=RES*np.hypot(da,db))
    # prune short spurs (corner and end artefacts of the skeleton)
    for _ in range(6):
        ends=[n for n in g if g.degree(n)==1]; removed=False
        for e in ends:
            path=[e]; cur=e; L=0
            while True:
                nb=[n for n in g.neighbors(cur) if n not in path]
                if len(nb)!=1 or g.degree(cur)>2 and cur!=e: break
                L+=g[cur][nb[0]]['len']; path.append(nb[0]); cur=nb[0]
                if g.degree(cur)!=2: break
            if g.degree(cur)>=3 and L<prune:
                g.remove_nodes_from(path[:-1]); removed=True
        if not removed: break
    g.remove_nodes_from([n for n in list(g) if g.degree(n)==0])
    return g,D,(xs,ys)
def simplify_graph(g):
    """collapse degree-2 chains into edges with polylines"""
    key=[n for n in g if g.degree(n)!=2]; H=nx.MultiGraph(); seen=set()
    for k in key: H.add_node(k,xy=g.nodes[k]['xy'])
    for k in key:
        for nb in g.neighbors(k):
            if (k,nb) in seen: continue
            path=[k,nb]; L=g[k][nb]['len']
            while g.degree(path[-1])==2:
                nxt=[n for n in g.neighbors(path[-1]) if n!=path[-2]][0]; L+=g[path[-1]][nxt]['len']; path.append(nxt)
            for a,b in zip(path[:-1],path[1:]): seen.add((a,b)); seen.add((b,a))
            ws=[g.nodes[n]['w'] for n in path]
            H.add_edge(path[0],path[-1],len=L,line=LineString([g.nodes[n]['xy'] for n in path]),w=ws)
    return H
