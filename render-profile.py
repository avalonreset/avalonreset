#!/usr/bin/env python3
"""Validate (and optionally regenerate shimmer for) the 3-across SVG card layout in avalonreset."""
import argparse
from pathlib import Path
import re
import runpy
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True

root = Path(__file__).resolve().parent
assets = root / "assets"
readme_path = root / "README.md"


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate avalonreset profile SVGs and README layout.")
    ap.add_argument("--shimmer", action="store_true", help="Regenerate assets/ecosystem-separator.svg")
    args = ap.parse_args()

    if args.shimmer:
        runpy.run_path(str(root / "render-shimmer.py"))

    readme = readme_path.read_text(encoding="utf-8")
    if "\u2014" in readme or "\u2013" in readme:
        raise SystemExit("FAIL: Em-dash or en-dash found in README.md")

    referenced = re.findall(r'src="(assets/[^"?]+)', readme)
    if not referenced:
        raise SystemExit("FAIL: No asset references found in README.md")

    for rel in referenced:
        target = root / rel
        if not target.is_file():
            raise SystemExit(f"FAIL: Missing referenced asset: {rel}")

    svg_files = sorted(assets.rglob("*.svg"))
    for svg_path in svg_files:
        text = svg_path.read_text(encoding="utf-8")
        if "\u2014" in text or "\u2013" in text:
            raise SystemExit(f"FAIL: Em-dash or en-dash in {svg_path.relative_to(root)}")
        ET.fromstring(text)

    expected_min_x = ("-0.004", "-2.25", "-4.496")
    module_refs = re.findall(r'src="(assets/cards/legends-[^"?]+\.svg)', readme)
    for idx, rel in enumerate(module_refs):
        vb_match = re.search(r'viewBox="([^"]+)"', (root / rel).read_text(encoding="utf-8"))
        want = f"{expected_min_x[idx % 3]} 1.25 296.5 155.5"
        if not vb_match or vb_match.group(1) != want:
            raise SystemExit(f"FAIL: {rel} column {idx % 3 + 1} viewBox is {vb_match.group(1) if vb_match else None!r}, expected {want!r}")

    print(
        f"Validated {len(referenced)} README card/banner references and {len(svg_files)} SVG files (0 issues)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
