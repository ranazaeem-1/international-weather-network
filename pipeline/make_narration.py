"""Generate per-segment narration (edge-tts, en-US-AndrewMultilingualNeural) + word-timed subtitles from script/narration.md."""
import asyncio, json, re, subprocess
from pathlib import Path
import edge_tts
import edge_tts.communicate as _etc
from edge_tts.constants import TRUSTED_CLIENT_TOKEN

# Since about 10 Oct 2026 the legacy Bing host answers every synthesis request with 403 (edge-tts issue #490).
# Edge itself now uses this Microsoft host with the same public token (edge-tts PR #491). Remove once edge-tts ships the fix.
_etc.WSS_URL = "wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1?Ocp-Apim-Subscription-Key=" + TRUSTED_CLIENT_TOKEN

EP = Path(__file__).resolve().parents[1]
SCRIPT = EP / "script" / "narration.md"
OUT = EP / "audio" / "narration"
VOICE = "en-US-AndrewMultilingualNeural"
RATE = "-6%"

# Pronunciation fixes applied only to the spoken text
# Pronunciation overrides. Leave EMPTY by default: write real place names in the script (18 Oct audit -
# research-voice-pronunciation-2026-10-18.md). Phonetic respellings like "Cap-ih-STRAH-no" made edge-tts spell the
# capital syllables letter by letter ("C-H-S-D-R"). Only if qa_narration.py flags a name, add ONE lowercase word with
# no hyphens or capitals (e.g. "Çiftçi": "chiftchee") and re-check it.
SAY = {
}


def _check_say():
    bad = [f"{k} -> {v}" for k, v in SAY.items() if "-" in v or re.search(r"[A-Z]{2,}", v)]
    if bad:
        raise SystemExit("SAY respellings must be one lowercase word (no hyphens / capital syllables): " + "; ".join(bad))


def segments():
    text = SCRIPT.read_text(encoding="utf8")
    for block in re.split(r"\n## ", text)[1:]:
        lines = block.split("\n")
        seg_id = lines[0].split(" ")[0]
        title = lines[0].split("—", 1)[1].split("[")[0].strip() if "—" in lines[0] else lines[0]
        body = [l for l in lines[1:] if l.strip() and not l.startswith("Clips:") and not l.startswith("---")]
        yield seg_id, title, "\n\n".join(body)


async def tts(seg_id, text):
    spoken = text
    for k, v in SAY.items():
        spoken = re.sub(rf"\b{re.escape(k)}\b", v, spoken)
    comm = edge_tts.Communicate(spoken, VOICE, rate=RATE, boundary="SentenceBoundary")
    sub = edge_tts.SubMaker()
    with open(OUT / f"{seg_id}.mp3", "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                sub.feed(chunk)
    (OUT / f"{seg_id}.srt").write_text(sub.get_srt(), encoding="utf8")


def duration(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]).strip())


async def main():
    _check_say()
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for seg_id, title, body in segments():
        # GWN style: narration in short parts, real clips with sound between them -> one file per paragraph
        parts = []
        for k, para in enumerate(p for p in body.split("\n\n") if p.strip()):
            pid = f"{seg_id}_{k}"
            done = OUT / f"{pid}.mp3"
            for attempt in range(10):   # edge-tts drops or hangs connections now and then
                if done.exists() and done.stat().st_size > 2000 and (OUT / f"{pid}.ok").exists() \
                        and (OUT / f"{pid}.ok").read_text(encoding="utf8") == para:
                    break
                try:
                    await asyncio.wait_for(tts(pid, para), timeout=60)
                    (OUT / f"{pid}.ok").write_text(para, encoding="utf8")
                    break
                except Exception as e:
                    print('retry', pid, type(e).__name__, flush=True)
                    await asyncio.sleep(3 + 3 * attempt)
            else:
                raise SystemExit('tts failed for ' + pid)
            parts.append({"id": pid, "duration": round(duration(OUT / f"{pid}.mp3"), 2)})
        d = sum(p["duration"] for p in parts)
        manifest.append({"id": seg_id, "title": title, "duration": round(d, 2), "words": len(body.split()), "parts": parts})
        safe_title = title.encode('ascii', 'replace').decode('ascii')
        print(f"{seg_id:5s} {d:6.1f}s  {len(parts)} parts  {safe_title}")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf8")
    print("TOTAL %.1fs (%.2f min)" % (sum(m["duration"] for m in manifest), sum(m["duration"] for m in manifest) / 60))


if __name__ == "__main__":
    asyncio.run(main())
