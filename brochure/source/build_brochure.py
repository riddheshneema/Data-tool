import json, re
import os
D = os.path.dirname(os.path.abspath(__file__)) + '/'
S = json.load(open(D + 'stats.json'))
def svg(fn, cls=''):
    t = open(D + fn).read()
    t = re.sub(r'width="[\d.]+" height="[\d.]+"', 'preserveAspectRatio="xMidYMid slice"' if 'slice' in cls else 'preserveAspectRatio="xMidYMid meet"', t, count=1)
    return t.replace('<svg ', f'<svg class="{cls}" ', 1)
I = {  # 24px stroke icons
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
 'pin': '<path d="M12 21s7-6.5 7-12a7 7 0 0 0-14 0c0 5.5 7 12 7 12Z"/><circle cx="12" cy="9" r="2.5"/>',
 'hwy': '<path d="M5 21 10 3M19 21 14 3M12 6v2M12 11v2M12 16v2"/>',
 'city': '<path d="M3 21h18M5 21V8l5-3v16M10 21V10h5v11M15 21V13h4v8"/>',
 'home': '<path d="M3 11 12 4l9 7M5 10v11h14V10M10 21v-6h4v6"/>',
 'shield': '<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6l-8-3Z"/>'}
def ic(n, c='currentColor'): return f'<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{I[n]}</svg>'
fonts = open(D + 'fonts.css').read().replace('fonts/', D + 'fonts/')
import os
def img(name):
    for ext in ('.png', '.jpg', '.jpeg', '.webp'):
        f = D + 'images/' + name + ext
        if os.path.exists(f): return 'file://' + f
    return None
IMG = {k: img(k) for k in ('01_cover_aerial', '02_maheshwar_ghats', '03_garden_boulevard', '04_streamside_garden', '05_villa')}
AI = '<div class="ai">AI-generated concept visualisation</div>'
cover_media = (f'<img class="photo" src="{IMG["01_cover_aerial"]}">' + AI) if IMG['01_cover_aerial'] else svg('cover_art.svg', 'slice')
band = (f'<div class="band photo-band"><img class="photo" src="{IMG["02_maheshwar_ghats"]}">{AI}</div>') if IMG['02_maheshwar_ghats'] else \
       '<div class="band type-band"><div class="eyebrow" style="color:#e7a56b">Maheshwar · on the Narmada</div><div class="bt">Where history<br>meets the river</div></div>'
pics3 = ''.join(f'<div class="pic"><img class="photo" src="{IMG[k]}">{AI}</div>' for k in ('03_garden_boulevard', '04_streamside_garden') if IMG[k])
villa = (f'<div class="pic wide"><img class="photo" src="{IMG["05_villa"]}">{AI}</div>') if IMG['05_villa'] else ''
garden_plot = '''<svg viewBox="0 0 240 150" class="sk"><rect width="240" height="150" rx="10" fill="#f3ead9"/>
<path d="M0 0H240V46C180 36 120 52 60 40 30 34 10 40 0 44Z" fill="#a8cf8c"/>''' + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for x, y, r, c in [(22,22,9,'#6e9f58'),(54,16,7,'#86b46a'),(88,26,9,'#5f8f4e'),(130,18,8,'#7fae63'),(170,26,9,'#6e9f58'),(210,16,8,'#86b46a')]) + '''
<path d="M70 48 L170 44 L176 118 L64 120 Z" fill="#fbf6ea" stroke="#b78b4e" stroke-width="2"/>
<path d="M0 122H240V150H0Z" fill="#e3dccd"/><text x="120" y="141" text-anchor="middle" font-family="Inter" font-size="10" fill="#6b6b5f">river drive</text>
<text x="120" y="88" text-anchor="middle" font-family="Cormorant Garamond" font-weight="700" font-size="17" fill="#1e3a2b">your plot</text>
<path d="M120 47 L120 30" stroke="#1e3a2b" stroke-width="1.6" stroke-dasharray="3 3"/><rect x="108" y="44" width="24" height="5" fill="#c46a2b"/>
<text x="140" y="36" font-family="Inter" font-size="9.5" fill="#1e3a2b">own garden gate</text>
<text x="18" y="70" font-family="Inter" font-size="10" fill="#3f6b3a">garden</text></svg>'''
villa_plot = '''<svg viewBox="0 0 240 150" class="sk"><rect width="240" height="150" rx="10" fill="#f3ead9"/>
<path d="M0 0H240V150H0Z" fill="#f3ead9"/><rect x="0" y="0" width="34" height="150" fill="#e3dccd"/><rect x="13" y="8" width="8" height="134" rx="3" fill="#7fae63"/>''' + ''.join(f'<circle cx="17" cy="{y}" r="4.2" fill="#5f8f4e"/>' for y in range(18, 140, 16)) + '''
<rect x="52" y="34" width="150" height="72" fill="#fbf6ea" stroke="#b78b4e" stroke-width="2"/>
<rect x="52" y="8" width="150" height="24" fill="none" stroke="#d8c7a5" stroke-width="1.2"/><rect x="52" y="108" width="150" height="24" fill="none" stroke="#d8c7a5" stroke-width="1.2"/>
<text x="127" y="75" text-anchor="middle" font-family="Cormorant Garamond" font-weight="700" font-size="17" fill="#1e3a2b">your plot</text>
<text x="44" y="74" text-anchor="middle" font-family="Inter" font-size="10" fill="#6b6b5f" transform="rotate(-90 44 74)">45 ft</text>
<text x="127" y="122" text-anchor="middle" font-family="Inter" font-size="10" fill="#6b6b5f">90 ft</text>
<text x="17" y="146" text-anchor="middle" font-family="Inter" font-size="8.5" fill="#3f6b3a">boulevard</text></svg>'''
html = f'''<!doctype html><html><head><meta charset="utf-8"><title>Maheshwar Greens – brochure</title><style>
{fonts}
@page {{ size: 210mm 297mm; margin: 0 }}
:root {{ --g9:#14281b; --g7:#1e3a2b; --g5:#3f6b3a; --s0:#fbf7ef; --s1:#f3ead9; --s2:#e9dcc5; --sf:#c46a2b; --ink:#22313f; --mu:#5f6d66; }}
* {{ box-sizing: border-box; margin: 0; padding: 0 }}
html, body {{ background: #ddd; }}
body {{ font-family: Inter, sans-serif; color: var(--ink); -webkit-font-smoothing: antialiased; }}
.page {{ width: 210mm; height: 297mm; position: relative; overflow: hidden; background: var(--s0); page-break-after: always; break-after: page; }}
.serif {{ font-family: 'Cormorant Garamond', serif; }}
.eyebrow {{ font-size: 8.2pt; letter-spacing: .22em; text-transform: uppercase; color: var(--sf); font-weight: 600; }}
h1 {{ font-family: 'Cormorant Garamond', serif; font-weight: 700; }}
h2 {{ font-family: 'Cormorant Garamond', serif; font-weight: 700; font-size: 27pt; line-height: 1.02; color: var(--g7); margin: 2.2mm 0 3.5mm; }}
p.lead {{ font-size: 10.2pt; line-height: 1.55; color: #3b4a44; }}
.ic {{ width: 6mm; height: 6mm; flex: none }}
/* cover */
.cover .art {{ position: absolute; inset: 0 0 auto 0; height: 196mm; }}
.cover .art svg {{ width: 100%; height: 100%; display: block }}
.cover .fade {{ position: absolute; left: 0; right: 0; top: 150mm; height: 48mm; background: linear-gradient(to bottom, rgba(20,40,27,0), rgba(20,40,27,1)); }}
.cover .panel {{ position: absolute; left: 0; right: 0; bottom: 0; height: 101mm; background: var(--g9); color: #f3ead9; padding: 6mm 15mm 0; }}
.cover .chip {{ position: absolute; top: 9mm; left: 12mm; background: rgba(251,247,239,.92); color: var(--g7); font-size: 7.4pt; padding: 1.6mm 3.2mm; border-radius: 10mm; letter-spacing: .04em; }}
.cover .brand {{ font-size: 50pt; line-height: .95; color: #fbf7ef; margin: 3mm 0 4mm; letter-spacing: .005em }}
.cover .tag {{ font-size: 11.4pt; line-height: 1.5; color: #e7dcc6; max-width: 150mm; font-weight: 300 }}
.cover .hl {{ display: flex; gap: 5mm; margin-top: 8mm; }}
.cover .hl div {{ flex: 1; border-top: 1px solid rgba(243,234,217,.35); padding-top: 3.2mm; display: flex; gap: 2.6mm; align-items: flex-start; }}
.cover .hl b {{ display: block; font-family: 'Cormorant Garamond', serif; font-size: 19pt; font-weight: 700; color: #fbf7ef; line-height: 1 }}
.cover .hl span {{ font-size: 8.4pt; color: #cdbf a6; color: #d6c9b0; line-height: 1.35 }}
.cover .ic {{ color: #e7a56b; margin-top: .6mm }}
.cover .foot {{ position: absolute; bottom: 7mm; left: 15mm; right: 15mm; display: flex; justify-content: space-between; font-size: 7pt; color: #a99f8b; letter-spacing: .05em }}
/* page 2 */
.band {{ height: 58mm; overflow: hidden; }}
.band svg {{ width: 100%; height: 100%; display: block }}
.inner {{ padding: 8mm 15mm 0; }}
.grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 3.6mm 7mm; margin-top: 5.5mm; }}
.item {{ display: flex; gap: 3mm; align-items: flex-start; }}
.item .ic {{ color: var(--sf); margin-top: .4mm }}
.item b {{ display: block; font-size: 9.6pt; color: var(--g7); margin-bottom: .6mm }}
.item span {{ font-size: 8.4pt; color: var(--mu); line-height: 1.42 }}
.loc {{ display: grid; grid-template-columns: 112mm 1fr; gap: 6mm; margin-top: 7mm; align-items: start }}
.loc .map svg {{ width: 100%; height: auto; display: block; border-radius: 4mm; box-shadow: 0 1mm 3mm rgba(0,0,0,.08) }}
.loc ul {{ list-style: none; }}
.loc li {{ display: flex; gap: 2.6mm; padding: 2.6mm 0; border-bottom: 1px solid var(--s2); font-size: 8.8pt; line-height: 1.38; color: #34433d }}
.loc li .ic {{ color: var(--g5); width: 5.4mm; height: 5.4mm }}
.loc li b {{ color: var(--g7) }}
.small {{ font-size: 6.8pt; color: #8a948e; line-height: 1.45 }}
/* page 3 */
.plan {{ margin: 4mm 0 0; border-radius: 4mm; overflow: hidden; background: #fff; box-shadow: 0 1mm 3mm rgba(0,0,0,.08); height: 118mm; padding: 2mm }}
.plan svg {{ width: 100%; height: 100%; display: block }}
.key {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 2.2mm 4mm; margin-top: 4mm; }}
.key div {{ display: flex; gap: 2mm; align-items: center; font-size: 8.2pt; color: #34433d; line-height: 1.25 }}
.key i {{ flex: none; width: 5.6mm; height: 5.6mm; border-radius: 50%; background: var(--g7); color: #fff; font-style: normal; font-weight: 700; font-size: 7.6pt; display: flex; align-items: center; justify-content: center }}
.feat {{ display: grid; grid-template-columns: 1fr 1fr; gap: 3.4mm 7mm; margin-top: 7mm; }}
.feat .item b {{ font-size: 9.4pt }}
/* page 4 */
.cards {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; margin-top: 5mm }}
.card {{ background: #fff; border-radius: 4mm; padding: 4.5mm; box-shadow: 0 1mm 3mm rgba(0,0,0,.07) }}
.card .sk {{ width: 100%; height: auto; display: block; border-radius: 2.5mm; margin-bottom: 3.5mm }}
.card h3 {{ font-family: 'Cormorant Garamond', serif; font-size: 18pt; color: var(--g7); line-height: 1 }}
.card .n {{ font-size: 8pt; letter-spacing: .14em; text-transform: uppercase; color: var(--sf); font-weight: 600; margin: 1.6mm 0 2mm }}
.card p {{ font-size: 8.8pt; line-height: 1.5; color: #3b4a44 }}
.why {{ display: grid; grid-template-columns: 1fr 1fr; gap: 3.2mm 7mm; margin-top: 7mm }}
.contact {{ position: absolute; left: 0; right: 0; bottom: 0; height: 76mm; background: var(--g9); color: #f3ead9; padding: 9mm 15mm 0; }}
.contact h3 {{ font-family: 'Cormorant Garamond', serif; font-size: 25pt; color: #fbf7ef; line-height: 1 }}
.contact .row {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5mm; margin-top: 6mm }}
.contact .row div {{ border-top: 1px solid rgba(243,234,217,.3); padding-top: 3mm; font-size: 8.4pt; color: #d6c9b0; line-height: 1.5 }}
.contact .row b {{ display: block; font-size: 7.2pt; letter-spacing: .16em; text-transform: uppercase; color: #e7a56b; margin-bottom: 1.4mm; font-weight: 600 }}
.contact .fill {{ display: inline-block; min-width: 42mm; border-bottom: 1px solid rgba(243,234,217,.6); height: 4.6mm }}
.contact .disc {{ position: absolute; left: 15mm; right: 15mm; bottom: 7mm; font-size: 6.4pt; color: #9f957f; line-height: 1.5 }}
.photo {{ width: 100%; height: 100%; object-fit: cover; display: block }}
.ai {{ position: absolute; right: 3mm; bottom: 3mm; background: rgba(20,40,27,.72); color: #f3ead9; font-size: 6.2pt; padding: 1mm 2.4mm; border-radius: 6mm; letter-spacing: .03em }}
.band {{ position: relative }}
.type-band {{ background: var(--g9); padding: 13mm 15mm 0; background-image: repeating-linear-gradient(165deg, rgba(255,255,255,.035) 0 2px, transparent 2px 14px); }}
.type-band .bt {{ font-family: 'Cormorant Garamond', serif; font-weight: 700; font-size: 34pt; line-height: .98; color: #fbf7ef; margin-top: 3mm }}
.pics {{ display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; margin-top: 4mm }}
.pic {{ position: relative; height: 46mm; border-radius: 4mm; overflow: hidden }}
.pic.wide {{ height: 52mm; margin-top: 5mm }}
.pg {{ position: absolute; bottom: 7mm; right: 15mm; font-size: 7pt; color: #9aa39d; letter-spacing: .08em }}
</style></head><body>

<section class="page cover">
  <div class="art">{cover_media}</div>
  <div class="chip">{"AI-generated concept visualisation" if IMG['01_cover_aerial'] else "Artist's impression of the planned layout"}</div>
  <div class="fade"></div>
  <div class="panel">
    <div class="eyebrow">Jalkoti · Maheshwar · Madhya Pradesh</div>
    <h1 class="brand">Maheshwar Greens</h1>
    <p class="tag">Plots for your home or weekend villa, on a quiet stream bend near the heritage town of Maheshwar.</p>
    <div class="hl">
      <div>{ic('home')}<p><b>{S['plots']} plots</b><span>garden-front and villa plots</span></p></div>
      <div>{ic('road')}<p><b>40 ft roads</b><span>wide, tree-lined, with garden boulevards</span></p></div>
      <div>{ic('leaf')}<p><b>{S['garden_ac']:.1f} acres</b><span>landscaped garden along the stream</span></p></div>
    </div>
    <div class="foot"><span>PROPOSED PLOTTED DEVELOPMENT</span><span>MP RERA REG. NO. ____________</span></div>
  </div>
</section>

<section class="page">
  {band}
  <div class="inner">
    <div class="eyebrow">The town</div>
    <h2>Live in the heritage town of the Narmada</h2>
    <p class="lead">Maheshwar sits on the north bank of the Narmada. It was the capital of Rani Ahilyabai Holkar, who ruled from 1767 to 1795, and her fort, temples and ghats still shape the town today: the steps to the river, the evening aarti, the boats at sunrise.</p>
    <div class="grid2">
      <div class="item">{ic('fort')}<p><b>Ahilya Fort and the ghats</b><span>Sandstone ghats, temples and the old fort on the Narmada.</span></p></div>
      <div class="item">{ic('loom')}<p><b>Maheshwari handloom</b><span>The town's famous sarees are still woven on its looms.</span></p></div>
      <div class="item">{ic('film')}<p><b>A favourite film location</b><span>Bajirao Mastani, Pad Man, Dabangg 3 and Kalank were shot here.</span></p></div>
      <div class="item">{ic('museum')}<p><b>Ahilya Lok is coming</b><span>MP Tourism's ₹110 crore heritage project on the Narmada bank, planned ahead of Simhastha 2028.</span></p></div>
      <div class="item">{ic('waves')}<p><b>Sahastradhara</b><span>The Narmada's "thousand streams" over a rocky bed, in Jalkoti village.</span></p></div>
      <div class="item">{ic('tree')}<p><b>Nimar countryside</b><span>Open fields, big skies and a slower pace, minutes from town.</span></p></div>
    </div>
    <div class="loc">
      <div class="map">{svg('location_map.svg')}</div>
      <div><div class="eyebrow">Getting here</div>
        <ul>
          <li>{ic('fort')}<span><b>About 4 km</b> from Ahilya Fort, as the crow flies</span></li>
          <li>{ic('city')}<span><b>About 90 km</b> from Indore</span></li>
          <li>{ic('hwy')}<span>Maheshwar is <b>13.5 km</b> from NH-52 (Agra–Mumbai highway) at Dhamnod</span></li>
          <li>{ic('pin')}<span>Own approach road off the <b>Jalkoti–Maheshwar road</b></span></li>
        </ul>
        <p class="small" style="margin-top:3mm">Distances are approximate. Driving times vary.</p>
      </div>
    </div>
  </div>
  <div class="pg">02</div>
</section>

<section class="page">
  <div class="inner" style="padding-top:12mm">
    <div class="eyebrow">The community</div>
    <h2>Planned around gardens and wide, tree-lined roads</h2>
    <p class="lead">A gated community of {S['plots']} plots on {S['colony_ac']:.1f} acres. Every road is 40 feet wide. A landscaped garden runs the length of the stream, and garden boulevards bring the green into the heart of the colony.</p>
    <div class="plan">{svg('plan_art.svg', 'meet')}</div>
    {('<div class="pics">' + pics3 + '</div>') if pics3 else ''}
    <div class="key">
      <div><i>1</i>Gated entry</div><div><i>2</i>Streamside garden</div><div><i>3</i>Garden-front plots</div><div><i>4</i>Villa plots</div>
      <div><i>5</i>Garden boulevards</div><div><i>6</i>Walkway to the garden</div><div><i>7</i>Link road</div><div><i>8</i>Water and sewage plant</div>
    </div>
    <div class="feat">
      <div class="item">{ic('shield')}<p><b>Gated, with one entry</b><span>A single gate on a dedicated approach road.</span></p></div>
      <div class="item">{ic('road')}<p><b>40 ft wide roads</b><span>Every road in the colony, lined with avenue trees.</span></p></div>
      <div class="item">{ic('tree')}<p><b>Garden boulevards</b><span>Three streets with a planted median down the middle.</span></p></div>
      <div class="item">{ic('leaf')}<p><b>A {S['garden_ac']:.1f}-acre garden</b><span>Along the stream, open to every resident.</span></p></div>
      <div class="item">{ic('drop')}<p><b>Water supply</b><span>Overhead tank and tubewell for the colony (planned).</span></p></div>
      <div class="item">{ic('cycle')}<p><b>Sewage treatment</b><span>A treatment plant and drainage for the colony (planned).</span></p></div>
      <div class="item">{ic('bolt')}<p><b>Power</b><span>Electricity with a transformer at the gate (planned).</span></p></div>
      <div class="item">{ic('walk')}<p><b>Walk to the garden</b><span>Footpath links from the river drive to the garden.</span></p></div>
    </div>
    <p class="small" style="margin-top:5mm">Artist's impression; not to scale. The layout and amenities are proposed and subject to approval.</p>
  </div>
  <div class="pg">03</div>
</section>

<section class="page">
  <div class="inner" style="padding-top:12mm">
    <div class="eyebrow">The plots</div>
    <h2>Choose your plot</h2>
    <p class="lead">Two kinds of plots, both on 40 ft roads. Buy, and build your own home or weekend villa in your own time.</p>
    <div class="cards">
      <div class="card">{garden_plot}<h3>Garden-front plots</h3><div class="n">{S['nR']} plots · about {round(S['rmin'], -2):,.0f} – {round(S['rmax'], -2):,.0f} sq ft</div>
        <p>The largest plots, in a row along the stream. Each backs straight onto the landscaped garden, with its own garden gate, and fronts the tree-lined river drive.</p></div>
      <div class="card">{villa_plot}<h3>Villa plots</h3><div class="n">{S['nV']} plots · from about {round(S['vmin'], -2):,.0f} sq ft</div>
        <p>Most are the classic 45 × 90 ft (4,050 sq ft). Corner and special plots go up to about {round(S['vmax'], -2):,.0f} sq ft. Many face a garden boulevard.</p></div>
    </div>
    {villa}
    <div class="why">
      <div class="item">{ic('fort')}<p><b>A heritage-town address</b><span>Maheshwar's ghats, fort, temples and markets close by.</span></p></div>
      <div class="item">{ic('leaf')}<p><b>Green and calm</b><span>A stream, a garden and open countryside around you.</span></p></div>
      <div class="item">{ic('road')}<p><b>Planned properly</b><span>Wide roads, gardens and services laid out from day one.</span></p></div>
      <div class="item">{ic('museum')}<p><b>A town on the rise</b><span>New heritage and tourism projects are coming to Maheshwar.</span></p></div>
    </div>
  </div>
  <div class="contact">
    <h3>Book a site visit</h3>
    <div class="row">
      <div><b>Call or WhatsApp</b><span class="fill"></span></div>
      <div><b>Site</b>Jalkoti, Maheshwar<br>District Khargone, Madhya Pradesh</div>
      <div><b>MP RERA</b>Reg. no. <span class="fill" style="min-width:30mm"></span></div>
    </div>
    <p class="disc">Artist's impressions, plans and plot sketches are illustrative and not to scale. The layout, plot sizes and amenities are proposed and subject to approval by the competent authorities; final sizes are as per the approved layout and the sale deed. Distances are approximate. This brochure is not an offer or a contract.</p>
  </div>
</section>
</body></html>'''
open(D + 'brochure.html', 'w').write(html); print('html written', len(html))
