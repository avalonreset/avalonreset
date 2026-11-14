"""Layered, deterministic pseudo-random flowing light with right-justified open source badge. No scripts in SVG."""
from pathlib import Path
import math
import random
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from typeset import Typesetter, width  # noqa: E402
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("render_cards", Path(__file__).resolve().parent / "render-cards.py")
rc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rc)

# Geometry: the stream runs in a track whose edges continue the chip's top and bottom borders,
# so the light and the [license: open source] badge share one height (y 6..30).
LB = 9.62
CHIP_W = width("open source", LB) + 28
CHIP_X = 885 - CHIP_W
LABEL_END = CHIP_X - 8
STREAM_END = LABEL_END - width("license:", LB) - 16
TOP, BOT = 6, 30
W, H, END = f"{STREAM_END - 1:.2f}", BOT - TOP, f"{STREAM_END:.2f}"

root = Path(__file__).parent
rng = random.Random(20260925)
out = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -8.2 886 41.7" width="100%">
<defs>
<linearGradient id="light"><stop stop-color="#ff0000" stop-opacity="0"/><stop offset=".2" stop-color="#c00000" stop-opacity=".2"/><stop offset=".48" stop-color="#ff0000" stop-opacity=".75"/><stop offset=".62" stop-color="#fff"/><stop offset=".73" stop-color="#ff1a1a" stop-opacity=".8"/><stop offset="1" stop-color="#ff0000" stop-opacity="0"/></linearGradient>
<clipPath id="crop"><rect x="1" y="{TOP}" width="{W}" height="{H}"/></clipPath><linearGradient id="fade" gradientUnits="userSpaceOnUse" x1="1" x2="{END}"><stop stop-color="#fff" stop-opacity="0"/><stop offset=".07" stop-color="#fff"/><stop offset=".86" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient><mask id="trail" maskUnits="userSpaceOnUse" x="0" y="{TOP}" width="{END}" height="{H}"><rect x="0" y="{TOP}" width="{END}" height="{H}" fill="url(#fade)"/></mask></defs><style>''']
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
        y = TOP + 2.5 + rail * (BOT - TOP - 5) / 7
        bend = math.sin(rail * 0.81 + layer * 1.3) * 0.6
        d = f"M0 {y:.2f} C{width*0.3:.2f} {y+bend:.2f} {width*0.7:.2f} {y-bend:.2f} {width} {y:.2f}"
        alpha = rng.uniform(0.27, 0.66)
        layers.append(
            f'<g class="flow f{n}" opacity="{alpha:.3f}"><path d="{d}" stroke="url(#light)" stroke-width="3.8" opacity=".12"/><path d="{d}" stroke="url(#light)" stroke-width="{rng.uniform(0.6, 1.15):.2f}"/></g>'
        )
out.append(
    '@media(prefers-reduced-motion:reduce){.flow{animation:none!important;transform:translateX(220px);opacity:.2}}</style><g mask="url(#trail)"><g clip-path="url(#crop)" fill="none">'
)
out.extend(layers)
out.append("</g>")
# The track: two hairlines on the chip's border lines, fading in and out with the light.
out.append(f'<path d="M1 {TOP + .5}H{STREAM_END:.2f}M1 {BOT - .5}H{STREAM_END:.2f}" stroke="#ffffff" stroke-opacity=".1" stroke-width="1"/></g>')
T = Typesetter()
chips = rc.label(T, LABEL_END, TOP, "license", LB, "end") + rc.chip(T, CHIP_X, TOP, "open source", LB, "chip-sep")
out.append(T.defs() + chips + "</svg>")
svg = "\n".join(out)
ET.fromstring(svg)
# Path tracks REV in render-cards.py.
(rc.cards / "ecosystem-separator.svg").write_text(svg, encoding="utf-8")
assert svg.count('class="flow ') == 80
print(f"80 filaments in a y {TOP}..{BOT} track (x=1..{STREAM_END:.0f}, faded) + license: [open source] (x={CHIP_X:.0f}..885); XML valid.")
