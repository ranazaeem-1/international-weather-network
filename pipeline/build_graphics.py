"""Build per-chapter IWN lower-thirds and the episode ticker as ProRes 4444 alpha clips (1920x1080, 30 fps).

Same layout, colours, font and motion as the brand-kit design (iwn-brand-kit/source/build_motion.py), but drawn directly
with Pillow and piped to ffmpeg: a few seconds per graphic instead of minutes. The Tesseract-based builder is kept as
build_graphics_tsrct.py in the pipeline folder in case an editable .tsrct project is ever needed.

Usage:  python build_graphics.py            # everything
        python build_graphics.py S04 ticker # only these
"""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from fontTools.pens.recordingPen import RecordingPen
from fontTools.svgLib.path import parse_path
from PIL import Image, ImageDraw, ImageFont

EP = Path(__file__).resolve().parents[1]
KIT = EP.parents[1] / "iwn-brand-kit"
OUT = EP / "graphics"
W, H, FPS = 1920, 1080, 30
D, WH, R = (0x17, 0x19, 0x1D), (0xF5, 0xF2, 0xEB), (0xEF, 0x34, 0x3D)
SS = 2                                                     # supersampling for smooth edges
LT_IN, LT_OUT_AT = 0.5, 7.4                                # seconds: length of the intro/outro clips, start of the outro
TK_Y0, TK_H = 880, 192                                     # rows of the frame the ticker strip covers
LOGO = ("M0 35H23V100H0Z M32 35H54L64 76L76 35H96L108 76L119 35H141L121 100H98L86 65L75 100H52Z "
        "M152 100V35H174V43C190 25 226 30 226 63V100H203V65C203 48 175 48 175 66V100Z")

# id: (category, headline, sub-line, location, date)
LOWER_THIRDS = {
    "S01": ("WEATHER UPDATE", "HEADLINE", "Sub-line", "PLACE", "01 JAN 2026"),
}

TICKER_COPY = (
    "TICKER COPY     •     "
)
TICKER_LABEL, TICKER_STATUS = "PLACE", "WEATHER UPDATE"

# Second ticker: calls to action, shown near the end of every chapter (user, 17 Oct). Set CTA_COPY per episode if needed.
CTA_COPY = (
    "SUBSCRIBE FOR LIVE WEATHER UPDATES     •     TURN ON NOTIFICATIONS SO YOU NEVER MISS A WARNING     •     "
    "LIKE THIS VIDEO IF YOU ARE STAYING SAFE     •     SHARE WITH FAMILY AND FRIENDS IN THE AREA     •     "
    "COMMENT YOUR LOCATION AND WHAT YOU ARE SEEING     •     "
)
CTA_LABEL, CTA_STATUS = "STAY UPDATED", "SUBSCRIBE"


def font(size):
    return ImageFont.truetype(str(KIT / "fonts/Manrope-Bold.ttf"), int(round(size * SS)))


class Layer:
    """A transparent 1920x1080 layer drawn at SS x and scaled down once."""
    def __init__(self):
        self.im = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def rect(self, x, y, w, h, c, r=0):
        self.d.rounded_rectangle([x * SS, y * SS, (x + w) * SS, (y + h) * SS], radius=min(r, w / 2, h / 2) * SS, fill=c + (255,))

    def text(self, x, y, size, s, c):                      # x, y = left end of the baseline, as in the motion design
        self.d.text((x * SS, y * SS), s, font=font(size), fill=c + (255,), anchor="ls")

    def badge(self, x, y, d):
        s = d * .7 / 226
        mx, my = x + d * .15, y + d * .32
        self.rect(x, y, d, d, D, d / 2)
        pen = RecordingPen()
        parse_path(LOGO, pen)
        pts, cur = [], (0, 0)
        for op, a in pen.value:
            if op == "moveTo":
                pts, cur = [a[0]], a[0]
            elif op == "lineTo":
                pts.append(a[0]); cur = a[0]
            elif op == "curveTo":
                p0, (p1, p2, p3) = cur, a
                for k in range(1, 13):
                    t = k / 12
                    pts.append(tuple((1 - t) ** 3 * p0[i] + 3 * (1 - t) ** 2 * t * p1[i] + 3 * (1 - t) * t * t * p2[i] + t ** 3 * p3[i] for i in (0, 1)))
                cur = p3
            elif op in ("closePath", "endPath") and len(pts) > 2:
                self.d.polygon([((mx + px * s) * SS, (my + py * s) * SS) for px, py in pts], fill=WH + (255,))
                pts = []
        self.rect(mx - .5 * s, my, 24 * s, 24 * s, R, 12 * s)

    def done(self):
        return np.asarray(self.im.resize((W, H), Image.LANCZOS), dtype=np.float32) / 255.0   # straight alpha, 0..1


def box(a):
    """Bounding rows/cols of a layer's visible pixels: (y0, y1, x0, x1)."""
    ys, xs = np.where(a[..., 3] > 0)
    return int(ys.min()), int(ys.max()) + 1, int(xs.min()), int(xs.max()) + 1


def u8(a):
    return (np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)


def place(frame, patch, y, x, opacity=1.0):
    """Put a float RGBA patch into a uint8 RGBA frame at (y, x) (whole pixels), clipped to the frame. The target area is empty."""
    y, x = int(round(y)), int(round(x))
    h, w = patch.shape[:2]
    y0, x0, y1, x1 = max(0, y), max(0, x), min(H, y + h), min(W, x + w)
    if y1 <= y0 or x1 <= x0:
        return
    p = patch[y0 - y:y1 - y, x0 - x:x1 - x]
    if opacity < 1:
        p = p.copy()
        p[..., 3] *= opacity
    frame[y0:y1, x0:x1] = u8(p)


def encode(frames, path, size=(W, H)):
    """frames: iterable of uint8 RGBA arrays or ready bytes (straight alpha) -> ProRes 4444 with alpha."""
    tmp = path.with_suffix(".part.mov")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{size[0]}x{size[1]}", "-r", str(FPS), "-i", "-",
                          "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-vendor", "apl0", str(tmp)],
                         stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f if isinstance(f, bytes) else f.tobytes())
    p.stdin.close()
    if p.wait():
        raise RuntimeError("ffmpeg failed for " + path.name)
    tmp.replace(path)


def lower_third(seg, cat, head, sub, loc, date):
    f27, f24 = font(27), font(24)
    bar = Layer()
    pill_w = max(275, int(f27.getlength(cat) / SS * 23 / 27) + 48)
    bar.rect(164, 848, 1658, 150, D, 36)
    bar.rect(291, 811, pill_w, 49, R, 24)
    bar.text(315, 845, 23, cat, WH)
    bar.text(291, 910, 35, head, WH)
    bar.text(291, 961, 28, sub, WH)
    bar.badge(82, 832, 184)
    bar = bar.done()

    cap = Layer()
    loc_w = f27.getlength(loc) / SS
    sep_x = 171 + loc_w + 22
    date_x = sep_x + 26
    cap_w = date_x + f24.getlength(date) / SS + 30 - 96
    cap.rect(96, 74, cap_w, 76, D, 38)
    cap.rect(119, 95, 34, 34, R, 17)
    cap.text(171, 122, 27, loc, WH)
    cap.rect(sep_x, 92, 2, 38, WH)
    cap.text(date_x, 122, 24, date, WH)
    cap = cap.done()

    # The bar (bottom) and the capsule (top) never overlap, so each frame is just the two patches placed on an empty frame.
    by0, by1, bx0, bx1 = box(bar)
    cy0, cy1, cx0, cx1 = box(cap)
    bar_p, cap_p = bar[by0:by1, bx0:bx1], cap[cy0:cy1, cx0:cx1]
    # Encoding ProRes is the slow part, and for 6.9 of the 8 seconds nothing moves. So the lower-third is delivered as
    # three pieces the draft builder lays end to end: intro clip (0-0.5 s), a still (0.5-7.4 s), outro clip (7.4-7.9 s).
    hold = np.zeros((H, W, 4), np.uint8)
    place(hold, bar_p, by0, bx0)
    place(hold, cap_p, cy0, cx0)
    Image.fromarray(hold, "RGBA").save(OUT / f"lt_{seg}.png")

    def frames(t0, n_frames):
        for n in range(n_frames):
            t = t0 + n / FPS
            a = 1 - (1 - min(1, t / .45)) ** 3
            b = max(0.0, min(1.0, (t - LT_OUT_AT) / .45))
            dy = 260 * (1 - a + b * b)
            op = min(1, t / .2) * max(0.0, 1 - (t - LT_OUT_AT) / .45)
            dx = -900 * (1 - min(1, t / .4)) ** 3
            fr = np.zeros((H, W, 4), np.uint8)
            place(fr, bar_p, by0 + dy, bx0, op)
            place(fr, cap_p, cy0, cx0 + dx)
            yield fr

    encode(frames(0.0, int(LT_IN * FPS)), OUT / f"lt_{seg}_in.mov")
    encode(frames(LT_OUT_AT, int(LT_IN * FPS)), OUT / f"lt_{seg}_out.mov")


def ticker(seconds=24, copy=None, label_txt=None, status=None, out_name="ticker_strip.mov"):
    copy, label_txt, status = copy or TICKER_COPY, label_txt or TICKER_LABEL, status or TICKER_STATUS
    band = Layer()
    band.rect(0, 930, 1920, 106, D)
    band.rect(0, 930, 1920, 4, R)
    band = band.done()
    label = Layer()
    label.rect(0, 934, 490, 102, D)
    label.text(224, 981, 27, label_txt, WH)
    label.text(225, 1010, 18, status, R)
    label.badge(56, 896, 142)
    label = label.done()

    # one long strip of scrolling copy, drawn once
    f31 = font(31)
    items = [s.strip() for s in copy.split("•") if s.strip()]
    need = 1430 + seconds * 90 + 200
    pieces, x, k = [], 0.0, 0
    while x < need:
        for piece in (items[k % len(items)], "•"):
            pieces.append((x, piece))
            x += f31.getlength(piece) / SS + 46
        k += 1
    strip_w, strip_h = int(x) + 10, 70
    im = Image.new("RGBA", (strip_w * SS, strip_h * SS), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    for px, piece in pieces:
        dr.text((px * SS, 50 * SS), piece, font=f31, fill=WH + (255,), anchor="ls")
    strip = np.asarray(im.resize((strip_w, strip_h), Image.LANCZOS), dtype=np.float32) / 255.0
    y0 = 995 - 50                                          # strip row 50 is the text baseline (y = 995 in the frame)

    # Fixed part (band + label + badge) built once; per frame only the 70-pixel-high copy area right of the label changes.
    base = np.zeros((H, W, 4), np.float32)
    for lay in (band, label):                              # label over band; the band is opaque where they overlap
        a = lay[..., 3:4]
        base[..., :3] = lay[..., :3] * a + base[..., :3] * (1 - a)
        base[..., 3:4] = a + base[..., 3:4] * (1 - a)
    base8 = u8(base)
    dark = np.array(D, np.float32) / 255.0
    X0 = 490                                               # right edge of the fixed label

    def frames():
        for n in range(seconds * FPS):
            t = n / FPS
            off = int(round(t * 90))                       # copy starts at x = 510 and scrolls left at 90 px/s
            fr = base8.copy()
            x_from = max(X0, 510 - off)
            s_from = x_from - (510 - off)
            w = min(W - x_from, strip_w - s_from)
            if w > 0:
                s = strip[:, s_from:s_from + w]
                fr[y0:y0 + strip_h, x_from:x_from + w, :3] = u8(s[..., :3] * s[..., 3:4] + dark * (1 - s[..., 3:4]))
            if t < .4:                                     # soft entrance; the edit cuts it off at the end
                fr[..., 3] = (fr[..., 3] * (t / .4)).astype(np.uint8)
            yield np.ascontiguousarray(fr[TK_Y0:TK_Y0 + TK_H])

    encode(frames(), OUT / out_name, size=(W, TK_H))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    only = sys.argv[1:]
    jobs = [(lower_third, (seg, *args)) for seg, args in LOWER_THIRDS.items() if not only or seg in only]
    if not only or "ticker" in only:
        jobs.append((ticker, ()))
    if not only or "cta" in only:
        jobs.append((ticker, (24, CTA_COPY, CTA_LABEL, CTA_STATUS, "cta_ticker_strip.mov")))
    with ThreadPoolExecutor(4) as ex:
        for fn, args in jobs:
            ex.submit(fn, *args).add_done_callback(
                lambda fut, name=(("cta" if len(args) == 5 else args[0]) if args else "ticker"): print("built" if not fut.exception() else f"FAILED {fut.exception()}", name, flush=True))
