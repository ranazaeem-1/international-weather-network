# How GWN sources its clips (forensic check, 18 Oct 2026)

**Scope:** 7 Global Weather Network (GWN) SoCal-fire videos, 3 Independent Weather Network (IWN) fire videos and one Turkey video from each channel. All were analysed as 360p copies.

**Method:**
- Cuts were found with ffmpeg scene detection (score 0.18 or higher).
- Each frame was fingerprinted from its central region (structure plus colour, 2 frames per second). Matching shots were grouped together without chaining.
- Every distinct GWN shot was viewed on contact sheets.
- The GWN shot pool was matched against IWN's entire fire library: 370 files from the malibu-fire, camp-pendleton-fire and socal-norte-fire folders (raw, user, found and held).
- Eyewitness speech in GWN's auto-captions was matched against the Whisper transcripts of the user's X clips.

Scratch data is in `%TEMP%\claude\...\scratchpad\cmp\`. The folders are `shots/` and `pool/`, and the files are `lib_matches.json` and `gwn_pool.json`.

**Evidence images:**
- `C:\Users\hp\AppData\Local\Temp\claude\C--Users-hp-Desktop-international-weather-network\2d1f4672-c3e1-4152-a623-9de471c252d0\scratchpad\cmp\pool\sheet_0.jpg`: the first 40 distinct GWN shots. Most are vertical phone clips inside blurred side bars tiled with "GWN".
- `...\scratchpad\cmp\fr\lib_matches.png`: GWN frame (left) next to the matching frame from IWN's own library (right).
- `...\scratchpad\cmp\fr\q247.png`: a "California" fire shot in GWN video QJM8c2cevA4 at 20:03. It is actually **Pine Bluff (Arkansas) Fire & Emergency Services**, so it is off-event stock.
- `...\scratchpad\cmp\fr\tags.png`: GWN's 16 Oct cold opens carry a "Southern California, CA · **SEP, 2026**" tag.
- Per-video cluster sheets: `...\scratchpad\cmp\shots\<id>_clusters.jpg`.

---

## Bottom line (the "secret")

GWN does **not** have a bigger or faster clip pipeline than IWN. It gets more video out of fewer clips:

1. **One growing library per event, recycled into every upload.** GWN made 7 fire videos (126 min) out of about **38 min of distinct footage** (274 distinct shots). Its later uploads are 66–97% footage from its earlier videos. The 18-min `JpfAKzf2LCc` had only 0.5 min of new footage, and the 30-min `-epiM2pvixk` was 93% recycled.
2. **Long shots, cut once each per video.** GWN's median shot is 7.5 s (90th percentile 15 s); IWN's is 3.5–5 s. Within a single video GWN rarely repeats a shot: 5–6% repeated footage in the Malibu and LA videos, against 47–59% in IWN's 16 Oct videos.
3. **No clip is too "dirty" for GWN.** It uses:
   - vertical X/TikTok reposts with the speech and profanity left in
   - TV helicopter feeds reposted on X, with the reporter's narration kept
   - scanner audio clips
   - clips cropped or blurred to hide burned-in text
   - at least one clip from an unrelated fire (Pine Bluff, Arkansas)

   The blurred side bars tiled with "GWN" hide whatever sits at the frame edges.
4. **Natural sound fills runtime.** Narration covers about 54–65% of runtime. The rest is eyewitness screams, reporters and radio traffic, which make long shots feel "rich".
5. **Speed comes from volume, not better sourcing.** GWN posted 12 videos on 17 Oct alone and 9 SoCal-fire videos in 32 hours. Its first video on each fire went up about 12–13 h after ignition. IWN's Norte video went up at 24.7 h.

IWN's Norte episode `9SnWUC0iIAU` already matches GWN on clip count within a single video: **216 distinct shots and 16.3 min of unique footage in 18.6 min**, against GWN's Malibu video at **113 shots and 15.2 min in 16 min**. IWN's gap is in **reuse across videos, shot length, speed of the first upload, and kept audio**, not in finding footage.

---

## 1. Distinct clips per video

The table counts distinct shots after merging repeats within each video.

| Channel | Video | Length (min) | Shots | Distinct shots | Unique footage (min) | Repeated runtime | Median shot (s) (10th–90th pct) | Most uses of one shot |
|---|---|---|---|---|---|---|---|---|
| GWN | 5SOrKXWV_Ys (16 Oct 12:40) | 10.1 | 74 | 52 | 7.4 | 27% | 6.75 (2.5–14.5) | 4 |
| GWN | 2vcv3Buai74 (16 Oct 16:23) | 15.1 | 114 | 88 | 12.2 | 19% | 6.75 (2–16) | 4 |
| GWN | JpfAKzf2LCc (16 Oct 20:48) | 18.1 | 135 | 93 | 12.6 | 30% | 7.0 (2–16) | 5 |
| GWN | lCR1ryuJHDs "LA burning" (17 Oct 06:48) | 12.1 | 90 | 85 | 11.4 | 6% | 7.5 (1.5–15.5) | 2 |
| GWN | Aw0nrvtMUr0 "Malibu HIT" (17 Oct 07:49) | 16.0 | 117 | 113 | 15.2 | 5% | 7.5 (2–14.7) | 2 |
| GWN | QJM8c2cevA4 "LA under siege" (17 Oct 13:37) | 25.1 | 180 | 147 | 20.1 | 20% | 7.5 (2.5–15) | 4 |
| GWN | -epiM2pvixk (17 Oct 20:22) | 30.1 | 219 | 162 | 22.6 | 25% | 7.5 (2–15) | 4 |
| IWN | VMWI72S7kp8 (3 wildfires) | 17.5 | 230 | 131 | 9.3 | 47% | 5.0 (1.5–6.5) | 8 |
| IWN | 9qvtZhVUEwk (Pendleton) | 17.1 | 292 | 120 | 7.0 | 59% | 3.5 (1.5–5.5) | 10 |
| IWN | 9SnWUC0iIAU (Norte) | 18.6 | 238 | 216 | 16.3 | 12% | 4.5 (2–7) | 5 |
| GWN | 3OAlVFwN61Y Turkey | 15.2 | 131 | 130 | 14.7 | 3% | 6.5 (2–12) | 2 |
| IWN | Fa0pKDdD3fE Turkey (15 Oct) | 23.3 | 377 | 167 | 9.5 | 59% | 4.0 (1–6) | 14 |

**Pooled per event, deduplicated across videos in upload order:**
- **GWN, 7 fire videos:** 126 min published, **274 distinct shots, 37.9 min distinct footage**. New footage per upload was 6.9, 5.1, 0.5, 10.4, 4.4, 8.5 and 2.0 min.
- **GWN, 17 Oct only (3 videos):** 53 min published, 194 distinct shots, 26.3 min distinct footage.
- **IWN, 3 fire videos:** 53 min published, **326 distinct shots, 24.2 min distinct footage**. IWN's Norte video also reused about 3.7 min from its Pendleton and "3 fires" videos.

**Shared footage between GWN videos on the same event (share of the later video's shots that also appear in the earlier one):**
- 2vcv contains 71 of 74 shots from 5SOr.
- JpfA contains 130 of 135 shots from 2vcv.
- Aw0n contains 62 of 90 shots from lCR1.
- QJM8 contains 73 of 117 shots from Aw0n.

GWN therefore works from **one library per event**. Each upload adds a few minutes of new clips and re-cuts the rest under a new title.

**Caveat:** a "shot" is one continuous cut. Some of GWN's long vertical clips are chopped into 1–2 s pieces, so distinct *source posts* are fewer than distinct shots. My estimate is roughly 120–150 source posts for the GWN fire pool, but this was not counted exactly. The cross-video dedupe is conservative: the same clip with different packaging sometimes escaped matching, so GWN's true reuse is a little higher.

---

## 2. Source types in the GWN pool

This is a visual classification of all 263 distinct shots in the first six GWN fire videos, accurate to about ±10%.

| Source type | Share | Notes |
|---|---|---|
| Vertical phone video (X/TikTok/IG reposts) | **≈60%** (about 160) | Shown in a centre box about 70% of frame width, cropped top and bottom, with blurred sides tiled with "GWN". Includes car-interior drive-throughs (dashcam-like phone clips), backyard ridge flames, evacuations and people filming helicopters. |
| Horizontal ground footage (residents, stringers) | **≈24%** (about 63) | Night engine and firefighter shots in stringer style (Key News Network/OnScene look), plus resident landscape clips. |
| Aerial: TV/agency helicopter and aircraft window | **≈14%** (about 36) | Night fire-line aerials, zoomed flame close-ups, an aerial of a red-roof house with a hose stream, and passenger or crew window shots over pine forest. At least one is a **TV helicopter broadcast reposted on X** with the reporter audio kept ("102 acres with a potential of 200…", X post `lbPKPlPX0AyllULL`, used in QJM8 at 8:29 and 18:37). |
| Official (CAL FIRE/OCFA/LAFD/DVIDS) | Few, none confirmed | One matched aerial came via a YouTube "repost of agency aerial" (Casey James, `Vp7M3cOlAVc`). |
| Drone | ≤2 possible | None confirmed. |
| Off-event / stale | At least 1 confirmed, more suspected | **Pine Bluff, AR Fire & Emergency Services** ladder truck (QJM8 at 20:03). Pine-forest and lake clips that don't fit Norte or Bryson terrain. The 16 Oct cold opens are tagged "SEP, 2026". |

**How GWN hides watermarks:**
1. **The 70% centre box with blurred, GWN-tiled sides** hides corner bugs and side UI on every non-16:9 clip and on many 16:9 clips.
2. **Zoom crops** remove burned-in bottom captions. In `lib_matches.png`, the library versions of two clips have a white text strip along the bottom that GWN's versions do not show.
3. GWN's own "BREAKING NEWS" lower third sits over the bottom band where TikTok/IG captions and chyrons live.

GWN keeps **all audio**: eyewitness profanity (bleeped in captions), TV reporters, a field reporter's stand-up ("Temperatures here probably in the low 80s, humidity level…") and fire-radio traffic ("Division Alpha… 227, they're up", "Engine 345").

---

## 3. Originals traced (19 visual matches, 5 caption-speech matches)

### Matches against IWN's own library

| GWN shot | Matches IWN file | Original source and time | Verdict |
|---|---|---|---|
| 5SOr 0:06; 2vcv 5:08 (night fire by gate) | user `6P3qjp9ZgS_3GWjP` (held as U032) | X post 17 Oct 06:46Z | **GWN had it at 16 Oct 12:40**, 18 h before the repost the user found |
| 5SOr 0:31 and 5:22 (night fire line) | malibu user `M4-F2LcxqMdg6Urn` | X, 16 Oct 05:50Z | GWN used it 6.8 h later |
| 5SOr 3:22 | malibu user `3xq_Aus-mbb7C9XE` (PCH / Trancas drive) | X, 16 Oct 01:17Z | Used 11.4 h later |
| 5SOr 3:33; lCR1 11:13 (orange sky) | malibu user `AhMxYT6gyoGh0Ssl` | X, 16 Oct 01:55Z | Library copy has a burned-in bottom caption; GWN cropped it out |
| 5SOr 4:12 (aerial flame front) | malibu found `U05_Aerial_Flame_Front_Hillside` | user clip | Match |
| 5SOr 5:38 (sunset smoke) | malibu user `pAk9a-ZD_QevcLYy` | X, 16 Oct 01:51Z | Match |
| 5SOr 5:54 (night road, red lights) | norte held `U032` / user clip | X | Match |
| lCR1 0:16 and 0:23 (drive into cul-de-sac) | norte found U007 and U009 (`9v8oVhTEjaYtRosh`) | X, 16 Oct 22:03Z | Used 8.8 h later, **with "Looks like we're about to lose everything…" audio kept** |
| lCR1 1:53 (night ridge, radio traffic) | user `YvmFJo13vVqjHOap` | X, 17 Oct 06:46Z (IWN rejected it) | Match; scanner audio kept |
| lCR1 2:09 (plume from sea) | norte held U015 (`F32TRfRhWcITnUbs`) | X, 17 Oct 00:36Z | Match |
| lCR1 2:39 | user `oxcg7QTguN4Ri3s0` | X, 16 Oct 20:19Z | Probable match |
| lCR1 6:08 | raw `6v3HWVNqyY4` (RockerBob, resident on YouTube) | YouTube, 17 Oct | Probable match |
| QJM8 0:30 | raw `Vp7M3cOlAVc` (Casey James, repost of agency aerial) | YouTube, 16 Oct | Match |
| QJM8 22:02 (aerial fire line) | raw `m2GuH8iLuS8` | YouTube | Probable match |

### Matches by eyewitness speech (GWN captions against Whisper on the user's X clips)

| Phrase in GWN captions | User's X clip | Note |
|---|---|---|
| "I'm in Meredith Canyon…" (lCR1 0:08) | `GPHiWorKJYmFEh-8` (16 Oct 22:14Z) and duplicate `xUYt…` | |
| "Looks like we're about to lose everything" (Aw0n 0:53, lCR1 0:17, QJM8 13:28) | `9v8oVhTEjaYtRosh` | |
| "Yeah, that's gonna go right up to the houses" (many times) | `c_uBAfHMce4zRE5l` (16 Oct 20:05Z) | |
| "You said it was 102 acres with a potential of 200 acres…" (QJM8 8:29, 18:37) | `lbPKPlPX0AyllULL` | TV helicopter broadcast reposted on X. IWN rejected it for its station bug and reporter. |
| "…227, they're up" (QJM8 19:51) | `YvmFJo13vVqjHOap` | Radio traffic |

Visual matching rejected 4 of the 23 candidates; those are not counted above.

**Where GWN's clips come from:**
- It draws on the **same X repost ecosystem the user already scrapes**. At least 16 of the user's own X clips appear in GWN videos. The batch of clips the user saved with X timestamps of 17 Oct 06:45–06:46Z (`6P3q`, `YvmF`, `lbPK`) looks like reposts by one aggregator account, and GWN had at least one of them about 18 h earlier. So GWN monitors the original posts or the large aggregator accounts, not later reposts.
- **Freshness:** GWN typically uses an X clip 6–11 h after it was posted, and in one case had a clip before the repost IWN found.

**Not verified:**
- **TV-station matching:** 18 TV-station uploads were downloaded (KTLA, ABC7, NBCLA, FOX 11, FOX Weather, TRT; they are in `scratchpad\cmp\tv\`) but not compared, for lack of time. The evidence for TV material is the reporter audio and the TV helicopter post on X.
- **X search:** I could not use it. The built-in browser pane was **not** logged in to X (it redirected to the login page), and per the rules I did not log in.
- **Stringer and licensing sites** (Storyful, Newsflare, ViralHog, LoudLabs): not checked.

---

## 4. Timing

| Event (ignition, UTC) | GWN first video | GWN videos on the event | IWN first video |
|---|---|---|---|
| Bryson / Henderson (15 Oct, about 21:00–23:55) | 16 Oct 12:40 (about 13 h) | 9 SoCal-fire videos by 17 Oct 20:22: 10, 15, 18, 12, 16, 23, 25, 27 and 30 min | 16 Oct 21:07 (about 21 h) |
| Norte (16 Oct, about 18:30) | 17 Oct 06:48 (**12.3 h**) | Folded into the same series | 17 Oct 19:13 (**24.7 h**) |

- **Channel output:** 12 uploads on 17 Oct across fires, Turkey, Brazil, Russia and Colombia.
- **Reuse across uploads:** confirmed and heavy (section 1). Each new video is a re-cut of one library per event with a new angle in the title ("Malibu HIT", "LA BURNING", "LA UNDER SIEGE", "FROM MALIBU TO LA").

---

## 5. GWN's likely pipeline

1. **Harvest viral social reposts early.** GWN watches X and TikTok aggregator accounts and the original posts in the first hours, downloads everything vertical, and keeps the audio. This is the largest share, about 60%.
2. **Add YouTube resident and stringer uploads** (the same channels IWN already uses: RockerBob, Casey James, KNN-style night footage).
3. **Add TV aerials secondhand.** These are mostly TV helicopter clips reposted on X, which are easier to grab than station uploads. Bugs are cropped or blurred, and the reporter audio is often left in.
4. **Package to hide marks.** The 70% centre box, blurred GWN-tiled sides, a zoom crop and its own lower third cover corners and bottom captions.
5. **Fill gaps with stale or off-event clips** (Pine Bluff, AR; a "SEP 2026" tag on 16 Oct videos; terrain that doesn't fit).
6. **Keep one library per event and re-cut it every 3–6 hours** into a new 10–30 min video, adding whatever new clips arrived.

There is no sign of Storyful or Newsflare licensing (no licensor credits, no consistent licensed-agency look). GWN is not compiling TV newscasts wholesale: there are no anchors or studio shots.

### What IWN could adopt within its current rules

These need no rule change:
- **One library per event, reused across videos.** IWN already allows 2 uses per clip within a video. Allowing reuse *across* that event's follow-up videos (Day 1, Day 2, the next evening) is a policy choice, not a quality issue. It would let IWN publish 2–3 videos per event from one 45-minute harvest.
- **Longer shots.** Hold clean clips for 6–10 s instead of 3.5–5 s. That roughly halves the number of clips a video needs: an 18-min video needs about 140 shots at 7.5 s against about 240 at 4.5 s.
- **First upload by about 12 h after ignition:** publish a Day-1 video at about 12 h with whatever is clean, then a follow-up.
- **Packaging:** the centre box with blurred, iwn-tiled sides is already in IWN's style for vertical clips. Use it for every vertical clip instead of rejecting low-res verticals.
- **Ambient natural sound with no speech** (wind, crackle, rotors) between narration lines.

### GWN practices that break IWN's current rules (for the user to decide)

1. **Keeping eyewitness speech and profanity.** IWN mutes all speech. GWN keeps it, bleeped only in the captions.
2. **TV helicopter footage with the bug cropped or blurred**, reporter narration kept (e.g. `lbPK`). This breaks the no-TV-station rule.
3. **Hiding burned-in text and logos by blur or crop beyond 15%.** The 70% centre box removes about 30% of a 16:9 frame's width, and the zoom crops cut bottom caption bars.
4. **Radio and scanner audio clips** (e.g. `YvmF`). They are not banned outright, but they are speech.
5. **Low-res (360p/540p) verticals.** IWN often rejects these.
6. **Unverified or off-event footage** (Pine Bluff, AR; "SEP 2026"). **I do not recommend copying this.** It is a factual-integrity and copyright risk, and IWN's verification is a strength.
7. **Music under montage** ("[music]" in GWN captions). IWN's rule is no music.

---

## 6. Faster IWN workflow: 100+ clean clips in under 45 min

The target is about 140 shots for an 18-min video at 7.5 s per shot, or about 45 source posts, each cut into 2–4 shots.

**Step 0 (2 min). Create the event folder.**
- Write a keyword list: fire or storm name, towns, landmarks, roads (e.g. "Norte Fire", "San Clemente", "San Juan Capistrano", "Ortega", "I-5", "Camino Las Ramblas").
- Note the event start time in UTC, so anything older can be rejected automatically.

**Step 1 (10 min). X first: it is the richest source and GWN's main feed.**
- Use the in-app browser *after the user logs in to it themselves*. The browser pane was not logged in today.
- Run these searches with the Latest tab:
  - `"<fire name>" filter:native_video`
  - `<town> fire filter:native_video`
  - `<town> min_faves:50 filter:videos since:<date>`
- Open the 10–15 largest aggregator accounts once (e.g. the ones that posted the 06:45Z batch) and take everything from the last 12 h.
- Collect status URLs into `x_urls.txt`, then batch-download with `yt-dlp -a x_urls.txt -o "%(id)s.%(ext)s"`. This works on public status URLs without logging in.
- Aim for 40–60 posts. Don't pre-judge them; the scan in step 4 does that.

**Step 2 (8 min). Official agency accounts on X and YouTube.**
- **Accounts:**
  - CAL FIRE: @CAL_FIRE plus the unit accounts
  - OCFA @OCFA_PIO
  - LAFD @LAFD and LACoFD @LACOFDPIO
  - Ventura County Fire @VCFD
  - US Forest Service: Angeles @Angeles_NF and Cleveland @ClevelandNF
  - Camp Pendleton @MCIPACPendleton
  - DVIDS (search "Camp Pendleton fire")
- Agency helicopter, drone and engine-crew video is clean, comes with no music, and is usually free to reuse with credit.
- Download with yt-dlp.

**Step 3 (8 min). YouTube stringers and residents.**
- Search with today's working method, but only on known stringer and resident channel lists:
  - Key News Network
  - TNLA
  - OnScene.TV
  - LoudLabs
  - RMG News
  - Smoke N' Scan (has scanner overlay, so mute it)
  - local resident channels
- Also search "<town> fire" sorted by upload date (`&sp=CAI%253D` in the results URL, which works with yt-dlp `--flat-playlist`).
- Skip channel names matching KTLA, ABC7, NBCLA, FOX 11, CBS LA, KCAL or any "News" station automatically.

**Step 4 (8 min, automated). Batch scan instead of judging clips by eye.**
- A script (extending the existing `_scan` / Whisper step) should:
  - run Whisper and drop clips that are mostly speech, while keeping speech-free spans
  - detect burned-in text by OCR or a text-region detector on 1 fps frames, and allow ≤15% crop
  - detect logos and bugs in the corners
  - flag music by audio classification
  - auto-cut usable 6–10 s spans
  - pHash-dedupe across the whole event library, including previous days
- **Output:** a single contact sheet plus a CSV. The user approves in one pass.

**Step 5 (5 min). Reddit and Telegram, as fallback and for late clips.**
- **Reddit:** r/CAWildfires, r/LosAngeles, r/orangecounty, r/sandiego, r/Wildfire (new posts in the last 12 h). `v.redd.it` links download with yt-dlp.
- **Telegram:** public disaster and OSINT channels (e.g. regional "Breaking" channels) via `t.me/s/<channel>` web previews. These are mostly reposts, so use them for international events (Turkey, Brazil) more than California.
- **Newsflare, Storyful and ViralHog:** the free previews are watermarked and the licensing costs money, so they are not usable at $0. Use them only to *find* the uploader, then contact or locate the original post.

**Step 6 (4 min). Build the day's library.**
- Keep one `event_library/` per event, not per episode. IWN currently clears episodes daily, so keep this folder outside `episodes/`.
- Reuse it for the Day-2 and Day-3 videos the way GWN does. Each new video only needs the new clips.

**Priority order:**
1. X native video (eyewitness)
2. Agency accounts
3. YouTube stringers and residents
4. Reddit
5. Telegram

TV is never used under the current rules.

**Realistic yield:** about 45 posts at 2–4 usable spans each gives 100–150 shots, or 15–20 min of distinct footage. That equals GWN's per-video unique footage. Reused across 2–3 follow-up videos, it matches GWN's whole output per event.
