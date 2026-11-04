"""Carver script tools: lint script/script.md, then build the HeyGen paste files and sections.json.

Usage:
  python script_tools.py lint  <episode_dir> [--demo]
  python script_tools.py build <episode_dir> [--demo]     (lint, then write the outputs)

Reads   <episode_dir>/script/script.md                   (format: docs/script-guide.md section 5.1)
Writes  <episode_dir>/script/heygen_paste.txt             THE one script the owner pastes into HeyGen (owner, 4 Nov:
                                                          "it needs to be one script"), one paragraph per section
        <episode_dir>/script/sections.json                schema: docs/timeline-schema.md section 1
        (--parts also writes heygen_paste_partNN.txt <= 4,500 chars, only if HeyGen ever refuses the full length)
Runtime cap: the finished video must be 12:00 or less (owner, 4 Nov): words / carver_wpm + nat-sound breaks + end tail.

Times are estimated on the HeyGen clock: words / carver_wpm (nat-sound breaks are not counted).
--demo turns the template and position checks (section word counts, section count, name-line,
CTA and full-host timing) into warnings. Every other rule stays an error. Exit code 1 on errors.
"""
import argparse
import glob
import json
import os
import re
import sys
import unicodedata

import yaml

PART_LIMIT = 4500
MAX_RUNTIME = 720.0             # s: owner's cap for the whole finished video
END_TAIL_EST = 4.0              # s: end-screen tail after the voice (plan_edit adds 2-8 s)
MAX_SENT_WORDS = 28
AVG_SENT_WARN = 16
TOTAL_TOL = 0.05
SECTION_TOL = 0.15
FULL_HOST_MAX_SECTIONS = 3
FULL_HOST_EARLIEST = 150.0      # s, estimated HeyGen time
FULL_HOST_MAX_DUR = 30.0        # s
CTA_EARLIEST = 120.0            # s
NAME_LINE = "I'm Glenn Carver, and this is the Carver Weather Desk"
NAME_LINE_WINDOW = (35.0, 55.0)
MAX_PAUSES = 8
MAX_NATSOUND = 3
NATSOUND_RANGE = (6, 10)
HEAD_MAX, SUB_MAX, TICKER_MAX = 40, 90, 90

LAYOUTS = ("box+footage", "box+map", "box+card", "full-host")
KICKERS = ("WEATHER ALERT", "DEVELOPING", "FORECAST", "AFTERMATH")
CTA_KINDS = ("share", "comment", "subscribe")
SECTION_KEYS = {"layout", "strap", "ticker", "visual", "cta", "natsound_after", "pause", "cue",
                "facts", "spoken", "notes"}

# docs/script-guide.md section 3 (12-minute cap, owner 4 Nov), words per section at 150 wpm (scaled by target_words / nominal)
TEMPLATE = {"S01": (85, 105), "S02": (45, 60), "S03": (195, 225), "S04": (140, 160),
            "S05": (195, 225), "S06": (200, 230), "S07": (150, 175), "S08": (200, 230),
            "S09": (120, 140), "S10": (90, 110), "S11": (50, 65), "S12": (40, 55)}
TEMPLATE_NOMINAL = sum((a + b) / 2 for a, b in TEMPLATE.values())   # 1,645 words = about 11:00 at 150 wpm

FORBIDDEN = re.compile(r'[0-9\[\](){}/\\&%$#@*_~+=<>|^"“”…—–;:!]')
ABBREV = re.compile(r"\bmph\b|\b[ap]\.m\.|\b(?:St|Mt|Ft|Rd|Ave|Blvd|Hwy|Co|Jr|Sr)\.(?=\s|$)|\bHwy\b|\bBlvd\b")
CAPS_OK = {"NOAA", "FEMA", "TV"}
NUMBER_WORDS = set("""zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen
fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred
thousand million billion half quarter dozen first second third fourth fifth sixth seventh eighth ninth tenth
eleventh twelfth twentieth thirtieth hundredth thousandth""".split())
BANNED = ["delve", "dive in", "dive into", "in today's video", "it's important to note", "it's worth noting",
          "a stark reminder", "a testament to", "navigating", "amidst", "in the realm of", "buckle up",
          "without further ado", "monster storm", "apocalyptic", "unprecedented", "insane", "shocking",
          "you won't believe", "mother nature", "brace yourselves", "calm before the storm", "smash that",
          "hit the bell", "where are you watching from", "it really helps the channel",
          "if this video helped you", "and it came at a cost", "but that was just the beginning",
          "as you can see", "basically", "game-changer"]


# ---------------------------------------------------------------- text helpers
def norm_tokens(s):
    """Lowercase, accents stripped, apostrophes dropped, other punctuation = space."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("’", "'").replace("‘", "'").replace("'", "")
    return re.sub(r"[^a-z0-9]+", " ", s).split()


def word_spans(text):
    return [m for m in re.finditer(r"\S+", text) if re.search(r"[A-Za-z0-9]", m.group())]


def tokens_with_map(text):
    spans = word_spans(text)
    toks = []
    for i, m in enumerate(spans):
        for t in norm_tokens(m.group()):
            toks.append((t, i))
    return spans, toks


def find_anchor(text, anchor):
    """First occurrence of anchor (case/punctuation-insensitive). Returns (first_word_idx, last_word_idx)."""
    want = norm_tokens(anchor)
    if not want:
        return None
    _, toks = tokens_with_map(text)
    seq = [t for t, _ in toks]
    n = len(want)
    for k in range(len(seq) - n + 1):
        if seq[k:k + n] == want:
            return toks[k][1], toks[k + n - 1][1]
    return None


def count_seq(seq, sub):
    n = len(sub)
    return sum(1 for k in range(len(seq) - n + 1) if seq[k:k + n] == sub) if n else 0


def clean_word(w):
    return re.sub(r"^[^\w']+|[^\w']+$", "", w)


def mmss(t):
    t = max(0, int(round(t)))
    return f"{t // 60}:{t % 60:02d}"


def num(x):
    x = float(x)
    return int(x) if x.is_integer() else x


def fmt_sec(x):
    x = float(x)
    return str(int(x)) if x.is_integer() else f"{x:g}"


# ---------------------------------------------------------------- report
class Report:
    def __init__(self, demo):
        self.demo, self.errors, self.warnings = demo, [], []

    def err(self, where, msg):
        self.errors.append(f"[{where}] {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"[{where}] {msg}")

    def soft(self, where, msg):
        """Template / position check: error normally, warning with --demo."""
        if self.demo:
            self.warnings.append(f"[{where}] {msg}  (demo: warning)")
        else:
            self.errors.append(f"[{where}] {msg}")


# ---------------------------------------------------------------- parsing script.md
KEY_RE = re.compile(r"^([a-z_]+):(?:\s(.*))?$")
HEAD_RE = re.compile(r"^##\s*\[(S\d{2})\]\s*(.*?)\s*$")


def parse_script(path, rep):
    raw = open(path, encoding="utf-8-sig").read().replace("\r\n", "\n").replace(" ", " ")
    lines = raw.split("\n")
    if not lines or lines[0].strip() != "---":
        rep.err("file", "script.md must start with a '---' front-matter block")
        return {}, []
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        rep.err("file", "front matter is not closed with '---'")
        return {}, []
    try:
        fm = yaml.safe_load("\n".join(lines[1:end])) or {}
    except yaml.YAMLError as e:
        rep.err("front matter", f"YAML error: {e}")
        return {}, []

    sections, cur, i = [], None, end + 1
    while i < len(lines):
        line = lines[i]
        m = HEAD_RE.match(line)
        if m:
            cur = {"id": m.group(1), "title": m.group(2), "fields": {}, "line": i + 1}
            sections.append(cur)
            i += 1
            continue
        if cur is None or not line.strip() or line.lstrip().startswith(("<!--", "# ")):
            i += 1
            continue
        km = KEY_RE.match(line)
        if not km:
            rep.err(cur["id"], f"line {i + 1}: not a 'key: value' line: {line.strip()[:60]}")
            i += 1
            continue
        key, val = km.group(1), (km.group(2) or "").strip()
        if key != "spoken":
            val = re.sub(r"\s+#\s.*$", "", val).strip()     # trailing ' # comment' on field lines
        if key not in SECTION_KEYS:
            rep.warn(cur["id"], f"line {i + 1}: unknown key '{key}' (ignored)")
        if key in cur["fields"]:
            rep.warn(cur["id"], f"line {i + 1}: '{key}' given twice; the last one wins")
        if key in ("ticker", "spoken") and val in ("", "|", ">"):
            block, i = [], i + 1
            while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                if HEAD_RE.match(lines[i]):
                    break
                block.append(lines[i])
                i += 1
            cur["fields"][key] = ("block", block)
            continue
        cur["fields"][key] = ("inline", val)
        i += 1
    return fm, sections


def fix_quotes(s):
    return s.replace("“", '"').replace("”", '"')


ANCH = r'(?:\s*@\s*"([^"]+)")?'


def parse_layout(val, sid, rep):
    parts = re.split(r"\s*(?:->|→)\s*", fix_quotes(val).strip())
    out = []
    for k, p in enumerate(parts):
        m = re.fullmatch(r"(box\+footage|box\+map|box\+card|full-host)" + ANCH, p.strip())
        if not m:
            rep.err(sid, f"layout: cannot read '{p}' (use one of {', '.join(LAYOUTS)}, switches as 'a -> b @ \"words\"')")
            continue
        lay, at = m.group(1), m.group(2)
        if k == 0 and at:
            rep.err(sid, "layout: the first layout starts with the section and takes no @ anchor")
            at = None
        if k > 0 and not at:
            rep.err(sid, f"layout: switch to '{lay}' needs an @ \"words\" anchor")
        out.append({"layout": lay, "at": at})
    return out


def parse_strap(val, sid, rep):
    if val.strip().lower() in ("none", "null", "~"):
        return None
    if not val.strip():
        rep.err(sid, "strap: empty (write 'strap: none' for no strap)")
        return None
    f = [x.strip() for x in val.split("|")]
    if len(f) != 4:
        rep.err(sid, f"strap: needs 4 fields 'KICKER | LOCATION | HEADLINE | subline', got {len(f)}")
        return None
    kicker, loc, head, sub = f
    if kicker not in KICKERS:
        rep.err(sid, f"strap: kicker '{kicker}' must be one of {' | '.join(KICKERS)}")
    if loc != loc.upper():
        rep.warn(sid, f"strap: location '{loc}' should be uppercase")
    plain = head.replace("*", "")
    if head.count("*") % 2:
        rep.err(sid, "strap: unbalanced *emphasis* markers in headline")
    if "**" in head:
        rep.err(sid, "strap: empty *emphasis* in headline")
    if len(plain) > HEAD_MAX:
        rep.err(sid, f"strap: headline is {len(plain)} chars (max {HEAD_MAX}): {plain}")
    if plain != plain.upper():
        rep.err(sid, f"strap: headline must be uppercase: {plain}")
    if not sub:
        rep.err(sid, "strap: subline is empty")
    elif len(sub) > SUB_MAX:
        rep.err(sid, f"strap: subline is {len(sub)} chars (max {SUB_MAX})")
    else:
        letters = [c for c in sub if c.isalpha()]
        if len(letters) > 3 and all(c.isupper() for c in letters):
            rep.warn(sid, f"strap: subline should be sentence case, not all caps: {sub}")
    return {"kicker": kicker, "loc": loc, "head": head, "sub": sub}


def parse_ticker(field, sid, rep):
    kind, val = field
    if kind == "inline":
        if val.strip() in ("[]", "none", ""):
            return []
        items = [val]
    else:
        items = []
        for l in val:
            s = l.strip()
            if not s:
                continue
            if not s.startswith("-"):
                rep.err(sid, f"ticker: list items start with '- ': {s[:50]}")
                continue
            items.append(s[1:].strip())
    out = []
    for it in items:
        if len(it) >= 2 and it[0] == it[-1] and it[0] in "\"'":
            it = it[1:-1]
        m = re.match(r"^([A-Z0-9][A-Z0-9 &/'.\-]*?):\s+(.+)$", it)
        label, text = (m.group(1).strip(), m.group(2).strip()) if m else (None, it.strip())
        if not text:
            rep.err(sid, "ticker: empty item")
        elif len(text) > TICKER_MAX:
            rep.warn(sid, f"ticker: item is {len(text)} chars (keep under {TICKER_MAX}): {text[:40]}...")
        out.append({"label": label, "text": text})
    return out


def parse_visual(val, sid, rep):
    out = []
    for p in [x.strip() for x in fix_quotes(val).split("|") if x.strip()]:
        m = re.fullmatch(r"(card:)?([A-Za-z0-9_\-]+)" + ANCH, p)
        if not m:
            rep.err(sid, f"visual: cannot read '{p}' (use ID, card:<id>, optional @ \"words\")")
            continue
        out.append({"kind": "card" if m.group(1) else "clip", "id": m.group(2), "at": m.group(3)})
    return out


def parse_cta(val, sid, rep):
    out = []
    for p in [x.strip() for x in fix_quotes(val).split("|") if x.strip()]:
        m = re.fullmatch(r"(\w+)\s*@\s*\"([^\"]+)\"", p)
        if not m or m.group(1) not in CTA_KINDS:
            rep.err(sid, f"cta: cannot read '{p}' (use share|comment|subscribe @ \"words\")")
            continue
        out.append({"kind": m.group(1), "at": m.group(2)})
    return out


def parse_pause(val, sid, rep):
    out = []
    for p in [x.strip() for x in fix_quotes(val).split("|") if x.strip()]:
        m = re.fullmatch(r'after\s*"([^"]+)"\s*(\d+(?:\.\d+)?)\s*s', p)
        if not m:
            rep.err(sid, f"pause: cannot read '{p}' (use after \"words\" 0.5s)")
            continue
        out.append({"after": m.group(1), "sec": num(m.group(2))})
    return out


def parse_natsound(val, sid, rep):
    v = val.strip()
    if v in ("0", "", "none"):
        return None
    m = re.fullmatch(r"([A-Za-z0-9]+)\s+(\d+(?:\.\d+)?)\s*s?", v)
    if not m:
        rep.err(sid, f"natsound_after: cannot read '{v}' (use '<clip ID> <seconds>' or 0)")
        return None
    return {"clip": m.group(1), "sec": num(m.group(2))}


def clip_file(ep, cid):
    return glob.glob(os.path.join(ep, "clips", "lib", f"{cid}_*.mp4"))


def load_glossary_caps(ep):
    caps = set(CAPS_OK)
    gl = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(ep))), "docs", "pronunciation-glossary.csv")
    if os.path.exists(gl):
        for l in open(gl, encoding="utf-8-sig"):
            t = l.split(",")[0].strip()
            if t and t.isupper():
                caps.add(t)
    return caps


# ---------------------------------------------------------------- lint + build model
def lint(ep, demo):
    rep = Report(demo)
    path = os.path.join(ep, "script", "script.md")
    if not os.path.exists(path):
        rep.err("file", f"missing {path}")
        return rep, None
    fm, raw_secs = parse_script(path, rep)
    if not raw_secs:
        rep.err("file", "no sections found (headers look like '## [S01] Title')")
        return rep, None

    # front matter
    for k in ("episode", "as_of", "ticker_updated", "target_words", "carver_wpm", "cta_copy"):
        if k not in fm:
            rep.err("front matter", f"missing '{k}'")
    wpm = float(fm.get("carver_wpm") or 150)
    target = int(fm.get("target_words") or 0)
    break_tags = bool(fm.get("break_tags", False))
    sample = bool(fm.get("sample", False))
    if fm.get("episode") and os.path.basename(os.path.abspath(ep)) != fm["episode"]:
        rep.warn("front matter", f"episode '{fm['episode']}' differs from folder '{os.path.basename(os.path.abspath(ep))}'")
    if demo and not sample:
        rep.warn("front matter", "--demo used on a script without sample: true")
    cta_copy = fm.get("cta_copy") or {}
    if not isinstance(cta_copy, dict):
        rep.err("front matter", "cta_copy must map share/comment/subscribe to {head, sub}")
        cta_copy = {}
    for k, v in cta_copy.items():
        if k not in CTA_KINDS:
            rep.err("front matter", f"cta_copy: unknown kind '{k}'")
        elif not (isinstance(v, dict) and isinstance(v.get("head"), str) and isinstance(v.get("sub"), str)):
            rep.err("front matter", f"cta_copy.{k} needs 'head' and 'sub' strings")
        elif v["head"] != v["head"].upper():
            rep.warn("front matter", f"cta_copy.{k}.head should be uppercase")
    caps_ok = load_glossary_caps(ep)

    # sections
    secs, seen, prev_ticker = [], set(), None
    for n, rs in enumerate(raw_secs, 1):
        sid, f = rs["id"], rs["fields"]
        if sid in seen:
            rep.err(sid, "duplicate section ID")
        seen.add(sid)
        if sid != f"S{n:02d}":
            rep.warn(sid, f"expected ID S{n:02d} here (IDs should run S01, S02, ... in order)")
        get = lambda k: f[k][1] if k in f and f[k][0] == "inline" else None

        if "spoken" not in f:
            rep.err(sid, "missing 'spoken'")
            spoken = ""
        else:
            kind, val = f["spoken"]
            spoken = " ".join(l.strip() for l in val) if kind == "block" else val
        spoken = re.sub(r"\s+", " ", spoken.replace("’", "'").replace("‘", "'")).strip()
        if not spoken and "spoken" in f:
            rep.err(sid, "spoken text is empty")

        layout = parse_layout(get("layout"), sid, rep) if get("layout") else []
        if not layout:
            rep.err(sid, "missing 'layout'")
        if "strap" not in f:
            rep.err(sid, "missing 'strap' (write 'strap: none' for no strap)")
            strap = None
        else:
            strap = parse_strap(get("strap") or "", sid, rep)
        if "ticker" in f:
            ticker = parse_ticker(f["ticker"], sid, rep)
        else:
            ticker = list(prev_ticker) if prev_ticker is not None else []
            if prev_ticker is None:
                rep.warn(sid, "no ticker (later sections without 'ticker:' keep the previous lines)")
        prev_ticker = ticker
        visual = parse_visual(get("visual"), sid, rep) if get("visual") else []
        cta = parse_cta(get("cta"), sid, rep) if get("cta") else []
        pause = parse_pause(get("pause"), sid, rep) if get("pause") else []
        nat = parse_natsound(get("natsound_after") or "0", sid, rep)
        if not sample and not get("facts"):
            rep.warn(sid, "no 'facts:' line (every number needs a facts.csv ID)")

        spans = word_spans(spoken)
        words = len(spans)
        cue_words = [clean_word(m.group()) for m in spans[:6]]
        cue = " ".join(w for w in cue_words if w)
        if get("cue") and norm_tokens(get("cue")) != norm_tokens(cue):
            rep.err(sid, f"cue: '{get('cue')}' is not the first 6 spoken words ('{cue}')")

        secs.append({"id": sid, "title": rs["title"], "layout": layout, "strap": strap, "ticker": ticker,
                     "visual": visual, "cta": cta, "natsound_after": nat, "pause": pause, "cue": cue,
                     "spoken": spoken, "words": words})

    # ---- spoken-text rules (guide section 4)
    for s in secs:
        sid, t = s["id"], s["spoken"]
        for m in FORBIDDEN.finditer(t):
            ctx = t[max(0, m.start() - 20):m.end() + 20]
            rep.err(sid, f"forbidden character '{m.group()}' in spoken text: ...{ctx}...")
        for m in ABBREV.finditer(t):
            rep.err(sid, f"abbreviation '{m.group()}': write it out (guide 4.4/4.5)")
        for m in word_spans(t):
            for part in re.split(r"[-']", clean_word(m.group())):
                if len(part) >= 2 and part.isalpha() and part.isupper() and part not in caps_ok:
                    rep.err(sid, f"ALL-CAPS word '{part}' (spell it out, or add it to docs/pronunciation-glossary.csv)")
        sents = [x for x in re.split(r"(?<=[.?!])\s+", t) if x.strip()]
        lens = [len(word_spans(x)) for x in sents]
        for x, n_ in zip(sents, lens):
            if n_ > MAX_SENT_WORDS:
                rep.err(sid, f"sentence of {n_} words (max {MAX_SENT_WORDS}): {x[:70]}...")
        if lens and sum(lens) / len(lens) > AVG_SENT_WARN:
            rep.warn(sid, f"average sentence is {sum(lens) / len(lens):.1f} words (aim for 12 to 16)")
        low = " " + " ".join(t.lower().replace("’", "'").split()) + " "
        for b in BANNED:
            if re.search(r"(?<![a-z])" + re.escape(b) + r"(?![a-z])", low):
                rep.warn(sid, f"banned phrase '{b}' (guide 2.5)")
    heres = sum(len(re.findall(r"\bhere's the part\b", s["spoken"].lower())) for s in secs)
    if heres > 2:
        rep.warn("script", f"'Here's the part' used {heres} times (max 2)")

    # ---- totals
    total = sum(s["words"] for s in secs)
    if target:
        lo, hi = round(target * (1 - TOTAL_TOL)), round(target * (1 + TOTAL_TOL))
        if not lo <= total <= hi:
            rep.err("script", f"total {total} words, target {target} +/-5% ({lo} to {hi})")
    nat_s = sum(s["natsound_after"]["sec"] for s in secs if s["natsound_after"])
    runtime = total / wpm * 60.0 + nat_s + END_TAIL_EST
    if runtime > MAX_RUNTIME:
        rep.err("script", f"estimated video {mmss(runtime)} is over the 12:00 cap ({total} words at {wpm:g} wpm"
                          f" + {nat_s:g} s breaks); cut about {int((runtime - MAX_RUNTIME) / 60 * wpm) + 1} words")

    # ---- template (soft). Ranges follow target_words when it is near a full episode (new wpm after the pilot).
    scale = (target / TEMPLATE_NOMINAL) if target else 1.0
    if not 0.8 <= scale <= 1.3:
        scale = 1.0
    for s in secs:
        if s["id"] in TEMPLATE:
            a, b = TEMPLATE[s["id"]]
            lo, hi = round(a * scale * (1 - SECTION_TOL)), round(b * scale * (1 + SECTION_TOL))
            if not lo <= s["words"] <= hi:
                rep.soft(s["id"], f"template: {s['words']} words, template {lo} to {hi} for this slot")
        else:
            rep.soft(s["id"], "template: no slot for this ID in the guide section 3 template")
    if len(secs) != len(TEMPLATE):
        rep.soft("script", f"template: {len(secs)} sections, the template has {len(TEMPLATE)}")

    # ---- anchors, timing, layouts, visuals
    start_w, acc = {}, 0
    for s in secs:
        start_w[s["id"]] = acc
        acc += s["words"]
    est = lambda sid, w: (start_w[sid] + w) / wpm * 60.0
    full_host_secs, name_found = [], False
    all_tokens = []
    for s in secs:
        all_tokens += norm_tokens(s["spoken"])
    for s in secs:
        sid, t = s["id"], s["spoken"]

        def pos(anchor, what):
            r = find_anchor(t, anchor)
            if r is None:
                rep.err(sid, f"{what}: anchor \"{anchor}\" is not in this section's spoken text")
            return r

        # layout segments
        segs = []
        for k, L in enumerate(s["layout"]):
            if k == 0:
                segs.append([L["layout"], 0])
            elif L["at"]:
                r = pos(L["at"], f"layout '{L['layout']}'")
                if r:
                    segs.append([L["layout"], r[0]])
        for a, b in zip(segs, segs[1:]):
            if b[1] <= a[1]:
                rep.err(sid, f"layout: switch to '{b[0]}' is not after the previous layout's start")
        for k, (lay, w0) in enumerate(segs):
            w1 = segs[k + 1][1] if k + 1 < len(segs) else s["words"]
            dur = (w1 - w0) / wpm * 60.0
            if lay == "full-host":
                if sid not in full_host_secs:
                    full_host_secs.append(sid)
                if dur > FULL_HOST_MAX_DUR:
                    rep.err(sid, f"full-host: about {dur:.0f} s (max {FULL_HOST_MAX_DUR:.0f} s)")
                if est(sid, w0) < FULL_HOST_EARLIEST:
                    rep.soft(sid, f"position: full-host at about {mmss(est(sid, w0))} (none before {mmss(FULL_HOST_EARLIEST)})")
        s["_segs"] = segs

        # visuals: anchors in order, files exist
        if any(L.startswith("box") for L, _ in segs) and not s["visual"]:
            rep.err(sid, "visual: a box layout needs at least one visual")
        last = -1
        for v in s["visual"]:
            if v["at"]:
                r = pos(v["at"], f"visual {v['id']}")
                if r:
                    if r[0] < last:
                        rep.err(sid, f"visual: '{v['id']}' is anchored before the item listed ahead of it")
                    last = r[0]
            if v["kind"] == "clip":
                fl = clip_file(ep, v["id"])
                if not fl:
                    rep.err(sid, f"visual: no clips/lib/{v['id']}_*.mp4")
                elif len(fl) > 1:
                    rep.err(sid, f"visual: {len(fl)} files match clips/lib/{v['id']}_*.mp4")
            elif not os.path.exists(os.path.join(ep, "graphics", "cards", v["id"] + ".mp4")):
                rep.warn(sid, f"visual: graphics/cards/{v['id']}.mp4 not rendered yet")
        if s["visual"] and s["visual"][0]["at"]:
            r = find_anchor(t, s["visual"][0]["at"])
            if r and r[0] > 0 and segs and segs[0][0] != "full-host":
                rep.warn(sid, f"visual: first item starts at word {r[0] + 1}; nothing is assigned to the section start")
        for lay, w0 in segs:
            if lay in ("box+map", "box+card") and not any(v["kind"] == "card" for v in s["visual"]):
                rep.warn(sid, f"layout {lay} but no card: visual in this section")

        # CTA
        for c in s["cta"]:
            if c["kind"] not in cta_copy:
                rep.err(sid, f"cta: '{c['kind']}' has no cta_copy entry in the front matter")
            r = pos(c["at"], f"cta {c['kind']}")
            if r and est(sid, r[0]) < CTA_EARLIEST:
                rep.soft(sid, f"position: {c['kind']} CTA at about {mmss(est(sid, r[0]))} (nothing before {mmss(CTA_EARLIEST)})")

        # pauses
        for p in s["pause"]:
            pos(p["after"], "pause")

        # nat-sound
        nat = s["natsound_after"]
        if nat:
            fl = clip_file(ep, nat["clip"])
            if not fl:
                rep.err(sid, f"natsound_after: no clips/lib/{nat['clip']}_*.mp4")
            elif len(fl) > 1:
                rep.err(sid, f"natsound_after: {len(fl)} files match clips/lib/{nat['clip']}_*.mp4")
            if not NATSOUND_RANGE[0] <= nat["sec"] <= NATSOUND_RANGE[1]:
                rep.warn(sid, f"natsound_after: {nat['sec']} s (guide: {NATSOUND_RANGE[0]} to {NATSOUND_RANGE[1]} s)")

        # cue
        ct = norm_tokens(s["cue"])
        if ct:
            if ct[0] in NUMBER_WORDS or (ct[0] in ("a", "an") and len(ct) > 1 and ct[1] in NUMBER_WORDS):
                rep.err(sid, f"cue: '{s['cue']}' starts with a number word (whisper writes digits)")
            if len(ct) < 6:
                rep.warn(sid, f"cue: only {len(ct)} words")
            if count_seq(all_tokens, ct) > 1:
                rep.err(sid, f"cue: '{s['cue']}' occurs {count_seq(all_tokens, ct)} times in the script; reword the opening")

        # name line
        r = find_anchor(t, NAME_LINE)
        if r and not name_found:
            name_found = True
            tt = est(sid, r[0])
            if not NAME_LINE_WINDOW[0] <= tt <= NAME_LINE_WINDOW[1]:
                rep.soft(sid, f"position: name line at about {mmss(tt)} (target {mmss(NAME_LINE_WINDOW[0])} to {mmss(NAME_LINE_WINDOW[1])})")

    if not name_found:
        rep.warn("script", f"name line not found: \"{NAME_LINE}.\"")
    if len(full_host_secs) > FULL_HOST_MAX_SECTIONS:
        rep.err("script", f"full-host in {len(full_host_secs)} sections ({', '.join(full_host_secs)}); max {FULL_HOST_MAX_SECTIONS}")
    npause = sum(len(s["pause"]) for s in secs)
    if npause > MAX_PAUSES:
        rep.warn("script", f"{npause} pauses (max {MAX_PAUSES})")
    nnat = sum(1 for s in secs if s["natsound_after"])
    if nnat > MAX_NATSOUND:
        rep.warn("script", f"{nnat} nat-sound breaks (max {MAX_NATSOUND})")

    # ---- paste text, parts, pause lines
    paste_secs, pause_lines = [], []
    for s in secs:
        t, spans = s["spoken"], word_spans(s["spoken"])
        inserts = []
        for p in s["pause"]:
            r = find_anchor(t, p["after"])
            if not r:
                continue
            last = r[1]
            ctx = " ".join(clean_word(m.group()) for m in spans[max(0, last - 3):last + 1])
            pause_lines.append(f'after "{ctx}" {fmt_sec(p["sec"])}s')
            inserts.append((spans[last].end(), f' <break time="{fmt_sec(p["sec"])}s"/>'))
        if break_tags:
            for at, tag in sorted(inserts, reverse=True):
                t = t[:at] + tag + t[at:]
        paste_secs.append(t)
    if not break_tags:
        for line in pause_lines:
            ctx = norm_tokens(line.split('"')[1])
            if count_seq(all_tokens, ctx) > 1:
                rep.warn("pauses", f"{line} matches more than one place; anchor on longer words")
    parts, cur = [], []
    for t in (paste_secs if "--parts" in sys.argv else []):          # one script by default (owner, 4 Nov)
        if cur and len("\n\n".join(cur + [t])) > PART_LIMIT:
            parts.append(cur)
            cur = [t]
        else:
            cur.append(t)
    if cur:
        parts.append(cur)
    part_texts = ["\n\n".join(p) for p in parts]
    for k, pt in enumerate(part_texts, 1):
        if len(pt) > PART_LIMIT:
            rep.err(f"part{k:02d}", f"{len(pt)} chars (max {PART_LIMIT}); one section is too long to fit a part")

    model = {"fm": fm, "secs": secs, "wpm": wpm, "target": target, "total": total, "start_w": start_w,
             "paste": "\n\n".join(paste_secs), "parts": part_texts, "pause_lines": pause_lines,
             "break_tags": break_tags, "sample": sample}
    return rep, model


# ---------------------------------------------------------------- output
def sections_json(model):
    fm = model["fm"]
    out = {"episode": fm.get("episode"), "as_of": fm.get("as_of"), "ticker_updated": fm.get("ticker_updated"),
           "cta_copy": fm.get("cta_copy") or {}, "sections": []}
    for s in model["secs"]:
        out["sections"].append({k: s[k] for k in ("id", "title", "layout", "strap", "ticker", "visual", "cta",
                                                 "natsound_after", "pause", "cue", "spoken", "words")})
    return out


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text if text.endswith("\n") or not text else text + "\n")


def build(ep, model):
    sd = os.path.join(ep, "script")
    for old in glob.glob(os.path.join(sd, "heygen_paste_part*.txt")):
        os.remove(old)
    written = []
    write(os.path.join(sd, "heygen_paste.txt"), model["paste"])
    written.append(("heygen_paste.txt", f"{len(model['paste']):,} chars"))
    for k, pt in enumerate(model["parts"], 1):
        name = f"heygen_paste_part{k:02d}.txt"
        write(os.path.join(sd, name), pt)
        written.append((name, f"{len(pt):,} chars"))
    pp = os.path.join(sd, "heygen_pauses.txt")                       # one script: no separate pause list
    if os.path.exists(pp):
        os.remove(pp)
    if model["break_tags"]:
        written.append(("(break tags inline)", f"{len(model['pause_lines'])} pauses"))
    with open(os.path.join(sd, "sections.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(sections_json(model), fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    written.append(("sections.json", f"{len(model['secs'])} sections"))
    return written


def print_report(ep, rep, model, mode):
    print(f"Carver script {mode}: {os.path.join(ep, 'script', 'script.md')}" + ("  [--demo]" if rep.demo else ""))
    if model:
        fm, wpm = model["fm"], model["wpm"]
        print(f"episode {fm.get('episode')} | {'SAMPLE | ' if model['sample'] else ''}{wpm:g} wpm | "
              f"target {model['target']} words | break_tags {str(model['break_tags']).lower()}")
        print(f"  {'ID':<4}{'words':>6}{'start':>7}  {'layout':<34}title")
        for s in model["secs"]:
            lay = " -> ".join(L for L, _ in (s["_segs"] or [])) or "?"
            st = model["start_w"][s["id"]] / wpm * 60
            nat = f"  +nat {s['natsound_after']['clip']} {s['natsound_after']['sec']}s" if s["natsound_after"] else ""
            print(f"  {s['id']:<4}{s['words']:>6}{mmss(st):>7}  {lay:<34}{s['title'][:44]}{nat}")
        nat_total = sum(s["natsound_after"]["sec"] for s in model["secs"] if s["natsound_after"])
        est = model["total"] / wpm * 60 + nat_total + END_TAIL_EST
        print(f"  TOTAL {model['total']} words = {mmss(model['total'] / wpm * 60)} of speech at {wpm:g} wpm"
              f" (+{nat_total:g} s nat-sound) | estimated video {mmss(est)} (cap 12:00) | one script, {len(model['paste']):,} chars")
    print(f"ERRORS ({len(rep.errors)})")
    for e in rep.errors:
        print("  " + e)
    print(f"WARNINGS ({len(rep.warnings)})")
    for w in rep.warnings:
        print("  " + w)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Lint / build a Carver script (docs/script-guide.md).")
    ap.add_argument("cmd", choices=["lint", "build"])
    ap.add_argument("episode_dir")
    ap.add_argument("--demo", action="store_true", help="template/position checks become warnings")
    a = ap.parse_args()
    ep = os.path.abspath(a.episode_dir)
    rep, model = lint(ep, a.demo)
    print_report(ep, rep, model, a.cmd)
    if rep.errors:
        print(f"RESULT: FAIL ({len(rep.errors)} errors, {len(rep.warnings)} warnings)"
              + ("; nothing written" if a.cmd == "build" else ""))
        sys.exit(1)
    if a.cmd == "build":
        print("WROTE " + os.path.join(ep, "script"))
        for name, info in build(ep, model):
            print(f"  {name:<28}{info}")
    print(f"RESULT: PASS ({len(rep.warnings)} warnings)")


if __name__ == "__main__":
    main()
