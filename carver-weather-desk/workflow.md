# Carver Weather Desk: production workflow

The channel is **Carver Weather Desk** (@CarverWeatherDesk). The host is **Glenn Carver**, an AI avatar the owner renders in HeyGen.
- Coverage: US weather events now, global later. English only, no Spanish edition for now.
- Reference channel: youtube.com/@WaltMercerReport. Studied 4 Nov 2026; findings are in `docs/script-guide.md` §1.
- Titles and thumbnails: to be decided with the owner later.

## The flow (owner, 4 Nov 2026)

1. **The owner** gives the idea or topic of the video, sometimes with clips or links.
2. **I** research it, scout footage, and write **ONE HeyGen script**: `script/heygen_paste.txt`.
   - I also paste it in the reply, ready to copy.
   - There are no part files and no extra instructions.
3. **The owner** renders it later as **one continuous HeyGen video** of Glenn. HeyGen's voice is the final voiceover. They send the video, which I save as `host/glenn_raw.mp4`.
4. **I** create the video: a rendered MP4 plus a CapCut draft.

**Maximum length: 12:00 for the finished video** (owner, 4 Nov). That is about 1,650 words, or 11:00 of speech at 150 wpm, plus breaks and the end screen. `script_tools.py` fails any script estimated over 12:00.

## Steps

1. **Intake.** Confirm the channel first: the "IWN or Carver?" question in the IWN repo's `AGENTS.md`. Then confirm the story and the owner's links. Create `episodes/YYYY-MM-DD-slug/` with `research/ script/ clips/ graphics/ host/ edit/ exports/ delivery/`.
2. **Research and footage, in parallel and time-boxed.** Same rules as IWN `worflow.md` §4–6:
   - a fact agent (about 15 min)
   - a footage scout covering X, local news and agency feeds (about 25 min)
   - the owner's links, each checked for place and date
   - every viral clip checked for an older original
   - topic-sheet numbers verified; they are usually wrong
   Output: `research/facts.csv` (an ID, source and time for every number) and `research/sources.csv`.
   - **Viewer reports, from episode 2 on.** These feed the inbox-callback beat (`docs/script-guide.md` §6).
     - Pull the comments of the previous Carver upload: `yt-dlp --write-comments --skip-download <url>`.
     - Pick at most one real report that fits this story: a handle, a town and what they saw.
     - Save it in `research/viewer_reports.md`. Never invent or embellish one.
3. **Script.** Follow `docs/script-guide.md` exactly. That covers the 12-section, 12:00-max structure, Glenn's voice, the TTS rules and the two open loops. Allow at most 2 full-host moments, none before 2:30; the sign-off runs over the end screen.
   - Write `script/script.md`, the master. Each section has `layout`, `strap`, `ticker`, `visual`, `facts`, `cue` and `spoken`.
   - Run `python pipeline/script_tools.py build <ep>`. It writes the ONE script, `heygen_paste.txt`, plus `sections.json`, and fails if the estimated video runs over 12:00.
   - Add new hard names to `docs/pronunciation-glossary.csv`. The owner enters them in HeyGen's Brand Glossary.
   - **CTA beats** (owner, 6 Nov: "more subs and engagement, but not typical"). Follow guide §6:
     - desk report (S02)
     - inbox callback (S04, when one fits)
     - pinned list (S06)
     - share to one person (S08)
     - subscribe for the answer (S10)
     - question of the day + watch next (S12)

     Each has its `cta:` kind and `cta_copy` card. A pinned beat needs `pinned_comment:`, which the build writes to `script/pinned_comment.txt`. The lint checks the beat plan and the spacing.
   - Give the owner the one script, both as the file and pasted in the reply.
4. **While the owner renders HeyGen:**
   - Build the footage library and trim clips.
   - Build map, radar and satellite cards in Carver style (`pipeline/goes_px.py` places cities on GOES CONUS frames).
   - Build headline straps, ticker copy and CTA copy from `script.md`.
5. **HeyGen video in** (`host/glenn_raw.mp4`):
   1. Align with faster-whisper word timestamps and the guide's §5.3 cues. Output: `edit/section_times.json`.
   2. Matte the host if the chosen frame style needs a cut-out.
   3. Plan the timeline: layout per section, cards at their spoken hand-off words, breaks only at section ends.
6. **Compose and render.** Layer order:
   - footage or card base
   - host (box, cut-out or full)
   - strap, ticker and bug
   - CTAs
   - intro sting at the name line, and outro / end screen
   Render 1920x1080 30 fps MP4 at -16 LUFS on the host audio, and build the CapCut draft.
7. **QC.** Watch these points:
   - every section start
   - each full-host moment
   - each card hand-off
   - the ticker spelling
   - no source credits on screen (owner's choice)
   - no Thai or other placeholder footage left in
   Then make a contact sheet per shot.
8. **Delivery.** Put the MP4 and the CapCut draft in `delivery/`, plus `pinned_comment.txt` when the script has a pinned beat. The owner pins that comment right after upload, because the script tells viewers it's there. The upload copy format follows once titles are decided.

## Screen layout rules (brand kit: `brand-kit/`)

- **Host frame.** Owner's pick (4 Nov 2026): **A, Desk Window**, a rectangle with **no labels**.
  - The owner's edit: no "WEATHER DESK" tag and no "GLENN CARVER | REPORTING" chip.
  - The circle (C) is rejected, and B is not used. **Not full-screen at the start**, and full-screen rarely: at most 3 moments per episode, each ≤ 30 s (guide §3). The closing full-host sign-off becomes the **end screen**.
- **The window comes and goes, and changes look** (owner, 6 Nov 2026). It is not on screen all the time: on for a while, off, on again. All of this is in `pipeline/host_box.py`, and `plan_edit.py` schedules it automatically.
  - The looks:
    - **main**: 640×360, head to upper chest (crop 4.6× face width). It is the most common look, about 40%.
      - It was 720×405 with a head-to-waist crop until 6 Nov. The owner then asked for it "a little smaller", and next "a little cropped so his hands don't show when he is talking".
      - A, B and C then moved one step down each, in both size and crop, so main stays the biggest and widest.
    - **A**: 608×342, head, collar and tie knot (4.2×).
    - **B**: 576×324, head and shoulders (3.8×).
    - **C**: 544×306, head and the top of the shoulders (3.5×).
    - Every look crops above the hands, and so does the end-screen frame.
    - Full-host moments still show the whole HeyGen frame.
  - The positions:
    - **TR**: top right, 40 px margins. This is the default.
    - **TL**: top left at y 128, under the bug.
    - **BR**: bottom right, 28 px above the ticker.
  - The rhythm:
    - The video opens on main TR.
    - Each section opens with the window ON for at least 5 s.
    - After that it alternates: ON for 10–17 s, OFF for 7–13 s.
    - No appearance is shorter than 5 s, and no gap shorter than 4 s.
  - Every card or map lands full-frame first: the window is OFF for the card's first 5 s. Over a card the window only appears TR, because cards keep that corner clear. TL and BR are used over footage only.
  - CTAs sit under main TR, so the window is ON as main TR for every CTA.
  - The window never switches during the intro sting or within 0.8 s of a layout wipe.
  - **Transitions** (owner, 6 Nov: "I like the animation, add other animations too"). Each appearance gets one transition, used for both its on and its off. They rotate in a fixed order (`host_box.FX` / `FX_SEQ`):
    - **panel** is the original skewed sweep, about 30% of transitions.
    - **radar**: a radar-scope disc with a rotating beam, plus a ping sound.
    - **doors**: navy doors with crimson edges and an emblem flash.
    - **blinds**: six slats.
    - **slide**: the window slides in from the nearest screen edge.
    - **rise**: the window fades in while rising, plus a tick sound.
  - How they render:
    - Panel, radar, doors and blinds are 0.6 s alpha overlays, one per window size (`brand-kit/motion/box_<fx>_<look>.mov`). Each fully covers the window from 0.25 to 0.35 s.
    - Slide and rise are position and opacity keyframes on the host item and its chrome item. `compose.py` renders them with `kf_x`, `kf_y`, `alpha_in` and `alpha_out`; `build_capcut.py` writes CapCut keyframes.
  - Preview reel of all six: `brand-kit/styleframes/host-box-2026-11-06/CWD_window-transitions-preview.mp4`.
  - `plan_report.txt` lists every appearance under "desk window".
- **Keep-clear zones.**
  - The host's corner is reserved: x ≥ 1130, y ≤ 475. Every look at TR fits inside it.
  - CTA cards sit 22 px under main TR, at the same left edge and width: x 1240, y 422, 640 wide (`host_box.cta_rect`).
  - The bottom 66 px is the ticker, with the strap and legend just above it.
  - Map cards keep their key places out of those zones.
- **Headline strap.** One line, ≤ 40 characters. The subline carries the numbers. The kicker is `WEATHER ALERT | DEVELOPING | FORECAST | AFTERMATH` plus the location.
- **Ticker.** "THE LATEST", 2–4 items from `script.md`. The right block reads `UPDATED <time> ET`, the as-of time, never a live clock.
- **Bug.** Top left, the white emblem and wordmark.

## Pipeline (`pipeline/`): run order for an episode

All commands run from `carver-weather-desk/pipeline/`, with `<ep>` = `../episodes/<YYYY-MM-DD-slug>`.

| # | Command | Output |
|---|---|---|
| 1 | `python script_tools.py build <ep>` (lint; fails if the estimated video is over 12:00; `--demo` relaxes the template checks) | `script/heygen_paste.txt` (ONE script for HeyGen), `sections.json` |
| 2 | The owner renders HeyGen. Save it as `host/glenn_raw.mp4` | |
| 3 | `python prep_host.py <ep>` | `host/host_full.mp4`, `host_box.mp4` (main 720×405) + `host_box_A/B/C.mp4` (face-placed crops per window look), `host_end.mp4`, `vo.wav` (-16 LUFS), `host_meta.json` |
| 4 | `python align_host.py <ep>` (faster-whisper word times + script matching, expect > 90% matched) | `edit/align.json`: section starts and every `@ "anchor"` time |
| 5 | Write card specs `graphics/cards/<id>.json` (format: `docs/cards.md`). Use `"at_words": "<spoken words>"` and the planner turns each into a time | |
| 6 | `python plan_edit.py <ep> --render` | `edit/timeline.json`, plus rendered cards, straps, chips, CTAs, supers, ticker and base shots; `edit/plan_report.txt` lists shots and warnings |
| 7 | `python compose.py <ep> --sheet` (chunked NVENC, about 3× real time) | `exports/<name>.mp4` + `_qc.jpg` |
| 8 | `python build_capcut.py <ep>` (`--name …_v2` if the draft is open in CapCut) | CapCut draft `<name>` in the CapCut drafts folder |

**Brand motion kit** (re-render only after design changes): `python make_brand_motion.py`. It produces:
- `brand-kit/motion/`: the wipes (one box wipe per window look), the 4.2 s sting, and the end-screen background and foreground
- `brand-kit/graphics/`: the bug, the window chrome (one per look) and the end plate
- `brand-kit/sfx/`
- `--preview` gives stills instead
- `--box` re-renders only the window chrome and wipes, after a change to `host_box.PRESETS`

**Demo (pipeline test, fictional, never upload):** `episodes/0000-00-00-pipeline-demo`. The footage is the Phuket flood clips as placeholders, and the voice is an edge-tts stand-in for HeyGen (`prep_host.py --standin`).

**Gotchas:**
- OpenCV 5 has no Haar cascades. `prep_host` uses YuNet (`pipeline/models/face_detection_yunet_2023mar.onnx`).
- faster-whisper runs on the GPU (RTX 4050) through the pip wheels `nvidia-cublas-cu12` + `nvidia-cudnn-cu12`, installed 4 Nov. `align_host` adds their DLL folders itself. With `medium.en`, 20 s of audio takes about 7 s, so a full episode takes about a minute. If those DLLs go missing it falls back to the CPU at about 2× real time.
- On Windows, `ProcessPoolExecutor` can't start from a stdin script. Run multiprocessing code from a .py file.
- CapCut's bottom track is magnetic. `build_capcut.py` adds a `canvas` track whenever `base` has gaps.
- Timeline items on one track must not overlap by even one frame. The CapCut builder refuses them, so keep durations frame-quantized.

## Pipeline files (`pipeline/`)



**Built:**
- `render_html.py`: renders an HTML/CSS page to PNG, or a seeked animation to ProRes 4444 alpha or MP4.
- `goes_px.py`: GOES-19 CONUS lat/lon to pixel.

**Next:**
- script lint and paste-file generator
- `align_host.py`
- host matting (if style B)
- strap, ticker, bug and CTA motion
- intro/outro stings and section transitions
- Carver card templates
- `compose.py` and the CapCut draft builder

**Reused from IWN by copying, with the origin noted in each file:** footage prep, radar, satellite and zoom tools. Never edit IWN files (outside `carver-weather-desk/`) for Carver.
