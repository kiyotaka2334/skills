#!/usr/bin/env python3
"""Generate photorealistic studio product mockups for Court & Clover.

Builds each tee as a studio flat-lay photograph: a clean boxy silhouette
with real cotton-jersey micro-texture (sampled from a public-domain garment
photo, scripts/fabric-source.jpg), soft form shading, seams, a ribbed
collar, gentle fabric folds, and a drop shadow on a warm studio backdrop.
Each design print is typeset with the brand's real fonts (Playfair Display
/ Inter) and composited with multiply blending so it inherits the fabric.

Fonts: pass --fonts DIR containing PlayfairDisplay.ttf,
PlayfairDisplay-Italic.ttf, Inter.ttf (variable TTFs from google/fonts).

Run from the site root:
    python3 scripts/generate_photo_mockups.py --fonts /path/to/fonts
Writes assets/photo-tee-<design>-<color>.jpg (+ -detail.jpg per design).
"""

import argparse
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "assets")

PINE = (31, 61, 43)
BRASS = (184, 137, 62)

# garment colors (fabric base, slightly off for realism)
COLORS = {
    "white": (248, 246, 241),
    "bay": (169, 192, 203),
    "lightgreen": (196, 206, 181),
}

# working size 1600x2000 (4:5); silhouette drawn 2x supersampled
W, H = 1600, 2000
SS = 2

# tee outline in the original 800x1000 design space — boxy CC1717 cut
TEE_SEGMENTS = [
    ("L", (326, 200), (242, 226)),
    ("L", (242, 226), (108, 386)),
    ("L", (108, 386), (152, 452)),
    ("L", (152, 452), (232, 402)),
    ("Q", (232, 402), (226, 500), (226, 560)),
    ("L", (226, 560), (228, 850)),
    ("Q", (228, 850), (228, 862), (240, 862)),
    ("L", (240, 862), (560, 862)),
    ("Q", (560, 862), (572, 862), (572, 850)),
    ("L", (572, 850), (574, 560)),
    ("Q", (574, 560), (568, 500), (568, 402)),
    ("L", (568, 402), (648, 452)),
    ("L", (648, 452), (692, 386)),
    ("L", (692, 386), (558, 226)),
    ("L", (558, 226), (474, 200)),
    ("Q", (474, 200), (400, 258), (326, 200)),
]

# underarm/shoulder anchors used by shading layers
SHOULDER_L, SHOULDER_R = (242, 226), (558, 226)
UNDERARM_L, UNDERARM_R = (232, 402), (568, 402)


def sample_outline(scale):
    pts = []
    for seg in TEE_SEGMENTS:
        if seg[0] == "L":
            pts.append(seg[1])
            pts.append(seg[2])
        else:
            (x0, y0), (cx, cy), (x1, y1) = seg[1], seg[2], seg[3]
            for i in range(13):
                t = i / 12
                x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x1
                y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y1
                pts.append((x, y))
    return [(x * scale, y * scale) for x, y in pts]


def tee_mask():
    s = W / 800 * SS
    im = Image.new("L", (W * SS, H * SS), 0)
    ImageDraw.Draw(im).polygon(sample_outline(s), fill=255)
    return im.resize((W, H), Image.LANCZOS)


def quad_points(p0, c, p1, n=24):
    return [
        (
            (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t ** 2 * p1[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t ** 2 * p1[1],
        )
        for t in (i / n for i in range(n + 1))
    ]


def fabric_texture():
    """Real cotton micro-texture: high-pass of the source garment photo."""
    src = ImageOps.exif_transpose(Image.open(os.path.join(HERE, "fabric-source.jpg"))).convert("L")
    # clean fabric area of the source tee (lower body, no embroidery)
    tile = src.crop((150, 620, 470, 940))
    a = np.asarray(tile, dtype=np.float32)
    blur = np.asarray(tile.filter(ImageFilter.GaussianBlur(14)), dtype=np.float32)
    hp = a - blur  # centered on 0
    hp = np.clip(hp * 1.4, -28, 28)
    t = Image.fromarray((hp + 128).astype(np.uint8))
    # mirror-tile to full canvas so seams vanish
    tw, th = t.size
    canvas = Image.new("L", (W, H))
    for j in range(0, H, th):
        for i in range(0, W, tw):
            tt = t
            if (i // tw) % 2:
                tt = ImageOps.mirror(tt)
            if (j // th) % 2:
                tt = ImageOps.flip(tt)
            canvas.paste(tt, (i, j))
    return np.asarray(canvas, dtype=np.float32) - 128.0  # zero-centered


def studio_background():
    """Warm studio sweep with a soft radial falloff and fine grain."""
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H * 0.42
    d = np.sqrt(((x - cx) / (W * 0.75)) ** 2 + ((y - cy) / (H * 0.85)) ** 2)
    fall = np.clip(d, 0, 1) ** 1.6
    base = np.array((241, 236, 225), dtype=np.float32)
    edge = np.array((222, 214, 196), dtype=np.float32)
    bg = base[None, None, :] * (1 - fall[..., None]) + edge[None, None, :] * fall[..., None]
    grain = np.random.default_rng(7).normal(0, 1.6, (H, W, 1)).astype(np.float32)
    return np.clip(bg + grain, 0, 255)


def fold_shading(rng):
    """Soft fabric folds: paired dark/light blurred strokes."""
    dark = Image.new("L", (W, H), 0)
    light = Image.new("L", (W, H), 0)
    dd, dl = ImageDraw.Draw(dark), ImageDraw.Draw(light)
    body_x0, body_x1 = 500, 1100
    for i in range(6):
        y0 = rng.uniform(950, 1680)
        amp = rng.uniform(-70, 70)
        x0 = body_x0 + rng.uniform(-60, 40)
        x1 = body_x1 + rng.uniform(-40, 60)
        pts = quad_points((x0, y0), ((x0 + x1) / 2, y0 + amp), (x1, y0 + rng.uniform(-40, 40)))
        wd = rng.uniform(10, 22)
        dd.line(pts, fill=int(rng.uniform(90, 150)), width=int(wd))
        dl.line([(px, py - wd * 1.4) for px, py in pts], fill=int(rng.uniform(60, 110)), width=int(wd))
    # diagonal stress folds from the sleeves toward the chest
    for sx, ex in ((330, 640), (1270, 960)):
        pts = quad_points((sx, 800), ((sx + ex) / 2, 870), (ex, rng.uniform(920, 980)))
        dd.line(pts, fill=105, width=16)
        dl.line([(px, py - 22) for px, py in pts], fill=80, width=14)
    dark = dark.filter(ImageFilter.GaussianBlur(26))
    light = light.filter(ImageFilter.GaussianBlur(30))
    return (
        np.asarray(dark, dtype=np.float32) / 255.0,
        np.asarray(light, dtype=np.float32) / 255.0,
    )


def seam_layer():
    """Stitch lines: shoulder seams, sleeve hems, bottom double-hem, sides."""
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    s = W / 800
    def L(a, b, w=3, v=70):
        d.line([(a[0] * s, a[1] * s), (b[0] * s, b[1] * s)], fill=v, width=w)
    # sleeve joins (shoulder point to underarm, slightly curved via two legs)
    L(SHOULDER_L, (238, 320), 4, 85); L((238, 320), UNDERARM_L, 4, 85)
    L(SHOULDER_R, (562, 320), 4, 85); L((562, 320), UNDERARM_R, 4, 85)
    # sleeve hems (inside the cuff edge)
    L((122, 396), (164, 458), 3, 70)
    L((678, 396), (636, 458), 3, 70)
    # bottom double hem
    L((232, 830), (568, 830), 3, 75)
    L((232, 842), (568, 842), 2, 55)
    # side seams
    L((231, 424), (229, 848), 2, 45)
    L((569, 424), (571, 848), 2, 45)
    return np.asarray(im.filter(ImageFilter.GaussianBlur(1.6)), dtype=np.float32) / 255.0


def sleeve_shading():
    """Separate the sleeve plane from the body: soft shadow along the join
    (body side) and a gentle lift on the sleeve top edge."""
    dark = Image.new("L", (W, H), 0)
    light = Image.new("L", (W, H), 0)
    dd, dl = ImageDraw.Draw(dark), ImageDraw.Draw(light)
    s = W / 800
    for (sh, ua, top) in ((SHOULDER_L, UNDERARM_L, (108, 386)), (SHOULDER_R, UNDERARM_R, (692, 386))):
        # shadow cast by the sleeve onto the body, hugging the seam
        dd.line([(sh[0] * s, sh[1] * s), (sh[0] * s - (sh[0] - ua[0]) * 0.2 * s, (sh[1] + 90) * s),
                 (ua[0] * s, ua[1] * s)], fill=110, width=26, joint="curve")
        # sleeve underside falls away
        mid = ((sh[0] + top[0]) / 2, (sh[1] + top[1]) / 2 + 40)
        dd.line([(sh[0] * s, (sh[1] + 60) * s), (mid[0] * s, mid[1] * s), (top[0] * s + (10 if top[0] < 400 else -10), (top[1] + 30) * s)],
                fill=70, width=42, joint="curve")
        # light catches the sleeve's top fold
        dl.line([(sh[0] * s, (sh[1] + 12) * s), (top[0] * s, (top[1] - 4) * s)], fill=70, width=16)
    dark = dark.filter(ImageFilter.GaussianBlur(22))
    light = light.filter(ImageFilter.GaussianBlur(18))
    return (
        np.asarray(dark, dtype=np.float32) / 255.0,
        np.asarray(light, dtype=np.float32) / 255.0,
    )


def collar_layers():
    """Ribbed collar: a band just inside the neckline, its seam line,
    and the soft shadow it casts on the chest."""
    band = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(band)
    s = W / 800
    outer = quad_points((326 * s, 202 * s), (400 * s, 260 * s), (474 * s, 202 * s), 40)
    inner = quad_points((466 * s, 206 * s), (400 * s, 240 * s), (334 * s, 206 * s), 40)
    d.polygon(outer + inner, fill=255)
    band = band.filter(ImageFilter.GaussianBlur(1.2))
    # collar seam: crisp line where the band is stitched to the body
    seam = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(seam)
    dr.line(quad_points((328 * s, 204 * s), (400 * s, 262 * s), (472 * s, 204 * s), 40), fill=90, width=4)
    seam = seam.filter(ImageFilter.GaussianBlur(1.4))
    shadow = Image.new("L", (W, H), 0)
    ds = ImageDraw.Draw(shadow)
    ds.line(quad_points((334 * s, 212 * s), (400 * s, 272 * s), (466 * s, 212 * s), 40), fill=120, width=12)
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    return (
        np.asarray(band, dtype=np.float32) / 255.0,
        np.asarray(seam, dtype=np.float32) / 255.0,
        np.asarray(shadow, dtype=np.float32) / 255.0,
    )


# ---------------------------------------------------------------- prints

def font(path_dir, name, size, weight=None):
    f = ImageFont.truetype(os.path.join(path_dir, name), size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def draw_tracked(d, xy, text, f, fill, tracking, anchor="mm"):
    """Letter-spaced text centered on xy."""
    widths = [d.textlength(ch, font=f) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = xy[0] - total / 2
    for ch, w in zip(text, widths):
        d.text((x, xy[1]), ch, font=f, fill=fill, anchor="lm")
        x += w + tracking


def draw_arc_text(im, center, radius, text, f, fill, tracking, top=True):
    """Per-character text along a circular arc."""
    d = ImageDraw.Draw(im)
    widths = [d.textlength(ch, font=f) for ch in text]
    arc_len = sum(widths) + tracking * (len(text) - 1)
    total_ang = arc_len / radius
    a = (-math.pi / 2 - total_ang / 2) if top else (math.pi / 2 + total_ang / 2)
    step = 1 if top else -1
    for ch, w in zip(text, widths):
        ang = a + step * (w / 2 + (tracking if ch != text[0] else 0) * 0) / radius
        a_mid = a + step * (w / 2) / radius
        x = center[0] + radius * math.cos(a_mid)
        y = center[1] + radius * math.sin(a_mid)
        deg = math.degrees(a_mid) + (90 if top else -90)
        glyph = Image.new("RGBA", (int(w * 3) + 8, f.size * 3), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glyph)
        gd.text((glyph.width / 2, glyph.height / 2), ch, font=f, fill=fill, anchor="mm")
        glyph = glyph.rotate(-deg, resample=Image.BICUBIC, expand=True)
        im.alpha_composite(glyph, (int(x - glyph.width / 2), int(y - glyph.height / 2)))
        a = a + step * (w + tracking) / radius


def draw_clover(d, cx, cy, r, fill):
    for dx, dy in ((-0.55, -0.55), (0.55, -0.55), (-0.55, 0.55), (0.55, 0.55)):
        d.ellipse([cx + dx * r - r * 0.62, cy + dy * r - r * 0.62,
                   cx + dx * r + r * 0.62, cy + dy * r + r * 0.62], fill=fill)
    d.line([(cx, cy + r * 0.3), (cx + r * 0.55, cy + r * 1.7)], fill=fill, width=max(2, int(r * 0.18)))


def draw_paddles(d, cx, cy, s, fill):
    wline = max(3, int(s * 0.09))
    for rot in (-24, 24):
        a = math.radians(rot)
        piv = (cx, cy + s * 0.85)
        def T(px, py):
            px, py = px - piv[0], py - piv[1]
            return (piv[0] + px * math.cos(a) - py * math.sin(a),
                    piv[1] + px * math.sin(a) + py * math.cos(a))
        # ellipse head approximated by polygon, rotated around the pivot
        head = [T(cx + s * 0.38 * math.cos(t), cy - s * 0.18 + s * 0.5 * math.sin(t))
                for t in (i / 40 * 2 * math.pi for i in range(41))]
        d.line(head + [head[0]], fill=fill, width=wline, joint="curve")
        d.line([T(cx, cy + s * 0.32), piv], fill=fill, width=wline)
    d.ellipse([cx - s * 0.16, cy - s * 1.1 - s * 0.16, cx + s * 0.16, cy - s * 1.1 + s * 0.16], fill=fill)


def render_print(design, fonts_dir):
    """Each design typeset on a transparent 1200x1200 canvas."""
    im = Image.new("RGBA", (1200, 1200), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pine = PINE + (255,)
    brass = BRASS + (255,)
    inter_b = lambda size: font(fonts_dir, "Inter.ttf", size, 700)
    inter_m = lambda size: font(fonts_dir, "Inter.ttf", size, 500)
    play_b = lambda size: font(fonts_dir, "PlayfairDisplay.ttf", size, 700)
    play_i = lambda size: font(fonts_dir, "PlayfairDisplay-Italic.ttf", size, 560)

    if design == "rather":
        draw_arc_text(im, (600, 1080), 700, "RATHER BE PLAYING", inter_b(74), pine, 14, top=True)
        draw_paddles(d, 600, 660, 170, pine)
        draw_tracked(d, (600, 950), "COURT & CLOVER", inter_m(44), brass, 14)
    elif design == "kitchen":
        draw_tracked(d, (600, 330), "STAY OUT OF", inter_b(62), pine, 20)
        d.text((600, 520), "the kitchen", font=play_i(190), fill=pine, anchor="mm")
        d.line([(430, 650), (770, 650)], fill=brass, width=7)
        draw_tracked(d, (600, 740), "A PICKLEBALL HOUSE RULE", inter_m(42), pine, 12)
    elif design == "dink":
        d.text((600, 400), "Dink", font=play_b(280), fill=pine, anchor="mm")
        draw_tracked(d, (600, 610), "RESPONSIBLY", inter_b(66), pine, 26)
        draw_clover(d, 600, 800, 56, brass)
    elif design == "crest":
        d.ellipse([220, 220, 980, 980], outline=pine, width=11)
        d.ellipse([265, 265, 935, 935], outline=pine, width=4)
        draw_arc_text(im, (600, 600), 275, "COURT & CLOVER", inter_b(60), pine, 16, top=True)
        draw_arc_text(im, (600, 600), 270, "PICKLEBALL CLUB", inter_m(46), pine, 14, top=False)
        d.text((600, 570), "C&C", font=play_b(200), fill=pine, anchor="mm")
        draw_clover(d, 600, 730, 46, brass)
    return im


# ---------------------------------------------------------------- compose

def compose(design, color_name, fonts_dir, cache):
    rng = random.Random(hash(design) % 10_000)
    nprng = np.random.default_rng(abs(hash(design)) % 10_000)

    if "static" not in cache:
        cache["static"] = {
            "mask": np.asarray(tee_mask(), dtype=np.float32) / 255.0,
            "tex": fabric_texture(),
            "bg": studio_background(),
            "seams": seam_layer(),
            "collar": collar_layers(),
            "sleeves": sleeve_shading(),
        }
    st = cache["static"]
    mask, tex, bg = st["mask"], st["tex"], st["bg"]
    seams = st["seams"]
    band, collar_seam, collar_shadow = st["collar"]
    sleeve_dark, sleeve_light = st["sleeves"]
    dark, light = fold_shading(rng)

    base = np.array(COLORS[color_name], dtype=np.float32)
    tee = np.ones((H, W, 3), dtype=np.float32) * base[None, None, :]

    # print (multiply blend so ink sits in the fabric) — chest placement
    pr = render_print(design, fonts_dir)
    pw = int(W * 0.335)
    box = (int((W - pw) / 2), int(H * 0.295), pw, pw)  # x, y, w, h
    pr = pr.resize((box[2], box[3]), Image.LANCZOS)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.alpha_composite(pr, (box[0], box[1]))
    pa = np.asarray(layer, dtype=np.float32)
    alpha = (pa[..., 3:4] / 255.0) * 0.93  # slight ink transparency
    ink = pa[..., :3]
    tee = tee * (1 - alpha) + (tee * ink / 255.0) * alpha

    # real fabric micro-texture (soft-light-ish)
    tee = np.clip(tee + tex[..., None] * 0.55, 0, 255)

    # form shading: edges curve away (kept tight so planes stay readable)
    from PIL import Image as _I
    mask_img = _I.fromarray((mask * 255).astype(np.uint8))
    inner = np.asarray(mask_img.filter(ImageFilter.GaussianBlur(30)), dtype=np.float32) / 255.0
    edge = np.clip(mask - inner, 0, 1)
    tee *= (1 - 0.22 * edge)[..., None]

    # sleeves read as their own plane
    tee *= (1 - 0.14 * sleeve_dark)[..., None]
    tee = np.clip(tee * (1 + 0.08 * sleeve_light)[..., None], 0, 255)

    # folds
    tee *= (1 - 0.15 * dark)[..., None]
    tee = np.clip(tee * (1 + 0.09 * light)[..., None], 0, 255)

    # seams + collar
    tee *= (1 - 0.5 * seams)[..., None]
    tee *= (1 - 0.30 * collar_shadow)[..., None]
    collar_col = base * 0.94
    tee = tee * (1 - band[..., None]) + collar_col[None, None, :] * band[..., None]
    tee = np.clip(tee + tex[..., None] * 0.4 * band[..., None], 0, 255)
    tee *= (1 - 0.5 * collar_seam)[..., None]

    # grain
    tee = np.clip(tee + nprng.normal(0, 1.1, (H, W, 1)).astype(np.float32), 0, 255)

    # drop shadow on backdrop
    sh = mask_img.filter(ImageFilter.GaussianBlur(4))
    sh = sh.transform((W, H), Image.AFFINE, (1, 0, -10, 0, 1, -34))
    sh = np.asarray(sh.filter(ImageFilter.GaussianBlur(42)), dtype=np.float32) / 255.0
    out = bg * (1 - 0.34 * sh)[..., None]

    # composite tee with a feathered edge
    soft = np.asarray(mask_img.filter(ImageFilter.GaussianBlur(1.2)), dtype=np.float32) / 255.0
    out = out * (1 - soft[..., None]) + tee * soft[..., None]

    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    final = img.resize((800, 1000), Image.LANCZOS)
    name = f"photo-tee-{design}-{color_name}.jpg"
    final.save(os.path.join(OUT, name), quality=90)

    detail = None
    if color_name == "white":
        crop = img.crop((int(W * 0.24), int(H * 0.31), int(W * 0.72), int(H * 0.61)))
        detail = crop.resize((800, 500), Image.LANCZOS).resize((800, 1000), Image.LANCZOS)
        # keep 4:5 by cropping a square-ish zone instead
        crop = img.crop((int(W * 0.26), int(H * 0.30), int(W * 0.70), int(H * 0.85)))
        detail = crop.resize((800, 1000), Image.LANCZOS)
        detail.save(os.path.join(OUT, f"photo-tee-{design}-detail.jpg"), quality=90)
    return name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", required=True, help="dir with PlayfairDisplay/Inter TTFs")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cache = {}
    for design in ("rather", "kitchen", "dink", "crest"):
        for color in COLORS:
            print("wrote", compose(design, color, args.fonts, cache))


if __name__ == "__main__":
    main()
