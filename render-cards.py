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
# Design revision folder. GitHub caches raw images by path and ignores ?v= bumps, so every
# visual change ships under a new folder: bump REV, git mv the files, rerun.
REV = "r2"
cards = root / "assets" / "cards" / REV
readme_path = root / "README.md"

GH = "https://github.com/avalonreset"
SITE = "https://cto-legends.com"
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Monaco, Consolas, monospace"

# Type scale, in rendered px at GitHub's ~829px README width. Four sizes only:
#   head 14 (section headings) / title 12 (card titles) / body 11 (prose) / label 9 (chips, meta, buttons)
# lowercase label = information; UPPERCASE letter-spaced label = clickable action; an arrow = a link.
TYPE = {"head": 14, "title": 12, "body": 11, "label": 9}
K_CARD = 829 * 0.3333 / 303  # px per SVG unit, module cards
K_WIDE = 829 / 886           # px per SVG unit, full-width panels
MONO_EM = 0.6025             # widest advance in the font stack (SF Mono / Menlo)


def u(role: str, k: float) -> float:
    return round(TYPE[role] / k, 2)


def wrap(text: str, size: float, width: float, lines: int) -> list:
    """Greedy wrap at spaces only (never mid-word or at hyphens); fail loudly on overflow."""
    cap = int(width / (size * MONO_EM))
    out, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > cap:
            out.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    out.append(cur)
    if len(out) > lines:
        raise SystemExit(f"FAIL: copy needs {len(out)} lines (max {lines}, {cap} chars): {text}")
    return out


# Module card copy: (category, license, one outcome-first sentence, 3 lines max).
COPY = {
    "legends-empire": ("foundation", "mit", "Turn your Obsidian vault into agent memory, with SHA-256 integrity locks and crash-safe writes."),
    "legends-astro": ("foundation", "mit", "Move WordPress, Next.js, or HTML sites to Astro with every route and SEO tag accounted for."),
    "legends-hetzner": ("infrastructure", "mit", "Check live Hetzner stock in the EU and US, size servers for cost, and preflight every build."),
    "legends-coolify": ("infrastructure", "mit", "Audit your Coolify servers read-only: containers, deploy queues, env keys, and backups."),
    "legends-cloudflare": ("infrastructure", "mit", "Change Cloudflare DNS without surprises: preview each edit, keep proxy settings, confirm it is live."),
    "legends-stripe": ("infrastructure", "mit", "Keep Stripe in sync: match Test and Live prices, reconcile fees to the cent, and verify webhooks."),
    "legends-buzz": ("infrastructure", "mit", "Run self-hosted Block Buzz Nostr relays from the command line, with no MCP daemon to babysit."),
    "legends-gohighlevel": ("infrastructure", "mit", "Run GoHighLevel agencies at scale: batch-clone snapshots, X-ray workflows, lock down permissions."),
    "legends-github": ("intelligence", "mit", "Keep repos launch-ready: health audits, verified releases, and topics matched to search demand."),
    "legends-jev": ("infrastructure", "mit", "Give your agent eyes: local OCR, exact pixel coordinates, and storefront sign checks."),
    "legends-geogrid": ("intelligence", "mit", "Map local Google Maps rankings across a circular grid at wholesale rates, with 21-page PDF reports."),
    "legends-dataforseo": ("intelligence", "mit", "Pull Google SERPs, Maps listings, and keyword volume from DataForSEO, cost previewed first."),
    "legends-firecrawl": ("intelligence", "mit", "Turn JavaScript-heavy sites into clean Markdown with preview-first, bounded Firecrawl crawls."),
    "legends-grant": ("intelligence", "mit", "Find grants across 56 US jurisdictions and check every eligibility rule word for word."),
    "legends-obs": ("studio", "mit", "Drive OBS Studio from your agent: scene switching, encoder checks, profile backups, and test clips."),
    "legends-captions": ("studio", "mit", "Frame-accurate, word-by-word subtitles for 4K60 video, with tech terms and acronyms spelled right."),
    "legends-youtube": ("studio", "mit", "Run YouTube channels through the official APIs: safe metadata edits, CTR audits, private uploads."),
    "legends-yt-dlp": ("studio", "mit", "Pull video, audio, and transcripts in paced, resumable batches, then cut clips frame-accurate."),
    "legends-stable-audio-3": ("studio", "apache-2.0", "Make custom instrumental music on your own GPU and blend it into seamless multi-hour mixes."),
    "legends-hyperyap": ("studio", "agpl-3.0", "Push-to-talk dictation that runs offline on your GPU and types into any app on Windows, macOS, or Linux."),
    "legends-ambient-intelligence": ("studio", "mit", "Turn voice recorder and meeting audio into structured Obsidian notes, entirely offline."),
}

# Flagship card copy (886-unit panel; body column x=20..716).
FLAG_TAG = "// start here"
FLAG_PILL = "1 install unlocks all 21 modules"
FLAG_LEAD = "Install this one package. Never install the 21 modules below by hand."
FLAG_BODY = ("Your agent starts with a ~650-token map of every tool instead of 50,000 tokens of MCP schemas, "
             "then installs the exact module a task calls for, SHA-256 verified, the moment it is needed.")
HANDOFF_NOTE = "// in a hurry? paste this into claude code, codex, or any coding agent"

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
BODY_TOP, BODY_BOTTOM = -16, 110  # top margin separates card rows; bottom is the seam
FOOT_H = 30
SPLIT = 146  # card spans x=1..291
BORDER = 'stroke="#ffffff" stroke-opacity="0.09" stroke-width="1"'

FLAG_W, FLAG_BOTTOM, FLAG_FOOT_H = 886, 118, 32
FLAG_B = [0, FLAG_W / 3, FLAG_W * 2 / 3, FLAG_W]  # equal thirds
RED = 'stroke="#ef4444" stroke-opacity="0.68" stroke-width="1"'


HANDOFF = f"Set up {GH}/cto-legends and check which modules apply to this workspace."
PLAIN = re.compile(r"<[^>]+>|&[a-z]+;")


def text(x: float, y: float, fill: str, label: str, size: float = 10, weight: str = "600") -> str:
    spaced = f' letter-spacing="{size * 0.1:.2f}"' if PLAIN.sub("", label).isupper() else ""
    return (f'  <text x="{x:g}" y="{y:g}" fill="{fill}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}"{spaced} text-anchor="middle">{label}</text>\n')


def ltext(x: float, y: float, fill: str, body: str, size: float, weight: str = "400", anchor: str = "start") -> str:
    a = "" if anchor == "start" else f' text-anchor="{anchor}"'
    return (f'  <text x="{x:g}" y="{y:g}" fill="{fill}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}"{a}>{body}</text>\n')


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
    cat, lic, desc = COPY[name]
    t, lb, bd = u("title", K_CARD), u("label", K_CARD), u("body", K_CARD)
    body = ltext(14, 25, "#ffffff", name, t, "700")
    body += ltext(14, 40, "#a1a1aa", f"{cat} · {lic}", lb, "600")
    for i, line in enumerate(wrap(desc, bd, 278 - 14, 3)):
        body += ltext(14, 60 + 17 * i, "#a1a1aa", line, bd)
    path.write_text(head + body + "</svg>\n", encoding="utf-8")

    b = FOOT_H - 0.5
    left_w, right_w = SPLIT - m, m + COL_W - SPLIT
    rule = 'stroke="#ffffff" stroke-opacity="0.07" stroke-width="1"'
    lbl = dict(size=u("label", K_CARD), weight="600")
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
    path = cards / "cto-legends-flagship.svg"
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

    hd, bd, lb = u("head", K_WIDE), u("body", K_WIDE), u("label", K_WIDE)
    lines = wrap(FLAG_LEAD + " " + FLAG_BODY, bd, 716 - 20, 3)
    assert lines[0].startswith(FLAG_LEAD), "lead must open line 1"
    lines[0] = f'<tspan fill="#ffffff" font-weight="700">{FLAG_LEAD}</tspan>{lines[0][len(FLAG_LEAD):]}'
    block = (
        "  <!-- Left Content Column (x=20..716) -->\n"
        + ltext(20, 30, "#f87171", "&gt;_", hd, "700")
        + ltext(44, 30, "#ffffff", "cto-legends", hd, "700")
        + ltext(156, 30, "#fca5a5", FLAG_TAG, bd, "600")
        + "\n  <rect x=\"478\" y=\"13\" width=\"238\" height=\"22\" rx=\"3\" fill=\"#ef4444\" fill-opacity=\"0.22\" stroke=\"#f87171\" stroke-opacity=\"0.58\" stroke-width=\"1\"/>\n"
        + ltext(597, 27.6, "#ffe4e6", FLAG_PILL, lb, "700", "middle")
        + "\n"
        + "".join(ltext(20, 60 + 18 * i, "#d4d4d8", ln, bd) for i, ln in enumerate(lines))
        + "\n"
    )
    s = path.read_text(encoding="utf-8")
    s = re.sub(r"  <!-- Left Content Column.*?(?=  <!-- Right Tucked)", lambda _: block, s, count=1, flags=re.S)
    path.write_text(s, encoding="utf-8")

    # Handoff label: same voice as "the ecosystem" heading, title tier; 24px above, 16px below (README <p> margin).
    t = u("title", K_WIDE)
    label = (ltext(4, 0, "#ef4444", "&gt;_", t, "700") + ltext(24, 0, "#ffffff", "agent handoff", t, "700")
             + ltext(24 + 13 * t * MONO_EM + 12, 0, "#a1a1aa", HANDOFF_NOTE, bd))
    (cards / "cto-legends-handoff-label.svg").write_text(svg(f"0 {-9 - 24 / K_WIDE:.2f} 886 {9 + 24 / K_WIDE + 3.5:.2f}", label), encoding="utf-8")

    b = FLAG_FOOT_H - 0.5
    fill = "#0c0507"
    divider = 'stroke="#ef4444" stroke-opacity="0.30" stroke-width="1"'
    segs = [
        ("cto-legends-foot-readme", 'GITHUB README  <tspan fill="#f87171">↗</tspan>', "#ffffff"),
        ("cto-legends-foot-releases", 'RELEASES  <tspan fill="#f87171">↗</tspan>', "#ffffff"),
        ("cto-legends-foot-handoff", 'AGENT HANDOFF &amp; DOCS  <tspan fill="#f87171">↗</tspan>', "#ffffff"),
    ]
    for i, (fname, label, color) in enumerate(segs):
        x0, x1 = FLAG_B[i], FLAG_B[i + 1]
        body = ""
        if i == 0:
            body += f'  <path d="M1 0 V{b - 4} A4 4 0 0 0 5 {b} H{x1} V0 Z" fill="{fill}"/>\n'
            body += f'  <path d="M1 0 V{b - 4} A4 4 0 0 0 5 {b} H{x1}" fill="none" {RED}/>\n'
        elif i == 2:
            body += f'  <path d="M{x0} 0 V{b} H881 A4 4 0 0 0 885 {b - 4} V0 Z" fill="{fill}"/>\n'
            body += f'  <path d="M{x0} {b} H881 A4 4 0 0 0 885 {b - 4} V0" fill="none" {RED}/>\n'
        else:
            body += f'  <rect x="{x0}" y="0" width="{x1 - x0:g}" height="{b}" fill="{fill}"/>\n'
            body += f'  <line x1="{x0}" y1="{b}" x2="{x1}" y2="{b}" {RED}/>\n'
        if i > 0:
            body += f'  <line x1="{x0 + 0.5:g}" y1="0" x2="{x0 + 0.5:g}" y2="{b}" {divider}/>\n'
        body += f'  <line x1="{max(x0, 1.5):g}" y1="0.5" x2="{min(x1, 884.5):g}" y2="0.5" {divider}/>\n'
        cx = ((1 if i == 0 else x0) + (885 if i == 2 else x1)) / 2
        body += text(cx, 20.4, color, label, size=u("label", K_WIDE), weight="700")
        (cards / f"{fname}.svg").write_text(svg(f"{x0:.3f} 0 {x1 - x0:.3f} {FLAG_FOOT_H}", body), encoding="utf-8")


def img(href: str, src: str, width: str, alt: str) -> str:
    return f'<a href="{href}"><img src="assets/cards/{REV}/{src}" width="{width}" align="top" alt="{alt}" /></a>'


def readme_block(alts: dict, widths: dict) -> str:
    flag_alt = f"cto-legends: {FLAG_LEAD} {FLAG_BODY}"
    out = ['<p align="left">', "  " + img(f"{GH}/cto-legends", "cto-legends-flagship.svg?v=2", "100%", flag_alt)]
    links = [
        (f"{GH}/cto-legends#readme", "cto-legends-foot-readme", "cto-legends GitHub readme"),
        (f"{GH}/cto-legends/releases", "cto-legends-foot-releases", "cto-legends releases"),
        (SITE, "cto-legends-foot-handoff", "cto-legends agent handoff and docs"),
    ]
    out.append("  " + "<!--\n  -->".join(
        img(u, f"{f}.svg?v=2", f"{(FLAG_B[i + 1] - FLAG_B[i]) / FLAG_W * 100:.2f}%", a)
        for i, (u, f, a) in enumerate(links)) + "<!--\n  -->"
        + f'<img src="assets/cards/{REV}/cto-legends-handoff-label.svg" width="100%" align="top" alt="agent handoff: {HANDOFF_NOTE[3:]}" />')
    out += [
        "</p>",
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
            img(f"{GH}/{n}", f"{n}.svg?v=7", f"{COL_PCT}%", f"{n}: {COPY[n][2]}") for n in trio))
        btns = []
        for n in trio:
            lw, rw = widths[n]
            btns.append(img(f"{SITE}/modules/{n}", f"{n}-spec.svg?v=4", lw, f"{n} engineering spec"))
            btns.append(img(f"{GH}/{n}#readme", f"{n}-repo.svg?v=4", rw, f"{n} GitHub readme"))
        out.append("  " + "<!--\n  -->".join(btns))
    out.append("</p>")
    return "\n".join(out)


def main() -> int:
    readme = readme_path.read_text(encoding="utf-8")
    alts = {}
    if set(COPY) != set(MODULES):
        raise SystemExit(f"FAIL: COPY and MODULES differ: {set(COPY) ^ set(MODULES)}")
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
