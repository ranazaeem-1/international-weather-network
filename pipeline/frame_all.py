"""Pre-frame every clip/crop combination the edit actually uses, in parallel (build_capcut.py then reuses them)."""
from concurrent.futures import ThreadPoolExecutor
import render as R, build_capcut as B

R.WORK.mkdir(parents=True, exist_ok=True)
B.spans()
jobs = {}
for ch in R.EDL["chapters"]:
    for _, _, _, _, pieces in R.plan_chapter(ch)[1]:
        for clip, _, _, opts in pieces:
            if not B.is_horizontal(clip, opts):       # 16:9 clips are used as originals (21 Oct): nothing to frame
                jobs[(clip, B.crop_key(opts))] = (clip, opts)
print(len(jobs), "clip ranges to frame (vertical / non-16:9 only)", flush=True)


def go(job):
    c, opts = job
    try:
        B.framed(c, opts)
        return c + " ok"
    except Exception as e:
        return c + " FAIL " + str(e)[-200:]


with ThreadPoolExecutor(6) as ex:
    for r in ex.map(go, jobs.values()):
        print(r, flush=True)
