"""Draws the animated header and skills map for the profile README.

Each image comes in a dark and a light version, picked by the README with
<picture> so it follows the visitor's GitHub theme. Everything is plain SVG
with CSS animation: no web fonts, no scripts, no third-party services.
Icons are Simple Icons (CC0), stored in data/icons.json.

    python scripts/make_profile_art.py
"""

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICONS = json.loads((ROOT / "data" / "icons.json").read_text())

ORANGE = "#f15c35"
THEMES = {
    "dark": {"ink": "#e6edf3", "muted": "#8b949e", "faint": "#30363d", "tile": "#161b22", "tile_line": "#30363d"},
    "light": {"ink": "#1f2328", "muted": "#59636e", "faint": "#d1d9e0", "tile": "#f6f8fa", "tile_line": "#d1d9e0"},
}
SERIF = "Georgia, 'Times New Roman', serif"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

PHRASES = [
    "Interactive product designer and developer.",
    "I design the interface,",
    "question the interaction,",
    "and build the working product.",
]


def header(theme):
    t = THEMES[theme]
    w, h = 860, 210
    step = 3.4  # seconds each phrase stays
    total = step * len(PHRASES)
    full = 560
    lines = []
    for i, phrase in enumerate(PHRASES):
        # SMIL, not CSS: Safari does not animate a rect's width from CSS, and
        # without the clip every phrase showed at once. Each phrase is also
        # hidden by opacity outside its slot, so even a renderer that ignores
        # the clip never stacks them. With no animation at all, only the
        # first phrase shows.
        s0, s1 = i / len(PHRASES), (i + 1) / len(PHRASES)
        typed = s0 + (s1 - s0) * .32
        hold = s1 - .01
        times = [0, s0, typed, hold, s1, 1]
        widths = [0, 0, full, full, 0, 0]
        shown = [0, 1, 1, 1, 0, 0]
        pairs = sorted({t: (w, o) for t, w, o in zip(times, widths, shown)}.items())
        kt = ";".join(f"{t:.4f}" for t, _ in pairs)
        wv = ";".join(str(w) for _, (w, _) in pairs)
        ov = ";".join(str(o) for _, (_, o) in pairs)
        static_w = full if i == 0 else 0
        lines.append(
            f'<clipPath id="c{i}"><rect x="196" y="104" height="36" width="{static_w}">'
            f'<animate attributeName="width" values="{wv}" keyTimes="{kt}" dur="{total}s" repeatCount="indefinite"/></rect></clipPath>'
        )
        lines.append(
            f'<text x="196" y="130" clip-path="url(#c{i})" class="role" opacity="{1 if i == 0 else 0}">{escape(phrase)}'
            f'<animate attributeName="opacity" values="{ov}" keyTimes="{kt}" dur="{total}s" calcMode="discrete" repeatCount="indefinite"/></text>'
        )
    style = f"""
    .name {{ font: 700 46px {SERIF}; fill: {t['ink']}; letter-spacing: -1px; }}
    .role {{ font: 400 21px {SERIF}; font-style: italic; fill: {t['ink']}; }}
    .meta {{ font: 600 11.5px {MONO}; fill: {t['muted']}; letter-spacing: 1.6px; }}
    .mark {{ font: italic 400 44px {SERIF}; fill: #221e19; }}
    .grid {{ stroke: {t['faint']}; stroke-width: 1; opacity: .55; }}
    .drift {{ animation: drift 14s linear infinite; }}
    .accent {{ animation: grow 1.4s cubic-bezier(.22,1,.36,1) .2s both; transform-origin: 196px 0; }}
    .rise {{ animation: rise .9s cubic-bezier(.22,1,.36,1) both; }}
    .caret {{ animation: blink 1s steps(1) infinite; fill: {ORANGE}; }}
    .tile {{ animation: pop 1s cubic-bezier(.22,1.4,.36,1) both; transform-origin: 100px 100px; }}
    @keyframes drift {{ from {{ transform: translateX(0) }} to {{ transform: translateX(-40px) }} }}
    @keyframes grow {{ from {{ transform: scaleX(0) }} to {{ transform: scaleX(1) }} }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(10px) }} to {{ opacity: 1; transform: none }} }}
    @keyframes blink {{ 50% {{ opacity: 0 }} }}
    @keyframes pop {{ from {{ transform: scale(.6) rotate(-8deg); opacity: 0 }} to {{ transform: none; opacity: 1 }} }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
    """
    grid = "".join(f'<line class="grid" x1="{x}" y1="0" x2="{x}" y2="{h}"/>' for x in range(0, w + 80, 40))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Xavi Bosch, interactive product designer and developer">
<style>{style}</style>
<defs><linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".25" stop-color="#fff" stop-opacity="1"/><stop offset=".75" stop-color="#fff" stop-opacity="1"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="m"><rect width="{w}" height="{h}" fill="url(#fade)"/></mask></defs>
<g mask="url(#m)"><g class="drift">{grid}</g></g>
<g class="tile"><rect x="40" y="45" width="120" height="120" rx="30" fill="{ORANGE}"/><text x="58" y="124" class="mark">xb</text></g>
<g class="rise"><text x="196" y="82" class="name">Xavi Bosch</text></g>
<rect class="accent" x="196" y="94" width="56" height="3" rx="1.5" fill="{ORANGE}"/>
{''.join(lines)}
<g class="rise" style="animation-delay:.35s"><text x="196" y="168" class="meta">BARCELONA  /  DESIGN + CODE  /  OPEN TO INTERNSHIPS FROM JUNE 2027</text></g>
</svg>"""


GROUPS = [
    ("Design and research", ["figma"], ["User research", "Usability testing", "Prototyping"]),
    ("Frontend", ["react", "typescript", "javascript", "html5", "css3", "vite", "gsap"], []),
    ("Apple platforms", ["swift", "apple", "xcode"], []),
    ("Desktop and backend", ["electron", "node", "firebase", "python"], []),
    ("Vision and hardware", ["mediapipe", "opencv", "arduino", "espressif", "mqtt"], []),
    ("Ship and run", ["git", "github", "vercel", "ollama"], []),
]
LABELS = {"apple": "SwiftUI", "espressif": "ESP32", "gsap": "GSAP", "node": "Node.js", "css3": "CSS"}


def skills(theme):
    t = THEMES[theme]
    w = 860
    row_h = 92
    h = 24 + row_h * len(GROUPS)
    tile, gap, x0 = 58, 14, 210
    out, n = [], 0
    for r, (label, keys, words) in enumerate(GROUPS):
        y = 20 + r * row_h
        out.append(f'<g class="in" style="animation-delay:{r * .12:.2f}s"><text x="20" y="{y + 34}" class="group">{escape(label.upper())}</text></g>')
        out.append(f'<line x1="20" y1="{y + row_h - 8}" x2="{w - 20}" y2="{y + row_h - 8}" stroke="{t["faint"]}" stroke-width="1"/>')
        x = x0
        for k in keys:
            icon = ICONS[k]
            colour = "#" + icon["hex"]
            r_, g_, b_ = (int(icon["hex"][i:i + 2], 16) / 255 for i in (0, 2, 4))
            luminance = .2126 * r_ + .7152 * g_ + .0722 * b_
            # Brand colours too dark to read on the dark theme take the ink colour.
            if luminance < .12 or (theme == "dark" and luminance < .3):
                colour = t["ink"]
            name = LABELS.get(k, icon["title"])
            delay = r * .12 + n * .035
            out.append(
                f'<g class="pop" style="animation-delay:{delay:.2f}s"><g class="float" style="animation-delay:{(n % 7) * .4:.1f}s">'
                f'<rect x="{x}" y="{y}" width="{tile}" height="{tile}" rx="14" fill="{t["tile"]}" stroke="{t["tile_line"]}"/>'
                f'<g transform="translate({x + 17} {y + 17})"><path d="{icon["path"]}" fill="{colour}"/></g>'
                f'<text x="{x + tile / 2}" y="{y + tile + 14}" class="cap" text-anchor="middle">{escape(name)}</text></g></g>'
            )
            x += tile + gap
            n += 1
        for word in words:
            width = 13 + len(word) * 7.4
            delay = r * .12 + n * .035
            out.append(
                f'<g class="pop" style="animation-delay:{delay:.2f}s"><rect x="{x}" y="{y + 14}" width="{width:.0f}" height="30" rx="15" fill="none" stroke="{t["tile_line"]}"/>'
                f'<text x="{x + width / 2:.0f}" y="{y + 33}" class="chip" text-anchor="middle">{escape(word)}</text></g>'
            )
            x += width + 10
            n += 1
    style = f"""
    .group {{ font: 700 11px {MONO}; fill: {t['muted']}; letter-spacing: 1.4px; }}
    .cap {{ font: 500 10.5px {SANS}; fill: {t['muted']}; }}
    .chip {{ font: 600 12px {SANS}; fill: {t['ink']}; }}
    .pop {{ animation: pop .7s cubic-bezier(.22,1.3,.36,1) both; transform-box: fill-box; transform-origin: center; }}
    .in {{ animation: in .8s cubic-bezier(.22,1,.36,1) both; }}
    .float {{ animation: float 5s ease-in-out infinite; }}
    @keyframes pop {{ from {{ opacity: 0; transform: translateY(14px) scale(.8) }} to {{ opacity: 1; transform: none }} }}
    @keyframes in {{ from {{ opacity: 0; transform: translateX(-12px) }} to {{ opacity: 1; transform: none }} }}
    @keyframes float {{ 0%,100% {{ transform: translateY(0) }} 50% {{ transform: translateY(-3px) }} }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
    """
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Skills: Figma, React, TypeScript, JavaScript, HTML, CSS, Vite, GSAP, Swift, SwiftUI, Xcode, Electron, Node.js, Firebase, Python, MediaPipe, OpenCV, Arduino, ESP32, MQTT, Git, GitHub, Vercel, Ollama">
<style>{style}</style>
{''.join(out)}
</svg>"""


for theme in THEMES:
    (ROOT / "assets" / f"header-{theme}.svg").write_text(header(theme))
    (ROOT / "assets" / f"skills-{theme}.svg").write_text(skills(theme))
    print("wrote", f"assets/header-{theme}.svg", f"assets/skills-{theme}.svg")
