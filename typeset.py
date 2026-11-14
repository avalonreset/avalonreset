"""Outline text to SVG paths so every profile image renders with identical metrics everywhere.

GitHub serves README SVGs as <img>, which cannot load web fonts, so live <text> falls back to
whatever monospace the viewer has (SF Mono 0.6025em, Consolas ~0.55em, ...) and the copy fit
drifts. Here each glyph of IBM Plex Mono (SIL OFL 1.1) is converted to a path once per SVG and
placed with <use>, so a line measured here is the line every viewer sees.

Fonts are read from FONT_DIR. Advance is exactly 0.6em for every glyph in every weight.
"""
from functools import lru_cache
from html import unescape
from pathlib import Path
import os
import re

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

FONT_DIR = Path(os.environ.get("PLEX_DIR", "C:/Windows/Fonts"))
WEIGHTS = {"400": "Regular", "500": "Medium", "600": "SemiBold", "700": "Bold"}
EM = 0.6  # advance per em, all weights
TSPAN = re.compile(r'<tspan([^>]*)>(.*?)</tspan>', re.S)
ATTR = re.compile(r'([\w-]+)="([^"]*)"')


@lru_cache(maxsize=None)
def _font(weight: str):
    f = TTFont(FONT_DIR / f"IBMPlexMono-{WEIGHTS[weight]}.ttf")
    return f, f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm


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
            f, gs, cmap, upm = _font(weight)
            name = cmap.get(ord(ch))
            if name is None:
                raise SystemExit(f"FAIL: IBM Plex Mono {WEIGHTS[weight]} has no glyph for {ch!r}")
            pen = SVGPathPen(gs, ntos=_num)
            gs[name].draw(pen)
            self.used[key] = (f"{'rmsb'[list(WEIGHTS).index(weight)]}{ord(ch):x}", pen.getCommands())
        return self.used[key][0]

    def run(self, x: float, y: float, size: float, body: str, fill: str = "#ffffff",
            weight: str = "400", anchor: str = "start", spacing: float = 0.0) -> str:
        """One line of text. spacing is extra letter-spacing in SVG units."""
        segs = segments(body, fill, weight)
        w = width(body, size, spacing)
        x0 = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
        s = size / 1000
        step = 600 + spacing / s
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
