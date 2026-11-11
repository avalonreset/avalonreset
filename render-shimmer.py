"""Layered, deterministic pseudo-random flowing light with right-justified open source badge. No scripts in SVG."""
from pathlib import Path
import math
import random
import xml.etree.ElementTree as ET

root = Path(__file__).parent
rng = random.Random(20260925)
out = ['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 886 36" width="100%">
<defs>
<linearGradient id="light"><stop stop-color="#ff0000" stop-opacity="0"/><stop offset=".2" stop-color="#bd101f" stop-opacity=".2"/><stop offset=".48" stop-color="#ff2738" stop-opacity=".75"/><stop offset=".62" stop-color="#fff"/><stop offset=".73" stop-color="#ff3645" stop-opacity=".8"/><stop offset="1" stop-color="#ff0000" stop-opacity="0"/></linearGradient>
<clipPath id="crop"><rect x="1" y="0" width="713" height="36"/></clipPath></defs><style>''']
layers = []
for rail in range(8):
    for layer in range(10):
        n = rail * 10 + layer
        duration = 7.8 + layer * 1.43 + rng.uniform(-0.7, 2.4) + rail * 0.173
        delay = -(layer * 3.71 + rail * 0.31 + rng.uniform(0, 2.1))
        width = rng.randint(90, 210) if layer % 2 else rng.randint(240, 490)
        positions = [
            -520,
            -180 + rng.randint(-60, 60),
            210 + rng.randint(-85, 85),
            580 + rng.randint(-70, 70),
            760,
        ]
        frames = "".join(f"{t}%{{transform:translateX({x}px)}}" for t, x in zip([0, 25, 50, 75, 100], positions))
        out.append(
            f"@keyframes f{n}{{{frames}}}.f{n}{{animation:f{n} {duration:.3f}s cubic-bezier(.33,.24,.67,.76) {delay:.3f}s infinite}}"
        )
        y = 4.5 + rail * 3.85
        bend = math.sin(rail * 0.81 + layer * 1.3) * 0.9
        d = f"M0 {y:.2f} C{width*0.3:.2f} {y+bend:.2f} {width*0.7:.2f} {y-bend:.2f} {width} {y:.2f}"
        alpha = rng.uniform(0.27, 0.66)
        layers.append(
            f'<g class="flow f{n}" opacity="{alpha:.3f}"><path d="{d}" stroke="url(#light)" stroke-width="3.8" opacity=".12"/><path d="{d}" stroke="url(#light)" stroke-width="{rng.uniform(0.6, 1.15):.2f}"/></g>'
        )
out.append(
    '@media(prefers-reduced-motion:reduce){.flow{animation:none!important;transform:translateX(220px);opacity:.2}}</style><g clip-path="url(#crop)" fill="none">'
)
out.extend(layers)
out.append("</g>")
out.append(
    '  <rect x="728" y="6" width="58" height="24" rx="3" fill="#050507" stroke="#ffffff" stroke-opacity="0.15" stroke-width="1"/>\n'
    '  <text x="757" y="21.5" fill="#a1a1aa" font-family="ui-monospace, SFMono-Regular, \'SF Mono\', Menlo, Monaco, Consolas, monospace" font-size="10" font-weight="600" text-anchor="middle">license</text>\n'
    '  <rect x="788" y="6" width="97" height="24" rx="3" fill="#1f070b" stroke="#ef4444" stroke-opacity="0.68" stroke-width="1"/>\n'
    '  <rect x="788" y="6" width="2.5" height="24" rx="1" fill="#ef4444"/>\n'
    '  <text x="837.5" y="21.5" fill="#ffffff" font-family="ui-monospace, SFMono-Regular, \'SF Mono\', Menlo, Monaco, Consolas, monospace" font-size="10" font-weight="700" text-anchor="middle">open source</text>\n'
    "</svg>"
)
svg = "\n".join(out)
ET.fromstring(svg)
(root / "assets/ecosystem-separator.svg").write_text(svg, encoding="utf-8")
assert "mask=" not in svg
assert svg.count('class="flow ') == 80
print("80 flowing filaments (x=1..714) + right-justified [license][open source] badge (x=728..885); XML valid.")
