#!/usr/bin/env python3
"""
Optional photo prep for the ASCII portrait.

make_ascii_svg.py works directly on source-photo.png, but a flatly-lit face
converts to a dark blob. If you want more punch, drop a face photo in and run:

    python scripts/prep_photo.py my-face.jpg

It grayscales, boosts contrast (autocontrast + a contrast bump — a lightweight
stand-in for CLAHE, no OpenCV needed), composites onto white, and overwrites
source-photo.png. Then run make_ascii_svg.py.

For best results use a photo with clear light/shadow on the face and a plain
background. If you have rembg/opencv installed you can pre-cut the background
for an even cleaner subject.
"""
import sys
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance

OUT = Path("source-photo.png")


def main():
    if len(sys.argv) < 2:
        print("usage: python scripts/prep_photo.py <photo>")
        raise SystemExit(1)
    src = Image.open(sys.argv[1]).convert("L")
    src = ImageOps.autocontrast(src, cutoff=1)
    src = ImageEnhance.Contrast(src).enhance(1.7)
    # composite onto white so the background maps to the blank end of the ramp
    white = Image.new("L", src.size, 255)
    white.paste(src, (0, 0))
    white.save(OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
