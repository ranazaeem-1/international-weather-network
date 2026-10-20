# IWN Video Production Workflow

International Weather Network · Working production guide · Updated 15 October 2026 (GWN sourcing, 13–15 min runtime, clean footage protocol)

## 0. Current format rules — 18 October 2026 (user decision after the GWN comparison; overrides older numbers below)

- **Shots 11–13 s** (pipeline default `max_shot=13`, render.Pool aims for ~12 s). Slice clips 12–30 s long when sourcing.
- **No cut shorter than 4 s** (`min_shot=4`): clips under 4 s are left out, short gaps are absorbed into the neighbouring shot, and the chapter lead-in continues the first shot instead of adding its own cut. 2–3 s flashes are not allowed.
- **Clips shorter than 11 s are used whole, uncut** (start to end; render.Pool never trims or starts them midway). They are welcome when sourcing, so do not discard good 6–10 s clips.
- **Cold open ~20 s** (`E.cold_open(..., seconds=20)` default): the 1–2 strongest clips with their real sound.
- **Clip audio: mute ONLY music** (user, 18 Oct). Speech in clips stays audible: eyewitnesses, reactions, people talking. Never replace or strip a clip's audio track when slicing. In `research/sources.csv`, log `sound: natural`, `speech` or `music`. In `gen_edl.py`, use `MUTED = E.muted_from_sources(EP)`, which mutes only clips logged with music. Picture rules are unchanged (no anchors, reporters on camera, TV bugs or burned-in text).
- **Narration starts right after the cold open** with a line that anchors the footage ("The video you just saw was filmed Friday in San Clemente…") plus one open loop the video answers later ("…and what forecasters expect next could be worse").
- **More narration: ~1,300–1,600 words, ~45–50 % of runtime (GWN measured 41–48 %)**, 15–17 one-paragraph chapters (see Script structure below), including the context chapters (science, history, what's next). Clip break after each chapter `tail=28`.
- **Archive footage: only for events that have NOT happened yet (user, 20 Oct 2026, revised the same day).**
  - **Upcoming or warned events:** a forecast, an approaching storm, a warning just issued. Footage of earlier events at the same place may be used, because no footage of the event exists yet. The narration must never say these pictures show the current event. Anchor the opening to the threat ("This is what the last nor'easter did to Rodanthe…"), not to "the video you just saw".
  - **Events that already happened:** only real footage of this event is used. No archive clips at all, including in history chapters.
  - **No on-screen ARCHIVE tag.**
  - **In the pipeline:** `E.build(..., event="upcoming", archive={clip: {"date": "SEP 2026"}})`. The default `event="happened"` refuses any archive clip. Log archive clips in sources.csv as `verification_status: archive <event, month year>`.
- **No fixed runtime (user, 20 Oct 2026).** The length follows the footage fetched: lots of verified footage gives a longer video, thin footage a shorter one, never padded with repeats. Use `E.build(..., tail="auto")`, which sizes each chapter's clip break to the distinct footage in the library (8–45 s): roughly runtime ≈ distinct footage minutes, ×1.25 when 2 uses are allowed. Example: 26.8 min of footage → about 20 min; 9 min → about 10 min.
- **iwn watermark on horizontal footage (user, 20 Oct 2026).** Every horizontal clip (16:9 after crops, no side bars) gets the iwn logo top right, at 160 px with a soft shadow; ES videos get the capital IWN. Vertical clips already carry the logo tile in their blurred side bars. `build_capcut.py` adds it automatically on a `watermark` track and creates `graphics/corner_watermark.png` on first use. Nothing is re-encoded.
- Measured reference: `gwn-vs-iwn-comparison-2026-10-18.md`.

### Narration voice and pronunciation (18 Oct 2026; audit in `research-voice-pronunciation-2026-10-18.md`)
- **No phonetic respellings.** Keep `SAY` in `make_narration.py` empty and write the real names in the script. Respellings like "Cap-ih-STRAH-no" made edge-tts spell capital syllables letter by letter. YouTube's captions showed "San Juan Caphsdn No" and "BH Loan Road". `make_narration.py` now refuses respellings with hyphens or capital syllables.
- **Run `python qa_narration.py` after every narration** (faster-whisper medium.en; `--fast` uses small.en). It flags proper nouns the voice didn't say recognisably. Fix them by rewording, or as a last resort with a one-word lowercase `SAY` entry, then re-run.
- GWN's voice was not identified: it matched none of 47 tested voices (edge-tts, ElevenLabs premade, OpenAI). It is higher-pitched (~135 Hz) and faster (~169 wpm) than Andrew Multilingual. Proper phoneme control would need paid Azure Speech (same Andrew voice, free tier available) or ElevenLabs.

### Script structure — GWN model (18 Oct 2026; full analysis in `research-gwn-script-structure-2026-10-18.md`)
- **One paragraph per chapter** (55–90 words, 20–30 s spoken), then **one clip break of 25–30 s** (`tail=28`). 15–17 chapters, ~1,300–1,600 words. Never split a chapter into sentence fragments.
- **Opening chapter (S01, after the ~20 s cold open):** point at the footage ("The video you just saw was filmed …"), then place + date, what happened with a speed/scale number, the human stakes number, one widening line, and one honest open question that a later fact answers ("Stay with us, because …").
- **Arc for fires:** start and why the place matters → growth by clock time → homes → evacuations (explain what the order means) → the firefight → **the science (e.g. Santa Ana winds) and history at about 30–45 % of runtime** → roads/power/air → other fires (distance + direction) → official response → what's next → an "As of [time, date]" recap. Floods: same skeleton plus victim chapters, with the "why it got so bad" chapter late as the answer to the opening question.
- **Hand-offs, not teasers:** end each paragraph by naming the next subject plainly; start the next paragraph on that subject. No "And it came at a cost." style cliffhangers, and no promising more than the facts deliver.
- **Language:** ~14-word sentences, plain verbs, define terms right away ("zero containment means…"), attribute every number to a source and time, use relatable comparisons. Do not read zone codes or addresses out as lists.
- **Footage:** mention the footage only in the opening; write the rest so any clip of the event fits. Narrate the right fire over the right fire's footage, and never credit one fire's impacts (e.g. an I-5 closure) to another.
- **Spoken CTAs:** never join them to the story with "because". S01 ends with "Stay with us, because…". One mid-video line restates where, what and the latest number, then asks for the subscribe. One closing line comes after the recap. On-screen pills and tickers carry the rest.

## 1. Purpose and default brief

Produce original, factual weather-news videos using verified reporting, relevant footage, and the approved IWN identity. GWN is a reference for format, clean sourcing, and pacing; its scripts, edits, and graphics are not production assets.

- **Runtime is not fixed (20 Oct 2026, see §0):** it follows the footage fetched. Older guidance: **13–15 minutes was the minimum baseline** (780–900 seconds). When sufficient verified footage, damage documentation, and meteorological developments support it, extend the duration to **15–20+ minutes** (matching the depth of long-format coverage on channels like GWN).
- **Narration duration**: superseded by §0 (18 Oct). Was: since 17 Oct 2026, +15% (~1,100 words / ~6.5 min across 13 blocks). Previously ~800–1,000 words total across 14–18 concise narration blocks (~40–55 words / 15–20s spoken each, totalling ~5–6 minutes of voiceover). If extending past 15 minutes, add 2–4 additional narration blocks.
- **Clean footage requirement**: Absolute zero tolerance for news anchors, TV network badges/chyrons, third-party watermarks, or social media emojis/stickers.
- Deliver a finished video, thumbnail, upload copy, source register, and editable project.
- Work locally by default. Uploading or publishing requires a user instruction.

## 2. Approved IWN identity

Use the existing assets in `iwn-brand-kit/` and the decisions in `iwn-brand-kit/source/brand-decisions.json`.

- Video branding: use existing approved motion assets and channel-language settings below.
- Thumbnail authority: root `AGENTS.md`, the three references in `iwn-brand-kit/approved-thumbnail-designs/`, and `iwn-brand-kit/thumbnail-workflow.md`. These supersede retired thumbnail directions in older brand-decision files and prompts.
- Ask for Design 1, 2 or 3 on a new thumbnail request unless already specified. No single design supersedes the other two.
- Designs 1/2 retain approved red packaging and English headlines; Design 3 uses yellow packaging and Spanish main headlines. Preserve each reference's logo, corners and badge wording.
- Headline treatment: huge heavy black type on the approved white bordered panel, with a short event-supported place-plus-action hook.
- Scene direction, updated 17 October: bright detailed exposure, readable night scenes, slightly elevated oblique aerial views, broader context and one clear focal subject. Avoid dark moody grading as the default.
- Do not use the retired `thumbnail-storm-demo` or `thumbnail-overlay-editable` layouts for new uploads.
- The New Mexico demo thumbnail is AI-adapted concept artwork, not verified documentary footage or a cleared reusable source image.

Existing motion assets:

| Component | Editable source | Transparent export |
|---|---|---|
| Subscribe animation — English channel (Independent Weather Network) | `pipeline/make_subscribe.py` | `motion/subscribe-en-transparent.mov` |
| Subscribe animation — Spanish channel (Instant Weather Network) | `pipeline/make_subscribe.py` | `motion/subscribe-es-transparent.mov` |
| Subscribe animation — old "International Weather Network" master (do not use in new videos) | `motion/subscribe.tsrct` | `motion/subscribe-transparent.mov` |
| News ticker | `motion/ticker.tsrct` | `motion/ticker-transparent.mov` |
| Broadcast lower-third and location/date | `motion/broadcast.tsrct` | `motion/broadcast-transparent.mov` |

### Channel names (from 16 October 2026)

The English and Spanish channels now have different names. Everything else (logo, colours, lower-thirds, ticker, layout) stays the same.

| | English channel | Spanish channel |
|---|---|---|
| Name in the subscribe animation | **Independent Weather Network** | **Instant Weather Network** |
| Subscribe file | `motion/subscribe-en-transparent.mov` | `motion/subscribe-es-transparent.mov` |
| Background / side-bar watermark | lowercase `iwn` logo (unchanged) | **`IWN` in capital letters** |
| Pipeline setting | `E.build(..., lang="en")` (default) · `make_watermark.py <graphics>` | `E.build(..., lang="es")` · `make_watermark.py <graphics> --lang es` |

The old "International Weather Network" subscribe animation is no longer used.

All paths in this table are relative to `iwn-brand-kit/`. Preview MP4s are available alongside the motion files. Replace sample copy and re-render any affected graphics for each episode.

## 3. Intake and production setup

Start with a topic, location, and reporting cutoff. Ask only for information that cannot reasonably be inferred, and continue independent research while awaiting answers.

Record:

- Event and geographic scope.
- Reporting cutoff, with timezone.
- Target runtime and intended publication date.
- Language, narration voice, and delivery style.
- Available footage subscriptions, permissions, and any spending limit.
- Output requirements; default to 1920 × 1080, 16:9.

Inspect available editing, narration, and rendering tools before promising a turnaround. A narration service or licensed voice must actually be available; never assume that an account or paid service is connected. Reuse approved choices on later episodes rather than asking again.

Create an episode folder:

```text
episodes/YYYY-MM-DD-topic/
  brief.md
  research/
    facts.csv
    sources.csv
  footage/
    originals/
    proxies/
  audio/
  script/
    narration.md
    shot-list.csv
  graphics/
  project/
  exports/
  delivery/
    upload-copy.md
    review-notes.md
```

Keep originals intact. Use descriptive filenames and preserve original source identifiers.

## 4. Research and verify the story

1. Establish the event timeline and affected places.
2. Read primary weather and emergency-management updates.
3. Cross-check consequential claims such as deaths, missing people, evacuation orders, dam status, and road closures against authoritative reporting.
4. Distinguish observed conditions, forecasts, warnings, and eyewitness claims.
5. Record each important fact with its source, publication time, event time, and verification status.
6. Recheck changing claims before final export. Include an “as of” time in the narration or graphics where needed.

Suggested `facts.csv` fields:

```text
fact_id,claim,location,event_time,source_url,published_at,checked_at,status,notes
```

Do not infer the location, date, severity, or cause of an event from dramatic imagery alone. If sources disagree, resolve the discrepancy or describe the uncertainty explicitly.

## 5. Find footage and trace its origin (Clean Sourcing Protocol)

GWN's visual signature is **clean, raw, high-impact reality**: no watermarks, no burned-in text, no emojis, no TV station badges, and zero news anchors. Our previous episodes failed because we downloaded broadcast news packages off YouTube (Meganoticias, ADN, TVN, El Comercio) or repost accounts, which burned in TV chyrons, station logos, and anchor desk talking heads.

### The Zero-Tolerance Clean Visual Standard
1. **Zero News Anchors & Studio Sets**: Never include frames where a reporter holds a microphone, an anchor speaks from a desk, or a TV crew films themselves. Bystander action and atmospheric footage only.
2. **Zero TV Network Badges & Chyrons**: Absolutely no third-party broadcast logos (e.g. Meganoticias, TVN, ADN, CNN, FOX, CBS corner bugs) or lower-third breaking news bars ("🔴 ALERTA ROJA", "ÚLTIMO MINUTO").
3. **Zero Platform Watermarks & Handles**: No bouncing TikTok watermarks, no Instagram username stamps, no YouTube Shorts icons.
4. **Zero Burned-in Emojis & Creator Overlays**: Reject or crop out clips with "😱😱", "WAIT FOR IT", reaction stickers, or hardcoded TikTok auto-captions.

---

### The 5-Pillar Clean Sourcing System (How GWN Actually Sources)

#### Pillar 1: TV News is an Index, NOT a Video Source
- Watch regional TV news coverage (ABC, 7News, 9News, Meganoticias, ERT, KOSA, etc.) **only to identify what happened and find who filmed it**.
- Inspect the on-screen credit (e.g. *"TikTok @username"*, *"Gentileza: Name"*, *"Video: X/@handle"*, *"Supplied"*), or read the article's embedded post link.
- **Never cut footage out of a TV newscast with the station bug.** Trace the credit directly to the original upload.

#### Pillar 2: Native Social Tracing (Twitter/X & Facebook Priority)
- Search directly on **Twitter/X** and **Facebook** in the native local language (e.g. Spanish for Chile: `#TormentaSantiago`, `Terminal Sur`, `Alameda granizo`, `Río Mapocho`, `Estación Central`).
- **Why X and Facebook?** Raw video uploads on Twitter/X and Facebook are the cleanest on the web: they do not burn in bouncing logos, watermarks, or user handles on the video stream.
- Search by location geotags, local transit stations, street intersections, and local municipal community groups.

#### Pillar 3: Clean, Watermark-Free Extraction for TikTok & Instagram
- When a valuable eyewitness clip exists only on TikTok or Instagram Reels:
  - **Never use screen recordings or standard app downloads** (which burn in user handles and bouncing logos).
  - Download the clean raw stream via watermark-free extractors (e.g., `tikwm`, `cobalt.tools`, `snaptik`, or `yt-dlp` direct stream extraction).

#### Pillar 4: Official Clean Feeds & Meteorological Data
- **Doppler Radar Loops**: Official NWS, NOAA, DMC, or BOM radar loops (clean GIFs/MP4s) showing rotation, wind velocity couplets, and precipitation cores.
- **Satellite Animations**: High-resolution GOES, EUMETSAT, or Zoom Earth clean satellite loops.
- **Department of Transportation / Traffic Cameras**: Highway webcams (State DOT / MDT live cams) during snowstorms, pass closures, and road flooding.
- **Civil Protection & Emergency Drone Surveys**: Official SENAPRED, Fire Department, or Police footage. These are broadcast quality, verified, and completely unbranded.

#### Pillar 5: Framing & Defensive Cropping (CapCut / FFmpeg)
- **Top/Bottom Text Stripping**: If an eyewitness placed text or stickers at the top or bottom of a vertical video, apply CapCut/FFmpeg crop to strip the top 15% and bottom 15% (`crop_top`, `crop_bottom`), leaving only the clean action area.
- **Corner Bug Punch-in**: If a rare, irreplaceable clip has a small network bug in the corner, apply a 10–15% zoom punch-in (`crop` settings in `edl.json`) to push the logo outside the active 1920×1080 canvas.
- **Visual Crop Check**: Run `python check_crops.py` from the episode project folder to generate a visual contact sheet of all clips before assembling. Any clip with visible station bugs, emojis, or talking heads must be re-cropped or replaced.

---

### Mandatory Video Quality & Bitrate Standards

A major defect in earlier episodes was pixelated, blurry, low-bitrate footage (300–800 kbps). This was caused by two technical mistakes that must never be repeated:

1. **The Downloader Height Bug on Vertical Video**:
   - In past scripts, `-f "bv*[height<=1080][ext=mp4]+ba"` was used.
   - On vertical videos (9:16), the height is **1920**, not 1080! Restricting `height<=1080` disqualified full HD ($1080 \times 1920$) and 720p ($720 \times 1280$), forcing yt-dlp to download washed-out $608 \times 1080$ or $480 \times 854$ streams at ~400 kbps!
   - Furthermore, `[ext=mp4]` rejected YouTube's highest-quality VP9/AV1 streams, which have **4–6× higher bitrates (3.5–5.5 Mbps)**.
   - **MANDATORY Command**: Always download with:
     ```bash
     yt-dlp -f "bv*+ba/b" --merge-output-format mp4 "<URL>"
     ```
     FFmpeg automatically merges the highest-bitrate video stream into an MP4 container with zero quality loss.

2. **First-Generation Source Rule**:
   - Never download screen recordings or third-hand compilation videos. Every re-encode (WhatsApp $\rightarrow$ TikTok $\rightarrow$ YouTube $\rightarrow$ CapCut) compounds macroblocking and destroys water/rain textures.
   - Trace back to the original Twitter/X or Facebook upload, which retains original camera bitrates.

3. **Minimum Resolution Standard**:
   - **Horizontal video**: 1080p ($1920 \times 1080$) standard; minimum 720p ($1280 \times 720$).
   - **Vertical video**: 1080p ($1080 \times 1920$) standard; minimum 720p ($720 \times 1280$).
   - Reject sub-720p files unless they capture an irreplaceable, verified moment of historical significance.

4. **Master Export Settings**:
   - CapCut Draft Export: 1080p (1920×1080), 30 fps, Codec H.264, Bitrate set to **"Higher" (15–20 Mbps)**.
   - FFmpeg headless render: Use `-preset medium` and `-crf 16` (avoids motion-blur blockiness on heavy rain and fast currents).

---

### Verifying and Logging Clips
For each clip:
1. Identify the earliest credible upload and verify date and location frame-by-frame.
2. Check for old recycled footage (e.g. past floods from previous years). Old footage may be used as **archive** only when the video is about an event that has not happened yet (a forecast or warning, §0), logged as `archive <event, month year>`. It is never passed off as the current event, and it is never used for events that already happened.
3. Confirm audio is authentic (run `python audio_scan.py` to ensure no copyrighted background music).
4. Record rights/credit in `research/sources.csv`. Apply the official on-screen lower-third source attribution tag (`build_source_tag.py`, §9) to eyewitness clips, and list full institutional citations in the YouTube description `SOURCES` list.

## 6. Footage register and reuse library

Suggested `sources.csv` fields:

```text
clip_id,filename,original_url,recorder,rights_contact,location,recorded_at,uploaded_at,duration,resolution,verification_status,permission_status,permission_record,required_credit,restrictions,used_in,notes
```

Build an event-specific library. Related updates can reuse relevant clips when the permission allows it, while adding new footage and information as available.

- Track episodes and time ranges in which each clip appears.
- Keep earlier footage dated and clearly contextualized; never present it as a new live scene.
- A missing match in a sampled comparison does not prove a clip is newly recorded.
- Avoid excessive repetition within an episode.
- Do not mirror footage to disguise reuse; orientation can matter to geographic accuracy.
- Use the new report's information to justify another episode, rather than merely changing its title.

Our sampled GWN comparison confirmed repeated footage across multiple New Mexico uploads, including changed crops and mirrored shots. It did not establish a channel-wide reuse percentage or prove that every upload uses the same clips.

## 7. Script and shot plan

Write an original script from the fact register. Do not paraphrase another channel scene by scene.

### Format: standard narration duration, 13–15 minute runtime (GWN pacing)

The voiceover maintains our proven, concise format: **~800–1,000 words total** (~5–6 minutes spoken voiceover). To reach the **13–15 minute runtime** (780–900 seconds), the video uses longer, high-energy natural sound breaks (30–45 seconds) and a gripping cold open (45–60 seconds). Clean eyewitness footage carries the story; the narration anchors each development.

- **Narration word count**: ~800–1,000 words total across **14–18 blocks**, each **15–20 seconds / ~40–55 words**. One block = one paragraph in `script/narration.md`.
- **Every block ends on a hook line** pulling directly into the subsequent clip break (e.g. *"But down along the avenue, the real destruction was only beginning."* / *"And emergency crews were facing their most critical test of the night."*).
- **Shot pacing**: see §0 — shots 11–13 s, clips under 11 s whole, no cut under 4 s.
- **Between blocks**: sound breaks of 12–13 s (one long shot each) with full authentic natural sound.
- **Cold open**: ~20 s, the 1–2 strongest clips with their real sound and eyewitness reactions (`"clips_only": true` in `edl.json`).
- **Dynamic Motion Graphics & Maps**: Layer animated Doppler radar loops (Windy, NOAA, local meteorological radar), satellite loops, and geographic locator callouts over the timeline to show substantive editorial modification.
- One chapter per block or pair of blocks; chapter titles in news style (e.g., *"Tornado Hits Terminal Sur"*, *"EMERGENCY — Mapocho River Surges"*, *"RADAR — Convective Supercell Mechanics"*).

Suggested 13–15 minute 3-Act shape:

| Act / Part | Blocks | Est. Duration | Editorial & Footage Focus |
|---|---|---|---|
| **Cold open** | None (pure footage) | 0:45–1:00 | Strongest raw eyewitness clips with full authentic sound |
| **Act 1: The Event & Immediate Impacts** | S01–S05 (5 blocks) | ~4:00–4:30 | First warning, touchdown/surge moment, initial shock, primary locations |
| **Act 2: Damage, Rescues & Infrastructure** | S06–S12 (7 blocks) | ~5:30–6:30 | Structural damage, stranded commuters, blackouts, drainage collapse, emergency responses |
| **Act 3: Meteorology, Radar & Outlook** | S13–S16 (4 blocks) | ~3:00–3:30 | Doppler radar velocity couplets, atmospheric mechanism, alerts, upcoming forecast |
| **Close** | S17 (1 block) | ~0:30–0:45 | Reporting cutoff + clean IWN subscribe lower-third |

Runtime = narration (~5.5 min at ~145 wpm) + breaks (~8–9 min) + cold open (~1 min) = **~13:30–15:00 minutes (minimum floor)**. When abundant verified footage is available, scale to **15–20+ minutes** by adding chapter blocks. Measure generated audio with `qa_narration.py`; adjust break durations in `edl.json` to hit the intended runtime.

For each segment, prepare:

```text
segment_id,start_time,duration,narration,fact_ids,clip_ids,source_in,source_out,on_screen_text,credit,audio_notes
```

Do not imply that a specific rescue, damage report, or locality is shown unless the selected footage supports that association. Label illustrative maps or simulations appropriately.

## 8. Narration and audio

1. Approved voice: edge-tts `en-US-AndrewMultilingualNeural` at rate −6% (free; chosen by the user on 8 Oct 2026, replacing `en-US-AvaNeural`). Generate with `project/make_narration.py` — one MP3 + SRT per block.
2. Check pronunciations of towns, rivers, people, and agencies (respellings go in the `SAY` table of `make_narration.py`).
3. Run `project/qa_narration.py` — transcribes each block and diffs it against the script; fix any omissions or misread numbers.
4. **No music.** The video uses narration plus the clips' own sound only.
5. **Scan every clip's audio for music** with `project/audio_scan.py` (lyrics via Whisper + tonality/beat measures). Clips with songs or beats are listed under `muted` in `edl.json` — they may play silently under narration but are never used as sound breaks. When unsure, mute.
6. Clip sound sits at ~12% under narration and 100% in breaks, with short fades.

As a starting mix target, aim near −14 LUFS integrated and at or below −1 dBTP true peak, then verify the actual export by measurement and listening. These are production defaults, not a claim that YouTube requires those exact values.

## 9. Edit and apply IWN graphics

1. **Footage & Visual Layers**: High-impact real footage layered with animated radar feeds (Windy, NOAA, local Doppler), satellite loops, and geographic locators to provide transformative editorial context.
2. **Mandatory Blurred Moving Background standard (GWN Visual Standard)**: 1920×1080, 30 fps. Vertical clips (9:16), square (1:1), and non-standard aspect ratio footage must **NEVER sit on flat dark charcoal bars or static frames**. They must sit centred over a dynamic, blurred, darkened copy of themselves (`boxblur=8:3`, `eq=brightness=-0.12:saturation=0.8`), with the **IWN logo watermark tiled down both blurred side bars** (`graphics/sidebar_watermark.png`, 16% opacity).
   - In `edl.json`, `"framing": "blur"` is the mandatory production default.
   - Run `python frame_all.py` before building CapCut drafts to pre-render framed shots in parallel. CapCut then automatically imports the 1080p framed footage with moving blurred sidebars.
3. **On-Screen Source Attribution**: Add clean, subtle lower-third source tags for eyewitness clips (e.g., *"Footage Source: Local Resident via X / [Location]"* or *"Source: Eyewitness via X"*). This establishes a professional newsroom editorial standard that clearly indicates transformative fair use to reviewers, rather than an uncurated clip compilation. Dedicated `source_tag` track in CapCut ensures they display cleanly without colliding with lower-thirds.
4. Per chapter: IWN lower-third + location/date pill for the first 8 s (`project/build_graphics.py`, real copy only).
5. **Tickers in every chapter** (user, 17 Oct 2026): the headline news ticker (~22 s, `ticker_len`) right after the subscribe CTA, and the CTA ticker (`graphics/cta_ticker_strip.mov`, ~12 s: subscribe / notifications / like / share / comment) in each chapter's last seconds. `edl_tools.build(..., every_chapter=True)` sets both. Never over a lower-third or the subscribe animation.
6. Subscribe CTA at every key moment: the cold open (~38 s), every chapter's first sound break, and the close. Since 17 Oct it is the bigger CTA with like + bell buttons (`pipeline/make_cta.py` -> `iwn-brand-kit/motion/subscribe-cta-<lang>-transparent.mov`, 7 s). Narration also carries short spoken CTAs (subscribe + notifications early, like/share mid, comment, and the close).
6b. **Clip repetition** (user, 17 Oct): each clip appears at most twice (3x only for clips listed as `important`). `edl_tools.build(pool=True)` makes render.Pool hand out footage video-wide, continuing each clip where it left off. Fetch enough footage: unique clean footage >= half the runtime (aim 12-15+ min for an 18-min video).
7. **Enforce Clean Framing** (shot pacing: §0):
   - Crop out all creator captions, timestamps, and emojis (`crop_top`, `crop_bottom`).
   - If an indispensable clip has an edge/corner TV badge, apply a 10–15% zoom punch-in (`crop` in `edl.json`) to keep the logo outside the frame.
   - Absolutely exclude frames with reporters holding microphones, news anchors speaking, or studio sets.
   - Run `python check_crops.py` in the episode's `project/` directory to generate the visual contact sheet (`crop_check.jpg`) and verify that every clip in the edit is 100% clean.
8. Captions are generated from the narration timing; check place names and numbers.
9. Check a frame from every graphic moment for collisions before export.

### The pipeline (in each episode's `project/` folder — copy from the latest episode, e.g. `episodes/2026-10-07-france-flash-floods/project/`)

Check that `VOICE` in `make_narration.py` is `en-US-AndrewMultilingualNeural` after copying.

| Step | Command |
|---|---|
| Narration per block | `python make_narration.py` |
| Narration check | `python qa_narration.py` |
| Music scan | `python audio_scan.py` → set `muted` in `edl.json` |
| Clean crop audit | `python check_crops.py` → review `crop_check.jpg` for badges/emojis |
| Lower-thirds + ticker | `python build_graphics.py` (edit the `LOWER_THIRDS` table and `TICKER_COPY` first; runs ~1 min per graphic — start it early in the background) |
| Source attribution tags | `python build_source_tag.py "<source>" "<location>" [--pos bottom_left\|top_right] [--anim]` (writes transparent PNG/MOV) |
| Edit list | `edl.json`: per chapter `shots` (under narration) and `breaks` (sound-on clips), `break_len` 18–25s |
| Pre-frame blur sidebars | `python frame_all.py` (parallel renders blurred moving background for all non-16:9 clips at CRF 16) |
| CapCut draft / Render | `python build_capcut.py` (builds multi-track draft with blurred framing + source tags) or `python render.py` |
| Chapter timestamps | `python update_chapters.py "<first chapter title>"` |

Known pitfalls already fixed in `render.py`: audio is mixed in a separate pass (mixing it inside the graphics pass dropped narration); still photos zoom over their full length; long ticker text is drawn by ffmpeg because long tsrct text layers wrap.

Keep the editing project and graphics editable. If a tool or asset format fails, preserve the source and report the limitation rather than claiming a completed render.

## 10. Thumbnail and upload copy

- Follow `iwn-brand-kit/thumbnail-workflow.md` and root `AGENTS.md`; use the selected finalized Design 1, 2 or 3 reference.
- Choose relevant imagery whose origin and permitted use are recorded.
- Draft short place-plus-action headlines and pair the best with a visual question the actual video answers. CALIFORNIA BURNING and PANAMA HIT AGAIN are user-reported outlier references, not verified CTR evidence.
- Prefer bright, detailed, slightly elevated views showing broader impact. Night imagery must retain readable homes, streets, vehicles and terrain.
- Avoid fabricated documentary scenes or exaggerated damage presented as evidence.
- Preserve the selected approved logo and badge treatment; do not revert to the retired circular-logo layout.
- Inspect at full size, 320x180 and 160x90 for headline legibility, visible subject detail, clear event scale and accurate story fit before delivery.
- Default thumbnail size: 1280 × 720; check the platform's current upload limits when delivering.
- Write an accurate title, concise description, reporting cutoff, chapters, and source/footage credits.
- Keep editorial citations separate from footage ownership credits when they differ.

## 11. Quality control

Review the complete exported video, not only the editing timeline.

- [ ] **Blurred Moving Background Framing**: Vertical/non-16:9 clips must NEVER sit on flat dark charcoal bars. They must use the dynamic blurred, darkened copy of the clip itself with subtle tiled IWN watermark sidebars (matching GWN's visual standard).
- [ ] **Zero News Anchors**: No reporters holding mics, studio sets, or TV crew footage.
- [ ] **Zero TV Channel Badges**: No third-party network logos, bugs, or breaking news chyrons.
- [ ] **Zero Watermarks & Emojis**: No bouncing TikTok logos, Instagram stamps, or emoji overlays.
- [ ] **Shot pacing**: shots mostly 11–13 s, clips under 11 s used whole, no cut shorter than 4 s.
- [ ] **On-Screen Source Attribution**: Subtle lower-third tags placed on eyewitness clips (*"Footage Source: ... via X / ..."*).
- [ ] **Resolution & Quality**: All footage meets HD standard (minimum 720p/1080p, no pixelated low-bitrate rips).
- [ ] **Runtime**: Total video duration meets the minimum floor (at least **13:00–15:00+**, scaling to **15:00–20:00+** when footage allows).
- [ ] **Narration Pacing**: Narration remains ~800–1,000 words (~5–6 min spoken) with balanced 18–25s natural sound breaks.
- [ ] Facts, locations, dates, units, and pronunciations checked.
- [ ] Dynamic claims rechecked against the reporting cutoff.
- [ ] Every used clip has verification and permission records.
- [ ] Older or illustrative footage is clearly contextualized.
- [ ] No accidental duplicate sequences, black frames, frozen frames, or missing media.
- [ ] Narration, natural sound, music, and captions remain synchronized.
- [ ] Tickers, lower-thirds, source credits, and subtitles do not collide.
- [ ] No sample headlines, dates, or placeholders remain in motion graphics.
- [ ] Audio measured and reviewed on speakers/headphones (−14 LUFS target).
- [ ] Thumbnail and title accurately represent the report.
- [ ] Export plays from beginning to end and matches intended runtime/resolution.

Correct issues, re-export affected deliverables, and verify the revised output.

## 12. Delivery and archiving

Default delivery package:

- Final 1080p MP4, typically H.264 video and AAC audio.
- Final thumbnail PNG or JPG, plus editable thumbnail source.
- Corrected SRT captions.
- Editable project with media references and required assets.
- Final script and shot list.
- Fact register, footage register, and permission records.
- Upload title, description, chapters, and credits.
- Review notes documenting any unresolved limitation.

Show the user the finished local deliverables for review. Do not upload or publish merely because the video is complete. Archive reusable cleared footage with recording dates and restrictions intact.

## 13. Time estimates and pilot measurement

**Pilot (Victoria flash floods, 4–5 Oct 2026):** ~5 hours for v1, plus ~2.5 hours for the v2 restyle. Most of it was one-time work (building the pipeline, graphics builder, music scan, render fixes) and a slow footage hunt (TikTok/X/Facebook search blocked without sign-in; first user-supplied clips were all wrong locations). Render speed: ~3 min per minute of video sequentially, ~1 min per minute with `render_parallel.py` on 8 threads.

Targets for the next episodes with the pipeline in place and the GWN format (~800 words):

| Stage | Target |
|---|---:|
| Research and fact register | 15–20 min |
| Footage: find, verify location/date, music scan | 25–40 min |
| Script (blocks + hooks) and narration QA | 10–15 min |
| Graphics (background) + edit list | 10–15 min |
| Render (parallel) | 12–15 min |
| QC | 5–10 min |
| **New event** | **~45–60 min** |
| **Follow-up on the same event** (reuse footage library, graphics, research) | **~20–30 min** |

Speed levers: build **one footage library per event** and produce several updates from it; build the shot list from news coverage first (§5), then trace originals in the signed-in browser; send post links rather than renamed files; send permission requests as soon as clips are chosen (replies are the only wait we can't shorten). Record actual times per stage and update this table.

## 14. Definition of done

An episode is complete when the finished export has been reviewed, its claims and footage are documented, the approved IWN identity is applied, and the full local delivery package is ready. Missing narration, uncleared essential footage, failed renders, or unresolved factual problems must be reported as incomplete work.
