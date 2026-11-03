"""Build clips/lib for an episode: today's clips/found plus earlier episodes' clips with a Y prefix (hard links).

usage: python make_ylib.py <episode> <old_episode>[:EXCLUDE1,EXCLUDE2] [...]
Writes <episode>/clips/lib/*, <episode>/research/sources_lib.csv and <episode>/research/ylib_muted.json
(old clip ids muted in their own edl.json, prefixed with Y).
"""
import csv, json, os, sys
from pathlib import Path

ep = Path(sys.argv[1]).resolve()
lib = ep / "clips/lib"
lib.mkdir(parents=True, exist_ok=True)


def link(src, dst):
    if dst.exists():
        return
    try:
        os.link(src, dst)
    except OSError:
        import shutil
        shutil.copy2(src, dst)


for f in (ep / "clips/found").glob("*.*"):
    if f.suffix.lower() in (".mp4", ".jpg", ".png", ".mov"):
        link(f, lib / f.name)

rows, muted, seen = [], set(), set()
for arg in sys.argv[2:]:
    old, _, excl = arg.partition(":")
    old = Path(old).resolve()
    excl = set(x for x in excl.split(",") if x)
    try:
        om = set(json.loads((old / "project/edl.json").read_text(encoding="utf8")).get("muted", []))
    except Exception:
        om = set()
    for f in sorted(((old / "clips/lib") if (old / "clips/lib").exists() else (old / "clips/found")).glob("*.*")):
        if f.suffix.lower() not in (".mp4", ".jpg"):
            continue
        cid = f.name.split("_")[0]
        if cid in excl:
            continue
        key = f.name.split("_", 1)[1] + str(f.stat().st_size)
        if key in seen:          # same file already taken from another old episode
            continue
        seen.add(key)
        nid = "Y" + cid
        link(f, lib / ("Y" + f.name))
        if cid in om:
            muted.add(nid)
        rows.append({"clip_id": nid, "filename": "Y" + f.name, "reused_from": f"{old.name} ({cid})",
                     "muted_in_source_episode": cid in om})

with open(ep / "research/sources_lib.csv", "w", newline="", encoding="utf8") as fh:
    w = csv.DictWriter(fh, fieldnames=["clip_id", "filename", "reused_from", "muted_in_source_episode"])
    w.writeheader()
    w.writerows(rows)
(ep / "research/ylib_muted.json").write_text(json.dumps(sorted(muted)), encoding="utf8")
print(f"lib: {len(list(lib.glob('*.*')))} files ({len(rows)} reused, {len(muted)} reused muted)")
