"""Fit 08_master_plan.png (from the final zip) to the plan geometry, then lift its stream into plan coordinates."""
import sys, os, math, pickle, json, numpy as np, warnings; warnings.filterwarnings('ignore')
SP = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
PLAN = SP + 'plan/'; OUT = SP + 'brochure2/'
os.makedirs(SP + 'review', exist_ok=True)
sys.path.insert(0, PLAN); os.chdir(PLAN)
exec(open('dims.py').read().split("if __name__=='__main__':")[0])
from PIL import Image, ImageDraw
from shapely import affinity
from shapely.geometry import Polygon, MultiPolygon
from skimage import measure, morphology
im = np.array(Image.open(SP + '../brochure/source/images/08_master_plan.png').convert('RGB')).astype(int)
H, W, _ = im.shape
def near(c, tol=14): return (np.abs(im - np.array(c)).sum(2) < tol)
body = np.zeros((H, W), bool); body[100:1930, :] = True
resort = near((236, 243, 219), 10)
colony08 = (near((251, 243, 211)) | near((243, 219, 179)) | near((147, 147, 147), 10) | near((124, 179, 66), 20) | near((46, 125, 50), 30)) & body & ~resort
from scipy import ndimage
colony08 = ndimage.binary_opening(colony08, iterations=2)
Image.fromarray((colony08*255).astype(np.uint8)).resize((800,669)).save(SP+'review/colony08_mask.png')
blue = near((78, 163, 211), 40) & body
print('colony px', colony08.sum(), 'blue px', blue.sum())
pc = C.centroid
def T(g, p):
    th, s, tx, ty, ax = p
    g = affinity.rotate(affinity.translate(g, -pc.x, -pc.y), th, origin=(0, 0))
    return affinity.affine_transform(g, [s * ax, 0, 0, -s, tx, ty])
def raster(g):
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    for p in getattr(g, 'geoms', [g]):
        d.polygon([tuple(c) for c in p.exterior.coords], fill=1)
        for r in p.interiors: d.polygon([tuple(c) for c in r.coords], fill=0)
    return np.array(m, bool)
ys, xs = np.nonzero(colony08)
p = [-5.55, 4.65, xs.mean(), ys.mean(), 1.0]
cent = T(C, p).centroid; p[2] += xs.mean() - cent.x; p[3] += ys.mean() - cent.y
def iou(p):
    m = raster(T(C, p)); return (m & colony08).sum() / (m | colony08).sum()
best = iou(p); print('start IoU %.4f' % best)
for steps in ((1.0, 0.1, 8, 0.02), (0.3, 0.03, 3, 0.006), (0.1, 0.01, 1, 0.002), (0.03, 0.003, 0.4, 0.0007)):
    improved = True
    while improved:
        improved = False
        for i, st in ((0, steps[0]), (1, steps[1]), (2, steps[2]), (3, steps[2]), (4, steps[3])):
            for sg in (1, -1):
                q = list(p); q[i] += sg * st; v = iou(q)
                if v > best: best, p, improved = v, q, True
print('fit: rot %.2f deg, scale %.3f px/m, aniso %.4f, IoU %.4f' % (p[0], p[1], p[4], best))
# stream: close the gap under the label box, keep big components, contour, lift to plan
b = morphology.binary_closing(blue, morphology.disk(28))
lab = measure.label(b); keep = np.zeros_like(b)
for r in measure.regionprops(lab):
    if r.area > 20000: keep |= lab == r.label
cs = measure.find_contours(np.pad(keep, 1).astype(float), 0.5)
th, s, tx, ty, ax = p
def inv(x, y):
    X = (x - tx) / (s * ax); Y = -(y - ty) / s
    a = math.radians(-th); return (X * math.cos(a) - Y * math.sin(a) + pc.x, X * math.sin(a) + Y * math.cos(a) + pc.y)
polys = []
for c in cs:
    if len(c) < 50: continue
    pts = [inv(x - 1, y - 1) for y, x in c]
    pg = Polygon(pts).buffer(0)
    if pg.area > 50: polys.append(pg)
stream = unary_union(polys).simplify(0.4)
print('stream area m2 %.0f, bounds %s' % (stream.area, [round(v) for v in stream.bounds]))
pickle.dump(dict(stream=stream, fit=p), open(OUT + 'stream08.pkl', 'wb'))
# check overlay: plots and roads from the plan, drawn on 08
ov = Image.open(SP + '../brochure/source/images/08_master_plan.png').convert('RGB'); d = ImageDraw.Draw(ov)
for g in list(PL.values()) + [C]:
    for q in getattr(T(g, p), 'geoms', [T(g, p)]): d.line([tuple(c) for c in q.exterior.coords], fill=(220, 0, 160), width=3)
for q in getattr(T(stream, p), 'geoms', [T(stream, p)]): d.line([tuple(c) for c in q.exterior.coords], fill=(255, 0, 0), width=3)
os.makedirs(SP + 'review', exist_ok=True); ov.resize((1600, 1337)).save(SP + 'review/fit08.jpg', quality=85)
