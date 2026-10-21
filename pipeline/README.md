# IWN episode pipeline (template)

Kept outside `episodes/` so clearing old episodes does not delete it.

## New episode
1. Copy `*.py` from here into `episodes/<YYYY-MM-DD-topic>/project/`.
2. `python make_watermark.py <episode>/graphics` (writes `background.png` + `sidebar_watermark.png`). Spanish versions: copy these two files from the English episode instead (20 Oct: same logo, no separate ES framing).
3. Per episode, edit only: `SAY` in `make_narration.py`; `LOWER_THIRDS`, `TICKER_COPY`, `TICKER_LABEL`, `TICKER_STATUS` in
   `build_graphics.py`; and write `gen_edl.py` (-> `edl.json`).

## Order (run from the episode's `project/` folder)
| Step | Script | Typical time |
|---|---|---|
| Narration | `make_narration.py` | 1-2 min |
| Graphics & Ticker | `build_graphics.py` | about 1 min for 13 lower-thirds + ticker |
| Intro title card | `make_intro.py` (`INTRO` in `cards.py`) | about 10 s |
| Animated cards | `make_cards.py --stills`, then `make_cards.py` (`CARDS` in `cards.py`) | about 5 s / 40 s for 8-10 cards |
| Source Tags | `build_source_tag.py` | seconds per clip (generates clean PNG/MOV attribution pills) |
| Edit list | `gen_edl.py` | seconds |
| CapCut draft | `build_capcut.py` | about 10 s |
| Chapter times | `update_chapters.py "<first chapter title>"` | seconds |

Nothing is re-encoded: the draft places the original clips on a `bg` track holding `background.png`, and logo/caption
crops are CapCut crop settings on each clip (`{"crop": [x, y, w, h]}` in the edit list, as fractions of the frame).

## Notes
- **Editorial Source Attribution Tags**: Run `python build_source_tag.py "<source>" "<location>" [--pos bottom_left|top_right] [--anim]` to render on-screen attribution tags matching the IWN broadcast brand identity.
- **High-Definition Clip Downloads**: Always download clips using `yt-dlp -f "bv*+ba/b" --merge-output-format mp4 "<URL>"`. Never use `[height<=1080]` as it severely degrades vertical videos (reducing 1080x1920 to 608x1080 at ~400 kbps).
- Old look (blurred, moving side bars; every clip re-encoded): put `"framing": "blur"` in `edl.json`, then run
  `frame_all.py` (and `check_framed.py` after an interrupted run) before `build_capcut.py`. 10-25 min per video.
- `build_graphics_tsrct.py` is the previous graphics builder (Tesseract projects, 3-4 min per lower-third). Same design.
- `make_narration.py` talks to `api.msedgeservices.com` because the legacy edge-tts host has answered 403 since about
  10 Oct 2026 (edge-tts issue #490 / PR #491). Remove that override once edge-tts ships the fix. `tts_probe.py` tests it.
- Lower-thirds are three files each (`lt_S##_in.mov`, `lt_S##.png`, `lt_S##_out.mov`); the ticker is `ticker_strip.mov`
  (1920x192), positioned by the draft builder.

- **Reusing the user's own GWN videos** (GWN is the user's channel; no credit): put the downloads + `--write-auto-subs --sub-format json3` captions in `clips/raw/`, run `analyze_gwn.py` (finds stretches with no GWN lower-third/pop-up, crop box between the blurred side bars, GWN-voice overlap) and review `clips/_scan/<id>/seg_*.jpg`; mark rejects in `clips/gwn_segments.json`, then cut them into `clips/lib/` (see the Texas/Oklahoma episode's `make_lib.py`: `G..._q_` = no GWN voice, safe for sound breaks).
- **Channel names (16 Oct 2026)**: English channel = *Independent Weather Network*, Spanish channel = *Instant Weather Network*.
  Set `lang="en"` (default) or `lang="es"` in `gen_edl.py`'s `E.build(...)`; the draft then uses
  `iwn-brand-kit/motion/subscribe-<lang>-transparent.mov` (made by `make_subscribe.py`). (Before 20 Oct, Spanish episodes used `make_watermark.py --lang es` for a capital `IWN`; now they reuse the English logo and framing.)

## 17 Oct 2026 changes (user feedback)
- `make_cta.py`: bigger subscribe CTA with like + bell buttons (cursor clicks like -> subscribe -> bell). Run once; render.py picks `subscribe-cta-<lang>-transparent.mov` automatically (SUB_LEN = 7).
- Tickers in every chapter: headline ticker (`ticker_len` 22) after the subscribe CTA + CTA ticker (`cta_ticker_strip.mov`, `CTA_COPY` in build_graphics.py) at each chapter's end.
- `edl_tools.build(pool=True)` (default): video-wide footage pool, max 2 appearances per clip (`important=[...]` allows 3). Chapter shot/break lists are preferences only. The build prints the pool report (second passes).

## 18 Oct 2026 changes (GWN comparison)
- Shots 11-13 s: render.Pool `max_shot=13` (aims ~12 s, prefers a full second showing over short leftovers); `edl_tools.build(max_shot=13)`.
- Clips under 11 s play whole, never trimmed (`Pool._short` / `_whole_ok`); small gap remainders are filled with a whole short clip that fits.
- Cold open 20 s default; `edl_tools.build(reactions={...})` keeps eyewitness-reaction clips audible.
- Defaults `break_len=12`, `tail=13`; write ~1,300-1,600 words of narration (55-60 % of runtime).
- No cut under 4 s (`Pool.min_shot=4`): clips under 4 s are skipped, short clips are used only when they fit a gap exactly or leave >= 4 s, gaps under 4 s continue the previous shot, `_no_slivers` folds any fragment into a neighbour, and the chapter lead-in is part of the first shot. Tested on the Norte edit: 0 shots under 4 s.

## 18 Oct 2026 — narration fixes
- `SAY` stays empty (respellings broke names); `make_narration.py` rejects hyphen/caps respellings.
- Spanish episodes: `python qa_narration.py --lang es` (multilingual faster-whisper `medium`, language=es). edge-tts has no es-* Multilingual voice; Spanish episodes use `en-US-AndrewMultilingualNeural`, which reads Spanish.
- New step after narration: `python qa_narration.py` → `audio/narration/qa_report.txt` lists names the voice did not say recognisably.
- One paragraph per chapter + `tail=28`; `_plan_overlays` handles one-part chapters (ticker over narration, pill + CTA ticker in the break).
- Clip audio: mute ONLY music (18 Oct). `MUTED = E.muted_from_sources(EP)` reads sources.csv/user_clips.csv and mutes clips whose sound/notes mention music; speech stays audible. Never strip audio when slicing.

## 18 Oct 2026 — chapter-reserved clips
- `edl["reserve"] = {clip: ["S11", ...]}` in gen_edl.py limits a clip to those chapters (render.Pool checks `pool.chapter`). Use it for footage tied to one place (e.g. the Lake Erie waterspout in the waterspout chapter, the user's Chicago clip in the Chicago chapter); combine with `edl["must"]` for user clips.
- make_narration.py cache key now includes SAY (19 Oct): `.ok` files store the spoken text, so adding a one-word fix regenerates every part that contains that name. Example tested fix: "Pego": "peggo" (default voice said "Pigo").

## 20 Oct 2026 — archive footage
- `E.build(..., archive={"F301": {"date": "FEB 2026", "chapters": ["S13"]}})`: footage from an earlier event is allowed only in the chapters about that event, and the narration there must say when it happened. `check_archive` refuses S00/S01. render.Pool reserves each archive clip to its chapters and offers it first there. There is no on-screen archive tag (user decision).
- **Revised the same day:** archive footage is only for events that have NOT happened yet. Use `E.build(..., event="upcoming", archive={clip: {"date": "SEP 2026"}})`; the default `event="happened"` refuses archive clips.
- `E.build(..., tail="auto")`: no fixed runtime. The clip break per chapter is sized to the distinct footage in the library (8–45 s). `auto_tail` prints the projected runtime.
- `build_capcut.py`: the iwn corner logo goes on every horizontal clip (`watermark` track, `graphics/corner_watermark.png` made on first use, capital IWN for ES). Vertical clips keep the side-bar logo tile.

## 20 Oct 2026 — Spanish versions: translate + shuffle only
- A Spanish version of an English video needs only three things:
  1. Translate the narration (and the lower-third/ticker text).
  2. Shuffle the clip placement (`gen_edl.py` with `clips_dir=<EN>/clips/found`, `lang="es"`, shuffled prefs/pool).
  3. Build the draft.
- No separate logo framing: `build_capcut.framed` reuses the English `_framed` copies by default, and the corner logo is the same lowercase iwn. Copy `background.png` and `sidebar_watermark.png` from the EN episode's graphics, so any newly framed span gets the same logo. Only the subscribe pill stays Spanish (`subscribe-cta-es`, Instant Weather Network).

## 21 Oct 2026 — faster framing
- Why it was slow: every used clip span was re-encoded (blurred side bars + logo tile) with x264 `medium`/crf 16, running 6 jobs on 8 threads. A 12 s 4K60 drone shot took ~39 s, and an episode needs ~80 spans.
- What changed:
  1. **16:9 clips are not framed at all.** When the (cropped) width/height is >= 1.7 (`build_capcut.H_MIN`), the clip fills the frame, so its blurred bars were invisible anyway. It goes into the draft as the original file with CapCut crop settings and gets the corner iwn logo. `frame_all.py` frames only vertical/square clips.
  2. **Framing encoder:** `veryfast`/crf 17 (`render.VENC`), about 2× faster per job. Framed copies are intermediates, and CapCut re-encodes on export.
  3. **The `bg` track** (background.png) is now always under the main track, to fill thin bars beside not-quite-16:9 clips.
- Measured: Outer Banks 95/97 shots and Spain update 22/111 shots need no framing. Intel QSV (`h264_qsv`) was only ~20% faster than veryfast here, so it is not used.

## 21 Oct 2026 — horizontal watermark = iwn pattern, faster framing
- `build_capcut.py`: horizontal (16:9) clips go in as originals with the tiled iwn pattern (`graphics/sidebar_watermark.png`, normal strength) on the `watermark` track. No re-encode, and the opacity is editable in CapCut. Set `"h_watermark": "corner"` in edl.json for the old top-right logo.
- Only vertical and non-16:9 clips are framed (blurred side bars), at `preset veryfast, crf 17`. Run `frame_all.py` in the background after `gen_edl.py`.
- Vertical framing (21 Oct): 30 fps and shrink to 1080 high before the blur, Intel Quick Sync encoder (`h264_qsv`) with x264 fallback. About 3x faster than before with the same look. No hardware decoding (d3d11va gave a green side bar). CapCut canvas blur was tested and rejected.

## 21 Oct 2026 — intro title card + animated cards
The look is matched to the user's hand-made Outer Banks graphics (youtube.com/watch?v=Bsw35dVmjLo). Rules are in worflow.md §0 and §9.
- `cards.py` per episode (template: `cards_example.py`, which shows every type and option): `INTRO = {"headline", "date"}` and
  `CARDS = [...]` (id, type, chapter, facts, pill, headline, sub, source + type-specific data).
- `make_intro.py` → `graphics/intro.mov`. It is 3.4 s of ProRes 4444 with alpha: the iwn letters fade in, the red dot drops in, a rule opens, then the channel name, the headline and "LATEST UPDATES · date" appear, and a red bar wipes the card away. `--headline/--date/--lang es` override cards.py.
- `make_cards.py` → `graphics/cards/<id>.mp4` (opaque H.264, 6-8 s) + `<id>.png` review stills. `--stills` (seconds) and `--contact` (`_contact.png`). It runs 4 cards in parallel.
  - Types: storm_map, closure_map, forecast_map, explainer_map, track_map, map, stat, timeline, alert, flood_map (GeoJSON or image), satellite (mp4).
  - Checks: no repeated id, headline or media file; no card in S00; fact ids must exist in research/facts.csv (`--no-facts-check` for tests); forecast/track maps must say forecast or outlook.
  - It prints a warning when a map label collides with the headline, logo or another label.
- Maps use `geo/natural_earth_10m.npz`: Natural Earth 1:10m land, lakes, borders, states and populated places. It is public domain, 4.4 MB, and works offline. Rebuild it with `geo/pack_natural_earth.py <folder of Natural Earth GeoJSON>`. When the scripts run from an episode's `project/` folder, they find it in `<root>/pipeline/geo/`, so there is no need to copy `geo/`.
- Shared drawing code is in `iwn_gfx.py` (fonts, colours, pill/headline/sub/source/logo chrome, encoders).
- `edl_tools.build(..., intro=True)` (default) writes `"intro": {"seconds": 3.4, "overlap": 0.45}` and checks `cards.py`.
  - `render.plan_chapter` gives S00 an extra `("intro", start, 2.95, None, [])` item, so the chapter times, the SRT and `update_chapters.py` all include it.
  - Old edl.json files without `"intro"` are unchanged.
- `build_capcut.py`: the new `cards` track sits between `source_tag` and `lt`.
  - The intro goes at the end of S00, and its wipe overlaps the start of S01.
  - `card_schedule()` places each card once under its chapter's narration: at `at` if given, else the first 0.5 s step after the lower-third that fits inside one narration part and covers no `must` clip. Each card fades with alpha keyframes of 0.3 s.
  - Lower-thirds, the subscribe pill and the tickers stay above the cards.
- Tested 21 Oct on a copy of the France Storm Adam episode: intro + 8 cards from its facts.csv. The draft is 13.2 min, and `build_capcut` takes about 10 s.
