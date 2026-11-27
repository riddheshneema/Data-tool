"""Sheet 2: plot guide (what each plot is) + schedule CSV."""
import sys, csv; sys.path.insert(0, '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/v7')
import render_v7 as rv
from render_v7 import *
from collections import Counter
import matplotlib.patheffects as pe
info = rv.info; V = rv.V; NA = K.area
def tier(p):
    t = p['tags']
    if 'stream-facing' in t: return 1
    if 'park-facing' in t or 'park-side' in t: return 2
    if 'beside the stream lawn' in t or 'garden-side' in t: return 3
    if p['corner']: return 4
    return 5 if p['front'] == 'lo' else 6
TN = {1: 'Stream-facing', 2: 'On the Central Park', 3: 'Beside a garden or the stream lawn', 4: 'Corner plot', 5: 'Standard, faces north', 6: 'Standard, faces south'}
TC = {1: '#a9d6f5', 2: '#ffd966', 3: '#c9b6e8', 4: '#f7b58a', 5: '#fdf6e4', 6: '#f1d3cc'}
for p in info: p['tier'] = tier(p)
def code(p):
    t = p['tags']; c = ''
    if 'stream-facing' in t: c += 'S'
    if 'park-facing' in t or 'park-side' in t: c += 'P'
    if 'beside the stream lawn' in t or 'garden-side' in t: c += 'G'
    if p['corner']: c += 'C'
    if 'on the avenue' in t: c += 'A'
    if any('T-junction' in x for x in p['cautions']): c += ' T!'
    if any('services' in x for x in p['cautions']): c += ' Y!'
    if p.get('special'): c = 'L' + c
    return c.strip()
fig = plt.figure(figsize=(16.54, 11.69))
fig.text(0.012, 0.972, 'JALKOTI COLONY — PLOT GUIDE', fontsize=15, weight='bold', color='#1e3a2b', va='top')
fig.text(0.012, 0.945, f'Layout v{rv.VER}: what each of the {len(info)} plots is, for pricing and for showing buyers', fontsize=8.6, color='#555', va='top')
ax = fig.add_axes([0.008, 0.33, 0.60, 0.60]); draw_plan(ax, plot_fill=lambda p: TC[p['tier']], small=True)
for p in info:
    c = p['poly'].centroid; fr = FR[p['grid']]
    if any('T-junction' in x for x in p['cautions']): ax.plot(c.x + fr.ev[0] * 4, c.y + fr.ev[1] * 4, marker='^', ms=4.5, color='#c62828', zorder=9)
    if any('services' in x for x in p['cautions']): ax.plot(c.x + fr.ev[0] * 4, c.y + fr.ev[1] * 4, marker='s', ms=3.8, color='#555', zorder=9)
ax.set_xlim(108, 474); ax.set_ylim(-275, -40); ax.set_aspect('equal'); ax.axis('off')
# legend + tier table
lg = fig.add_axes([0.012, 0.02, 0.60, 0.30]); lg.axis('off'); lg.set_xlim(0, 1); lg.set_ylim(0, 1)
lg.text(0, 0.96, 'PRICE GROUPS (suggested)', fontsize=8.8, weight='bold', color='#1e3a2b', va='top'); lg.plot([0, 0.56], [0.885, 0.885], color='#1e3a2b', lw=0.6)
lg.text(0.30, 0.83, 'Plots', fontsize=6.6, weight='bold', ha='right'); lg.text(0.43, 0.83, 'Sq ft', fontsize=6.6, weight='bold', ha='right'); lg.text(0.56, 0.83, 'Share', fontsize=6.6, weight='bold', ha='right')
tot = sum(p['area'] for p in info); y = 0.755
for k in range(1, 7):
    ps = [p for p in info if p['tier'] == k]; a = sum(p['area'] for p in ps)
    lg.add_patch(plt.Rectangle((0, y - 0.028), 0.022, 0.056, fc=TC[k], ec='#9b7b4b', lw=0.5))
    lg.text(0.032, y, TN[k], fontsize=7, va='center'); lg.text(0.30, y, str(len(ps)), fontsize=7, ha='right', va='center')
    lg.text(0.43, y, f'{a:,.0f}', fontsize=7, ha='right', va='center'); lg.text(0.56, y, f'{a / tot * 100:.0f}%', fontsize=7, ha='right', va='center'); y -= 0.082
lg.text(0, y - 0.005, 'Total', fontsize=7, weight='bold', va='center'); lg.text(0.30, y - 0.005, str(len(info)), fontsize=7, weight='bold', ha='right', va='center'); lg.text(0.43, y - 0.005, f'{tot:,.0f}', fontsize=7, weight='bold', ha='right', va='center')
y -= 0.10
lg.plot(0.011, y, marker='^', ms=5, color='#c62828'); lg.text(0.032, y, 'looks straight down a side street (T-junction): set the gate off-axis, price a little lower', fontsize=6.6, va='center'); y -= 0.075
lg.plot(0.011, y, marker='s', ms=4.5, color='#555'); lg.text(0.032, y, 'backs onto the services yard: keep a planted screen; final yard position after the levels survey', fontsize=6.6, va='center')
lg.text(0.62, 0.96, "KEPT FROM THE ENGINEER'S OPTION 6", fontsize=8.8, weight='bold', color='#1e3a2b', va='top'); lg.plot([0.62, 1.0], [0.885, 0.885], color='#1e3a2b', lw=0.6)
yy = 0.83
for t_ in ['Road along the stream with a green edge', 'Plots in double rows between parallel roads', 'Lawn at the stream bend' + (', garden in the north-east' if not V['gardenE'].is_empty else ', garden on the stream at the Avenue'),
           'Central green with the clubhouse near the entry', '12 m road from the gate into the heart']:
    lg.text(0.62, yy, '•  ' + t_, fontsize=6.9, va='center'); yy -= 0.066
yy -= 0.03
lg.text(0.62, yy, 'CHANGED', fontsize=8.8, weight='bold', color='#1e3a2b', va='center'); lg.plot([0.62, 1.0], [yy - 0.045, yy - 0.045], color='#1e3a2b', lw=0.6); yy -= 0.11
for t_ in ['Hotel, shops and parking removed', 'Rows made straight, so plots are rectangles', 'Plots 3,000 sq ft and up (his: 2,000–2,520)', f"One road fewer through the middle; parks and gardens {(park.area + V['gardenN'].area + V['lawnW'].area + V['gardenE'].area) / NA * 100:.0f}% of the land"]:
    lg.text(0.62, yy, '•  ' + t_, fontsize=6.9, va='center'); yy -= 0.066
# plot list
tb = fig.add_axes([0.625, 0.02, 0.37, 0.955]); tb.axis('off'); tb.set_xlim(0, 3); tb.set_ylim(0, 1)
tb.text(0, 0.985, 'PLOT LIST', fontsize=8.8, weight='bold', color='#1e3a2b', va='top'); tb.plot([0, 2.97], [0.958, 0.958], color='#1e3a2b', lw=0.6)
per = 25 if len(info) <= 75 else 26; rh = 0.0318 if len(info) <= 75 else 0.0306
for ci in range(3):
    x0 = ci + 0.0
    for lbl, dx, ha in (('No', 0.10, 'right'), ('Front×depth', 0.14, 'left'), ('Sq ft', 0.60, 'right'), ('Faces', 0.64, 'left'), ('Notes', 0.78, 'left')):
        tb.text(x0 + dx, 0.94, lbl, fontsize=6.0, weight='bold', ha=ha, va='center')
    for ri, p in enumerate(info[ci * per:(ci + 1) * per]):
        yv = 0.94 - (ri + 1) * rh
        tb.add_patch(plt.Rectangle((x0 + 0.005, yv - rh * 0.36), 0.035, rh * 0.72, fc=TC[p['tier']], ec='#9b7b4b', lw=0.3))
        dim = f"{round(p['front_w'] * FT)}×{round(p['depth'] * FT)}" if 'cross' not in p['shape'] else f"{round(p['front_w'] * FT)}/{round(p['back_w'] * FT)}×{round(p['depth'] * FT)}"
        if p.get('special'): dim = f"{round(p['wide'] * FT)}×{round(p['dmin'] * FT)}–{round(p['dmax'] * FT)}" if p['dmax'] - p['dmin'] > 1 else f"{round(p['wide'] * FT)}×{round(p['dmax'] * FT)}"
        tb.text(x0 + 0.10, yv, str(p['no']), fontsize=6.2, ha='right', va='center', weight='bold'); tb.text(x0 + 0.14, yv, dim, fontsize=6.0, va='center')
        tb.text(x0 + 0.60, yv, f"{p['area']:,.0f}", fontsize=6.0, ha='right', va='center'); tb.text(x0 + 0.64, yv, 'N' if p['front'] == 'lo' else 'S', fontsize=6.0, va='center')
        tb.text(x0 + 0.78, yv, code(p), fontsize=5.8, va='center', color='#333')
tb.text(0, 0.94 - (per + 1.3) * rh, 'Notes:  S stream-facing · P on the Central Park · G beside a garden or the stream lawn · C corner · A on the Avenue', fontsize=5.9, va='center', color='#333')
tb.text(0, 0.94 - (per + 2.1) * rh, 'T! looks down a T-junction · Y! backs onto the services yard · L larger plot with an irregular back (width × depth range).', fontsize=5.9, va='center', color='#333')
tb.text(0, 0.94 - (per + 2.9) * rh, 'Plots 1–11 Third Street south side · 12–26 Third Street north side · 27–42 Second Street south side', fontsize=5.9, va='center', color='#333')
tb.text(0, 0.94 - (per + 3.7) * rh, '43–61 Second Street north side · 62–75 Stream Drive.' + ('' if len(info) <= 75 else '   New: 76 beside the clubhouse (Third Street) · 77 Second Street, park side.'), fontsize=5.9, va='center', color='#333')
fig.savefig(OUT + f'Jalkoti_Colony_v{rv.VER}_Plot_Guide.pdf'); fig.savefig(OUT + f'Jalkoti_Colony_v{rv.VER}_Plot_Guide.png', dpi=170)
with open(OUT + f'Jalkoti_Colony_v{rv.VER}_Plot_Schedule.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['Plot', 'Street', 'Side of street', 'Faces', 'Front (ft)', 'Back (ft)', 'Depth (ft)', 'Area (sq ft)', 'Area (m2)', 'Shape', 'Price group', 'Premiums', 'Cautions', 'Nearest park or garden (m)', 'Drive from gate (m)'])
    for p in info:
        side = 'stream side' if p['row'] == 'A1' else ('north side' if p['row'] in ('A2', 'B2') else 'south side')
        w.writerow([p['no'], p['street'], side, 'North' if p['front'] == 'lo' else 'South', round(p['front_w'] * FT, 1), round(p['back_w'] * FT, 1) if not p.get('special') else '', (round(p['depth'] * FT, 1) if not p.get('special') else f"{round(p['dmin'] * FT)}-{round(p['dmax'] * FT)}"), round(p['area']), round(p['area'] / SQFT, 1),
                    p['shape'], TN[p['tier']], '; '.join(p['tags']), '; '.join(c for c in p['cautions'] if c != 'south-facing'), round(p['park_m']), round(p['gate_m'])])
print('sheet 2 + schedule saved;', {TN[k]: sum(1 for p in info if p['tier'] == k) for k in TN})
