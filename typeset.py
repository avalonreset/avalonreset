"""Outline text to SVG paths so every profile image renders with identical metrics everywhere.

GitHub serves README SVGs as <img>, which cannot load web fonts, so live <text> falls back to
whatever monospace the viewer has (SF Mono 0.6025em, Consolas ~0.55em, ...) and the copy fit
drifts. Here each glyph is converted to
a path once per SVG and placed with <use>, so a line measured here is the line every viewer sees.

The family is PROFILE_FONT (default legends, the brand font). Sizes are nominal: each font is
scaled so one advance is 0.6 of the size, so every candidate sets on the same character grid and
the layout math never changes. Glyphs a family lacks (Legends has no arrows) come from IBM Plex
Mono, centered in the cell.
"""
from functools import lru_cache
from html import unescape
from pathlib import Path
import os
import re

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

WKEYS = ("400", "500", "600", "700")
WIN, LEGENDS = "C:/Windows/Fonts", "E:/empire/Workspaces/Brands & Sites/cto-legends/fonts"


def _static(prefix, d=WIN, names=("Regular", "Medium", "SemiBold", "Bold")):
    """Weight -> file; a missing weight falls back to the nearest one the family ships."""
    out = {}
    for w, n in zip(WKEYS, names):
        cands = [n] + (["Medium", "Regular"] if w == "500" else ["Bold", "Medium"] if w == "600" else [])
        out[w] = next((f"{d}/{prefix}-{c}.ttf" for c in cands if Path(f"{d}/{prefix}-{c}.ttf").exists()), None)
    return out


def _variable(path):
    return {w: (path, int(w)) for w in WKEYS}


# Every candidate is outlined to paths, so viewers never need the font installed.
FONTS = {
    "legends": _static("Legends", LEGENDS, ("Regular", "Regular", "Bold", "Bold")),
    "plex": _static("IBMPlexMono"),
    "roboto": _static("RobotoMono"),
    "source": _static("SourceCodePro"),
    "cascadia": _variable(f"{WIN}/CascadiaCode.ttf"),
    "jetbrains": _static("JetBrainsMono", os.environ.get("JETBRAINS_DIR", "E:/_to-sort-later/root-folders-2026-07-16/_tmp_bt_rewrite2/assets/fonts")),
}
FONTS.update({k: (_variable(v) if isinstance(v, str) else v)
              for k, v in __import__("json").loads(os.environ.get("PROFILE_FONTS_EXTRA", "{}")).items()})
FONT = os.environ.get("PROFILE_FONT", "legends")
WEIGHTS = {w: w for w in WKEYS}
EM = 0.6  # nominal advance per em: sizes are normalized so every font sets on the same grid
TSPAN = re.compile(r'<tspan([^>]*)>(.*?)</tspan>', re.S)
ATTR = re.compile(r'([\w-]+)="([^"]*)"')


@lru_cache(maxsize=None)
def _font(weight: str, family: str = FONT):
    src = FONTS[family][weight]
    if isinstance(src, (tuple, list)):
        from fontTools.varLib.instancer import instantiateVariableFont
        f = instantiateVariableFont(TTFont(src[0]), {"wght": src[1]})
    else:
        f = TTFont(src)
    cmap = f.getBestCmap()
    return f, f.getGlyphSet(), cmap, f["head"].unitsPerEm, f["hmtx"][cmap[ord("M")]][0]


_, _, _, UPM, ADV = _font("400")
NORM = EM * UPM / ADV  # scale so one advance is 0.6 of the nominal size
CAP = _font("400")[0]["OS/2"].sCapHeight / UPM * NORM  # cap height per nominal em


def _num(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def segments(body: str, fill: str, weight: str) -> list:
    """Split '<tspan fill=.. font-weight=..>..</tspan>' markup into (text, fill, weight) runs."""
    out, pos = [], 0
    for m in TSPAN.finditer(body):
        if m.start() > pos:
            out.append((unescape(body[pos:m.start()]), fill, weight))
        a = dict(ATTR.findall(m.group(1)))
        out.append((unescape(m.group(2)), a.get("fill", fill), a.get("font-weight", weight)))
        pos = m.end()
    if pos < len(body):
        out.append((unescape(body[pos:]), fill, weight))
    return out


def width(body: str, size: float, spacing: float = 0.0) -> float:
    n = sum(len(t) for t, _, _ in segments(body, "", "400"))
    return n * size * EM + max(n - 1, 0) * spacing


class Typesetter:
    """Collects the glyphs one SVG uses; call defs() once and run() per line."""

    def __init__(self):
        self.used = {}

    def _gid(self, ch: str, weight: str) -> str:
        key = (ch, weight)
        if key not in self.used:
            f, gs, cmap, upm, adv = _font(weight)
            name = cmap.get(ord(ch))
            pen = SVGPathPen(gs, ntos=_num)
            if name is None:  # borrow from Plex and fit it, centered, into this font's cell
                f, gs, cmap, pupm, padv = _font(weight, "plex")
                name = cmap.get(ord(ch))
                if name is None:
                    raise SystemExit(f"FAIL: neither {FONT} nor Plex has a glyph for {ch!r}")
                from fontTools.pens.transformPen import TransformPen
                k = upm / pupm
                pen = SVGPathPen(gs, ntos=_num)
                gs[name].draw(TransformPen(pen, (k, 0, 0, k, (adv - padv * k) / 2, 0)))
            else:
                gs[name].draw(pen)
            self.used[key] = (f"{'rmsb'[list(WEIGHTS).index(weight)]}{ord(ch):x}", pen.getCommands())
        return self.used[key][0]

    def run(self, x: float, y: float, size: float, body: str, fill: str = "#ffffff",
            weight: str = "400", anchor: str = "start", spacing: float = 0.0) -> str:
        """One line of text. spacing is extra letter-spacing in SVG units."""
        segs = segments(body, fill, weight)
        w = width(body, size, spacing)
        x0 = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
        s = size * NORM / UPM
        step = ADV + spacing / s
        parts, i = [], 0
        for t, f, wt in segs:
            uses = []
            for ch in t:
                if not ch.isspace():
                    uses.append(f'<use href="#{self._gid(ch, wt)}" x="{_num(i * step)}"/>')
                i += 1
            if uses:
                parts.append(f'<g fill="{f}">{"".join(uses)}</g>')
        return (f'  <g transform="translate({x0:.2f} {y:.2f}) scale({s:.5f} {-s:.5f})">'
                f'{"".join(parts)}</g>\n')

    def defs(self) -> str:
        if not self.used:
            return ""
        paths = "".join(f'<path id="{gid}" d="{d}"/>' for gid, d in self.used.values())
        return f"  <defs>{paths}</defs>\n"
