"""Build an editable CapCut draft from edl.json + narration + IWN graphics (timing from render.plan_chapter).

Nothing is re-encoded. Tracks, bottom to top:
  bg       : one still, graphics/background.png (dark IWN frame) for the whole video - shows beside vertical clips
  main     : the ORIGINAL clips, cut as planned; logo/caption crops are CapCut crop settings on the clip, and CapCut fits
             the (cropped) picture inside the 1920x1080 canvas. Volume 0.12 under narration, 1.0 in breaks, 0 if muted.
  lt       : per-chapter lower-third = intro clip + still + outro clip
  subscribe: subscribe animation
  ticker   : headline ticker strip (1920x192) after the subscribe CTA, then the CTA ticker (chapter "cta": True) at the end
  vo       : narration, one segment per paragraph
Captions are written next to the draft as an SRT for upload (not burned in).

Old look (each clip re-encoded with blurred, moving side bars): set "framing": "blur" in edl.json and run frame_all.py first.

Usage:  python build_capcut.py [--name IWN_draft_name] [--drafts-dir DIR]
"""
import argparse, os, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import pycapcut as cc
import render as R

SEC = 1_000_000
us = lambda s: int(round(s * SEC))
STATIC = R.EDL.get("framing", "blur") == "static"
LT_IN, LT_OUT_AT = 0.5, 7.4            # must match build_graphics.py
TK_Y0, TK_H = 880, 192


def crop_key(opts):
    if opts.get("crop"):
        return "_c" + "-".join(f"{v:.3f}" for v in opts["crop"])
    if opts.get("crop_top") or opts.get("crop_bottom"):
        return f"_t{opts.get('crop_top', 0):.3f}b{opts.get('crop_bottom', 0):.3f}"
    return ""


def crop_settings(opts):
    """edl crop -> CapCut crop (corner coordinates as fractions of the source frame)."""
    if opts.get("crop"):
        x, y, w, h = opts["crop"]
    elif opts.get("crop_top") or opts.get("crop_bottom"):
        x, y, w, h = 0.0, opts.get("crop_top", 0), 1.0, 1.0 - opts.get("crop_top", 0) - opts.get("crop_bottom", 0)
    else:
        return cc.CropSettings()
    return cc.CropSettings(upper_left_x=x, upper_left_y=y, upper_right_x=x + w, upper_right_y=y,
                           lower_left_x=x, lower_left_y=y + h, lower_right_x=x + w, lower_right_y=y + h)


# ---- old look: re-encoded copies with blurred side bars (only used when edl "framing" is "blur") -------------------
_spans = None
def spans():
    """(clip, crop key) -> (first second used, last second used) over the whole edit, padded by 2 s."""
    global _spans
    if _spans is None:
        sp = {}                                  # built locally, published once: frame_all.py calls this from several threads
        for ch in R.EDL["chapters"]:
            for _, _, _, _, pieces in R.plan_chapter(ch)[1]:
                for clip, tin, take, opts in pieces:
                    k = (clip, crop_key(opts))
                    lo, hi = sp.get(k, (tin, tin + take))
                    sp[k] = (min(lo, tin), max(hi, tin + take))
        _spans = {k: (max(0, int(lo) - 2), int(hi) + 3) for k, (lo, hi) in sp.items()}
    return _spans


def framed(clip, opts):
    """1920x1080 framed copy of the part of a clip this edit uses. Returns (path, offset of the copy inside the source)."""
    src = R.EP / R.EDL["media"][clip]
    key = crop_key(opts)
    if R.is_still(clip):
        lo, hi = 0, 20
    else:
        lo, hi = spans()[(clip, key)]
        hi = min(hi, int(R.probe(src)[0]))
    # the side-bar watermark is baked in and differs by language (ES: capital IWN), so ES copies get their own folder
    lang = R.EDL.get("lang", "en")
    out = src.parent / ("_framed" if lang == "en" else f"_framed_{lang}") / f"{src.stem}{key}_s{lo}-{hi}.mp4"
    if not (out.exists() and out.stat().st_size > 0):
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_suffix(".part.mp4")           # never leave a half-written file under the final name
        R.render_shot(clip, lo, hi - lo, opts, 1.0, str(tmp))
        tmp.replace(out)
    return out, lo


# ---- draft -------------------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default=R.OUT_NAME + "_capcut")
    ap.add_argument("--drafts-dir", default=os.path.join(os.environ.get("LOCALAPPDATA", ""), "CapCut", "User Data", "Projects", "com.lveditor.draft"))
    a = ap.parse_args()
    R.WORK.mkdir(parents=True, exist_ok=True)
    G = R.EP / "graphics"

    script = cc.DraftFolder(a.drafts_dir).create_draft(a.name, 1920, 1080, fps=R.FPS, allow_replace=True)
    for i, name in enumerate((["bg"] if STATIC else []) + ["main", "source_tag", "lt", "subscribe", "ticker"]):
        script.add_track(cc.TrackType.video, name, relative_index=i)
    script.add_track(cc.TrackType.audio, "vo")

    mats = {}
    def mat(path, opts=None):
        key = (str(path), crop_key(opts or {}))
        if key not in mats:
            mats[key] = cc.VideoMaterial(str(path), crop_settings=crop_settings(opts or {}))
        return mats[key]

    ticker_len = R.EDL.get("ticker_len", 14)
    has_ticker = any(ch.get("ticker") for ch in R.EDL["chapters"])
    tk = mat(G / "ticker_strip.mov") if has_ticker and (G / "ticker_strip.mov").exists() else None
    tk_full = mat(G / "ticker_full.mov") if has_ticker and tk is None else None          # graphics from the old builder
    tk_pos = cc.ClipSettings(transform_y=-((TK_Y0 + TK_H / 2) - 540) / 540)              # strip centre, in half-canvas heights
    sub = mat(R.subscribe_mov())
    cta_len = R.EDL.get("cta_ticker_len", 12)
    cta = mat(G / "cta_ticker_strip.mov") if any(ch.get("cta") for ch in R.EDL["chapters"]) and (G / "cta_ticker_strip.mov").exists() else None
    t0, vo_abs, n = 0.0, [], 0
    for ch in R.EDL["chapters"]:
        length, items = R.plan_chapter(ch)
        for kind, start, _, pid, pieces in items:
            at = t0 + start
            for clip, tin, take, opts in pieces:
                if STATIC:
                    m = mat(R.EP / R.EDL["media"][clip], opts)
                    if R.is_still(clip):
                        tin = 0.0
                else:
                    fpath, off = framed(clip, opts)
                    m = mat(fpath)
                    tin = min(tin, m.duration / SEC - take) if R.is_still(clip) else max(0.0, tin - off)
                vol = 0.0 if (clip in R.MUTED or clip[:3] in R.MUTED) else (1.0 if kind == "break" else R.UNDER_VO)
                take_us = min(us(take), m.duration - us(tin))
                script.add_segment(cc.VideoSegment(m, cc.Timerange(us(at), take_us),
                                                   source_timerange=cc.Timerange(us(tin), take_us), volume=vol), "main")
                tag_path = G / f"source_tags/src_{clip}.png"
                if tag_path.exists():
                    tag_m = mat(tag_path)
                    tag_dur = min(take, 5.0)
                    lt_id = ch.get("lower_third")
                    rel = at - t0
                    lt_win = [(0, R.LT_DELAY + R.LT_LEN)] + ([(ch["lt_again_at"] - 0.5, ch["lt_again_at"] + R.LT_LEN)] if ch.get("lt_again_at") is not None else [])
                    in_lt_window = (lt_id is not None) and any(a - tag_dur < rel < b for a, b in lt_win)
                    if not in_lt_window and tag_dur >= 2.0:
                        script.add_segment(cc.VideoSegment(tag_m, cc.Timerange(us(at), us(tag_dur)),
                                                           source_timerange=cc.Timerange(0, us(tag_dur))), "source_tag")
                at += take; n += 1
            if kind == "vo":
                am = cc.AudioMaterial(str(R.EP / f"audio/narration/{pid}.mp3"))
                script.add_segment(cc.AudioSegment(am, cc.Timerange(us(t0 + start), am.duration)), "vo")
                vo_abs.append((t0 + start, pid))
        lt_id = ch.get("lower_third")
        lt_again = ch.get("lt_again_at")                                     # headline repeated mid-chapter (17 Oct)
        if lt_id and (G / f"lt_{lt_id}.png").exists():                       # intro clip + still + outro clip
            for p_rel in [R.LT_DELAY] + ([lt_again] if lt_again is not None else []):
                p0 = t0 + p_rel
                for path, at, d in ((G / f"lt_{lt_id}_in.mov", p0, LT_IN), (G / f"lt_{lt_id}.png", p0 + LT_IN, LT_OUT_AT - LT_IN),
                                    (G / f"lt_{lt_id}_out.mov", p0 + LT_OUT_AT, LT_IN)):
                    m = mat(path)
                    d = min(us(d), m.duration)
                    script.add_segment(cc.VideoSegment(m, cc.Timerange(us(at), d), source_timerange=cc.Timerange(0, d)), "lt")
        elif lt_id:                                                          # single 8 s clip from the old builder
            lt = mat(G / f"lt_{lt_id}.mov")
            d = min(lt.duration, us(length - R.LT_DELAY))
            script.add_segment(cc.VideoSegment(lt, cc.Timerange(us(t0 + R.LT_DELAY), d), source_timerange=cc.Timerange(0, d)), "lt")
        subs = ch.get("subscribe_at")
        subs = [] if subs is None else (list(subs) if isinstance(subs, (list, tuple)) else [subs])
        sub_at = subs[0] if subs else None
        for s_at in subs:                                                    # the IWN subscribe/like/bell pill, 1-2 per chapter
            d = min(sub.duration, us(length - s_at))
            script.add_segment(cc.VideoSegment(sub, cc.Timerange(us(t0 + s_at), d), source_timerange=cc.Timerange(0, d), volume=1.0), "subscribe")
        later = sorted(x for x in subs[1:] + ([lt_again] if lt_again is not None else []))
        busy_end = max([R.LT_DELAY + R.LT_LEN] + [s + R.SUB_LEN for s in subs] + ([lt_again + R.LT_LEN] if lt_again is not None else []))
        t2 = None
        if ch.get("ticker") and (tk or tk_full):
            if ch.get("ticker_window"):                                    # explicit window (one-paragraph chapters, 18 Oct)
                t1, t2 = ch["ticker_window"]
                t2 = min(t2, length - 0.4)
            else:
                t1 = R.LT_DELAY + R.LT_LEN + 0.6
                if sub_at is not None:
                    t1 = max(t1, sub_at + R.SUB_LEN + 0.4)
                nxt = min([x for x in later if x > t1] or [length])
                t2 = min(length - 0.4, t1 + ticker_len, nxt - 0.5)
            if t2 - t1 > 2:
                m = tk or tk_full
                d = min(us(t2 - t1), m.duration)
                script.add_segment(cc.VideoSegment(m, cc.Timerange(us(t0 + t1), d), source_timerange=cc.Timerange(0, d),
                                                   clip_settings=tk_pos if tk else None), "ticker")
        t_free = max(busy_end, t2 or 0) + 0.8
        if ch.get("cta") and cta:                                             # CTA ticker in the chapter's last seconds
            if ch.get("cta_window"):
                c1, c2 = ch["cta_window"]
                c2 = min(c2, length - 0.4)
            else:
                c1 = max(t_free, length - cta_len - 1.0)
                c2 = min(length - 0.4, c1 + cta_len)
            if c2 - c1 > 3:
                d = min(us(c2 - c1), cta.duration)
                script.add_segment(cc.VideoSegment(cta, cc.Timerange(us(t0 + c1), d), source_timerange=cc.Timerange(0, d),
                                                   clip_settings=tk_pos), "ticker")
        print(f"{ch['id']}  {length:6.1f}s", flush=True)
        t0 += length

    if STATIC:
        bg = mat(G / "background.png")
        script.add_segment(cc.VideoSegment(bg, cc.Timerange(0, us(t0)), source_timerange=cc.Timerange(0, us(t0))), "bg")
    script.save()
    exp = R.EP / "exports"
    exp.mkdir(exist_ok=True)
    (exp / f"{a.name}.srt").write_text(R.build_srt(vo_abs), encoding="utf8")
    print(f"draft '{a.name}': {t0:.1f}s ({t0 / 60:.2f} min), {n} clip segments, {len(vo_abs)} narration parts -> {a.drafts_dir}")


if __name__ == "__main__":
    main()
