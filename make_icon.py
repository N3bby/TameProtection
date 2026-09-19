"""Generate package/icon.png - a 256x256 Thunderstore icon.

Rendered at 4x and downsampled for antialiasing. No external assets.
Motif: a Norse round shield (protection) carrying a boar (the iconic Valheim tame).
"""
from PIL import Image, ImageDraw

SS, OUT = 4, 256
S = OUT * SS

BG_EDGE   = (0x12, 0x0e, 0x0a)
BG_CORE   = (0x2a, 0x20, 0x17)
IRON_LIT  = (0x9a, 0x94, 0x86)
IRON_DIM  = (0x45, 0x41, 0x3a)
WOOD_LIT  = (0xcf, 0xa5, 0x6b)
WOOD_DIM  = (0x93, 0x6c, 0x3e)
SEAM      = (0x7d, 0x5a, 0x33)
GOLD      = (0xd9, 0xab, 0x4d)
INK       = (0x24, 0x1b, 0x13)

img = ImageDraw.Draw(base := Image.new("RGB", (S, S), BG_EDGE))
C = S / 2

def circle(d, cx, cy, r, **kw):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], **kw)

# --- background: radial falloff, drawn as concentric rings (fast, smooth enough) ---
steps = 120
for i in range(steps, 0, -1):
    t = i / steps
    col = tuple(round(BG_EDGE[c] + (BG_CORE[c] - BG_EDGE[c]) * (1 - t) ** 1.6) for c in range(3))
    circle(img, C, C, C * 1.42 * t, fill=col)

R_OUT = S * 0.455          # outer edge of the iron rim
R_WOOD = R_OUT * 0.855     # wood field
R_WARD = R_WOOD * 0.93     # thin gold ward ring

# --- iron rim: full ring, thin machined highlight, riveted ---
circle(img, C, C, R_OUT, fill=IRON_DIM)
circle(img, C, C, R_OUT * 0.985, outline=IRON_LIT, width=int(S * 0.006))

# --- wood field with plank seams, clipped to the disc ---
wood = Image.new("RGB", (S, S), WOOD_DIM)
wd = ImageDraw.Draw(wood)
for i in range(steps, 0, -1):          # gentle top-left sheen
    t = i / steps
    col = tuple(round(WOOD_DIM[c] + (WOOD_LIT[c] - WOOD_DIM[c]) * (1 - t) ** 1.3) for c in range(3))
    circle(wd, C - R_WOOD * 0.22, C - R_WOOD * 0.24, R_WOOD * 1.75 * t, fill=col)
for k in (-2, -1, 0, 1, 2):            # vertical planking
    x = C + k * R_WOOD * 0.42
    wd.line([(x, 0), (x, S)], fill=SEAM, width=int(S * 0.006))

mask = Image.new("L", (S, S), 0)
circle(ImageDraw.Draw(mask), C, C, R_WOOD, fill=255)
base.paste(wood, (0, 0), mask)

# --- rivets around the rim ---
import math
R_RIV = (R_OUT + R_WOOD) / 2
for i in range(10):
    a = math.radians(i * 36 - 90)
    circle(img, C + math.cos(a) * R_RIV, C + math.sin(a) * R_RIV,
           S * 0.011, fill=IRON_LIT)
    circle(img, C + math.cos(a) * R_RIV, C + math.sin(a) * R_RIV,
           S * 0.005, fill=IRON_DIM)

# --- gold ward ring ---
circle(img, C, C, R_WARD, outline=GOLD, width=int(S * 0.008))

# --- boar silhouette -------------------------------------------------------
# Normalised 0..100 box, facing left; body drawn as one polygon, limbs added
# as separate shapes so their union forms a single clean silhouette.
BX, BY, BW = C - S * 0.255, C - S * 0.165, S * 0.51
def P(pts):
    return [(BX + x / 100 * BW, BY + y / 100 * BW * 0.78) for x, y in pts]

body = P([
    (3, 60), (6, 50), (13, 43), (22, 37),          # snout -> face -> brow
    (30, 33), (37, 28), (46, 24),                  # neck rising to the shoulder
    (55, 23), (64, 25), (74, 29),                  # broad withers, back easing down
    (82, 34), (87, 42), (93, 44), (88, 51),        # rump and a short low tail
    (85, 60), (80, 69),                            # hindquarter
    (64, 74), (44, 76), (29, 71),                  # belly
    (17, 65), (8, 62),                             # chest -> jaw
])
img.polygon(body, fill=INK)

for lx, lw, top, bot in ((21, 10, 64, 91), (34, 10, 67, 89), (67, 10, 67, 89), (79, 10, 64, 91)):
    x0, y0 = P([(lx, top)])[0]
    x1, y1 = P([(lx + lw, bot)])[0]
    img.rounded_rectangle([x0, y0, x1, y1], radius=(x1 - x0) * 0.42, fill=INK)

img.polygon(P([(31, 31), (36, 20), (42, 29)]), fill=INK)          # ear
img.polygon(P([(10, 56), (1, 37), (7, 51), (16, 53)]), fill=(0xf2, 0xea, 0xd8))  # tusk
circle(img, *P([(20, 46)])[0], R_OUT * 0.026, fill=WOOD_LIT)     # eye

base.resize((OUT, OUT), Image.LANCZOS).save("package/icon.png", optimize=True)
print("wrote package/icon.png")
