"""Build an editable CapCut desktop draft from edit/timeline.json (Carver Weather Desk).

compose.py (the ffmpeg MP4) and this builder read the same timeline (docs/timeline-schema.md §2), so the MP4 and the
draft match. Nothing is re-encoded: every item is its own source file, cut at its source in-point and placed with
CapCut transform/scale. Conventions follow the IWN builder the owner already opens in CapCut
(international-weather-network/episodes/2026-10-29-sakurajima-eruption/project/build_capcut.py).

Tracks: one CapCut track per timeline track, with the same name, in the same bottom-to-top order. Video tracks get
relative_index 0, 1, 2 ... in list order. Audio tracks are added after them, with relative_index 0, 1 ... among the
audio tracks. pycapcut sorts the saved track array by render_index, so the vo track lands right after the bottom video
track, as in the IWN drafts ([bg, vo, main, ...]). CapCut groups the tracks by type.
One exception: CapCut's bottom video track is its magnetic main track. When it does not start at 0 or has gaps
(full-host moments with no base footage), CapCut slides its clips to 0 and closes the gaps. In that case an extra
bottom track, "canvas", is added: one black 1920x1080 still for the whole video, like IWN's "bg" track. The timeline's
own bottom track then sits above it and keeps its exact times. The black frame is the same thing the MP4 shows in
those gaps.

Placement (x, y, w, h in canvas pixels, top-left origin) -> CapCut clip settings:
  At scale 1.0, CapCut fits ("contains") every material inside the canvas, so it shows at (mw*f) x (mh*f) with
  f = min(W/mw, H/mh). The IWN drafts prove this both ways: 1280x720 clips at scale 1.0 fill 1920x1080 (scaled up 1.5x),
  and the 1920x192 ticker strip at scale 1.0 stays 1920x192 (f = 1).
      scale_x     = w / (mw * f)              scale_y     = h / (mh * f)
      transform_x = (x + w/2 - W/2) / (W/2)   transform_y = -(y + h/2 - H/2) / (H/2)    (half-canvas units, y up)
  A source rendered at exactly w x h gets one uniform scale, 1/f (536x302 host box: 0.2796). A still drawn into a
  rectangle with a different aspect gets scale_x != scale_y, and its uniform-scale lock is turned off.

Alpha: ProRes 4444 .mov files are plain VideoMaterials, as with IWN's intro.mov. CapCut keeps their alpha.
Volume: each video item gets the timeline volume (default 0 = mute). Stills keep CapCut's default, because they
have no audio. Opacity: ClipSettings.alpha.

What pycapcut 0.0.3 cannot express, and what this builder does instead:
  - Markers: there is no API, and "time_marks" is never written. They are printed, so they can be added by hand
    in CapCut (M key).
  - Audio fades on VIDEO items (nat sound in breaks): pycapcut has fades only for audio segments. They are written as
    linear volume keyframes (0 -> volume over fade_in, volume -> 0 over fade_out), at offsets from the segment start.
    That is the same keyframe mechanism as the IWN card alpha fades.
  - Audio items get native CapCut fades (AudioSegment.add_fade).

Usage:
  python build_capcut.py <episode_dir> [--timeline edit/timeline.json] [--name NAME] [--drafts-dir DIR]
  The default name is the timeline "name". The default drafts dir is CapCut's own drafts folder (production only:
  for tests, always pass --drafts-dir).
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import pycapcut as cc
import pymediainfo
from pycapcut.exceptions import SegmentOverlap

SEC = 1_000_000
DEFAULT_DRAFTS = os.path.join(os.environ.get("LOCALAPPDATA", ""), "CapCut", "User Data", "Projects", "com.lveditor.draft")
CLAMP_QUIET = 0.07      # s: an item running past its file's end by up to ~2 frames is shortened without a warning
UNIFORM_TOL = 1e-4      # relative scale_x/scale_y difference treated as uniform (< 0.2 px on 1920)


def us(s):
    return int(round(float(s) * SEC))


def tc(s):
    return f"{int(s // 60)}:{s % 60:05.2f}"


def fit_factor(mw, mh, W, H):
    """Factor CapCut applies at scale 1.0: the material is fitted (contained) inside the canvas."""
    return min(W / mw, H / mh)


def placement(x, y, w, h, mw, mh, W, H):
    """Pixel rect -> (scale_x, scale_y, transform_x, transform_y) for a mw x mh material on a W x H canvas."""
    f = fit_factor(mw, mh, W, H)
    sx, sy = w / (mw * f), h / (mh * f)
    if abs(sx - sy) <= UNIFORM_TOL * max(sx, sy):
        sx = sy = (sx + sy) / 2
    tx = (x + w / 2 - W / 2) / (W / 2) + 0.0
    ty = -(y + h / 2 - H / 2) / (H / 2) + 0.0          # + 0.0: no "-0.0" in the JSON
    return sx, sy, tx, ty


def next_name(name):
    m = re.search(r"_v(\d+)$", name)
    return f"{name[:m.start()]}_v{int(m[1]) + 1}" if m else f"{name}_v2"


def lock_files(draft_dir):
    """CapCut leaves a .locked file in a draft's folder while the draft is open."""
    if not draft_dir.is_dir():
        return []
    return [p for p in draft_dir.iterdir() if p.name == ".locked" or p.name.endswith(".locked")]


def locked_exit(name, why):
    print(f"\nDraft '{name}' is open in CapCut ({why}), so it can't be replaced.\n"
          f"Close it in CapCut and run again, or build a new copy:  --name {next_name(name)}")
    sys.exit(2)


def black_canvas(path, W, H):
    if not path.exists():
        from PIL import Image
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (W, H), (0, 0, 0)).save(path)
    return path


def main():
    ap = argparse.ArgumentParser(description="edit/timeline.json -> editable CapCut desktop draft")
    ap.add_argument("episode_dir")
    ap.add_argument("--timeline", default="edit/timeline.json", help="relative to episode_dir, or absolute")
    ap.add_argument("--name", help="draft name (default: the timeline's name)")
    ap.add_argument("--drafts-dir", default=DEFAULT_DRAFTS, help="CapCut drafts folder (default: CapCut's own)")
    a = ap.parse_args()

    ep = Path(a.episode_dir).resolve()
    tl_path = Path(a.timeline) if Path(a.timeline).is_absolute() else ep / a.timeline
    if not tl_path.exists() and Path(a.timeline).exists():          # a path relative to the current folder
        tl_path = Path(a.timeline).resolve()
    if not tl_path.exists():
        raise SystemExit(f"timeline not found: {tl_path}")
    tl = json.loads(tl_path.read_text(encoding="utf-8"))
    if tl.get("version", 1) != 1:
        print(f"note: timeline version {tl.get('version')} (this builder knows version 1)")
    W, H = int(tl.get("w", 1920)), int(tl.get("h", 1080))
    fps = tl.get("fps", 30)
    fps = int(fps) if float(fps).is_integer() else float(fps)
    name = a.name or tl.get("name") or ep.name
    drafts = Path(a.drafts_dir)
    if not drafts.is_dir():
        raise SystemExit(f"drafts folder not found: {drafts}")
    draft_dir = drafts / name
    locks = lock_files(draft_dir)                      # check first: no point building a draft we can't write
    if locks:
        locked_exit(name, f"found {locks[0]}")

    root = Path(tl["root"]) if tl.get("root") else ep
    if not root.is_dir():
        print(f"note: timeline root {root} not found; resolving sources against {ep}")
        root = ep
    elif root.resolve() != ep:
        print(f"note: timeline root {root} is not the episode dir {ep}; sources are looked up in the root first")
    tried = []

    def resolve(src):
        p = Path(src)
        for c in ([p] if p.is_absolute() else [root / p, ep / p]):
            if c.exists():
                return c.resolve()
        tried.append(src)
        return None

    warnings, notes = [], []
    vmats, amats, has_audio = {}, {}, {}

    def vmat(p):
        if p not in vmats:
            vmats[p] = cc.VideoMaterial(str(p))
            has_audio[p] = vmats[p].material_type == "video" and bool(pymediainfo.MediaInfo.parse(str(p)).audio_tracks)
        return vmats[p]

    def amat(p):
        if p not in amats:
            try:
                amats[p] = cc.AudioMaterial(str(p))
            except ValueError as e:
                raise SystemExit(f"audio item {p.name}: {e} (audio tracks take audio files such as .wav; put video "
                                 f"files on a video track with a volume)")
        return amats[p]

    def times(item, src_len, still, where):
        """(start_us, dur_us, in_us), shortened if the item runs past the end of its file."""
        start = us(item["start"])
        dur = us(float(item["start"]) + float(item["dur"])) - start      # end rounded once: butt cuts stay exact
        tin = 0 if still else us(item.get("in", 0.0))
        if dur <= 0:
            return None
        if not still and tin + dur > src_len:
            over = (tin + dur - src_len) / SEC
            if tin >= src_len:
                raise SystemExit(f"{where}: in-point {tin / SEC:.3f}s is past the end of the file ({src_len / SEC:.3f}s)")
            dur = src_len - tin
            if over > CLAMP_QUIET:
                warnings.append(f"{where}: runs {over:.3f}s past the end of its file; shortened to {dur / SEC:.3f}s")
        return start, dur, tin

    tracks = tl.get("tracks", [])
    bad = [t.get("name") for t in tracks if t.get("type", "video") not in ("video", "audio")]
    if bad:
        raise SystemExit(f"unsupported track type on {bad} (video and audio only)")
    vtracks = [t for t in tracks if t.get("type", "video") == "video"]
    atracks = [t for t in tracks if t.get("type") == "audio"]
    names = [t["name"] for t in tracks]
    if len(set(names)) != len(names):
        raise SystemExit(f"track names must be unique: {names}")

    # Does the bottom video track need the canvas under it (CapCut's magnetic main track)?
    end_all = max([us(float(i["start"]) + float(i["dur"])) for t in tracks for i in t.get("items", [])] + [us(tl.get("duration", 0))])
    bottom = sorted(vtracks[0].get("items", []), key=lambda i: float(i["start"])) if vtracks else []
    canvas_why = None
    if vtracks and any(t.get("items") for t in vtracks):
        if not bottom:
            canvas_why = f"'{vtracks[0]['name']}' is empty"
        elif us(bottom[0]["start"]) > 0:
            canvas_why = f"'{vtracks[0]['name']}' starts at {float(bottom[0]['start']):.2f}s"
        else:
            gaps = [(us(float(p["start"]) + float(p["dur"])), us(q["start"])) for p, q in zip(bottom, bottom[1:])]
            gaps = [(e, s) for e, s in gaps if s - e > 1]
            if gaps:
                canvas_why = f"'{vtracks[0]['name']}' has {len(gaps)} gap(s), first at {gaps[0][0] / SEC:.2f}s"
    canvas_name = "canvas" if "canvas" not in names else "canvas_bg"

    # Build the whole draft in memory first: a bad timeline must never wipe an existing draft (create_draft replaces it).
    script = cc.ScriptFile(W, H, fps)
    vbase = 1 if canvas_why else 0
    if canvas_why:
        script.add_track(cc.TrackType.video, canvas_name, relative_index=0)
    for i, t in enumerate(vtracks):
        script.add_track(cc.TrackType.video, t["name"], relative_index=vbase + i)
    for j, t in enumerate(atracks):
        script.add_track(cc.TrackType.audio, t["name"], relative_index=j)

    def add(seg, track, where):
        try:
            script.add_segment(seg, track)
        except SegmentOverlap:
            raise SystemExit(f"{where}: overlaps the previous item on track '{track}' (items on one track must not overlap)")

    if canvas_why:
        cm = vmat(black_canvas(ep / "edit" / f"capcut_canvas_{W}x{H}.png", W, H))
        add(cc.VideoSegment(cm, cc.Timerange(0, end_all), source_timerange=cc.Timerange(0, end_all)), canvas_name, "canvas")
        notes.append(f"added bottom track '{canvas_name}' (black still, 0-{end_all / SEC:.2f}s) because {canvas_why}: "
                     f"CapCut's magnetic main track would otherwise move those clips")

    counts, kf_fades = {}, 0
    for t in vtracks:
        items = sorted(t.get("items", []), key=lambda i: float(i["start"]))
        counts[t["name"]] = 0
        for k, it in enumerate(items):
            where = f"{t['name']}[{k}] {it.get('src')}"
            p = resolve(it["src"])
            if p is None:
                continue
            m = vmat(p)
            still = m.material_type == "photo"
            tt = times(it, m.duration, still, where)
            if tt is None:
                warnings.append(f"{where}: zero duration, skipped")
                continue
            start, dur, tin = tt
            x, y = float(it.get("x", 0)), float(it.get("y", 0))
            w, h = float(it.get("w", W)), float(it.get("h", H))
            sx, sy, tx, ty = placement(x, y, w, h, m.width, m.height, W, H)
            vol = 1.0 if still else float(it.get("volume", 0.0))
            seg = cc.VideoSegment(m, cc.Timerange(start, dur), source_timerange=cc.Timerange(tin, dur), volume=vol,
                                  clip_settings=cc.ClipSettings(alpha=float(it.get("opacity", 1.0)), scale_x=sx,
                                                                scale_y=sy, transform_x=tx, transform_y=ty))
            if sx != sy:
                seg.uniform_scale = False
            fi, fo = max(0.0, float(it.get("fade_in", 0) or 0)), max(0.0, float(it.get("fade_out", 0) or 0))
            if (fi or fo) and not still:
                if not has_audio[p]:
                    notes.append(f"{where}: fade_in/fade_out ignored, the file has no audio")
                elif vol > 0:
                    if fi + fo > dur / SEC:                                    # fades longer than the clip: share it
                        fi, fo = fi * (dur / SEC) / (fi + fo), fo * (dur / SEC) / (fi + fo)
                    kf = {}
                    if fi:
                        kf.update({0: 0.0, us(fi): vol})
                    if fo:
                        kf.update({dur - us(fo): vol, dur: 0.0})
                    for off, v in sorted(kf.items()):
                        seg.add_keyframe(cc.KeyframeProperty.volume, off, v)
                    kf_fades += 1
            if vol > 0 and not still and not has_audio[p]:
                notes.append(f"{where}: volume {vol} but the file has no audio")
            add(seg, t["name"], where)
            counts[t["name"]] += 1

    native_fades = 0
    for t in atracks:
        items = sorted(t.get("items", []), key=lambda i: float(i["start"]))
        counts[t["name"]] = 0
        for k, it in enumerate(items):
            where = f"{t['name']}[{k}] {it.get('src')}"
            p = resolve(it["src"])
            if p is None:
                continue
            m = amat(p)
            tt = times(it, m.duration, False, where)
            if tt is None:
                warnings.append(f"{where}: zero duration, skipped")
                continue
            start, dur, tin = tt
            seg = cc.AudioSegment(m, cc.Timerange(start, dur), source_timerange=cc.Timerange(tin, dur),
                                  volume=float(it.get("volume", 1.0)))
            fi, fo = us(max(0.0, float(it.get("fade_in", 0) or 0))), us(max(0.0, float(it.get("fade_out", 0) or 0)))
            if fi or fo:
                if fi + fo > dur:
                    fi, fo = fi * dur // (fi + fo), fo * dur // (fi + fo)
                seg.add_fade(fi, fo)
                native_fades += 1
            add(seg, t["name"], where)
            counts[t["name"]] += 1

    if tried:
        raise SystemExit("missing source files (draft not written):\n  " + "\n  ".join(tried))

    # Write: create_draft makes the folder + draft_meta_info.json (replacing an older build), then save our content.
    if lock_files(draft_dir):
        locked_exit(name, "a .locked file appeared while building")
    try:
        shell = cc.DraftFolder(str(drafts)).create_draft(name, W, H, fps=fps, allow_replace=True)
    except OSError as e:                                # Windows: files still held open by CapCut
        locked_exit(name, f"replacing the old draft failed: {e}")
    script.save_path = shell.save_path
    script.save()

    # Summary
    total = script.duration / SEC
    print(f"draft '{name}' -> {draft_dir}")
    print("tracks, bottom to top:")
    if canvas_why:
        print(f"  video  {canvas_name:<12} 1 item   (added, see notes)")
    for t in vtracks + atracks:
        n = counts.get(t["name"], 0)
        print(f"  {t.get('type', 'video'):<6} {t['name']:<12} {n} item{'s' if n != 1 else ''}")
    n_items = sum(counts.values())
    print(f"{n_items} items, {len(vmats)} video/still materials, {len(amats)} audio materials (one per source file)")
    want = float(tl.get("duration", total))
    print(f"duration {total:.2f}s ({tc(total)}), timeline says {want:.2f}s"
          + ("" if abs(total - want) < 1.5 / float(fps) else "  <-- differs"))
    if native_fades or kf_fades:
        print(f"audio fades: {native_fades} native (audio items), {kf_fades} as volume keyframes (video items)")
    markers = tl.get("markers") or []
    if markers:
        print(f"markers ({len(markers)}): pycapcut can't write CapCut markers; add them by hand (M key):")
        for mk in sorted(markers, key=lambda m: float(m["t"])):
            print(f"  {tc(float(mk['t']))}  {mk.get('label', '')}")
    for n in notes:
        print(f"note: {n}")
    for w in warnings:
        print(f"WARNING: {w}")


if __name__ == "__main__":
    main()
