#!/usr/bin/env python3
"""
Turn source-photo.png into a self-typing, monochrome ASCII-art SVG.

Pure Pillow — no rembg/opencv. Steps:
  1. grayscale + strong auto-contrast so a flat image gets real highlights/shadows
  2. downsample to a character grid (chars are ~2x taller than wide, so we squash Y)
  3. map each cell's brightness to a glyph on a density ramp
  4. emit one <text> per row, each wrapped in a left-to-right clip wipe that
     staggers top->bottom — SMIL animation GitHub actually plays. Prints once,
     then freezes (no looping).

Run:  python scripts/make_ascii_svg.py   ->  writes avi-ascii.svg
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance

SRC = Path("source-photo.png")
OUT = Path("avi-ascii.svg")

COLS = 92                      # character columns
RAMP = " .`:-=+*csoe#%@"       # bright (sparse) -> dark (dense); leading space = blank
CELL_W = 7.2                   # px per glyph horizontally
CELL_H = 12.6                  # px per line vertically
FG = "#c9d1d9"                 # single light-gray fill (monochrome = clean, not noisy)
CURSOR = "#39d353"             # little block that rides the wipe edge
ROW_STAGGER = 0.045            # seconds between rows starting to print
ROW_DUR = 0.5                  # seconds each row takes to wipe in


def load_grid():
    img = Image.open(SRC).convert("L")
    # Composite onto white first so any transparency maps to the blank ramp end.
    if Image.open(SRC).mode in ("RGBA", "LA", "P"):
        base = Image.new("L", img.size, 255)
        rgba = Image.open(SRC).convert("RGBA")
        base.paste(img, mask=rgba.split()[-1])
        img = base

    img = ImageOps.autocontrast(img, cutoff=2)
    img = ImageEnhance.Contrast(img).enhance(1.5)

    w, h = img.size
    rows = max(1, int(COLS * (h / w) * (CELL_W / CELL_H)))
    img = img.resize((COLS, rows), Image.LANCZOS)
    px = img.load()

    grid = []
    n = len(RAMP)
    for y in range(rows):
        line = []
        for x in range(COLS):
            v = px[x, y]            # 0 dark .. 255 bright
            # bright -> ramp[0] (space), dark -> ramp[-1]
            idx = int((255 - v) / 255 * (n - 1) + 0.5)
            line.append(RAMP[idx])
        grid.append("".join(line).rstrip())
    # drop fully-blank leading/trailing rows
    while grid and not grid[0].strip():
        grid.pop(0)
    while grid and not grid[-1].strip():
        grid.pop()
    return grid


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(grid):
    rows = len(grid)
    width = int(COLS * CELL_W) + 24
    height = int(rows * CELL_H) + 24
    total = ROW_STAGGER * rows + ROW_DUR

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'font-family="SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace">'
    )
    parts.append(f'<rect width="100%" height="100%" fill="#0d1117" rx="10"/>')

    defs = ['<defs>']
    body = []
    for i, line in enumerate(grid):
        if not line:
            continue
        y = 18 + i * CELL_H
        begin = f"{i * ROW_STAGGER:.3f}s"
        clip_id = f"c{i}"
        cw = len(line) * CELL_W
        # clip rectangle that grows left->right
        defs.append(
            f'<clipPath id="{clip_id}"><rect x="12" y="{y - CELL_H:.1f}" '
            f'width="0" height="{CELL_H + 4:.1f}">'
            f'<animate attributeName="width" from="0" to="{cw:.1f}" '
            f'begin="{begin}" dur="{ROW_DUR}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.2 0.7 0.2 1" keyTimes="0;1"/>'
            f'</rect></clipPath>'
        )
        body.append(
            f'<text x="12" y="{y:.1f}" fill="{FG}" font-size="12" '
            f'xml:space="preserve" clip-path="url(#{clip_id})">{esc(line)}</text>'
        )
        # cursor block rides the wipe edge, then vanishes when the row is done
        body.append(
            f'<rect x="12" y="{y - CELL_H + 2:.1f}" width="{CELL_W:.1f}" '
            f'height="{CELL_H:.1f}" fill="{CURSOR}" opacity="0">'
            f'<animate attributeName="x" from="12" to="{12 + cw:.1f}" '
            f'begin="{begin}" dur="{ROW_DUR}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.9" begin="{begin}"/>'
            f'<set attributeName="opacity" to="0" begin="{i * ROW_STAGGER + ROW_DUR:.3f}s"/>'
            f'</rect>'
        )

    defs.append('</defs>')
    parts.extend(defs)
    parts.extend(body)
    parts.append('</svg>')
    _ = total
    return "\n".join(parts)


def main():
    grid = load_grid()
    OUT.write_text(build_svg(grid), encoding="utf-8")
    print(f"wrote {OUT} ({len(grid)} rows)")


if __name__ == "__main__":
    main()
