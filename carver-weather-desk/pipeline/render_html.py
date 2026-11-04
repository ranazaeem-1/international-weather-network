"""Render a Carver HTML page to PNG (still) or to an alpha image sequence / video (animation).

Still:      python render_html.py page.html out.png [--transparent] [--w 1920 --h 1080] [--at 3.5]
Animation:  python render_html.py page.html out.mov --dur 4.0 --fps 30 [--transparent]
            (pages use CSS/Web Animations; every animation is paused and seeked per frame,
             so renders are deterministic. A page may also define window.seek(t) for JS-driven parts.)
Query args: --q "k=v&k2=v2" is appended to the URL (pages read copy from location.search).
Options added for the card system (all optional, defaults keep the original behaviour):
  --at T             still: seek to T seconds instead of "the end" (1e6 s)
  --clip x,y,w,h     render only that region of the page (output is w x h)
  --crf 16           h264 quality for .mp4
  --jpeg             opaque renders: grab frames as JPEG q100 (about 2x faster, final is 4:2:0 h264 anyway)
Library use: from render_html import render; render("page.html", "out.mp4", dur=6, q="spec=...")
"""
import argparse, pathlib, subprocess, sys
from playwright.sync_api import sync_playwright

SEEK_JS = """(t) => {
  for (const a of document.getAnimations()) { a.pause(); a.currentTime = t * 1000; }
  if (window.seek) window.seek(t);
}"""


def _codec(out, transparent, crf):
    if out.suffix.lower() == ".mov":
        return ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le"] if transparent else \
               ["-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le"]
    # limited-range BT.709 4:2:0 (JPEG frames decode full-range; without the scale the file is tagged yuvj420p)
    return ["-vf", "scale=out_range=tv:out_color_matrix=bt709,format=yuv420p", "-c:v", "libx264", "-crf", str(crf), "-preset", "medium",
            "-pix_fmt", "yuv420p", "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-movflags", "+faststart"]


def render(html, out, w=1920, h=1080, transparent=False, dur=0.0, fps=30, q="", clip=None, at=None,
           crf=16, jpeg=False, still_too=None, log=None):
    """Render `html` to `out`. still_too=(t|None, png_path) also saves one still during an animation render
    (t=None: just after the page's window.cardEnd). Returns {"out", "zones", "end", "still_t"}."""
    url = pathlib.Path(html).resolve().as_uri() + (("?" + q) if q else "")
    out = pathlib.Path(out)
    shot = {}
    if clip:
        cx, cy, cw, ch = clip
        shot["clip"] = {"x": cx, "y": cy, "width": cw, "height": ch}
    use_jpeg = jpeg and not transparent and dur > 0
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        if log:
            pg.on("console", lambda m: log(f"[page {m.type}] {m.text}"))
            pg.on("pageerror", lambda e: log(f"[page error] {e}"))
        pg.goto(url); pg.wait_for_load_state("networkidle"); pg.evaluate("document.fonts.ready")
        info = {"out": out, "zones": [], "end": None}
        if pg.evaluate("window.cardReady !== undefined"):   # Carver cards: wait for the async build, surface errors
            pg.wait_for_function("window.cardReady === true || !!window.cardError", timeout=60000)
            err = pg.evaluate("window.cardError || null")
            if err:
                b.close(); raise RuntimeError(f"card build failed: {err}")
            info["zones"] = pg.evaluate("window.cardZones || []"); info["end"] = pg.evaluate("window.cardEnd ?? null")
        seekable = pg.evaluate("document.getAnimations().length > 0 || typeof window.seek === 'function'")
        if dur <= 0:
            if seekable:
                pg.evaluate(SEEK_JS, 1e6 if at is None else at)
            pg.screenshot(path=str(out), omit_background=transparent, **shot)
        else:
            n = round(dur * fps)
            fmt = ["-f", "image2pipe", "-c:v", "mjpeg" if use_jpeg else "png"]
            cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), *fmt, "-i", "-",
                   *_codec(out, transparent, crf), "-r", str(fps), "-frames:v", str(n), str(out)]
            ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            st_t, st_path = still_too if still_too else (None, None)
            if st_path and st_t is None:   # default still: just after everything has entered
                st_t = min(dur - 1.0 / fps, (info["end"] or dur * .6) + .4)
            info["still_t"] = st_t
            st_i = None if st_t is None else min(n - 1, max(0, round(st_t * fps)))
            try:
                for i in range(n):
                    pg.evaluate(SEEK_JS, i / fps)
                    if use_jpeg:
                        buf = pg.screenshot(type="jpeg", quality=100, **shot)
                    else:
                        buf = pg.screenshot(type="png", omit_background=transparent, **shot)
                    ff.stdin.write(buf)
                    if i == st_i:
                        pg.screenshot(path=str(st_path), omit_background=transparent, **shot)
            finally:
                ff.stdin.close()
                rc = ff.wait()
            if rc != 0:
                raise RuntimeError(f"ffmpeg failed ({rc}) for {out}")
        b.close()
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html"); ap.add_argument("out")
    ap.add_argument("--w", type=int, default=1920); ap.add_argument("--h", type=int, default=1080)
    ap.add_argument("--transparent", action="store_true")
    ap.add_argument("--dur", type=float, default=0); ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--q", default="")
    ap.add_argument("--at", type=float, default=None, help="still: seek time in seconds (default: end)")
    ap.add_argument("--clip", default=None, help="x,y,w,h region of the page to render")
    ap.add_argument("--crf", type=int, default=16)
    ap.add_argument("--jpeg", action="store_true", help="opaque animation: JPEG frames (faster)")
    a = ap.parse_args()
    clip = tuple(float(v) for v in a.clip.split(",")) if a.clip else None
    if clip and len(clip) != 4:
        sys.exit("--clip needs x,y,w,h")
    render(a.html, a.out, a.w, a.h, a.transparent, a.dur, a.fps, a.q, clip, a.at, a.crf, a.jpeg)
    print(a.out)


if __name__ == "__main__":
    main()
