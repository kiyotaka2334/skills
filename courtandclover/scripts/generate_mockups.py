#!/usr/bin/env python3
"""Generate placeholder product mockups (SVG) for Court & Clover.

Blueprint Part 3: product photography placeholder = flat mockups on cream
until the Comfort Colors sample arrives and is shot. These are deliberately
vector so they stay crisp and tiny (Lighthouse-friendly).

Run from the site root:  python3 scripts/generate_mockups.py
Writes into assets/.
"""

import os

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

CREAM_WELL = "#ECE5D4"   # image well, one step below page cream
PINE = "#1F3D2B"
BRASS = "#B8893E"
INK = "#222019"

GARMENT = {
    "ivory": {"fill": "#F0EAD9", "shade": "#E2DAC4"},
    "bay": {"fill": "#A9C0CB", "shade": "#96AEBA"},
    "lightgreen": {"fill": "#C4CEB5", "shade": "#B2BEA0"},
}

# Boxy garment-dyed tee, flat lay. viewBox 0 0 800 1000 (4:5).
TEE_PATH = (
    "M330,205 L250,228 L118,392 L162,452 L253,398 "
    "L246,862 Q246,872 256,872 L544,872 Q554,872 554,862 "
    "L547,398 L638,452 L682,392 L550,228 L470,205 "
    "Q400,262 330,205 Z"
)
COLLAR = (
    "M330,205 Q400,262 470,205 Q472,196 464,194 "
    "Q400,246 336,194 Q328,196 330,205 Z"
)


def tee(color, print_group, texture=False):
    g = GARMENT[color]
    texture_lines = ""
    if texture:
        lines = []
        for i in range(-10, 30):
            x = i * 40
            lines.append(
                f'<line x1="{x}" y1="0" x2="{x + 300}" y2="1000" '
                f'stroke="{INK}" stroke-opacity="0.04" stroke-width="6"/>'
            )
        texture_lines = "".join(lines)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000" role="img">
  <rect width="800" height="1000" fill="{CREAM_WELL}"/>
  <path d="{TEE_PATH}" fill="{g['fill']}" stroke="{g['shade']}" stroke-width="3"/>
  <path d="M253,398 L246,862" stroke="{g['shade']}" stroke-width="2" fill="none"/>
  <path d="M547,398 L554,862" stroke="{g['shade']}" stroke-width="2" fill="none"/>
  <path d="{COLLAR}" fill="{g['shade']}"/>
  {print_group}
  {texture_lines}
</svg>
"""


def clover(cx, cy, r, fill):
    """Four-leaf clover mark built from circles."""
    return (
        f'<g fill="{fill}">'
        f'<circle cx="{cx - r * 0.55}" cy="{cy - r * 0.55}" r="{r * 0.62}"/>'
        f'<circle cx="{cx + r * 0.55}" cy="{cy - r * 0.55}" r="{r * 0.62}"/>'
        f'<circle cx="{cx - r * 0.55}" cy="{cy + r * 0.55}" r="{r * 0.62}"/>'
        f'<circle cx="{cx + r * 0.55}" cy="{cy + r * 0.55}" r="{r * 0.62}"/>'
        f'<rect x="{cx - r * 0.09}" y="{cy}" width="{r * 0.18}" height="{r * 1.7}" rx="{r * 0.09}" '
        f'transform="rotate(18 {cx} {cy})"/>'
        f"</g>"
    )


def paddles(cx, cy, s, fill):
    """Two crossed pickleball paddles + ball. Rotation pivot sits at the
    handle end so the paddle heads swing apart and visibly cross."""
    piv_y = cy + s * 0.85
    return f"""<g stroke="{fill}" fill="none" stroke-width="{s * 0.09}">
  <g transform="rotate(-24 {cx} {piv_y})">
    <ellipse cx="{cx}" cy="{cy - s * 0.18}" rx="{s * 0.38}" ry="{s * 0.5}"/>
    <line x1="{cx}" y1="{cy + s * 0.32}" x2="{cx}" y2="{piv_y}" stroke-linecap="round"/>
  </g>
  <g transform="rotate(24 {cx} {piv_y})">
    <ellipse cx="{cx}" cy="{cy - s * 0.18}" rx="{s * 0.38}" ry="{s * 0.5}"/>
    <line x1="{cx}" y1="{cy + s * 0.32}" x2="{cx}" y2="{piv_y}" stroke-linecap="round"/>
  </g>
  <circle cx="{cx}" cy="{cy - s * 1.1}" r="{s * 0.16}" fill="{fill}" stroke="none"/>
</g>"""


SERIF = "Georgia, 'Times New Roman', serif"
SANS = "Helvetica, Arial, sans-serif"

PRINT_RATHER = f"""
  <defs><path id="arc" d="M212,492 Q400,380 588,492" fill="none"/></defs>
  <text font-family="{SANS}" font-size="30" font-weight="bold" letter-spacing="3" fill="{PINE}">
    <textPath href="#arc" startOffset="50%" text-anchor="middle">RATHER BE PLAYING</textPath>
  </text>
  {paddles(400, 580, 72, PINE)}
  <text x="400" y="700" font-family="{SANS}" font-size="20" letter-spacing="5"
        text-anchor="middle" fill="{BRASS}">COURT &amp; CLOVER</text>
"""

PRINT_KITCHEN = f"""
  <text x="400" y="470" font-family="{SANS}" font-size="26" font-weight="bold" letter-spacing="7"
        text-anchor="middle" fill="{PINE}">STAY OUT OF</text>
  <text x="400" y="560" font-family="{SERIF}" font-size="82" font-style="italic"
        text-anchor="middle" fill="{PINE}">the kitchen</text>
  <line x1="320" y1="596" x2="480" y2="596" stroke="{BRASS}" stroke-width="3"/>
  <text x="400" y="640" font-family="{SANS}" font-size="19" letter-spacing="4"
        text-anchor="middle" fill="{PINE}">A PICKLEBALL HOUSE RULE</text>
"""

PRINT_DINK = f"""
  <text x="400" y="510" font-family="{SERIF}" font-size="110" font-weight="bold"
        text-anchor="middle" fill="{PINE}">Dink</text>
  <text x="400" y="565" font-family="{SANS}" font-size="30" letter-spacing="10"
        text-anchor="middle" fill="{PINE}">RESPONSIBLY</text>
  {clover(400, 640, 26, BRASS)}
"""

PRINT_CREST = f"""
  <circle cx="400" cy="540" r="170" fill="none" stroke="{PINE}" stroke-width="5"/>
  <circle cx="400" cy="540" r="150" fill="none" stroke="{PINE}" stroke-width="2"/>
  <defs>
    <path id="crestTop" d="M282,570 A125,125 0 1 1 518,570" fill="none"/>
    <path id="crestBot" d="M295,585 A118,118 0 0 0 505,585" fill="none"/>
  </defs>
  <text font-family="{SANS}" font-size="27" font-weight="bold" letter-spacing="6" fill="{PINE}">
    <textPath href="#crestTop" startOffset="50%" text-anchor="middle">COURT &amp; CLOVER</textPath>
  </text>
  <text font-family="{SANS}" font-size="20" letter-spacing="5" fill="{PINE}">
    <textPath href="#crestBot" startOffset="50%" text-anchor="middle">PICKLEBALL CLUB</textPath>
  </text>
  <text x="400" y="560" font-family="{SERIF}" font-size="86" font-weight="bold"
        text-anchor="middle" fill="{PINE}">C&amp;C</text>
  {clover(400, 615, 22, BRASS)}
"""


def detail_crop():
    """Close crop of the print texture (gallery image 2)."""
    inner = tee("ivory", PRINT_RATHER, texture=True)
    body = inner.split(">", 1)[1].rsplit("</svg>", 1)[0]
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="180 360 448 560" role="img">'
        + body
        + "</svg>\n"
    )


def flatlay():
    """Size-context shot: tee with measurement props (gallery image 3)."""
    base = tee("ivory", PRINT_RATHER)
    body = base.split(">", 1)[1].rsplit("</svg>", 1)[0]
    props = f"""
  <g stroke="{BRASS}" stroke-width="3" fill="none">
    <line x1="246" y1="930" x2="554" y2="930"/>
    <line x1="246" y1="918" x2="246" y2="942"/>
    <line x1="554" y1="918" x2="554" y2="942"/>
    <line x1="620" y1="228" x2="620" y2="872"/>
    <line x1="608" y1="228" x2="632" y2="228"/>
    <line x1="608" y1="872" x2="632" y2="872"/>
  </g>
  <text x="400" y="975" font-family="{SANS}" font-size="26" letter-spacing="3"
        text-anchor="middle" fill="{INK}">20 in wide (size M)</text>
  <text x="660" y="556" font-family="{SANS}" font-size="26" letter-spacing="3"
        fill="{INK}" transform="rotate(90 660 556)" text-anchor="middle">28 in long</text>
"""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000" role="img">'
        + body
        + props
        + "</svg>\n"
    )


FILES = {
    "tee-rather-ivory.svg": tee("ivory", PRINT_RATHER),
    # per-color variants so PDP swatches can swap the garment image
    "tee-rather-bay.svg": tee("bay", PRINT_RATHER),
    "tee-rather-lightgreen.svg": tee("lightgreen", PRINT_RATHER),
    "tee-rather-detail.svg": detail_crop(),
    "tee-rather-flatlay.svg": flatlay(),
    "tee-kitchen-bay.svg": tee("bay", PRINT_KITCHEN),
    "tee-dink-lightgreen.svg": tee("lightgreen", PRINT_DINK),
    "tee-crest-ivory.svg": tee("ivory", PRINT_CREST),
}

FILES["favicon.svg"] = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="8" fill="{PINE}"/>
  {clover(32, 30, 11, "#F4EFE4")}
</svg>
"""

FILES["og-image.svg"] = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" role="img">
  <rect width="1200" height="630" fill="#F4EFE4"/>
  <line x1="510" y1="180" x2="690" y2="180" stroke="{BRASS}" stroke-width="3"/>
  <text x="600" y="330" font-family="{SERIF}" font-size="96" font-weight="bold"
        text-anchor="middle" fill="{PINE}">Court &amp; Clover</text>
  <text x="600" y="410" font-family="{SANS}" font-size="30" letter-spacing="8"
        text-anchor="middle" fill="{INK}">PREMIUM PICKLEBALL &amp; GOLF GIFTS</text>
  {clover(600, 500, 24, BRASS)}
</svg>
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, content in FILES.items():
        with open(os.path.join(OUT, name), "w") as f:
            f.write(content)
        print(f"wrote assets/{name}")


if __name__ == "__main__":
    main()
