import sys, json, numpy as np, warnings; warnings.filterwarnings('ignore')
sys.path.insert(0,'/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/plan'); import d8
from shapely import wkt
from shapely.geometry import Point, LineString
from shapely import affinity
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
SQFT=10.7639
r=d8.design(100,0,45,90,'m12',0,return_geom=True)
g=r['geom']; C=wkt.loads(g['C']); R=wkt.loads(g['R']); rpark=wkt.loads(g['river_park'])
plots=[(wkt.loads(s),k) for s,k in g['plots']]
def front(p,road): return p.buffer(0.8).intersection(road).area/0.8
elems=[]
drive=wkt.loads(r['drive']); dmed=wkt.loads(r['drive_med']) if r['drive_med'] else None
elems.append(('RD','River drive',drive,dmed,12))
elems.append(('EB','Entry boulevard (at colony gate)',wkt.loads(r['boul']),wkt.loads(r['bmed']),24))
for i,s,m in r['per_street']:
    elems.append((f'S{i}',f'Street {i}',wkt.loads(s),wkt.loads(m),12))
rows=[]
for code,name,poly,med,w in elems:
    L=poly.area/w
    fp=[(p,k) for p,k in plots if front(p,poly)>=8]
    # side split: use the road's long axis
    mrr=poly.minimum_rotated_rectangle; c=list(mrr.exterior.coords)
    e=[(Point(c[j]).distance(Point(c[j+1])),j) for j in range(2)]; j=max(e)[1]
    ax_=np.array(c[j+1])-np.array(c[j]); ax_=ax_/np.linalg.norm(ax_); nrm=np.array([-ax_[1],ax_[0]]); cen=np.array(poly.centroid.coords[0])
    if code=='RD':
        a=[x for x in fp if x[1]=='River-front villa']; b=[x for x in fp if x[1]!='River-front villa']
        sides=('river side','inland side')
    else:
        a=[x for x in fp if np.dot(np.array(x[0].centroid.coords[0])-cen,nrm)>0]; b=[x for x in fp if x not in a]
        sides=('side A','side B')
    river_facing=sum(1 for p,k in fp if k=='River-front villa')
    rows.append(dict(code=code,name=name,length=round(L),width=w,median_sqm=round(med.area) if med is not None else 0,
                     plots_A=len(a),plots_B=len(b),river_plots=river_facing,cen=[round(v) for v in poly.centroid.coords[0]]))
for x in rows: print(x)
json.dump(rows,open('audit.json','w'))
# annotated map
fig,ax=plt.subplots(figsize=(10,8))
def fill(gm,**kw):
    for p in getattr(gm,'geoms',[gm]):
        if p.geom_type=='Polygon' and not p.is_empty:
            xx,yy=p.exterior.xy; ax.fill(xx,yy,**kw)
fill(R.intersection(C.buffer(60)),fc='#9fd3f2'); fill(rpark,fc='#c5e1a5')
for p,k in plots: fill(p,fc='#fff3d6' if k.startswith('River') else 'white',ec='#b71c1c',lw=0.5)
cols=['#ef6c00','#6a1b9a','#00838f','#2e7d32','#c62828','#283593','#ad1457','#4e342e']
for (code,name,poly,med,w),col,x in zip(elems,cols,rows):
    fill(poly,fc=col,alpha=0.45,ec=col)
    if med is not None: fill(med,fc='#1b5e20')
    ax.text(*x['cen'],f"{code}\n{x['length']} m\n{x['plots_A']}+{x['plots_B']} plots\nmedian {x['median_sqm']} m²",fontsize=7,ha='center',va='center',weight='bold',color='k',
            bbox=dict(fc='white',ec=col,alpha=0.9,boxstyle='round,pad=0.25'))
ax.set_aspect('equal'); ax.set_xlim(110,470); ax.set_ylim(-270,-45); ax.axis('off')
ax.set_title('Road audit – 4,000 sq ft layout B (current): every road, its length, plots fronting each side, median area',fontsize=10)
plt.savefig('/home/user/Data-tool/site_plans/Road_Audit_4000_B.png',dpi=130,bbox_inches='tight')
