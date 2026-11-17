W, H = 900, 620
s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
     '<defs><linearGradient id="nr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a9d6ec"/><stop offset="1" stop-color="#6fadd1"/></linearGradient></defs>',
     f'<rect width="{W}" height="{H}" rx="20" fill="#f6efe2"/>']
# Narmada
s.append('<path d="M -20 470 C 140 440, 250 470, 360 452 S 560 420, 680 440 S 840 470, 920 452 L 920 560 C 820 580, 700 545, 610 548 S 420 565, 320 568 S 120 585, -20 598 Z" fill="url(#nr)"/>')
s.append('<text x="700" y="512" font-family="Cormorant Garamond" font-style="italic" font-weight="600" font-size="34" fill="#ffffff">Narmada</text>')
road = 'fill="none" stroke="#c9a46c" stroke-width="8" stroke-linecap="round"'
s.append(f'<path d="M 150 400 C 240 378, 300 368, 380 372 S 520 384, 610 378" {road}/>')                      # Jalkoti – Maheshwar road
s.append(f'<path d="M 610 378 C 560 300, 430 230, 300 160" {road}/>')                                           # Maheshwar – Dhamnod
s.append('<path d="M 380 372 L 372 336" fill="none" stroke="#1e3a2b" stroke-width="5" stroke-linecap="round" stroke-dasharray="2 7"/>')  # approach road
s.append('<path d="M 110 250 L 300 160 L 560 47" fill="none" stroke="#b9533a" stroke-width="10" stroke-linecap="round"/>')
s.append('<polygon points="590,34 556,30 568,60" fill="#b9533a"/>')
s.append('<text x="352" y="118" font-family="Inter" font-weight="700" font-size="17" fill="#8f3b27" transform="rotate(-23.5 352 118)">NH-52 · to Indore ≈ 90 km</text>')
s.append('<text x="150" y="256" font-family="Inter" font-size="13" fill="#8f3b27" transform="rotate(-25 150 256)">Agra–Mumbai highway</text>')
def town(x, y, name, sub, anchor, tx, ty, big=False):
    s.append(f'<circle cx="{x}" cy="{y}" r="{10 if big else 7}" fill="#1e3a2b" stroke="#ffffff" stroke-width="3"/>')
    s.append(f'<text x="{tx}" y="{ty}" text-anchor="{anchor}" font-family="Cormorant Garamond" font-weight="700" font-size="{34 if big else 25}" fill="#1e3a2b">{name}</text>')
    s.append(f'<text x="{tx}" y="{ty + 22}" text-anchor="{anchor}" font-family="Inter" font-size="14" fill="#5b6b62">{sub}</text>')
town(610, 378, 'Maheshwar', 'Ahilya Fort · ghats · temples', 'start', 632, 372, big=True)
town(300, 160, 'Dhamnod', '13.5 km from Maheshwar', 'end', 282, 150)
town(150, 400, 'Jalkoti', 'home of Sahastradhara', 'middle', 150, 436)
s.append('<g transform="translate(578,300)" fill="#b8692e"><rect x="0" y="26" width="52" height="18" rx="1"/>' + ''.join(f'<rect x="{2 + 12 * i}" y="17" width="7" height="9"/>' for i in range(5)) + '<path d="M 21 26 L 21 8 Q 26 -2 31 8 L 31 26 Z"/></g>')
sx, sy = 372, 330
s.append(f'<circle cx="{sx}" cy="{sy - 18}" r="40" fill="#5f8f4e" fill-opacity="0.18"/>')
s.append(f'<path d="M {sx} {sy} C {sx - 18} {sy - 22}, {sx - 18} {sy - 46}, {sx} {sy - 50} C {sx + 18} {sy - 46}, {sx + 18} {sy - 22}, {sx} {sy} Z" fill="#1e3a2b"/><circle cx="{sx}" cy="{sy - 33}" r="7" fill="#f6efe2"/>')
s.append(f'<text x="{sx}" y="{sy - 66}" text-anchor="middle" font-family="Cormorant Garamond" font-weight="700" font-size="27" fill="#1e3a2b">Maheshwar Greens</text>')
s.append(f'<path d="M {sx + 24} {sy - 30} Q 480 300, 572 318" fill="none" stroke="#1e3a2b" stroke-width="2.2" stroke-dasharray="6 6"/>')
s.append('<text x="482" y="338" text-anchor="middle" font-family="Inter" font-weight="700" font-size="15" fill="#1e3a2b">≈ 4 km to Ahilya Fort</text>')
s.append('<text x="482" y="356" text-anchor="middle" font-family="Inter" font-size="12.5" fill="#5b6b62">straight-line distance</text>')
s.append(f'<g transform="translate({W - 62},62)"><path d="M 0 -30 L 11 7 L 0 1 L -11 7 Z" fill="#1e3a2b"/><text x="0" y="28" text-anchor="middle" font-family="Inter" font-weight="700" font-size="15" fill="#1e3a2b">N</text></g>')
s.append(f'<text x="26" y="{H - 22}" font-family="Inter" font-size="13" fill="#7a8a80">Schematic map – not to scale</text>')
s.append('</svg>'); open('location_map.svg', 'w').write(''.join(s)); print('map ok')
