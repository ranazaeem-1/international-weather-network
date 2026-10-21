"""Build an editable CapCut draft from edl.json + narration + IWN graphics (timing from render.plan_chapter).

Nothing is re-encoded. Tracks, bottom to top:
  bg       : one still, graphics/background.png (dark IWN frame) for the whole video - shows beside vertical clips
  main     : the ORIGINAL clips, cut as planned; logo/caption crops are CapCut crop settings on the clip, and CapCut fits
             the (cropped) picture inside the 1920x1080 canvas. Volume 0.12 under narration, 1.0 in breaks, 0 if muted.
  watermark: the tiled iwn pattern (graphics/sidebar_watermark.png, normal strength) over every HORIZONTAL clip (user,
             21 Oct; vertical clips carry the same tile in their blurred side bars). "h_watermark": "corner" in edl.json
             brings back the single top-right logo (graphics/corner_watermark.png)
  cards    : the intro title card right after the cold open (graphics/intro.mov, make_intro.py; its red wipe plays over
             the start of S01) and the animated info cards (graphics/cards/<id>.mp4, make_cards.py), each once, under
             the narration of the chapter named in project/cards.py, faded in/out with alpha keyframes (21 Oct)
  lt       : per-chapter lower-third = intro clip + still + outro clip
  subscribe: subscribe animation
  ticker   : headline ticker strip (1920x192) after the subscribe CTA, then the CTA ticker (chapter "cta": True) at the end
  vo       : narration, one segment per paragraph
Captions are written next to the draft as an SRT for upload (not burned in).

Blur look ("framing": "blur", the default): only clips that do NOT fill 16:9 (vertical/square phone video) are re-encoded
with blurred side bars by frame_all.py; 16:9 clips go in as originals with CapCut crops (21 Oct: framing was ~3x slower
than real time per clip and the bars were invisible on 16:9 footage anyway).

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
# Vertical clips always use ffmpeg-framed copies with blurred, darkened side bars + iwn tile (user, 21 Oct: CapCut's own
# canvas blur was tested and rejected as "not acceptable").
LT_IN, LT_OUT_AT = 0.5, 7.4            # must match build_graphics.py
TK_Y0, TK_H = 880, 192
WM_W, WM_OPACITY, WM_MARGIN = 160, 0.9, (64, 44)   # corner logo: width px, opacity, (right, top) margin


H_WATERMARK = "pattern"   # user 21 Oct: horizontal clips get the tiled iwn pattern (graphics/sidebar_watermark.png, the same
                          # tile as the vertical clips' side bars, normal strength) as a CapCut overlay - no re-encode.
                          # Set edl.json "h_watermark": "corner" for the older single top-right logo.


def h_watermark(G):
    """Overlay image put over every horizontal clip: the tiled iwn pattern (default) or the corner logo."""
    if R.EDL.get("h_watermark", H_WATERMARK) == "corner":
        return corner_watermark(G)
    p = G / "sidebar_watermark.png"
    if not p.exists():
        raise SystemExit("graphics/sidebar_watermark.png missing: run make_watermark.py <episode>/graphics first")
    return p


def corner_watermark(G):
    """graphics/corner_watermark.png: the iwn logo in the top-right corner of a transparent 1920x1080 frame (EN and ES)."""
    out = G / "corner_watermark.png"
    if out.exists():
        return out
    from PIL import Image
    logo = Image.open(R.KIT / "logo-white-transparent.png").convert("RGBA")   # same lowercase iwn for EN and ES (20 Oct)
    logo = logo.crop(logo.getbbox())
    logo = logo.resize((WM_W, round(logo.height * WM_W / logo.width)), Image.LANCZOS)
    logo.putalpha(logo.getchannel("A").point(lambda a: int(a * WM_OPACITY)))
    from PIL import ImageFilter
    xy = (1920 - WM_MARGIN[0] - logo.width, WM_MARGIN[1])
    shadow = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))     # soft dark halo so the white logo reads on bright skies
    a = Image.new("L", (1920, 1080), 0)
    a.paste(logo.getchannel("A"), xy)
    shadow.putalpha(a.filter(ImageFilter.GaussianBlur(6)).point(lambda v: min(255, int(v * 1.6))))
    canvas = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    canvas.alpha_composite(shadow)
    canvas.alpha_composite(logo, xy)
    canvas.save(out)
    return out


H_MIN = 1.7   # (cropped) width/height from which a clip fills the 16:9 frame: used as-is, no blurred side bars, corner logo
_dims = {}
def is_horizontal(clip, opts):
    """True when the (cropped) clip fills the 16:9 frame, i.e. it has no blurred side bars carrying the logo tile."""
    if R.is_still(clip):
        return False
    src = R.EP / R.EDL["media"][clip]
    if src not in _dims:
        import json, subprocess
        d = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_streams", "-of", "json", str(src)]))
        st = d["streams"][0]
        w, h = int(st["width"]), int(st["height"])
        rot = abs(int(st.get("tags", {}).get("rotate", 0) or 0))
        for sd in st.get("side_data_list", []) or []:
            rot = abs(int(sd.get("rotation", rot) or 0))
        _dims[src] = (h, w) if rot in (90, 270) else (w, h)
    w, h = _dims[src]
    if opts.get("crop"):
        w, h = w * opts["crop"][2], h * opts["crop"][3]
    elif opts.get("crop_top"):
        h = h * (1 - opts["crop_top"])
    return w / h >= H_MIN


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
    # Spanish versions reuse the English framed copies and logo (user 20 Oct: no separate logo framing for ES; translate
    # the narration, shuffle the clips, done). EDL "framed_lang" can still force a separate _framed_<lang> folder.
    lang = R.EDL.get("framed_lang", "en")
    out = src.parent / ("_framed" if lang == "en" else f"_framed_{lang}") / f"{src.stem}{key}_s{lo}-{hi}.mp4"
    if not (out.exists() and out.stat().st_size > 0) and out.parent.exists():
        # reuse any existing copy of this clip + crop whose span covers the one needed (saves re-encoding)
        import re
        for p in out.parent.glob(f"{src.stem}{key}_s*-*.mp4"):
            m = re.fullmatch(re.escape(src.stem + key) + r"_s(\d+)-(\d+)\.mp4", p.name)
            if m and int(m[1]) <= lo + 2 and int(m[2]) >= hi - 3 and p.stat().st_size > 0:   # spans carry 2/3 s of padding
                return p, int(m[1])
    if not (out.exists() and out.stat().st_size > 0):
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_suffix(".part.mp4")           # never leave a half-written file under the final name
        R.render_shot(clip, lo, hi - lo, opts, 1.0, str(tmp))
        tmp.replace(out)
    return out, lo


# ---- intro + cards (user, 21 Oct 2026) ----------------------------------------------------------------------------
CARD_FADE = 0.3
CARD_EARLIEST = R.LT_DELAY + R.LT_LEN + 0.3      # after the chapter's lower-third


def card_schedule():
    """[(absolute start, seconds, mp4 path, card id, chapter)] for every card in project/cards.py.

    Each card goes under the narration of its chapter: at its "at" (seconds from the chapter start) when given, else the
    first spot after the lower-third where it fits inside one narration part and covers none of the user's must-show
    clips. Never in the cold open, never twice, never overlapping another card."""
    import iwn_gfx
    _, cards = iwn_gfx.load_config(R.EP / "project")
    if not cards:
        return []
    starts, t = {}, 0.0
    for ch in R.EDL["chapters"]:
        length, items = R.plan_chapter(ch)
        starts[ch["id"]] = (t, length, items, ch)
        t += length
    must = set(R.EDL.get("must", []))
    out, seen, busy = [], set(), {}
    for c in cards:
        cid, chap = c["id"], c.get("chapter")
        if cid in seen:
            raise SystemExit(f"card {cid}: listed twice in cards.py (no repeats)")
        seen.add(cid)
        if chap not in starts or starts[chap][3].get("clips_only"):
            raise SystemExit(f"card {cid}: chapter {chap!r} is not a narration chapter of this edit (never the cold open)")
        path = R.EP / f"graphics/cards/{cid}.mp4"
        if not path.exists():
            raise SystemExit(f"graphics/cards/{cid}.mp4 missing: run make_cards.py")
        t0, length, items, _ = starts[chap]
        sec = max(6.0, min(8.0, float(c.get("seconds", 7.0))))
        vos = [(st, d, pieces) for kind, st, d, _, pieces in items if kind == "vo"]

        def clash(a, b):
            if any(not (b <= x0 or a >= x1) for x0, x1 in busy.get(chap, [])):
                return True
            for st, d, pieces in vos:                         # must-show user clips stay visible
                at = st
                for clip, _, take, _ in pieces:
                    if clip in must and not (b <= at or a >= at + take):
                        return True
                    at += take
            return False

        at = None
        if c.get("at") is not None:
            want = float(c["at"])
            ok = [(st, d) for st, d, _ in vos if st - 0.05 <= want and want + sec <= st + d + 0.5]
            if ok:
                at = want
            else:
                print(f"card {cid}: at={want} is not inside one narration part of {chap}; placing it automatically")
        if at is None:
            for lo in (CARD_EARLIEST, 0.5):                  # after the lower-third if the paragraph is long enough
                for st, d, _ in vos:
                    a = max(st + 0.3, lo)
                    while a + sec <= st + d + 0.01 and at is None:
                        if not clash(a, a + sec):
                            at = round(a, 2)
                        a += 0.5
                    if at is not None:
                        break
                if at is not None:
                    break
        if at is None:                                    # narration parts too short: shorten to the longest part
            st, d, _ = max(vos, key=lambda v: v[1])
            if d < 4.5:
                raise SystemExit(f"card {cid}: no narration part in {chap} is long enough for a card")
            at, sec = round(st + 0.3, 2), round(min(sec, d - 0.4), 2)
            print(f"card {cid}: shortened to {sec:.1f} s to stay under the narration of {chap}")
        busy.setdefault(chap, []).append((at, at + sec))
        out.append((t0 + at, sec, path, cid, chap))
    return out


# ---- draft -------------------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default=R.OUT_NAME + "_capcut")
    ap.add_argument("--drafts-dir", default=os.path.join(os.environ.get("LOCALAPPDATA", ""), "CapCut", "User Data", "Projects", "com.lveditor.draft"))
    a = ap.parse_args()
    R.WORK.mkdir(parents=True, exist_ok=True)
    G = R.EP / "graphics"
    wm = None

    script = cc.DraftFolder(a.drafts_dir).create_draft(a.name, 1920, 1080, fps=R.FPS, allow_replace=True)
    for i, name in enumerate(["bg", "main", "watermark", "source_tag", "cards", "lt", "subscribe", "ticker"]):
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
        for kind, start, dur, pid, pieces in items:
            at = t0 + start
            if kind == "intro":                              # intro title card; its wipe overlaps the start of S01
                if not R.INTRO_MOV.exists():
                    raise SystemExit("graphics/intro.mov missing: run make_intro.py (or set \"intro\": null in edl.json)")
                im = mat(R.INTRO_MOV)
                d = min(im.duration, us(dur + float(R.EDL["intro"].get("overlap", 0.45))))
                script.add_segment(cc.VideoSegment(im, cc.Timerange(us(at), d), source_timerange=cc.Timerange(0, d)), "cards")
                print(f"intro   at {at:6.1f}s", flush=True)
                continue
            for clip, tin, take, opts in pieces:
                horiz = is_horizontal(clip, opts)
                if STATIC or horiz:                          # 16:9 clips fill the frame: original file + CapCut crop, no re-encode (21 Oct)
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
                if horiz:                                    # iwn pattern on horizontal footage (user, 21 Oct)
                    wm = wm or mat(h_watermark(G))
                    script.add_segment(cc.VideoSegment(wm, cc.Timerange(us(at), take_us), source_timerange=cc.Timerange(0, take_us)), "watermark")
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

    for at, sec, path, cid, chap in card_schedule():
        m = mat(path)
        d = min(us(sec), m.duration)
        seg = cc.VideoSegment(m, cc.Timerange(us(at), d), source_timerange=cc.Timerange(0, d))
        for off, v in ((0, 0.0), (us(CARD_FADE), 1.0), (d - us(CARD_FADE), 1.0), (d, 0.0)):
            seg.add_keyframe(cc.KeyframeProperty.alpha, off, v)
        script.add_segment(seg, "cards")
        print(f"card    {cid:<16} {chap}  at {int(at // 60)}:{at % 60:04.1f}  {sec:.1f}s", flush=True)

    bg = mat(G / "background.png")          # under everything: fills any thin bars beside not-quite-16:9 clips
    script.add_segment(cc.VideoSegment(bg, cc.Timerange(0, us(t0)), source_timerange=cc.Timerange(0, us(t0))), "bg")
    script.save()
    exp = R.EP / "exports"
    exp.mkdir(exist_ok=True)
    (exp / f"{a.name}.srt").write_text(R.build_srt(vo_abs), encoding="utf8")
    print(f"draft '{a.name}': {t0:.1f}s ({t0 / 60:.2f} min), {n} clip segments, {len(vo_abs)} narration parts -> {a.drafts_dir}")


if __name__ == "__main__":
    main()
