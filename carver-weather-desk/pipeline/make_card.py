"""Render Carver Weather Desk info cards (pipeline/cards/<type>.html) from JSON specs.

  python make_card.py <spec.json> [out.mp4] [--png [out.png]]   one card (default out: <spec dir>/<id>.mp4)
  python make_card.py a.json b.json c.json --png -j 4             several specs, in parallel
  python make_card.py --episode <ep_dir> [--force] [-j 4]          every graphics/cards/*.json whose MP4 is
                                                                   missing or older than the spec
Output: 1920x1080, 30 fps, opaque h264 MP4 (crf 16), exactly `dur` seconds. Spec format: docs/cards.md.
Map cards with a video base render their overlay as a ProRes 4444 alpha MOV and are composited over the
loop with ffmpeg (no Ken Burns on video bases).
"""
import argparse, json, math, pathlib, subprocess, sys, tempfile, time, urllib.parse
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
CARDS = HERE / "cards"
GEO = ROOT / "brand-kit" / "geo"
DEFAULT_GOES = ROOT / "brand-kit" / "src" / "goes_conus.jpg"
sys.path.insert(0, str(HERE))
import goes_px                     # noqa: E402
from render_html import render     # noqa: E402

TYPES = ("map", "stat", "chart", "timeline", "list", "split", "document")
FPS = 30


class SpecError(ValueError):
    pass


def find(p, spec_dir):
    p = pathlib.Path(p)
    cands = [p] if p.is_absolute() else [spec_dir / p, ROOT / p, pathlib.Path.cwd() / p]
    for c in cands:
        if c.exists():
            return c.resolve()
    raise SpecError(f"asset not found: {p} (looked next to the spec, in {ROOT} and in the cwd)")


def uri(p):
    return pathlib.Path(p).resolve().as_uri()


def img_size(p):
    from PIL import Image
    with Image.open(p) as im:
        return im.size


def video_size(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    w, h = r.stdout.strip().split(",")[:2]
    return int(w), int(h)


# ---------- projection maths (mirrors cards/card.js) ----------
def proj_fn(P, W, H):
    t = (P or {}).get("type", "goes_conus")
    if t == "goes_conus":
        def f(lon, lat):
            x, y = goes_px.scan(lat, lon)
            return ((x - goes_px.XMIN) / (goes_px.XMAX - goes_px.XMIN) * W, (goes_px.YMAX - y) / (goes_px.YMAX - goes_px.YMIN) * H)
        return f
    if "bbox" not in P:
        raise SpecError(f"projection {t} needs bbox [lon_min, lat_min, lon_max, lat_max]")
    a, b, c, d = P["bbox"]
    if t == "linear":
        return lambda lon, lat: ((lon - a) / (c - a) * W, (d - lat) / (d - b) * H)
    if t == "mercator":
        my = lambda la: math.log(math.tan(math.pi / 4 + math.radians(la) / 2))
        return lambda lon, lat: ((lon - a) / (c - a) * W, (my(d) - my(lat)) / (my(d) - my(b)) * H)
    raise SpecError(f"unknown projection type {t!r} (goes_conus | linear | mercator)")


def view_rect(S, W, H):
    """Visible window of the base in natural image px, expanded to 16:9 and kept inside the image."""
    P = S.get("projection") or {"type": "goes_conus"}
    goes = P.get("type", "goes_conus") == "goes_conus"
    V = S.get("view") or {}
    if "crop" in V:                                   # goes: 2500x1500 product px; others: image px
        x0, y0, x1, y1 = V["crop"]
        if goes:
            x0, x1, y0, y1 = x0 * W / 2500, x1 * W / 2500, y0 * H / 1500, y1 * H / 1500
    elif "bbox" in V:
        f = proj_fn(P, W, H)
        lo0, la0, lo1, la1 = V["bbox"]
        pts = [f(lo0 + (lo1 - lo0) * i / 24, la) for i in range(25) for la in (la0, la1)] + \
              [f(lo, la0 + (la1 - la0) * i / 24) for i in range(25) for lo in (lo0, lo1)]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        pad = V.get("pad", 0.04)
        dx, dy = (x1 - x0) * pad, (y1 - y0) * pad
        x0, x1, y0, y1 = x0 - dx, x1 + dx, y0 - dy, y1 + dy
    elif goes:                                        # frame M framing
        x0, y0, x1, y1 = 700 * W / 2500, 50 * H / 1500, 2100 * W / 2500, 837.5 * H / 1500
    else:
        x0, y0, x1, y1 = 0, 0, W, H
    cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
    if w / h > 16 / 9:
        h = w * 9 / 16
    else:
        w = h * 16 / 9
    if w > W or h > H:                                # bigger than the image: largest 16:9 window inside it
        s = min(W / w, H / h)
        w, h = w * s, h * s
    x0 = min(max(cx - w / 2, 0), W - w)
    y0 = min(max(cy - h / 2, 0), H - h)
    return {"x0": x0, "y0": y0, "k": 1920 / w, "img_w": W, "img_h": H}


_STATES = None


def states_index():
    global _STATES
    if _STATES is None:
        fc = json.loads((GEO / "us-states.geojson").read_text(encoding="utf-8"))
        _STATES = {}
        for f in fc["features"]:
            _STATES[f["properties"]["abbr"].upper()] = f
            _STATES[f["properties"]["name"].upper()] = f
    return _STATES


def rings_of(g):
    """GeoJSON (FeatureCollection | Feature | geometry) -> list of lon/lat rings."""
    t = g.get("type")
    if t == "FeatureCollection":
        return [r for f in g["features"] for r in rings_of(f)]
    if t == "Feature":
        return rings_of(g["geometry"]) if g.get("geometry") else []
    if t == "GeometryCollection":
        return [r for gg in g["geometries"] for r in rings_of(gg)]
    if t == "Polygon":
        return g["coordinates"]
    if t == "MultiPolygon":
        return [r for poly in g["coordinates"] for r in poly]
    return []


# ---------- spec ----------
def validate(S):
    warn = []
    for k in ("id", "type", "dur"):
        if k not in S:
            raise SpecError(f"spec needs '{k}'")
    if S["type"] not in TYPES:
        raise SpecError(f"type {S['type']!r} is not one of {', '.join(TYPES)}")
    if not (0.5 <= float(S["dur"]) <= 120):
        raise SpecError("dur must be 0.5-120 s")
    for it in S.get("items", []) if S["type"] == "list" else []:
        txt = it if isinstance(it, str) else it.get("text", "")
        if len(txt) > 60:
            warn.append(f"list item over 60 chars ({len(txt)}): {txt[:40]}...")
    def ats(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "at" and isinstance(v, (int, float)) and v > float(S["dur"]) - 0.3:
                    warn.append(f"an element starts at {v} s, too close to the end of a {S['dur']} s card")
                ats(v)
        elif isinstance(o, list):
            for v in o:
                ats(v)
    ats(S)
    return warn


def resolve(S, spec_dir):
    R = json.loads(json.dumps(S))
    R.setdefault("strap_clear", False)
    R["dur"] = float(R["dur"])
    if R.get("bg_image"):
        R["bg_image"] = uri(find(R["bg_image"], spec_dir))
    if R["type"] == "map":
        base = R.get("base") or {}
        if isinstance(base, str):
            base = {"image": base}
        if base.get("video"):
            vp = find(base["video"], spec_dir)
            W, H = video_size(vp)
            R["_video"], R["_alpha"] = str(vp), True
        else:
            ip = find(base["image"], spec_dir) if base.get("image") else DEFAULT_GOES
            if not pathlib.Path(ip).exists():
                raise SystemExit(f"{R.get('id')}: map card needs base.image (fetch a current satellite/radar frame); "
                                 f"the old default {DEFAULT_GOES.name} is not shipped in the repo")
            W, H = img_size(ip)
            R["_base_image"] = uri(ip)
        R["_view"] = view_rect(R, W, H)
        if R.get("states"):
            R["_states_lines"] = json.loads((GEO / "us-states-lines.geojson").read_text(encoding="utf-8"))["geometry"]["coordinates"]
        for pg in R.get("polygons", []):
            rings = []
            for name in pg.get("states", []):
                f = states_index().get(str(name).upper())
                if not f:
                    raise SpecError(f"unknown state {name!r} (use USPS code or full name)")
                rings += rings_of(f)
            g = pg.get("geojson")
            if isinstance(g, str):
                g = json.loads(find(g, spec_dir).read_text(encoding="utf-8"))
            if g:
                rings += rings_of(g)
            if pg.get("geometry"):
                rings += rings_of(pg["geometry"])
            pg.pop("geojson", None)
            pg["_rings"] = [[[round(x, 4), round(y, 4)] for x, y, *_ in r] for r in rings]
    return R


def composite(R, mov, out, dur, crf=16):
    V = R["_view"]; k = V["k"]
    sw, sh = math.ceil(V["img_w"] * k), math.ceil(V["img_h"] * k)
    cx, cy = min(round(V["x0"] * k), sw - 1920), min(round(V["y0"] * k), sh - 1080)
    n = round(dur * FPS)
    fc = (f"[0:v]fps={FPS},scale={sw}:{sh}:flags=lanczos,crop=1920:1080:{cx}:{cy},setsar=1[b];"
          f"[b][1:v]overlay=0:0:format=auto,scale=out_range=tv:out_color_matrix=bt709,format=yuv420p[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", R["_video"], "-i", str(mov),
                    "-filter_complex", fc, "-map", "[v]", "-frames:v", str(n), "-r", str(FPS), "-an",
                    "-c:v", "libx264", "-crf", str(crf), "-preset", "medium", "-pix_fmt", "yuv420p", "-color_range", "tv",
                    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-movflags", "+faststart",
                    str(out)], check=True)


def out_path(spec_path, S):
    return spec_path.with_name(f"{S.get('id') or spec_path.stem}.mp4")


def render_card(spec_path, out=None, png=None, log=print):
    """Render one spec. png=True -> <out>.png; png=<path> -> that path. Returns a result dict."""
    spec_path = pathlib.Path(spec_path).resolve()
    S = json.loads(spec_path.read_text(encoding="utf-8"))
    warns = validate(S)
    out = pathlib.Path(out).resolve() if out else out_path(spec_path, S)
    out.parent.mkdir(parents=True, exist_ok=True)
    png = (out.with_suffix(".png") if png is True else pathlib.Path(png).resolve()) if png else None
    R = resolve(S, spec_path.parent)
    msgs = []
    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix="cwd_card_") as td:
        td = pathlib.Path(td)
        js = td / "spec.js"
        js.write_text("window.CARD = " + json.dumps(R, ensure_ascii=False) + ";\n", encoding="utf-8")
        q = urllib.parse.urlencode({"spec": js.as_uri()})
        html = CARDS / f"{R['type']}.html"
        dur, crf = R["dur"], int(R.get("crf", 16))
        st = R.get("still_at")
        if R.get("_video"):
            mov = td / "overlay.mov"
            info = render(html, mov, transparent=True, dur=dur, fps=FPS, q=q, log=msgs.append)
            composite(R, mov, out, dur, crf)
            if png:
                t = st if st is not None else min(dur - 1 / FPS, (info["end"] or dur * .6) + .4)
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(out), "-frames:v", "1", str(png)], check=True)
                info["still_t"] = t
        else:
            info = render(html, out, dur=dur, fps=FPS, q=q, crf=crf, jpeg=True,
                          still_too=(st, png) if png else None, log=msgs.append)
    dt = time.time() - t0
    msgs = [m for m in msgs if "warn" in m.lower() or "error" in m.lower()]
    res = {"spec": str(spec_path), "out": str(out), "png": str(png) if png else None, "sec": round(dt, 1),
           "frames": round(R["dur"] * FPS), "zones": info.get("zones", []), "warnings": warns + msgs, "still_t": info.get("still_t")}
    if log:
        log(f"{out.name}: {res['frames']} frames in {dt:.1f} s" + (f"  (still @ {res['still_t']:.2f} s)" if png and res["still_t"] is not None else ""))
        for z in res["zones"]:
            log(f"  ZONE  {z}")
        for w in res["warnings"]:
            log(f"  WARN  {w}")
    return res


def _job(args):
    spec, out, png = args
    try:
        return render_card(spec, out, png, log=None)
    except Exception as e:  # report and keep going
        return {"spec": spec, "error": f"{type(e).__name__}: {e}"}


def run_many(jobs, workers=4):
    results = []
    with ProcessPoolExecutor(max_workers=max(1, workers)) as ex:
        futs = [ex.submit(_job, j) for j in jobs]
        for f in as_completed(futs):
            r = f.result(); results.append(r)
            if "error" in r:
                print(f"FAILED {pathlib.Path(r['spec']).name}: {r['error']}")
                continue
            print(f"{pathlib.Path(r['out']).name}: {r['frames']} frames in {r['sec']} s")
            for z in r["zones"]:
                print(f"  ZONE  {z}")
            for w in r["warnings"]:
                print(f"  WARN  {w}")
    return results


def episode(ep, force=False, workers=4, png=False):
    cdir = pathlib.Path(ep) / "graphics" / "cards"
    specs = sorted(cdir.glob("*.json"))
    jobs = []
    for sp in specs:
        S = json.loads(sp.read_text(encoding="utf-8"))
        out = out_path(sp, S)
        if force or not out.exists() or out.stat().st_mtime < sp.stat().st_mtime:
            jobs.append((str(sp), str(out), png))
    print(f"{len(specs)} card specs in {cdir}, {len(jobs)} to render")
    return run_many(jobs, workers) if jobs else []


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("specs", nargs="*", help="spec.json [out.mp4]  or  several spec.json files")
    ap.add_argument("--episode", help="episode dir: render stale graphics/cards/*.json")
    ap.add_argument("--force", action="store_true", help="with --episode: re-render everything")
    ap.add_argument("--png", nargs="?", const=True, default=False, help="also save a still after all elements entered")
    ap.add_argument("-j", "--jobs", type=int, default=4)
    a = ap.parse_args()
    t0 = time.time()
    if a.episode:
        rs = episode(a.episode, a.force, a.jobs, bool(a.png))
    elif len(a.specs) == 2 and a.specs[1].lower().endswith(".mp4"):
        rs = [render_card(a.specs[0], a.specs[1], a.png)]
    elif len(a.specs) == 1:
        rs = [render_card(a.specs[0], None, a.png)]
    elif a.specs:
        rs = run_many([(s, None, bool(a.png)) for s in a.specs], a.jobs)
    else:
        ap.error("give a spec.json or --episode <dir>")
    print(f"done: {len(rs)} card(s) in {time.time() - t0:.1f} s")
    if any("error" in r for r in rs):
        sys.exit(1)


if __name__ == "__main__":
    main()
