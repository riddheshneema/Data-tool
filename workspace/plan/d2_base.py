import json, pickle, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import wkt
D='/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
G=pickle.load(open(D+'site/geo.pkl','rb')); P=G['P']
river=np.load(D+'site/river.npy'); res=0.5
# vectorise river mask
cs=plt.contour(np.arange(river.shape[1])*res, -np.arange(river.shape[0])*res, river.astype(float), levels=[0.5])
polys=[]
for path in cs.get_paths():
    for ring in path.to_polygons():
        if len(ring)>3:
            p=Polygon(ring).buffer(0)
            if p.area>200: polys.append(p)
R=unary_union(polys)
print('river vector area',round(R.area))
F=json.load(open(D+'plan/final.json'))
colony=wkt.loads(F['colony']); resort=wkt.loads(F['resort'])
pickle.dump(dict(river=R,colony=colony,resort=resort,P=P),open(D+'plan/d2_base.pkl','wb'))
for d in [25,58.5,71.5,102,110,140.5,153.5,180]:
    a=colony.difference(R.buffer(d)).area
    print(f'colony area beyond {d} m: {a/4046.86:.2f} ac')
