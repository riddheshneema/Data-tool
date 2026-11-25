"""v7 construction kit: two straight plot grids (west + east) that follow the two stream reaches and meet on a mitre line."""
import sys, os, math, pickle, json, warnings; warnings.filterwarnings('ignore')
SP = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/'
os.chdir(SP + 'plan'); sys.path.insert(0, SP + 'plan')
exec(open('dims.py').read().split("if __name__=='__main__':")[0])
from shapely.geometry import Polygon, LineString, Point, box, MultiPolygon
from shapely.ops import unary_union
SQFT = 10.7639; FT = 3.28084
class Fr:
    def __init__(s, o, th):
        s.o = o; t = math.radians(th); s.th = th
        s.eu = (math.cos(t), math.sin(t)); s.ev = (math.sin(t), -math.cos(t))
    def xy(s, u, v): return (s.o[0] + u * s.eu[0] + v * s.ev[0], s.o[1] + u * s.eu[1] + v * s.ev[1])
    def uv(s, x, y):
        dx, dy = x - s.o[0], y - s.o[1]
        return (dx * s.eu[0] + dy * s.eu[1], dx * s.ev[0] + dy * s.ev[1])
    def rect(s, u0, u1, v0, v1): return Polygon([s.xy(u0, v0), s.xy(u1, v0), s.xy(u1, v1), s.xy(u0, v1)])
    def line(s, pts): return LineString([s.xy(u, v) for u, v in pts])
    def arc(s, cu, cv, r, a0, a1, n=24):
        """arc in frame coords; angle measured from +u towards +v"""
        return [(cu + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cv + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
def big(g): return max(getattr(g, 'geoms', [g]), key=lambda x: x.area) if not g.is_empty else g
def parts(g): return [q for q in getattr(g, 'geoms', [g]) if q.geom_type == 'Polygon' and not q.is_empty]
def fillet(pts, R, n=10):
    """round every interior corner of a polyline with radius R"""
    out = [pts[0]]
    for a, b, c in zip(pts[:-2], pts[1:-1], pts[2:]):
        v1 = (a[0] - b[0], a[1] - b[1]); v2 = (c[0] - b[0], c[1] - b[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2); v1 = (v1[0] / l1, v1[1] / l1); v2 = (v2[0] / l2, v2[1] / l2)
        cosang = max(-1, min(1, v1[0] * v2[0] + v1[1] * v2[1])); ang = math.acos(cosang)
        if abs(math.pi - ang) < 1e-3: out.append(b); continue
        t = min(R / math.tan(ang / 2), l1 * 0.49, l2 * 0.49); r = t * math.tan(ang / 2)
        p1 = (b[0] + v1[0] * t, b[1] + v1[1] * t); p2 = (b[0] + v2[0] * t, b[1] + v2[1] * t)
        bis = (v1[0] + v2[0], v1[1] + v2[1]); bl = math.hypot(*bis); cdist = r / math.sin(ang / 2)
        ctr = (b[0] + bis[0] / bl * cdist, b[1] + bis[1] / bl * cdist)
        a1 = math.atan2(p1[1] - ctr[1], p1[0] - ctr[0]); a2 = math.atan2(p2[1] - ctr[1], p2[0] - ctr[0])
        d = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        out += [(ctr[0] + r * math.cos(a1 + d * k / n), ctr[1] + r * math.sin(a1 + d * k / n)) for k in range(n + 1)]
    out.append(pts[-1]); return out
