from pathlib import Path
from html import escape
import random
import xml.etree.ElementTree as ET

root = Path(__file__).parent
assets = root / 'assets'
rng = random.Random(47)
parts = ['''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="90" viewBox="0 0 1200 90">
<defs>
<linearGradient id="pulse"><stop stop-color="#ff0000" stop-opacity="0"/><stop offset=".28" stop-color="#ad1723" stop-opacity=".15"/><stop offset=".55" stop-color="#e53340" stop-opacity=".55"/><stop offset=".72" stop-color="#fff" stop-opacity=".8"/><stop offset=".8" stop-color="#ff4955" stop-opacity=".55"/><stop offset="1" stop-color="#ff0000" stop-opacity="0"/></linearGradient>
<linearGradient id="fade"><stop stop-color="#fff" stop-opacity="0"/><stop offset=".12" stop-color="#fff"/><stop offset=".88" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="edges"><rect width="1200" height="90" fill="url(#fade)"/></mask>
<clipPath id="crop"><rect width="1200" height="90"/></clipPath></defs>
<style>@keyframes flow{from{transform:translateX(-680px)}to{transform:translateX(1280px)}}''']
for i in range(8):
    duration=12.8+i*.63+rng.random()*1.5
    parts.append(f'.s{i}{{animation:flow {duration:.3f}s linear {-4.7+i*.39:.3f}s infinite}} .t{i}{{animation:flow {duration+6.3:.3f}s linear {-13.9+i*.57:.3f}s infinite}}')
parts.append('@media(prefers-reduced-motion:reduce){.scanner{animation:none!important;transform:translateX(340px)}} </style><g clip-path="url(#crop)" mask="url(#edges)">')
for i in range(8):
    y=24+i*6
    width=rng.randint(420,640)
    parts.append(f'<path d="M0 {y}H1200" stroke="#72212a" stroke-opacity=".13"/><g class="scanner s{i}"><rect y="{y-2}" width="{width}" height="4" opacity=".10" fill="url(#pulse)"/><rect y="{y-.6}" width="{width}" height="1.2" fill="url(#pulse)"/></g><rect class="scanner t{i}" y="{y-.4}" width="{width-85}" height=".8" opacity=".45" fill="url(#pulse)"/>')
parts.append('</g></svg>')
(assets/'ecosystem-separator.svg').write_text('\n'.join(parts),encoding='utf-8')

def panel(name,width,height,lines,red=False):
    bg=('#310b10','#17080b') if red else ('#303741','#20262e')
    size=23 if width==240 else 22
    content=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"><title>{escape(" ".join(lines))}</title><defs><linearGradient id="bg" x2="0" y2="1"><stop stop-color="{bg[0]}"/><stop offset="1" stop-color="{bg[1]}"/></linearGradient></defs><rect width="{width}" height="{height}" rx="3" fill="url(#bg)"/><path d="M0 1H{width}" stroke="'+('#80212c' if red else '#59616a')+'"/>'
    start=(height-(len(lines)-1)*30)/2+8
    for j,line in enumerate(lines):
        content+=f'<text x="16" y="{start+j*30}" fill="#fff" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{600 if width==240 or height==48 else 400}">{escape(line)}</text>'
    content+='</svg>'
    (assets/name).write_text(content,encoding='utf-8')

for file,width,label in [('module',276,'module'),('focus',204,'focus'),('capabilities',720,'capability streamline')]:
    panel(f'heading-{file}.svg',width,48,[label])

p=root/'README.md'
s=p.read_text(encoding='utf-8')
start=s.index('<table width="100%">',s.index('### The ecosystem'))
end=s.index('</table>',start)+len('</table>')
s=s[:start]+'''<table width="100%"><tr>
<td width="277" valign="top"><a href="https://github.com/avalonreset/cto-legends"><strong><code>cto-legends</code></strong></a> &nbsp;&lt;---</td>
<td width="220" valign="top"><strong>single-skill-router</strong></td>
<td width="703" valign="top">central capability index, module manager, and execution router.</td>
</tr></table>'''+s[end:]
s=s.replace('height="56" alt=""','height="90" alt=""')
old='<tr><th width="20%" align="left">Module</th><th width="20%" align="left">Focus</th><th width="720" align="left">What you can do</th></tr>'
new='<tr>'+''.join(f'<th width="{w}" align="left"><img src="assets/heading-{n}.svg" width="100%" alt="{label}" /></th>' for w,n,label in [(276,'module','module'),(204,'focus','focus'),(720,'capabilities','capability streamline')])+'</tr>'
assert old in s or new in s
p.write_text(s.replace(old,new),encoding='utf-8')
for path in assets.glob('*.svg'):
    ET.parse(path)
print('Generated eight layered left-to-right shimmer tracks; restored text router; retained shaded headings. SVG XML validated.')

# Keep the current layered animation when regenerating the full profile.
import runpy
runpy.run_path(str(root / 'render-shimmer.py'))
