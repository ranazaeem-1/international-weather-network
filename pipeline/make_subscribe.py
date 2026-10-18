"""Channel-specific subscribe animations, made from the approved IWN subscribe animation.

    python make_subscribe.py            -> iwn-brand-kit/motion/subscribe-en-transparent.mov  (Independent Weather Network)
                                           iwn-brand-kit/motion/subscribe-es-transparent.mov  (Instant Weather Network)

Takes the settled frames of motion/subscribe-transparent.mov (SUBSCRIBE and SUBSCRIBED states), swaps only the
channel name, and replays the original motion (slide up 0-0.5 s, button flips at 3.1 s, slide out from 5.3 s,
red dot pulse) exactly as iwn-brand-kit/source/build_motion.py defines it. Everything else stays identical.
"""
import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

KIT = Path(__file__).resolve().parents[1] / "iwn-brand-kit"
SRC = KIT / "motion/subscribe-transparent.mov"
NAMES = {"en": "Independent Weather Network", "es": "Instant Weather Network"}
OLD_NAME = "International Weather Network"
W, H, FPS, SECONDS = 1920, 1080, 30, 6
PILL = (0xF5, 0xF2, 0xEB, 255)
DARK = (0x17, 0x19, 0x1D, 255)
NAME_BOX = (282, 860, 798, 912)        # channel-name area inside the pill (left of the red button at x=804)
DOT_BOX = (90, 817, 268, 995)          # the circular badge; its red dot pulses


def frame_at(t):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(SRC), "-frames:v", "1",
                                   "-f", "rawvideo", "-pix_fmt", "rgba", "-"])
    return Image.frombytes("RGBA", (W, H), raw)


def text_bbox(im):
    """Bounding box of the dark channel-name pixels inside NAME_BOX."""
    a = np.asarray(im.crop(NAME_BOX)).astype(int)
    dark = (a[..., 3] > 200) & (a[..., :3].sum(axis=2) < 300)
    ys, xs = np.nonzero(dark)
    return NAME_BOX[0] + xs.min(), NAME_BOX[1] + ys.min(), NAME_BOX[0] + xs.max(), NAME_BOX[1] + ys.max()


def fit_font(ref_box):
    """Manrope Bold size whose rendering of the old name matches the original's width."""
    target = ref_box[2] - ref_box[0]
    best = None
    for size in range(20, 40):
        f = ImageFont.truetype(str(KIT / "fonts/Manrope-Bold.ttf"), size)
        w = f.getbbox(OLD_NAME)[2] - f.getbbox(OLD_NAME)[0]
        if best is None or abs(w - target) < best[0]:
            best = (abs(w - target), f)
    return best[1]


def retitle(im, name, font, ref_box):
    im = im.copy()
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = ref_box
    d.rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 3], fill=PILL)
    # align the new name's ink top-left with the old name's (same cap height, same baseline)
    bb = font.getbbox(OLD_NAME)
    d.text((x0 - bb[0], y0 - bb[1]), name, font=font, fill=DARK)
    return im


def red_mask(im):
    a = np.asarray(im.crop(DOT_BOX)).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (r > 150) & (g < 90) & (b < 90)


def render(lang, sub, subd, font, ref_box):
    a_sub = retitle(sub, NAMES[lang], font, ref_box)
    a_subd = retitle(subd, NAMES[lang], font, ref_box)
    dot = red_mask(sub)
    out = KIT / f"motion/subscribe-{lang}-transparent.mov"
    tmp = out.with_suffix(".part.mov")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-vendor", "apl0", str(tmp)],
                         stdin=subprocess.PIPE)
    for n in range(FPS * SECONDS):
        t = n / FPS
        base = a_sub if t < 3.1 else a_subd
        e = 1 - (1 - min(1, t / .5)) ** 3
        o = max(0.0, min(1.0, (t - 5.3) / .5))
        dy = 250 * (1 - e) + 250 * o * o
        alpha = min(1, t / .18) * max(0.0, 1 - (t - 5.3) / .5)
        pulse = 1.0 if t < .65 else (80 + 20 * math.cos((t - .65) * math.pi * 2)) / 100
        g = np.asarray(base).copy()
        if pulse < 1:
            sub_a = g[DOT_BOX[1]:DOT_BOX[3], DOT_BOX[0]:DOT_BOX[2], 3]
            sub_a[dot] = (sub_a[dot] * pulse).astype(np.uint8)
        g[..., 3] = (g[..., 3] * min(1.0, alpha)).astype(np.uint8)
        fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        fr.alpha_composite(Image.fromarray(g), (0, int(round(dy))))
        p.stdin.write(fr.tobytes())
    p.stdin.close()
    if p.wait():
        raise RuntimeError("ffmpeg failed for " + out.name)
    tmp.replace(out)
    a_sub.save(KIT / f"previews/subscribe-{lang}.png")
    print("ok", out.name)


if __name__ == "__main__":
    sub, subd = frame_at(2.65), frame_at(3.65)   # dot pulse at 100% on these frames
    ref = text_bbox(sub)
    font = fit_font(ref)
    for lang in NAMES:
        render(lang, sub, subd, font, ref)
