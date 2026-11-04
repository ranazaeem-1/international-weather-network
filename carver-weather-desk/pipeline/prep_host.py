"""Prepare the HeyGen host video for the edit.

  python prep_host.py <episode_dir>              uses host/glenn_raw.mp4 (the owner's HeyGen export)
  python prep_host.py <episode_dir> --standin    first builds a STAND-IN host/glenn_raw.mp4 for pipeline tests:
                                                 Glenn's studio still + an edge-tts voice reading script/heygen_paste.txt
Outputs (host/):
  host_meta.json   fps (project fps follows HeyGen: 25 -> 25, 24 -> 24, else 30), duration, crop rects, loudness
  host_full.mp4    1920x1080 full-frame host (no audio)
  host_box.mp4     720x405 head-shoulders-chest crop for the Desk Window (no audio)
  host_end.mp4     896x504 slightly wider crop for the end screen (no audio)
  vo.wav           voice: rumble cut, light presence EQ, gentle compression, two-pass loudnorm -16 LUFS / -1.5 dBTP
The crop is placed from OpenCV face detection over 7 frames (median face box); fallback = studio-still framing.
"""
import asyncio, json, statistics, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CWD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
from enc import h264
YUNET = Path(__file__).parent / "models/face_detection_yunet_2023mar.onnx"
YUNET_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
STILL = CWD / "brand-kit/host/glenn-studio-16x9.png"
STANDIN_VOICE = "en-US-ChristopherNeural"
VO_CHAIN = ("highpass=f=70,equalizer=f=220:t=q:w=1.0:g=-1.5,equalizer=f=3200:t=q:w=1.4:g=2,"
            "acompressor=threshold=-20dB:ratio=2.2:attack=8:release=150:makeup=1.2")


def sh(args, **kw):
    return subprocess.run([str(a) for a in args], check=True, capture_output=True, text=True, **kw)


def probe(p):
    j = json.loads(sh(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", p]).stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    num, den = map(int, v["r_frame_rate"].split("/"))
    return {"w": v["width"], "h": v["height"], "fps": num / den, "dur": float(j["format"]["duration"]),
            "audio": any(s["codec_type"] == "audio" for s in j["streams"])}


def standin(ep):
    """Stand-in HeyGen render: still image with a slow breathing zoom + edge-tts voice."""
    import edge_tts
    if not STILL.exists():
        sys.exit(f"--standin needs Glenn's studio still at {STILL} (not in the repo; it is only for pipeline tests)")
    text = (ep / "script/heygen_paste.txt").read_text(encoding="utf-8")
    mp3 = ep / "host/_standin_voice.mp3"
    for k in range(4):
        try:
            asyncio.run(edge_tts.Communicate(text, STANDIN_VOICE).save(str(mp3))); break
        except Exception as e:                                   # edge-tts rate limits: retry
            if k == 3:
                raise
            import time; time.sleep(5 * (k + 1))
    d = probe_audio(mp3) + 0.6
    sh(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "30", "-i", STILL, "-i", mp3,
        "-filter_complex", "[0:v]scale=3840:-2,zoompan=z='1.012+0.008*sin(2*PI*on/210)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30,format=yuv420p[v]",
        "-map", "[v]", "-map", "1:a", "-t", f"{d:.2f}", *h264("fast"), "-c:a", "aac", "-b:a", "192k",
        ep / "host/glenn_raw.mp4"])
    print(f"stand-in host video: {d:.1f} s ({STANDIN_VOICE})")


def probe_audio(p):
    return float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).stdout)


def face_rects(raw, info):
    import cv2                                                   # OpenCV 5: YuNet face detector (Haar cascades were removed)
    cap = cv2.VideoCapture(str(raw))
    if not YUNET.exists():                                       # MIT-licensed model from opencv_zoo, fetched once
        import urllib.request
        YUNET.parent.mkdir(parents=True, exist_ok=True); urllib.request.urlretrieve(YUNET_URL, YUNET)
    det = cv2.FaceDetectorYN.create(str(YUNET), "", (info["w"], info["h"]), 0.8)
    boxes = []
    for k in range(7):
        cap.set(cv2.CAP_PROP_POS_MSEC, (k + 0.5) / 7 * info["dur"] * 1000)
        ok, fr = cap.read()
        if not ok:
            continue
        det.setInputSize((fr.shape[1], fr.shape[0]))
        _, f = det.detect(fr)
        if f is not None and len(f):
            b = max(f, key=lambda r: r[2] * r[3])
            boxes.append([float(b[0]), float(b[1]), float(b[2]), float(b[3])])
    cap.release()
    W, H = info["w"], info["h"]
    if not boxes:                                                # fallback: framing measured on the studio still
        return {"box": [0, 0, W, H], "end": None, "face": None}
    x, y, w, h = (statistics.median(b[i] for b in boxes) for i in range(4))
    cx = x + w / 2

    def rect(scale, head_room):
        cw = min(W, w * scale); ch = cw * 9 / 16
        top = max(0, y - head_room * h); left = min(max(0, cx - cw / 2), W - cw)
        if top + ch > H:
            top = H - ch
        return [round(left), round(top), round(cw / 2) * 2, round(ch / 2) * 2]
    return {"box": rect(6.2, 0.9), "end": rect(6.2, 0.9), "face": [round(x), round(y), round(w), round(h)]}   # head + shoulders + chest (owner 4 Nov)


def vo(raw, out):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(raw), "-af", VO_CHAIN + ",loudnorm=I=-16:TP=-1.5:LRA=8:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(p.stderr[p.stderr.rfind("{"):p.stderr.rfind("}") + 1])
    ln = (f"loudnorm=I=-16:TP=-1.5:LRA=8:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    sh(["ffmpeg", "-v", "error", "-y", "-i", raw, "-vn", "-af", VO_CHAIN + "," + ln, "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", out])
    return float(m["input_i"])


def main():
    ep = Path(sys.argv[1]).resolve(); (ep / "host").mkdir(exist_ok=True)
    if "--standin" in sys.argv:
        standin(ep)
    raw = ep / "host/glenn_raw.mp4"
    info = probe(raw)
    fps = 25 if abs(info["fps"] - 25) < .5 else 24 if abs(info["fps"] - 24) < .5 else 30
    R = face_rects(raw, info); end = R["end"] or R["box"]
    enc = ["-an", *h264("inter"), "-pix_fmt", "yuv420p", "-g", str(fps * 2)]
    full_vf = f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x050C1A,fps={fps}"
    crop = lambda r, w, h: f"crop={r[2]}:{r[3]}:{r[0]}:{r[1]},scale={w}:{h}:flags=lanczos,unsharp=5:5:0.4,fps={fps}"
    jobs = [["ffmpeg", "-v", "error", "-y", "-i", raw, "-vf", full_vf, *enc, ep / "host/host_full.mp4"],
            ["ffmpeg", "-v", "error", "-y", "-i", raw, "-vf", crop(R["box"], 720, 405), *enc, ep / "host/host_box.mp4"],
            ["ffmpeg", "-v", "error", "-y", "-i", raw, "-vf", crop(end, 896, 504), *enc, ep / "host/host_end.mp4"]]
    with ThreadPoolExecutor(4) as ex:
        futs = [ex.submit(sh, j) for j in jobs] + [ex.submit(vo, raw, ep / "host/vo.wav")]
        lufs_in = [f.result() for f in futs][-1]
    meta = {"raw": "host/glenn_raw.mp4", "raw_w": info["w"], "raw_h": info["h"], "raw_fps": info["fps"], "fps": fps,
            "dur": probe_audio(ep / "host/vo.wav"), "box_rect_src": R["box"], "end_rect_src": end, "face": R["face"],
            "vo_input_lufs": lufs_in, "standin": (ep / "host/_standin_voice.mp3").exists()}
    (ep / "host/host_meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
