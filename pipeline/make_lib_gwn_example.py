"""Build clips/lib: one folder the edit list reads from.

- F## : hard links to clips/found (downloaded, checked footage)
- U## : hard links to the user's accepted clips in clips/user
- GA###/GB### : clean stretches cut out of the user's own GWN videos (crop to the clip area, no GWN graphics)
"""
import json, os, subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

EP = Path(__file__).resolve().parents[1]
LIB = EP / "clips/lib"
LIB.mkdir(parents=True, exist_ok=True)

USER = ["3z_K7uEBgnR78lgY.mp4", "AOxouys9qxHrOnwQ.mp4", "hJTrWftWUQubxhXW.mp4"]   # ATPq... rejected (not Texas)
TAG = {"9LdVX46lUfA": "GA", "Ks_EcZ1y_SE": "GB"}


def link(src, dst):
    if not dst.exists():
        os.link(src, dst)


for p in sorted((EP / "clips/found").glob("F[0-9][0-9]_*.mp4")):
    link(p, LIB / p.name)
for i, name in enumerate(USER, 1):
    link(EP / "clips/user" / name, LIB / f"U{i:02d}_user_{Path(name).stem}.mp4")

segs = json.loads((EP / "clips/gwn_segments.json").read_text(encoding="utf8"))
jobs = []
for vid, d in segs.items():
    for s in d["segments"]:
        if not s["verdict"].startswith("ok"):
            continue
        n = int(s["id"].rsplit("_", 1)[1])
        quiet = "q" if s["narr_s"] == 0 and s["verdict"] == "ok" else "v"
        out = LIB / f"{TAG[vid]}{n:03d}_{quiet}_gwn.mp4"
        x, y, w, h = s["crop"]
        jobs.append((vid, s["in"], s["out"], x, w, out))


def cut(job):
    vid, a, b, x, w, out = job
    if out.exists() and out.stat().st_size > 0:
        return
    vf = f"crop=trunc(iw*{w}/2)*2:ih:trunc(iw*{x}):0"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-to", str(b), "-i", str(EP / "clips/raw" / f"{vid}.mp4"),
                    "-vf", vf, "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", str(out)], check=True)


with ThreadPoolExecutor(6) as ex:
    list(ex.map(cut, jobs))
print(len(list(LIB.glob("*.mp4"))), "clips in lib")
