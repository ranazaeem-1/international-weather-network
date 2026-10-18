"""Pre-frame every clip/crop combination the edit actually uses, in parallel (build_capcut.py then reuses them)."""
from concurrent.futures import ThreadPoolExecutor
import render as R, build_capcut as B

R.WORK.mkdir(parents=True, exist_ok=True)
B.spans()
jobs = {}
for ch in R.EDL["chapters"]:
    for _, _, _, _, pieces in R.plan_chapter(ch)[1]:
        for clip, _, _, opts in pieces:
            jobs[(clip, B.crop_key(opts))] = (clip, opts)


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
