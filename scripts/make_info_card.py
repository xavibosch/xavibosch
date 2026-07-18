#!/usr/bin/env python3
"""
Hand-authored neofetch-style info card as an animated SVG.

The contribution graph already covers the GitHub stats, so this panel carries
the story numbers can't tell: who I am, what I'm building, the stack. Each row
fades + slides in on a short stagger so it looks like it's printing next to the
ASCII portrait.

STATIC=1 emits a frozen frame (for local Quick Look).

Run:  python scripts/make_info_card.py   ->  writes info-card.svg
"""
import os
from pathlib import Path

OUT = Path("info-card.svg")
STATIC = os.environ.get("STATIC") == "1"

# ---- content ---------------------------------------------------------------
TITLE = "xavi@github"
SUB = "~ neofetch"

# (label, value, value-color)
GREEN = "#39d353"
CYAN = "#39c5cf"
YELL = "#e3b341"
PINK = "#db61a2"
FG = "#c9d1d9"
DIM = "#8b949e"

ROWS = [
    ("Name",       "Xavi Bosch",                              CYAN),
    ("Role",       "Solo founder · iOS & web dev",            FG),
    ("Now",        "Building Betsy — social sports app",      GREEN),
    ("Stack",      "SwiftUI · Firebase · Next.js · TS",       FG),
    ("Also",       "Remotion promos · design · marketing",    FG),
    ("Focus",      "Ship fast, validate, harden",             FG),
    ("Highlights", "Self-learner · hard-worker · team player", YELL),
    ("Location",   "Barcelona, Catalunya",                    FG),
    ("Contact",    "https://boschwebs.website",               PINK),
]

# ---- geometry --------------------------------------------------------------
PAD = 18
BAR_H = 34
ROW_H = 26
LABEL_W = 118
WIDTH = 560
HEIGHT = PAD * 2 + BAR_H + 14 + len(ROWS) * ROW_H + 12
MONO = "SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def row_anim(i):
    """Fade + slide-in per row unless STATIC."""
    if STATIC:
        return "", "translate(0,0)"
    begin = 0.25 + i * 0.11
    anim = (
        f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" '
        f'dur="0.35s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'from="10 0" to="0 0" begin="{begin:.2f}s" dur="0.35s" '
        f'calcMode="spline" keySplines="0.2 0.7 0.2 1" keyTimes="0;1" fill="freeze"/>'
    )
    return anim, None


def build():
    p = []
    p.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" font-family="{MONO}">'
    )
    p.append(f'<rect width="100%" height="100%" rx="10" fill="#0d1117" '
             f'stroke="#30363d" stroke-width="1"/>')

    # title bar (mac dots + prompt)
    for k, cx in enumerate((PAD + 8, PAD + 26, PAD + 44)):
        color = ("#ff5f57", "#febc2e", "#28c840")[k]
        p.append(f'<circle cx="{cx}" cy="{PAD + 8}" r="6" fill="{color}"/>')
    p.append(
        f'<text x="{PAD + 66}" y="{PAD + 13}" fill="{DIM}" font-size="13">'
        f'{esc(TITLE)} <tspan fill="#484f58">{esc(SUB)}</tspan></text>'
    )
    p.append(f'<line x1="{PAD}" y1="{PAD + BAR_H}" x2="{WIDTH - PAD}" '
             f'y2="{PAD + BAR_H}" stroke="#21262d"/>')

    y0 = PAD + BAR_H + 26
    for i, (label, value, color) in enumerate(ROWS):
        y = y0 + i * ROW_H
        anim, _ = row_anim(i)
        op = "1" if STATIC else "0"
        p.append(f'<g opacity="{op}">{anim}')
        p.append(f'<text x="{PAD}" y="{y}" fill="{GREEN}" font-size="13" '
                 f'font-weight="bold">{esc(label)}</text>')
        p.append(f'<text x="{PAD + 96}" y="{y}" fill="{DIM}" font-size="13">:</text>')
        p.append(f'<text x="{PAD + LABEL_W}" y="{y}" fill="{color}" '
                 f'font-size="13">{esc(value)}</text>')
        p.append('</g>')

    # little color palette strip (neofetch signature)
    sy = y0 + len(ROWS) * ROW_H + 2
    for k, c in enumerate(["#0d1117", "#39d353", "#39c5cf", "#e3b341",
                           "#db61a2", "#c9d1d9"]):
        p.append(f'<rect x="{PAD + k * 20}" y="{sy}" width="16" height="10" '
                 f'rx="2" fill="{c}" stroke="#30363d" stroke-width="0.5"/>')

    p.append('</svg>')
    return "\n".join(p)


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT}  (static={STATIC})")
