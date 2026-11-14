"""Silk-wave separator: layered harmonic ribbons drifting right to left, with light pulses riding them.

Pure SVG + CSS (GitHub serves README SVGs as <img>: no scripts, no fonts). Each ribbon is a sum of
three harmonics of one wavelength P, drawn 1.5 periods wide past the track and translated by exactly
P per cycle, so the loop is seamless. Ribbons use different P, phases and speeds, so their
interference never visibly repeats. Everything stays inside the chip's y 6..30 track.
"""
from pathlib import Path
import importlib.util
import math
import random
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from typeset import Typesetter, width  # noqa: E402

_spec = importlib.util.spec_from_file_location("render_cards", Path(__file__).resolve().parent / "render-cards.py")
rc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rc)

LB = 9.62
CHIP_W = width("open source", LB) + 28
CHIP_X = 885 - CHIP_W
LABEL_END = CHIP_X - 8
END = LABEL_END - width("license:", LB) - 16   # the light stops here, before the label
TOP, BOT = 6, 30
MID, ROOM = (TOP + BOT) / 2, (BOT - TOP) / 2 - 2.2  # vertical room for a ribbon, stroke included

rng = random.Random(20261114)
css, glow, core, pulses = [], [], [], []


def ribbon(P: float, amps, phases, x0: float, x1: float, step: float = 4.5) -> str:
    pts = []
    x = x0
    while x <= x1 + 1e-6:
        y = MID + sum(a * math.sin(2 * math.pi * (k + 1) * x / P + ph) for k, (a, ph) in enumerate(zip(amps, phases)))
        pts.append(f"{x:.1f} {y:.1f}")
        x += step
    return "M" + "L".join(pts)


# (colour, opacity, width, count): deep red body, bright red ribbons, two white silk highlights
KINDS = [("#990000", 0.5, 1.6, 4), ("#ff0000", 0.5, 0.8, 5), ("#ff1a1a", 0.45, 0.55, 3), ("#ffffff", 0.32, 0.45, 2)]
n = 0
for colour, op, sw, count in KINDS:
    for _ in range(count):
        P = rng.uniform(260, 520)
        # three harmonics, amplitudes shrinking, total scaled to fit the track exactly
        raw = [rng.uniform(.55, 1), rng.uniform(.15, .45), rng.uniform(.05, .22)]
        k = ROOM * rng.uniform(.45, 1) / sum(raw)
        amps = [a * k for a in raw]
        phases = [rng.uniform(0, 2 * math.pi) for _ in raw]
        d = ribbon(P, amps, phases, 0, END + P + 6)
        dur = rng.uniform(16, 34) * (P / 400)          # slow, soothing drift
        breathe = rng.uniform(7, 15)
        css.append(f".w{n}{{animation:drift{n} {dur:.2f}s linear {-rng.uniform(0, dur):.2f}s infinite}}"
                   f"@keyframes drift{n}{{to{{transform:translateX(-{P:.2f}px)}}}}"
                   f".b{n}{{transform-origin:0 {MID}px;animation:breathe {breathe:.2f}s ease-in-out {-rng.uniform(0, breathe):.2f}s infinite alternate}}")
        core.append(f'<g class="b{n}"><path class="w{n}" d="{d}" stroke="{colour}" stroke-opacity="{op}" stroke-width="{sw}"/></g>')
        if colour != "#ffffff":
            glow.append(f'<g class="b{n}"><path class="w{n}" d="{d}" stroke="{colour}" stroke-opacity="{op * .5:.2f}" stroke-width="{sw * 3:.1f}"/></g>')
        # light pulses: a short bright dash gliding leftward along some ribbons
        if colour in ("#ff0000", "#ffffff") and rng.random() < .8:
            pd = rng.uniform(5, 11)
            css.append(f".p{n}{{stroke-dasharray:12 988;animation:pulse{n} {pd:.2f}s linear {-rng.uniform(0, pd):.2f}s infinite}}"
                       f"@keyframes pulse{n}{{from{{stroke-dashoffset:-1000}}to{{stroke-dashoffset:0}}}}")
            pulses.append(f'<g class="b{n}"><g class="w{n}"><path class="p{n}" pathLength="1000" d="{d}" stroke="#ffffff" '
                          f'stroke-opacity=".75" stroke-width="{sw + .3:.1f}" stroke-linecap="round"/></g></g>')
        n += 1

style = ("".join(css)
         + "@keyframes breathe{from{transform:scaleY(.72)}to{transform:scaleY(1)}}"
         + "@media(prefers-reduced-motion:reduce){*{animation:none!important}}")

T = Typesetter()
badge = rc.label(T, LABEL_END, TOP, "license", LB, "end") + rc.chip(T, CHIP_X, TOP, "open source", LB, "chip-sep")
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -8.2 886 41.7" width="100%">
<defs>
<clipPath id="crop"><rect x="1" y="{TOP}" width="{END - 1:.2f}" height="{BOT - TOP}"/></clipPath>
<linearGradient id="fade" gradientUnits="userSpaceOnUse" x1="1" x2="{END:.2f}"><stop stop-color="#fff" stop-opacity="0"/><stop offset=".08" stop-color="#fff"/><stop offset=".84" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="trail" maskUnits="userSpaceOnUse" x="0" y="{TOP}" width="{END:.2f}" height="{BOT - TOP}"><rect x="0" y="{TOP}" width="{END:.2f}" height="{BOT - TOP}" fill="url(#fade)"/></mask>
<filter id="soft" x="-5%" y="-60%" width="110%" height="220%"><feGaussianBlur stdDeviation="1.6"/></filter>
<filter id="spark" x="-5%" y="-60%" width="110%" height="220%"><feGaussianBlur stdDeviation="2.2" result="b"/><feComponentTransfer in="b" result="b"><feFuncA type="linear" slope="2.2"/></feComponentTransfer><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs><style>{style}</style>
<g mask="url(#trail)"><g clip-path="url(#crop)" fill="none">
<g filter="url(#soft)">{"".join(glow)}</g>
{"".join(core)}
<g filter="url(#spark)">{"".join(pulses)}</g>
</g>
<path d="M1 {TOP + .5}H{END:.2f}M1 {BOT - .5}H{END:.2f}" stroke="#ffffff" stroke-opacity=".1" stroke-width="1"/></g>
{T.defs()}{badge}</svg>'''
ET.fromstring(svg)
(rc.cards / "ecosystem-separator.svg").write_text(svg, encoding="utf-8")
print(f"{n} silk ribbons, {len(pulses)} light pulses, right to left, track y {TOP}..{BOT} x 1..{END:.0f}; "
      f"license: [open source] x {CHIP_X:.0f}..885; {len(svg) // 1024} KB; XML valid.")
