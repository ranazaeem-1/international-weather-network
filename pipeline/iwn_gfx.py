"""Shared drawing helpers for make_intro.py and make_cards.py (IWN card look, 21 Oct 2026).

Look taken from the user's Outer Banks video (youtube.com/watch?v=Bsw35dVmjLo): dark navy radial background, red pill
top-left, bold condensed white headline (Anton), Manrope for everything else, iwn logo top-right, small grey source line
bottom-left. Frames are drawn with Pillow (2x supersampled sprites) and piped to ffmpeg, like build_graphics.py.
"""
import math, subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
W, H, FPS = 1920, 1080, 30
SS = 2                                                   # supersampling for sprites

# brand colours (build_graphics.py) + card palette sampled from the reference video
WH = (0xF5, 0xF2, 0xEB)
RED = (0xEF, 0x34, 0x3D)
DARK = (0x17, 0x19, 0x1D)
NAVY_C, NAVY_E = (37, 46, 58), (23, 30, 40)              # radial background: centre, edges
OCEAN = (25, 32, 42)
LAND = (52, 64, 79)
LAND_EDGE = (72, 86, 103)
STATE = (78, 92, 109)
BORDER = (104, 118, 136)
GREY = (150, 156, 164)
SOURCE = (112, 120, 130)
AMBER = (233, 160, 48)
BLUE = (64, 156, 255)
COLORS = {"red": RED, "amber": AMBER, "orange": (240, 120, 40), "yellow": (240, 200, 60), "blue": BLUE,
          "white": WH, "grey": GREY, "green": (70, 190, 120), "purple": (170, 110, 230)}

# card layout (1920x1080, measured on the reference)
MARGIN_X = 96
PILL_Y, PILL_H = 86, 40
HEAD_BASE = 208                                          # headline baseline
SUB_Y = 238                                              # top of the sub-line box
SOURCE_BASE = 836
LOGO_BOX = (1696, 44, 164)                               # x, y, width of the top-right logo
SAFE_BOTTOM = 880                                        # the headline ticker covers 930-1036: keep content above


def kit_dir():
    """iwn-brand-kit/ next to pipeline/ (template) or two levels above an episode's project/ folder."""
    for base in (HERE.parent, HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent):
        if (base / "iwn-brand-kit").exists():
            return base / "iwn-brand-kit"
    raise SystemExit("iwn-brand-kit/ not found next to pipeline/ or above the episode folder")


def geo_file():
    for p in (HERE / "geo/natural_earth_10m.npz", HERE.parents[2] / "pipeline/geo/natural_earth_10m.npz" if len(HERE.parents) > 2 else None):
        if p and p.exists():
            return p
    raise SystemExit("pipeline/geo/natural_earth_10m.npz not found (bundled Natural Earth map data)")


@lru_cache(None)
def font(size, kind="bold"):
    """kind: anton | bold | semibold | medium | regular | light (Manrope variable font)."""
    k = kit_dir() / "fonts"
    if kind == "anton":
        return ImageFont.truetype(str(k / "Anton-Regular.ttf"), int(round(size)))
    f = ImageFont.truetype(str(k / "Manrope.ttf"), int(round(size)))
    f.set_variation_by_name({"bold": "Bold", "semibold": "SemiBold", "medium": "Medium", "regular": "Regular",
                             "light": "Light", "extrabold": "ExtraBold"}[kind])
    return f


def text_w(s, size, kind="bold"):
    return font(size * SS, kind).getlength(s) / SS


def ease_out(t):
    t = min(1.0, max(0.0, t))
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    t = min(1.0, max(0.0, t))
    return 3 * t * t - 2 * t * t * t


def back_out(t, s=1.9):
    """Overshoot pop (pins, dots)."""
    t = min(1.0, max(0.0, t))
    if t <= 0:
        return 0.0
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def rgba(c, a=255):
    return tuple(c[:3]) + (int(a),)


# ---- sprites: small RGBA images drawn at SS and scaled down once ---------------------------------------------------
class Sprite:
    """Draw in 1x coordinates on an SS canvas; .img is the 1x result. (ax, ay) is the anchor inside the sprite."""
    def __init__(self, w, h, ax=0, ay=0):
        self.w, self.h, self.ax, self.ay = int(math.ceil(w)), int(math.ceil(h)), ax, ay
        self.big = Image.new("RGBA", (self.w * SS, self.h * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.big)
        self._img = None

    def rect(self, x, y, w, h, c, r=0, a=255):
        if w < 0.5 or h < 0.5:
            return
        self.d.rounded_rectangle([x * SS, y * SS, (x + w) * SS - 1, (y + h) * SS - 1], radius=max(0, min(r, w / 2, h / 2)) * SS,
                                 fill=rgba(c, a))

    def circle(self, x, y, r, c, a=255, outline=None, width=0):
        self.d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=rgba(c, a) if c else None,
                       outline=rgba(outline) if outline else None, width=int(width * SS))

    def text(self, x, y, size, s, c, kind="bold", anchor="ls", a=255):
        self.d.text((x * SS, y * SS), s, font=font(size * SS, kind), fill=rgba(c, a), anchor=anchor)

    def line(self, pts, c, width, a=255):
        self.d.line([(x * SS, y * SS) for x, y in pts], fill=rgba(c, a), width=int(round(width * SS)), joint="curve")
        for x, y in (pts[0], pts[-1]):                              # round caps
            self.circle(x, y, width / 2, c, a)

    def arc(self, x, y, r, a0, a1, c, width):
        self.d.arc([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], a0, a1, fill=rgba(c), width=int(width * SS))

    def polygon(self, pts, c, a=255):
        self.d.polygon([(x * SS, y * SS) for x, y in pts], fill=rgba(c, a))

    @property
    def img(self):
        if self._img is None:
            self._img = self.big.resize((self.w, self.h), Image.LANCZOS)
        return self._img


def paste(frame, img, x, y, opacity=1.0, scale=1.0, ax=0, ay=0):
    """Alpha-composite img onto the PIL RGBA/RGB frame with its anchor (ax, ay) at (x, y)."""
    if opacity <= 0.003 or scale <= 0.01:
        return
    if abs(scale - 1) > 0.01:
        img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.BICUBIC)
        ax, ay = ax * scale, ay * scale
    if opacity < 0.997:
        img = img.copy()
        img.putalpha(img.getchannel("A").point(lambda v: int(v * opacity)))
    x0, y0 = int(round(x - ax)), int(round(y - ay))
    if frame.mode == "RGBA":
        frame.alpha_composite(img, (max(0, x0), max(0, y0)), (max(0, -x0), max(0, -y0)))
    else:
        frame.paste(img, (x0, y0), img)


# ---- background, logo, chrome -------------------------------------------------------------------------------------
@lru_cache(None)
def background():
    """Dark navy radial gradient (RGB 1920x1080)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W * 0.5) / (W * 0.62)) ** 2 + ((yy - H * 0.45) / (H * 0.75)) ** 2)
    t = np.clip(d, 0, 1)[..., None] ** 1.4
    c = np.array(NAVY_C, np.float32) * (1 - t) + np.array(NAVY_E, np.float32) * t
    noise = np.random.default_rng(7).normal(0, 0.9, (H, W, 1))           # tiny grain against banding
    return Image.fromarray(np.clip(c + noise, 0, 255).astype(np.uint8), "RGB")


@lru_cache(None)
def logo_parts():
    """(letters, dot) as RGBA images from logo-white-transparent.png (904x448: dot on top, letters below row 130)."""
    im = Image.open(kit_dir() / "logo-white-transparent.png").convert("RGBA")
    dot, letters = im.crop((0, 0, im.width, 130)), im.crop((0, 130, im.width, im.height))
    return letters.crop(letters.getbbox()), dot.crop(dot.getbbox()), im.crop(im.getbbox())


@lru_cache(None)
def logo(width, shadow=True):
    """Full iwn logo (letters + red dot) at the given width, with a soft dark halo like the corner watermark."""
    full = logo_parts()[2]
    lg = full.resize((width, round(full.height * width / full.width)), Image.LANCZOS)
    if not shadow:
        return lg
    pad = 16
    out = Image.new("RGBA", (lg.width + 2 * pad, lg.height + 2 * pad), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(lg.getchannel("A"), (pad, pad))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 255))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * 0.55)))
    out.alpha_composite(sh)
    out.alpha_composite(lg, (pad, pad))
    out.info["pad"] = pad
    return out


def pill(label, size=21, color=RED, text_color=WH, h=PILL_H, padx=20):
    w = text_w(label, size, "bold") + 2 * padx
    s = Sprite(w + 2, h + 2)
    s.rect(0, 0, w, h, color, h / 2)
    s.text(padx, h / 2 + size * 0.36, size, label, text_color, "bold")
    return s.img


def headline_sprite(text, size=68, color=WH, max_w=1500):
    while text_w(text, size, "anton") > max_w and size > 40:
        size -= 2
    w, asc = text_w(text, size, "anton"), size * 1.05
    s = Sprite(w + 8, asc + size * 0.3, 0, asc)
    s.text(0, asc, size, text, color, "anton")
    # soft shadow so the headline reads over a bright satellite frame or flood map
    img = s.img
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.putalpha(img.getchannel("A").filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * 0.5)))
    out = Image.alpha_composite(sh, img)
    return out, asc


def sub_box(text, size=34, max_w=1400):
    while text_w(text, size, "semibold") > max_w - 60 and size > 22:
        size -= 1
    w, h = text_w(text, size, "semibold") + 52, size * 2.0
    s = Sprite(w + 2, h + 2)
    s.rect(0, 0, w, h, (17, 20, 25), 4, a=225)
    s.rect(0, 0, 7, h, RED)
    s.text(30, h / 2 + size * 0.36, size, text, WH, "semibold")
    return s.img


def source_sprite(text, size=19):
    s = Sprite(text_w(text, size, "regular") + 6, size * 1.6, 0, size * 1.2)
    s.text(0, size * 1.2, size, text, SOURCE, "regular")
    return s.img


class Chrome:
    """Pill + headline + sub-line + source + logo, with their entrance animation. Draw last, over the card content."""
    def __init__(self, pill_text, headline=None, sub=None, source=None, sub_at=1.6, dark_top=False):
        self.pill = pill(pill_text.upper()) if pill_text else None
        self.head = headline_sprite(headline.upper()) if headline else None
        self.sub = sub_box(sub) if sub else None
        self.src = source_sprite(source) if source else None
        self.logo = logo(LOGO_BOX[2])
        self.sub_at = sub_at
        self.top_shade = None
        if dark_top:                                     # legibility over photos / satellite video
            g = np.linspace(1, 0, 420, dtype=np.float32) ** 1.6
            a = (g * 170).astype(np.uint8)[:, None].repeat(W, 1)
            sh = Image.new("RGBA", (W, 420), (10, 13, 18, 0))
            sh.putalpha(Image.fromarray(a, "L"))
            self.top_shade = sh
            gb = (np.clip(np.linspace(0, 1.4, 360, dtype=np.float32), 0, 1) ** 1.6 * 150).astype(np.uint8)[:, None].repeat(W, 1)
            bs = Image.new("RGBA", (W, 360), (10, 13, 18, 0))
            bs.putalpha(Image.fromarray(gb, "L"))
            self.bot_shade = bs

    def boxes(self):
        """Screen areas the chrome covers (x, y, w, h): map labels keep out of them."""
        b = [(LOGO_BOX[0] - 12, LOGO_BOX[1] - 12, LOGO_BOX[2] + 24, 110)]
        if self.pill:
            b.append((MARGIN_X, PILL_Y, self.pill.width, self.pill.height))
        if self.head:
            img, asc = self.head
            b.append((MARGIN_X, HEAD_BASE - asc, img.width, asc + 16))
        if self.sub:
            b.append((MARGIN_X, SUB_Y, self.sub.width, self.sub.height))
        if self.src:
            b.append((MARGIN_X, SOURCE_BASE - 26, self.src.width, 34))
        return b

    def draw(self, fr, t):
        if self.top_shade is not None:
            paste(fr, self.top_shade, 0, 0)
            paste(fr, self.bot_shade, 0, H - 360)
        pad = self.logo.info.get("pad", 0)
        paste(fr, self.logo, LOGO_BOX[0] - pad, LOGO_BOX[1] - pad)
        if self.pill:
            a = ease_out((t - 0.15) / 0.35)
            paste(fr, self.pill, MARGIN_X - 40 * (1 - a), PILL_Y, a)
        if self.head:
            img, asc = self.head
            a = ease_out((t - 0.3) / 0.45)
            paste(fr, img, MARGIN_X, HEAD_BASE + 26 * (1 - a), a, ay=asc)
        if self.sub:
            a = ease_out((t - self.sub_at) / 0.4)
            paste(fr, self.sub, MARGIN_X - 30 * (1 - a), SUB_Y, a)
        if self.src:
            paste(fr, self.src, MARGIN_X, SOURCE_BASE, ease_out((t - 0.6) / 0.5) * 0.9, ay=19 * 1.2)


# ---- encoders -------------------------------------------------------------------------------------------------------
def encode_mp4(frames, path, fps=FPS):
    """Opaque card -> H.264 mp4 (CapCut fades it in/out with alpha keyframes)."""
    path = Path(path)
    tmp = path.with_name(path.stem + ".part.mp4")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
                          "-movflags", "+faststart", str(tmp)], stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    if p.wait():
        raise RuntimeError("ffmpeg failed for " + path.name)
    tmp.replace(path)


def encode_prores(frames, path, fps=FPS):
    """RGBA frames -> ProRes 4444 with alpha (the intro: its red wipe reveals the first narration clip)."""
    path = Path(path)
    tmp = path.with_name(path.stem + ".part.mov")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(fps),
                          "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-vendor", "apl0",
                          str(tmp)], stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    if p.wait():
        raise RuntimeError("ffmpeg failed for " + path.name)
    tmp.replace(path)


def load_config(project_dir):
    """project/cards.py -> (INTRO dict or None, CARDS list)."""
    import importlib.util
    p = Path(project_dir) / "cards.py"
    if not p.exists():
        return None, []
    spec = importlib.util.spec_from_file_location("iwn_cards_cfg", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return getattr(m, "INTRO", None), list(getattr(m, "CARDS", []))
