"""Delete framed copies that are unreadable or shorter than the span in their name (e.g. an ffmpeg killed mid-encode).
Run from an episode's project/ folder before frame_all.py when a run was interrupted."""
import re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import render as R


def dur(p):
    try:
        return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                             stderr=subprocess.DEVNULL).strip() or 0)
    except Exception:
        return 0.0


bad = 0
_fd = "_framed" if R.EDL.get("framed_lang", "en") == "en" else "_framed_" + R.EDL["framed_lang"]   # must match build_capcut.framed
for d in {(R.EP / rel).parent / _fd for rel in R.EDL["media"].values()}:
    for f in d.glob("*.mp4"):
        m = re.search(r"_s(\d+)-(\d+)(\.part)?\.mp4$", f.name)
        if f.name.endswith(".part.mp4") or (m and dur(f) < int(m.group(2)) - int(m.group(1)) - 1.5):
            print("bad", f.name)
            f.unlink()
            bad += 1
print("removed", bad)
