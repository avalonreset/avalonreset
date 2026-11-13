#!/usr/bin/env python3
"""Render split module cards for the avalonreset profile README.

Each card is a body image (links to the GitHub repo) plus a row of separate
button images, so every visible "button" is its own real link:
  - card body        -> github.com/avalonreset/<repo>
  - engineering spec -> cto-legends.com/modules/<repo>
  - github readme    -> github.com/avalonreset/<repo>#readme

Idempotent: safe to rerun. Rewrites the card block of README.md between the
CARDS:START / CARDS:END markers.
"""
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True

root = Path(__file__).resolve().parent
cards = root / "assets" / "cards"
readme_path = root / "README.md"

GH = "https://github.com/avalonreset"
SITE = "https://cto-legends.com"
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Monaco, Consolas, monospace"

MODULES = [
    "legends-empire", "legends-astro", "legends-hetzner",
    "legends-coolify", "legends-cloudflare", "legends-stripe",
    "legends-buzz", "legends-gohighlevel", "legends-github",
    "legends-jev", "legends-geogrid", "legends-dataforseo",
    "legends-firecrawl", "legends-grant", "legends-obs",
    "legends-captions", "legends-youtube", "legends-yt-dlp",
    "legends-stable-audio-3", "legends-hyperyap", "legends-ambient-intelligence",
]

# Column viewBox x-offsets give flush outer edges and symmetric gutters.
COL_MIN_X = (-0.004, -2.25, -4.496)
COL_W = 296.5
BODY_VB_Y, BODY_VB_H = -3, 113  # card rect y=2.5..108.5
BTN_H = 27
FLAG_W = 886

STYLES = {
    "spec": dict(fill="#0a0506", stroke="#ef4444", sop="0.45", text="#f87171", weight="600"),
    "repo": dict(fill="#000000", stroke="#ffffff", sop="0.16", text="#e4e4e7", weight="600"),
    "pip": dict(fill="#07080c", stroke="#ef4444", sop="0.58", text="#ffffff", weight="600"),
    "docs": dict(fill="#0a0506", stroke="#ef4444", sop="0.58", text="#ffffff", weight="700"),
}


def pct(units: float, total: float) -> str:
    return f"{units / total * 100:.2f}%"


def button_svg(vb_x: float, vb_w: float, x0: float, x1: float, label: str, style: str, font: float = 10) -> str:
    s = STYLES[style]
    cx = (x0 + x1) / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb_x:g} 0 {vb_w:g} {BTN_H}" width="100%">\n'
        f'  <rect x="{x0:g}" y="0.5" width="{x1 - x0:g}" height="{BTN_H - 1}" rx="4" fill="{s["fill"]}" '
        f'stroke="{s["stroke"]}" stroke-opacity="{s["sop"]}" stroke-width="1"/>\n'
        f'  <text x="{cx:g}" y="17.2" fill="{s["text"]}" font-family="{FONT}" font-size="{font}" '
        f'font-weight="{s["weight"]}" text-anchor="middle">{label}</text>\n'
        f'</svg>\n'
    )


def render_module(name: str, col: int) -> None:
    path = cards / f"{name}.svg"
    svg = path.read_text(encoding="utf-8")
    m = COL_MIN_X[col]
    # Body: drop the painted footer and shorten the card.
    svg = re.sub(r'\s*<line x1="14" y1="115"[^>]*/>', "", svg)
    svg = re.sub(r'\s*<text x="14" y="136"[^>]*>[^<]*</text>', "", svg)
    svg = re.sub(r'\s*<text x="278" y="136"[^>]*>[^<]*</text>', "", svg)
    svg = re.sub(r'viewBox="[^"]+"', f'viewBox="{m:g} {BODY_VB_Y} {COL_W} {BODY_VB_H}"', svg, count=1)
    svg = re.sub(r'(<rect x="1" y="2.5" width="290" height=")[0-9.]+(")', r"\g<1>106\2", svg, count=1)
    path.write_text(svg, encoding="utf-8")
    half = COL_W / 2
    # Card spans x=1..291; buttons split it with a 6-unit gap centred at 146.
    (cards / f"{name}-spec.svg").write_text(
        button_svg(m, half, 1, 143, "engineering spec  →", "spec"), encoding="utf-8")
    (cards / f"{name}-repo.svg").write_text(
        button_svg(m + half, half, 149, 291, "github readme  ↗", "repo"), encoding="utf-8")


def render_flagship() -> None:
    path = cards / "cto-legends.svg"
    svg = path.read_text(encoding="utf-8")
    if "<!-- split-v1 -->" not in svg:
        svg = svg.replace('viewBox="0 0 886 161.5"', 'viewBox="0 0 886 120"', 1)
        svg = svg.replace('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 886 120" width="100%">',
                          '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 886 120" width="100%">\n  <!-- split-v1 -->', 1)
        svg = svg.replace('height="158"', 'height="116"')
        svg = re.sub(r'\s*<line x1="20" y1="114"[^>]*/>', "", svg)
        svg = re.sub(r'\s*<rect x="20" y="126"[^>]*/>', "", svg)
        svg = re.sub(r'\s*<text x="109" y="140.5".*?</text>', "", svg, flags=re.S)
        svg = re.sub(r'\s*<text x="212" y="140.5".*?</text>', "", svg, flags=re.S)
        svg = re.sub(r'\s*<text x="716" y="140.5".*?</text>', "", svg, flags=re.S)
        # Portrait: 136px square -> 94px square to fit the shorter card.
        svg = svg.replace('<rect x="734" y="13" width="136" height="136" rx="5"/>',
                          '<rect x="776" y="13" width="94" height="94" rx="5"/>')
        svg = svg.replace('<rect x="733" y="12" width="138" height="138" rx="6" fill="#050507"/>',
                          '<rect x="775" y="12" width="96" height="96" rx="6" fill="#050507"/>')
        svg = svg.replace('<image x="734" y="13" width="136" height="136"',
                          '<image x="776" y="13" width="94" height="94"')
        svg = svg.replace('<rect x="734" y="13" width="136" height="136" rx="5" fill="none"',
                          '<rect x="776" y="13" width="94" height="94" rx="5" fill="none"')
        svg = svg.replace('<line x1="736" y1="14" x2="868" y2="14"', '<line x1="778" y1="14" x2="868" y2="14"')
        path.write_text(svg, encoding="utf-8")
    # Three real buttons across the flagship width.
    b = [0, 354.4, 620.2, FLAG_W]
    segs = [
        ("cto-legends-pip", '<tspan fill="#f87171" font-weight="700">$</tspan> pip install cto-legends  ·  pypi v0.2.11', "pip"),
        ("cto-legends-repo", "github readme  ↗", "repo"),
        ("cto-legends-docs", '1-click agent handoff &amp; docs  <tspan fill="#f87171">↗</tspan>', "docs"),
    ]
    for i, (fname, label, style) in enumerate(segs):
        x0 = 1 if i == 0 else b[i] + 3
        x1 = FLAG_W - 1 if i == 2 else b[i + 1] - 3
        (cards / f"{fname}.svg").write_text(
            button_svg(b[i], b[i + 1] - b[i], x0, x1, label, style, font=10.4), encoding="utf-8")


def readme_block(alts: dict) -> str:
    b = [0, 354.4, 620.2, FLAG_W]
    out = ['<p align="left">']
    out.append(f'  <a href="{GH}/cto-legends"><img src="assets/cards/cto-legends.svg?v=7" width="100%" alt="{alts["cto-legends"]}" /></a>')
    links = [
        ("https://pypi.org/project/cto-legends/", "cto-legends-pip", "pip install cto-legends on PyPI"),
        (f"{GH}/cto-legends#readme", "cto-legends-repo", "cto-legends GitHub readme"),
        (SITE, "cto-legends-docs", "cto-legends agent handoff and docs"),
    ]
    row = [f'<a href="{u}"><img src="assets/cards/{f}.svg?v=1" width="{pct(b[i + 1] - b[i], FLAG_W)}" alt="{a}" /></a>'
           for i, (u, f, a) in enumerate(links)]
    out.append("  " + "<!--\n  -->".join(row))
    for r in range(0, len(MODULES), 3):
        trio = MODULES[r:r + 3]
        bodies = [f'<a href="{GH}/{n}"><img src="assets/cards/{n}.svg?v=4" width="33.33%" alt="{alts[n]}" /></a>' for n in trio]
        out.append("  " + "<!--\n  -->".join(bodies))
        btns = []
        for n in trio:
            btns.append(f'<a href="{SITE}/modules/{n}"><img src="assets/cards/{n}-spec.svg?v=1" width="16.66%" alt="{n} engineering spec" /></a>')
            btns.append(f'<a href="{GH}/{n}#readme"><img src="assets/cards/{n}-repo.svg?v=1" width="16.66%" alt="{n} GitHub readme" /></a>')
        out.append("  " + "<!--\n  -->".join(btns))
    out.append("</p>")
    return "\n".join(out)


def main() -> int:
    readme = readme_path.read_text(encoding="utf-8")
    alts = dict(re.findall(r'src="assets/cards/([a-z0-9-]+)\.svg\?v=\d+" width="[0-9.]+%" alt="([^"]+)"', readme))
    missing = [n for n in ["cto-legends", *MODULES] if n not in alts]
    if missing:
        raise SystemExit(f"FAIL: alt text missing for {missing}")
    for i, n in enumerate(MODULES):
        render_module(n, i % 3)
    render_flagship()
    block = readme_block(alts)
    start, end = "<!-- CARDS:START -->", "<!-- CARDS:END -->"
    if start in readme:
        readme = re.sub(re.escape(start) + r".*?" + re.escape(end), f"{start}\n{block}\n{end}", readme, flags=re.S)
    else:
        readme = re.sub(r'<p align="left">\s*<a href="[^"]*"><img src="assets/cards/cto-legends\.svg.*?</p>',
                        lambda _: f"{start}\n{block}\n{end}", readme, flags=re.S)
    readme_path.write_text(readme, encoding="utf-8")
    print(f"Rendered {len(MODULES)} module cards + flagship with split links.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
