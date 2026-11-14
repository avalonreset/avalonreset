#!/usr/bin/env python3
"""Render split module cards for the avalonreset profile README.

Each card is a body image plus a footer cut into separate link images, so
every visible button is its own real link while the card still reads as one
unit. All card images use align="top", which removes the inline-image
baseline gap so body and footer join with no seam.

  card body          -> github.com/avalonreset/<repo>
  engineering spec   -> cto-legends.com/modules/<repo>
  github readme      -> github.com/avalonreset/<repo>#readme

Idempotent: rerun after editing card text. Rewrites the README block between
CARDS:START / CARDS:END.
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
# Gutter = 1.5*COL_W - 437 (18 units); min-x keeps outer edges flush.
COL_W = 303
COL_MIN_X = (0, (292 - COL_W) / 2, 292 - COL_W)
COL_PCT = 33.33
BODY_TOP, BODY_BOTTOM = -16, 108  # top margin separates card rows; bottom is the seam
FOOT_H = 30
SPLIT = 146  # card spans x=1..291
BORDER = 'stroke="#ffffff" stroke-opacity="0.09" stroke-width="1"'

FLAG_W, FLAG_BOTTOM, FLAG_FOOT_H = 886, 118, 32
FLAG_B = [0, FLAG_W / 3, FLAG_W * 2 / 3, FLAG_W]  # equal thirds
RED = 'stroke="#ef4444" stroke-opacity="0.68" stroke-width="1"'


HANDOFF = f"Set up {GH}/cto-legends and check which modules apply to this workspace."
PLAIN = re.compile(r"<[^>]+>|&[a-z]+;")
SPACED = ' letter-spacing="1.3"'  # small-caps button labels


def text(x: float, y: float, fill: str, label: str, size: float = 10, weight: str = "600") -> str:
    return (f'  <text x="{x:g}" y="{y:g}" fill="{fill}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}"{SPACED if PLAIN.sub("", label).isupper() else ""} text-anchor="middle">{label}</text>\n')


def svg(vb: str, body: str) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="100%">\n{body}</svg>\n'


def render_module(name: str, col: int) -> tuple[str, str]:
    path = cards / f"{name}.svg"
    s = path.read_text(encoding="utf-8")
    m = COL_MIN_X[col]
    # Legacy footer (v1 and earlier) removal.
    s = re.sub(r'\s*<line x1="14" y1="115"[^>]*/>', "", s)
    s = re.sub(r'\s*<text x="(?:14|278)" y="136"[^>]*>[^<]*</text>', "", s)
    edge = f"M1 {BODY_BOTTOM} V6.5 A4 4 0 0 1 5 2.5 H287 A4 4 0 0 1 291 6.5 V{BODY_BOTTOM}"
    head = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{m:g} {BODY_TOP} {COL_W} {BODY_BOTTOM - BODY_TOP}" width="100%">\n'
        '  <!-- seam-v3 -->\n'
        '  <defs>\n'
        '    <linearGradient id="sheen" x1="0" y1="2.5" x2="0" y2="108" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.05"/><stop offset="0.6" stop-color="#ffffff" stop-opacity="0"/></linearGradient>\n'
        '    <linearGradient id="edge" x1="0" y1="2.5" x2="0" y2="108" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.22"/><stop offset="1" stop-color="#ffffff" stop-opacity="0.09"/></linearGradient>\n'
        '  </defs>\n'
        '  <rect x="1" y="2.5" width="290" height="130" rx="4" fill="#000000"/>\n'
        f'  <path d="{edge} Z" fill="url(#sheen)"/>\n'
        f'  <path d="{edge}" fill="none" stroke="url(#edge)" stroke-width="1"/>\n'
    )
    s = re.sub(r'<svg[^>]*>\n.*?(?=  <text)', lambda _: head, s, count=1, flags=re.S)
    path.write_text(s, encoding="utf-8")

    b = FOOT_H - 0.5
    left_w, right_w = SPLIT - m, m + COL_W - SPLIT
    rule = 'stroke="#ffffff" stroke-opacity="0.07" stroke-width="1"'
    lbl = dict(size=8.6, weight="600")
    left = (
        f'  <path d="M1 0 V{b - 4} A4 4 0 0 0 5 {b} H{SPLIT} V0 Z" fill="#000000"/>\n'
        f'  <path d="M1 0 V{b - 4} A4 4 0 0 0 5 {b} H{SPLIT}" fill="none" {BORDER}/>\n'
        f'  <line x1="14" y1="0.5" x2="{SPLIT}" y2="0.5" {rule}/>\n'
        + text((1 + SPLIT) / 2, 18.6, "#f87171", "ENGINEERING SPEC →", **lbl)
    )
    right = (
        f'  <path d="M{SPLIT} 0 V{b} H287 A4 4 0 0 0 291 {b - 4} V0 Z" fill="#000000"/>\n'
        f'  <path d="M{SPLIT} {b} H287 A4 4 0 0 0 291 {b - 4} V0" fill="none" {BORDER}/>\n'
        f'  <line x1="{SPLIT}" y1="0.5" x2="278" y2="0.5" {rule}/>\n'
        f'  <line x1="{SPLIT + 0.5}" y1="9" x2="{SPLIT + 0.5}" y2="21" {rule}/>\n'
        + text((SPLIT + 291) / 2, 18.6, "#d4d4d8", "GITHUB README ↗", **lbl)
    )
    (cards / f"{name}-spec.svg").write_text(svg(f"{m:g} 0 {left_w:g} {FOOT_H}", left), encoding="utf-8")
    (cards / f"{name}-repo.svg").write_text(svg(f"{SPLIT} 0 {right_w:g} {FOOT_H}", right), encoding="utf-8")
    return f"{left_w / COL_W * COL_PCT:.3f}%", f"{right_w / COL_W * COL_PCT:.3f}%"


def render_flagship() -> None:
    path = cards / "cto-legends.svg"
    s = path.read_text(encoding="utf-8")
    if "<!-- seam-v2 -->" not in s:
        s = re.sub(r'viewBox="0 0 886 [0-9.]+"', f'viewBox="0 0 886 {FLAG_BOTTOM}"', s, count=1)
        s = s.replace('<rect x="1" y="2" width="884" height="116" rx="4" fill="#090406"/>',
                      '<!-- seam-v2 -->\n  <rect x="1" y="2" width="884" height="130" rx="4" fill="#090406"/>')
        s = s.replace(f'<rect x="1" y="2" width="884" height="116" rx="4" fill="url(#flagship-glow)" {RED}/>',
                      '<rect x="1" y="2" width="884" height="130" rx="4" fill="url(#flagship-glow)"/>')
        s = s.replace('<rect x="1" y="2" width="884" height="116" rx="4" fill="url(#portrait-glow)"/>',
                      '<rect x="1" y="2" width="884" height="130" rx="4" fill="url(#portrait-glow)"/>\n'
                      f'  <path d="M1 {FLAG_BOTTOM} V6 A4 4 0 0 1 5 2 H881 A4 4 0 0 1 885 6 V{FLAG_BOTTOM}" fill="none" {RED}/>')
        s = s.replace('<rect x="1" y="2" width="4" height="116" rx="1.5" fill="#ef4444"/>',
                      '<rect x="1" y="2" width="4" height="130" rx="1.5" fill="#ef4444"/>')
        if "<!-- seam-v2 -->" not in s or f"V{FLAG_BOTTOM}" not in s:
            raise SystemExit("FAIL: flagship SVG did not match expected markup")
        path.write_text(s, encoding="utf-8")

    b = FLAG_FOOT_H - 0.5
    fill = "#0c0507"
    divider = 'stroke="#ef4444" stroke-opacity="0.30" stroke-width="1"'
    segs = [
        ("cto-legends-repo", "GITHUB README  ↗", "#ffffff"),
        ("cto-legends-releases", "RELEASES  ↗", "#e4e4e7"),
        ("cto-legends-docs", 'AGENT HANDOFF &amp; DOCS  <tspan fill="#f87171">↗</tspan>', "#ffffff"),
    ]
    for i, (fname, label, color) in enumerate(segs):
        x0, x1 = FLAG_B[i], FLAG_B[i + 1]
        body = ""
        if i == 0:
            body += f'  <path d="M1 0 V{b - 4} A4 4 0 0 0 5 {b} H{x1} V0 Z" fill="{fill}"/>\n'
            body += f'  <path d="M1 0 V{b - 4} A4 4 0 0 0 5 {b} H{x1}" fill="none" {RED}/>\n'
            body += f'  <rect x="1" y="0" width="4" height="{b - 3}" fill="#ef4444"/>\n'
        elif i == 2:
            body += f'  <path d="M{x0} 0 V{b} H881 A4 4 0 0 0 885 {b - 4} V0 Z" fill="{fill}"/>\n'
            body += f'  <path d="M{x0} {b} H881 A4 4 0 0 0 885 {b - 4} V0" fill="none" {RED}/>\n'
        else:
            body += f'  <rect x="{x0}" y="0" width="{x1 - x0:g}" height="{b}" fill="{fill}"/>\n'
            body += f'  <line x1="{x0}" y1="{b}" x2="{x1}" y2="{b}" {RED}/>\n'
        if i > 0:
            body += f'  <line x1="{x0 + 0.5:g}" y1="0" x2="{x0 + 0.5:g}" y2="{b}" {divider}/>\n'
        body += f'  <line x1="{max(x0, 5):g}" y1="0.5" x2="{min(x1, 884.5):g}" y2="0.5" {divider}/>\n'
        cx = ((5 if i == 0 else x0) + (885 if i == 2 else x1)) / 2
        body += text(cx, 20.4, color, label, size=9.4, weight="700")
        (cards / f"{fname}.svg").write_text(svg(f"{x0:.3f} 0 {x1 - x0:.3f} {FLAG_FOOT_H}", body), encoding="utf-8")


def img(href: str, src: str, width: str, alt: str) -> str:
    return f'<a href="{href}"><img src="assets/cards/{src}" width="{width}" align="top" alt="{alt}" /></a>'


def readme_block(alts: dict, widths: dict) -> str:
    out = ['<p align="left">', "  " + img(f"{GH}/cto-legends", "cto-legends.svg?v=8", "100%", alts["cto-legends"])]
    links = [
        (f"{GH}/cto-legends#readme", "cto-legends-repo", "cto-legends GitHub readme"),
        (f"{GH}/cto-legends/releases", "cto-legends-releases", "cto-legends releases"),
        (SITE, "cto-legends-docs", "cto-legends agent handoff and docs"),
    ]
    out.append("  " + "<!--\n  -->".join(
        img(u, f"{f}.svg?v=3", f"{(FLAG_B[i + 1] - FLAG_B[i]) / FLAG_W * 100:.2f}%", a)
        for i, (u, f, a) in enumerate(links)))
    out += [
        "</p>",
        "",
        "<sub><b>AGENT HANDOFF</b> &nbsp;·&nbsp; in a hurry? copy this into Claude Code, Codex or any coding agent</sub>",
        "",
        "```text",
        HANDOFF,
        "```",
        "",
        '<p align="left">',
    ]
    for r in range(0, len(MODULES), 3):
        trio = MODULES[r:r + 3]
        out.append("  " + "<!--\n  -->".join(
            img(f"{GH}/{n}", f"{n}.svg?v=6", f"{COL_PCT}%", alts[n]) for n in trio))
        btns = []
        for n in trio:
            lw, rw = widths[n]
            btns.append(img(f"{SITE}/modules/{n}", f"{n}-spec.svg?v=3", lw, f"{n} engineering spec"))
            btns.append(img(f"{GH}/{n}#readme", f"{n}-repo.svg?v=3", rw, f"{n} GitHub readme"))
        out.append("  " + "<!--\n  -->".join(btns))
    out.append("</p>")
    return "\n".join(out)


def main() -> int:
    readme = readme_path.read_text(encoding="utf-8")
    alts = dict(re.findall(r'src="assets/cards/([a-z0-9-]+)\.svg\?v=\d+" width="[0-9.]+%"(?: align="top")? alt="([^"]+)"', readme))
    missing = [n for n in ["cto-legends", *MODULES] if n not in alts]
    if missing:
        raise SystemExit(f"FAIL: alt text missing for {missing}")
    widths = {n: render_module(n, i % 3) for i, n in enumerate(MODULES)}
    render_flagship()
    block = readme_block(alts, widths)
    start, end = "<!-- CARDS:START -->", "<!-- CARDS:END -->"
    if start not in readme:
        raise SystemExit("FAIL: CARDS markers missing from README.md")
    readme = re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: f"{start}\n{block}\n{end}", readme, flags=re.S)
    readme_path.write_text(readme, encoding="utf-8")
    print(f"Rendered {len(MODULES)} module cards + flagship with seamless split footers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
