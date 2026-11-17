"""Reference images for Google Flow, from the real layout (text-free where the model will look at them)."""
import sys, os, math, random, json, numpy as np, warnings; warnings.filterwarnings('ignore')
B = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/brochure/'
exec(open(B + 'make_art.py').read().split("# ------------------------------------------------------------------ schematic location map")[0])
OUT = '/home/user/Data-tool/brochure/flow_references/'; os.makedirs(OUT, exist_ok=True)
# 1. whole layout, top-down, no labels (cover aerial reference)
layout_art(B + 'ref_01.svg', labels=False, x0=92, x1=478, y0=-302, y1=-32, k=6.0, bg='#f3ead9')
# 2. the riverside garden strip and the river-front plots on the north run (garden reference)
layout_art(B + 'ref_04.svg', labels=False, x0=250, x1=430, y0=-125, y1=-30, k=12.0, bg='#f3ead9')
# 3. a garden boulevard (S3) from above, close in (street reference)
layout_art(B + 'ref_03a.svg', labels=False, x0=275, x1=345, y0=-200, y1=-120, k=14.0, bg='#f3ead9')
# 4. cross-section of the 12 m garden street, drawn to scale, no text
W, H = 1600, 700; sc = 1600 / 14.0
parts = [(1.0, '#bfb6a4'), (3.5, '#8d8d8d'), (3.0, '#6e9f58'), (3.5, '#8d8d8d'), (1.0, '#bfb6a4')]
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#f6efe2"/>']
x = sc * 1.0
svg.append(f'<rect x="0" y="470" width="{sc}" height="60" fill="#e3d6bd"/><rect x="{W - sc}" y="470" width="{sc}" height="60" fill="#e3d6bd"/>')
for w, c in parts:
    svg.append(f'<rect x="{x:.0f}" y="480" width="{w * sc:.0f}" height="50" fill="{c}"/>'); x += w * sc
for cx in (sc * 1.0 + sc * 4.5 + sc * 1.5,):
    svg.append(f'<rect x="{cx - 8:.0f}" y="330" width="16" height="150" fill="#6b4f2a"/><circle cx="{cx:.0f}" cy="300" r="120" fill="#5f8f4e"/><circle cx="{cx - 60:.0f}" cy="330" r="70" fill="#6e9f58"/><circle cx="{cx + 60:.0f}" cy="320" r="80" fill="#7fae63"/>')
for cx in (sc * 0.5, W - sc * 0.5):
    svg.append(f'<rect x="{cx - 6:.0f}" y="370" width="12" height="110" fill="#6b4f2a"/><circle cx="{cx:.0f}" cy="340" r="70" fill="#6e9f58"/>')
for cx in (sc * 2.6, sc * 7.7):
    svg.append(f'<rect x="{cx - 90:.0f}" y="440" width="180" height="40" rx="14" fill="#c9c3b6"/>')
svg.append(f'<rect x="0" y="230" width="{sc * 0.6:.0f}" height="250" fill="#efe6d4" stroke="#c7b48e" stroke-width="4"/><rect x="{W - sc * 0.6:.0f}" y="230" width="{sc * 0.6:.0f}" height="250" fill="#efe6d4" stroke="#c7b48e" stroke-width="4"/>')
svg.append('</svg>'); open(B + 'ref_03b.svg', 'w').write(''.join(svg))
# 5. one 45 x 90 ft villa plot on a garden boulevard, from above, no text
W, H = 1400, 1000; k = 1000 / 34.0
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#f3ead9"/>']
svg.append(f'<rect x="0" y="0" width="{12 * k:.0f}" height="{H}" fill="#e3dccd"/><rect x="{4.5 * k:.0f}" y="0" width="{3 * k:.0f}" height="{H}" fill="#7fae63"/>')
for y in np.arange(30, H, 95): svg.append(f'<circle cx="{6 * k:.0f}" cy="{y:.0f}" r="{1.3 * k:.0f}" fill="#5f8f4e"/>')
x0 = 12 * k + 6
for j, (yy, hh) in enumerate([(0, 13.72), (13.72, 13.72), (27.44, 6.56)]):
    svg.append(f'<rect x="{x0:.0f}" y="{yy * k:.0f}" width="{27.43 * k:.0f}" height="{hh * k:.0f}" fill="{"#fbf6ea" if j == 1 else "#f1e7d4"}" stroke="#b78b4e" stroke-width="{6 if j == 1 else 2}"/>')
svg.append(f'<rect x="{x0 + 3.6 * k:.0f}" y="{13.72 * k + 3 * k:.0f}" width="{(27.43 - 6.6) * k:.0f}" height="{(13.72 - 6) * k:.0f}" fill="none" stroke="#c46a2b" stroke-width="4" stroke-dasharray="14 10"/>')
svg.append('</svg>'); open(B + 'ref_05.svg', 'w').write(''.join(svg))
print('svgs ok')
