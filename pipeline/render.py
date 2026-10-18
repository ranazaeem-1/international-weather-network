"""Render the episode from edl.json + per-paragraph narration + IWN graphics (GWN-style pacing).

Each chapter = narration part, sound break, narration part, ... , tail break.
 - shots under narration: clip sound ducked (music clips in EDL 'muted' are silent)
 - breaks: a sound-on clip at full volume
 - IWN logo watermark tiled on the blurred side bars, lower-third per chapter, short ticker on flagged chapters.

Usage:  python render.py            # full render
        python render.py S02 S03    # re-render only these chapters, then re-join
"""
import json, math, re, shutil, subprocess, sys
from pathlib import Path

EP = Path(__file__).resolve().parents[1]
KIT = EP.parents[1] / "iwn-brand-kit"
WORK = EP / "project/_work"
EDL = json.loads((EP / "project/edl.json").read_text(encoding="utf8"))
MAN = {m["id"]: m for m in json.loads((EP / "audio/narration/manifest.json").read_text(encoding="utf8"))}
MUTED = set(EDL.get("muted", []))
OUT_NAME = "IWN_" + EP.name[11:] + "_v1"   # episode folder = YYYY-MM-DD-topic
FPS = 30
LT_DELAY = 0.3
LT_LEN = 8.0
SUB_LEN = 7.0           # subscribe-cta animation length (6.0 for the old pill)
UNDER_VO = 0.12          # clip sound level under narration
VENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS)]
AENC = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
WATERMARK = EP / "graphics/sidebar_watermark.png"
REUSE_SHOTS = True      # reuse already-cut pieces in _work (set False after changing edl.json shot ranges)



def subscribe_mov():
    """English channel = Independent Weather Network, Spanish = Instant Weather Network (edl "lang": "en" | "es")."""
    lang = EDL.get('lang', 'en')
    p = KIT / f"motion/subscribe-cta-{lang}-transparent.mov"          # bigger CTA with like + bell (make_cta.py, 17 Oct)
    if not p.exists():
        p = KIT / f"motion/subscribe-{lang}-transparent.mov"
    if not p.exists():
        raise SystemExit(f"{p.name} missing: run pipeline/make_subscribe.py")
    return p

def ff(*args, cwd=WORK):
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", *map(str, args)], cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-3000:])


_probe = {}
def probe(path):
    if path not in _probe:
        d = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]))
        _probe[path] = (float(d["format"].get("duration", 0) or 0), any(s["codec_type"] == "audio" for s in d["streams"]))
    return _probe[path]


def is_still(clip):
    return Path(EDL["media"][clip]).suffix.lower() in (".jpg", ".jpeg", ".png")


def render_shot(clip, tin, dur, opts, vol, out, fade=False):
    src = EP / EDL["media"][clip]
    if clip[:3] in MUTED or clip in MUTED:
        vol = 0.0
    crop = ""
    if opts.get("crop"):                # fractions of the frame: [x, y, w, h]
        x, y, w, h = opts["crop"]
        crop = f"crop=iw*{w:.3f}:ih*{h:.3f}:iw*{x:.3f}:ih*{y:.3f},"
    elif opts.get("crop_top"):
        c = opts["crop_top"]
        crop = f"crop=iw:ih*{1 - c:.3f}:0:ih*{c:.3f},"
    afade = f",afade=t=in:d=0.25,afade=t=out:st={max(0, dur - 0.3):.2f}:d=0.3" if fade else ""
    if is_still(clip):
        frames = int(round(dur * FPS))
        vf = (f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=30:3,"
              f"eq=brightness=-0.12:saturation=0.8,loop=loop=-1:size=1,fps={FPS},trim=duration={dur}[bg];"
              f"[0:v]scale=-2:2160,zoompan=z='1+0.10*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
              f"d={frames}:s=hd1080:fps={FPS},scale=-2:1080[fgz];"
              f"[bg][fgz]overlay=(W-w)/2:0,format=yuv420p[v]")
        ff("-loop", "1", "-i", src, "-f", "lavfi", "-t", dur, "-i", "anullsrc=r=48000:cl=stereo",
           "-filter_complex", vf, "-map", "[v]", "-map", "1:a", "-t", dur, *VENC, *AENC, out)
        return
    _, has_audio = probe(src)
    vf = (f"[0:v]{crop}split[a][b];"
          f"[a]scale=480:270:force_original_aspect_ratio=increase,crop=480:270,boxblur=8:3,scale=1920:1080:flags=bilinear,"
          f"eq=brightness=-0.12:saturation=0.8[bg0];"
          f"[bg0][1:v]overlay=0:0:format=auto[bg];"
          f"[b]scale=1920:1080:force_original_aspect_ratio=decrease:flags=lanczos,setsar=1[fg];"
          f"[bg][fg]overlay=(W-w)/2:(H-h)/2,fps={FPS},format=yuv420p[v]")
    args = ["-ss", tin, "-t", dur, "-i", src, "-loop", "1", "-t", dur, "-i", WATERMARK]
    if has_audio:
        amap = ["-map", "0:a:0", "-af", f"aresample=48000,aformat=channel_layouts=stereo,volume={vol}{afade}"]
    else:
        args += ["-f", "lavfi", "-t", dur, "-i", "anullsrc=r=48000:cl=stereo"]
        amap = ["-map", "2:a"]
    ff(*args, "-filter_complex", vf, "-map", "[v]", *amap, "-t", dur, *VENC, *AENC, out)


class Feed:
    """Hands out consecutive pieces of a shot list (shots up to max_shot; 13 s since 18 Oct, was the 8-second rule)."""
    def __init__(self, shots, max_shot=13.0):
        self.shots = shots
        self.max_shot = max_shot
        self.i = 0
        self.pos = {}

    def take(self, need):
        pieces = []
        loop_guard = 0
        while need > 0.1 and loop_guard < 100:
            loop_guard += 1
            idx = self.i % len(self.shots)
            s = self.shots[idx]
            clip, tin, tout = s[0], s[1], s[2]
            opts = s[3] if len(s) > 3 else {}
            if not is_still(clip):
                tout = min(tout, probe(EP / EDL["media"][clip])[0] - 0.05)
            start = self.pos.get(idx, tin)
            avail = tout - start
            if avail < 1.0:                     # this shot is exhausted: loop it back to tin and advance
                self.pos[idx] = tin
                self.i += 1
                continue
            n_cuts = max(1, math.ceil(need / self.max_shot))
            target = round(need / n_cuts, 2)
            take = round(min(avail, target), 2)
            pieces.append((clip, start, take, opts))
            need = round(need - take, 2)
            start_next = start + take
            if tout - start_next < 1.0:
                self.pos[idx] = tin
            else:
                self.pos[idx] = start_next
            self.i += 1
        return pieces


class Pool:
    """Video-wide footage pool (user, 17 Oct: no clip on screen more than twice unless it is important).

    Each clip keeps one cursor for the whole video, so footage continues where it left off instead of restarting in
    every chapter. Fresh footage from the chapter's preferred clips is used first, then fresh footage from any clip in
    the pool, and only when every clip is used up does a second pass begin (max_uses, or important_uses for clips
    listed in EDL "important"). Never cuts to the same clip twice in a row.
    """
    def __init__(self, order, max_uses=2, important=(), important_uses=3, max_shot=13.0, min_shot=4.0):
        self.order, self.max_shot, self.min_shot = list(order), max_shot, min_shot
        self.limit = {c: (important_uses if c in important else max_uses) for c in self.order}
        self.pos, self.uses, self.last = {}, {c: 1 for c in self.order}, None
        self.shown = {}                                   # clip -> seconds shown, for the report
        self.want = max_shot
        self.must = set(EDL.get("must", []))
        # EDL "reserve": {clip: [chapter ids]} -> that clip may only appear in those chapters (e.g. a Lake Erie
        # waterspout only in the waterspout chapter, user clips in the chapter about their location)
        self.reserve, self.chapter = EDL.get("reserve", {}), None
        self.need = max_shot

    def _cuts(self, need):
        """Number of shots for a gap: aim for ~max_shot-1 s each (12 s), never above ~max_shot+4 (user 18 Oct: 11-13 s shots)."""
        n = max(1, round(need / (self.max_shot - 1)))
        while need / n > self.max_shot + 4:
            n += 1
        return n

    def _short(self, c):
        """Clips shorter than 11 s are shown whole, never trimmed (user 18 Oct)."""
        tin, tout = self._range(c)
        return tout - tin < 11.0

    def _whole_ok(self, c):
        tin, tout = self._range(c)
        left = self.need - (tout - tin)                  # what would remain of the gap after the whole clip
        return self._short(c) and self.pos.get(c, tin) <= tin + 0.01 and (-0.3 <= left <= 0.05 or left >= self.min_shot)

    def _range(self, c):
        tout = probe(EP / EDL["media"][c])[0] - 0.05 if not is_still(c) else 6.0
        return 0.0, tout

    def _avail(self, c):
        tin, tout = self._range(c)
        return tout - self.pos.get(c, tin)

    def _pick(self, prefs, sound):
        ok = lambda c: c != self.last and (c not in self.reserve or self.chapter in self.reserve[c]) and (not sound or c not in MUTED) and self._range(c)[1] - self._range(c)[0] >= self.min_shot
        long_enough = min(self.want, self.max_shot - 2) - 0.05
        # clips the user asked for (EDL "must"): place each one at least once, trimming if it doesn't fit exactly
        must = [c for c in prefs + self.order if c in self.must and not self.shown.get(c) and ok(c) and self._avail(c) >= self.min_shot]
        if must:
            return must[0]
        if self.need < self.max_shot - 2:   # small remainder: a whole short clip that fits beats trimming a long one
            for group in (prefs, self.order):
                fit = [c for c in group if ok(c) and self._whole_ok(c) and self._range(c)[1] >= self.need - 3]
                if fit:
                    return max(fit, key=lambda c: self._range(c)[1])
        for group in (prefs, self.order):
            fresh = [c for c in group if ok(c) and ((not self._short(c) and self._avail(c) >= long_enough) or self._whole_ok(c))]
            if fresh:
                return max(fresh, key=lambda c: (-self.uses[c], self._avail(c))) if group is self.order else fresh[0]
        # a full-length second showing (still within the use limit) beats a short leftover: keeps 11-13 s shots
        full = [c for c in self.order if ok(c) and self.uses[c] < self.limit[c] and
                (self._range(c)[1] >= long_enough or (self._short(c) and self._range(c)[1] <= self.need + 0.3))]
        if full:
            c = ([p for p in prefs if p in full] or sorted(full, key=lambda c: self.uses[c]))[0]
            self.uses[c] += 1
            self.pos[c] = self._range(c)[0]
            return c
        for group in (prefs, self.order):
            fresh = [c for c in group if ok(c) and self._avail(c) >= self.min_shot]
            if fresh:
                return max(fresh, key=lambda c: (-self.uses[c], self._avail(c))) if group is self.order else fresh[0]
        if sound:   # natural-sound footage used up: unseen muted footage beats repeating a clip (user: retention first)
            fresh = [c for c in self.order if c != self.last and (c not in self.reserve or self.chapter in self.reserve[c]) and self._avail(c) >= self.min_shot]
            if fresh:
                return max(fresh, key=lambda c: (-self.uses[c], self._avail(c)))
        again = [c for c in self.order if ok(c) and self.uses[c] < self.limit[c]]
        if not again and sound:                           # any clip still under its limit (silent) beats an extra repeat
            again = [c for c in self.order if c != self.last and self.uses[c] < self.limit[c]]
        if not again:
            again = [c for c in self.order if c != self.last]   # pool far too small: allow more repeats rather than fail
        pref_again = [c for c in prefs if c in again]
        c = (pref_again or sorted(again, key=lambda c: self.uses[c]))[0]
        self.uses[c] += 1
        self.pos[c] = self._range(c)[0]
        return c

    def take(self, need, prefs, sound=False):
        pieces = []
        # a gap shorter than min_shot continues the previous shot (same clip, next frames) instead of a new cut
        if need < self.min_shot and self.last and self._avail(self.last) >= need and (not sound or self.last not in MUTED):
            c = self.last
            start = self.pos.get(c, self._range(c)[0])
            self.pos[c] = start + need
            self.shown[c] = self.shown.get(c, 0) + need
            return [(c, start, round(need, 2), {})]
        while need > 0.1:
            self.want = need / self._cuts(need)
            self.need = need
            c = self._pick(prefs, sound)
            tin, tout = self._range(c)
            start = self.pos.get(c, tin)
            if self._short(c) and start <= tin + 0.01 and (need - (tout - tin) <= 0.05 and tout - tin <= need + 0.3):
                take = round(min(tout - tin, need), 2)          # short clip: the whole clip, uncut
            else:
                take = round(min(tout - start, need / self._cuts(need)), 2)
            rem = need - take
            if 0.1 < rem < self.min_shot:                 # never leave a sub-4 s piece for the next cut (user 18 Oct)
                if tout - start >= need:
                    take = round(need, 2)                 # absorb it into this shot
                elif take - (self.min_shot - rem) >= self.min_shot and not self._short(c):
                    take = round(take - (self.min_shot - rem), 2)   # shorten this shot so the next is >= min_shot
            pieces.append((c, start, take, {}))
            self.pos[c] = start + take
            self.shown[c] = self.shown.get(c, 0) + take
            self.last = c
            need = round(need - take, 2)
            if 0 < need < self.min_shot:                       # short leftover: stretch this shot if the clip has footage
                extra = min(need, tout - (start + take))
                if extra > 0:
                    c0, s0, d0, o0 = pieces[-1]
                    pieces[-1] = (c0, s0, round(d0 + extra, 2), o0)
                    self.pos[c] += extra
                    self.shown[c] += extra
                    need = round(need - extra, 2)
            # move prefs on so the next cut comes from a different clip
            prefs = [p for p in prefs if p != c] + [c]
        return self._no_slivers(pieces)

    def _no_slivers(self, pieces):
        """Final pass per gap: no shot under min_shot (user 18 Oct: 'meaningful cuts', min 4 s).
        A fragment is folded into the previous or next shot when that clip has footage left; otherwise the previous long
        shot gives up time so the fragment's clip can run min_shot."""
        ps = [list(p) for p in pieces]
        k = 0
        while k < len(ps):
            c, a, d, o = ps[k]
            if d >= self.min_shot - 0.05 or len(ps) == 1:
                k += 1
                continue
            done = False
            for j in ([k - 1] if k > 0 else []) + ([k + 1] if k + 1 < len(ps) else []):
                cj, aj, dj, oj = ps[j]
                if self._range(cj)[1] - (aj + dj) >= d:           # neighbour can run longer
                    ps[j][2] = round(dj + d, 2)
                    self.pos[cj] = max(self.pos.get(cj, 0), aj + dj + d)
                    self.shown[c] -= d
                    del ps[k]
                    done = True
                    break
            if not done and k > 0:
                cp, ap, dp, op = ps[k - 1]
                give = self.min_shot - d
                if not self._short(cp) and dp - give >= self.min_shot and self._range(c)[1] - a >= self.min_shot:
                    ps[k - 1][2] = round(dp - give, 2)
                    ps[k][2] = round(self.min_shot, 2)
                    self.pos[c] = max(self.pos.get(c, 0), a + self.min_shot)
                    done = True
            k += 1 if done is False or (k < len(ps) and ps[k][2] >= self.min_shot - 0.05) else 0
        return [tuple(p) for p in ps]



_PLANS = None


def _plan_all():
    """Plans every chapter once, in order, so the shared Pool advances deterministically (build_capcut calls twice)."""
    global _PLANS
    crops = dict(EDL.get("crops", {}))
    for ch in EDL["chapters"]:
        for s in ch["shots"] + ch["breaks"]:
            if len(s) > 3:
                crops[s[0]] = s[3]
    pool = Pool(EDL["pool"], EDL.get("max_uses", 2), set(EDL.get("important", [])), max_shot=EDL.get("max_shot", 13.0))
    _PLANS = {}
    for ch in EDL["chapters"]:
        pool.chapter = ch["id"]
        shots = [s[0] for s in ch["shots"]]
        breaks = [s[0] for s in ch["breaks"]]
        def take(need, sound):
            return [(c, a, d, crops.get(c, {})) for c, a, d, _ in pool.take(need, breaks if sound else shots, sound)]
        if ch.get("clips_only"):
            _PLANS[ch["id"]] = (round(ch["tail"], 2), [("break", 0.0, ch["tail"], None, take(ch["tail"], True))])
            continue
        parts = MAN[ch["id"]]["parts"]
        items, t = [], 0.0
        lead = EDL["lead_in"]
        # the lead-in is planned together with the first narration part and split inside one continuous shot,
        # so it never becomes its own 0.4 s cut (user 18 Oct: no cuts under 4 s)
        both = take(lead + parts[0]["duration"], False)
        c0, s0, d0, o0 = both[0]
        lead_pieces, first_vo = [(c0, s0, lead, o0)], [(c0, round(s0 + lead, 3), round(d0 - lead, 2), o0)] + both[1:]
        items.append(("lead", t, lead, None, lead_pieces)); t += lead
        for k, p in enumerate(parts):
            items.append(("vo", t, p["duration"], p["id"], first_vo if k == 0 else take(p["duration"], False))); t += p["duration"]
            gap = EDL["break_len"] if k < len(parts) - 1 else ch["tail"]
            items.append(("break", t, gap, None, take(gap, True))); t += gap
        _PLANS[ch["id"]] = (round(t, 2), items)
    over = {c: u for c, u in pool.uses.items() if u > 1}
    print(f"pool: {len(pool.shown)} of {len(pool.order)} clips shown; second passes: {over or 'none'}", flush=True)


def plan_chapter(ch):
    """Returns (length, items) where items = [(kind, start, dur, part_id|None, pieces)]."""
    if EDL.get("pool"):
        if _PLANS is None:
            _plan_all()
        return _PLANS[ch["id"]]
    if ch.get("clips_only"):            # cold open: real clips with their own sound, no narration
        return round(ch["tail"], 2), [("break", 0.0, ch["tail"], None, Feed(ch["breaks"]).take(ch["tail"]))]
    parts = MAN[ch["id"]]["parts"]
    shots, breaks = Feed(ch["shots"]), Feed(ch["breaks"])
    items, t = [], 0.0
    lead = EDL["lead_in"]
    first = shots.take(lead)
    items.append(("lead", t, lead, None, first)); t += lead
    for k, p in enumerate(parts):
        items.append(("vo", t, p["duration"], p["id"], shots.take(p["duration"]))); t += p["duration"]
        gap = EDL["break_len"] if k < len(parts) - 1 else ch["tail"]
        items.append(("break", t, gap, None, breaks.take(gap))); t += gap
    return round(t, 2), items


def render_chapter(ch):
    cid = ch["id"]
    length, items = plan_chapter(ch)
    names, n = [], 0
    for kind, _, _, _, pieces in items:
        for clip, tin, take, opts in pieces:
            out = WORK / f"{cid}_{n:02d}_{kind}_{clip}.mp4"
            if REUSE_SHOTS and out.exists() and out.stat().st_size > 0:
                names.append(out.name); n += 1
                continue
            render_shot(clip, tin, take, opts, 1.0 if kind == "break" else UNDER_VO, out.name, fade=(kind == "break"))
            names.append(out.name); n += 1
    lst = WORK / f"{cid}_list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in names), encoding="utf8")

    inputs = ["-f", "concat", "-safe", "0", "-i", lst.name]
    vo = [(start, pid) for kind, start, _, pid, _ in items if kind == "vo"]
    for _, pid in vo:
        inputs += ["-i", EP / f"audio/narration/{pid}.mp3"]
    idx = 1 + len(vo)
    fc, vlast = [], "0:v"
    if ch.get("lower_third"):
        inputs += ["-itsoffset", LT_DELAY, "-i", EP / f"graphics/lt_{ch['lower_third']}.mov"]
        fc.append(f"[{vlast}][{idx}:v]overlay=eof_action=pass:format=auto[vlt]")
        vlast, idx = "vlt", idx + 1
    sub_at = ch.get("subscribe_at")
    if sub_at is not None:
        inputs += ["-itsoffset", sub_at, "-i", subscribe_mov()]
        fc.append(f"[{vlast}][{idx}:v]overlay=eof_action=pass:format=auto[vsub]")
        vlast, idx = "vsub", idx + 1
    if ch.get("ticker"):
        t1 = LT_DELAY + LT_LEN + 0.6
        if sub_at is not None:
            t1 = max(t1, sub_at + SUB_LEN + 0.4)
        t2 = min(length - 0.4, t1 + EDL.get("ticker_len", 14))
        inputs += ["-stream_loop", "-1", "-i", EP / "graphics/ticker.mov",
                   "-stream_loop", "-1", "-i", EP / "graphics/ticker_text.mov"]
        fade = f"fade=t=in:st={t1:.2f}:d=0.4:alpha=1,fade=t=out:st={t2 - 0.4:.2f}:d=0.4:alpha=1"
        fc += [f"[{idx}:v]{fade}[tk]", f"[{idx + 1}:v]{fade}[tt]",
               f"[{vlast}][tk]overlay=shortest=1:format=auto[vtk0]",
               "[vtk0][tt]overlay=x=490:y=948:shortest=1:format=auto[vtk]"]
        vlast, idx = "vtk", idx + 2
    fc.append(f"[{vlast}]format=yuv420p[vout]")
    # Audio is mixed in its own pass: mixing it inside the heavy video graph made ffmpeg drop later narration parts.
    ain = ["-f", "concat", "-safe", "0", "-i", lst.name]
    afc, labels = [], ["[0:a]"]
    for j, (start, pid) in enumerate(vo):
        ain += ["-i", EP / f"audio/narration/{pid}.mp3"]
        ms = int(start * 1000)
        afc.append(f"[{j + 1}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[vo{j}]")
        labels.append(f"[vo{j}]")
    afc.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=first[aout]")
    mix = WORK / f"chapter_{cid}_mix.wav"
    ff(*ain, "-filter_complex", ";".join(afc), "-map", "[aout]", "-t", length, "-c:a", "pcm_s16le", mix.name)
    # drop the narration inputs from the video pass (keep concat + graphics), renumbering graphic inputs
    vin = inputs[:6] + inputs[6 + 2 * len(vo):]
    vfc = ";".join(fc)
    for j in range(len(vo) + 1, idx + 1):
        vfc = vfc.replace(f"[{j}:v]", f"[{j - len(vo)}:v]")
    out = WORK / f"chapter_{cid}.mp4"
    ff(*vin, "-i", mix.name, "-filter_complex", vfc, "-map", "[vout]", "-map", f"{idx - len(vo)}:a",
       "-t", length, *VENC, *AENC, out.name)
    return out.name, length, vo


def srt_time(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}".replace(".", ",")


def parse_srt_time(s):
    h, m, rest = s.split(":")
    sec, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


def build_srt(vo_abs):
    out, n, prev_end = [], 1, 0.0
    for start, pid in vo_abs:
        srt = (EP / f"audio/narration/{pid}.srt").read_text(encoding="utf8")
        for block in srt.strip().split("\n\n"):
            lines = block.strip().split("\n")
            if len(lines) < 3:
                continue
            t0, t1 = [parse_srt_time(x.strip()) + start for x in lines[1].split("-->")]
            t0 = max(t0, prev_end)
            prev_end = t1
            out.append(f"{n}\n{srt_time(t0)} --> {srt_time(t1)}\n" + "\n".join(lines[2:]) + "\n")
            n += 1
    return "\n".join(out)


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    chapters, vo_abs, plan, t = [], [], {}, 0.0
    for ch in EDL["chapters"]:
        if not only or ch["id"] in only:
            name, length, vo = render_chapter(ch)
            print(f"rendered {ch['id']} {length:.1f}s", flush=True)
        else:
            length, items = plan_chapter(ch)
            name, vo = f"chapter_{ch['id']}.mp4", [(s, pid) for k, s, _, pid, _ in items if k == "vo"]
        chapters.append(name)
        vo_abs += [(t + s, pid) for s, pid in vo]
        plan[ch["id"]] = {"start": round(t, 2), "length": length}
        t += length
    (WORK / "chapters.txt").write_text("".join(f"file '{c}'\n" for c in chapters), encoding="utf8")
    ff("-f", "concat", "-safe", "0", "-i", "chapters.txt", "-c", "copy", "joined.mp4")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(WORK / "joined.mp4"), "-af", "loudnorm=I=-14:TP=-2:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    meas = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-2:LRA=11:measured_I={meas['input_i']}:measured_TP={meas['input_tp']}:"
          f"measured_LRA={meas['input_lra']}:measured_thresh={meas['input_thresh']}:offset={meas['target_offset']}:linear=true")
    exp = EP / "exports"
    exp.mkdir(exist_ok=True)
    ff("-i", "joined.mp4", "-map", "0:v", "-map", "0:a", "-c:v", "copy", "-af", ln, *AENC, "-movflags", "+faststart", exp / f"{OUT_NAME}.mp4")
    (exp / f"{OUT_NAME}.srt").write_text(build_srt(vo_abs), encoding="utf8")
    (WORK / "timeline.json").write_text(json.dumps(plan, indent=2), encoding="utf8")
    print(f"done: {t:.1f}s ({t / 60:.2f} min) -> exports/{OUT_NAME}.mp4")


if __name__ == "__main__":
    main()
