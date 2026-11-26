# callouts, labels, key and notes for the landscape sheet (runs inside landscape_v8.py)
halo = [pe.withStroke(linewidth=1.8, foreground='#ffffff')]
def call(n, xy):
    ax.add_patch(Circle(xy, 3.3, fc='#1e3a2b', ec='#ffffff', lw=0.8, zorder=10)); ax.text(xy[0], xy[1], str(n), color='#ffffff', fontsize=6.6, weight='bold', ha='center', va='center', zorder=11)
gx, gy = W.xy(GU, VS)
lw_pt = big(V['lawnW'].difference(STRIP).buffer(-6)).representative_point()
gr_pt = E.xy(176, 96)
KEY = [(1, (gx + 11, gy + 1), 'Entrance court', 'paved forecourt, planted island, gate'),
       (2, W.xy(GU + 11, 96), 'The Avenue', 'double row of flowering trees, gate to stream'),
       (3, W.xy(pu - PWd / 2 - 0.5, pv - 24.5), 'Central Park', 'oval lawn, walking loop, play circle, pavilion'),
       (4, W.xy(GU - 13, 1.5), 'Viewing deck', 'timber deck where the Avenue meets the stream'),
       (5, W.xy(GU + 27, 16.5 - 22), 'Stream Garden', 'lawn, stepped seating facing the water'),
       (6, W.xy(40, 3.2), 'Stream promenade', 'walking track with seats under riverside trees'),
       (7, (lw_pt.x - 9, lw_pt.y + 8), 'Stream Lawn', 'party lawn with a gazebo'),
       (8, W.xy(GU + 6 + 10, L['C1'][0] + 21.5), 'Clubhouse', 'pool and deck beside the gate'),
       (9, (gr_pt[0] + 3, gr_pt[1] + 2), 'East grove', 'fruit-tree grove in the corner by the boundary'),
       (10, W.xy(62, mid('s2') ), 'Street trees', 'one at each plot line on every street'),
       (11, E.xy(140, L['C1'][1] + 9), 'Screen planting', 'dense trees round the services yard')]
for n, xy, a, b in KEY: call(n, xy)
ax.text(186, -74, 'S T R E A M', fontsize=9, color='#3d7ea6', rotation=24, zorder=9, style='italic')
ax.text(150, -262, 'RESORT LAND', fontsize=8, color='#9a8a62', zorder=9)
ax.annotate('', xy=(462, -52), xytext=(462, -68), arrowprops=dict(arrowstyle='-|>', color='k', lw=1.6)); ax.text(462, -48.5, 'N', ha='center', fontsize=11, weight='bold')
ax.plot([395, 445], [-262, -262], color='k', lw=2.2); ax.text(420, -267.5, '50 m  (164 ft)', ha='center', fontsize=7)
ax.set_xlim(108, 474); ax.set_ylim(-275, -40); ax.set_aspect('equal'); ax.axis('off')
pn = fig.add_axes([0.778, 0.03, 0.215, 0.94]); pn.axis('off'); pn.set_xlim(0, 1); pn.set_ylim(0, 1)
pn.text(0, 0.995, 'JALKOTI COLONY', fontsize=15, weight='bold', va='top', color='#1e3a2b')
pn.text(0, 0.962, 'Landscape plan (concept) on layout v8', fontsize=8.6, va='top', color='#555')
y = 0.905; pn.text(0, y, 'KEY', fontsize=8.8, weight='bold', color='#1e3a2b'); y -= 0.008; pn.plot([0, 1], [y, y], color='#1e3a2b', lw=0.6); y -= 0.03
for n, xy, a, b in KEY:
    pn.plot(0.035, y - 0.004, marker='o', ms=11.5, color='#1e3a2b', clip_on=False)
    pn.text(0.035, y - 0.005, str(n), color='#fff', fontsize=6.2, weight='bold', ha='center', va='center')
    pn.text(0.09, y + 0.006, a, fontsize=7.4, weight='bold', va='center'); pn.text(0.09, y - 0.014, b, fontsize=6.4, va='center', color='#444'); y -= 0.049
y -= 0.012; pn.text(0, y, 'WHAT IT USES', fontsize=8.8, weight='bold', color='#1e3a2b'); y -= 0.008; pn.plot([0, 1], [y, y], color='#1e3a2b', lw=0.6); y -= 0.026
tot = sum(p['area'] for p in info)
for t_ in ['Only land that was already green, and the', 'road verges. No plot gets smaller.', f'Plots stay at {len(info)}, {tot:,.0f} sq ft ({tot / SQFT / NA * 100:.1f}%).',
           f'Walking track along the stream: about {sum(t.length for t in track):,.0f} m.', 'Streets stay 9 m: 6 m carriageway and a', '1.5 m planted verge each side.',
           'The Avenue stays 12 m: 7 m carriageway', 'and a 2.5 m tree verge each side.', 'Paver tables at junctions slow the traffic.']:
    pn.text(0, y, t_, fontsize=6.8, va='center'); y -= 0.0205
bd = fig.add_axes([0.012, 0.018, 0.755, 0.245]); bd.axis('off'); bd.set_xlim(0, 3); bd.set_ylim(0, 1)
SW = [('#ee8f5a', 'Avenue: flowering trees in two colours', 'for example gulmohar and amaltas'), ('#3c7340', 'Stream edge: tall riverside trees', 'for example arjun and jamun'),
      ('#b7a0dc', 'Park edge: small flowering trees', 'for example kachnar or jacaranda'), ('#e79ab3', 'Lawns: accent trees', 'for example pink cassia'),
      ('#5f9c48', 'Streets: compact shade trees', 'one per plot line, clear of gates'), ('#4a8a3c', 'East grove: fruit trees', 'for example mango, on a 6.5 m grid'),
      ('#f6f1e4', 'Clubhouse: scented trees', 'for example champa by the pool')]
bd.text(0.02, 0.95, 'PLANTING', fontsize=8.6, weight='bold', color='#1e3a2b', va='top'); bd.plot([0.02, 1.9], [0.87, 0.87], color='#1e3a2b', lw=0.6)
for i, (c_, a, b) in enumerate(SW):
    cx_ = 0.045 + (i % 2) * 0.96; cy_ = 0.76 - (i // 2) * 0.205
    bd.plot(cx_, cy_, marker='o', ms=14, mfc=c_, mec='#2f5a2a', mew=0.5, clip_on=False)
    bd.text(cx_ + 0.05, cy_ + 0.04, a, fontsize=7.0, weight='bold', va='center'); bd.text(cx_ + 0.05, cy_ - 0.05, b, fontsize=6.5, va='center', color='#444')
bd.text(2.02, 0.95, 'BEFORE THIS IS BUILT', fontsize=8.6, weight='bold', color='#1e3a2b', va='top'); bd.plot([2.02, 2.95], [0.87, 0.87], color='#1e3a2b', lw=0.6)
for i, t_ in enumerate(['This is a concept drawing, not a planting', 'plan. Species are suggestions for a', 'landscape designer to confirm for the soil',
                        'and water on site.', 'Nothing is built inside the 9 m strip along', 'the stream: only the track, seats and trees.',
                        'Tree positions on streets move to suit', 'each plot gate.']):
    bd.text(2.02, 0.77 - i * 0.092, t_, fontsize=6.8, va='center')
