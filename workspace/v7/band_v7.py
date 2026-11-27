# bottom band of sheet 1: the same plan read three ways (runs inside render_v7.py)
from collections import Counter
bd = fig.add_axes([0.012, 0.018, 0.72, 0.30]); bd.axis('off'); bd.set_xlim(0, 3); bd.set_ylim(0, 1)
NW_ = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', 6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten'}; nsp_ = sum(1 for p in info if p.get('special')); ncross_ = sum(1 for p in info if 'cross' in p['shape'])
cc_ = Counter(p['cls'] for p in info); nN = sum(1 for p in info if p['front'] == 'lo'); nS = len(info) - nN
nstream = sum(1 for p in info if 'stream-facing' in p['tags']); npark = sum(1 for p in info if 'park-facing' in p['tags'] or 'park-side' in p['tags'])
ngard = sum(1 for p in info if 'beside the stream lawn' in p['tags'] or 'garden-side' in p['tags']); ncor = sum(1 for p in info if p['corner'])
nT = sum(1 for p in info if any('T-junction' in c for c in p['cautions'])); nsv = sum(1 for p in info if any('services' in c for c in p['cautions']))
cols = [('READ AS THE SELLER', [
            f"{len(info)} plots, {tot:,.0f} sq ft to sell ({tot / SQFT / NA * 100:.0f}% of the land).", ("   The previous sheet (v6) had 54 plots, 210,930 sq ft." if not TAG else "   The previous sheet (v7) had 75 plots, 248,023 sq ft."),
            f"Sizes step up like a price list: {cc_['3,000-3,200']} plots of 3,000–3,200 sq ft,", f"   {cc_['3,200-3,500']} of 3,200–3,500 and {cc_['3,500-4,000']} of 3,500–4,000" + (f", {cc_['4,000+']} over 4,000." if cc_['4,000+'] else "."),
            f"Premium stock: {nstream} stream-facing, {npark} on the Central Park,", f"   {ngard} beside a garden or the stream lawn, {ncor} corners.",
            f"{V['road_len']:,.0f} m of road for {len(info)} plots ({V['road_len'] / len(info):.0f} m a plot); every street", "   except Stream Drive sells on both sides.",
            "Launch from Third Street, next to the gate; hold Stream Drive", "   for the best price.", "Clubhouse at the gate can be the sales office from day one."]),
        ('READ AS THE BUYER', [
            "The plot is a true rectangle, 40–50 ft wide and 75 ft deep.", f"   {NW_[ncross_]} corner plots on Cross Street have one side 6° off square.",
            "Every plot opens onto a 9 m street; side and back walls are", "   shared with neighbours, no leftover strips between plots.",
            ] + ([f"{NW_[nsp_]} larger plots take in leftover corners, so their backs", "   are irregular (sizes are in the plot guide)."] if nsp_ else []) + [
            f"A park, garden or the stream promenade is within {max(p['park_m'] for p in info):.0f} m", "   of every plot.",
            f"{nN} plots face north and {nS} face south (marked by colour).", "One gate, loop streets, three short closes: no through traffic.",
            f"Marked plainly in the schedule: {nT} plot{'s' if nT != 1 else ''} look{'s' if nT == 1 else ''} down a T-junction,", f"   {nsv} back onto the services yard."]),
        ('READ AS THE ARCHITECT / ENGINEER', [
            "Two straight grids follow the two reaches of the stream and", "   meet on Cross Street. Blocks are all 150 ft deep, so rear walls,",
            "   drains and service lines run in straight lines.",
            "Stream Drive keeps the 9 m no-build strip public, as a", "   promenade, instead of hiding it behind back walls.",
            "The Avenue (12 m) runs gate, Central Park, viewing deck.", "Junctions at right angles, 4.5 m kerb radii, turning circles",
            "   at the two longer closes.",
            ] + (["The odd corners left by the stream bank are the gardens,", "   so no plot is forced into an odd shape."] if not nsp_ else
                 ["Leftover corners in the north-east and beside the clubhouse", "   are now part of larger plots; the stream-bank corners stay", "   as the gardens."]) + [
            "Still needed on site: levels and high-water survey (drain", "   falls, STP position) before the T&CP submission drawing."])]
for i, (h, items) in enumerate(cols):
    x0 = i + 0.02
    bd.text(x0, 0.965, h, fontsize=8.6, weight='bold', color='#1e3a2b', va='top')
    bd.plot([x0, i + 0.94], [0.905, 0.905], color='#1e3a2b', lw=0.6)
    yy = 0.855
    for t_ in items:
        cont = t_.startswith('   ')
        if not cont: bd.add_patch(plt.Circle((x0 + 0.012, yy + 0.004), 0.0045, color='#b3261e', transform=bd.transData, clip_on=False))
        bd.text(x0 + 0.035, yy, t_.strip(), fontsize=6.9, va='center', color='#222'); yy -= 0.066
