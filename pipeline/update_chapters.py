"""Rewrite the CHAPTERS block and Length line of delivery/youtube.md from the current edl + narration manifest.
Run from an episode's project/ folder:  python update_chapters.py "<first chapter title>"
"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import render as R

first = sys.argv[1]
lines, t = [], 0.0
for ch in R.EDL["chapters"]:
    L, _ = R.plan_chapter(ch)
    title = first if ch["id"] == "S00" else R.MAN[ch["id"]]["title"]
    lines.append("%d:%02d — %s" % (int(t) // 60, int(t) % 60, title))
    t += L
length = "%d:%02d" % (int(t) // 60, int(t) % 60)
p = R.EP / "delivery/youtube.md"
if not p.exists():
    mds = list((R.EP / "delivery").glob("*.md"))
    p = mds[0] if mds else p
s = p.read_text(encoding="utf8")
s = re.sub(r"CHAPTERS\n(?:\d+:\d\d — .*\n)+", lambda _: "CHAPTERS\n" + "\n".join(lines) + "\n", s)
s = re.sub(r"Length \d+:\d\d", "Length " + length, s)
s = re.sub(r"\((\d+) min\)", "(%d min)" % round(t / 60), s, count=1)
p.write_text(s, encoding="utf8")
print("length", length)
print("\n".join(lines))
