"""Pre-render the base footage shots listed in edit/jobs.json -> edit/base/bNNN.mp4 (exact frame counts).

  python build_base.py <episode_dir> [--workers 4] [--force]

Framing per shot ("mode" from plan_edit.py, override per clip in clips/framing.json):
  cover     16:9-ish footage: scale to cover 1920x1080, centre crop (or "focus": 0..1 horizontal position)
  blurfill  vertical / square phone video: the sharp picture centred over a blurred, darkened, navy-tinted copy
  "crop": [x, y, w, h] as fractions of the source, applied first (removes logos, burned captions, clocks)
Audio: the clip's own sound, unattenuated (the timeline sets the level), 48 kHz stereo AAC; silent sources get silence.
"""
import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from enc import h264

ENC = h264("inter") + ["-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709"]


def has_audio(p):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True).stdout.strip()
    return bool(o)


def vf(mode, fps, crop=None, focus=0.5):
    pre = f"crop=iw*{crop[2]}:ih*{crop[3]}:iw*{crop[0]}:ih*{crop[1]}," if crop else ""
    if mode == "cover":
        return f"[0:v]{pre}scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080:(iw-1920)*{focus}:(ih-1080)/2,setsar=1,fps={fps}[v]"
    return (f"[0:v]{pre}split=2[a][b];[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,gblur=sigma=34,"
            f"eq=brightness=-0.09:saturation=0.75,drawbox=c=0x0A1B38@0.40:t=fill[bg];[b]scale=-2:1080:flags=lanczos[fg];"
            f"[bg][fg]overlay=(W-w)/2:0,setsar=1,fps={fps}[v]")


def one(ep, j, over, force):
    out = ep / j["out"]
    if out.exists() and not force:
        return f"{j['id']} cached"
    out.parent.mkdir(parents=True, exist_ok=True)
    src = ep / j["src"]; o = over.get(j["clip"], {}); mode = o.get("mode", j["mode"]); fps = j["fps"]
    n = round(j["dur"] * fps)
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{j['in']:.3f}", "-t", f"{j['dur'] + 0.5:.3f}", "-i", str(src)]
    aud = has_audio(src)
    if not aud:
        cmd += ["-f", "lavfi", "-t", f"{j['dur']:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
    cmd += ["-filter_complex", vf(mode, fps, o.get("crop"), o.get("focus", 0.5)), "-map", "[v]", "-map", "0:a:0" if aud else "1:a",
            "-frames:v", str(n), "-r", str(fps), *ENC, "-af", "aresample=48000,aformat=channel_layouts=stereo",
            "-c:a", "aac", "-b:a", "192k", "-t", f"{n / fps:.4f}", "-movflags", "+faststart", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"{j['id']} {j['clip']}: {r.stderr[-500:]}")
    return f"{j['id']} {j['clip']} {mode:<8} in {j['in']:6.2f} dur {j['dur']:5.2f}"


def main():
    ep = Path(sys.argv[1]).resolve()
    w = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 4
    jobs = json.loads((ep / "edit/jobs.json").read_text(encoding="utf-8"))["base"]
    fj = ep / "clips/framing.json"; over = json.loads(fj.read_text(encoding="utf-8")) if fj.exists() else {}
    with ThreadPoolExecutor(w) as ex:
        for line in ex.map(lambda j: one(ep, j, over, "--force" in sys.argv), jobs):
            print(line, flush=True)


if __name__ == "__main__":
    main()
