"""Render the reusable Carver brand motion kit once (re-run after design changes).

  python make_brand_motion.py            -> brand-kit/motion/*  (+ brand-kit/graphics/*.png)
  python make_brand_motion.py --preview  -> brand-kit/styleframes/motion/*.png stills for review (fast)

Outputs:
  graphics/bug.png, graphics/box_chrome.png  full-frame transparent PNGs (static)
  motion/wipe_full.mov   0.8 s full-frame alpha wipe; fully covered 0.34-0.46 s (switch layouts at 0.40 s)
  motion/wipe_box.mov    0.6 s alpha wipe for the desk window, 720x405 placed at 1160,40; covered ~0.25-0.35 s (switch at 0.30 s)
  motion/sting.mov       4.2 s full-frame alpha intro sting; covered 0.55-3.45 s
  motion/end_bg.mp4      30 s opaque animated end-screen background
  motion/end_fg.mov      30 s alpha end-screen foreground (host frame at 80,250 896x504 + 2 video slots + subscribe slot)
  sfx/*.wav              whoosh, whoosh_small, sting (procedural, 48 kHz stereo)
"""
import sys
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

sys.path.insert(0, str(Path(__file__).parent))
from motion import render_jobs

CWD = Path(__file__).resolve().parents[1]
BK = CWD / "brand-kit"; HTML = "brand-kit/src/overlays.html"
WIPE_FULL = {"dur": 0.8, "switch": 0.40}
WIPE_BOX = {"dur": 0.6, "switch": 0.30, "rect": [1160, 40, 720, 405]}
STING = {"dur": 4.2, "covered": [0.55, 3.45]}


def jobs(preview=False):
    J = []
    J.append({"html": HTML, "data": {"kind": "bug"}, "out": "brand-kit/graphics/bug.png", "dur": 0, "alpha": True})
    J.append({"html": HTML, "data": {"kind": "chrome"}, "out": "brand-kit/graphics/box_chrome.png", "dur": 0, "alpha": True})
    J.append({"html": HTML, "data": {"kind": "end_plate"}, "out": "brand-kit/graphics/end_plate.png", "dur": 0, "alpha": False, "clip": [80, 250, 896, 504]})
    if preview:
        P = "brand-kit/styleframes/motion/"
        J += [{"html": HTML, "data": {"kind": "wipe_full", "dur": .8}, "out": P + f"wipe_full_{t}.png", "dur": 0, "t": t, "alpha": True} for t in (0.2, 0.4)]
        J += [{"html": HTML, "data": {"kind": "sting", "dur": 4.2}, "out": P + f"sting_{t}.png", "dur": 0, "t": t, "alpha": True} for t in (0.9, 1.4, 2.6, 3.7)]
        J.append({"html": HTML, "data": {"kind": "end_bg", "dur": 30}, "out": P + "end_bg.png", "dur": 0, "t": 5, "alpha": False})
        J.append({"html": HTML, "data": {"kind": "end_fg", "dur": 30}, "out": P + "end_fg.png", "dur": 0, "t": 5, "alpha": True})
        return J
    J.append({"html": HTML, "data": {"kind": "wipe_full", "dur": WIPE_FULL["dur"]}, "out": "brand-kit/motion/wipe_full.mov", "dur": WIPE_FULL["dur"], "alpha": True})
    J.append({"html": HTML, "data": {"kind": "wipe_box", "dur": WIPE_BOX["dur"], "w": WIPE_BOX["rect"][2], "h": WIPE_BOX["rect"][3]}, "out": "brand-kit/motion/wipe_box.mov", "dur": WIPE_BOX["dur"],
              "clip": WIPE_BOX["rect"], "alpha": True})
    J.append({"html": HTML, "data": {"kind": "sting", "dur": STING["dur"]}, "out": "brand-kit/motion/sting.mov", "dur": STING["dur"], "alpha": True})
    J.append({"html": HTML, "data": {"kind": "end_bg", "dur": 30}, "out": "brand-kit/motion/end_bg.mp4", "dur": 30, "alpha": False})
    J.append({"html": HTML, "data": {"kind": "end_fg", "dur": 30}, "out": "brand-kit/motion/end_fg.mov", "dur": 30, "alpha": True, "static": [1.6, 30]})
    return J


# ---------------- procedural sound design ----------------
SR = 48000


def _noise(n, seed):
    return np.random.default_rng(seed).standard_normal(n)


def _sweep_noise(dur, f0, f1, seed=1, q=1.6):
    """band-limited noise whose centre frequency glides f0 -> f1 (processed in short blocks)."""
    n = int(dur * SR); x = _noise(n, seed); y = np.zeros(n); blk = 1024
    for s in range(0, n, blk):
        fc = f0 * (f1 / f0) ** (s / n)
        lo, hi = max(40, fc / q), min(SR / 2 - 100, fc * q)
        sos = butter(2, [lo, hi], btype="band", fs=SR, output="sos")
        seg = x[max(0, s - 2048): s + blk]
        y[s: s + blk] = sosfilt(sos, seg)[-len(x[s: s + blk]):]
    return y


def _env(n, attack, release, peak_at=None):
    t = np.linspace(0, 1, n); p = peak_at if peak_at is not None else attack / (attack + release)
    e = np.where(t < p, (t / p) ** 2, ((1 - t) / (1 - p)) ** 1.6)
    return e


def whoosh(dur=0.8, gain=0.32, seed=3, f0=250, f1=2600, pan=True):
    y = _sweep_noise(dur, f0, f1, seed) * _env(int(dur * SR), .45, .55, .48)
    y /= np.abs(y).max() + 1e-9
    n = len(y); p = np.linspace(-0.7, 0.7, n) if pan else np.zeros(n)          # right -> left like the wipe
    L, R = y * np.sqrt((1 + p) / 2), y * np.sqrt((1 - p) / 2)
    return np.stack([L, R], 1) * gain


def hit(dur=2.2, gain=0.5):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 62 * np.exp(-t * 1.8) + 38                                              # sub thump gliding down
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2)
    trans = sosfilt(butter(2, [900, 6000], btype="band", fs=SR, output="sos"), _noise(n, 9)) * np.exp(-t * 28)
    shimmer = sosfilt(butter(2, [3500, 9000], btype="band", fs=SR, output="sos"), _noise(n, 11)) * np.exp(-t * 2.2) * 0.25
    y = sub * 0.9 + trans * 0.5 + shimmer
    # small stereo room: two decaying delays
    L = y.copy(); R = y.copy()
    for d, g in ((0.031, .35), (0.047, .28), (0.083, .18)):
        k = int(d * SR); L[k:] += g * y[:-k]; R[int(k * 1.13):] += g * y[:-int(k * 1.13)]
    s = np.stack([L, R], 1); s /= np.abs(s).max() + 1e-9
    return s * gain


def sfx():
    out = BK / "sfx"; out.mkdir(parents=True, exist_ok=True)
    w = lambda name, a: wavfile.write(out / name, SR, (np.clip(a, -1, 1) * 32767).astype(np.int16))
    w("whoosh.wav", whoosh(0.8, 0.30))
    w("whoosh_small.wav", whoosh(0.6, 0.16, seed=5, f0=500, f1=3800))
    n = int(STING["dur"] * SR); s = np.zeros((n, 2))
    def put(a, at):
        k = int(at * SR); s[k:k + len(a)] += a[: n - k]
    put(whoosh(0.7, 0.30, seed=7), 0.0); put(hit(2.6, 0.42), 1.05); put(whoosh(0.8, 0.22, seed=8, f0=400, f1=3000), 3.35)
    w("sting.wav", s)


if __name__ == "__main__":
    prev = "--preview" in sys.argv
    for o in render_jobs(jobs(prev), workers=4):
        print(o)
    if not prev:
        from PIL import Image                                      # plain ink fill behind full-host moments
        Image.new("RGB", (1920, 1080), (5, 12, 26)).save(BK / "graphics/navy.png")
        sfx(); print("sfx ok")
