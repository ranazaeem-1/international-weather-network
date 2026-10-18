"""Still-frame check of how clips will look in the draft (crop applied, fitted on the background colour).
Run from an episode's project/ folder:  python check_crops.py Q01 Q11 ...   (no ids = first 9 cropped clips)
Writes research/_work/crop_check.jpg (3 columns)."""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import render as R

first = {}
for ch in R.EDL["chapters"]:
    for s in ch["shots"] + ch["breaks"]:
        first.setdefault(s[0], s)
ids = sys.argv[1:] or [c for c, s in first.items() if len(s) > 3][:9]
out = R.EP / "research/_work"
out.mkdir(parents=True, exist_ok=True)
tiles = []
for i, c in enumerate(ids):
    s = first[c]
    vf = "scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2:color=0x27303a"
    if len(s) > 3 and s[3].get("crop"):
        x, y, w, h = s[3]["crop"]
        vf = f"crop=iw*{w}:ih*{h}:iw*{x}:ih*{y}," + vf
    t = out / f"_cc{i}.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s[1] + min(5, (s[2] - s[1]) / 2)), "-i", str(R.EP / R.EDL["media"][c]),
                    "-frames:v", "1", "-vf", vf, str(t)], check=True)
    tiles.append(t)
rows = (len(tiles) + 2) // 3
layout = "|".join(f"{(i % 3) * 640}_{(i // 3) * 360}" for i in range(len(tiles)))
args = []
for t in tiles:
    args += ["-i", str(t)]
subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", f"xstack=inputs={len(tiles)}:layout={layout}:fill=0x27303a",
                "-frames:v", "1", str(out / "crop_check.jpg")], check=True)
for t in tiles:
    t.unlink()
print(out / "crop_check.jpg")
