#!/usr/bin/env python3
"""Render every text-bearing image on the avalonreset profile README.

Page story, one job per element:
  banner      what cto-legends is (one line) and what you get
  community   the community bar (tagline locked, owner-written)
  overview    why it matters and how it works, in three steps
  flagship    start here: the one package you install
  handoff     the copyable agent prompt (the only >_ on the page: it is a paste-into-terminal action)
  modules     heading, separator, then the on-demand module cards

All text is outlined from the Legends Font by typeset.py, so metrics are identical on every OS
and wrap() is exact. Module cards are a body image plus a footer cut into separate link
images; align="top" removes the inline-image baseline gap so the pieces join with no seam.

Idempotent: rerun after editing copy. Rewrites README between HEADER:* and CARDS:* markers.
"""
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from typeset import CAP, EM, FONT, Typesetter, width  # noqa: E402

root = Path(__file__).resolve().parent
# Design revision folder. GitHub caches raw images by path and ignores ?v= bumps, so every
# visual change ships under a new folder: bump REV, git mv the files, rerun.
REV = "r32"
cards = root / "assets" / "cards" / REV
readme_path = root / "README.md"
BANNER_TEMPLATE = root / "assets" / "banner.svg"  # original art: defs, animation, rail

GH = "https://github.com/avalonreset"
STAR_LIST = "https://github.com/stars/avalonreset/lists/cto-legends"
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

# Aligned with cto-legends.com hero: fractional cto heaven (top-right beacon),
# core positioning on line 1, mission statement on line 2.
BANNER_L1 = "sovereign business infrastructure & operational ontology"
BANNER_L2 = "a crusade against dehumanization by tech entropy"
BANNER_PILL = "fractional cto heaven"
BANNER_ALT = ("cto-legends by Avalon Reset: fractional cto heaven. "
              "Sovereign business infrastructure & operational ontology. "
              "A crusade against dehumanization by tech entropy.")

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
FLAG_BODY = ("Every module below stays off your machine until a task needs one. Then your agent installs "
             "it from a pinned, checksum-verified release, in its own environment, and checks it is ready.")

HANDOFF_NOTE = "// vendor-agnostic: paste this into any AI coding agent and it does the setup"
HANDOFF = f"Set up {GH}/cto-legends and check which modules apply to this workspace."

MODULES_HEAD = "the modules"
MODULES_NOTE = "each module installs only when a task needs it"

# Module card copy: (category, license, one outcome-first sentence, 3 lines max).
COPY = {
    "legends-empire": ("foundation", "mit", "Turn your Markdown vault into agent memory with SHA-256 integrity locks and crash-safe writes."),
    "legends-astro": ("foundation", "mit", "Start greenfield Astro sites, migrate frameworks, publish posts with 301s, and verify dist/."),
    "legends-a2ui": ("foundation", "mit", "Validate A2UI v1.0 JSON, upgrade legacy payloads, project CLI data to cards, and preview offline."),
    "legends-hetzner": ("infrastructure", "mit", "Check live Hetzner stock in Germany and Finland, size servers for cost, and preflight every build."),
    "legends-coolify": ("infrastructure", "mit", "Audit your Coolify servers read-only: containers, deploy queues, env keys, and backups."),
    "legends-cloudflare": ("infrastructure", "mit", "Change Cloudflare DNS without surprises: preview each edit, keep proxy settings, confirm it is live."),
    "legends-stripe": ("infrastructure", "mit", "Keep Stripe in sync: match Test and Live prices, reconcile fees to the cent, and verify webhooks."),
    "legends-buzz": ("infrastructure", "mit", "Run self-hosted Block Buzz Nostr relays from the command line, with no MCP daemon to babysit."),
    "legends-gohighlevel": ("infrastructure", "mit", "Run GoHighLevel agencies at scale: batch-clone snapshots, X-ray workflows, lock down permissions."),
    "legends-github": ("intelligence", "mit", "Keep repos launch-ready: health audits, verified releases, and topics tuned to search demand."),
    "legends-jev": ("infrastructure", "mit", "Give your agent eyes: hosted OCR, exact pixel coordinates, and storefront sign checks."),
    "legends-geogrid": ("intelligence", "mit", "Map local Google Maps rankings on a 30-deep circular honeycomb grid with vector PDF reports."),
    "legends-dataforseo": ("intelligence", "mit", "Pull Google SERPs, Maps listings, and keyword volume from DataForSEO, cost previewed first."),
    "legends-firecrawl": ("intelligence", "mit", "Turn JavaScript-heavy sites into clean Markdown with preview-first, bounded Firecrawl crawls."),
    "legends-grant": ("intelligence", "mit", "Find grants across 56 US jurisdictions and check every eligibility rule word for word."),
    "legends-obs": ("studio", "mit", "Drive OBS Studio from your agent: scene switching, encoder checks, profile backups, and test clips."),
    "legends-captions": ("studio", "mit", "Word-by-word subtitles timed by forced alignment, with tech terms and acronyms spelled right."),
    "legends-capcut": ("studio", "mit", "Compile CapCut Desktop timelines, surgically patch scenes, render storyboards, and audit pacing."),
    "legends-youtube": ("studio", "mit", "Run YouTube channels, pull paced yt-dlp video archives, cut clips, and freeze private drafts."),
    "legends-temporal": ("infrastructure", "mit", "Schedule durable Temporal crons, delayed timers, and module jobs across split worker queues."),
    "legends-stable-audio-3": ("studio", "apache-2.0", "Make custom instrumental music on your own GPU and blend it into seamless multi-hour mixes."),
    "legends-hyperyap": ("studio", "agpl-3.0", "Push-to-talk dictation that runs offline on your GPU and types into any Windows, macOS, or Linux app."),
    "legends-ambient-intelligence": ("studio", "mit", "Turn voice recorder and meeting audio into structured Markdown notes, entirely offline."),
}

MODULES = [
    # Canonical business-owner storyline order (synced with cto-legends catalog.json & cto-legends.com):
    # 1. foundation: agent memory, your own cloud server, and a self-hosted deploy platform
    "legends-empire", "legends-hetzner", "legends-coolify",
    # 2. go live & capture leads: point DNS, launch or convert to Astro, wire up CRM pipelines
    "legends-cloudflare", "legends-astro", "legends-gohighlevel",
    # 3. collect revenue & get found: Stripe billing, Google/AI search demand, local Maps grids
    "legends-stripe", "legends-dataforseo", "legends-geogrid",
    # 4. market intel, capital & reach: scrape competitors/docs, find grants, grow on YouTube
    "legends-firecrawl", "legends-grant", "legends-youtube",
    # 5. video production engine: record in OBS, edit timelines in CapCut, burn word-timed captions
    "legends-obs", "legends-capcut", "legends-captions",
    # 6. audio & voice speed: custom GPU music beds, offline dictation, meeting notes
    "legends-stable-audio-3", "legends-hyperyap", "legends-ambient-intelligence",
    # 7. autonomous operations: 24/7 durable schedules, optical eyes, private ChatOps relays
    "legends-temporal", "legends-jev", "legends-buzz",
    # 8. builder & open-source tier: interactive A2UI surfaces, public GitHub shipping
    "legends-a2ui", "legends-github",
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
RED = 'stroke="#ff0000" stroke-opacity="0.68" stroke-width="1"'
GAP16, GAP32 = 16 / K_WIDE, 32 / K_WIDE  # spacing system, in wide-panel units


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
    import math
    import random

    src = BANNER_TEMPLATE.read_text(encoding="utf-8")
    # Preserve the original Legends wordmark glyphs from the template, not re-outlined.
    title = src[src.index("  <!-- Title: cto-legends"):src.index("  <!-- Divider Rail Base")].rstrip() + "\n"
    t = Typesetter()

    # One 50u frame: title and rail start at x=50, rail ends at x=1150. The slogan tucks into the
    # top-right corner (cap top y=50) and the site link into the bottom-right (baseline y=272).
    # Pure #ff0000 on #000000 / #ffffff only (no white shimmer highlights, no pink/lightened reds).
    FRAME_R, FRAME_T, FRAME_B = 1150, 50, 272
    RAIL_Y = 146
    sz = 18
    base = FRAME_T + sz * CAP
    tx = FRAME_R - width(BANNER_PILL, sz)
    cx, cy = tx - 16, base - sz * CAP / 2

    # Harmonic pure-red silk ribbons along the divider rail (ties banner to ecosystem-separator.svg).
    rng = random.Random(20261122)
    rail_x0, rail_x1 = 54.0, 1146.0
    ribbon_specs = [
        ("#4d0000", 0.75, 1.25),
        ("#990000", 0.65, 0.90),
        ("#cc0000", 0.65, 0.65),
        ("#ff0000", 0.80, 0.55),
        ("#ff0000", 0.55, 0.45),
    ]
    ribbon_css, ribbon_glow, ribbon_core = [], [], []
    for idx, (col, op, sw) in enumerate(ribbon_specs):
        P = rng.uniform(300, 480)
        raw = [rng.uniform(0.55, 1.0), rng.uniform(0.18, 0.42), rng.uniform(0.06, 0.20)]
        scale = 6.2 * rng.uniform(0.55, 0.95) / sum(raw)
        amps = [a * scale for a in raw]
        phases = [rng.uniform(0, 2 * math.pi) for _ in raw]
        pts = []
        x = rail_x0
        while x <= rail_x1 + P + 8:
            y = RAIL_Y + sum(a * math.sin(2 * math.pi * (k + 1) * (x - rail_x0) / P + ph)
                             for k, (a, ph) in enumerate(zip(amps, phases)))
            pts.append(f"{x:.1f} {y:.1f}")
            x += 6.0
        d = "M" + "L".join(pts)
        dur = rng.uniform(6.5, 11.5) * (P / 380.0)
        delay = -rng.uniform(0, dur)
        ribbon_css.append(
            f"    @keyframes drift-{idx} {{ to {{ transform: translateX(-{P:.2f}px); }} }}\n"
            f"    .rw-{idx} {{ animation: drift-{idx} {dur:.2f}s linear {delay:.2f}s infinite; }}\n"
        )
        ribbon_core.append(
            f'      <path class="rw-{idx}" d="{d}" stroke="{col}" stroke-opacity="{op:.2f}" stroke-width="{sw:.2f}" />\n'
        )
        if col in ("#cc0000", "#ff0000"):
            ribbon_glow.append(
                f'      <path class="rw-{idx}" d="{d}" stroke="#ff0000" stroke-opacity="{op * 0.38:.2f}" stroke-width="{sw * 3.6:.2f}" />\n'
            )

    # Subtle architectural grid lines in the deep upper-right field (masked cleanly around text).
    grid_lines = []
    for gx in range(560, 1181, 40):
        grid_lines.append(f'      <line x1="{gx}" y1="16" x2="{gx}" y2="132" />\n')
    for gy in (44, 84, 124):
        grid_lines.append(f'      <line x1="560" y1="{gy}" x2="1180" y2="{gy}" />\n')

    pill = (
        "  <!-- Slogan beacon, tucked top right -->\n"
        f'  <circle cx="{cx:.2f}" cy="{cy:.2f}" r="4.5" fill="none" stroke="#ff0000" stroke-width="1.3" class="beacon-ring" />\n'
        f'  <circle cx="{cx:.2f}" cy="{cy:.2f}" r="4.5" fill="#ff0000" class="beacon" />\n'
        + t.run(tx, base, sz, BANNER_PILL, "#ffffff", "600")
    )
    subs = (
        "  <!-- Positioning / Mission -->\n"
        + t.run(50, 200, 28, BANNER_L1, "#ffffff", "600")
        + t.run(50, 248, 28, BANNER_L2, "#a1a1aa", "400")
    )
    l1_end = 50 + width(BANNER_L1, 28)
    if l1_end > FRAME_R:
        raise SystemExit(f"FAIL: banner line 1 overflows right frame ({l1_end:.1f} > {FRAME_R})")
    l2_end = 50 + width(BANNER_L2, 28)
    cs = 18.5
    ax = FRAME_R - 9.5  # arrow is 9.5u wide, ends on the frame
    cta_x = ax - 10 - width("cto-legends.com", cs)
    if l2_end + 22 > cta_x - 24:
        raise SystemExit("FAIL: banner line 2 runs into the site link")
    cursor = f'  <rect x="{l2_end + 9:.2f}" y="227" width="13" height="24" fill="#ff0000" class="cursor" />\n'
    ay = FRAME_B - 1
    cta = (
        "  <!-- Site link, tucked bottom right -->\n"
        + t.run(cta_x, FRAME_B, cs, "cto-legends.com", "#ffffff", "600")
        + f'  <g class="cta-arrow"><path d="M{ax:.2f} {ay:.2f} L{ax + 9.5:.2f} {ay - 9.5:.2f} '
        f'M{ax + 2.5:.2f} {ay - 9.5:.2f} H{ax + 9.5:.2f} V{ay - 2.5:.2f}" '
        'stroke="#ff0000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none" /></g>\n'
    )

    out = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 320" width="100%" height="auto">
  <defs>
    <clipPath id="cardClip"><rect width="1200" height="320" rx="6" /></clipPath>
    <clipPath id="railClip"><rect x="54" y="{RAIL_Y - 10}" width="1092" height="20" /></clipPath>
    <clipPath id="coreClip"><rect x="50" y="{RAIL_Y - 3}" width="1100" height="6" rx="2" /></clipPath>
    <radialGradient id="titleAura" cx="265" cy="84" r="330" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#ff0000" stop-opacity="0.14" />
      <stop offset="48%" stop-color="#ff0000" stop-opacity="0.04" />
      <stop offset="100%" stop-color="#ff0000" stop-opacity="0" />
    </radialGradient>
    <radialGradient id="gridFade" cx="980" cy="70" r="340" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="1" />
      <stop offset="65%" stop-color="#ffffff" stop-opacity="0.35" />
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0" />
    </radialGradient>
    <mask id="gridMask" maskUnits="userSpaceOnUse" x="560" y="16" width="620" height="116">
      <rect x="560" y="16" width="620" height="116" fill="url(#gridFade)" />
    </mask>
    <linearGradient id="railFade" gradientUnits="userSpaceOnUse" x1="54" y1="0" x2="1146" y2="0">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0" />
      <stop offset="8%" stop-color="#ffffff" stop-opacity="0.85" />
      <stop offset="50%" stop-color="#ffffff" stop-opacity="1" />
      <stop offset="92%" stop-color="#ffffff" stop-opacity="0.85" />
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0" />
    </linearGradient>
    <mask id="railMask" maskUnits="userSpaceOnUse" x="54" y="{RAIL_Y - 10}" width="1092" height="20">
      <rect x="54" y="{RAIL_Y - 10}" width="1092" height="20" fill="url(#railFade)" />
    </mask>
    <linearGradient id="barScanGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ff0000" stop-opacity="0" />
      <stop offset="50%" stop-color="#ff0000" stop-opacity="1" />
      <stop offset="100%" stop-color="#ff0000" stop-opacity="0" />
    </linearGradient>
    <linearGradient id="pulseGrad1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ff0000" stop-opacity="0" />
      <stop offset="30%" stop-color="#ff0000" stop-opacity="0.35" />
      <stop offset="50%" stop-color="#ff0000" stop-opacity="0.95" />
      <stop offset="70%" stop-color="#ff0000" stop-opacity="0.35" />
      <stop offset="100%" stop-color="#ff0000" stop-opacity="0" />
    </linearGradient>
    <linearGradient id="pulseGrad2" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ff0000" stop-opacity="0" />
      <stop offset="35%" stop-color="#ff0000" stop-opacity="0.28" />
      <stop offset="50%" stop-color="#ff0000" stop-opacity="0.72" />
      <stop offset="65%" stop-color="#ff0000" stop-opacity="0.28" />
      <stop offset="100%" stop-color="#ff0000" stop-opacity="0" />
    </linearGradient>
    <filter id="redGlow" x="-8%" y="-160%" width="116%" height="420%">
      <feGaussianBlur stdDeviation="2.4" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <filter id="silkSoft" x="-4%" y="-90%" width="108%" height="280%">
      <feGaussianBlur stdDeviation="1.8" />
    </filter>
  </defs>
  <style>
    @keyframes aura-breathe {{
      0%, 100% {{ opacity: 0.65; }}
      50% {{ opacity: 1; }}
    }}
    @keyframes bar-breathe {{
      0%, 100% {{ opacity: 0.72; }}
      50% {{ opacity: 1; }}
    }}
    @keyframes bar-scan {{
      0% {{ transform: translateY(-140px); }}
      100% {{ transform: translateY(340px); }}
    }}
    @keyframes beacon-pulse {{
      0%, 100% {{ transform: scale(1); opacity: 0.75; }}
      50% {{ transform: scale(1.22); opacity: 1; filter: drop-shadow(0 0 6px #ff0000); }}
    }}
    @keyframes beacon-ring {{
      0% {{ transform: scale(1); opacity: 0.75; }}
      80%, 100% {{ transform: scale(2.8); opacity: 0; }}
    }}
    @keyframes rail-breathe {{
      0%, 100% {{ opacity: 0.28; }}
      50% {{ opacity: 0.62; }}
    }}
    @keyframes pulse-sweep-1 {{
      0% {{ transform: translateX(-460px); }}
      100% {{ transform: translateX(1160px); }}
    }}
    @keyframes pulse-sweep-2 {{
      0% {{ transform: translateX(1160px); }}
      100% {{ transform: translateX(-640px); }}
    }}
    @keyframes cursor-blink {{
      0%, 49% {{ opacity: 1; }}
      50%, 100% {{ opacity: 0; }}
    }}
    @keyframes title-glow {{
      0%, 100% {{ filter: drop-shadow(0 0 0px #ff0000); }}
      50% {{ filter: drop-shadow(0 0 8px rgba(255, 0, 0, 0.32)); }}
    }}
    @keyframes arrow-nudge {{
      0%, 100% {{ transform: translate(0, 0); opacity: 0.9; }}
      50% {{ transform: translate(1.8px, -1.8px); opacity: 1; }}
    }}
{"".join(ribbon_css)}    .aura {{ animation: aura-breathe 6s ease-in-out infinite; }}
    .red-bar {{ animation: bar-breathe 3.4s ease-in-out infinite; }}
    .red-bar-scan {{ animation: bar-scan 3.8s cubic-bezier(0.4, 0, 0.2, 1) infinite; }}
    .beacon {{ animation: beacon-pulse 2.4s ease-in-out infinite; transform-origin: {cx:.2f}px {cy:.2f}px; }}
    .beacon-ring {{ animation: beacon-ring 2.4s cubic-bezier(0.15, 0.6, 0.3, 1) infinite; transform-origin: {cx:.2f}px {cy:.2f}px; }}
    .rail-glow {{ animation: rail-breathe 4.4s ease-in-out infinite; }}
    .pulse-1 {{ animation: pulse-sweep-1 3.4s cubic-bezier(0.4, 0, 0.2, 1) infinite; }}
    .pulse-2 {{ animation: pulse-sweep-2 5.4s cubic-bezier(0.35, 0, 0.25, 1) infinite 0.9s; }}
    .cursor {{ animation: cursor-blink 1s steps(1) infinite; }}
    .wordmark {{ animation: title-glow 5.5s ease-in-out infinite; }}
    .cta-arrow {{ animation: arrow-nudge 3.2s ease-in-out infinite; }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
  </style>
{t.defs()}  <g clip-path="url(#cardClip)">
    <!-- Background -->
    <rect width="1200" height="320" fill="#000000" />
    <rect width="1200" height="320" fill="url(#titleAura)" class="aura" />
    <!-- Subtle ontology grid (upper right) -->
    <g mask="url(#gridMask)" stroke="#ffffff" stroke-opacity="0.045" stroke-width="1">
{"".join(grid_lines)}    </g>
    <!-- Left Accent Stripe -->
    <rect x="0" y="0" width="6" height="320" fill="#590000" />
    <rect x="0" y="0" width="6" height="320" fill="#ff0000" class="red-bar" />
    <rect x="0" y="0" width="6" height="140" fill="url(#barScanGrad)" class="red-bar-scan" />
  </g>
  <rect x="0.5" y="0.5" width="1199" height="319" rx="5.5" fill="none" stroke="#ffffff" stroke-opacity="0.09" stroke-width="1" />

{pill}
  <g class="wordmark">
{title}  </g>

  <!-- Kinetic Pure-Red Divider Rail -->
  <line x1="50" y1="{RAIL_Y}" x2="1150" y2="{RAIL_Y}" stroke="#260000" stroke-width="1.2" />
  <line x1="50" y1="{RAIL_Y}" x2="1150" y2="{RAIL_Y}" stroke="#ff0000" stroke-width="1.2" class="rail-glow" />
  <g mask="url(#railMask)">
    <g clip-path="url(#railClip)" fill="none">
      <g filter="url(#silkSoft)">
{"".join(ribbon_glow)}      </g>
{"".join(ribbon_core)}    </g>
  </g>
  <g clip-path="url(#coreClip)">
    <rect x="0" y="{RAIL_Y - 1.5}" width="640" height="3" fill="url(#pulseGrad2)" class="pulse-2" filter="url(#redGlow)" />
    <rect x="0" y="{RAIL_Y - 1.5}" width="460" height="3" fill="url(#pulseGrad1)" class="pulse-1" filter="url(#redGlow)" />
  </g>
  <rect x="50" y="{RAIL_Y - 2}" width="4" height="4" fill="#ff0000" />
  <rect x="1146" y="{RAIL_Y - 2}" width="4" height="4" fill="#ff0000" />

{subs}{cursor}{cta}</svg>
'''
    (cards / "banner.svg").write_text(out, encoding="utf-8")


# ---------------------------------------------------------------- community bar (tagline locked)

def chip(t: Typesetter, x: float, y: float, body: str, size: float, gid: str) -> str:
    """The one boxed element per row: hairline red frame, a faint red-to-black depth, white bold copy.
    Shared by the community bar and the separator so the two rows stay one system."""
    w = width(body, size) + 28
    return (
        f'  <defs><linearGradient id="{gid}" x2="0" y2="1"><stop stop-color="#2a0508"/>'
        f'<stop offset="1" stop-color="#0a0a0c"/></linearGradient></defs>\n'
        f'  <rect x="{x + .5:.2f}" y="{y + .5}" width="{w - 1:.2f}" height="23" rx="3" fill="url(#{gid})" '
        f'stroke="#ff0000" stroke-opacity="0.6" stroke-width="1"/>\n'
        f'  <path d="M{x + 3.5:.2f} {y + 1.5}h{w - 7:.2f}" stroke="#ffffff" stroke-opacity="0.12" stroke-width="1"/>\n'
        + t.run(x + w / 2, y + 15.4, size, body, "#ffffff", "700", "middle")
    )


def label(t: Typesetter, x: float, y: float, text: str, size: float, anchor: str = "start") -> str:
    """Muted key, config style: 'community:' / 'license:'. Never boxed."""
    return t.run(x, y + 15.4, size, f'{text}<tspan fill="#52525b">:</tspan>', "#8b8b94", "600", anchor)


def render_bar() -> None:
    t = Typesetter()
    lb = u("label", K_WIDE)
    k_w = width("community:", lb)
    p_txt = '<tspan fill="#ffffff">ai-marketing-hub-pro</tspan><tspan fill="#ff0000"> ↗</tspan>'
    p_x = 1 + k_w + 8
    p_w = width(p_txt, lb) + 28
    body = (
        label(t, 1, 3, "community", lb)
        + chip(t, p_x, 3, p_txt, lb, "chip-bar")
        + t.run(p_x + p_w + 12, 18.4, lb, BAR_TAGLINE, "#ffffff", "600")
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
        body += t.run(cx, top, lb, num, "#ff0000", "700")
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
    body += t.run(x1, base, lb, "zero context bloat", "#ff0000", "600", "end")
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
        + button(tl, (1 + SPLIT) / 2, 18.6, "#ff0000", "ENGINEERING SPEC →", lb)
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
    # The portrait is square art, so its slot is square (side = card height): the whole image shows,
    # edge to edge, with no crop. The copy column runs to a 20u gutter before it.
    px0 = 885 - (FLAG_BOTTOM - 2)
    # The bold lead stands alone on line 1; the body takes lines 2 and 3.
    lines = [f'<tspan fill="#ffffff" font-weight="700">{FLAG_LEAD}</tspan>'] + wrap(FLAG_BODY, bd, px0 - 20 - 20, 2)
    runs = (
        t.run(20, 30, hd, FLAG_TITLE, "#ffffff", "700")
        + t.run(20 + width(FLAG_TITLE, hd) + 12, 30, bd, FLAG_TAG, "#ff0000", "600")
        + "".join(t.run(20, 60 + 18 * i, bd, ln, "#d4d4d8") for i, ln in enumerate(lines))
    )
    block = f"  <!-- Left Content Column (x=20..{px0 - 20}) -->\n" + t.defs() + runs + "\n"
    s, n = re.subn(r"  <!-- Left Content Column.*?(?=  <!-- Right Tucked)", lambda _: block, s, count=1, flags=re.S)
    if n != 1:
        raise SystemExit("FAIL: flagship SVG markers missing")
    # Portrait: full bleed into the card's right edge, top border to footer seam, no frame.
    # Clipped to the card's rounded top-right corner; a 20u gutter separates it from the copy.
    href = re.search(r'<image [^>]*href="([^"]+)"', s).group(1)
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
    divider = 'stroke="#ff0000" stroke-opacity="0.30" stroke-width="1"'
    segs = [
        ("cto-legends-foot-readme", 'GITHUB README  <tspan fill="#ff0000">↗</tspan>'),
        ("cto-legends-foot-releases", 'RELEASES  <tspan fill="#ff0000">↗</tspan>'),
        ("cto-legends-foot-handoff", 'DOCS &amp; AGENT HANDOFF  <tspan fill="#ff0000">↗</tspan>'),
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
    label = (t.run(2, 0, ti, "&gt;_", "#ff0000", "700")
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


def render_collection_shrine() -> None:
    """Graphic shrine for the complete CTO Legends GitHub Star List."""
    import math
    t = Typesetter()
    hd, bd, lb = u("head", K_WIDE), u("body", K_WIDE), u("label", K_WIDE)
    h = 96
    cx, cy = 58.0, 48.0
    r_out, r_in = 23.5, 9.8
    verts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        r = r_out if i % 2 == 0 else r_in
        verts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))

    facets = ""
    for i in range(10):
        x1, y1 = verts[i]
        x2, y2 = verts[(i + 1) % 10]
        tri = f"{cx:.2f},{cy:.2f} {x1:.2f},{y1:.2f} {x2:.2f},{y2:.2f}"
        facets += f'  <polygon points="{tri}" fill="#ff0000"/>\n'
        if i % 2 == 1:
            facets += f'  <polygon points="{tri}" fill="#000000" opacity="0.34"/>\n'
    star_outline = " ".join(f"{x:.2f},{y:.2f}" for x, y in verts)

    def mini_star(mx: float, my: float, ro: float = 4.2, ri: float = 1.6) -> str:
        pts = []
        for k in range(8):
            a = math.radians(-90 + k * 45)
            rk = ro if k % 2 == 0 else ri
            pts.append(f"{mx + rk * math.cos(a):.2f},{my + rk * math.sin(a):.2f}")
        return " ".join(pts)

    body = (
        '  <defs>\n'
        f'    <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="{h}" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.05"/>'
        '<stop offset="0.65" stop-color="#ffffff" stop-opacity="0"/></linearGradient>\n'
        f'    <radialGradient id="star-aura" cx="{cx:.1f}" cy="{cy:.1f}" r="34" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#ff0000" stop-opacity="0.32"/>'
        '<stop offset="0.65" stop-color="#ff0000" stop-opacity="0.08"/>'
        '<stop offset="1" stop-color="#ff0000" stop-opacity="0"/></radialGradient>\n'
        '  </defs>\n'
        f'  <rect x="1" y="1" width="884" height="{h - 2}" rx="4" fill="#0c0507" {RED}/>\n'
        f'  <rect x="1" y="1" width="884" height="{h - 2}" rx="4" fill="url(#sheen)"/>\n'
        f'  <rect x="1" y="1" width="4" height="{h - 2}" rx="2" fill="#ff0000"/>\n'
        '  <rect x="18" y="12" width="80" height="72" rx="4" fill="#000000" stroke="#ff0000" stroke-opacity="0.55" stroke-width="1"/>\n'
        '  <rect x="22" y="16" width="72" height="64" rx="2" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="1"/>\n'
        f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="34" fill="url(#star-aura)"/>\n'
        + facets
        + f'  <polygon points="{star_outline}" fill="none" stroke="#ff0000" stroke-opacity="0.9" stroke-width="0.6"/>\n'
        + f'  <polygon points="{mini_star(29.5, 48.0)}" fill="#ff0000" opacity="0.75"/>\n'
        + f'  <polygon points="{mini_star(86.5, 48.0)}" fill="#ff0000" opacity="0.75"/>\n'
    )
    tx = 116
    sub = "Bookmark or star the router and every module from a single GitHub list."
    body += t.run(tx, 27, lb, "GITHUB STAR LIST", "#ff0000", "700")
    x_meta = tx + width("GITHUB STAR LIST", lb) + 10
    body += t.run(x_meta, 27, lb, "// github.com/stars/avalonreset/lists/cto-legends", "#a1a1aa", "400")
    body += t.run(tx, 52, hd, "The complete cto-legends collection on one page", "#ffffff", "700")
    body += t.run(tx, 74, bd, sub, "#d4d4d8", "400")

    btn_w = 216
    btn_x = 868 - btn_w
    assert tx + width(sub, bd) + 20 <= btn_x, "Shrine subline collides with button"
    body += f'  <rect x="{btn_x}" y="29" width="{btn_w}" height="38" rx="3" fill="#000000" {RED}/>\n'
    body += button(t, btn_x + btn_w / 2, 52.5, "#ffffff", 'OPEN GITHUB LIST <tspan fill="#ff0000">↗</tspan>', lb, "700")

    top = 16.0
    (cards / "collection-shrine.svg").write_text(svg(f"0 {-top:.2f} 886 {h + top:.2f}", body, t), encoding="utf-8")


# ---------------------------------------------------------------- README

def img(href: str, src: str, width_: str, alt: str) -> str:
    tag = f'<img src="assets/cards/{REV}/{src}" width="{width_}" align="top" alt="{alt}" />'
    return f'<a href="{href}">{tag}</a>' if href else tag


def header_block(overview_alt: str) -> str:
    banner_alt = BANNER_ALT
    bar_alt = "community: ai-marketing-hub-pro on Skool, designed to combine into an agentic digital marketing system"
    ov_alt = ("How cto-legends works: If your AI hands the steps back to you, nothing was delegated. "
              "You just got one more thing to babysit. cto-legends is free software that gives your agents real hands, "
              "so your only job is to say what you want. 01. you talk: Say it the way you would to your CTO, such as "
              "move my DNS to Cloudflare or why did my Stripe fees jump? 02. the agents operate: They find the file, "
              "install the right module, run the command and check the result. You touch nothing. 03. you decide: "
              "You get back what happened and what it means, not a to-do list. That is business intelligence. "
              "Vendor agnostic presets: claude, codex, gemini, grok, muse, deepseek, qwen, glm.")
    parts = [
        img(f"{SITE}/home", "banner.svg", "100%", banner_alt),
        img(SKOOL, "bar-community.svg", "100%", bar_alt),
        img(f"{GH}/cto-legends", "overview-panel.svg", "100%", ov_alt),
    ]
    return '<p align="left">\n  ' + "<!--\n  -->".join(parts) + "\n</p>"


def cards_block(widths: dict) -> str:
    flag_alt = f"start here, the one package you install: {FLAG_LEAD} {FLAG_BODY}"
    out = ['<p align="left">', "  " + img(f"{GH}/cto-legends", "cto-legends-flagship.svg", "100%", flag_alt)]
    links = [
        (f"{GH}/cto-legends#readme", "cto-legends-foot-readme", "GITHUB README: read the avalonreset/cto-legends documentation on GitHub"),
        (f"{GH}/cto-legends/releases", "cto-legends-foot-releases", "RELEASES: view pinned avalonreset/cto-legends releases on GitHub"),
        (f"{SITE}/modules/cto-legends", "cto-legends-foot-handoff", "DOCS AND AGENT HANDOFF: open cto-legends.com/modules/cto-legends specification and agent handoff"),
    ]
    out.append("  " + "<!--\n  -->".join(
        img(h, f"{f}.svg", f"{(FLAG_B[i + 1] - FLAG_B[i]) / FLAG_W * 100:.2f}%", a)
        for i, (h, f, a) in enumerate(links)) + "<!--\n  -->"
        + img("", "cto-legends-handoff-label.svg", "100%", "agent handoff: vendor-agnostic, paste this prompt into any AI coding agent and it runs the setup"))
    out += ["</p>", "", "```text", HANDOFF, "```", "", '<p align="left">']
    shrine_alt = "GitHub Star List: The complete cto-legends collection on one page. Bookmark or star the router and every module from a single GitHub list."
    out.append("  " + img("", "modules-heading.svg", "100%", "the modules: on-demand open-source CLI modules for sovereign business infrastructure and operational ontology, each one installs only when a task needs it") + "<!--\n  -->"
               + img(f"{GH}/cto-legends#development-contributing-and-license", "ecosystem-separator.svg", "100%", "license: open source (MIT core; legends-stable-audio-3 is Apache-2.0, legends-hyperyap is AGPL-3.0)"))
    lic_fmt = {"mit": "MIT", "apache-2.0": "Apache-2.0", "agpl-3.0": "AGPL-3.0"}
    for r in range(0, len(MODULES), 3):
        trio = MODULES[r:r + 3]
        row_imgs = [
            img(f"{GH}/{n}", f"{n}.svg", f"{COL_PCT}%", f"{n} ({COPY[n][0]}, {lic_fmt.get(COPY[n][1], COPY[n][1])}): {COPY[n][2]}") for n in trio
        ]
        if len(trio) < 3:
            pad_cols = 3 - len(trio)
            pad_name = f"spacer-{pad_cols}col.svg"
            (cards / pad_name).write_text(
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {COL_W * pad_cols} 1" width="100%"/>\n',
                encoding="utf-8",
            )
            row_imgs.append(img("", pad_name, f"{COL_PCT * pad_cols:.2f}%", ""))
        out.append("  " + "<!--\n  -->".join(row_imgs))
        btns = []
        for n in trio:
            lw, rw = widths[n]
            btns.append(img(f"{SITE}/modules/{n}", f"{n}-spec.svg", lw, f"ENGINEERING SPEC: {n} specification on cto-legends.com"))
            btns.append(img(f"{GH}/{n}#readme", f"{n}-repo.svg", rw, f"GITHUB README: avalonreset/{n} repository README"))
        if len(trio) < 3:
            pad_cols = 3 - len(trio)
            btns.append(img("", f"spacer-{pad_cols}col.svg", f"{COL_PCT * pad_cols:.2f}%", ""))
        out.append("  " + "<!--\n  -->".join(btns))
    out.append("  " + img(STAR_LIST, "collection-shrine.svg", "100%", shrine_alt))
    out.append("</p>")
    return "\n".join(out)


YOU_ALT = "Start here with cto-legends: red demon character in a black dress pointing forward with the caption YOU. YES, YOU."
MEME_ALT = ("CTO Legends business intelligence panel: two figures in Greek vase style, asking wait, it was business intelligence "
            "this whole time? Always has been.")
YOU_HREF = "https://github.com/avalonreset/cto-legends#readme"   # the call to action: go install it
MEME_HREF = "https://cto-legends.com/home"                       # the punchline: what it is all for

# Closing row under the grid: the square portrait and the 16:9 meme at one shared height, filling
# the 886u row exactly full bleed with no gutter (the README joins them
# with no whitespace). 32px section gap above: 16px README paragraph + 16px viewBox padding.
CLOSE_G = 0  # full bleed: the two images meet with no gutter (owner 2026-11-14)
CLOSE_H = (886 - CLOSE_G) / (1 + 16 / 9)
CLOSE_YOU_W, CLOSE_MEME_W = CLOSE_H, CLOSE_H * 16 / 9


def framed(src: Path, mime: str, w: float, h: float, cid: str, side: str) -> str:
    """Half of a full-bleed pair: rounded on its outer side, square and borderless at the seam."""
    import base64
    data = base64.b64encode(src.read_bytes()).decode()
    r, t, bt = 6, 0.5, h - 0.5
    if side == "left":
        edge = f"M{w:.2f} {t} H{r + t} A{r} {r} 0 0 0 {t} {r + t} V{bt - r:.2f} A{r} {r} 0 0 0 {r + t} {bt:.2f} H{w:.2f}"
    else:
        edge = f"M0 {t} H{w - r - t:.2f} A{r} {r} 0 0 1 {w - t:.2f} {r + t} V{bt - r:.2f} A{r} {r} 0 0 1 {w - r - t:.2f} {bt:.2f} H0"
    return (f'<clipPath id="{cid}"><path d="{edge} Z"/></clipPath>\n'
            f'<image href="data:{mime};base64,{data}" x="0" y="0" width="{w:.2f}" height="{h:.2f}" '
            f'preserveAspectRatio="xMidYMid slice" clip-path="url(#{cid})"/>\n'
            f'<path d="{edge}" fill="none" {BORDER}/>\n')


def render_closing() -> None:
    h, top = CLOSE_H, GAP16
    you = framed(root / "assets" / "you-yes-you.webp", "image/webp", CLOSE_YOU_W, h, "yc", "left")
    meme = framed(root / "assets" / "bizintel.webp", "image/webp", CLOSE_MEME_W, h, "mc", "right")
    (cards / "closing-you.svg").write_text(svg(f"0 {-top:.2f} {CLOSE_YOU_W:.2f} {h + top:.2f}", you), encoding="utf-8")
    (cards / "closing-meme.svg").write_text(
        svg(f"{-CLOSE_G:.2f} {-top:.2f} {CLOSE_MEME_W + CLOSE_G:.2f} {h + top:.2f}", meme), encoding="utf-8")
    old = cards / "bizintel-meme.svg"
    if old.exists():
        old.unlink()


def meme_block() -> str:
    you_pct = int(CLOSE_YOU_W / 886 * 100000) / 1000
    meme_pct = int((CLOSE_MEME_W + CLOSE_G) / 886 * 100000) / 1000
    return ('<p align="center">\n  '
            + img(YOU_HREF, "closing-you.svg", f"{you_pct:.3f}%", YOU_ALT) + "<!--\n  -->"
            + img(MEME_HREF, "closing-meme.svg", f"{meme_pct:.3f}%", MEME_ALT) + "\n</p>")


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
    render_collection_shrine()
    render_closing()
    readme = readme_path.read_text(encoding="utf-8")
    readme = splice(readme, "HEADER", header_block(overview_alt))
    readme = splice(readme, "CARDS", cards_block(widths))
    readme = splice(readme, "MEME", meme_block())
    readme_path.write_text(readme, encoding="utf-8")
    print(f"Rendered banner, bar, overview, flagship, heading and {len(MODULES)} module cards (outlined {FONT}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
