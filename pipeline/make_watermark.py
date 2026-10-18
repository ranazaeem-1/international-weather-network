"""IWN frame art for an episode's graphics folder.

  python make_watermark.py <graphics dir> [--lang en|es]
      en (default): the lowercase iwn logo tile (English channel, Independent Weather Network)
      es          : "IWN" in capitals (Spanish channel, Instant Weather Network)
writes  background.png        - opaque dark frame with the faint tiled IWN logo: the fixed background every clip sits on
        sidebar_watermark.png - the same logo tile on transparency (only needed for the old blurred-sides look)
(a path ending in .png is also accepted, for older notes: both files are then written next to it)
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

KIT = Path(__file__).resolve().parents[1] / "iwn-brand-kit"
if not KIT.exists():
    KIT = Path(__file__).resolve().parents[3] / "iwn-brand-kit"
args = [a for a in sys.argv[1:] if not a.startswith("--")]
LANG = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "en"
if LANG not in ("en", "es"):
    raise SystemExit("--lang must be en or es")
args = [a for a in args if a not in ("en", "es")]
out = Path(args[0])
out = out.parent if out.suffix.lower() == ".png" else out
out.mkdir(parents=True, exist_ok=True)

w = 170
if LANG == "es":
    # Spanish channel: capital IWN, white, same tile width as the English logo
    f = ImageFont.truetype(str(KIT / "fonts/Manrope.ttf"), 200)
    f.set_variation_by_axes([800])          # ExtraBold, matching the weight of the lowercase logo
    bb = f.getbbox("IWN")
    big = Image.new("RGBA", (bb[2] - bb[0] + 8, bb[3] - bb[1] + 8), (0, 0, 0, 0))
    ImageDraw.Draw(big).text((4 - bb[0], 4 - bb[1]), "IWN", font=f, fill=(255, 255, 255, 255))
    logo = big
else:
    logo = Image.open(KIT / "logo-white-transparent.png").convert("RGBA")
logo = logo.resize((w, round(logo.height * w / logo.width)), Image.LANCZOS)


def tile(opacity):
    lg = logo.copy()
    lg.putalpha(lg.getchannel("A").point(lambda a: int(a * opacity)))
    canvas = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    for row, y in enumerate(range(40, 1080, 250)):
        for x in range(-150 + (row % 2) * 150, 1920, 300):
            if 0 <= x <= 1920 - lg.width and y <= 1080 - lg.height:
                canvas.alpha_composite(lg, (x, y))
    return canvas


tile(0.16).save(out / "sidebar_watermark.png")

# background: a dark blue-grey, clearly lighter than the lower-third panel (#17191D) so the graphics still stand out on it
bg = Image.new("RGB", (1920, 1080), (0x27, 0x2E, 0x39))
glow = Image.new("L", (192, 108), 0)
ImageDraw.Draw(glow).ellipse([-40, -30, 232, 138], fill=255)
glow = glow.resize((1920, 1080), Image.BICUBIC).point(lambda v: int(v * 0.35))
bg = Image.composite(Image.new("RGB", (1920, 1080), (0x3D, 0x47, 0x56)), bg, glow).convert("RGBA")
bg.alpha_composite(tile(0.06))
bg.convert("RGB").save(out / "background.png")
print("ok", out, LANG)
