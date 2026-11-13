"""Maheshwar Greens: the 6-page consumer brochure (A4 portrait), built only from the final image set
(brochure/brochure_images.zip @ e834f9c). Writes brochure.html next to this script.
Inputs in the same folder: img/ (crops from prep_images.py), plan_consumer.svg, fonts.css + fonts/."""
import json, os, re, sys
D = os.path.dirname(os.path.abspath(__file__)) + '/'
S = json.load(open(D + 'stats.json'))
I = {
 'gate': '<path d="M4 21V9M20 21V9M4 9a8 8 0 0 1 16 0M8 21v-7M12 21v-9M16 21v-7"/>',
 'road': '<path d="M8 3 5 21M16 3l3 18M12 4v3M12 10v3M12 16v3"/>',
 'tree': '<circle cx="12" cy="9" r="6"/><path d="M12 15v6M9 21h6"/>',
 'leaf': '<path d="M5 19C5 10 11 5 20 4c-1 9-6 15-15 15ZM5 19l7-7"/>',
 'drop': '<path d="M12 3s6 7 6 11a6 6 0 0 1-12 0c0-4 6-11 6-11Z"/>',
 'cycle': '<path d="M20 7a8 8 0 0 0-14.5 2M4 17a8 8 0 0 0 14.5-2M20 3v4h-4M4 21v-4h4"/>',
 'bolt': '<path d="M13 2 4 14h7l-1 8 9-12h-7l1-8Z"/>',
 'walk': '<circle cx="13" cy="4.5" r="2"/><path d="M13 7.5 11 14l-3 7M11 14l4 3 1 4M8 11l3-3.5 3 2.5 3 1"/>',
 'fort': '<path d="M3 21V9h3V6h3v3h2V5h2v4h2V6h3v3h3v12ZM10 21v-5h4v5"/>',
 'loom': '<path d="M4 6h16M4 12h16M4 18h16M8 4v16M16 4v16"/>',
 'film': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 9h18M3 15h18M7 5v4M12 5v4M17 5v4M7 15v4M12 15v4M17 15v4"/>',
 'museum': '<path d="M3 21h18M5 21V11M19 21V11M9.7 21V11M14.3 21V11M2 11l10-6 10 6Z"/>',
 'waves': '<path d="M3 8c3 0 3 2 6 2s3-2 6-2 3 2 6 2M3 14c3 0 3 2 6 2s3-2 6-2 3 2 6 2"/>',
 'shield': '<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6l-8-3Z"/>',
 'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
 'flame': '<path d="M12 22c4 0 7-3 7-7 0-5-4-7-5-12-2 2-3 4-3 6-1-1-2-2-2-4-2 2-4 5-4 10 0 4 3 7 7 7Z"/>',
 'bag': '<path d="M5 8h14l-1 13H6L5 8ZM9 8V6a3 3 0 0 1 6 0v2"/>',
 'plane': '<path d="M2 16l20-6-20-6 4 6-4 6ZM6 10h8"/>',
 'temple': '<path d="M12 2.5 15 9H9l3-6.5ZM8 9h8v3.5H8ZM5.5 12.5h13V21h-13ZM10 21v-4.5h4V21M3 21h18"/>'}
def ic(n): return f'<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{I[n]}</svg>'
AI = '<div class="ai">AI-generated concept visualisation</div>'
def fig(src, w, h, extra='', ai=True, radius=True):
    return f'<div class="fig{"" if radius else " sq"}" style="width:{w}mm;height:{h}mm;{extra}"><img src="img/{src}">{AI if ai else ""}</div>'
plan = open(D + 'plan_consumer.svg').read()
plan = re.sub(r'width="\d+" height="\d+"', 'preserveAspectRatio="xMidYMid meet" style="width:100%;height:100%;display:block"', plan, count=1)
fonts = open(D + 'fonts.css').read()
r = lambda v, n=-2: f'{round(v, n):,.0f}'

CSS = r"""
@page { size: 210mm 297mm; margin: 0 }
:root { --g9:#10241a; --g8:#163222; --g7:#1e3a2b; --g5:#3f6b3a; --iv:#fbf7ef; --s1:#f3ead9; --s2:#e6d9bf;
        --sf:#c46a2b; --sf2:#e7a56b; --ink:#22313f; --mu:#5d6b64; }
* { box-sizing: border-box; margin: 0; padding: 0 }
html, body { background: #d9d6cf }
body { font-family: Inter, sans-serif; color: var(--ink); -webkit-font-smoothing: antialiased; }
.page { width: 210mm; height: 297mm; position: relative; overflow: hidden; background: var(--iv); break-after: page; page-break-after: always }
.abs { position: absolute }
.eyebrow { font-size: 7.4pt; font-weight: 600; letter-spacing: .24em; text-transform: uppercase; color: var(--sf); line-height: 1 }
h2 { font-family: 'Cormorant Garamond', serif; font-weight: 700; font-size: 30pt; line-height: 1.0; color: var(--g7); margin: 3.2mm 0 4.2mm; letter-spacing: -.005em }
h3 { font-family: 'Cormorant Garamond', serif; font-weight: 700; font-size: 17pt; line-height: 1.05; color: var(--g7) }
.lead { font-size: 9.8pt; line-height: 1.62; color: #3a4943 }
p { font-size: 8.8pt; line-height: 1.55; color: #3a4943 }
.ic { width: 5.6mm; height: 5.6mm; flex: none; color: var(--sf) }
.fig { position: relative; overflow: hidden; border-radius: 1.6mm; background: #ccc; flex: none }
.fig.sq { border-radius: 0 }
.fig img { display: block; width: 100%; height: 100%; object-fit: cover; object-position: 100% 100% }
.ai { position: absolute; left: 2.6mm; top: 2.6mm; background: rgba(16,36,26,.62); color: #f3ead9; font-size: 5.6pt; font-weight: 500;
      letter-spacing: .04em; padding: 1.2mm 2.2mm; border-radius: 5mm; line-height: 1 }
.cap { font-size: 7.4pt; line-height: 1.45; color: var(--mu); margin-top: 2.2mm }
.cap b { color: var(--g7); font-weight: 600 }
.pg { position: absolute; bottom: 8mm; right: 14mm; font-size: 6.8pt; letter-spacing: .16em; color: #9aa39d }
.run { position: absolute; bottom: 8mm; left: 14mm; font-size: 6.8pt; letter-spacing: .16em; text-transform: uppercase; color: #9aa39d }
.item { display: flex; gap: 2.8mm; align-items: flex-start }
.item b { display: block; font-size: 9.2pt; color: var(--g7); margin-bottom: .8mm; font-weight: 600 }
.item span { display: block; font-size: 8.1pt; color: var(--mu); line-height: 1.45 }
/* cover */
.cover .bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 100% 100% }
.cover .shade-top { position: absolute; left: 0; right: 0; top: 0; height: 132mm;
   background: linear-gradient(to bottom, rgba(9,22,14,.90) 0%, rgba(9,22,14,.74) 40%, rgba(9,22,14,.34) 70%, rgba(9,22,14,0) 100%) }
.cover .shade-bot { position: absolute; left: 0; right: 0; bottom: 0; height: 78mm;
   background: linear-gradient(to top, rgba(9,22,14,.88) 0%, rgba(9,22,14,.55) 45%, rgba(9,22,14,0) 100%);
   -webkit-mask-image: linear-gradient(to right, #000 0%, #000 52%, transparent 80%); mask-image: linear-gradient(to right, #000 0%, #000 52%, transparent 80%) }
.cover .ai { left: auto; right: 6mm; top: 6mm }
.cover .mast { position: absolute; left: 16mm; right: 16mm; top: 19mm; color: #fbf7ef }
.cover .eyebrow { color: var(--sf2) }
.cover h1 { font-family: 'Cormorant Garamond', serif; font-weight: 600; font-size: 64pt; line-height: .88; margin: 5mm 0 5.5mm; letter-spacing: .004em; text-shadow: 0 .4mm 2.4mm rgba(0,0,0,.35) }
.cover .tag { font-size: 12.2pt; line-height: 1.5; font-weight: 400; color: #f6eedf; max-width: 122mm; text-shadow: 0 .3mm 1.6mm rgba(0,0,0,.6) }
.cover .facts { position: absolute; left: 16mm; bottom: 21mm; display: flex; gap: 8mm }
.cover .facts div { border-top: 1px solid rgba(251,247,239,.5); padding-top: 2.8mm; width: 33mm }
.cover .facts b { display: block; font-family: 'Cormorant Garamond', serif; font-weight: 700; font-size: 22pt; color: #fbf7ef; line-height: 1 }
.cover .facts span { display: block; font-size: 7.6pt; letter-spacing: .05em; color: #e6dac2; margin-top: 1.4mm }
.cover .legal { position: absolute; left: 16mm; bottom: 9mm; font-size: 6.4pt; letter-spacing: .14em; text-transform: uppercase; color: #d5c9b1 }
/* page 2 */
.p2 .quote { font-family: 'Cormorant Garamond', serif; font-style: italic; font-weight: 500; font-size: 15pt; line-height: 1.3; color: var(--g5);
             border-left: 2px solid var(--sf2); padding-left: 4mm; margin-top: 6mm }
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6mm 7mm }
.band { position: absolute; left: 0; right: 0; bottom: 0; background: var(--g9); color: #efe5d2; padding: 11mm 14mm 0 }
.band .eyebrow { color: var(--sf2) }
.band h3 { color: #fbf7ef; font-size: 21pt; margin: 2.6mm 0 5.5mm }
.band .grid3 .item b { color: #fbf7ef }
.band .grid3 .item span { color: #cdbfa5 }
.band .ic { color: var(--sf2) }
.band .pg { color: #8d9a8f }
/* page 3 */
.journey { margin-top: 7mm; position: relative }
.journey .stop { display: flex; gap: 4mm; align-items: flex-start; position: relative }
.journey .dot { width: 4.4mm; height: 4.4mm; border-radius: 50%; background: var(--iv); border: 1.4mm solid var(--g5); flex: none; margin-top: .5mm; position: relative; z-index: 2 }
.journey .end .dot { width: 6.2mm; height: 6.2mm; border: 1.9mm solid var(--sf); margin-left: -.9mm; margin-top: -.3mm }
.journey .stop b { display: block; font-family: 'Cormorant Garamond', serif; font-weight: 700; font-size: 17pt; color: var(--g7); line-height: 1 }
.journey .stop span { display: block; font-size: 8.2pt; color: var(--mu); margin-top: 1.2mm; line-height: 1.4 }
.journey .tagk { font-size: 6.4pt; font-weight: 600; letter-spacing: .18em; text-transform: uppercase; color: var(--sf); margin-left: auto; padding-top: 1.4mm }
.journey .leg { margin-left: 2.2mm; border-left: 1.2mm dotted #a9b8a2; padding: 4.6mm 0 4.6mm 5.6mm; font-size: 7.8pt; color: #6f7c75; letter-spacing: .02em }
.journey .leg i { font-style: normal; display: inline-block; background: var(--s1); border-radius: 4mm; padding: 1.2mm 2.6mm; color: #55625b }
.stat { display: flex; gap: 6mm; margin-top: 6mm }
.stat div { flex: 1; border-top: 1px solid var(--s2); padding-top: 2.6mm }
.stat b { display: block; font-family: 'Cormorant Garamond', serif; font-weight: 700; font-size: 25pt; color: var(--g7); line-height: 1 }
.stat span { display: block; font-size: 7.6pt; color: var(--mu); margin-top: 1.2mm; letter-spacing: .04em }
.nearband { position: absolute; left: 0; right: 0; bottom: 0; height: 104mm; background: var(--s1); padding: 12mm 14mm 0 }
.nearband .run, .nearband .pg { bottom: 8mm }
.near { display: grid; grid-template-columns: repeat(5, 1fr); gap: 0 }
.near > div { padding: 0 3.6mm 0 0 }
.near > div + div { padding-left: 3.6mm; border-left: 1px solid #ddd0b4 }
.near .ic { display: block; width: 6.4mm; height: 6.4mm; margin-bottom: 3mm }
.near b { display: block; font-size: 8.6pt; color: var(--g7); font-weight: 600; line-height: 1.25 }
.near em { display: block; font-style: normal; font-family: 'Cormorant Garamond', serif; font-weight: 700; font-size: 16pt; color: var(--sf); margin-top: 1.8mm; line-height: 1 }
.near em small { display: block; font-family: Inter, sans-serif; font-size: 6.2pt; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: #a08b6a; margin-bottom: .8mm }
.near span { display: block; font-size: 7.3pt; color: var(--mu); margin-top: 1.6mm; line-height: 1.38 }
.small { font-size: 6.6pt; line-height: 1.5; color: #8a948e }
/* page 4 */
.planbox { background: #f4f1e8; border-radius: 1.6mm; overflow: hidden; box-shadow: 0 .6mm 2.4mm rgba(0,0,0,.08) }
.legend { display: grid; grid-template-columns: repeat(4, auto); justify-content: space-between; gap: 2.6mm 4mm; font-size: 7.8pt; color: #34433d }
.legend div { display: flex; gap: 2mm; align-items: center; white-space: nowrap }
.legend i { width: 5mm; height: 3.4mm; border-radius: .8mm; flex: none }
.legend u { text-decoration: none; width: 4.6mm; height: 4.6mm; border-radius: 50%; background: var(--g7); color: #fff; font-size: 6.6pt; font-weight: 700;
            display: flex; align-items: center; justify-content: center; flex: none; border: .5mm solid #fff; box-shadow: 0 0 0 .25mm var(--g7) }
.grid4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5mm 5.5mm }
.grid4 .item b { font-size: 8.8pt }
.grid4 .item span { font-size: 7.7pt }
/* page 5 */
.note { margin-top: 5mm; background: var(--s1); border-radius: 1.6mm; padding: 3.6mm 4mm; font-size: 7.9pt; line-height: 1.5; color: #4b5852 }
.note b { color: var(--g7) }
/* page 6 */
.card { background: #fff; border-radius: 1.6mm; padding: 5mm 5mm 4.6mm; box-shadow: 0 .6mm 2.4mm rgba(0,0,0,.07) }
.card .n { font-size: 7.2pt; letter-spacing: .14em; text-transform: uppercase; color: var(--sf); font-weight: 600; margin: 2mm 0 2.4mm }
.contact { position: absolute; left: 0; right: 0; bottom: 0; height: 66mm; background: var(--g9); color: #efe5d2; padding: 9mm 14mm 0 }
.contact h3 { color: #fbf7ef; font-size: 23pt }
.contact .row { display: grid; grid-template-columns: 1.1fr 1.2fr 1fr; gap: 6mm; margin-top: 5mm }
.contact .row div { border-top: 1px solid rgba(243,234,217,.3); padding-top: 2.8mm; font-size: 8.4pt; color: #dccfb6; line-height: 1.5 }
.contact .row b { display: block; font-size: 6.8pt; letter-spacing: .16em; text-transform: uppercase; color: var(--sf2); margin-bottom: 1.4mm; font-weight: 600 }
.contact .fill { display: inline-block; width: 44mm; border-bottom: 1px solid rgba(243,234,217,.6); height: 4.4mm }
.contact .disc { position: absolute; left: 14mm; right: 14mm; bottom: 8mm; font-size: 6.1pt; line-height: 1.5; color: #9f9784 }
"""

html = f'''<!doctype html><html><head><meta charset="utf-8"><title>Maheshwar Greens</title><style>{fonts}{CSS}</style></head><body>

<section class="page cover">
  <img class="bg" src="img/p1_cover.jpg">
  <div class="shade-top"></div><div class="shade-bot"></div>
  {AI}
  <div class="mast">
    <div class="eyebrow">Jalkoti &middot; Maheshwar &middot; Madhya Pradesh</div>
    <h1>Maheshwar<br>Greens</h1>
    <p class="tag">Farmhouse plots beside a quiet stream, a short drive from the ghats of Maheshwar.</p>
  </div>
  <div class="facts">
    <div><b>{S["plots"]}</b><span>farmhouse plots</span></div>
    <div><b>{S["garden_ac"]:.1f} acres</b><span>streamside garden</span></div>
    <div><b>2 hours</b><span>from Indore</span></div>
  </div>
  <div class="legal">Proposed plotted development &middot; MP RERA Reg. No. ________________</div>
</section>

<section class="page p2">
  <div class="abs" style="left:0;top:0">{fig("p2_ghats.jpg", 116, 155.36, radius=False)}</div>
  <div class="abs" style="left:126mm;right:14mm;top:19mm">
    <div class="eyebrow">The town</div>
    <h2 style="font-size:27pt">Maheshwar, the heritage town on the Narmada</h2>
    <p class="lead">Maheshwar sits on the north bank of the Narmada. It was the capital of Rani Ahilyabai Holkar, who ruled from 1767 to 1795. Her fort, temples and ghats still shape the town today.</p>
    <p class="quote">Stone steps down to the water, the evening aarti, boats at sunrise. A town where the river still sets the pace of the day.</p>
  </div>
  <div class="abs eyebrow" style="left:14mm;top:167mm">What makes Maheshwar special</div>
  <div class="abs grid3" style="left:14mm;right:14mm;top:176mm;row-gap:8mm">
    <div class="item">{ic("fort")}<p><b>Ahilya Fort and the ghats</b><span>Sandstone ghats, temples and the old fort, right on the river.</span></p></div>
    <div class="item">{ic("loom")}<p><b>Maheshwari handloom</b><span>The town&rsquo;s famous sarees are still woven on its looms.</span></p></div>
    <div class="item">{ic("film")}<p><b>A favourite film location</b><span><i>Bajirao Mastani</i>, <i>Pad Man</i> and <i>Dabangg 3</i> were shot here.</span></p></div>
    <div class="item">{ic("waves")}<p><b>Sahastradhara, in Jalkoti</b><span>The Narmada&rsquo;s &ldquo;thousand streams&rdquo; over a rocky bed.</span></p></div>
    <div class="item">{ic("museum")}<p><b>Ahilya Lok</b><span>A heritage project planned by MP Tourism on the Narmada bank.</span></p></div>
    <div class="item">{ic("tree")}<p><b>Nimar countryside</b><span>Open fields, big skies and a slower pace of life.</span></p></div>
  </div>
  <div class="band" style="height:62mm">
    <div class="eyebrow">Weekends here</div>
    <h3>A weekend in Maheshwar</h3>
    <div class="grid3">
      <div class="item">{ic("sun")}<p><b>Sunrise on the Narmada</b><span>Take a boat out from the ghats as the mist lifts.</span></p></div>
      <div class="item">{ic("flame")}<p><b>The evening aarti</b><span>Lamps on the water and bells from the temples.</span></p></div>
      <div class="item">{ic("bag")}<p><b>The old town</b><span>Handloom sarees, local food and quiet old lanes.</span></p></div>
    </div>
    <div class="pg">02</div>
  </div>
</section>

<section class="page p3">
  <div class="abs" style="left:14mm;top:19mm;width:96mm">
    <div class="eyebrow">Location</div>
    <h2>About two hours from Indore</h2>
    <p class="lead">Maheshwar Greens is at Jalkoti, just west of Maheshwar town. From Indore it is an easy drive south-west on the Agra&ndash;Mumbai highway to Dhamnod, and on to Maheshwar.</p>
    <div class="journey">
      <div class="stop"><div class="dot"></div><div><b>Indore</b><span>City, airport and railway station</span></div><div class="tagk">Start</div></div>
      <div class="leg"><i>NH-52 &middot; Agra&ndash;Mumbai highway</i></div>
      <div class="stop"><div class="dot"></div><div><b>Dhamnod</b><span>Leave the highway for Maheshwar</span></div></div>
      <div class="leg"><i>about 13 km to Maheshwar</i></div>
      <div class="stop end"><div class="dot"></div><div><b>Maheshwar Greens</b><span>Jalkoti, about 4 km west of Ahilya Fort*</span></div><div class="tagk">Arrive</div></div>
    </div>
  </div>
  <div class="abs" style="right:14mm;top:19mm;width:80mm">
    {fig("p3_entrance.jpg", 80, 107.14)}
    <p class="cap"><b>Arrival.</b> The entrance gateway, as planned.</p>
    <div class="stat"><div><b>95 km</b><span>approx., by road</span></div><div><b>2 hours</b><span>approx., by car</span></div></div>
  </div>
  <div class="nearband">
    <div class="eyebrow">Around Maheshwar Greens</div>
    <h3 style="margin:2.6mm 0 6mm">Day trips and weekend outings</h3>
    <div class="near">
      <div>{ic("fort")}<b>Ahilya Fort &amp; ghats</b><em><small>about</small>4 km*</em><span>Maheshwar&rsquo;s riverfront, temples and markets</span></div>
      <div>{ic("waves")}<b>Sahastradhara</b><em><small>&nbsp;</small>in Jalkoti</em><span>The Narmada&rsquo;s &ldquo;thousand streams&rdquo;</span></div>
      <div>{ic("museum")}<b>Mandu</b><em><small>about</small>1&frac14; hours</em><span>Hilltop fort city of the Malwa sultans</span></div>
      <div>{ic("temple")}<b>Omkareshwar</b><em><small>about</small>65 km</em><span>Jyotirlinga temple on a Narmada island</span></div>
      <div>{ic("plane")}<b>Indore airport</b><em><small>about</small>2 hours</em><span>Devi Ahilyabai Holkar International Airport</span></div>
    </div>
    <p class="small" style="margin-top:6mm">Distances and times are approximate and depend on the route and traffic. *Straight-line distance.</p>
    <div class="run">Maheshwar Greens</div><div class="pg">03</div>
  </div>
</section>

<section class="page p4">
  <div class="abs" style="left:14mm;right:14mm;top:17mm">
    <div class="eyebrow">The plan</div>
    <h2>A gated community, planned around gardens</h2>
    <p class="lead" style="max-width:168mm">{S["plots"]} plots on about {S["colony_ac"]:.1f} acres, with a single gated entry. A landscaped garden runs the length of the stream, and three garden boulevards carry the green into the heart of the community.</p>
  </div>
  <div class="abs planbox" style="left:14mm;top:63mm;width:182mm;height:149.7mm">{plan}</div>
  <div class="abs legend" style="left:15mm;right:15mm;top:216.5mm">
    <div><i style="background:#7fb446"></i>Streamside garden</div>
    <div><i style="background:#f3d8ab;border:.3mm solid #a5854f"></i>Streamside plots ({S["nR"]})</div>
    <div><i style="background:#fcf1d6;border:.3mm solid #a5854f"></i>Garden plots ({S["nV"]})</div>
    <div><i style="background:#2f7d33"></i>Garden boulevards</div>
    <div><i style="background:#a3a3a3"></i>40 ft roads</div>
    <div><u>1</u>Gated entry</div>
    <div><u>2</u>Walkway to the garden</div>
    <div><u>3</u>Services</div>
  </div>
  <div class="abs grid4" style="left:14mm;right:14mm;top:233mm">
    <div class="item">{ic("shield")}<p><b>Gated, one entry</b><span>A single gate on its own entrance road.</span></p></div>
    <div class="item">{ic("road")}<p><b>40 ft roads</b><span>Paver-block roads, lined with trees.</span></p></div>
    <div class="item">{ic("tree")}<p><b>Garden boulevards</b><span>Three streets with a planted median.</span></p></div>
    <div class="item">{ic("leaf")}<p><b>Streamside garden</b><span>About {S["garden_ac"]:.1f} acres, open to all residents.</span></p></div>
    <div class="item">{ic("drop")}<p><b>Water supply</b><span>Overhead tank and tubewell (planned).</span></p></div>
    <div class="item">{ic("cycle")}<p><b>Sewage treatment</b><span>A treatment plant for the colony (planned).</span></p></div>
    <div class="item">{ic("bolt")}<p><b>Power</b><span>Electricity to every plot (planned).</span></p></div>
    <div class="item">{ic("walk")}<p><b>Walk to the garden</b><span>A footpath from the road to the garden.</span></p></div>
  </div>
  <p class="abs small" style="left:14mm;right:40mm;bottom:8mm">Indicative plan drawn from the land survey; stream position &copy; OpenStreetMap contributors. Layout and amenities are proposed and subject to approval.</p>
  <div class="pg">04</div>
</section>

<section class="page p5">
  <div class="abs" style="left:14mm;right:14mm;top:17mm">
    <div class="eyebrow">Green living</div>
    <h2>Green on every street</h2>
    <p class="lead" style="max-width:170mm">Every plot is a short walk from the garden. A landscaped garden runs along the stream, and three boulevards have a planted median down the middle.</p>
  </div>
  <div class="abs" style="left:14mm;top:56mm">{fig("p5_garden.jpg", 92, 92)}</div>
  <div class="abs" style="left:114mm;right:14mm;top:58mm">
    <div class="eyebrow">The streamside garden</div>
    <h3 style="margin:2.6mm 0 3.4mm">A garden the length of the stream</h3>
    <p>About {S["garden_ac"]:.1f} acres of lawns and trees along a seasonal stream on the north-west edge, open to every resident. The streamside plots back straight onto it.</p>
    <div class="note"><b>Proposed:</b> a low check dam to hold a pool of water through the dry months, subject to approval. The picture shows this proposal, not the stream today.</div>
    <div style="display:flex;flex-direction:column;gap:4mm;margin-top:6mm">
      <div class="item">{ic("walk")}<p><b>Walk in from the road</b><span>A walkway leads from the road into the garden.</span></p></div>
      <div class="item">{ic("tree")}<p><b>Lawns and native trees</b><span>Open green space to walk, sit and watch the water.</span></p></div>
    </div>
  </div>
  <div class="abs" style="left:14mm;top:155mm;width:88mm">{fig("p5_boulevard.jpg", 88, 110)}<p class="cap"><b>Garden boulevard at dusk.</b> Two lanes either side of a planted median.</p></div>
  <div class="abs" style="left:108mm;top:155mm;width:88mm">{fig("p5_boulevard_walk.jpg", 88, 110)}<p class="cap"><b>The median as a walking garden.</b> A path, benches and flower beds between the lanes.</p></div>
  <div class="run">Maheshwar Greens</div><div class="pg">05</div>
</section>

<section class="page p6">
  <div class="abs" style="left:14mm;right:14mm;top:17mm">
    <div class="eyebrow">The plots</div>
    <h2>Build your weekend farmhouse</h2>
    <p class="lead" style="max-width:170mm">Buy a plot and build a cottage in your own time, to your own design, within the approved rules.</p>
  </div>
  <div class="abs" style="left:14mm;top:54mm;width:92mm">{fig("p6_villa.jpg", 92, 92)}<p class="cap"><b>A single-storey cottage</b> on a 45 &times; 90 ft plot.</p></div>
  <div class="abs" style="left:113mm;right:14mm;top:54mm;display:flex;flex-direction:column;gap:5mm">
    <div class="card"><h3>Streamside plots</h3><div class="n">{S["nR"]} plots &middot; about {r(S["rmin"])} &ndash; {r(S["rmax"])} sq ft</div>
      <p>The largest plots, in a row along the stream. Each backs onto the landscaped garden and fronts a tree-lined road.</p></div>
    <div class="card"><h3>Garden plots</h3><div class="n">{S["nV"]} plots &middot; from about {r(S["vmin"])} sq ft</div>
      <p>{S["n4050"]} are the classic 45 &times; 90 ft (4,050 sq ft). Corner plots go up to about {r(S["vmax"])} sq ft. Many face a garden boulevard.</p></div>
  </div>
  <div class="abs" style="left:14mm;top:158mm">{fig("p6_resort.jpg", 92, 61)}</div>
  <div class="abs" style="left:113mm;right:14mm;top:160mm">
    <div class="eyebrow">Next door</div>
    <h3 style="margin:2.6mm 0 3mm">A planned resort</h3>
    <p>The front of the estate, by the main entry, is planned as a boutique resort with cottages and lawns. It is a separate project, shown here as a concept.</p>
  </div>
  <div class="contact">
    <h3>Book a site visit</h3>
    <div class="row">
      <div><b>Call or WhatsApp</b><span class="fill"></span></div>
      <div><b>Site</b>Jalkoti, Maheshwar<br>District Khargone, Madhya Pradesh</div>
      <div><b>MP RERA</b>Reg. no. <span class="fill" style="width:30mm"></span></div>
    </div>
    <p class="disc">Pictures marked &ldquo;AI-generated concept visualisation&rdquo; were made with Google Flow. They show the planned character of the project, not the site today. The plan is indicative and drawn from the land survey; stream position &copy; OpenStreetMap contributors. The layout, plot sizes and amenities are proposed and subject to approval by the competent authorities; final sizes are as per the approved layout and the sale deed. The stream is seasonal and the check dam is a proposal. The resort is a separate project. Distances and times are approximate. This brochure is not an offer or a contract.</p>
  </div>
</section>
</body></html>'''
open(D + 'brochure.html', 'w').write(html); print('html written', len(html))
