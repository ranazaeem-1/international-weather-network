"""Generate per-segment narration + subtitles from script/narration.md.

Voice comes from <project>/voices/voices.json ("default", or IWN_VOICE=<name>):
  gwn    -> ElevenLabs (key in voices/elevenlabs.env), saved but unused (no key)
  andrew -> edge-tts en-US-AndrewMultilingualNeural -6% (default, user 3 Nov 2026)
"""
import asyncio, base64, json, os, re, subprocess, urllib.request, urllib.error
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


def _voices_dir():
    for p in Path(__file__).resolve().parents:
        if (p / "voices" / "voices.json").exists():
            return p / "voices"
    return None


VDIR = _voices_dir()
VCFG = json.loads((VDIR / "voices.json").read_text(encoding="utf8")) if VDIR else {"default": "andrew", "voices": {}}
VNAME = os.environ.get("IWN_VOICE") or VCFG.get("default", "andrew")
V = VCFG["voices"].get(VNAME, {"engine": "edge"})
ENGINE = V.get("engine", "edge")
if ENGINE == "edge":
    VOICE, RATE = V.get("voice", VOICE), V.get("rate", RATE)
CACHE_TAG = "" if ENGINE == "edge" else f"[{VNAME}:{V.get('model_id')}:{json.dumps(V.get('voice_settings'), sort_keys=True)}]"


def _eleven_env():
    env = {}
    f = VDIR / "elevenlabs.env" if VDIR else None
    if f and f.exists():
        for line in f.read_text(encoding="utf8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    key = os.environ.get("ELEVENLABS_API_KEY") or env.get("ELEVENLABS_API_KEY")
    if not key:
        raise SystemExit(f"No ElevenLabs key: put ELEVENLABS_API_KEY=... in {f} (or run with IWN_VOICE=andrew).")
    return key, (env.get("VOICE_ID") or V.get("voice_id") or "")


def _eleven_req(url, key, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"xi-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf8", "replace")[:400]
        if e.code in (401, 402, 403, 422):   # bad key / no credits / bad request: retrying won't help
            raise SystemExit(f"ElevenLabs {e.code}: {msg}")
        raise RuntimeError(f"ElevenLabs {e.code}: {msg}")


_EL = {}


def _eleven_voice():
    if not _EL:
        key, vid = _eleven_env()
        if not vid:
            want = V.get("voice_name_contains", VNAME).lower()
            vs = _eleven_req("https://api.elevenlabs.io/v1/voices", key).get("voices", [])
            hits = [v for v in vs if want in v.get("name", "").lower()]
            if len(hits) != 1:
                raise SystemExit(f"Found {len(hits)} ElevenLabs voices named like '{want}': "
                                 + ", ".join(f"{v['name']}={v['voice_id']}" for v in (hits or vs)[:15])
                                 + f". Set VOICE_ID in {VDIR / 'elevenlabs.env'}.")
            vid = hits[0]["voice_id"]
            print(f"ElevenLabs voice: {hits[0]['name']} ({vid})", flush=True)
        _EL.update(key=key, vid=vid)
    return _EL["key"], _EL["vid"]


def _srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def _sentence_srt(chars, starts, ends):
    """Sentence-level SRT from ElevenLabs character alignment (same granularity as edge SentenceBoundary)."""
    cues, buf, t0 = [], "", None
    for i, c in enumerate(chars):
        if t0 is None and not c.isspace():
            t0 = starts[i]
        buf += c
        nxt = chars[i + 1] if i + 1 < len(chars) else " "
        if (c in ".!?" and nxt.isspace()) or i == len(chars) - 1:
            if buf.strip():
                cues.append((t0, ends[i], buf.strip()))
            buf, t0 = "", None
    return "\n".join(f"{n}\n{_srt_time(a)} --> {_srt_time(b)}\n{t}\n" for n, (a, b, t) in enumerate(cues, 1))


def tts_eleven(seg_id, text):
    key, vid = _eleven_voice()
    body = {"text": text, "model_id": V.get("model_id", "eleven_v3"), "voice_settings": V.get("voice_settings", {})}
    r = _eleven_req(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}/with-timestamps?output_format=mp3_44100_128", key, body)
    (OUT / f"{seg_id}.mp3").write_bytes(base64.b64decode(r["audio_base64"]))
    al = r.get("normalized_alignment") or r.get("alignment") or {}
    srt = _sentence_srt(al.get("characters", []), al.get("character_start_times_seconds", []),
                        al.get("character_end_times_seconds", [])) if al else ""
    (OUT / f"{seg_id}.srt").write_text(srt, encoding="utf8")

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


def _spoken(text):
    for k, v in SAY.items():
        text = re.sub(rf"\b{re.escape(k)}\b", v, text)
    return text


async def tts(seg_id, text):
    spoken = _spoken(text)
    if ENGINE == "elevenlabs":
        return await asyncio.to_thread(tts_eleven, seg_id, spoken)
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
    print(f"Voice: {VNAME} ({ENGINE}{', ' + V.get('model_id', '') if ENGINE != 'edge' else ', ' + VOICE + ' ' + RATE})", flush=True)
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
                        and (OUT / f"{pid}.ok").read_text(encoding="utf8") == CACHE_TAG + _spoken(para):   # cache key includes SAY + voice, so a fix or voice switch regenerates
                    break
                try:
                    await asyncio.wait_for(tts(pid, para), timeout=60 if ENGINE == "edge" else 180)
                    (OUT / f"{pid}.ok").write_text(CACHE_TAG + _spoken(para), encoding="utf8")
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
