"""Render edit/timeline.json -> exports/<name>.mp4 (the same timeline the CapCut draft is built from).

  python compose.py <episode_dir> [--chunk 20] [--workers 3] [--range a,b] [--sheet]

Video: the timeline is cut into ~20 s chunks rendered in parallel (ffmpeg overlay graph per chunk, 4:4:4 compositing,
       h264_nvenc, or libx264 without an NVIDIA GPU), then concatenated losslessly. Every track item is seeked into its chunk, so cuts are frame-exact.
Audio: mixed in numpy at 48 kHz (voice, base clips' nat sound at their timeline volumes + fades, sfx), then a two-pass
       loudnorm to -16 LUFS / -1.5 dBTP.
--range a,b renders just that span (seconds) for a quick look; --sheet writes a QC contact sheet next to the export.
"""
import json, subprocess, sys, shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from enc import h264

SR = 48000
STILL = {".png", ".jpg", ".jpeg"}
COLOR_TAGS = ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709"]
_bbox_cache = {}


def rpath(tl, s):
    p = Path(s)
    return p if p.is_absolute() else Path(tl["root"]) / p


def still_bbox(path):
    """crop a full-frame transparent PNG to its visible box (fast overlays); returns (x, y, w, h) or None."""
    if path in _bbox_cache:
        return _bbox_cache[path]
    from PIL import Image
    im = Image.open(path)
    bb = None
    if im.mode in ("RGBA", "LA") and im.size == (1920, 1080):
        b = im.getchannel("A").getbbox()
        if b:
            x0, y0, x1, y1 = b; x0 -= x0 % 2; y0 -= y0 % 2; x1 += x1 % 2; y1 += y1 % 2
            bb = (x0, y0, x1 - x0, y1 - y0)
    _bbox_cache[path] = bb
    return bb


_size_cache = {}


def vsize(path):
    if path not in _size_cache:
        o = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path)]).decode()
        w, h = o.strip().split(",")[:2]; _size_cache[path] = (int(w), int(h))
    return _size_cache[path]


def kf_expr(keys, start):
    """Piecewise-linear ffmpeg expression of overlay time t for [[t_item, value]] keys (item starts at chunk time `start`).
    Linear between keys, held before the first and after the last: the same interpolation CapCut uses for keyframes."""
    T = f"(t-({start:.4f}))"; ks = sorted(keys)
    e = f"{ks[-1][1]}"
    for (t0, v0), (t1, v1) in reversed(list(zip(ks, ks[1:]))):
        seg = f"{v0}" if t1 - t0 < 1e-6 else f"({v0}+({v1}-({v0}))*({T}-{t0})/{t1 - t0:.4f})"
        e = f"if(lt({T},{t1}),{seg},{e})"
    return f"if(lt({T},{ks[0][0]}),{ks[0][1]},{e})"


def chunk_cmd(tl, f0, f1, out):
    fps = tl["fps"]; a, b = f0 / fps, f1 / fps; n = f1 - f0
    args, filt, k, cur = [], [f"color=c=0x050C1A:s=1920x1080:r={fps}:d={n / fps:.4f},format=yuv444p[c0]"], 0, "c0"
    for tr in tl["tracks"]:
        if tr["type"] != "video":
            continue
        for it in tr["items"]:
            s0, s1 = it["start"], it["start"] + it["dur"]
            if s0 >= b - 1e-6 or s1 <= a + 1e-6:
                continue
            p = rpath(tl, it["src"]); ext = p.suffix.lower()
            seg0, seg1 = max(a, s0), min(b, s1); d = seg1 - seg0; off = seg0 - a
            x, y, w, h = it.get("x", 0), it.get("y", 0), it.get("w", 1920), it.get("h", 1080)
            chain = []
            if ext in STILL:
                args += ["-loop", "1", "-framerate", str(fps), "-t", f"{d:.4f}", "-i", str(p)]
                bb = still_bbox(str(p)) if (w, h) == (1920, 1080) and (x, y) == (0, 0) else None
                if bb:
                    chain.append(f"crop={bb[2]}:{bb[3]}:{bb[0]}:{bb[1]}"); x, y = bb[0], bb[1]
                else:
                    chain.append(f"scale={w}:{h}:flags=lanczos")
                chain[-1] += ":out_color_matrix=bt709:out_range=tv" if chain[-1].startswith("scale") else ""
                chain.append("format=yuva444p")
            else:
                sin = it.get("in", 0.0) + (seg0 - s0)
                args += ["-ss", f"{sin:.4f}", "-t", f"{d + 0.2:.4f}", "-i", str(p)]
                chain.append(f"trim=duration={d:.4f}")
                if vsize(p) != (w, h):
                    chain.append(f"scale={w}:{h}:flags=lanczos")
                if ext == ".mov":
                    chain.append("format=yuva444p")
            op = it.get("opacity", 1.0)
            if op < 0.999:
                chain += ["format=yuva444p", f"colorchannelmixer=aa={op:.3f}"]
            fiv = it.get("fade_in_video", 0)
            if fiv and seg0 - s0 < fiv:
                chain += ["format=yuva444p", f"fade=t=in:st={max(0.0, off - (seg0 - s0)):.4f}:d={fiv}:alpha=1"]
            ai, ao = float(it.get("alpha_in", 0) or 0), float(it.get("alpha_out", 0) or 0)   # window 'rise' transition
            tin = seg0 - s0                                                             # item time at this input's t = 0
            if (ai and tin < ai) or (ao and seg1 > s1 - ao):
                fa = []
                if ai and tin < ai:
                    fa.append(f"clip((T+{tin:.4f})/{ai},0,1)")
                if ao and seg1 > s1 - ao:
                    fa.append(f"clip(({s1 - s0:.4f}-(T+{tin:.4f}))/{ao},0,1)")
                en = "+".join(([f"lt(t+{tin:.4f},{ai})"] if ai else []) + ([f"gt(t+{tin:.4f},{s1 - s0 - ao:.4f})"] if ao else []))
                chain += ["format=yuva444p", f"geq=lum='lum(X,Y)':cb='cb(X,Y)':cr='cr(X,Y)':a='alpha(X,Y)*{'*'.join(fa)}':enable='{en}'"]
            chain.append(f"setpts=PTS-STARTPTS+{off:.4f}/TB")
            filt.append(f"[{k}:v]{','.join(chain)}[v{k}]")
            ox = f"'{x}+{kf_expr(it['kf_x'], s0 - a)}'" if it.get("kf_x") else x       # window 'slide'/'rise' keyframes
            oy = f"'{y}+{kf_expr(it['kf_y'], s0 - a)}'" if it.get("kf_y") else y
            filt.append(f"[{cur}][v{k}]overlay=x={ox}:y={oy}:eof_action=pass:format=yuv444[c{k + 1}]")
            cur = f"c{k + 1}"; k += 1
    filt.append(f"[{cur}]format=yuv420p,setsar=1[out]")
    return ["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", ";".join(filt), "-map", "[out]", "-frames:v", str(n), "-r", str(fps),
            *h264("final"),
            "-g", str(fps * 2), "-bf", "2", *COLOR_TAGS, "-an", str(out)]


def decode(path, t_in, dur):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t_in:.4f}", "-t", f"{dur:.4f}", "-i", str(path), "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


def mix(tl, a, b, wav):
    N = int(round((b - a) * SR)); m = np.zeros((N, 2), np.float32)
    for tr in tl["tracks"]:
        for it in tr["items"]:
            vol = it.get("volume", 1.0 if tr["type"] == "audio" else 0.0)
            if vol <= 0:
                continue
            s0, s1 = it["start"], it["start"] + it["dur"]
            if s0 >= b or s1 <= a:
                continue
            seg0, seg1 = max(a, s0), min(b, s1)
            x = decode(rpath(tl, it["src"]), it.get("in", 0.0) + (seg0 - s0), seg1 - seg0) * vol
            n = len(x); t = (np.arange(n) / SR) + (seg0 - s0)          # time from item start
            g = np.ones(n, np.float32)
            fi, fo = it.get("fade_in", 0), it.get("fade_out", 0)
            if fi:
                g = np.minimum(g, np.clip(t / fi, 0, 1))
            if fo:
                g = np.minimum(g, np.clip((it["dur"] - t) / fo, 0, 1))
            k = int(round((seg0 - a) * SR)); n = min(n, N - k)
            m[k:k + n] += x[:n] * g[:n, None]
    raw = wav.with_suffix(".raw.wav")
    from scipy.io import wavfile
    wavfile.write(raw, SR, np.clip(m, -1, 1))
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(raw), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    j = json.loads(p.stderr[p.stderr.rfind("{"):p.stderr.rfind("}") + 1])
    ln = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
          f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", ln, "-ar", str(SR), "-c:a", "pcm_s16le", str(wav)], check=True)
    raw.unlink(missing_ok=True)
    return float(j["input_i"])


def sheet(tl, mp4, out, a=0.0):
    """QC contact sheet: 2 s into each marker + the end screen."""
    from PIL import Image, ImageDraw
    ts = [m["t"] + 2.0 for m in tl["markers"]] + [tl["duration"] - 6.0]
    ts = [t - a for t in ts if 0 <= t - a < tl["duration"]]
    tiles = []
    for t in ts:
        f = out.with_name(f"_qc_{t:07.2f}.jpg")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(mp4), "-frames:v", "1", "-q:v", "3", str(f)], check=True)
        im = Image.open(f).convert("RGB").resize((640, 360)); d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 92, 22], fill=(0, 0, 0)); d.text((5, 5), f"{int(t // 60)}:{t % 60:05.2f}", fill=(255, 220, 0)); tiles.append(im); f.unlink()
    cols = 3; rows = -(-len(tiles) // cols); sh = Image.new("RGB", (640 * cols, 360 * rows))
    for i, im in enumerate(tiles):
        sh.paste(im, ((i % cols) * 640, (i // cols) * 360))
    sh.save(out, quality=85)


def main():
    ep = Path(sys.argv[1]).resolve(); av = sys.argv
    tl = json.loads((ep / "edit/timeline.json").read_text(encoding="utf-8"))
    fps = tl["fps"]; chunk = float(av[av.index("--chunk") + 1]) if "--chunk" in av else 20.0
    workers = int(av[av.index("--workers") + 1]) if "--workers" in av else 3
    a, b = (map(float, av[av.index("--range") + 1].split(","))) if "--range" in av else (0.0, tl["duration"])
    F0, F1 = round(a * fps), round(min(b, tl["duration"]) * fps); step = int(chunk * fps)
    work = ep / "edit/_render"; shutil.rmtree(work, ignore_errors=True); work.mkdir(parents=True)
    parts = [(f, min(F1, f + step), work / f"c{i:03d}.mp4") for i, f in enumerate(range(F0, F1, step))]

    def run(p):
        r = subprocess.run(chunk_cmd(tl, *p), capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(f"chunk {p[2].name}: {r.stderr[-1500:]}")
        return p[2].name
    with ThreadPoolExecutor(workers) as ex:
        for nme in ex.map(run, parts):
            print("rendered", nme, flush=True)
    (work / "list.txt").write_text("".join(f"file '{p[2].as_posix()}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(work / "list.txt"), "-c", "copy", str(work / "video.mp4")], check=True)
    lufs = mix(tl, F0 / fps, F1 / fps, work / "master.wav")
    name = tl["name"] + ("" if "--range" not in av else f"_range_{int(a)}-{int(b)}")
    out = ep / "exports" / f"{name}.mp4"; out.parent.mkdir(exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(work / "video.mp4"), "-i", str(work / "master.wav"), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest", str(out)], check=True)
    print(f"wrote {out}  ({(F1 - F0) / fps:.2f} s, mix in {lufs:.1f} LUFS -> -16)")
    if "--sheet" in av:
        sheet(tl, out, out.with_name(out.stem + "_qc.jpg"), a=F0 / fps); print("qc sheet", out.with_name(out.stem + "_qc.jpg"))
    shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
