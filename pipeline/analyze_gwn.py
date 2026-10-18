"""Find clean footage stretches inside the user's own GWN compilation videos (clips/raw/*.mp4).

A stretch is kept when no GWN lower-third / subscribe pop-up is on screen. Each stretch gets:
  - crop box (fractions) for the sharp clip area between GWN's blurred, watermarked side bars
  - narration overlap (seconds of GWN voice-over, from the auto captions) so natural-sound
    breaks only use stretches with no GWN voice.
Writes clips/gwn_segments.json and a contact sheet per video in clips/_scan/.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

EP = Path(__file__).resolve().parents[1]
RAW = EP / "clips/raw"
SCAN = EP / "clips/_scan"
FPS = 4
W, H = 480, 270


def frames(path):
    cmd = ["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)


def narration(vid):
    d = json.loads((RAW / f"{vid}.en.json3").read_text(encoding="utf8"))
    ev = []
    for e in d["events"]:
        t = "".join(s.get("utf8", "") for s in e.get("segs", [])).strip()
        if t:
            ev.append([e["tStartMs"] / 1000, (e["tStartMs"] + e.get("dDurationMs", 0)) / 1000, t])
    # merge overlapping/adjacent caption events into runs; long runs = GWN narrator
    runs = []
    for a, b, t in ev:
        if runs and a <= runs[-1][1] + 0.6:
            runs[-1][1] = max(runs[-1][1], b)
            runs[-1][2] += 1
            runs[-1][3] += " " + t
        else:
            runs.append([a, b, 1, t])
    narr = [(a, b) for a, b, n, t in runs if n >= 4 and b - a > 9]
    speech = [(a, b, t) for a, b, n, t in runs if not (n >= 4 and b - a > 9)]
    return narr, speech


def overlap(a, b, ivs):
    return sum(max(0, min(b, y) - max(a, x)) for x, y, *_ in ivs)


def is_blue(f):
    r, g, b = f[..., 0].astype(int), f[..., 1].astype(int), f[..., 2].astype(int)
    return (b > 150) & (b - r > 70) & (b - g > 40)


def analyse(vid):
    narr, speech = narration(vid)
    rows = []
    prev = None
    for i, f in enumerate(frames(RAW / f"{vid}.mp4")):
        blue = is_blue(f)
        lt = blue[int(H * .76):int(H * .93), int(W * .0):int(W * .70)].mean() > 0.04   # lower-third bar
        sub = blue[int(H * .80):int(H * .97), int(W * .70):].mean() > 0.02           # subscribe pop-up
        g = f.mean(axis=2)
        cut = prev is not None and np.abs(g - prev).mean() > 28
        prev = g
        col = np.abs(np.diff(g, axis=1)).mean(axis=0)  # vertical-edge strength per column
        rows.append((i / FPS, lt or sub, cut, col))
    # shots
    shots, start = [], 0
    for k, r in enumerate(rows):
        if r[2] and k - start > 2:
            shots.append((start, k))
            start = k
    shots.append((start, len(rows)))
    segs = []
    for s, e in shots:
        prof = np.median(np.stack([rows[k][3] for k in range(s, e)]), axis=0)
        base = np.median(prof) + 1e-6
        lpos = int(np.argmax(prof[5:W // 2 - 20])) + 5
        rpos = int(np.argmax(prof[W // 2 + 20:W - 5])) + W // 2 + 20
        x0 = lpos / W if prof[lpos] > 6 * base else 0.0
        x1 = (rpos + 1) / W if prof[rpos] > 6 * base else 1.0
        if x0 and x1 == 1.0:  # one-sided edge: assume centred content
            x1 = 1 - x0
        if x1 < 1.0 and not x0:
            x0 = 1 - x1
        # pad inward a little so no blurred/watermarked edge shows
        if x0 > 0:
            x0, x1 = x0 + 0.006, x1 - 0.006
        k = s
        while k < e:
            if rows[k][1]:
                k += 1
                continue
            j = k
            while j < e and not rows[j][1]:
                j += 1
            a, b = k / FPS + 0.25, j / FPS - 0.25
            if b - a >= 2.5:
                segs.append({
                    "vid": vid, "in": round(a, 2), "out": round(b, 2), "dur": round(b - a, 2),
                    "crop": [round(x0, 4), 0.0, round(x1 - x0, 4), 1.0],
                    "narr_s": round(overlap(a, b, narr), 1),
                    "speech": [t for x, y, t in speech if min(b, y) - max(a, x) > 0],
                })
            k = j
    return segs, narr


def sheet(vid, segs):
    out = SCAN / vid
    out.mkdir(parents=True, exist_ok=True)
    tiles = []
    for n, s in enumerate(segs):
        x0, _, w, _ = s["crop"]
        t = (s["in"] + s["out"]) / 2
        p = out / f"seg_{n:03d}.jpg"
        vf = f"crop=iw*{w}:ih:iw*{x0}:0,scale=-2:240"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(RAW / f"{vid}.mp4"), "-frames:v", "1", "-vf", vf, str(p)], check=True)
        tiles.append(p)
    return tiles


if __name__ == "__main__":
    vids = sys.argv[1:] or [p.stem for p in RAW.glob("*.mp4")]
    allsegs = {}
    for v in vids:
        segs, narr = analyse(v)
        allsegs[v] = {"segments": segs, "narration": narr}
        (EP / "clips/gwn_segments.json").write_text(json.dumps(allsegs, indent=1), encoding="utf8")
        sheet(v, segs)
        allsegs[v] = {"segments": segs, "narration": narr}
        clean = sum(s["dur"] for s in segs)
        quiet = sum(s["dur"] for s in segs if s["narr_s"] == 0)
        print(f"{v}: {len(segs)} segments, {clean:.0f}s clean picture, {quiet:.0f}s with no GWN voice")
    (EP / "clips/gwn_segments.json").write_text(json.dumps(allsegs, indent=1), encoding="utf8")
