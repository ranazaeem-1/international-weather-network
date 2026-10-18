"""Bigger subscribe CTA with like + bell buttons (user, 17 Oct 2026), built on the approved IWN subscribe pill.

    python make_cta.py      -> iwn-brand-kit/motion/subscribe-cta-en-transparent.mov  (Independent Weather Network)
                               iwn-brand-kit/motion/subscribe-cta-es-transparent.mov  (Instant Weather Network)
                               iwn-brand-kit/previews/subscribe-cta-<lang>.png / -filmstrip.png

Same look as motion/subscribe-transparent.mov (warm-white pill, charcoal iwn badge, red button, Manrope), scaled by SCALE
and extended with a like and a bell button. A cursor clicks like -> subscribe -> bell; the bell rings. 7 s, 1920x1080,
ProRes 4444 with alpha. render.py / build_capcut.py use it automatically when it exists (SUB_LEN = 7).
"""
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

KIT = Path(__file__).resolve().parents[1] / "iwn-brand-kit"
OLD = KIT / "motion/subscribe-transparent.mov"
W, H, FPS, SECONDS = 1920, 1080, 30, 7.0
SCALE = 1.3
SS = 2                                    # supersampling for clean edges
PILL, DARK, RED, IDLE = (0xF5, 0xF2, 0xEB, 255), (0x17, 0x19, 0x1D, 255), (0xEF, 0x34, 0x3D, 255), (0xE2, 0xDD, 0xD3, 255)
WHITE = (255, 255, 255, 255)
TEXT = {"en": ("Independent Weather Network", "People. Places. Weather.", "SUBSCRIBE", "SUBSCRIBED"),
        "es": ("Instant Weather Network", "Personas. Lugares. Clima.", "SUSCRÍBETE", "SUSCRITO")}
ICON = ImageFont.truetype("C:/Windows/Fonts/segmdl2.ttf", 10)   # Segoe MDL2: like E8E1, bell EA8F
LIKE, BELL = "\uE8E1", "\uEA8F"

# Layout in the original 1x coordinates (iwn-brand-kit/source/build_motion.py), then extended to the right
BADGE = (90, 817, 268, 995)               # charcoal circle with the iwn logo, copied from the approved animation
PILL_BOX = (172, 832, 1282, 980)
BTN = (804, 870, 1054, 942)
LIKE_C, BELL_C, ICON_R = (1118, 906), (1210, 906), 37
NAME_XY, TAG_XY = (290, 878), (290, 924)
X0, Y_BOTTOM = 40, 1048                   # where the scaled block sits on the 1920x1080 frame


def font(bold, size):
    return ImageFont.truetype(str(KIT / ("fonts/Manrope-Bold.ttf" if bold else "fonts/Manrope.ttf")), size)


def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def badge_image():
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", "2.65", "-i", str(OLD), "-frames:v", "1",
                                   "-f", "rawvideo", "-pix_fmt", "rgba", "-"])
    return Image.frombytes("RGBA", (1920, 1080), raw).crop(BADGE)


# Local canvas = bounding box of the block in 1x coords, padded for the pop/ring overshoot and the cursor
LX0, LY0, LX1, LY1 = 80, 800, 1330, 1060


def S(v):            # 1x coord -> supersampled local pixel
    return v * SCALE * SS


def P(x, y):
    return S(x - LX0), S(y - LY0)


def icon(glyph, r, fg, bg, scale=1.0, angle=0.0):
    size = int(S(r * 2 * scale)) + 4
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([2, 2, size - 3, size - 3], fill=bg)
    f = ICON.font_variant(size=int(size * 0.46))
    g = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(g).text((size / 2, size / 2), glyph, font=f, fill=fg, anchor="mm")
    if angle:
        g = g.rotate(angle, resample=Image.BICUBIC, center=(size / 2, size * 0.3))
    im.alpha_composite(g)
    return im


def cursor(pressed):
    s = int(S(46))
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    k = s / 24 * (0.88 if pressed else 1.0)
    pts = [(1, 1), (1, 19), (6, 14.5), (9.5, 22), (12.5, 20.7), (9.2, 13.4), (15.5, 13.4)]
    d = ImageDraw.Draw(im)
    d.polygon([(x * k, y * k) for x, y in pts], fill=WHITE, outline=DARK, width=max(2, int(1.6 * k)))
    return im


def frame(t, lang, badge, fonts):
    name, tag, sub_txt, subd_txt = TEXT[lang]
    f_name, f_tag, f_btn = fonts
    loc = Image.new("RGBA", (int(S(LX1 - LX0)), int(S(LY1 - LY0))), (0, 0, 0, 0))
    d = ImageDraw.Draw(loc)
    x0, y0 = P(PILL_BOX[0], PILL_BOX[1]); x1, y1 = P(PILL_BOX[2], PILL_BOX[3])
    d.rounded_rectangle([x0, y0, x1, y1], radius=S(74), fill=PILL)
    d.text(P(*NAME_XY), name, font=f_name, fill=DARK)
    d.text(P(*TAG_XY), tag, font=f_tag, fill=DARK)

    # timeline: like click 1.3 s, subscribe click 2.25 s, bell click 3.2 s
    t_like, t_sub, t_bell = 1.3, 2.25, 3.2
    subd = t >= t_sub
    bx0, by0 = P(BTN[0], BTN[1]); bx1, by1 = P(BTN[2], BTN[3])
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=S(36), fill=DARK if subd else RED)
    d.text(((bx0 + bx1) / 2, (by0 + by1) / 2), subd_txt if subd else sub_txt, font=f_btn, fill=WHITE, anchor="mm")

    def pop(tc):
        if t < tc:
            return 1.0
        u = (t - tc) / 0.35
        return 1.0 + 0.22 * math.sin(math.pi * min(1, u)) if u < 1 else 1.0

    for c, glyph, tc in ((LIKE_C, LIKE, t_like), (BELL_C, BELL, t_bell)):
        on = t >= tc
        ang = 0.0
        if glyph == BELL and on:
            u = t - tc
            ang = 22 * math.sin(u * 2 * math.pi * 3.2) * math.exp(-u * 2.2) if u < 1.6 else 0.0
        im = icon(glyph, ICON_R, WHITE if on else DARK, RED if on else IDLE, pop(tc), ang)
        cx, cy = P(*c)
        loc.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
        if on and t - tc < 0.45:                                          # click ripple
            u = (t - tc) / 0.45
            r = S(ICON_R * (1.1 + 0.7 * u))
            a = int(170 * (1 - u))
            ImageDraw.Draw(loc).ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0xEF, 0x34, 0x3D, a), width=int(S(4)))

    b = badge.resize((int(S(BADGE[2] - BADGE[0])), int(S(BADGE[3] - BADGE[1]))), Image.LANCZOS)
    loc.alpha_composite(b, tuple(int(v) for v in P(BADGE[0], BADGE[1])))

    # cursor path: enters from the right, visits like -> subscribe -> bell, fades out
    btn_c = ((BTN[0] + BTN[2]) / 2 + 40, (BTN[1] + BTN[3]) / 2)
    keys = [(0.6, (1320, 1000)), (1.15, LIKE_C), (1.5, LIKE_C), (2.1, btn_c), (2.45, btn_c), (3.05, BELL_C), (4.2, BELL_C)]
    if 0.6 <= t <= 4.6:
        for (ta, pa), (tb, pb) in zip(keys, keys[1:]):
            if ta <= t <= tb:
                u = ease_io((t - ta) / (tb - ta)); cx, cy = pa[0] + (pb[0] - pa[0]) * u, pa[1] + (pb[1] - pa[1]) * u
                break
        else:
            cx, cy = keys[-1][1]
        pressed = any(0 <= t - tc < 0.12 for tc in (t_like, t_sub, t_bell))
        cur = cursor(pressed)
        fade = min(1.0, (t - 0.6) / 0.2) * (1.0 - max(0.0, (t - 4.2) / 0.4))
        if fade < 1:
            a = cur.getchannel("A").point(lambda v: int(v * max(0.0, fade)))
            cur.putalpha(a)
        px, py = P(cx + 6, cy + 10)
        loc.alpha_composite(cur, (int(px), int(py)))

    loc = loc.resize((int(loc.width / SS), int(loc.height / SS)), Image.LANCZOS)
    # slide up in / down out + fade, as the original
    e = ease_out(t / 0.5)
    o = max(0.0, min(1.0, (t - 6.3) / 0.5))
    dy = 300 * (1 - e) + 300 * o * o
    alpha = min(1.0, t / 0.18) * max(0.0, 1 - (t - 6.3) / 0.5)
    if alpha < 1:
        loc.putalpha(loc.getchannel("A").point(lambda v: int(v * alpha)))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    left = X0
    top = Y_BOTTOM - loc.height + int(S(LY1 - PILL_BOX[3]) / SS) + int(round(dy))
    out.paste(loc, (left, top), loc)
    return out


def render(lang):
    badge = badge_image()
    fonts = (font(True, int(S(28))), font(True, int(S(21))), font(True, int(S(22))))
    out = KIT / f"motion/subscribe-cta-{lang}-transparent.mov"
    tmp = out.with_suffix(".part.mov")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-vendor", "apl0", str(tmp)],
                         stdin=subprocess.PIPE)
    strip = []
    for n in range(int(FPS * SECONDS)):
        t = n / FPS
        fr = frame(t, lang, badge, fonts)
        p.stdin.write(fr.tobytes())
        if n in (int(1.0 * FPS), int(1.45 * FPS), int(2.4 * FPS), int(3.35 * FPS), int(5.0 * FPS)):
            strip.append(fr)
    p.stdin.close()
    if p.wait():
        raise RuntimeError("ffmpeg failed for " + out.name)
    tmp.replace(out)
    bg = Image.new("RGBA", (W, H), (0x34, 0x38, 0x3D, 255))
    prev = bg.copy(); prev.alpha_composite(strip[-1]); prev.convert("RGB").save(KIT / f"previews/subscribe-cta-{lang}.png")
    tiles = []
    for fr in strip:
        b = bg.copy(); b.alpha_composite(fr); tiles.append(b.crop((0, 700, 1920, 1080)).resize((960, 190)))
    fs = Image.new("RGB", (960, 190 * len(tiles)))
    for i, tl in enumerate(tiles):
        fs.paste(tl.convert("RGB"), (0, 190 * i))
    fs.save(KIT / f"previews/subscribe-cta-{lang}-filmstrip.png")
    print("ok", out.name)


if __name__ == "__main__":
    import sys
    for lang in (sys.argv[1:] or TEXT):
        render(lang)
