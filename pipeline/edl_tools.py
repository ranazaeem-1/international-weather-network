"""Helpers for an episode's gen_edl.py: crop shorthands and a builder that writes project/edl.json.

    import edl_tools as E
    CROP  = {"T04": E.TOP(0.12), ...}      # per clip id; fractions of the frame
    MUTED = {"T09", ...}                   # silent everywhere (voice-over, music, unknown sound)
    def chapters(s, ch):
        return [E.cold_open(s, [s("T01", 0, 12), ...]),
                ch("S01", [shots under narration...], [sound breaks...], ticker=True, subscribe_at=22), ...]
    E.build(EP, "notes", chapters, CROP, MUTED, backup=["T01", ...])

Clip ids are the part of the file name before the first underscore (clips/found/T01_Place_slug.mp4 -> T01).
A shot is s(clip, start=0, end=None). Breaks carry the clip's own sound, so muted clips are swapped for a backup clip.
"""
import json, subprocess
from pathlib import Path

TOP = lambda f: {"crop": [0.0, f, 1.0, 1.0 - f]}            # cut the top f of the frame
KEEP_TOP = lambda f: {"crop": [0.0, 0.0, 1.0, f]}           # keep only the top f
band = lambda y, h: {"crop": [0.0, y, 1.0, h]}              # keep rows y .. y+h
box = lambda x, y, w, h: {"crop": [x, y, w, h]}


def cold_open(s, breaks, seconds=20):
    """GWN-style cold open (18 Oct): ~20 s, the 1-2 strongest clips with their real sound/reactions, then narration."""
    return {"id": "S00", "clips_only": True, "tail": seconds, "lower_third": None, "shots": [breaks[0]], "breaks": breaks}


def muted_from_sources(ep: Path, files=("research/sources.csv", "research/user_clips.csv")):
    """Clips to silence (user 18 Oct: mute ONLY music; speech in clips stays audible).
    A clip is muted when its `sound` or `notes` column mentions music / song / soundtrack / beat."""
    import csv, re
    out = set()
    for f in files:
        p = ep / f
        if not p.exists():
            continue
        for row in csv.DictReader(open(p, encoding="utf8")):
            cid = (row.get("clip_id") or "").strip()
            txt = " ".join(str(row.get(k) or "") for k in ("sound", "notes")).lower()
            if cid and cid != "-" and re.search(r"music|song|soundtrack|beat", txt):
                out.add(cid)
    return out


def _plan_overlays(ep, chapters, break_len, sub_len=7.0, lt_len=8.3):
    """Bottom-of-screen schedule per chapter (user, 17 Oct: more subscribe pills, headlines, tickers):
    lower-third 0-8 s -> subscribe pill in the 1st sound break -> headline ticker -> subscribe pill in the 2nd sound
    break -> headline lower-third again -> CTA ticker at the end (placed by build_capcut). Uses the narration manifest."""
    man = ep / "audio/narration/manifest.json"
    if not man.exists():
        return
    parts = {m["id"]: [p["duration"] for p in m["parts"]] for m in json.loads(man.read_text(encoding="utf8"))}
    for c in chapters:
        d = parts.get(c["id"])
        if c.get("clips_only") or not d:
            continue
        b1 = 0.4 + d[0]
        if len(d) == 1:
            # GWN structure (18 Oct): one paragraph, then one long clip break. Lower-third over the narration start,
            # headline ticker over the rest of the narration, subscribe pill at the start of the break, CTA ticker after it.
            length = b1 + c.get("tail", 28)
            s1 = round(b1 + 0.3, 1)
            c["subscribe_at"] = [s1]
            if b1 - 0.3 - (lt_len + 0.7) >= 6:
                c["ticker_window"] = [round(lt_len + 0.7, 1), round(min(b1 - 0.3, lt_len + 0.7 + 24), 1)]
            c1 = s1 + sub_len + 0.5
            if length - 0.4 - c1 >= 6:
                c["cta_window"] = [round(c1, 1), round(min(length - 0.4, c1 + 14), 1)]
            continue
        subs = [round(max(lt_len + 0.3, b1 + 0.3), 1)]
        if len(d) > 2:
            b2 = b1 + break_len + d[1]
            s2 = round(max(b2 + 0.3, subs[0] + sub_len + 6), 1)
            subs.append(s2)
            c["lt_again_at"] = round(s2 + sub_len + 0.6, 1)
        c["subscribe_at"] = subs


def check_archive(archive, used, chapter_ids, event):
    """Archive footage rule (user, 20 Oct 2026, revised): footage from an earlier event is allowed ONLY when the video's
    event has NOT happened yet (event="upcoming": a forecast, an approaching storm, a warning just issued). For events
    that already happened (event="happened") only real footage of that event is used, so any archive clip is refused.
    No on-screen tag. archive = {clip: {"date": "SEP 2026", "chapters": [...optional, default all]}}. The narration must
    never claim archive pictures show the current event."""
    if event not in ("happened", "upcoming"):
        raise SystemExit('event must be "happened" or "upcoming"')
    if archive and event == "happened":
        raise SystemExit("archive footage is only allowed for upcoming / warned events; this event already happened: "
                         "use real footage of it only (" + ", ".join(archive) + ")")
    out = {}
    for clip, a in (archive or {}).items():
        if clip not in used:
            print("archive: skipped", clip, "(not in library)")
            continue
        if not a.get("date"):
            raise SystemExit(f"archive clip {clip}: needs the date of the event it shows")
        chs = list(a.get("chapters") or chapter_ids)
        out[clip] = {"date": str(a["date"]).upper(), "chapters": chs}
    if out:
        print("archive clips (upcoming event):", ", ".join(f"{c} {v['date']}" for c, v in out.items()))
    return out


INTRO_SECONDS, INTRO_OVERLAP = 3.4, 0.45   # must match make_intro.LENGTH / WIPE


def check_cards(ep, chapter_ids):
    """project/cards.py (user, 21 Oct 2026): every card once, in a narration chapter that exists, never in the cold open."""
    p = ep / "project/cards.py"
    if not p.exists():
        print("cards: none (no project/cards.py)")
        return
    import iwn_gfx
    _, cards = iwn_gfx.load_config(ep / "project")
    seen = set()
    for c in cards:
        cid, chap = c.get("id"), c.get("chapter")
        if cid in seen:
            raise SystemExit(f"cards.py: card {cid} listed twice (no repeats)")
        seen.add(cid)
        if chap == chapter_ids[0] or chap == "S00":
            raise SystemExit(f"cards.py: card {cid} is in the cold open ({chap}); cards go under narration only")
        if chap not in chapter_ids:
            raise SystemExit(f"cards.py: card {cid} names chapter {chap}, which is not in the edit")
    where = ", ".join("%s@%s" % (c["id"], c["chapter"]) for c in cards)
    print(f"cards: {len(cards)} ({where})")


def auto_tail(ep, lib_seconds, max_uses, cold_open=20.0, lo=8.0, hi=45.0):
    """No fixed runtime (user, 20 Oct 2026): the clip break after each chapter is sized so the edit uses the footage
    that was actually fetched, without padding by repeats. runtime ~= distinct footage (x1.25 when 2 uses are allowed)."""
    man = json.loads((ep / "audio/narration/manifest.json").read_text(encoding="utf8"))
    narr = sum(m["duration"] for m in man)
    n = sum(1 for m in man if m["duration"] > 0)
    target = lib_seconds * (1.0 if max_uses <= 1 else 1.25)
    tail = max(lo, min(hi, (target - narr - cold_open) / max(1, n)))
    print(f"auto tail: {lib_seconds / 60:.1f} min footage, {narr / 60:.1f} min narration -> {tail:.0f} s breaks, "
          f"runtime ~{(narr + cold_open + n * tail) / 60:.1f} min")
    return round(tail, 1)


def build(ep: Path, notes, chapters_fn, crop, muted, backup=(), clips_dir=None, break_len=12, tail=28, pattern="*.mp4", lang="en",
          pool=True, important=(), max_uses=2, ticker_len=22, cta_ticker_len=12, every_chapter=True, auto_overlays=True, max_shot=13.0, reactions=(),
          archive=None, event="happened", intro=True):
    """pool=True (default since 17 Oct): chapter shot/break lists are preferences; render.Pool hands out footage from the
    whole library so each clip continues where it left off and nothing repeats until the library is used up (max_uses,
    or 3 for clips in `important`). every_chapter=True puts the headline ticker and the CTA ticker in every chapter.
    intro=True (21 Oct 2026): a ~3.4 s intro title card (make_intro.py) after the cold open; cards in project/cards.py
    (make_cards.py) are checked here and placed by build_capcut.py."""
    lib = Path(clips_dir) if clips_dir else ep / "clips/found"
    files = {p.name.split("_")[0]: p for p in sorted(lib.glob(pattern))}
    D = {}

    def dur(c):
        if c not in D:
            D[c] = round(float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                                         str(files[c])]).strip()) - 0.1, 2)
        return D[c]

    if tail == "auto":
        tail = auto_tail(ep, sum(dur(c) for c in files if dur(c) >= 4.0 and files[c].suffix.lower() == ".mp4"), max_uses)

    def s(c, a=0.0, b=None):
        e = [c, a, dur(c) if b is None else min(b, dur(c))]
        return e + [crop[c]] if c in crop else e

    def ch(cid, shots, breaks, **kw):
        d = {"id": cid, "tail": tail, "lower_third": cid, "shots": shots, "breaks": breaks}
        if every_chapter:
            d.update(ticker=True, cta=True)
        d.update(kw)
        return d

    # eyewitness reactions ("look at this!", gasps) stay audible like GWN; mute only reporters, AI narration, music, profanity
    muted = set(muted) - set(reactions)
    chapters = chapters_fn(s, ch)
    if auto_overlays:
        _plan_overlays(ep, chapters, break_len)
    if not pool:
        spare, k = [s(c, 0, break_len) for c in backup if c not in muted], 0
        for c in chapters:
            fixed = []
            for b in c["breaks"]:
                if b[0] in muted and spare:
                    b, k = spare[k % len(spare)], k + 1
                fixed.append(b)
            c["breaks"] = fixed
    used = sorted(files) if pool else sorted({x[0] for c in chapters for x in c["shots"] + c["breaks"]})
    media = {c: str(files[c]).replace("\\", "/") for c in used}
    edl = {"_notes": notes, "lang": lang, "framing": "blur", "lead_in": 0.4, "break_len": break_len, "muted": sorted(set(muted) & set(used)),
           "ticker_len": ticker_len, "cta_ticker_len": cta_ticker_len, "max_shot": max_shot, "chapters": chapters, "media": media}
    if pool:
        edl.update(pool=used, max_uses=max_uses, important=sorted(important), crops={c: crop[c] for c in used if c in crop})
    archive = check_archive(archive, used, [c["id"] for c in chapters], event)
    if archive:
        edl["archive"] = archive
    edl["event"] = event
    if intro:
        edl["intro"] = {"seconds": INTRO_SECONDS, "overlap": INTRO_OVERLAP}
    check_cards(ep, [c["id"] for c in chapters])
    (ep / "project/edl.json").write_text(json.dumps(edl, indent=1), encoding="utf8")
    print(len(media), "clips in library" if pool else "clips used of", len(files))
