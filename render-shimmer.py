"""Layered, deterministic pseudo-random flowing light. No scripts in SVG."""
from pathlib import Path
import math
import random
import re
import xml.etree.ElementTree as ET

root = Path(__file__).parent
rng = random.Random(20260925)
out = ['''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="44" viewBox="0 0 1200 44" preserveAspectRatio="none">
<defs>
<linearGradient id="light"><stop stop-color="#ff0000" stop-opacity="0"/><stop offset=".2" stop-color="#bd101f" stop-opacity=".2"/><stop offset=".48" stop-color="#ff2738" stop-opacity=".75"/><stop offset=".62" stop-color="#fff"/><stop offset=".73" stop-color="#ff3645" stop-opacity=".8"/><stop offset="1" stop-color="#ff0000" stop-opacity="0"/></linearGradient>
<clipPath id="crop"><rect width="1200" height="44"/></clipPath></defs><style>''']
layers=[]
# Eight close rails, ten simultaneous light layers on every rail.
# Related delays form diagonal cascades; incommensurate periods prevent lockstep.
for rail in range(8):
    for layer in range(10):
        n=rail*10+layer
        duration=7.8+layer*1.43+rng.uniform(-.7,2.4)+rail*.173
        delay=-(layer*3.71+rail*.31+rng.uniform(0,2.1))
        width=rng.randint(110,280) if layer%2 else rng.randint(330,670)
        positions=[-720, -250+rng.randint(-90,90), 290+rng.randint(-120,120), 820+rng.randint(-100,100),1280]
        frames=''.join(f'{t}%{{transform:translateX({x}px)}}' for t,x in zip([0,25,50,75,100],positions))
        out.append(f'@keyframes f{n}{{{frames}}}.f{n}{{animation:f{n} {duration:.3f}s cubic-bezier(.33,.24,.67,.76) {delay:.3f}s infinite}}')
        y=3+rail*5.35
        # Each filament gently curves around its rail instead of being a flat rectangle.
        bend=math.sin(rail*.81+layer*1.3)*1.1
        d=f'M0 {y:.2f} C{width*.3:.2f} {y+bend:.2f} {width*.7:.2f} {y-bend:.2f} {width} {y:.2f}'
        alpha=rng.uniform(.27,.66)
        layers.append(f'<g class="flow f{n}" opacity="{alpha:.3f}"><path d="{d}" stroke="url(#light)" stroke-width="4.5" opacity=".12"/><path d="{d}" stroke="url(#light)" stroke-width="{rng.uniform(.65,1.3):.2f}"/></g>')
out.append('@media(prefers-reduced-motion:reduce){.flow{animation:none!important;transform:translateX(350px);opacity:.2}}</style><g clip-path="url(#crop)" fill="none">')
out.extend(layers)
out.append('</g></svg>')
svg='\n'.join(out)
ET.fromstring(svg)
(root/'assets/ecosystem-separator.svg').write_text(svg,encoding='utf-8')
p=root/'README.md'
s=p.read_text(encoding='utf-8')
s=re.sub(r'<(?:p|div)><img src="assets/ecosystem-separator.svg"[^>]+/></(?:p|div)>', '<div><img src="assets/ecosystem-separator.svg" width="100%" height="44" alt="" /></div>',s)
p.write_text(s,encoding='utf-8')
assert 'mask=' not in svg
assert svg.count('class="flow ') == 80
print('80 flowing filaments, 8 rails, 44px canvas, hard-cut full-width edges; XML valid.')
