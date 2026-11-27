p = '/tmp/claude-0/-home-user-Data-tool/dbda6b63-1fb5-5cd3-90ba-f6a3071a9612/scratchpad/brochure/build_brochure.py'
s = open(p).read()
if 'def img(name)' not in s:
    s = s.replace("fonts = open(D + 'fonts.css').read().replace('fonts/', D + 'fonts/')",
"""fonts = open(D + 'fonts.css').read().replace('fonts/', D + 'fonts/')
import os
def img(name):
    for ext in ('.png', '.jpg', '.jpeg', '.webp'):
        f = D + 'images/' + name + ext
        if os.path.exists(f): return 'file://' + f
    return None
IMG = {k: img(k) for k in ('01_cover_aerial', '02_maheshwar_ghats', '03_garden_boulevard', '04_streamside_garden', '05_villa')}
AI = '<div class="ai">AI-generated concept visualisation</div>'
cover_media = (f'<img class="photo" src="{IMG["01_cover_aerial"]}">' + AI) if IMG['01_cover_aerial'] else svg('cover_art.svg', 'slice')
band = (f'<div class="band photo-band"><img class="photo" src="{IMG["02_maheshwar_ghats"]}">{AI}</div>') if IMG['02_maheshwar_ghats'] else \\
       '<div class="band type-band"><div class="eyebrow" style="color:#e7a56b">Maheshwar · on the Narmada</div><div class="bt">Where history<br>meets the river</div></div>'
pics3 = ''.join(f'<div class="pic"><img class="photo" src="{IMG[k]}">{AI}</div>' for k in ('03_garden_boulevard', '04_streamside_garden') if IMG[k])
villa = (f'<div class="pic wide"><img class="photo" src="{IMG["05_villa"]}">{AI}</div>') if IMG['05_villa'] else ''""")
    s = s.replace("""  <div class="art">{svg('cover_art.svg', 'slice')}</div>
  <div class="chip">Artist's impression of the planned layout</div>""", """  <div class="art">{cover_media}</div>
  <div class="chip">{"AI-generated concept visualisation" if IMG['01_cover_aerial'] else "Artist's impression of the planned layout"}</div>""")
    s = s.replace("""  <div class="band">{svg('heritage.svg', 'slice')}</div>""", """  {band}""")
    s = s.replace("""    <div class="plan">{svg('plan_art.svg', 'slice')}</div>""", """    <div class="plan">{svg('plan_art.svg', 'slice')}</div>
    {('<div class="pics">' + pics3 + '</div>') if pics3 else ''}""")
    s = s.replace("""    <div class="why">""", """    {villa}
    <div class="why">""")
    s = s.replace(".pg {{ position: absolute;", """.photo {{ width: 100%; height: 100%; object-fit: cover; display: block }}
.ai {{ position: absolute; right: 3mm; bottom: 3mm; background: rgba(20,40,27,.72); color: #f3ead9; font-size: 6.2pt; padding: 1mm 2.4mm; border-radius: 6mm; letter-spacing: .03em }}
.band {{ position: relative }}
.type-band {{ background: var(--g9); padding: 13mm 15mm 0; background-image: repeating-linear-gradient(165deg, rgba(255,255,255,.035) 0 2px, transparent 2px 14px); }}
.type-band .bt {{ font-family: 'Cormorant Garamond', serif; font-weight: 700; font-size: 34pt; line-height: .98; color: #fbf7ef; margin-top: 3mm }}
.pics {{ display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; margin-top: 4mm }}
.pic {{ position: relative; height: 46mm; border-radius: 4mm; overflow: hidden }}
.pic.wide {{ height: 52mm; margin-top: 5mm }}
.pg {{ position: absolute;""", 1)
    open(p, 'w').write(s)
print('slots in place:', 'def img(name)' in s)
