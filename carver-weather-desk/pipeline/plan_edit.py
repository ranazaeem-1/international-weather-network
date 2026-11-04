"""Plan a Carver edit: script/sections.json + edit/align.json + host/host_meta.json -> edit/timeline.json + edit/jobs.json

  python plan_edit.py <episode_dir>            plan only (prints the shot list)
  python plan_edit.py <episode_dir> --render   plan + render what the timeline needs (overlays, ticker, cards, base shots)
  --name CWD_slug_v2                             export / CapCut draft name (default CWD_<slug>_v1)

Layout model (owner, 4 Nov 2026): Glenn sits in the Desk Window (top right) over footage/maps/cards; full-screen only where
the script says full-host (rare); the closing full-host becomes the end screen (Glenn in a large frame + 2 video slots +
subscribe slot, >= 20 s). Ticker + bug run until the end screen; the intro sting plays on the name line.
Breaks (natsound_after) hide and pause Glenn at a section end while the footage plays with full sound.
"""
import json, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from align_host import norm_words

CWD = Path(__file__).resolve().parents[1]
BOX = [1160, 40, 720, 405]          # Desk Window (owner 4 Nov: bigger, wider framing, no labels)
NAME_CHIP = False                   # owner 4 Nov: no 'GLENN CARVER | REPORTING' chip
END_HOST = [80, 250, 896, 504]
STRAP_CLIP = [40, 720, 1360, 294]; CHIP_CLIP = [1310, 300, 600, 90]; CTA_CLIP = [1120, 440, 800, 260]; SUPER_CLIP = [60, 830, 1100, 170]
TICKER = [0, 1014, 1920, 66]
OVL = "brand-kit/src/overlays.html"
BK = (CWD / "brand-kit").as_posix()          # brand assets are absolute in the timeline (episode-relative paths are not)
UNDER_VO = 0.07; BREAK_VOL = 1.0; SFX_VOL = 0.55
SHOT_PATTERN = [5.4, 4.6, 6.0, 5.0, 4.4, 5.6]
WIPE_SWITCH, BOXWIPE_SWITCH, STING_LEAD, STING_DUR = 0.40, 0.30, 0.45, 4.2


def ffdur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))


def ffsize(p):
    o = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(p)]).decode()
    w, h = o.strip().split(",")[:2]
    return int(w), int(h)


class Plan:
    def __init__(self, ep):
        self.ep = ep
        self.S = json.loads((ep / "script/sections.json").read_text(encoding="utf-8"))
        self.A = json.loads((ep / "edit/align.json").read_text(encoding="utf-8"))
        self.M = json.loads((ep / "host/host_meta.json").read_text(encoding="utf-8"))
        self.fps = self.M["fps"]
        self.secs = self.S["sections"]; self.ids = [s["id"] for s in self.secs]
        self.warn = []
        self.name = sys.argv[sys.argv.index("--name") + 1] if "--name" in sys.argv else None     # e.g. CWD_slug_v2
        self.lib = {}
        for f in sorted((ep / "clips/lib").glob("*.mp4")):
            cid = f.name.split("_")[0]
            w, h = ffsize(f)
            self.lib[cid] = {"path": f.relative_to(ep).as_posix(), "dur": ffdur(f), "w": w, "h": h, "used": []}
        # token -> section ownership (same tokenizer as align_host)
        self.tok_range = {}; k = 0
        for s in self.secs:
            n = len(norm_words(s["spoken"])); self.tok_range[s["id"]] = (k, k + n); k += n

    def q(self, t):
        return round(round(t * self.fps) / self.fps, 4)

    # ---------- anchors ----------
    def anchor(self, sid, phrase):
        t = self.A["anchors"].get(sid, {}).get(phrase)
        if t is None:
            t = self.find(sid, phrase)
        if t is None:
            self.warn.append(f"{sid}: anchor not found {phrase!r}")
        return t

    def find(self, sid, phrase):
        a, b = self.tok_range[sid]; toks = self.A["tokens"][a:b]; pt = norm_words(phrase)
        for j in range(len(toks) - len(pt) + 1):
            if [t[0] for t in toks[j:j + len(pt)]] == pt:
                return toks[j][1] - 0.05
        return None

    # ---------- host-time layout segments ----------
    def host_segments(self):
        segs = []
        for s in self.secs:
            sid = s["id"]; t0, t1 = self.A["sections"][sid]["start"], self.A["sections"][sid]["end"]
            cur = s["layout"][0]["layout"]; cuts = []
            for l in s["layout"][1:]:
                t = self.anchor(sid, l["at"]) if l.get("at") else None
                if t is not None and t0 < t < t1:
                    cuts.append((t, l["layout"]))
            pts = [t0] + [c[0] for c in cuts] + [t1]; kinds = [cur] + [c[1] for c in cuts]
            for k, kind in enumerate(kinds):
                segs.append({"kind": kind, "h0": pts[k], "h1": pts[k + 1], "sec": sid})
        # end screen: starts on the closing subscribe line (the end screen carries the subscribe slot) or the closing
        # full-host sign-off, whichever comes first; else the last ~15 s of the voice. Never longer than 25 s of speech.
        vo_end = self.A["vo_end"]; lsid = self.ids[-1]; lsec = self.secs[-1]
        cands = [self.anchor(lsid, c["at"]) for c in lsec.get("cta", []) if c["kind"] == "subscribe" and c.get("at")]
        cands = [c for c in cands if c is not None]
        if segs[-1]["kind"] == "full-host":
            cands.append(segs[-1]["h0"])
        es = min(cands) if cands else max(self.A["sections"][lsid]["start"], vo_end - 15)
        es = max(es, vo_end - 25, self.A["sections"][lsid]["start"])
        keep = [s for s in segs if s["h1"] <= es + 1e-6]
        cut = next((s for s in segs if s["h0"] < es < s["h1"]), None)
        if cut:
            keep.append(dict(cut, h1=es))
        keep.append({"kind": "endscreen", "h0": es, "h1": segs[-1]["h1"], "sec": lsid})
        return keep

    # ---------- clip picking ----------
    def pick(self, cid, want):
        c = self.lib[cid]; d = c["dur"]; want = min(want, d - 0.3)
        for a in [0.25 + 0.5 * i for i in range(int(max(1, (d - want) / 0.5)) + 1)]:
            b = a + want
            if b <= d - 0.05 and all(b <= u0 or a >= u1 for u0, u1 in c["used"]):
                c["used"].append((a, b)); return a, want
        # all used: least-overlap start
        a = 0.25 + (len(c["used"]) * 1.7) % max(0.3, d - want - 0.3)
        c["used"].append((a, a + want)); return a, want

    def clip_pool(self, sec):
        own = [v["id"] for v in sec.get("visual", []) if v["kind"] == "clip" and v["id"] in self.lib]
        return own or sorted(self.lib, key=lambda k: len(self.lib[k]["used"]))

    def run(self):
        fps = self.fps; q = self.q; ep = self.ep
        hsegs = self.host_segments(); vo_end = self.A["vo_end"]
        # breaks at section ends
        brk = []
        for s in self.secs[:-1]:
            na = s.get("natsound_after")
            if na and na.get("clip") in self.lib and na.get("sec", 0) > 0:
                brk.append({"h": self.A["sections"][s["id"]]["end"], "len": float(na["sec"]), "clip": na["clip"], "sec": s["id"]})
            elif na and na.get("sec", 0) > 0:
                self.warn.append(f"{s['id']}: natsound clip {na.get('clip')} not in clips/lib")

        def out(h, after=True):
            return h + sum(b["len"] for b in brk if b["h"] < h - 1e-6 or (after and abs(b["h"] - h) <= 1e-6))

        # output segments
        osegs = []
        for sg in hsegs:
            osegs.append(dict(sg, t0=q(out(sg["h0"], True)), t1=q(out(sg["h1"], False))))
            for b in brk:
                if abs(b["h"] - sg["h1"]) < 1e-6:
                    t0 = q(out(b["h"], False)); osegs.append({"kind": "break", "t0": t0, "t1": q(t0 + b["len"]), "h0": b["h"], "h1": b["h"], "sec": b["sec"], "clip": b["clip"]})
        es = next(s for s in osegs if s["kind"] == "endscreen")
        es_tail = min(8.0, max(2.0, 14.0 - (es["t1"] - es["t0"])))      # end screen >= ~14 s, Glenn talks through most of it
        es["t1"] = q(es["t1"] + es_tail)
        T = es["t1"]
        tracks = {n: [] for n in ["base", "host_full", "host_box", "chrome", "straps", "chip", "cta", "supers", "ticker", "ticker_top", "bug", "wipes", "vo", "sfx"]}
        jobs = {"base": [], "gfx": [], "cards": {}}
        secmap = {s["id"]: s for s in self.secs}
        footage_windows = {}          # sec -> [(t0, t1)] runs of footage shots (strap placement)

        def add_shot(cid, t0, t1, vol=UNDER_VO, fades=(0, 0), sec=None):
            # same clip again straight after itself: extend the previous shot (no jump cut) while the clip has material
            if jobs["base"] and jobs["base"][-1]["clip"] == cid and tracks["base"][-1].get("volume") == vol and \
                    abs(tracks["base"][-1]["start"] + tracks["base"][-1]["dur"] - t0) < 1e-3:
                lj, li, c = jobs["base"][-1], tracks["base"][-1], self.lib[cid]
                a0 = lj["in"] + lj["dur"]; room = c["dur"] - 0.05 - a0
                if room > 0.8 and all(a0 + min(t1 - t0, room) <= u0 or a0 >= u1 for u0, u1 in c["used"][:-1]):
                    t1 = q(t0 + min(t1 - t0, room))
                    lj["dur"] = li["dur"] = round(t1 - li["start"], 4); c["used"][-1] = (lj["in"], lj["in"] + lj["dur"])
                    if sec and vol == UNDER_VO:
                        footage_windows.setdefault(sec, []).append((t0, t1))
                    return t1
            n = len(jobs["base"]) + 1; a, d = self.pick(cid, max(0.4, t1 - t0))
            if d < t1 - t0 - 1e-3:        # clip shorter than the slot (no slow-motion): the caller fills the rest
                t1 = q(t0 + d)
            c = self.lib[cid]; mode = "cover" if c["w"] / c["h"] >= 1.7 else "blurfill"
            bid = f"b{n:03d}"
            jobs["base"].append({"id": bid, "clip": cid, "src": c["path"], "in": round(a, 3), "dur": round(t1 - t0, 4), "mode": mode, "fps": fps,
                                 "out": f"edit/base/{bid}.mp4"})
            tracks["base"].append({"src": f"edit/base/{bid}.mp4", "start": t0, "dur": round(t1 - t0, 4), "in": 0.0, "volume": vol,
                                   "fade_in": fades[0], "fade_out": fades[1], "label": f"{cid} @ {a:.1f}s"})
            if sec and vol == UNDER_VO:
                footage_windows.setdefault(sec, []).append((t0, t1))
            return t1

        def fill(t0, t1, pool, sec):
            t, k = t0, 0
            while t1 - t > 1e-3:
                want = SHOT_PATTERN[(len(jobs["base"])) % len(SHOT_PATTERN)]
                if t1 - t < want + 2.0:
                    want = t1 - t
                cid = pool[k % len(pool)]; k += 1
                t = q(add_shot(cid, t, q(min(t1, t + want)), sec=sec))

        for sg in osegs:
            sec = secmap.get(sg["sec"], {}); t0, t1 = sg["t0"], sg["t1"]
            if t1 - t0 < 1e-3:
                continue
            if sg["kind"] == "break":
                add_shot(sg["clip"], t0, t1, vol=BREAK_VOL, fades=(0.25, 0.35)); continue
            if sg["kind"] == "endscreen":
                tracks["base"].append({"src": f"{BK}/motion/end_bg.mp4", "start": t0, "dur": round(t1 - t0, 4), "in": 0.0}); continue
            if sg["kind"] == "full-host":
                tracks["base"].append({"src": f"{BK}/graphics/navy.png", "start": t0, "dur": round(t1 - t0, 4), "in": 0.0}); continue
            if sg["kind"] in ("box+map", "box+card"):
                cards = [v for v in sec.get("visual", []) if v["kind"] == "card"]
                anchored = []
                for v in cards:
                    at = self.anchor(sg["sec"], v["at"]) if v.get("at") else None
                    if at is not None:
                        at = q(out(at, True))
                        if t0 - 0.5 <= at < t1:
                            anchored.append((max(t0, at), v["id"]))
                if not anchored and cards:
                    anchored = [(t0, cards[0]["id"])]
                anchored.sort()
                if not anchored:
                    self.warn.append(f"{sg['sec']}: {sg['kind']} without a card -> footage"); fill(t0, t1, self.clip_pool(sec), sg["sec"]); continue
                if anchored[0][0] - t0 >= 2.5:
                    fill(t0, anchored[0][0], self.clip_pool(sec), sg["sec"])
                else:
                    anchored[0] = (t0, anchored[0][1])
                for k, (a, cid) in enumerate(anchored):
                    b = anchored[k + 1][0] if k + 1 < len(anchored) else t1
                    tracks["base"].append({"src": f"graphics/cards/{cid}.mp4", "start": a, "dur": round(b - a, 4), "in": 0.0, "label": f"card {cid}"})
                    j = jobs["cards"].setdefault(cid, {"dur": 0, "start": a, "h_start": round(sg["h0"] + (a - sg["t0"]), 4), "sec": sg["sec"]})
                    j["dur"] = max(j["dur"], round(b - a + 0.2, 2))
                continue
            # box+footage: anchored clips start at their anchor, the rest fill in order
            pool = self.clip_pool(sec); marks = []
            for v in sec.get("visual", []):
                if v["kind"] == "clip" and v.get("at") and v["id"] in self.lib:
                    at = self.anchor(sg["sec"], v["at"])
                    if at is not None and t0 + 2 <= q(out(at, True)) < t1 - 2:
                        marks.append((q(out(at, True)), v["id"]))
            t = t0
            for at, cid in sorted(marks):
                fill(t, at, [p for p in pool if p != cid] or pool, sg["sec"]); t = at
                nxt = min([m for m, _ in marks if m > at] + [t1]); t = q(add_shot(cid, t, min(nxt, t + 6.5), sec=sg["sec"]))
            fill(t, t1, pool, sg["sec"])

        # ---------- host + voice ----------
        for sg in osegs:
            d = round(sg["t1"] - sg["t0"], 4)
            if sg["kind"].startswith("box"):
                tracks["host_box"].append({"src": "host/host_box.mp4", "start": sg["t0"], "dur": d, "in": round(sg["h0"], 4), "x": BOX[0], "y": BOX[1], "w": BOX[2], "h": BOX[3]})
            elif sg["kind"] == "full-host":
                tracks["host_full"].append({"src": "host/host_full.mp4", "start": sg["t0"], "dur": d, "in": round(sg["h0"], 4)})
            elif sg["kind"] == "endscreen":
                live = min(d, self.M["dur"] - sg["h0"] - 0.05, vo_end + 0.6 - sg["h0"])
                live = round(int(live * fps + 1e-6) / fps, 4)            # whole frames, so the plate starts exactly after it
                tracks["host_box"].append({"src": "host/host_end.mp4", "start": sg["t0"], "dur": live, "in": round(sg["h0"], 4),
                                           "x": END_HOST[0], "y": END_HOST[1], "w": END_HOST[2], "h": END_HOST[3]})
                if d - live > 0.1:
                    tracks["host_box"].append({"src": f"{BK}/graphics/end_plate.png", "start": q(sg["t0"] + live), "dur": round(d - live, 4),
                                               "x": END_HOST[0], "y": END_HOST[1], "w": END_HOST[2], "h": END_HOST[3], "fade_in_video": 0.5})
        cuts = sorted(b["h"] for b in brk)
        edges = [0.0] + cuts + [min(self.M["dur"], vo_end + 0.6)]
        for a, b in zip(edges, edges[1:]):
            if b - a > 0.05:
                tracks["vo"].append({"src": "host/vo.wav", "start": q(out(a, True)), "dur": round(b - a, 4), "in": round(a, 4), "volume": 1.0})

        # ---------- chrome, bug, ticker ----------
        box_runs = []
        for sg in osegs:
            if sg["kind"].startswith("box"):
                if box_runs and abs(box_runs[-1][1] - sg["t0"]) < 1e-3:
                    box_runs[-1][1] = sg["t1"]
                else:
                    box_runs.append([sg["t0"], sg["t1"]])
        for a, b in box_runs:
            tracks["chrome"].append({"src": f"{BK}/graphics/box_chrome.png", "start": a, "dur": round(b - a, 4)})
        tracks["chrome"].append({"src": f"{BK}/motion/end_fg.mov", "start": es["t0"], "dur": round(min(30, es["t1"] - es["t0"]), 4), "in": 0.0})
        tracks["bug"].append({"src": f"{BK}/graphics/bug.png", "start": 0.0, "dur": es["t0"]})
        tracks["ticker_top"].append({"src": "graphics/ticker_top.png", "start": 0.0, "dur": es["t0"]})
        tk = self.ticker_items()
        jobs["ticker"] = {"items": tk, "updated": self.S.get("ticker_updated", "")}
        self.ticker_loop = None   # filled by render; planned with a placeholder loop length
        jobs["ticker_span"] = [0.0, es["t0"]]

        # ---------- wipes + sting ----------
        def wipe(src, at, d, sfx, rect=None):
            it = {"src": src, "start": q(at), "dur": d, "in": 0.0}
            if rect:
                it.update(x=rect[0], y=rect[1], w=rect[2], h=rect[3])
            if any(not (it["start"] + d <= w["start"] or it["start"] >= w["start"] + w["dur"]) for w in tracks["wipes"]):
                return False
            tracks["wipes"].append(it)
            tracks["sfx"].append({"src": f"{BK}/sfx/{sfx}.wav", "start": q(at), "dur": round(min(d, ffdur(CWD / f'brand-kit/sfx/{sfx}.wav')), 4), "in": 0.0, "volume": SFX_VOL})
            return True
        name_sec = next((s["id"] for s in self.secs if "glenn carver" in s["spoken"].lower()), None)
        sting_at = None
        if name_sec:
            sting_at = max(0.0, q(out(self.A["sections"][name_sec]["start"], True) - STING_LEAD))
            wipe(f"{BK}/motion/sting.mov", sting_at, STING_DUR, "sting")
        host_mode = lambda k: "box" if k.startswith("box") else k
        for a, b in zip(osegs, osegs[1:]):
            ma, mb = host_mode(a["kind"]), host_mode(b["kind"]); t = b["t0"]
            if ma == mb:
                continue
            if {ma, mb} == {"box", "break"}:                   # only the desk window changes: wipe just the window
                wipe(f"{BK}/motion/wipe_box.mov", t - BOXWIPE_SWITCH, 0.6, "whoosh_small", BOX)
            else:
                wipe(f"{BK}/motion/wipe_full.mov", t - WIPE_SWITCH, 0.8, "whoosh")
        tracks["wipes"].sort(key=lambda w: w["start"]); tracks["sfx"].sort(key=lambda w: w["start"])

        # ---------- name chip, supers, straps, CTAs ----------
        def in_box(t, d):
            return any(sg["kind"].startswith("box") and sg["t0"] - 1e-3 <= t and t + d <= sg["t1"] + 1e-3 for sg in osegs)

        HOLD_FROM = {"strap": 1.45, "chip": 0.8, "super": 0.9, "cta": None}      # in-animations finish before these times

        def gfx(track, name, data, clip, at, d):
            d = round(round(d * fps) / fps, 4); out_p = f"graphics/{track}/{name}.mov"; h = HOLD_FROM.get(data["kind"])
            jobs["gfx"].append({"html": OVL, "data": dict(data, dur=d), "out": str(self.ep / out_p), "dur": d, "fps": fps, "clip": clip, "alpha": True,
                                "static": [h, d - 0.6] if h is not None and d - 0.6 > h else None})
            tracks[track].append({"src": out_p, "start": q(at), "dur": d, "in": 0.0, "x": clip[0], "y": clip[1], "w": clip[2], "h": clip[3]})

        chip_times = [0.6] if NAME_CHIP else []
        if sting_at is not None and NAME_CHIP:
            chip_times.append(sting_at + STING_DUR + 0.3)
        for a, b in zip(osegs, osegs[1:]):
            if NAME_CHIP and a["kind"] in ("full-host", "break") and b["kind"].startswith("box"):
                chip_times.append(b["t0"] + 0.5)
        chips = []
        for k, t in enumerate(sorted(chip_times)):
            d = 8.0 if k == 0 else 6.5
            sg = next((s for s in osegs if s["kind"].startswith("box") and s["t0"] - 1e-3 <= t < s["t1"]), None)
            if not sg:
                continue
            d = min(d, sg["t1"] - t - 0.3)
            if d >= 3 and all(t >= c[0] + c[1] or t + d <= c[0] for c in chips):
                chips.append((t, d)); gfx("chip", f"chip_{k:02d}", {"kind": "chip"}, CHIP_CLIP, t, d)
        tracks["chip"] = tracks.pop("chip", [])
        for sg in osegs:
            if sg["kind"] == "full-host" and sg["t1"] - sg["t0"] >= 4:
                sec = secmap[sg["sec"]]; label = sec.get("super") or (sec["title"].split(":", 1)[-1].strip().upper())[:34]
                gfx("supers", f"super_{sg['sec']}", {"kind": "super", "label": label}, SUPER_CLIP, sg["t0"] + 0.55, min(7.0, sg["t1"] - sg["t0"] - 1.0))
        for sid in self.ids:
            st = secmap[sid].get("strap")
            if not st:
                continue
            placed = False
            lead = 1.2 if sid == self.ids[0] else 0.6            # cold open: let the first second breathe
            for a, b in self.merge(footage_windows.get(sid, [])):
                pieces = [(a, b)]
                if sting_at is not None:                         # never under the intro sting
                    s0_, s1_ = sting_at, sting_at + STING_DUR + 0.2
                    pieces = [(x, min(y, s0_)) for x, y in pieces if x < s0_] + [(max(x, s1_), y) for x, y in pieces if y > s1_]
                for x, y in pieces:
                    s0 = x + lead; d = min(10.5, y - s0 - 0.3)
                    if d >= 5:
                        gfx("straps", f"strap_{sid}", {"kind": "strap", "strap": st}, STRAP_CLIP, s0, d); placed = True; break
                if placed:
                    break
            if not placed:
                self.warn.append(f"{sid}: no footage stretch >= 6 s for the strap (card/full-host section: its title carries it)")
        copy = self.S.get("cta_copy", {})
        cands = []
        for s in self.secs:
            for c in s.get("cta", []):
                at = self.anchor(s["id"], c["at"]) if c.get("at") else None
                if at is not None:
                    cands.append((q(out(at, True)), c["kind"], s["id"]))
        cands.sort()
        for k, (t, kind, sid) in enumerate(cands):
            if t >= es["t0"] - 1e-3:
                if kind != "subscribe":
                    self.warn.append(f"{sid}: CTA {kind} falls in the end screen (skipped)")
                continue                                         # the end screen carries the subscribe slot
            run = next((r for r in box_runs if r[0] - 1e-3 <= t < r[1]), None)
            if not run:
                self.warn.append(f"{sid}: CTA {kind} falls outside the desk-window layout (skipped)"); continue
            nxt = next((c[0] for c in cands[k + 1:] if c[0] < es["t0"]), None)
            d = min(8.0, run[1] - t - 0.2, (nxt - t - 0.15) if nxt else 99)
            if d < 4.0:
                self.warn.append(f"{sid}: CTA {kind} has no room ({d:.1f} s, skipped)"); continue
            cc = copy.get(kind, {})
            gfx("cta", f"cta_{kind}_{sid}", {"kind": "cta", "cta": kind, "head": cc.get("head", ""), "sub": cc.get("sub", "")}, CTA_CLIP, t, d)

        order = ["base", "host_full", "host_box", "chrome", "straps"] + (["chip"] if NAME_CHIP else []) + ["cta", "supers", "ticker", "ticker_top", "bug", "wipes"]
        self.tracks, self.osegs, self.jobs, self.T, self.es = tracks, osegs, jobs, T, es
        self.order = order
        return self

    @staticmethod
    def merge(ws):
        ws = sorted(ws); out = []
        for a, b in ws:
            if out and a - out[-1][1] < 1e-3:
                out[-1][1] = b
            else:
                out.append([a, b])
        return out

    def ticker_items(self):
        seen, items = set(), []
        for s in self.secs:
            for it in s.get("ticker", []):
                key = (it.get("label", ""), it.get("text", ""))
                if key not in seen:
                    seen.add(key); items.append({"label": it.get("label", ""), "text": it.get("text", "")})
        return items

    # ---------- write ----------
    def timeline(self, ticker_loop):
        tr = self.tracks
        a, b = self.jobs["ticker_span"]; t = a; L = ticker_loop
        tr["ticker"] = []
        while b - t > 1e-3:
            d = round(min(L, b - t), 4)
            tr["ticker"].append({"src": "graphics/ticker_run.mp4", "start": round(t, 4), "dur": d, "in": 0.0, "x": TICKER[0], "y": TICKER[1], "w": TICKER[2], "h": TICKER[3]})
            t = round(t + d, 4)
        vids = [{"name": n, "type": "video", "items": sorted(tr.get(n, []), key=lambda i: i["start"])} for n in self.order]
        auds = [{"name": n, "type": "audio", "items": sorted(tr[n], key=lambda i: i["start"])} for n in ("vo", "sfx")]
        markers = []
        for s in self.secs:
            sg = next(g for g in self.osegs if g["sec"] == s["id"] and g["kind"] != "break")
            markers.append({"t": sg["t0"], "label": f"{s['id']} {s['title']}"})
        name = self.name or f"CWD_{self.ep.name[11:] if self.ep.name[:4].isdigit() else self.ep.name}_v1"
        return {"version": 1, "name": name, "root": self.ep.as_posix(),
                "w": 1920, "h": 1080, "fps": self.fps, "duration": self.T, "tracks": vids + auds, "markers": markers}

    def report(self):
        if self.T > 720.0:          # owner's cap (4 Nov): the finished video is 12:00 or less
            self.warn.insert(0, f"FINISHED VIDEO {int(self.T // 60)}:{self.T % 60:05.2f} IS OVER THE 12:00 CAP: HeyGen read slower than "
                                f"carver_wpm. Drop a nat-sound break, or ask the owner to re-render a trimmed script")
        lines = [f"timeline {self.T:.2f}s @ {self.fps} fps; end screen {self.es['t0']:.2f}-{self.es['t1']:.2f}"]
        for sg in self.osegs:
            lines.append(f"  {sg['t0']:7.2f}-{sg['t1']:7.2f}  {sg['kind']:<11} {sg['sec']}")
        lines.append("base:")
        for it in self.tracks["base"]:
            lines.append(f"  {it['start']:7.2f} +{it['dur']:5.2f}  {it.get('label', it['src'])}  vol {it.get('volume', 0)}")
        for n in ("straps", "chip", "cta", "supers", "wipes"):
            for it in self.tracks.get(n, []):
                lines.append(f"  {n:<7} {it['start']:7.2f} +{it['dur']:5.2f}  {Path(it['src']).name}")
        if self.warn:
            lines.append("WARNINGS:"); lines += ["  ! " + w for w in self.warn]
        return "\n".join(lines)


def render_ticker(ep, items, updated, fps):
    """ticker_top.png (static chrome) + ticker_run.mp4 (seamless scrolling loop, 1920x66). Returns loop seconds."""
    from playwright.sync_api import sync_playwright
    sys.path.insert(0, str(Path(__file__).parent)); from motion import render_jobs
    render_jobs([{"html": OVL, "data": {"kind": "ticker_top", "updated": updated}, "out": str(ep / "graphics/ticker_top.png"), "dur": 0}], 1)
    esc = lambda s: (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    unit = "".join(f'<span>{("<b>" + esc(i["label"]) + "</b> ") if i["label"] else ""}{esc(i["text"])}</span><i class="sep"></i>' for i in items) or \
           '<span><b>CARVER WEATHER DESK</b> Weather news that tells you what to do</span><i class="sep"></i>'
    css = (CWD / "brand-kit/src/brand.css").as_uri()
    html = f"""<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{css}"><style>
      html,body{{width:auto;height:66px;background:transparent}}
      #s{{display:inline-flex;align-items:center;height:66px;gap:26px;padding-left:26px;white-space:nowrap;
         background:linear-gradient(180deg,#0D2250 0%,#071430 100%);box-shadow:inset 0 2px 0 rgba(92,200,255,.35);
         font:600 27px/1 var(--sans);letter-spacing:-.005em;color:#fff}}
      #s b{{font-weight:800;color:var(--amber)}} #s .sep{{width:10px;height:10px;background:var(--crimson);transform:rotate(45deg);flex:none}}
    </style></head><body><div id="s"></div></body></html>"""
    tmp = ep / "graphics/_ticker.html"; tmp.write_text(html, encoding="utf-8")
    px = 4 if fps >= 30 else 5
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 16000, "height": 66})
        pg.goto(tmp.as_uri()); pg.evaluate("document.fonts.ready")
        reps = 1
        while True:
            pg.evaluate("([u, n]) => { document.getElementById('s').innerHTML = u.repeat(n); }", [unit, reps])
            w = pg.evaluate("document.getElementById('s').getBoundingClientRect().width")
            if w >= 1960 or reps > 12:
                break
            reps += 1
        wa = int(-(-w // px) * px)
        pg.evaluate(f"document.getElementById('s').style.width = '{wa}px'")
        pg.locator("#s").screenshot(path=str(ep / "graphics/_ticker_cycle.png"))
        b.close()
    n = wa // px
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(fps), "-i", str(ep / "graphics/_ticker_cycle.png"),
                    "-filter_complex", f"[0:v]split[a][b];[a][b]hstack,crop=1920:66:x='mod(n*{px},{wa})':y=0,format=yuv420p[v]",
                    "-map", "[v]", "-frames:v", str(n), "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-r", str(fps),
                    str(ep / "graphics/ticker_run.mp4")], check=True)
    tmp.unlink(missing_ok=True)
    return n / fps


def resolve_card_specs(plan):
    """graphics/cards/<id>.json (authored) -> edit/cards/<id>.json with dur + every at_words resolved to seconds."""
    ep = plan.ep; out = {}
    for cid, j in plan.jobs["cards"].items():
        src = ep / f"graphics/cards/{cid}.json"
        if not src.exists():
            plan.warn.append(f"card spec missing: graphics/cards/{cid}.json"); continue
        spec = json.loads(src.read_text(encoding="utf-8")); spec["dur"] = j["dur"]; spec["id"] = cid

        def walk(o):
            if isinstance(o, dict):
                if "at_words" in o:
                    phrase = o.pop("at_words"); t = plan.find(j["sec"], phrase)          # host clock, like h_start
                    if t is not None:
                        o["at"] = round(max(0.3, t - j["h_start"]), 2)
                    else:
                        plan.warn.append(f"card {cid}: at_words not found {phrase!r}")
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(spec)
        dst = ep / f"edit/cards/{cid}.json"; dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(spec, indent=1), encoding="utf-8"); out[cid] = dst
    return out


def main():
    ep = Path(sys.argv[1]).resolve()
    P = Plan(ep).run()
    render = "--render" in sys.argv
    loop = render_ticker(ep, P.jobs["ticker"]["items"], P.jobs["ticker"]["updated"], P.fps) if render else 60.0
    tl = P.timeline(loop)
    (ep / "edit").mkdir(exist_ok=True)
    (ep / "edit/timeline.json").write_text(json.dumps(tl, indent=1), encoding="utf-8")
    (ep / "edit/jobs.json").write_text(json.dumps(P.jobs, indent=1), encoding="utf-8")
    if render:
        from motion import render_jobs
        cards = resolve_card_specs(P)
        procs = [subprocess.Popen([sys.executable, str(CWD / "pipeline/make_card.py"), str(spec), str(ep / f"graphics/cards/{cid}.mp4")])
                 for cid, spec in cards.items()]
        render_jobs(P.jobs["gfx"], workers=4)
        subprocess.run([sys.executable, str(CWD / "pipeline/build_base.py"), str(ep)], check=True)
        for p in procs:
            p.wait()
            if p.returncode:
                P.warn.append(f"make_card failed ({p.args[2]})")
    rep = P.report(); (ep / "edit/plan_report.txt").write_text(rep, encoding="utf-8"); print(rep)


if __name__ == "__main__":
    main()
