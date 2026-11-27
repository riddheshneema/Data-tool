"""Cut plots along a reference road centre-line (curved), with frontage-perpendicular cuts."""
import math
from shapely.geometry import LineString, MultiLineString, Point, Polygon, MultiPolygon
from shapely.ops import split, unary_union

import numpy as np, networkx as nx
from skimage.morphology import skeletonize
from PIL import Image, ImageDraw
SQFT = 10.7639

def _normal(ref, s, closed):
    L = ref.length
    a = (s - 1.0) % L if closed else max(0.0, s - 1.0)
    b = (s + 1.0) % L if closed else min(L, s + 1.0)
    p1, p2 = ref.interpolate(a), ref.interpolate(b)
    tx, ty = p2.x - p1.x, p2.y - p1.y
    n = math.hypot(tx, ty) or 1.0
    return -ty / n, tx / n

def frontage_runs(ref, piece, reach, step=0.5, closed=True):
    """Parameter intervals of `ref` that lie within `reach` of `piece`."""
    L = ref.length; k = int(L / step)
    flags = [ref.interpolate(i * step).distance(piece) <= reach for i in range(k)]
    runs, i = [], 0
    while i < k:
        if flags[i]:
            j = i
            while j + 1 < k and flags[j + 1]: j += 1
            runs.append([i * step, j * step]); i = j + 1
        else: i += 1
    if closed and len(runs) > 1 and runs[0][0] == 0 and runs[-1][1] >= (k - 1) * step:
        runs[0] = [runs[-1][0] - L, runs[0][1]]; runs.pop()
    return runs

def cut_piece(piece, ref, width, reach, depth, closed=True, side=None):
    """Split `piece` into plots of about `width` frontage, cuts perpendicular to `ref`."""
    L = ref.length
    cuts = []
    for a, b in frontage_runs(ref, piece, reach, closed=closed):
        run = b - a
        n = max(1, int(run / width + 0.3))
        for k in range(1, n):
            s = (a + k * run / n) % L if closed else a + k * run / n
            p = ref.interpolate(s); nx, ny = _normal(ref, s, closed)
            for sg in ((1, -1) if side is None else (side,)):
                q0 = (p.x + sg * nx * (reach - 2.0), p.y + sg * ny * (reach - 2.0))
                q1 = (p.x + sg * nx * (reach + depth + 6.0), p.y + sg * ny * (reach + depth + 6.0))
                seg = LineString([q0, q1])
                if seg.intersects(piece): cuts.append(seg)
    if not cuts: return [piece]
    parts = split(piece, MultiLineString(cuts))
    return [g for g in parts.geoms if g.area > 1.0]

def cut_piece_area(piece, ref, a_target, w_min, reach, depth, closed=True, step=1.0):
    """Equal-area plots along `ref`: n = min(area / a_target, frontage / w_min)."""
    L = ref.length
    cuts = []
    for a, b in frontage_runs(ref, piece, reach, closed=closed):
        run = b - a
        if run < w_min: continue
        fine = []
        k = int(run / step)
        for i in range(1, k):
            s = (a + i * run / k) % L if closed else a + i * run / k
            p = ref.interpolate(s); nx, ny = _normal(ref, s, closed)
            segs = []
            for sg in (1, -1):
                q0 = (p.x + sg * nx * (reach - 2.0), p.y + sg * ny * (reach - 2.0))
                q1 = (p.x + sg * nx * (reach + depth + 6.0), p.y + sg * ny * (reach + depth + 6.0))
                seg = LineString([q0, q1])
                if seg.intersects(piece): segs.append(seg)
            fine.append((i * run / k, segs))
        # area swept between consecutive fine cuts
        sub = piece.intersection(ref.buffer(reach + depth + 6.0))
        allc = [sg for _, segs in fine for sg in segs]
        if not allc: continue
        slices = [g for g in split(sub, MultiLineString(allc)).geoms if g.area > 0.01]
        def pos(g):
            t = ref.project(g.centroid) - a
            if closed: t = t % L
            return t
        slices = sorted([(pos(g), g.area) for g in slices])
        tot = sum(x[1] for x in slices)
        n = max(1, min(int(tot / a_target), int(run / w_min)))
        if n == 1: continue
        acc, targets, j = 0.0, [tot * m / n for m in range(1, n)], 0
        marks = []
        for t, ar in slices:
            acc += ar
            while j < len(targets) and acc >= targets[j]:
                marks.append(t); j += 1
        for t in marks:
            # nearest fine cut to t
            best = min(fine, key=lambda f: abs(f[0] - t))
            cuts += best[1]
    if not cuts: return [piece]
    parts = split(piece, MultiLineString(cuts))
    return [g for g in parts.geoms if g.area > 1.0]

def merge_small(plots, min_area, keep_free=()):
    """Merge plots under min_area into the neighbour they share the longest edge with."""
    plots = [p for p in plots]
    changed = True
    while changed:
        changed = False
        plots.sort(key=lambda g: g.area)
        for i, g in enumerate(plots):
            if g.area >= min_area: continue
            best, bl = None, 0.0
            for j, h in enumerate(plots):
                if j == i: continue
                l = g.boundary.intersection(h.boundary.buffer(0.05)).length
                if l > bl: best, bl = j, l
            if best is None or bl < 2.0: continue
            m = unary_union([g, plots[best]]).buffer(0.01).buffer(-0.01)
            plots = [h for k_, h in enumerate(plots) if k_ not in (i, best)] + [m]
            changed = True
            break
    return plots

def frontage_len(plot, roads, tol=0.6):
    return plot.boundary.intersection(roads.buffer(tol)).length

def min_width(plot):
    r = plot.minimum_rotated_rectangle
    xs = list(r.exterior.coords)
    e = [math.dist(xs[i], xs[i + 1]) for i in range(4)]
    return min(e)

def centreline(poly, res=0.5):
    x0, y0, x1, y1 = poly.bounds; W_, H_ = int((x1 - x0) / res) + 3, int((y1 - y0) / res) + 3
    im = Image.new('L', (W_, H_), 0); d = ImageDraw.Draw(im)
    d.polygon([((x - x0) / res + 1, (y1 - y) / res + 1) for x, y in poly.exterior.coords], fill=1)
    sk = skeletonize(np.array(im, bool)); ys, xs = np.nonzero(sk)
    G = nx.Graph(); pts = set(zip(xs, ys))
    for x, y in pts:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (dx or dy) and (x + dx, y + dy) in pts: G.add_edge((x, y), (x + dx, y + dy), weight=math.hypot(dx, dy))
    a = max(G.nodes, key=lambda n: n[0]); dist = nx.single_source_dijkstra_path_length(G, a)
    b = max(dist, key=dist.get); dist2 = nx.single_source_dijkstra_path_length(G, b); a = max(dist2, key=dist2.get)
    path = nx.dijkstra_path(G, a, b)
    line = LineString([((x - 1) * res + x0, y1 - (y - 1) * res) for x, y in path]).simplify(1.5)
    for _ in range(3):  # Chaikin smoothing
        c = list(line.coords); new = [c[0]]
        for p, q in zip(c[:-1], c[1:]): new += [(0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]), (0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1])]
        new.append(c[-1]); line = LineString(new)
    return line
