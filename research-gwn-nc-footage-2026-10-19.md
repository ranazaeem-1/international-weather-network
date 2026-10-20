# Where GWN's North Carolina nor'easter footage comes from (forensic check, 19–20 Oct 2026)

**Question:** GWN's NC nor'easter videos have far more and better footage than IWN's Outer Banks video. Why, and where does GWN's footage come from?

**Short answer:** GWN did not find better footage of *this* storm. Its NC series is one library of about **11.7 minutes of footage** (62 source clips), recut six times into **99.6 minutes**. At least **83%** of that footage is from **earlier events**:
- the **23–27 September 2026 nor'easter**, which destroyed NC 12 on Pea Island and pushed the ocean through Rodanthe's streets
- the **1–2 February 2026 Buxton house collapse** (snow on the roof)

The remaining **17% is untraced**. **No GWN shot could be verified as footage of the 16–19 October storm.** GWN shows an on-screen "VIEWER ADVISORY: Some footage in this video is from previous nor'easter events" banner for about 8 seconds at a time, 3–4 times per video. Meanwhile:
- its narration says "The footage you just saw comes from North Carolina's Outer Banks where a nor'easter is pounding Hatteras and Ocracoke on Sunday, October 18th".
- its cold open tags the Feb 2026 house collapse "Outer Banks, NC · OCT, 2026".

---

## Method

**Videos analysed:** 6 GWN NC videos, analysed as 360p copies. P_6RvYzR6cY was also downloaded at 1080p for reading details.

**Shot detection and clustering**
- Shots were cut with ffmpeg scene detection (score 0.18 or higher).
- Repeated shots were grouped within each video using frame fingerprints.
- Shots were then pooled across the six videos in upload order.

**Second de-duplication pass**
- GWN re-crops and re-times the same clip in each video, so fingerprints alone miss many repeats.
- A second pass used ORB keypoint matching with RANSAC, plus visual checks. Pairs are on `pool/orbcheck_*.jpg` and `pool/manual_check.jpg`.

**Matching against other footage**
- Every distinct GWN shot was matched with ORB, scale- and shift-tolerant, against:
  - 13 of GWN's own September 2026 NC/East Coast nor'easter videos
  - 125 YouTube reference videos (news, ViralHog, Storyful, local creators, collapse videos 2022–2026, Hurricane Erin, Oct 2025 nor'easter)
  - IWN's 99 `clips/found` clips and the A Lil' OBX shorts
  - keyframes every 10 s from the three webcam livestreams IWN scanned: HurricaneTrack AYDmeQlOs2g, Carolina Weather Group RvzpUQVHupE and StormChasingVideo U10HMoa3MHo
- **Match threshold:** 20 or more RANSAC inliers. Every match used below was confirmed side by side by eye.

**Pitfall found and fixed**
- GWN's blurred side bars are tiled with "GWN" text. Comparing GWN against GWN therefore produced false matches with more than 200 inliers.
- Example: `M1_overlay_false_positive_example.jpg` shows GWN #16 matched to a school-bus shot.
- All final matches use a central crop (x 30–70%, y 8–80%) that excludes overlays.

**Scratch folder:** `C:\Users\hp\AppData\Local\Temp\claude\C--Users-hp-Desktop-international-weather-network\2d1f4672-c3e1-4152-a623-9de471c252d0\scratchpad\cmp_nc\`. Throughout this report, "`cmp_nc\`" means this folder.
- Scripts are in `py\`.
- Pool contact sheets are `pool\sheet_00..06.jpg`.
- 1080p frames are in `hd\`.
- Match tables are `m_gwnsep_n.json`, `m_ytall_n.json`, `m_yt2_n.json` … `m_yt5_n.json` and `m_gwnsep2_n.json`.
- Verdicts are in `verdicts.json`; the share calculation is `py\shares.py`.

**Evidence images** are in `cmp_nc\ev\final\`. In every image the GWN frame is on the left and the original is on the right.

| File | Shows |
|---|---|
| `E1/E2/E3_gwn_oct_vs_gwn_sept_*.jpg` | 56 October shots matched to GWN's own 26–30 September videos |
| `E4_gwn_vs_dated_third_party.jpg` | Matches to ABC7, USA TODAY, ABC News, FOX Weather, ViralHog, 13News Now and NY Post uploads |
| `E5_collapse_is_feb2026_buxton_snow.jpg` | GWN's cold-open collapse next to the Hunter Hicks / 13News Now (2 Feb 2026) and NY Post (4 Feb 2026) frames |
| `E6_man_wading_viralhog_sep25_2026.jpg` | GWN's man-wading shot next to the ViralHog upload ("Occurred on September 25, 2026, Rodanthe") |
| `E7_jeep_gwn_vs_abc_sep25.jpg` | GWN's Jeep shot next to ABC News's different Jeep take on the same street (25 Sep 2026) |
| `E8_viewer_advisory_banner.png` | GWN's on-screen advisory banner |
| `E9_untraced_items_hd.jpg` | The untraced shots at 1080p |

---

## 1. Composition of each GWN NC video

GWN has six NC videos. The sixth, cFZ6tOullGA (19 Oct 18:40 UTC), appeared during the check. No 19 Oct video added any new footage.

| Video (upload, UTC) | Length | Shots | Distinct shots in video | Median shot (10th–90th pct) | New footage vs earlier GWN NC videos | Average uses of each clip |
|---|---|---|---|---|---|---|
| wNCDK-l0oBw "HOMES COULD COLLAPSE" (18 Oct 15:38) | 12.1 min | 77 | 75 | 10.0 s (3–16.5) | **11.7 min (all of the library)** | 1.03× |
| m-tpSSrVTvc "Subtropical Risk" (18 Oct 18:48) | 15.1 min | 92 | 78 | 10.5 s (3–17) | 0 s (100% recycled) | 1.29× |
| YLkEjNJHoJQ "Oceanfront Houses Destroyed" (18 Oct 21:45) | 18.1 min | 117 | 83 | 9.0 s (2.8–16.5) | 0 s | 1.54× |
| P_6RvYzR6cY "14-Foot Waves Strike Hatteras" (18 Oct 23:00) | 20.1 min | 133 | 88 | 9.0 s (3–16) | 0 s | 1.73× |
| 8BQBdn4FCyk "STATE OF EMERGENCY" (19 Oct 01:00) | 22.1 min | 147 | 90 | 9.0 s (3–16.5) | 0 s | 1.90× |
| cFZ6tOullGA "1,700 People In Danger" (19 Oct 18:40) | 12.1 min | 76 | 67 | 9.0 s (2.75–17) | 0 s | 1.19× |
| **Pooled** | **99.6 min** | 642 | **75 distinct shots, 62 source clips, 11.7 min** | | | |

- The automatic fingerprint pool first counted 126 distinct shots and 16.3 min. ORB and visual checks showed that all 51 "new" shots in videos 2–6 are re-crops or re-timings of shots in wNCDK.
- Every GWN NC video uses 51–62 of the same 62 source clips. Longer videos simply repeat them more.

**What the footage is made of**
- **100% footage.** There are no maps, graphics or anchors; narration runs over the clips.
- **Natural sound is kept**, including eyewitness speech, for example:
  - "All right, we're back at the campground… overwash is not stopping"
  - "This guy's got waders on… higher than my 12-inch XtraTufs"
  - "Still covered midtown… completely covered in salt water"
- **Source types** (share of the 11.7 min of distinct footage, and of the 99.6 min runtime):
  - **Vertical phone video** (social reposts in GWN's blurred-sidebar box): **78%** of distinct footage (48 of 62 clips), 77% of runtime.
  - **Horizontal handheld eyewitness video:** 22% (14 clips).
  - **TV news footage** (helicopter, live shot, reporter or chyron): **0 clips.** Several of GWN's September clips were also distributed by TV networks through Storyful and ViralHog licensing (see §2), but GWN's copies carry no TV graphics.
  - **Webcams:** 0. Nothing matched the HurricaneTrack, Carolina Weather Group or StormChasingVideo streams.
  - **Drone:** 0. **Official agency footage (NPS, NCDOT, Dare County):** 0.
  - **Overlap with IWN's 99 `found` clips and the A Lil' OBX shorts:** 0.
- **Places shown:**
  - mostly Rodanthe: Ocean Drive and Mirlo Beach stilt houses, Rodanthe Pier, flooded side streets
  - a Hatteras-village soundside marina and the "Hatterasman" restaurant street
  - Jennette's Pier in Nags Head (cold open)
  - Buxton (the collapse)
  - Nothing obviously from another state or coast was found.

### The "VIEWER ADVISORY" banner (detected by template match at 2 fps)

The banner reads **"⚠ VIEWER ADVISORY — WARNING: Some footage in this video is from previous nor'easter events and may not depict current conditions. Viewer discretion is advised."**

| Video | Banner on screen | Where |
|---|---|---|
| wNCDK | 25 s (3.4%) | 0:54–1:02, 4:32–4:40, 9:04–9:12 |
| m-tp | 26 s (2.8%) | 0:54–1:02, 4:12–4:20, 9:04–9:12 |
| YLkE | 34 s (3.1%) | 0:54–1:02, 3:42–3:50, 8:33–8:41, 15:10–15:18 |
| P_6R | 34 s (2.8%) | same four slots as YLkE |
| 8BQB | 30 s (2.3%) | 0:02–0:07, 3:53–4:01, 8:10–8:18, 15:02–15:09 |
| cFZ6 | not detected | Possibly a changed layout; not checked by eye |

The banner never covers the cold open where the collapse plays, except in 8BQB at 0:02. The rest of the time the lower third reads "BREAKING NEWS".

**Labels that misdate the footage:**
- **P_6R cold open:** the Feb 2026 collapse carries an "Outer Banks, NC · **OCT, 2026**" tag. So do the Jennette's Pier shots.
- **YLkE:** the collapse opens the video with the word "Live footage." audible.
- **Same clips, earlier label:** GWN's 29–30 September videos tagged the same clips (#13 and #15/#74) "North Carolina, USA · **SEP, 2026**" (see E1 and E3).
- **Lower thirds about the September storm:** some lower thirds run over the September clips and refer back to that storm, for example "NOR'EASTER LEFT HOMES IN DEBRIS AND RIPPED APART AVON PIER" and "20-FOOT GAP LEFT IN AVON PIER AFTER LAST STORM".

---

## 2. Origins and dates of GWN's most prominent scenes

All times are in wNCDK unless noted. "In GWN's Sept videos" means the identical shot is in GWN's own uploads of 26–30 Sept 2026; the earliest is **XQLImnJG4wQ**, 26 Sep 00:20 UTC, with 757k views. That proves the shot is at least 19 days older than this storm.

| # | GWN time | Scene | Original or earliest copy found (uploader, URL, date) | Verdict |
|---|---|---|---|---|
| 0/4 | 0:00 and 0:23 (cold open of every video; "OCT, 2026" tag in P_6R 0:05) | Snow-roofed house collapsing into surf, seen from a neighbour's deck | **Hunter Hicks** via 13News Now "Raw video: OBX houses collapse into the ocean", youtube.com/watch?v=V6H-3UGpMCc, **2 Feb 2026** ("Video courtesy Hunter Hicks"); NY Post FdREoPZiCI4 (4 Feb 2026); ABC News guHqEqzA7wA (3 Feb 2026). Evidence: E5 | **Feb 2026 Buxton collapse** |
| 12 | 1:28; 8BQB 0:00 | Dark-brown three-storey stilt house in surf | USA TODAY 7xW3Vbtf7Do (**24 Sep 2026 19:00**); ABC7 Chicago kuk4qcr8sPM "Sept. 24, 2026" (24 Sep 18:52); FOX Weather 7sp6pQVVF_0 (25 Sep); GWN XQLImnJG4wQ (26 Sep) | **Sept 2026 nor'easter** |
| 11 | 1:14 | Overwash pouring between houses onto a road, black SUV | ABC7 Chicago kuk4qcr8sPM (24 Sep 2026); USA TODAY 7xW3 (24 Sep) | **Sept 2026** |
| 68/69 | 10:48 | Yellow stilt house, waves undercutting the scarp | USA TODAY 7xW3 (24 Sep); ABC News OgxYpHDlw7k (25 Sep 00:21); ABC7 Chicago. FOX Weather reused it as file footage on **18 Oct** (SbtkAqhEH84) | **Sept 2026** |
| 71 | 11:03 | Tall cream house, surf at the stairs | ABC7 Chicago (24 Sep); USA TODAY (24 Sep); USA TODAY vwdPOz0Cq_I (25 Sep) | **Sept 2026** |
| 70 | 10:54 | Overwash running down a beach road between dunes | ABC7 Chicago (24 Sep) | **Sept 2026** |
| 41 | 5:51 | **Man wading** in a waist-deep flooded street | **ViralHog** qMKfffEZPVk "Occurred on **September 25, 2026**, Rodanthe… Video credit **Jenni Koontz / Epic Shutter Photography**" (YouTube upload 9 Oct 2026); GWN YINrD6007Tg (28 Sep). Evidence: E6 | **Sept 25 2026** |
| 39/40 | 5:36 | Teal house, sand and overwash street | Same ViralHog upload (Jenni Koontz, 25 Sep 2026) | **Sept 2026** |
| 42 | 5:58 | Jeep driving through a flooded street with debris | Not matched. Same street, debris and light as #41. ABC News Ik_ODHmycMc (25 Sep 2026, "Jenni Koontz/Epic Shutter Photography via Storyful") shows a *different* Jeep take in the same Rodanthe flooding. Evidence: E7 | **Probable Sept 25 2026** |
| 18 | 2:46 | **Car buried** in surf and sand beside a house | In GWN's Sept videos (XQLImnJG4wQ 26 Sep, z40E, GV2F, YINr); original poster not found | **Sept 2026 or older** |
| 15/74 | 2:03, 11:55 | Flooded street at dusk with headlights ("still covered midtown… salt water") | In GWN's Sept videos (XQL 26 Sep); GWN tagged it "SEP, 2026" in i8LYD (29 Sep) | **Sept 2026 or older** |
| 16 | 2:17 | Flooded road, pedestrian-crossing sign, pickup ("one saving grace on the north end of town… water's flowing right through") | In GWN's Sept videos (XQL 26 Sep, z40E 27 Sep) | **Sept 2026 or older** |
| 46 | 7:01 | Flooded street outside the **HATTERASMAN** restaurant | In GWN's Sept videos (GV2F 28 Sep, YINr, z40E, J_Yg) | **Sept 2026 or older** |
| 45 | 6:45 | Pink-dusk overwash at a lit building ("we're back at the campground… overwash is not stopping") | In GWN's Sept videos (z40E 27 Sep) | **Sept 2026 or older** |
| 13 | 1:37 | Row of stilt houses in surf | GWN EF7GXcs8eXM (30 Sep, tagged "SEP, 2026"); CRISIS REPORT G9kimv0PiXU (26 Sep 03:47) | **Sept 2026** |
| 17/32/43 | 2:32, 5:03, 6:12 | Waves smashing under stilt houses, stairs with a red sign | GWN XQL (26 Sep); CRISIS REPORT (26 Sep) | **Sept 2026** |
| 33–37 | 5:12–5:23 | Close-ups of stilt-house pilings in surf | GWN z40E (27 Sep), YINr, J_Yg | **Sept 2026 or older** |
| 20 | 2:55 | Surf seen from inside a house, then a stilt house and debris on the beach | GWN XQL (26 Sep) | **Sept 2026 or older** |
| 21 | 3:06 | Overwash through sand fencing into a street | GWN XQL (26 Sep); USA TODAY vwdPOz0Cq_I (25 Sep) | **Sept 2026** |
| 23 | 3:33 | People walking in a flooded beach road under red flags | GWN 3_UdHwx5Q2g (27 Sep) | **Sept 2026 or older** |
| 5 | 0:35 | Pier pilings hammered by surf | Disasters Watch dVGJ8SpxBiY ("Outer Banks, USA · SEP 25", 25 Sep 2026); GWN XQL | **Sept 2026** |
| 66/67 | 10:42 | Rodanthe Pier building and gate | GWN i8LYD (29 Sep), EF7G | **Sept 2026 or older** |
| 44/53 | 6:30, 8:44 | Grey stilt house with deck, surf underneath | FOX Weather 7sp6pQVVF_0 (25 Sep 2026); GWN z40E | **Sept 2026** |
| 54 | 9:00 | Man in waders on flooded soundside docks ("High tide's not for another hour… higher than my 12-inch XtraTufs") | Not in any GWN September video or reference | **Untraced.** Could be Hatteras-village soundside flooding on Sat 17 Oct, or the Sept 25 ferry-terminal flooding |
| 1/2/3 | 0:05–0:23 (cold open, "OCT, 2026" tag) | **Jennette's Pier**, Nags Head, in big surf | Not in GWN's September videos or any reference found | **Untraced** (possibly this storm; unverified) |
| 30 | 4:46 | CAT loader towing a pickup out of the surf beside a house | Not found | **Untraced** |
| 28/29 | 4:33 | Double red flags, sand fencing, surf at the fence | Not found | **Untraced** |

**No match was found to:**
- any Hurricane Erin (Aug 2025) clip (8 references checked)
- the Oct 2025 nor'easter (Live Storms Media Mirlo Beach and Buxton, 13News Now)
- the 2022 Rodanthe collapses (6 references)
- the Sept 2024 collapses (Storyful, ViralHog, Epic Shutter)
- the Sept–Oct 2025 or June 2026 Buxton collapses (about 20 references)

The only collapse GWN uses is the February 2026 one.

---

## 3. Answer, with numbers

### How much is this storm, and how much is older?

Based on the 62 source clips (11.7 min of distinct footage) and the 99.6 min of runtime across all six videos:

| Verdict | Distinct footage | Source clips | Share of runtime |
|---|---|---|---|
| **(a) Verifiably this storm (16–19 Oct)** | **0 min (0%)** | **0** | **0%** |
| (b) Sept 2026 nor'easter, confirmed by a dated third-party copy from 24–26 Sep | 3.2 min (27.5%) | 14 | 28% |
| (b) In GWN's own 26–30 Sep / 2 Oct uploads (at least 19 days old; almost certainly the September storm) | 6.0 min (51.1%) | 33 | 50% |
| (b) Probable Sept 2026 (the Jeep) | 0.2 min (2.0%) | 1 | 2% |
| (b) Feb 2026 Buxton collapse | 0.3 min (2.5%) | 1 | 2% (but it opens every video) |
| **(b) Total older events** | **9.7 min (83%)** | **49 (79%)** | **≈83%** |
| **(c) Untraced** | **2.0 min (17%)** | **13 (21%)** | **≈17%** |

- **Untraced clips:** the Jennette's Pier cold-open shots (×3), the red flag, the loader and pickup, the soundside waders, red flags and sand fence (×2), surf (×2), sea oats, beach debris (×2) and an under-pier shot.
- **Location:** essentially 100% is the Outer Banks; nothing was identified as another place.
- **The untraced 17%** contains the only *candidates* for footage of this storm: the Jennette's Pier surf, the soundside waders at a marina, and red flags on the beach. None appeared in GWN's September content. None could be verified, because X, TikTok and Facebook could not be searched (see below).

### Source platforms

- **About 78% vertical social video.** The September clips trace to local eyewitness accounts, chiefly **Jenni Koontz / Epic Shutter Photography**, whose Facebook reels are licensed through Storyful and ViralHog. Those reels were picked up by:
  - ABC News, USA TODAY, ABC7 Chicago and FOX Weather on YouTube, 24–25 Sep 2026
  - the ViralHog YouTube upload on 9 Oct
- **About 22% horizontal handheld clips.**
- **0% TV news footage, webcams, drone or agency footage.**
- **The collapse** came from Hunter Hicks's own video, published by 13News Now, NY Post and ABC News.
- **No credits.** GWN credits none of the footage. Its descriptions list only text sources: Dare County, WRAL, WITN, WXII and the Island Free Press.

### Which footage of THIS storm did GWN have that IWN's search missed?

**None that could be verified.** GWN's advantage is not a better search for this storm. It is:
1. **A bigger, older library.** GWN had built it for the September storm in 13 videos, 26 Sep – 2 Oct; XQLImnJG4wQ alone has 757k views. It reused that library under October titles, plus the February 2026 collapse.
2. **Willingness to present it as current.** That means "The footage you just saw comes from… Sunday, October 18th" and "OCT, 2026" tags, with only intermittent 8-second advisories.
3. **Recutting the same 11.7 min six times,** with about 10-second shots, 100% footage and natural sound left in.

**This storm was a weak footage producer by GWN's upload time.** wNCDK went up on Sun 18 Oct at 11:38 EDT. By then:
- Island Free Press reported no overwash at Saturday's midday tide, only blowing sand and foam on Pea Island.
- Island Free Press reported only minor soundside flooding in Hatteras on Saturday evening.
- NC 12 stayed open into Sunday afternoon.

So none of GWN's dramatic scenes (houses in surf, overwash through Rodanthe streets, the man wading, the buried car) can be from this storm.

**This storm's footage that was on YouTube, which GWN did not use:**
- Island Free Press "Sunday, October 18, 2026" (BcJtUyvE_-s, 15 s)
- WAVY "Coastal storm impacts the Outer Banks" (uui9F6HU0-E; IWN already has it)
- WAVY Ocracoke ferry passenger (-iZZfeKN4cc)
- FOX Weather "Gusty Winds And Choppy Waves…" (KI0V17PawVA, 19 Oct 03:00 UTC, and lfqwhqi4x7s, 19 Oct 12:00 UTC)
- PositivityMePlease "Nor'easter on Nags Head OBX" (Y1aPI2tWQZU, 19 Oct 17:14 UTC)
- HurricaneTrack livestreams for 10/18 (SMhXEMlK95Q) and 10/19 (slM00Ae5JiM)
- the Carolina Weather Group LIVE CAMS stream eXTl19l9FqE

IWN's library came from the 17 Oct HurricaneTrack, Carolina Weather Group and StormChasingVideo streams, plus two A Lil' OBX clips. It is genuine footage of this storm and shares no clip with GWN's.

---

## Not verified / limits

- **Social platforms could not be searched.** X needs a login; I did not log in. TikTok search showed a CAPTCHA, and I stopped there. Facebook and Instagram need a login. So the original posts of the untraced 17% (Jennette's Pier, waders, loader) were not found. Their platform is unknown.
- **How old the "GWN Sept" clips really are.** Being in GWN's 26–30 Sep uploads proves a clip is older than this storm. It does not prove the exact event date: GWN could have reused even older clips in September. Many sit in sequences with clips dated 24–25 Sep 2026 (same Rodanthe houses and streets), so the September storm is the likely date.
- **Livestreams not scanned.** The HurricaneTrack 10/18 and 10/19 streams and the CWG eXTl19l9FqE stream were found late and not scanned. The three streams IWN used were scanned (every 10 s) with no match.
- **Coverage of GWN's September uploads.** 13 of GWN's September uploads were matched (9 NC-specific and 4 multi-state compilations). Any unchecked September uploads could still contain some of the untraced shots.
