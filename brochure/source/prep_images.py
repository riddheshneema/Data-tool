"""Crops of the nine final images (zip e834f9c). Every crop is anchored bottom-right so Google's
provenance watermark stays in the picture."""
import sys, os, numpy as np
from PIL import Image
SRC, DST = sys.argv[1], sys.argv[2]; os.makedirs(DST, exist_ok=True)
def save(name, box, out, q=90):
    im = Image.open(os.path.join(SRC, name)).convert('RGB')
    w, h = im.size; x0, y0, x1, y1 = box(w, h)
    assert x1 == w and y1 == h, 'crop must keep the bottom-right corner'
    im.crop((x0, y0, x1, y1)).save(os.path.join(DST, out), quality=q, optimize=True, progressive=True)
    print(out, (x1 - x0, y1 - y0))
save('01_cover_aerial.png', lambda w, h: (w - round(h * 210 / 297), 0, w, h), 'p1_cover.jpg', 88)
save('02_maheshwar_ghats.png', lambda w, h: (0, 0, w, h), 'p2_ghats.jpg', 92)
save('06_entrance.png', lambda w, h: (0, 0, w, h), 'p3_entrance.jpg', 92)
for n, o in (('03_garden_boulevard.png', 'p5_boulevard.jpg'), ('03b_garden_boulevard_walkable.png', 'p5_boulevard_walk.jpg')):
    save(n, lambda w, h: (0, h - round(w * 5 / 4), w, h), o)          # 4:5, trims only sky
for n, o in (('04_streamside_garden.png', 'p5_garden.jpg'), ('05_villa.png', 'p6_villa.jpg')):
    save(n, lambda w, h: (0, h - w, w, h), o)
# 07 is two pictures stacked: keep the lower one (it carries the watermark), starting below the white gap
im = np.array(Image.open(os.path.join(SRC, '07_resort_cottages.png')).convert('L')).astype(float)
rows = np.where(im[:, 50:-50].mean(1) > 247)[0]; rows = rows[(rows > im.shape[0] * 0.3) & (rows < im.shape[0] * 0.7)]
top = int(rows.max()) + 6; print('07 gap rows', rows.min(), rows.max())
save('07_resort_cottages.png', lambda w, h: (0, top, w, h), 'p6_resort.jpg')
