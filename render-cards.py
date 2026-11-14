#!/usr/bin/env python3
"""Render every text-bearing image on the avalonreset profile README.

Page story, one job per element:
  banner      what cto-legends is (one line) and what you get
  community   the community bar (tagline locked, owner-written)
  overview    why it matters and how it works, in three steps
  flagship    start here: the one package you install
  handoff     the copyable agent prompt (the only >_ on the page: it is a paste-into-terminal action)
  modules     heading, separator, then the 21 module cards

All text is outlined from IBM Plex Mono by typeset.py, so metrics are identical on every OS
and wrap() is exact. Module cards are a body image plus a footer cut into separate link
images; align="top" removes the inline-image baseline gap so the pieces join with no seam.

Idempotent: rerun after editing copy. Rewrites README between HEADER:* and CARDS:* markers.
"""
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from typeset import EM, Typesetter, width  # noqa: E402

root = Path(__file__).resolve().parent
# Design revision folder. GitHub caches raw images by path and ignores ?v= bumps, so every
# visual change ships under a new folder: bump REV, git mv the files, rerun.
REV = "r5"
cards = root / "assets" / "cards" / REV
readme_path = root / "README.md"
BANNER_TEMPLATE = root / "assets" / "banner.svg"  # original art: defs, animation, rail

GH = "https://github.com/avalonreset"
SITE = "https://cto-legends.com"
SKOOL = "https://www.skool.com/ai-marketing-hub-pro"

# Type scale, in rendered px at GitHub's ~829px README width. Four sizes only:
#   head 14 (section headings) / title 12 (card titles) / body 11 (prose) / label 9 (chips, meta, buttons)
# lowercase label = information; UPPERCASE letter-spaced label = clickable action; an arrow = a link.
TYPE = {"head": 14, "title": 12, "body": 11, "label": 9}
K_CARD = 829 * 0.3333 / 303  # px per SVG unit, module cards
K_WIDE = 829 / 886           # px per SVG unit, full-width panels


def u(role: str, k: float) -> float:
    return round(TYPE[role] / k, 2)


def wrap(text: str, size: float, width_u: float, lines: int) -> list:
    """Greedy wrap at spaces only (never mid-word or at hyphens); fail loudly on overflow.
    A line never ends on the first word of a new sentence: that word moves down with the rest."""
    cap = int(width_u / (size * EM) + 1e-6)
    out, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > cap:
            words = cur.split(" ")
            if len(words) > 2 and words[-2][-1] in ".!?:" and len(words[-1]) + 1 + len(w) <= cap:
                out.append(" ".join(words[:-1]))
                cur = f"{words[-1]} {w}"
                continue
            out.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    out.append(cur)
    if len(out) > lines:
        raise SystemExit(f"FAIL: copy needs {len(out)} lines (max {lines}, {cap} chars): {text}")
    return out


# ---------------------------------------------------------------- copy

# Owner vision (vault): the human is the controller, the agents do the operating; the only thing
# that ever mattered was business intelligence; working slogan "fractional cto heaven".
BANNER_L1 = "the human is the controller. the agents do the operating."
BANNER_L2 = "stop being your computer's assistant."
BANNER_PILL = "fractional cto heaven"
BANNER_ALT = ("cto-legends: the human is the controller, the agents do the operating. "
              "Stop being your computer's assistant. fractional cto heaven.")

BAR_TAGLINE = "&lt;--- carefully designed to voltron into the world&apos;s greatest agentic digital marketing system"  # locked

OVERVIEW_LEAD = "If your AI hands the steps back to you, nothing was delegated. You just got one more thing to babysit."
OVERVIEW_REST = "cto-legends is free software that gives your agents real hands, so your only job is to say what you want."
STEPS = [
    ("01", "you talk", 'Say it the way you would to your CTO: "move my DNS to Cloudflare" or "why did my Stripe fees jump?"'),
    ("02", "the agents operate", "They find the file, install the right module, run the command and check the result. You touch nothing."),
    ("03", "you decide", "You get back what happened and what it means, not a to-do list. That is business intelligence."),
]
AGENTS = ["claude", "codex", "gemini", "grok", "muse", "deepseek", "qwen", "glm"]

FLAG_TITLE = "start here"
FLAG_TAG = "// the one package you install"
FLAG_LEAD = "Install cto-legends once and your agent can reach every module below. That is the whole setup."
FLAG_BODY = ("The 21 modules below stay off your machine until a task needs one. Then your agent installs "
             "it from a pinned, checksum-verified release, in its own environment, and checks it is ready.")

HANDOFF_NOTE = "// paste this into claude code, codex or any coding agent and it does the setup"
HANDOFF = f"Set up {GH}/cto-legends and check which modules apply to this workspace."

MODULES_HEAD = "the modules"
MODULES_NOTE = "21 modules · each one installs only when a task needs it"

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

MODULES = [
    "legends-empire", "legends-astro", "legends-hetzner",
    "legends-coolify", "legends-cloudflare", "legends-stripe",
    "legends-buzz", "legends-gohighlevel", "legends-github",
    "legends-jev", "legends-geogrid", "legends-dataforseo",
    "legends-firecrawl", "legends-grant", "legends-obs",
    "legends-captions", "legends-youtube", "legends-yt-dlp",
    "legends-stable-audio-3", "legends-hyperyap", "legends-ambient-intelligence",
]

# ---------------------------------------------------------------- geometry

# Column viewBox x-offsets give flush outer edges and symmetric gutters.
COL_W = 303
COL_MIN_X = (0, (292 - COL_W) / 2, 292 - COL_W)
COL_PCT = 33.33
BODY_TOP, BODY_BOTTOM = -16, 110  # top margin separates card rows; bottom is the seam
FOOT_H = 30
SPLIT = 146  # card spans x=1..291
BORDER = 'stroke="#ffffff" stroke-opacity="0.09" stroke-width="1"'
HAIR = 'stroke="#ffffff" stroke-opacity="0.07" stroke-width="1"'
CHIP = 'fill="#090a0e" stroke="#ffffff" stroke-opacity="0.15" stroke-width="1"'

FLAG_W, FLAG_BOTTOM, FLAG_FOOT_H = 886, 118, 32
FLAG_B = [0, FLAG_W / 3, FLAG_W * 2 / 3, FLAG_W]  # equal thirds
RED = 'stroke="#ef4444" stroke-opacity="0.68" stroke-width="1"'
GAP16, GAP32 = 16 / K_WIDE, 32 / K_WIDE  # spacing system, in wide-panel units
CAP = 0.698  # Plex Mono cap height per em


def svg(vb: str, body: str, t: Typesetter = None) -> str:
    defs = t.defs() if t else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="100%">\n{defs}{body}</svg>\n'


def button(t: Typesetter, cx: float, y: float, fill: str, label: str, size: float, weight: str = "600") -> str:
    """Centered action label; UPPERCASE gets 0.1em tracking."""
    plain = re.sub(r"<[^>]+>|&\w+;", "", label)
    spacing = size * 0.1 if plain.isupper() else 0.0
    return t.run(cx, y, size, label, fill, weight, "middle", spacing)


# ---------------------------------------------------------------- banner

def render_banner() -> None:
    src = BANNER_TEMPLATE.read_text(encoding="utf-8")
    head = src[:src.index("  <!-- Live Status Badge")]
    rail = src[src.index("  <!-- Divider Rail Base"):src.index("  <!-- Subtitle Lines")]
    t = Typesetter()

    # One 50u frame: title and rail start at x=50, rail ends at x=1150. The slogan tucks into the
    # top-right corner (cap top y=50) and the site link into the bottom-right (baseline y=270).
    # No pill borders: a glowing dot, then text, like cto-legends.com.
    FRAME_R, FRAME_T, FRAME_B = 1150, 50, 270
    sz = 18
    base = FRAME_T + sz * CAP
    tx = FRAME_R - width(BANNER_PILL, sz)
    cx, cy = tx - 15, base - sz * CAP / 2
    head = re.sub(r"transform-origin: [\d.]+px [\d.]+px", f"transform-origin: {cx:.2f}px {cy:.2f}px", head)
    pill = (
        "  <!-- Slogan, tucked top right -->\n"
        f'  <circle cx="{cx:.2f}" cy="{cy:.2f}" r="4.5" fill="#ff0000" class="beacon" />\n'
        + t.run(tx, base, sz, BANNER_PILL, "#ffffff", "600")
    )
    # Title keeps the original Legends wordmark glyphs from the template, not outlined Plex Bold.
    title = src[src.index("  <!-- Title: cto-legends"):src.index("  <!-- Divider Rail Base")].rstrip() + "\n"
    subs = ("  <!-- What it is / what you get -->\n"
            + t.run(50, 195, 28, BANNER_L1, "#ffffff", "500")
            + t.run(50, 245, 28, BANNER_L2, "#a1a1aa", "400"))
    l2_end = 50 + width(BANNER_L2, 28)
    cs = 18.5
    ax = FRAME_R - 9.5  # arrow is 9.5u wide, ends on the frame
    cta_x = ax - 10 - width("cto-legends.com", cs)
    if l2_end + 22 > cta_x - 24:
        raise SystemExit("FAIL: banner line 2 runs into the site link")
    cursor = f'  <rect x="{l2_end + 8:.2f}" y="224" width="14" height="24" fill="#ff0000" class="cursor" />\n'
    ay = FRAME_B - 1
    cta = (
        "  <!-- Site link, tucked bottom right -->\n"
        + t.run(cta_x, FRAME_B, cs, "cto-legends.com", "#ffffff", "500")
        + f'  <path d="M{ax:.2f} {ay:.2f} L{ax + 9.5:.2f} {ay - 9.5:.2f} M{ax + 2.5:.2f} {ay - 9.5:.2f} H{ax + 9.5:.2f} V{ay - 2.5:.2f}" '
        'stroke="#ff2738" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" fill="none" />\n'
    )
    out = head + t.defs() + pill + "\n" + title + "\n" + rail + subs + cursor + cta + "</svg>\n"
    (cards / "banner.svg").write_text(out, encoding="utf-8")


# ---------------------------------------------------------------- community bar (tagline locked)

def render_bar() -> None:
    t = Typesetter()
    lb = u("label", K_WIDE)
    c_w = width("community", lb) + 24
    p_txt = '<tspan fill="#ffffff">ai-marketing-hub-pro</tspan><tspan fill="#f87171"> ↗</tspan>'
    p_w = width(p_txt, lb) + 28
    body = (
        f'  <rect x="1" y="3" width="{c_w:.2f}" height="24" rx="3" fill="#050507" stroke="#ffffff" stroke-opacity="0.15" stroke-width="1"/>\n'
        + t.run(1 + c_w / 2, 18.4, lb, "community", "#a1a1aa", "600", "middle")
        + f'  <rect x="{c_w + 3:.2f}" y="3" width="{p_w:.2f}" height="24" rx="3" fill="#1f070b" {RED}/>\n'
        + f'  <rect x="{c_w + 3:.2f}" y="3" width="2.5" height="24" rx="1" fill="#ef4444"/>\n'
        + t.run(c_w + 3 + 1.25 + p_w / 2, 18.4, lb, p_txt, "#ffffff", "700", "middle")
        + t.run(c_w + 3 + p_w + 12, 18.4, lb, BAR_TAGLINE, "#ffffff", "600")
    )
    (cards / "bar-community.svg").write_text(svg("0 -14.6 886 42.1", body, t), encoding="utf-8")


# ---------------------------------------------------------------- overview

def render_overview() -> str:
    t = Typesetter()
    bd, ti, lb = u("body", K_WIDE), u("title", K_WIDE), u("label", K_WIDE)
    x0, x1 = 18, 868
    body = ""
    y = 2 + 14 + bd * CAP  # 14u inner top pad to cap height
    # Claim on line 1 (white bold), answer on line 2: one sentence each, no widows.
    for ln, fill, wt in ((OVERVIEW_LEAD, "#ffffff", "700"), (OVERVIEW_REST, "#d4d4d8", "400")):
        wrap(ln, bd, x1 - x0, 1)
        body += t.run(x0, y, bd, ln, fill, wt)
        y += 18
    div1 = y - 18 + 15
    body += f'  <line x1="{x0}" y1="{div1:.2f}" x2="{x1}" y2="{div1:.2f}" {HAIR}/>\n'

    gap = 28
    col = (x1 - x0 - 2 * gap) / 3
    top = div1 + 15 + ti * CAP
    deepest = 0
    for i, (num, head, text) in enumerate(STEPS):
        cx = x0 + i * (col + gap)
        body += t.run(cx, top, lb, num, "#f87171", "700")
        body += t.run(cx + width(num, lb) + 9, top, ti, head, "#ffffff", "700")
        lines = wrap(text, bd, col, 3)
        for j, ln in enumerate(lines):
            body += t.run(cx, top + 20 + 17 * j, bd, ln, "#a1a1aa")
        deepest = max(deepest, top + 20 + 17 * (len(lines) - 1))
        if i:
            body += f'  <line x1="{cx - gap / 2:.2f}" y1="{top - ti * CAP:.2f}" x2="{cx - gap / 2:.2f}" y2="{deepest + 4:.2f}" {HAIR}/>\n'
    div2 = deepest + 15
    body += f'  <line x1="{x0}" y1="{div2:.2f}" x2="{x1}" y2="{div2:.2f}" {HAIR}/>\n'

    chip_top = div2 + 10
    base = chip_top + 13
    lab = "vendor agnostic:"
    body += t.run(x0, base, lb, lab, "#a1a1aa", "600")
    cx = x0 + width(lab, lb) + 10
    for a in AGENTS:
        w = width(a, lb) + 18
        body += f'  <rect x="{cx:.2f}" y="{chip_top:.2f}" width="{w:.2f}" height="19" rx="3" {CHIP}/>\n'
        body += t.run(cx + w / 2, base, lb, a, "#e4e4e7", "600", "middle")
        cx += w + 6
    body += t.run(x1, base, lb, "zero context bloat", "#f87171", "600", "end")
    panel_b = chip_top + 19 + 10
    frame = f'  <rect x="1" y="2" width="884" height="{panel_b - 2:.2f}" rx="4" fill="#000000" stroke="#ffffff" stroke-opacity="0.10" stroke-width="1"/>\n'
    # 32px to the flagship: 16px here + the 16px margin of the README <p> that holds the cards.
    vb = f"0 {-GAP16 + 2:.2f} 886 {panel_b + GAP16 + GAP16 - 2:.2f}"
    (cards / "overview-panel.svg").write_text(svg(vb, frame + body, t), encoding="utf-8")
    steps = " ".join(f"{n}. {h}: {x}" for n, h, x in STEPS)
    return f"{OVERVIEW_LEAD} {OVERVIEW_REST} {steps}"


# ---------------------------------------------------------------- module cards

def render_module(name: str, col: int) -> tuple:
    m = COL_MIN_X[col]
    edge = f"M1 {BODY_BOTTOM} V6.5 A4 4 0 0 1 5 2.5 H287 A4 4 0 0 1 291 6.5 V{BODY_BOTTOM}"
    frame = (
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
    t = Typesetter()
    ti, lb, bd = u("title", K_CARD), u("label", K_CARD), u("body", K_CARD)
    body = t.run(14, 25, ti, name, "#ffffff", "700")
    body += t.run(14, 40, lb, f"{cat} · {lic}", "#a1a1aa", "600")
    for i, line in enumerate(wrap(desc, bd, 278 - 14, 3)):
        body += t.run(14, 60 + 17 * i, bd, line, "#a1a1aa")
    (cards / f"{name}.svg").write_text(
        svg(f"{m:g} {BODY_TOP} {COL_W} {BODY_BOTTOM - BODY_TOP}", frame + body, t), encoding="utf-8")

    b = FOOT_H - 0.5
    left_w, right_w = SPLIT - m, m + COL_W - SPLIT
    tl, tr = Typesetter(), Typesetter()
    left = (
        f'  <path d="M1 0 V{b - 4} A4 4 0 0 0 5 {b} H{SPLIT} V0 Z" fill="#000000"/>\n'
        f'  <path d="M1 0 V{b - 4} A4 4 0 0 0 5 {b} H{SPLIT}" fill="none" {BORDER}/>\n'
        f'  <line x1="14" y1="0.5" x2="{SPLIT}" y2="0.5" {HAIR}/>\n'
        + button(tl, (1 + SPLIT) / 2, 18.6, "#f87171", "ENGINEERING SPEC →", lb)
    )
    right = (
        f'  <path d="M{SPLIT} 0 V{b} H287 A4 4 0 0 0 291 {b - 4} V0 Z" fill="#000000"/>\n'
        f'  <path d="M{SPLIT} {b} H287 A4 4 0 0 0 291 {b - 4} V0" fill="none" {BORDER}/>\n'
        f'  <line x1="{SPLIT}" y1="0.5" x2="278" y2="0.5" {HAIR}/>\n'
        f'  <line x1="{SPLIT + 0.5}" y1="9" x2="{SPLIT + 0.5}" y2="21" {HAIR}/>\n'
        + button(tr, (SPLIT + 291) / 2, 18.6, "#d4d4d8", "GITHUB README ↗", lb)
    )
    (cards / f"{name}-spec.svg").write_text(svg(f"{m:g} 0 {left_w:g} {FOOT_H}", left, tl), encoding="utf-8")
    (cards / f"{name}-repo.svg").write_text(svg(f"{SPLIT} 0 {right_w:g} {FOOT_H}", right, tr), encoding="utf-8")
    return f"{left_w / COL_W * COL_PCT:.3f}%", f"{right_w / COL_W * COL_PCT:.3f}%"


# ---------------------------------------------------------------- flagship, handoff, modules heading

def render_flagship() -> None:
    path = cards / "cto-legends-flagship.svg"
    s = path.read_text(encoding="utf-8")
    t = Typesetter()
    hd, bd = u("head", K_WIDE), u("body", K_WIDE)
    lines = wrap(FLAG_LEAD + " " + FLAG_BODY, bd, 716 - 20, 3)
    assert lines[0].startswith(FLAG_LEAD), "lead must open line 1"
    lines[0] = f'<tspan fill="#ffffff" font-weight="700">{FLAG_LEAD}</tspan>{lines[0][len(FLAG_LEAD):]}'
    runs = (
        t.run(20, 30, hd, FLAG_TITLE, "#ffffff", "700")
        + t.run(20 + width(FLAG_TITLE, hd) + 12, 30, bd, FLAG_TAG, "#fca5a5", "600")
        + "".join(t.run(20, 60 + 18 * i, bd, ln, "#d4d4d8") for i, ln in enumerate(lines))
    )
    block = "  <!-- Left Content Column (x=20..716) -->\n" + t.defs() + runs + "\n"
    s, n = re.subn(r"  <!-- Left Content Column.*?(?=  <!-- Right Tucked)", lambda _: block, s, count=1, flags=re.S)
    if n != 1:
        raise SystemExit("FAIL: flagship SVG markers missing")
    # Portrait: full bleed into the card's right edge, top border to footer seam, no frame.
    # Clipped to the card's rounded top-right corner; a 20u gutter separates it from the copy.
    href = re.search(r'<image [^>]*href="([^"]+)"', s).group(1)
    px0 = 716 + 20
    edge = f"M{px0} 2 H881 A4 4 0 0 1 885 6 V{FLAG_BOTTOM}"
    s = re.sub(r'<clipPath id="babe-clip">.*?</clipPath>',
               f'<clipPath id="babe-clip"><path d="{edge} H{px0} Z"/></clipPath>', s, count=1, flags=re.S)
    portrait = (
        "  <!-- Right Tucked Operator Portrait (full bleed) -->\n"
        f'  <image x="{px0}" y="2" width="{885 - px0}" height="{FLAG_BOTTOM - 2}" clip-path="url(#babe-clip)" '
        f'preserveAspectRatio="xMidYMid slice" href="{href}"/>\n'
        f'  <path d="{edge}" fill="none" {RED}/>\n'
    )
    s = re.sub(r"  <!-- Right Tucked.*?(?=</svg>)", lambda _: portrait, s, count=1, flags=re.S)
    assert max(width(re.sub(r"<[^>]+>", "", ln), bd) for ln in lines) + 20 <= px0 - 20 + 1e-6
    path.write_text(s, encoding="utf-8")

    b = FLAG_FOOT_H - 0.5
    fill = "#0c0507"
    divider = 'stroke="#ef4444" stroke-opacity="0.30" stroke-width="1"'
    segs = [
        ("cto-legends-foot-readme", 'GITHUB README  <tspan fill="#f87171">↗</tspan>'),
        ("cto-legends-foot-releases", 'RELEASES  <tspan fill="#f87171">↗</tspan>'),
        ("cto-legends-foot-handoff", 'DOCS &amp; AGENT HANDOFF  <tspan fill="#f87171">↗</tspan>'),
    ]
    for i, (fname, label) in enumerate(segs):
        x0, x1 = FLAG_B[i], FLAG_B[i + 1]
        ft = Typesetter()
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
        body += button(ft, cx, 20.4, "#ffffff", label, u("label", K_WIDE), "700")
        (cards / f"{fname}.svg").write_text(svg(f"{x0:.3f} 0 {x1 - x0:.3f} {FLAG_FOOT_H}", body, ft), encoding="utf-8")

    # Handoff label: 24px above (from the flagship footer), 16px below (README <p> margin).
    t = Typesetter()
    ti = u("title", K_WIDE)
    label = (t.run(2, 0, ti, "&gt;_", "#ef4444", "700")
             + t.run(2 + width("&gt;_", ti) + 8, 0, ti, "agent handoff", "#ffffff", "700")
             + t.run(2 + width("&gt;_", ti) + 8 + width("agent handoff", ti) + 12, 0, bd, HANDOFF_NOTE, "#a1a1aa"))
    top = ti * CAP + 24 / K_WIDE
    (cards / "cto-legends-handoff-label.svg").write_text(svg(f"0 {-top:.2f} 886 {top + 3.5:.2f}", label, t), encoding="utf-8")


def render_modules_heading() -> None:
    # 32px section gap above: 16px come from the code block's margin, 16px live here.
    t = Typesetter()
    hd, lb = u("head", K_WIDE), u("label", K_WIDE)
    body = (t.run(2, 0, hd, MODULES_HEAD, "#ffffff", "700")
            + t.run(884, 0, lb, MODULES_NOTE, "#a1a1aa", "400", "end"))
    top = hd * CAP + GAP16
    (cards / "modules-heading.svg").write_text(svg(f"0 {-top:.2f} 886 {top + 4:.2f}", body, t), encoding="utf-8")


# ---------------------------------------------------------------- README

def img(href: str, src: str, width_: str, alt: str) -> str:
    tag = f'<img src="assets/cards/{REV}/{src}" width="{width_}" align="top" alt="{alt}" />'
    return f'<a href="{href}">{tag}</a>' if href else tag


def header_block(overview_alt: str) -> str:
    bar_alt = "community: ai-marketing-hub-pro - carefully designed to voltron into the world's greatest agentic digital marketing system"
    parts = [
        img(SITE, "banner.svg", "100%", BANNER_ALT),
        img(SKOOL, "bar-community.svg", "100%", bar_alt),
        img(f"{GH}/cto-legends", "overview-panel.svg", "100%", f"how cto-legends works: {overview_alt}"),
    ]
    return '<p align="left">\n  ' + "<!--\n  -->".join(parts) + "\n</p>"


def cards_block(widths: dict) -> str:
    flag_alt = f"start here: {FLAG_LEAD} {FLAG_BODY}"
    out = ['<p align="left">', "  " + img(f"{GH}/cto-legends", "cto-legends-flagship.svg", "100%", flag_alt)]
    links = [
        (f"{GH}/cto-legends#readme", "cto-legends-foot-readme", "cto-legends GitHub readme"),
        (f"{GH}/cto-legends/releases", "cto-legends-foot-releases", "cto-legends releases"),
        (SITE, "cto-legends-foot-handoff", "cto-legends docs and agent handoff"),
    ]
    out.append("  " + "<!--\n  -->".join(
        img(h, f"{f}.svg", f"{(FLAG_B[i + 1] - FLAG_B[i]) / FLAG_W * 100:.2f}%", a)
        for i, (h, f, a) in enumerate(links)) + "<!--\n  -->"
        + img("", "cto-legends-handoff-label.svg", "100%", f"agent handoff: {HANDOFF_NOTE[3:]}"))
    out += ["</p>", "", "```text", HANDOFF, "```", "", '<p align="left">']
    out.append("  " + img("", "modules-heading.svg", "100%", f"{MODULES_HEAD}: {MODULES_NOTE}") + "<!--\n  -->"
               + img(f"{GH}/cto-legends/blob/main/LICENSE", "ecosystem-separator.svg", "100%", "license: open source"))
    for r in range(0, len(MODULES), 3):
        trio = MODULES[r:r + 3]
        out.append("  " + "<!--\n  -->".join(
            img(f"{GH}/{n}", f"{n}.svg", f"{COL_PCT}%", f"{n}: {COPY[n][2]}") for n in trio))
        btns = []
        for n in trio:
            lw, rw = widths[n]
            btns.append(img(f"{SITE}/modules/{n}", f"{n}-spec.svg", lw, f"{n} engineering spec"))
            btns.append(img(f"{GH}/{n}#readme", f"{n}-repo.svg", rw, f"{n} GitHub readme"))
        out.append("  " + "<!--\n  -->".join(btns))
    out.append("</p>")
    return "\n".join(out)


def splice(readme: str, name: str, block: str) -> str:
    start, end = f"<!-- {name}:START -->", f"<!-- {name}:END -->"
    if start not in readme or end not in readme:
        raise SystemExit(f"FAIL: {name} markers missing from README.md")
    return re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: f"{start}\n{block}\n{end}", readme, flags=re.S)


def main() -> int:
    if set(COPY) != set(MODULES):
        raise SystemExit(f"FAIL: COPY and MODULES differ: {set(COPY) ^ set(MODULES)}")
    render_banner()
    render_bar()
    overview_alt = render_overview()
    widths = {n: render_module(n, i % 3) for i, n in enumerate(MODULES)}
    render_flagship()
    render_modules_heading()
    readme = readme_path.read_text(encoding="utf-8")
    readme = splice(readme, "HEADER", header_block(overview_alt))
    readme = splice(readme, "CARDS", cards_block(widths))
    readme_path.write_text(readme, encoding="utf-8")
    print(f"Rendered banner, bar, overview, flagship, heading and {len(MODULES)} module cards (outlined IBM Plex Mono).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
