from pathlib import Path
from html import escape
import random
import xml.etree.ElementTree as ET

root = Path(__file__).parent
assets = root / 'assets'
rng = random.Random(47)
parts = ['''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="90" viewBox="0 0 1200 90">
<defs><linearGradient id="pulse"><stop stop-color="#ff0000" stop-opacity="0"/><stop offset=".3" stop-color="#a80000"/><stop offset=".46" stop-color="#ff0000"/><stop offset=".5" stop-color="#fff"/><stop offset=".54" stop-color="#ff0000"/><stop offset=".7" stop-color="#a80000"/><stop offset="1" stop-color="#ff0000" stop-opacity="0"/></linearGradient><clipPath id="crop"><rect width="1200" height="90"/></clipPath></defs>
<style>''']
for i in range(8):
    xs = [rng.randint(-220,80),rng.randint(580,990),rng.randint(150,390),rng.randint(720,1100)]
    parts.append(f'@keyframes sweep{i}{{0%,100%{{transform:translateX({xs[0]}px)}}28%{{transform:translateX({xs[1]}px)}}57%{{transform:translateX({xs[2]}px)}}79%{{transform:translateX({xs[3]}px)}}}} .s{i}{{animation:sweep{i} {6.7+i*.613:.3f}s cubic-bezier(.45,0,.55,1) {-i*1.731:.3f}s infinite;}}')
parts.append('@media(prefers-reduced-motion:reduce){.scanner{animation:none!important;transform:translateX(440px)}} </style><g clip-path="url(#crop)">')
for i in range(8):
    y=24+i*6
    parts.append(f'<path d="M0 {y}H1200" stroke="#6b0000" stroke-opacity=".24"/><rect class="scanner s{i}" y="{y-1}" width="{rng.randint(220,380)}" height="2" fill="url(#pulse)"/>')
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

panel('router-name.svg',240,112,['cto-legends'],True)
panel('router-role.svg',240,112,['single-skill','router'],True)
panel('router-purpose.svg',720,112,['One entry point for the Legends ecosystem.','Discover modules, load instructions, and check readiness.'],True)
for file,width,label in [('module',240,'Module'),('focus',240,'Focus'),('capabilities',720,'What you can do')]:
    panel(f'heading-{file}.svg',width,48,[label])

p=root/'README.md'
s=p.read_text(encoding='utf-8')
start=s.index('<table width="100%">',s.index('### The ecosystem'))
end=s.index('</table>',start)+len('</table>')
s=s[:start]+'''<table width="100%"><tr>
<td width="20%"><a href="https://github.com/avalonreset/cto-legends"><img src="assets/router-name.svg" width="100%" alt="cto-legends" /></a></td>
<td width="20%"><img src="assets/router-role.svg" width="100%" alt="single-skill router" /></td>
<td width="60%"><img src="assets/router-purpose.svg" width="100%" alt="One entry point for the Legends ecosystem. Discover modules, load instructions, and check readiness." /></td>
</tr></table>'''+s[end:]
s=s.replace('height="56" alt=""','height="90" alt=""')
old='<tr><th width="20%" align="left">Module</th><th width="20%" align="left">Focus</th><th width="60%" align="left">What you can do</th></tr>'
new='<tr>'+''.join(f'<th width="{w}%" align="left"><img src="assets/heading-{n}.svg" width="100%" alt="{label}" /></th>' for w,n,label in [(20,'module','Module'),(20,'focus','Focus'),(60,'capabilities','What you can do')])+'</tr>'
assert old in s
p.write_text(s.replace(old,new),encoding='utf-8')
for path in assets.glob('*.svg'):
    ET.parse(path)
print('Generated eight independently timed scanner tracks and six shaded panels; SVG XML validated.')
