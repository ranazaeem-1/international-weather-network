"""Align the script to Glenn's HeyGen audio (faster-whisper word timestamps + sequence matching).

  python align_host.py <episode_dir> [--model medium.en]
Reads script/sections.json and host/vo.wav. Writes edit/align.json:
  sections: {S01: {start, end}}          host-clock seconds (HeyGen time)
  anchors:  {S03: {"<anchor words>": t}} first time each anchor phrase is spoken inside its section
  tokens:   [[script_token, t, matched]]
  match:    share of script tokens matched to the transcript (expect > 0.9; low values mean HeyGen skipped/changed text)
Every section start is the first spoken word of that section (minus a small lead), so cuts land on breaths.
"""
import json, re, sys, difflib
from pathlib import Path
from num2words import num2words

LEAD = 0.12


def norm_words(text):
    """lowercase word tokens; digits -> words; symbols -> words; hyphens split."""
    text = text.replace("%", " percent ").replace("&", " and ").replace("°", " degrees ")
    out = []
    for raw in re.split(r"[\s\-–—/]+", text):
        w = raw.strip().lower().strip(".,;:!?\"'()[]{}…“”‘’")
        w = w.replace("’", "'")
        if not w:
            continue
        m = re.fullmatch(r"(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d+))?(st|nd|rd|th|s)?", w)
        if m:
            n = int(m.group(1).replace(",", "")); dec = m.group(2); suf = m.group(3)
            if dec is None and suf in ("st", "nd", "rd", "th"):
                words = num2words(n, to="ordinal")
            elif dec is None and 1100 <= n <= 2099 and "," not in m.group(1):
                words = num2words(n, to="year")
            else:
                words = num2words(n) + ((" point " + " ".join(num2words(int(c)) for c in dec)) if dec else "")
            out += [t for t in re.split(r"[\s\-,]+", words) if t and t != "and"]
            continue
        m = re.fullmatch(r"(\d{1,2}):(\d{2})", w)                 # clock times 10:18 -> ten eighteen
        if m:
            h, mi = int(m.group(1)), int(m.group(2))
            out += num2words(h).split() + ([] if mi == 0 else (["oh"] if mi < 10 else []) + re.split(r"[\s\-]+", num2words(mi)))
            continue
        w = re.sub(r"[^a-z0-9']", "", w)
        if w:
            out.append(w)
    return out


def _cuda_dlls():
    """pip's nvidia-cublas-cu12 / nvidia-cudnn-cu12 put their DLLs in site-packages/nvidia/*/bin: make them loadable."""
    import importlib.util, os, glob
    spec = importlib.util.find_spec("nvidia")
    for root in (spec.submodule_search_locations if spec else []):
        for d in glob.glob(os.path.join(root, "*", "bin")):
            try:
                os.add_dll_directory(d)
            except (OSError, AttributeError):
                pass
            os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")


def transcribe(wav, model_name):
    _cuda_dlls()
    from faster_whisper import WhisperModel
    try:
        m = WhisperModel(model_name, device="cuda", compute_type="float16")
        segs, _ = m.transcribe(str(wav), language="en", word_timestamps=True, beam_size=5, condition_on_previous_text=False, vad_filter=False)
        segs = list(segs)
    except Exception as e:                                         # no CUDA runtime -> CPU
        print("CUDA whisper unavailable, CPU fallback:", str(e)[:120])
        m = WhisperModel(model_name, device="cpu", compute_type="int8")
        segs, _ = m.transcribe(str(wav), language="en", word_timestamps=True, beam_size=5, condition_on_previous_text=False, vad_filter=False)
        segs = list(segs)
    toks = []                                                      # [token, start, end] (number words share their span)
    for s in segs:
        for w in s.words:
            parts = norm_words(w.word)
            for k, p in enumerate(parts):
                a = w.start + (w.end - w.start) * k / len(parts); b = w.start + (w.end - w.start) * (k + 1) / len(parts)
                toks.append([p, a, b])
    return toks


def main():
    ep = Path(sys.argv[1]).resolve()
    model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "medium.en"
    S = json.loads((ep / "script/sections.json").read_text(encoding="utf-8"))
    secs = S["sections"]
    stoks, owner = [], []                                          # script tokens and their section index
    for i, s in enumerate(secs):
        for t in norm_words(s["spoken"]):
            stoks.append(t); owner.append(i)
    tr = transcribe(ep / "host/vo.wav", model)
    ttoks = [t[0] for t in tr]
    sm = difflib.SequenceMatcher(None, stoks, ttoks, autojunk=False)
    tmap = [None] * len(stoks)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            tmap[a + k] = b + k
    matched = sum(x is not None for x in tmap)
    # times: matched -> word start; unmatched -> interpolate between neighbours by index
    times = [tr[j][1] if j is not None else None for j in tmap]
    known = [i for i, t in enumerate(times) if t is not None]
    if not known:
        sys.exit("alignment failed: no script words found in the HeyGen audio")
    for i in range(len(times)):
        if times[i] is None:
            lo = max((k for k in known if k < i), default=None); hi = min((k for k in known if k > i), default=None)
            if lo is None:
                times[i] = times[hi]
            elif hi is None:
                times[i] = times[lo] + 0.3 * (i - lo)
            else:
                times[i] = times[lo] + (times[hi] - times[lo]) * (i - lo) / (hi - lo)
    vo_end = tr[-1][2] if tr else times[-1]
    sec_out, anchors, report = {}, {}, []
    first_idx = {}
    for i, o in enumerate(owner):
        first_idx.setdefault(o, i)
    for i, s in enumerate(secs):
        k0 = first_idx[i]
        start = 0.0 if i == 0 else max(0.0, times[k0] - LEAD)
        sec_out[s["id"]] = {"start": round(start, 3)}
        idx = [k for k, o in enumerate(owner) if o == i]
        loc = sum(tmap[k] is not None for k in idx) / max(1, len(idx))
        report.append(f"{s['id']}: start {start:7.2f}s  matched {loc:5.1%}")
        # anchors
        want = [l["at"] for l in s.get("layout", []) if l.get("at")] + [v["at"] for v in s.get("visual", []) if v.get("at")] + \
               [c["at"] for c in s.get("cta", []) if c.get("at")] + [p["after"] for p in s.get("pause", []) if p.get("after")]
        sec_tokens = [stoks[k] for k in idx]
        for phrase in want:
            pt = norm_words(phrase)
            hit = next((j for j in range(len(sec_tokens) - len(pt) + 1) if sec_tokens[j:j + len(pt)] == pt), None)
            if hit is None:
                report.append(f"  ! anchor not found in {s['id']}: {phrase!r}")
                continue
            anchors.setdefault(s["id"], {})[phrase] = round(times[idx[hit]] - 0.05, 3)
    ids = [s["id"] for s in secs]
    for a, b in zip(ids, ids[1:]):
        sec_out[a]["end"] = sec_out[b]["start"]
    sec_out[ids[-1]]["end"] = round(vo_end + 0.35, 3)
    out = {"vo_end": round(vo_end, 3), "match": round(matched / len(stoks), 4), "model": model,
           "sections": sec_out, "anchors": anchors,
           "tokens": [[stoks[i], round(times[i], 3), tmap[i] is not None] for i in range(len(stoks))]}
    (ep / "edit").mkdir(exist_ok=True)
    (ep / "edit/align.json").write_text(json.dumps(out, indent=1))
    print(f"matched {matched}/{len(stoks)} script words ({matched / len(stoks):.1%}); voice ends {vo_end:.2f}s")
    print("\n".join(report))


if __name__ == "__main__":
    main()
