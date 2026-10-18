"""Pronunciation / accuracy check for the generated narration (18 Oct 2026, after viewer complaints).

    python qa_narration.py            # all parts in audio/narration/
    python qa_narration.py S03 S07    # only some chapters
    python qa_narration.py --lang es  # Spanish episodes (multilingual Whisper model, language="es")

Transcribes every narration mp3 with faster-whisper and compares it with the script text. It lists
  - proper nouns (capitalised words that are not sentence-initial) that the transcript does not contain, and
  - any other word-level differences above a threshold,
so mispronounced place names are caught before the draft is built. Writes audio/narration/qa_report.txt.
Fix a flagged name by rewriting the sentence or, as a last resort, a lowercase one-word SAY respelling.
"""
import difflib
import re
import sys
import unicodedata
from pathlib import Path

from faster_whisper import WhisperModel

EP = Path(__file__).resolve().parents[1]
OUT = EP / "audio" / "narration"
LANG = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "en"
MODEL = ("small" if "--fast" in sys.argv else "medium") + (".en" if LANG == "en" else "")


def norm(w):
    w = unicodedata.normalize("NFKD", w)
    w = "".join(ch for ch in w if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", w.lower())


def words(s):
    return [norm(w) for w in s.split() if norm(w)]


NUMBER_WORDS = set("one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen "
                   "eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million".split())


def proper_nouns(text):
    out = []
    for sent in re.split(r"(?<=[.!?])\s+", text):
        toks = sent.split()
        for i, tok in enumerate(toks):
            if i > 0 and tok[:1].isupper() and norm(tok) and norm(tok) not in NUMBER_WORDS:
                out.append(tok.strip(",.;:!?\"'()"))
    return out


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("--") and a != LANG]
    model = WhisperModel(MODEL, device="cpu", compute_type="int8")
    lines, flagged = [], 0
    for ok in sorted(OUT.glob("S*_*.ok")):
        pid = ok.stem
        if only and pid.split("_")[0] not in only:
            continue
        script = ok.read_text(encoding="utf8")
        segs, _ = model.transcribe(str(OUT / f"{pid}.mp3"), language=LANG, beam_size=5)
        heard = " ".join(s.text for s in segs)
        hw = set(words(heard))
        missing = []
        for name in proper_nouns(script):
            parts = [p for p in words(name) if len(p) > 2]
            if parts and not all(any(difflib.SequenceMatcher(None, p, h).ratio() >= 0.8 for h in hw) for p in parts):
                missing.append(name)
        sim = difflib.SequenceMatcher(None, words(script), words(heard)).ratio()
        if missing or sim < 0.9:
            flagged += 1
            lines.append(f"{pid}  match {sim:.2f}  names not heard: {', '.join(dict.fromkeys(missing)) or '-'}\n    heard: {heard.strip()}")
    report = "\n".join(lines) or "all parts OK"
    (OUT / "qa_report.txt").write_text(report, encoding="utf8")
    print(report.encode("ascii", "replace").decode())
    print(f"\n{flagged} part(s) flagged -> {OUT / 'qa_report.txt'}")


if __name__ == "__main__":
    main()
