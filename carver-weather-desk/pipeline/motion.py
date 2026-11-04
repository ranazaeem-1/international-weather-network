"""Parallel, frame-accurate renderer for Carver broadcast overlays (HTML/CSS -> PNG / ProRes 4444 alpha / h264).

A job is a dict:
  {"html": "brand-kit/src/overlays.html", "data": {...}, "out": "graphics/x.mov",
   "dur": 10.0, "fps": 30, "clip": [x, y, w, h] | null, "alpha": true, "static": [t0, t1] | null}
- data is exposed to the page as window.DATA (before load); the page builds its DOM from it.
- Every CSS/Web Animation is paused and seeked per frame (window.seek(t) is also called if defined).
- "static": frames inside [t0, t1] are identical; one is rendered and reused (holds between in/out animations).
- dur == 0 -> a single PNG (out must end in .png).
Usage:  python motion.py jobs.json [--workers 4]      (or import render_jobs)
"""
import json, os, shutil, subprocess, sys, tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

CWD = Path(__file__).resolve().parents[1]
SEEK = "(t) => { for (const a of document.getAnimations()) { a.pause(); a.currentTime = t * 1000; } if (window.seek) window.seek(t); }"


def _resolve(p):
    p = Path(p)
    return p if p.is_absolute() else CWD / p


BT709 = ["-vf", "scale=out_color_matrix=bt709:out_range=tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709"]


def _codec(out, alpha):
    # RGB frames -> YUV with the BT.709 matrix (HD), tagged, so overlays match footage and the final h264 exactly
    if out.suffix.lower() == ".mov":
        return BT709 + (["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-vendor", "apl0"] if alpha else
                        ["-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le"])
    return BT709 + ["-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]


def _render(job):
    from playwright.sync_api import sync_playwright
    out = _resolve(job["out"]); html = _resolve(job["html"])
    fps, dur = job.get("fps", 30), float(job.get("dur", 0))
    clip = job.get("clip"); alpha = job.get("alpha", True); static = job.get("static")
    jpeg = (not alpha) and dur > 0
    shot = {"omit_background": alpha, "caret": "hide"}
    shot.update({"type": "jpeg", "quality": 100} if jpeg else {"type": "png"})
    if clip:
        shot["clip"] = {"x": clip[0], "y": clip[1], "width": clip[2], "height": clip[3]}
    out.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        pg.add_init_script("window.DATA = " + json.dumps(job.get("data", {})) + ";")
        pg.goto(html.as_uri()); pg.wait_for_load_state("networkidle"); pg.evaluate("document.fonts.ready")
        pg.wait_for_function("window.READY === true", timeout=15000)
        if dur <= 0:
            pg.evaluate(SEEK, float(job.get("t", 1e3)))
            shot.pop("quality", None); shot["type"] = "png"
            pg.screenshot(path=str(out), **shot)
        else:
            n = round(dur * fps); held = None
            cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-f", "image2pipe", "-c:v", "mjpeg" if jpeg else "png",
                   "-i", "-", *_codec(out, alpha), "-r", str(fps), "-frames:v", str(n), str(out)]
            ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            try:
                for i in range(n):
                    t = i / fps
                    if static and static[0] <= t <= static[1]:
                        if held is None:
                            pg.evaluate(SEEK, t); held = pg.screenshot(**shot)
                        ff.stdin.write(held); continue
                    pg.evaluate(SEEK, t); ff.stdin.write(pg.screenshot(**shot))
            finally:
                ff.stdin.close(); rc = ff.wait()
            if rc:
                raise RuntimeError(f"ffmpeg failed ({rc}) for {out}")
        b.close()
    return str(out)


def render_jobs(jobs, workers=4):
    jobs = list(jobs)
    if not jobs:
        return []
    if len(jobs) == 1 or workers <= 1:
        return [_render(j) for j in jobs]
    with ProcessPoolExecutor(min(workers, len(jobs))) as ex:
        return list(ex.map(_render, jobs))


if __name__ == "__main__":
    a = sys.argv[1:]
    w = int(a[a.index("--workers") + 1]) if "--workers" in a else 4
    jobs = json.loads(Path(a[0]).read_text(encoding="utf-8"))
    for o in render_jobs(jobs, w):
        print(o)
