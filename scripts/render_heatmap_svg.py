#!/usr/bin/env python3
"""
Render data/contributions.json as an animated 53x7 contribution heatmap SVG.

Rounded boxes on a GitHub-ish green ramp, revealed once with a diagonal
line-after-line slide-down (CSS keyframes that play on load then freeze — no
looping glow). Month labels on top, weekday labels on the left, a Less->More
legend and a "N contributions in the last year" footer.

GitHub renders SVG <img> and runs their inline <style> keyframes, so the
animation lives entirely inside this file.

Run:  python scripts/render_heatmap_svg.py   ->  writes contrib-heatmap.svg
"""
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

DATA = Path("data/contributions.json")
OUT = Path("contrib-heatmap.svg")

CELL = 13
GAP = 3
STEP = CELL + GAP
TOP = 30           # room for month labels
LEFT = 30          # room for weekday labels
PALETTE = ["#21272f", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL_STROKE = "#30363d"   # outline so the 53x7 grid clearly reads even when empty
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONO = "SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace"


def load():
    return json.loads(DATA.read_text(encoding="utf-8"))


def weeks_from(days):
    """Group day dicts into columns (weeks), Sunday-first like GitHub."""
    cols = []
    cur = []
    for d in days:
        y, m, dd = map(int, d["date"].split("-"))
        wd = date(y, m, dd).weekday()      # Mon=0..Sun=6
        wd = (wd + 1) % 7                   # -> Sun=0..Sat=6
        if wd == 0 and cur:
            cols.append(cur)
            cur = []
        cur.append((wd, d))
    if cur:
        cols.append(cur)
    return cols


def build(payload):
    days = payload["days"]
    stats = payload["stats"]
    cols = weeks_from(days)
    n_weeks = len(cols)
    width = LEFT + n_weeks * STEP + 10
    height = TOP + 7 * STEP + 46

    total_cells = n_weeks * 7
    # per-cell reveal delay along the diagonal (col + row)
    max_diag = n_weeks + 7
    per = 1.6 / max_diag        # total sweep ~1.6s

    p = []
    p.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{MONO}">'
    )
    # keyframes: each cell starts hidden + shifted up, drops into place, freezes
    p.append(
        '<style>'
        '@keyframes drop{from{opacity:0;transform:translateY(-6px)}'
        'to{opacity:1;transform:translateY(0)}}'
        '.c{opacity:0;animation:drop .45s ease-out forwards;transform-box:fill-box;}'
        '.lbl{fill:#8b949e;font-size:10px;}'
        '</style>'
    )
    p.append('<rect width="100%" height="100%" rx="10" fill="#0d1117"/>')

    # month labels (top) — print the month at the first week it appears
    seen_month = set()
    for wi, col in enumerate(cols):
        first = col[0][1]["date"]
        mo = int(first[5:7])
        if mo not in seen_month:
            seen_month.add(mo)
            x = LEFT + wi * STEP
            p.append(f'<text class="lbl" x="{x}" y="{TOP - 12}">{MONTHS[mo-1]}</text>')

    # weekday labels (Mon/Wed/Fri like GitHub)
    for wd, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = TOP + wd * STEP + CELL - 2
        p.append(f'<text class="lbl" x="0" y="{y}">{name}</text>')

    # cells
    for wi, col in enumerate(cols):
        for wd, d in col:
            x = LEFT + wi * STEP
            y = TOP + wd * STEP
            lvl = min(d["level"], len(PALETTE) - 1)
            fill = PALETTE[lvl]
            delay = (wi + wd) * per
            p.append(
                f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="3" fill="{fill}" stroke="{CELL_STROKE}" stroke-width="1" '
                f'style="animation-delay:{delay:.3f}s">'
                f'<title>{d["date"]}: {d["count"]}</title></rect>'
            )

    # legend (Less -> More)
    ly = TOP + 7 * STEP + 20
    lx = width - 12 - 6 * (CELL - 3) - 80
    p.append(f'<text class="lbl" x="{lx - 34}" y="{ly + CELL - 3}">Less</text>')
    for k, c in enumerate(PALETTE):
        p.append(f'<rect x="{lx + k * (CELL - 2)}" y="{ly}" width="{CELL-3}" '
                 f'height="{CELL-3}" rx="2" fill="{c}"/>')
    p.append(f'<text class="lbl" x="{lx + 6 * (CELL - 2) + 6}" y="{ly + CELL - 3}">More</text>')

    # footer stats
    fy = TOP + 7 * STEP + 20
    total = stats["total"]
    cur = stats["current_streak"]
    lng = stats["longest_streak"]
    p.append(
        f'<text x="0" y="{fy + CELL - 3}" fill="#c9d1d9" font-size="12">'
        f'{total:,} contributions in the last year'
        f'<tspan fill="#8b949e">   ·   streak {cur}d (max {lng}d)</tspan></text>'
    )
    _ = total_cells
    p.append('</svg>')
    return "\n".join(p)


if __name__ == "__main__":
    OUT.write_text(build(load()), encoding="utf-8")
    print(f"wrote {OUT}")
