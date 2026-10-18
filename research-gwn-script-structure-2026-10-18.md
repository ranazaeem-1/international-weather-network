# GWN narration structure, reverse-engineered, plus a fix for IWN

Research date: 18 October 2026. Sources: YouTube auto-captions (`.en-orig.json3`, with word timing) and `.info.json` chapters for 10 Global Weather Network (GWN) videos and 4 Independent Weather Network (IWN) videos. IWN's `narration.md`, `edl.json` and `facts.csv` files were also read. No episode or pipeline files were changed.

Scripts and intermediate files are in the session scratchpad (`scratchpad/gwnscripts/`):

- `blocks.py` splits the captions into timed speech blocks.
- `recon.py` rebuilds the clean narration (the output is in Appendix A).
- `nstats.py` computes the pacing statistics.

---

## 0. Summary

1. **GWN's unit is "one paragraph, then one clip break".** Every chapter is a single block of narration, about 55–90 words read for 20–30 s, followed by about 23–38 s of raw clip with its own sound. Then the next chapter starts. Within one video every block is about the same size, so chapter lengths are nearly equal (43 s, 50 s, 53 s or 65 s, depending on the video).
2. **IWN's unit is different.** IWN chops each chapter into three paragraphs of 1–2 sentences each (about 23 words, about 9 s). Each paragraph is followed by a 17 s break, because `make_narration.py` renders one audio file per paragraph. The viewer hears a sentence and a half, then 17 s of footage, then the next sentence and a half. Across a video that makes about 40 fragments, against GWN's 14–25 complete paragraphs. This is the main reason the narration "doesn't make sense". Each thought is cut off before its explanation arrives.
3. **GWN does not end its blocks on cliffhangers. It ends them on a hand-off ("baton") line.** The last sentence of a block names the next block's subject in concrete terms (a place, an object or a number), and the next block's first sentence picks up that exact word. IWN's earlier GWN analysis (5 Oct) recorded these as "cliffhanger lines". As a result, IWN writes vague teasers ("And it came at a cost.") at the end of almost every paragraph.
4. **GWN puts no subscribe or like calls in its narration.** The only retention call it uses is a single "Stay with us, because [a specific payoff later in the video]" in the opening paragraph (4 of 10 videos). IWN joins its calls to action (CTAs) to story hooks with "Because…", which produces nonsense: subscribe, *because the fire would explode*.
5. **The same structure works for fires and floods.** Floods add victim-by-victim chapters and an accountability thread, and the "why" chapter becomes the payoff of the opening question.
6. Section 6 is a fill-in template for 16–18 min and 1,300–1,600 words: 17 equal chapters of about 80 words, each followed by a 25–30 s break. Section 7 rewrites the start of the Norte Fire script in that template, using only facts from `facts.csv`.

---

## 1. Data and method

| Channel | Video | Topic | Length |
|---|---|---|---|
| GWN | `Aw0nrvtMUr0` | Norte Fire, "Malibu HIT by WILDFIRE, 16,000 ordered to evacuate" | 16:00 |
| GWN | `QJM8c2cevA4` | Bryson Fire, "LA UNDER SIEGE" | 25:03 |
| GWN | `lCR1ryuJHDs` | Norte Fire, "LOS ANGELES BURNING, 46X in 3 hours" | 12:06 |
| GWN | `5SOrKXWV_Ys` | 3 wildfires (Henderson, Peak, Bryson) | 10:05 |
| GWN | `JpfAKzf2LCc` | 3 wildfires, 120,000+ without power | 18:05 |
| GWN | `2vcv3Buai74` | 3 wildfires, 1,000+ acres | 15:05 |
| GWN | `3OAlVFwN61Y` | Turkey slammed, second wave | 15:09 |
| GWN | `q2BeGUu-9k4` | Turkey orange alert | 17:08 |
| GWN | `y_o9xAJaTfM` | São Paulo flash flood, tunnel and court case | 18:23 |
| GWN | `zy8u5gObPbo` | Brazil flooding, cyclone and Uruguay River | 15:16 |
| IWN | `VMWI72S7kp8` | 3 wildfires (Malibu script) | 17:32 |
| IWN | `9SnWUC0iIAU` | Norte Fire | 18:34 |
| IWN | `9qvtZhVUEwk` | Camp Pendleton | 17:06 |
| IWN | `Fa0pKDdD3fE` | Turkey (15 Oct script) | 23:19 |

**How narrator and eyewitness speech were separated.** The captions mark speaker changes with ">>". A speech run of 40 or more words with no pause longer than 2.5 s was classed as GWN narration. Short exclamations and walkie-talkie or reporter audio were classed as clip sound. Three long eyewitness runs were excluded by hand, and one narration block that the captions had split was merged back together. For IWN the threshold was 15 words, because its paragraphs are short.

**Caveats.** Auto-captions misspell names (for example "Kevin Federman", "chaperel", "2,80 acres"). The obvious errors are corrected in Appendix A and the uncertain ones are flagged. Times are ±0.5 s.

---

## 2. Measurements: GWN vs IWN

| Video | Length | First narration at | Narration blocks | Narration words | Words per block (median) | Narration per block | Clip break (median, IQR) | Narration share of runtime | Mean sentence length |
|---|---|---|---|---|---|---|---|---|---|
| GWN Aw0n Norte | 16:00 | 0:22 | 17 | 1,143 | 68 | 24 s | 30 s (28–32) | 43% | 14.3 words |
| GWN QJM8 Bryson | 25:03 | 0:20 | 23 | 1,982 | 85 | 29 s | 36 s (35–38) | 46% | 15.9 |
| GWN lCR1 Norte | 12:06 | 0:17 | 16 | 912 | 56 | 20 s | 24 s (24–26) | 46% | 14.4 |
| GWN 5SOr 3 fires | 10:05 | 0:20 | 14 | 780 | 56 | 20 s | 23 s (22–23) | 46% | 13.4 |
| GWN JpfA 3 fires | 18:05 | 0:20 | 17 | 1,275 | 75 | 26 s | 38 s (37–39) | 41% | 14.7 |
| GWN 2vcv 3 fires | 15:05 | 0:20 | 17 | 1,225 | 73 | 25 s | 28 s (27–29) | 47% | 14.9 |
| GWN 3OAl Turkey | 15:09 | 0:21 | 18 | 1,250 | 71 | 24 s | 26 s (24–27) | 48% | 14.1 |
| GWN q2Be Turkey | 17:08 | 0:21 | 19 | 1,353 | 71 | 24 s | 30 s (28–32) | 45% | 13.9 |
| GWN y_o9 São Paulo | 18:23 | 0:21 | 19 | 1,543 | 82 | 28 s | 29 s (27–31) | 48% | 12.2 |
| GWN zy8u Brazil | 15:16 | 0:21 | 17 | 1,178 | 70 | 24 s | 29 s (28–31) | 44% | 13.5 |
| **IWN VMWI 3 fires** | 17:32 | 1:00 | ≈37 | 850 | 23 | 9 s | 18 s (18–20) | 31% | 16.7 |
| **IWN 9SnW Norte** | 18:34 | 1:00 | ≈40 | 1,001 | 23.5 | 9 s | 17 s (17–19) | 34% | 15.1 |
| **IWN 9qvt Pendleton** | 17:06 | 1:00 | ≈32 | 757 | 23.5 | 9 s | 18 s (18–20) | 28% | 16.5 |
| **IWN Fa0p Turkey** | 23:19 | 1:00 | ≈45 | 979 | 21 | 10 s | 17 s (17–20) | 33% | 21.3 |

What the numbers say:

- **Speaking speed is not the problem.** GWN reads at about 2.8–2.9 words/s and IWN at about 2.6. Sentence length is also similar, about 14 words for GWN and 15–17 for IWN. The exception is the old Turkey script, at 21 words per sentence.
- **Block size is the problem.** A GWN block is 3–4 times longer than an IWN block. GWN has about half as many breaks, and each break is longer.
- **IWN has a thinner narration track.** At the same runtime, IWN carries about 42–54 narration words per minute of video, against GWN's 70–84. A 16–18 min GWN video carries 1,150–1,550 narration words, which matches the 1,300–1,600 target.
- **GWN's chapter period is nearly constant within a video.** Chapter start times are spaced 43 s apart (5SOr), 50 s (3OAl), 53 s (2vcv), 57 s (y_o9) and 65 s (QJM8, JpfA). Runtime is therefore about 20 s + N × (block + break).

---

## 3. GWN's structure template

### 3.1 Cold open

- **Length is 17–22 s every time.** In most videos it is an "Untitled Chapter 1" running from 0:00 to 0:20.
- **What plays:** one or two of the strongest raw clips, with their natural sound (flames or water, plus eyewitness exclamations). There is no narration, music or title card.
- **How narration enters, at about 0:20:** the first sentence points at the footage and names place and date in the same breath. This happens in 9 of 10 videos. Patterns seen:
  - "This footage comes out of / from [place], where on [weekday, date] …" (5SOr, JpfA, 2vcv, y_o9, zy8u)
  - "The images you just saw come from [city], where …" (3OAl)
  - "[What you] just watched was filmed in [city] …" (q2Be)
  - "This footage was filmed [weekday, date] in [city], where …" (lCR1)
  - "The flames in this footage are burning in [place] …" (QJM8)
  - The one exception starts on the date: "On Friday, October 16th, a wind-driven wildfire broke out in…" (Aw0n)
- **Footage references after the opening are rare.** One later example is "Much of the footage from that evening was filmed here" (JpfA, 2vcv).

### 3.2 The opening paragraph

The opening is 56–85 words (20–30 s), the same size as every other block. It follows the same order every time:

| # | Beat | Typical length | Real examples (short) |
|---|---|---|---|
| 1 | **Footage anchor + where + when** | 1 sentence | "This footage comes out of São Paulo, where a violent storm…" |
| 2 | **What happened + speed or scale number** | 1 sentence | "within 3 hours, it had torn across more than 400 acres"; "11 days of normal rain in 40 minutes"; "heaviest rain… since 1942" |
| 3 | **Human stakes number** | 1 sentence | "16,000 people were ordered to leave"; "more than 7,000 structures sat in the threat zone" |
| 4 | **Severity label** (fires; used once) | a clause | "a devastating, life-threatening…"; "a very life-threatening situation" |
| 5 | **Widening** (it isn't over or isn't the only one) | 1 sentence | "the winds driving them have not peaked"; "only one front of a much larger battle" |
| 6 | **Open loop** pointing to a specific later chapter, sometimes as "Stay with us because…" | 1 sentence | "the reason those creeks turned so deadly may be sitting right on their banks" |

**The open loop always pays off with a real fact later in the video:**

| Video | Loop | Payoff |
|---|---|---|
| 3OAl | "the reason… may be sitting right on their banks" | Construction in stream beds chapter, at 80% |
| q2Be | Demolitions "for a reason" | Same, at 70–75% |
| y_o9 | "that tunnel has flooded before… 1999" | 1999 chapter, at 33% |
| zy8u | "clear skies won't mean safe ground" | Soaked soil can still slide, at 84% |
| 5SOr, JpfA, 2vcv | "the bigger danger may come after the flames are out" | El Niño and mudslides, at about 90% |
| QJM8 | "what scientists expect next could hit Los Angeles even harder" | El Niño, at 72% |
| Aw0n | "only one front of a much larger battle" | Henderson, Peak and Bryson chapters, at 63–86% |

### 3.3 Chapter arc

These sequences come straight from the chapter lists and blocks.

**Fire videos.** Aw0n, lCR1, QJM8, 5SOr, JpfA and 2vcv all follow this order. Positions are approximate shares of runtime:

| Order | Section | Position | Notes |
|---|---|---|---|
| 0 | Cold open (clips only) | 0–2% | 20 s |
| 1 | Opening paragraph | 2–5% | see 3.2 |
| 2 | **Ignition + "why this place matters"** | 5–10% | Fire name, start time, landmark. Then a geography explainer: "San Clemente sits at the very southern tip of Orange County…" or "To understand why that matters, picture the town." |
| 3 | **Growth timeline by the clock** | 10–15% | Acreage at each time ("10 acres… half an hour later, 50… by 2:40, 465"), plus the mechanism (embers carried a mile ahead) |
| 4 | **First damage** (homes, the worst-hit town) | 15–22% | Number of homes plus an agency attribution |
| 5 | **Evacuations** (numbers, what the order means, where people went) | 20–28% | "In California, an evacuation order means an immediate threat to life." |
| 6 | **Firefight** (crews, aircraft explained, injuries, containment) | 25–35% | Super Scoopers are explained in two sentences |
| 7 | **The science: Santa Ana mechanism + the 2025 firestorm** | **28–46%** | Always one block, always this pairing. Usually set up by a baton about the wind. |
| 8 | Knock-on impacts (roads, I-5, trains, water, power cuts, air quality, heat) | 40–65% | One impact per block |
| 9 | Wider context (other fires, each with distance and direction) | 55–80% | "About 20 miles south…" |
| 10 | Official response (governor, FEMA, pre-staging) | 60–85% | |
| 11 | History or recovery (earlier fires on the same ridges, 2025 aid) | 60–70% (long videos only) | QJM8 only |
| 12 | **What's next** (burn scars → debris flows → El Niño wet winter); usually the payoff of the opening loop | 85–95% | |
| 13 | **Status recap**, starting "As of [time], [date]…" | last block | see 3.9 |

**Flood videos (3OAl, q2Be, y_o9, zy8u)** follow the same skeleton. Only the content of the slots changes:

1. Cold open, then the opening paragraph with its loop.
2. **Today's alert or what is coming now** (orange alert, the next storm).
3. **Geography + how much rain, with a US comparison.** Examples: Istanbul is split by the Bosphorus; one district "more than a quarter of Chicago's yearly rain"; "São Paulo's version of Central Park".
4. **Deaths, one victim per sentence or block,** with age, place and what happened, then **the missing**.
5. **Damage** (homes, hospitals, metro, airport), then other provinces or cities (each with distance and direction).
6. **Why it got so bad.** This is the human or structural cause (buildings in creek beds, concrete, a protocol that failed) and the payoff of the loop, at 70–85%.
7. **Accountability.** Examples: a broken 2009 promise, demolitions, aid payments, prosecutors; or governor vs mayor and the court case.
8. **Forecast and secondary hazard** (wind, landslides, a river crest), then the "As of" recap.

São Paulo (y_o9) runs the middle as one causal chain: tunnel → 1999 → governor → mayor → prosecutors → judge → Rio → forecast. It is still one block per chapter with baton links.

### 3.4 Section length

- **Every section is one block of the video's standard size.** There are no long or short chapters. The science chapter, the opening and the recap are all the same length as the rest.

| Videos | Words per block | Seconds per block |
|---|---|---|
| lCR1, 5SOr | 51–61 | 19–22 s |
| Aw0n, 3OAl, q2Be, zy8u, 2vcv | 63–75 | 21–27 s |
| QJM8, JpfA, y_o9 | 76–94 | 24–34 s |

- **The clip break after each block is 23–38 s.** As a rule of thumb, break length ≈ block length + 0–10 s.
- **Chapter count:** 14 for a 10 min video, 17–20 for 15–18 min, and 23 for 25 min.

### 3.5 How narration refers to the footage

- Only the opening sentence references the footage explicitly. GWN never describes clip actions (nothing like "in this video a resident films…").
- The narration is written at story level: events, numbers, explanations. Any clip of the same event can sit under it.
- The eyewitness audio in the breaks carries the emotion, with lines like "we're about to lose everything", "get out of town". This is why GWN can reuse its strongest clips several times per video.
- GWN never lists things that need a specific picture: no zone codes, street lists or shelter addresses.

### 3.6 Transitions and hook devices

1. **Baton hand-off (in almost every block).** The last sentence names the next subject concretely, and the next block's first words repeat it.
   - "…the worst of it was waiting inside a tunnel downtown." → "The Anhangabaú tunnel runs beneath…"
   - "…because the wind that started all this had not let up." → "That wind is the Santa Ana."
   - "Containment was still zero." → "Firefighters refused to back off overnight."
   - "East of the city, the destruction took a different shape." → "In Sakarya province…"
   - "…the hardest news is the news that has not come." → "Three men are still missing…"

   The baton is usually a full informative sentence that already contains a fact. It is rarely a three-word teaser.
2. **Pronoun or keyword pickup at the start of a block:** "That wind is…", "Those embers…", "That fire closed…", "That province is…", "Those conditions were extreme."
3. **Contrast pivots:** "Still,", "However,", "But…", "Even so,", "Yet,". Often there are two per block, one in the middle and one in the baton.
4. **Place pivots that state distance and direction:** "About 20 miles south…", "about 93 miles east…", "a few hundred miles up the coast…", "Far to the south…", "Back in São Paulo, though…".
5. **Questions,** answered at once in the same block or in the next sentence: "How fast did it happen? [Mayor] said…", "So, why did this get so bad?" Only occasionally does a question end a block ("Did it work?").
6. **"To understand why, look at a map" / "picture the town".** This sets up an explainer.
7. **One opening loop per video** with a real payoff (3.2). Small loops open and close within 1–2 blocks.

### 3.7 Language

- **Sentence length:** mean 12–16 words. Most blocks contain one or two 3–6 word punch sentences ("It grew fast." "It worked." "That is where people died.").
- **Vocabulary:** plain, about 8th-grade level, with one strong verb per sentence ("tore", "charged", "squeezed", "swamped"). Adjectives are restrained. The severity phrase ("devastating, life-threatening") appears once, in the opening. There is no purple prose; compare IWN's old Turkey line "torrential convective storms… inundating metropolitan Istanbul".
- **Tense:**
  - Past tense for the narrative.
  - Present or present perfect for the current state ("is still burning", "remain in place").
  - Present "says" for attribution.
  - Modals for forecasts ("could", "should", "is expected").
  - Days are given as weekdays ("on Thursday", "Friday night"). The full date appears only in the opening and the recap.
- **Explaining terms in place.** A definition goes straight after the term, separated by commas: "retardant, a chemical that slows flames"; "a spot fire, a new blaze started by flying embers"; "level three, known simply as go". Meanings are spelled out: "0% contained. That means crews had not secured any part of its edge."
- **US-audience comparisons:**
  - "about the size of Rhode Island"
  - "faster than most people drive on the interstate"
  - "Like New York, São Paulo has both a governor… and a mayor…"
  - "a bit like a state attorney general here"
  - "much like a nor'easter"
  - "like a flood wave rolling down the Mississippi"
  - "shed water almost like a parking lot"
- **Numbers:**
  - Rounded with "about / roughly / nearly / more than".
  - Given as clock-time sequences.
  - Converted to US units (in, ft, mph, °F, $).
  - Time-stamped: "as of Saturday's latest update", "so far", "at last report".
- **Attribution:**
  - Usually at the start of the sentence: "The Orange County Fire Authority says…", "Cal Fire mapped it at…", "Mayor Ricardo Nunes said…".
  - Sometimes at the end: "…according to the Los Angeles County Fire Department."
  - People get title + name. There are only 1–2 short direct quotes per video. Unsourced claims are rare.

### 3.8 Rhythm between narration and clips

GWN runs a steady pattern: narration 20–30 s → clip 23–38 s → narration … There are no mid-chapter breaks and no one-sentence blocks. Narration covers 41–48% of runtime. Every break starts on a complete thought, so after 30 s of clip the viewer comes back to a sentence that picks up the last named subject.

### 3.9 Ending formula

The final block is the same size as the others and follows this order:

1. "**As of** [Friday night / Saturday], [Month day]," followed by the main event's current numbers (acres and containment, deaths and missing, homes).
2. What is **still in effect** (evacuation orders, warnings, school closures).
3. One **official's urging or line** ("urging residents to follow those orders because the wind can change").
4. A sentence on the **secondary areas**.
5. A last line looking ahead, tied to a time or a threat: "…the Santa Ana winds will not ease until Saturday"; "the next test… could come within days."

There is no subscribe call, no sign-off and no "stay safe". Then 5–30 s of clip runs out the video.

### 3.10 Fires vs floods

The mechanics are identical:

- 20 s cold open
- footage-anchored opening with a loop
- one block per chapter
- equal chapter lengths
- baton transitions
- explanation in place
- an "As of" recap

The differences are in content: victim-by-victim and missing-person chapters replace the acreage timeline, an accountability thread replaces "official response", and the why-chapter comes late as the loop's payoff.

### 3.11 Reused explainer blocks

GWN reuses paragraphs across its "Latest Updates" videos on the same event. The Santa Ana + 2025 block, the El Niño block and the Peak Fire block are almost word for word the same in 5SOr, JpfA and 2vcv. GWN keeps evergreen blocks (science, history, what's next) and rewrites only the news blocks. IWN could keep a small library of its own reusable explainer blocks.

---

## 4. Why IWN's narration "does not make any sense"

Examples come from `2026-10-17-socal-norte-fire/script/narration.md` (captioned as `9SnWUC0iIAU`), plus the Turkey, São Paulo and Malibu scripts and `edl.json`. They are ordered by impact.

### 4.1 Paragraph fragments separated by 17 s of footage (biggest cause)

`make_narration.py` creates one audio file per blank-line paragraph, and `gen_edl.py` places a 16–18 s break after each one. Every IWN section has three 1–2 sentence paragraphs, so the viewer gets 9 s of narration, then 17 s of clip, about 40 times per video.

Example: S04 ends "Residents loaded their cars and drove out of the hills as smoke filled the sky. So where did all of those people go?" Then comes 17 s of footage, then a list of three venue names (S05). The question, the break and the answer are three disconnected units. GWN never breaks inside a thought.

### 4.2 A teaser line at the end of nearly every paragraph, with small payoffs

Every section except the last (12 of 13) ends on a teaser, and so do many paragraphs in the middle of sections:

- "And then the fire reached the neighborhoods."
- "But thousands of people were already being told to leave."
- "And it came at a cost." The payoff is that two firefighters were treated, one for heat exhaustion.
- "And the freeway was not the only route that was cut."
- "But how long will this danger last?" The answer is a Red Flag Warning until Saturday evening.

Turkey has the same pattern: "And the search was not over." and "But for some families, help came too late." Teasers that oversell, repeated every 30 s, make viewers distrust the narration.

GWN's version is a baton: a concrete, informative last sentence that the next block picks up word for word.

### 4.3 CTAs joined to the story with "Because"

- S01: "…subscribe and turn on notifications if you live anywhere in California. Because within a few hours, the Norte Fire would explode."
- S05: "…hit like and share it with them. Because the fire was about to cut off one of California's busiest highways."
- Turkey S05: "…hit like so more people see these warnings. Because in Sakarya, the damage was even more widespread."
- São Paulo S04: "…share it with someone in Brazil. Because downtown, the water was pouring underground."

Read literally, the next plot point becomes the reason to subscribe. That is exactly the kind of line people call nonsensical. Each script has four spoken CTAs, and the first comes after only two narration paragraphs. GWN has no subscribe or like lines in narration. Its only retention line is an opening "Stay with us, because [what you'll learn]", where the "because" is a real reason to keep watching.

### 4.4 A generic, multi-place opening with no anchor

- S01 opens: "California is under fire. From Malibu to Camp Pendleton to the hills of south Orange County…" That is three places before the viewer learns which fire this video is about.
- There is no footage anchor, no date in the first sentence, no speed number and no open loop. The first spoken fact arrives at 1:31.
- The cold open lasts 60 s without narration, against GWN's 20 s. It also includes a Malibu clip (`F046_Malibu_BrysonTallFlames`) in a Norte Fire video.

### 4.5 Missing "why" and missing meaning

- **The Santa Ana wind is explained only in S12, at about 15:50 (85% of runtime).** GWN explains the wind at 28–46% and the ember mechanism in the growth chapter.
- **"Zero containment" is never explained.** "Between 465 and 570 acres" is never explained either. It is a conflict between sources (facts N02) presented as a range.
- **The script has lists that mean nothing to viewers and need visuals it doesn't have:** "zones twelve and thirteen… zones four, five and ten", three shelter venues, and three street names in S03. GWN instead tells viewers what an evacuation order means and that the area is legally closed.

### 4.6 Jumps between places and confusion about causes

- **Which fire closed I-5 is unclear.**
  - The S05 hand-off says the Norte Fire "was about to cut off one of California's busiest highways".
  - S06 then describes the Vandergrift–Basilone closure, which `facts.csv` N08 files under "I-5 Camp Pendleton".
  - S10 says the Henderson Fire "first closed Interstate Five on Thursday".

  The viewer cannot tell which fire closed the freeway.
- **Place jumps come without bearings.** S07 (San Onofre trains, Scales Fire) and S11 (Malibu, then statewide power) arrive with no distance or direction. GWN would say "about 20 miles south…" and give one line on why the place matters.

### 4.7 Generic filler in place of facts or explanation

- "Plumes of smoke towered over the coast and could be seen for miles."
- "Many families left with only minutes to pack, not knowing whether their homes would still be standing…"
- "On the ground, the heat and the wind made that work brutal."
- "Residents loaded their cars and drove out of the hills as smoke filled the sky."

None of these is in `facts.csv`, and any fire could use them. The old Turkey script (`Fa0pKDdD3fE`) is worse: 21-word sentences such as "…leaving millions across the Marmara region navigating dangerous flash floods and structural collapses."

### 4.8 Narration that doesn't match the footage

From the `edl.json` shot lists. This was checked by shot order only, not frame by frame:

- S01's narration shots are `F072_SanClemente_PyroCloud`, `F088_LagunaNiguel_BigPlume`, `F021_Malibu_BrysonNightFlames` and `F046_Malibu_BrysonTallFlames`. So half the footage under "The most destructive so far is the Norte Fire… San Clemente… Friday morning" is Malibu at night.
- The S05 shelter list plays over Dana Point street and church smoke clips. No shelters are shown.
- The S07 train narration plays over coastal smoke at Dana Point and Camp Pendleton. No trains are shown.

The specific nouns in IWN's script (venues, trains, zones) promise pictures the footage pool doesn't have. GWN avoids this by writing at story level.

### 4.9 No status recap at the end

S13 contains the FEMA grant, the cause still under investigation, the Red Flag Warning, then subscribe and a sign-off. It never restates where things stand (acres, containment, homes, evacuations). GWN always closes with an "As of…" block.

### 4.10 Thin narration track

IWN has about 750–1,000 words in 17–18 min, so narration covers only 28–34% of runtime. Ticker and pill loops fill long silent stretches, so the story feels like scattered captions rather than a report.

**Not a cause:** voice speed and average sentence length are close to GWN's in the new scripts.

---

## 5. Changes from earlier assumptions

- The 5 Oct measurement in memory ("~16 blocks of ~15–20 s, ~50 words, each ending on a cliffhanger, ~800 words, ~43% narration") was close on narration share. It undercounted the current GWN block size, which is 55–90 words and 20–30 s. It also mislabeled the baton as a cliffhanger.
- GWN's cold open is 20 s. IWN's is 30–60 s, a rule the user set on 5 Oct. Matching GWN "exactly" means changing that rule to 20 s, which is the user's decision. The template below assumes 20 s.

---

## 6. IWN script template (GWN structure)

**Targets:**

- 16–18 min runtime.
- 17 chapters. The cold open is not counted.
- Each chapter is ONE paragraph of 75–90 words, about 29–35 s at IWN's measured 2.6 words/s.
- Each chapter is followed by ONE clip break of 25–30 s with natural sound.
- Total narration is 1,330–1,550 words, including about 60 words of spoken CTAs.
- Chapter period is about 58–64 s, so runtime ≈ 20 s + 17 × 60 s ≈ 17.3 min.

**Format rule for `narration.md`:** write each `## Sxx` as a single paragraph with no blank lines inside. `make_narration.py` already renders one audio part per paragraph, so the break then falls after the whole block. No pipeline change is needed. Set the chapter tail to about 25–30 s where the episode's `gen_edl.py` sets `tail`.

### 6.1 Fill-in outline

Each line below gives the chapter, its purpose, a target word count, and fill-in slots in [brackets]. The example lines are original wording.

| Chapter | Words | What goes in it |
|---|---|---|
| **S00 Cold open** | 0 | 20 s. Use 1–2 of the strongest clips with natural sound, **all from the place named in S01's first sentence**. |
| **S01 Opening** | 80 | Footage anchor + place + full date → what happened + speed or scale number → human stakes number → (fires) one severity clause → widening line → open loop that a later chapter pays off with a real fact. Spoken CTA slot 1 may be the loop: "Stay with us, because [what the viewer will learn in Sxx]." |
| **S02 Where it started and why the place matters** | 80 | Event name, start time, landmark. One or two sentences on the place: what it is, who lives there, the one physical feature that matters (canyons, a creek, a tunnel, a valley). Use a US comparison if the place is foreign. Baton: name the next place or step. |
| **S03 How fast: timeline by the clock** | 80 | 3–4 time-stamped numbers ("At [time], [n]. By [time], [n]."). The mechanism in one sentence (embers, intense bursts of rain on concrete). Define one key term in place (containment, flash flood). Baton: the first damage. |
| **S04 First damage, at the worst-hit spot** | 80 | Name the hardest-hit place, the number of homes or deaths with an agency attribution, and one concrete detail from the facts. Fires: homes. Floods: victims, one per sentence with age, place and what happened. |
| **S05 People: evacuations, missing, shelter** | 80 | One headline number (people, homes), what the order means in plain words, where people went (as a category, e.g. "community centers in both cities", not addresses). |
| **S06 The response** | 80 | Crews, aircraft and equipment, with any unusual tool explained in one sentence. Injuries. Containment or search status. Baton toward the cause ("…and the wind that drove all of this had not let up."). |
| **S07 The turn or the night** | 80 | What changed at the next milestone: knockdown, evening numbers, a second wave arriving. Keep it chronological. |
| **S08 Why it happened (science)** | 85 | Spoken CTA slot 2: re-anchor, see 6.2. Then pick up the baton: the mechanism in 3–4 plain sentences (where the air or water comes from, why it is worse now), plus one history comparison with numbers. **This must land between 35% and 45% of runtime.** |
| **S09 Knock-on impact 1** | 80 | Roads, rail, airport. State clearly which event caused each closure. |
| **S10 Knock-on impact 2** | 80 | Power, water, air quality, heat or schools. One impact per sentence with a number. |
| **S11 Wider context A** | 80 | The second event. Open with **distance + direction + relation** ("About [n] miles [south], a second fire…"), then that event's own mini-timeline. |
| **S12 Wider context B** | 80 | The third event or the regional picture (other cities or provinces). |
| **S13 Official response** | 80 | Governor, state and federal steps (FEMA grant, declarations, pre-staging). Who did what, when, and what it pays for. |
| **S14 History or accountability** | 80 | Spoken CTA slot 3: re-anchor. Then: has this happened here before (dates, numbers), and what was promised or changed. Floods: planning failures, prosecutors, promises. Fires: earlier fires on the same ridges. |
| **S15 What's next 1: the forecast** | 80 | Warnings with end times, wind or rain amounts, the timing of relief. |
| **S16 What's next 2: the secondary hazard** | 80 | Usually the payoff of S01's loop: burn scars and debris flows, soaked soil and landslides, a river crest. Explain the mechanism. |
| **S17 Status recap** | 80 + 20 | "As of [day/time], [date], …" Repeat S01's key numbers updated, what is still in effect, one official urging, the secondary areas, and a last line looking ahead with a time. Then spoken CTA slot 4 as a **separate final sentence** of up to 20 words. |

**Word budget:** S01–S16 at about 80 words + S08 85 + S17 100 + two re-anchor CTAs at about 25 words each ≈ 1,450 words, within the 1,300–1,600 band.

**Flood variant** (same slots):

- S03: rainfall totals with a comparison.
- S04: deaths, then S05: the missing and the search.
- S06: rescue scale.
- S07: damage to homes and infrastructure.
- S08: why the rain was so intense, or why the city flooded (the drainage mechanism).
- S11–S12: other provinces or cities.
- S14: accountability (planning, prosecutors, broken promises).
- S16: landslides, river crest or the next storm.

### 6.2 Spoken CTA rules (four slots, none breaking the story)

1. **Slot 1, S01:** "Stay with us, because [a specific thing you'll learn later]." The "because" must give a real reason to keep watching. It must never point to the next plot beat. Do not say "subscribe" here.
2. **Slots 2 and 3, start of S08 and S14 (act breaks):** a **re-anchor CTA** of up to 2 sentences and about 25 words. It restates where and what with the latest number, then asks for the subscribe. Example: *"If you're just joining us, this is the Norte Fire in San Clemente: 16,000 people told to leave and still zero containment. Subscribe so the next update reaches you."* Then pick up the previous block's baton word. After a 27 s break the re-anchor also re-orients returning viewers.
3. **Slot 4, end of S17:** one closing sentence after the recap, for example: *"Subscribe and turn on notifications for the next update from Southern California."* A short sign-off is optional. The story is over by then, so nothing is interrupted.
4. **Never:**
   - Join a CTA to a story beat with "Because…", "So…" or "Now…".
   - Place a CTA as the last sentence before a break (except S17).
   - Put a CTA inside a timeline or casualty sequence.
   - Use "if this coverage is helping you…" lines.
   - Ask for comments mid-story.

   Comment prompts belong in a re-anchor slot or the close.
5. **Visual CTAs stay as they are:** subscribe pill, CTA ticker, like and bell animation in every chapter's clip break (memory rules from 16–17 Oct). They live in the breaks, so they no longer compete with narration.

### 6.3 Writing rules (checklist)

- [ ] Each chapter is one paragraph of 75–90 words. No blank lines inside a chapter.
- [ ] The first sentence of S01 names the footage's place and date, and the cold-open clips match that place.
- [ ] One open loop in S01 is paid off by a real fact in a named later chapter. No invented suspense.
- [ ] Every block's last sentence is a **baton**: it names the next block's subject concretely (place, object, number or person) and is ideally an informative sentence in its own right. Ban the free-standing teasers "And it came at a cost.", "But that was just the beginning." and "And the search was not over."
- [ ] Every block's first sentence picks up the baton word ("That wind…", "That city…", "Those crews…").
- [ ] Every new place gets distance + direction + one line on why it matters.
- [ ] Every technical term gets a definition right after it ("containment, the share of the fire's edge crews have secured").
- [ ] Every number has a time ("by 6:45", "as of Saturday") and a source ("the Orange County Fire Authority says").
- [ ] Never list zone codes, street names or venue addresses. Put them in tickers or lower-thirds if needed. Describe categories instead.
- [ ] Sentences average about 14 words. Include one or two punch sentences per block. Use plain verbs and no stacked adjectives.
- [ ] Every sentence comes from `facts.csv`, is a definition, or explains a general mechanism. Mark conflicting facts honestly ("a later update put it at 570").
- [ ] When an event closes a road, say which event did it.
- [ ] The why-chapter (S08) lands at 35–45% of runtime. Don't hold it for the end.
- [ ] The final chapter starts with "As of [time], [date]" and restates the key numbers.
- [ ] Footage check: no sentence names something the footage pool can't show (trains, shelters) unless the line works over generic event footage.

### 6.4 Example baton and pickup pairs (original lines)

| Baton (end of block) | Pickup (start of next block) |
|---|---|
| "…and by nightfall, the smoke had settled over the freeway." | "That freeway is Interstate 5, the main link between…" |
| "Thirty miles inland, a second town was about to get the same storm." | "That town is…" |
| "The water drained in hours. The repairs will take far longer." | "The first estimates came on…" |
| "One number still had not moved: containment." | "Containment is the share of a fire's edge…" |
| "So why did an ordinary autumn storm do this much damage?" (as a block opener) | answered in the very next sentence: "Engineers point to…" |

---

## 7. Worked example: the start of the Norte Fire episode in the new structure

The old S01 and S02 (165 words in 6 fragments, with 2 teasers and 1 CTA) are redistributed into three full chapters below. Every event fact comes from `episodes/2026-10-17-socal-norte-fire/research/facts.csv`, cited by row ID. Lines marked *(definition)* or *(mechanism)* explain terms and add no new event facts.

**S00, cold open (20 s, no narration):** use only San Clemente / San Juan Capistrano clips with natural sound, for example `U001_SanClemente_HomesBurningOnRidge` or `F003_SanJuanCapistrano_HouseFlames`. Do not include the Malibu clip `F046`.

**S01, opening (84 words, about 32 s):**

> This footage was filmed on Friday, October 16th, in San Clemente, California, where a wildfire broke out late in the morning. About three hours later, it had reached homes in San Juan Capistrano. By evening, around 16,000 residents were under evacuation orders, and the fire was still zero percent contained. Officials have confirmed six homes damaged or destroyed, but aerial images suggest the real number is higher. Stay with us, because the dry wind behind this fire was forecast to keep blowing through Saturday.

- Facts:
  - Start 11:33 (N01).
  - Homes off Via La Mirada at 2:37, so "about three hours" (N03).
  - About 16,000 residents under orders (N04).
  - 0% contained (N02).
  - Six homes, aerials suggest 8 or more (N03).
  - Easterly winds through Saturday (N13).
- Devices: footage anchor + place + date → speed → stakes → loop A (aerial count, paid off in S04) → loop B as CTA slot 1 (wind, paid off in S15). There is no subscribe line and no "because + plot beat".

**S02, where it started and why it spread (84 words, about 32 s):**

> It is called the Norte Fire. It started at 11:33 on Friday morning in San Clemente, close to Interstate 5, and the Orange County Fire Authority took command. The conditions were against the crews from the start. Gusty winds were blowing from the east, which here means dry air pushing out of the inland hills toward the ocean, and humidity was down in the teens. Air that dry pulls moisture out of everything it crosses. And this fire did not stay in San Clemente.

- Facts:
  - 11:33, San Clemente, near I-5, under the Orange County Fire Authority (N01).
  - Gusty easterly winds, very dry, humidity in the teens (N13).
- What "east wind" means and what dry air does: *(definition / mechanism)*.
- The baton names the next place without a teaser.
- Street names (Portico Del Norte / Eminencia Del Norte) moved to the lower-third.
- "Santa Ana" is not used, because `facts.csv` has no row for it. Add a sourced row first if the term is wanted here.

**S03, how fast it grew (78 words, about 30 s):**

> By the middle of the afternoon, it had pushed into San Juan Capistrano. At 2:37, reports came in of four homes affected off Via La Mirada. By 6:45 that evening, the fire was mapped at 465 acres, and a later update that night put it at 570. One number was the same in every report: zero containment. That means crews had not yet secured any part of the fire's edge. Meanwhile, the count of damaged homes kept climbing.

- Facts:
  - Four homes off Via La Mirada in San Juan Capistrano at 2:37 p.m. (N03).
  - 465 acres at 6:45 p.m., 570 in later updates, 0% in each (N02).
- The source conflict is now stated as a sequence instead of an unexplained range. Containment gets a meaning *(definition)*.
- The baton hands off to S04.

**S04 would open with the pickup:**

> "By 4:30, Orange County Fire Authority Division Chief Mark Backoff said six homes had been damaged or destroyed, most of them on the San Juan Capistrano side…"

It then pays off loop A with "aerial images suggest eight or more" (N03).

**Side by side:**

| | Old S01–S02 | New S01–S03 |
|---|---|---|
| Narration units | 6 paragraphs, each followed by a 17 s break | 3 blocks, each followed by a 25–30 s break |
| Words | 165 | 246 |
| Places in the first sentence | 3 | 1 |
| CTA | subscribe + "Because… would explode" | "Stay with us, because [real payoff]" |
| Terms explained | 0 | 2 (east wind, containment) |
| Teasers | 2 | 0, replaced by 2 batons |
| Conflicting acreage | given as an unexplained range | reported as two time-stamped updates |

---

## 8. Recommended next steps (not done; need the user's go-ahead)

1. Decide on the cold open: 20 s to match GWN, or keep IWN's 30–60 s.
2. Write the next episode's `narration.md` with one paragraph per chapter and set the chapter tail to about 25–30 s in that episode's `gen_edl.py`. Existing renderers then produce GWN-style rhythm unchanged.
3. Cut spoken CTAs to the four slots in 6.2 and keep the visual CTAs in every break.
4. Optional: keep a small library of reusable explainer blocks (Santa Ana + 2025, El Niño and burn scars, urban flash floods, PSPS power shutoffs). Each needs a sourced row in each episode's `facts.csv`.

---

## Appendix A: Reconstructed GWN narration (narrator only), with block and clip-break timings

Built by `recon.py`. Eyewitness speech, radio chatter and [music] tags were removed. Clip breaks are the gaps between narration blocks, and they hold the raw clips with natural sound. Obvious caption errors are fixed (chaparral, Santa Ana, El Niño, Azusa, Newsom, 2,080 acres, 1:15 / 2:40). Remaining misspellings, mainly Turkish and Portuguese place names, are left as the captions have them. Seven videos are included: four fire, three flood.

### Aw0nrvtMUr0 Malibu HIT by WILDFIRE — 16,000 Ordered to EVACUATE (Latest Updates) dur 960

- *[clip break 0:00–0:21, 22 s, natural sound/eyewitness]*
- **0:21–0:48 · 69 words · 27 s** — On Friday, October 16th, a wind-driven wildfire broke out in San Clemente, California. And within 3 hours, it had torn across more than 400 acres and into the homes of the next town over. The footage from that afternoon spread fast. So did the danger. 16,000 people were ordered to leave as a devastating life-threatening fire closed in. And it was only one front of a much larger battle.
- *[clip break 0:48–1:16, 28 s, natural sound/eyewitness]*
- **1:16–1:39 · 68 words · 23 s** — San Clemente sits at the very southern tip of Orange County, a surf town of hillside neighborhoods wedged between the Pacific and the open land of Camp Pendleton. The fire started around 11:30 in the morning just east of Interstate 5. Those hills are covered with grass and chaparral. Chaparal is dense brush that burns extremely hot once it dries out. And on Friday, it was bone dry.
- *[clip break 1:39–2:08, 30 s, natural sound/eyewitness]*
- **2:08–2:31 · 63 words · 23 s** — It was first reported at 10 acres. Half an hour later, it was 50. And by about 1:15, it covered 250. Then it nearly doubled again, reaching 465 acres by 2:40. Fire officials say Santa Ana gusts can carry embers a mile or more ahead of the flames. That is how this fire kept leaping past the crews trying to cut it off.
- *[clip break 2:31–3:03, 32 s, natural sound/eyewitness]*
- **3:03–3:29 · 71 words · 25 s** — Those embers pushed the fire north into San Juan Capistrano, a historic town best known for its old Spanish mission. That is where the flames reached houses. The Orange County Fire Authority says six homes were damaged or destroyed, most of them on the San Juan Capistrano side. Ground crews poured heavy streams of water onto threatened houses while air tankers dropped retardant overhead to stop the next row from catching.
- *[clip break 3:29–3:58, 29 s, natural sound/eyewitness]*
- **3:58–4:25 · 70 words · 27 s** — By Friday evening, about 16,000 residents and 6,000 homes were under evacuation orders and warnings in San Clemente and San Juan Capistrano. In California, an evacuation order means an immediate threat to life. It is a lawful order to leave now and the area is closed to the public. Emergency shelters opened at community centers in both cities while firefighters kept pushing back against the flames on the edge of town.
- *[clip break 4:25–4:53, 28 s, natural sound/eyewitness]*
- **4:53–5:17 · 65 words · 24 s** — More than 500 firefighters were fighting the Norte fire with extra crews sent from Los Angeles and San Bernardino counties. The work was brutal and dangerous. Two firefighters were hospitalized with significant injuries. And Orange County Fire Chief Kevin Federman [ASR spelling] says both are now in stable condition. Meanwhile, the flames kept testing the lines because the wind that started all this had not let up.
- *[clip break 5:17–5:43, 26 s, natural sound/eyewitness]*
- **5:43–6:09 · 71 words · 27 s** — That wind is the Santa Ana. It forms when high pressure builds inland and sends dry desert air rushing through the mountain passes toward the coast, drying out everything it touches. It shows up every fall right when the hills are driest. However, Southern California knows exactly how deadly it can be since in 2025, these winds drove a firestorm that killed more than 30 people and burned over 16,000 structures.
- *[clip break 6:09–6:37, 28 s, natural sound/eyewitness]*
- **6:37–7:01 · 66 words · 24 s** — By 5:45 on Friday, crews had knocked down most of the Norte fire. Still, the gusts kept blowing hard across the ridges, and firefighters spent the evening chasing embers and hot spots. Fire Authority Captain Steve Conaldi says the department helicopters will keep flying through the wind whenever there is a threat. And with this much dry brush still standing, the threat had not gone anywhere.
- *[clip break 7:01–7:32, 31 s, natural sound/eyewitness]*
- **7:32–7:53 · 65 words · 21 s** — For the people who live here, it came out of nowhere. One longtime resident, Robert Morris, said he has lived in the area since 1995, and this was the first time a fire had really come through. He called it a wakeup call. Many of his neighbors spent Friday night in shelters or with family, still waiting to learn whether their streets were still standing.
- *[clip break 7:53–8:22, 29 s, natural sound/eyewitness]*
- **8:22–8:45 · 68 words · 22 s** — The fire also squeezed the roads. The on-ramp from Ortega Highway to the southbound freeway was closed as well, and part of the northbound freeway shut down as flames moved toward it. The local water district even asked residents to cut back on water. Orange County Fire Chief TJ McGovern says crews have had no trouble getting water onto the fire and the request was only a precaution.
- *[clip break 8:45–9:15, 30 s, natural sound/eyewitness]*
- **9:15–9:40 · 68 words · 26 s** — The smoke turned into its own hazard. Air quality in San Clemente, Dana Point, San Juan Capistrano, and Laguna Niguel dropped to levels unhealthy for sensitive groups, a category that includes older adults and people with heart or lung disease. Officials told people to stay indoors and wear N95 masks outside. On top of that, a heat advisory runs until 8 on Saturday night with highs near 95.
- *[clip break 9:40–10:12, 32 s, natural sound/eyewitness]*
- **10:12–10:34 · 65 words · 22 s** — 20 m to the south, the Henderson fire is still burning at Camp Pendleton. It started around 2 on Thursday afternoon and burned about 400 acres in its first 90 minutes. The base is roughly the size of Rhode Island, and by Friday, the fire had grown to about 2,080 acres. It even crossed containment lines on its northwest side before crews reached 20% containment.
- *[clip break 10:34–11:07, 32 s, natural sound/eyewitness]*
- **11:07–11:28 · 66 words · 22 s** — It also kept Interstate 5 in chaos. For the second day in a row, the freeway was shut down through the base. This time after a spot fire. A new blaze started by flying embers broke out around noon Friday. Trains along the coast were delayed or cancelled outright. And a separate fire right beside the freeway called the Scales Fire burned another 20 acres nearby.
- *[clip break 11:28–11:54, 26 s, natural sound/eyewitness]*
- **11:54–12:19 · 64 words · 25 s** — Across the state, the power situation remains tense. Near the Norte fire, about 2,300 customers lost electricity on Friday. Earlier in the week, Pacific Gas and Electric shut off power to nearly 62,000 customers in Northern California to keep lines from sparking fires. Now, there is some relief up north since the company has started restoring power in the Bay Area as conditions improve.
- *[clip break 12:19–12:51, 32 s, natural sound/eyewitness]*
- **12:51–13:18 · 69 words · 26 s** — Governor Gavin Newsom secured a federal FEMA grant on Friday to help pay for fighting the Norte fire. It allows agencies to recover 75% of their eligible firefighting costs. The state had moved early, too. On Thursday, a day before the fire, it sent five engines, a bulldozer, a water tender, a helicopter, and 45 extra personnel into Orange County. So, crews were already close when the call came.
- *[clip break 13:18–13:46, 28 s, natural sound/eyewitness]*
- **13:46–14:13 · 67 words · 27 s** — In Los Angeles County, the picture improved. Firefighters stopped the forward progress of the Peak Fire in Azusa. And by Friday afternoon, they had begun containing the Bryson fire in Malibu. Neither fire is known to have burned any homes. However, evacuation orders stayed in place and red flag warnings for Los Angeles and Ventura counties run through Saturday night. So, no one is standing down yet.
- *[clip break 14:13–14:39, 26 s, natural sound/eyewitness]*
- **14:39–15:03 · 72 words · 24 s** — After that, cooler weather and a chance of light rain are expected over the next few days. That should help firefighters. But rain is also the next worry because a potentially historic El Niño is building in the Pacific, and scientists see a very high chance of a wet winter in Southern California. Freshly burned hillsides cannot soak up heavy rain, so they can send mud and rocks sliding into neighborhoods below.
- *[clip break 15:03–15:33, 30 s, natural sound/eyewitness]*
- **15:33–15:59 · 64 words · 25 s** — As of Friday night, October 16th, the Norte fire had burned about 465 acres between San Clemente and San Juan Capistrano, and evacuation orders were still in effect. Six homes had been hit. Orange County Supervisor Katrina Foley is urging residents to follow those orders because the wind can change without warning. Down the coast, the Henderson fire was still moving across Camp Pendleton.
- *[outro clip 15:59–end]*

### lCR1ryuJHDs LOS ANGELES BURNING — Wildfire Grows 46X IN 3 HOURS (Latest Updates) dur 726

- *[clip break 0:00–0:17, 17 s, natural sound/eyewitness]*
- **0:17–0:42 · 59 words · 26 s** — This footage was filmed Friday, October 16th in San Clemente, California, where a wildfire charged out of the hills and into the neighborhoods next door. It was a devastating, life-threatening emergency from the start. Homes burned within hours. Thousands were ordered out, and as night fell, the same winds that drove this fire were still blowing across the region.
- *[clip break 0:42–1:06, 24 s, natural sound/eyewitness]*
- **1:06–1:26 · 57 words · 19 s** — The Norte fire started around 11:30 in the morning near a residential area of San Clemente, just east of Interstate 5. San Clemente is a beach city at the southern tip of Orange County, roughly halfway between Los Angeles and San Diego. Its southern edge borders Camp Pendleton, where another fire had already been burning since Thursday.
- *[clip break 1:26–1:51, 26 s, natural sound/eyewitness]*
- **1:51–2:11 · 53 words · 20 s** — The growth was violent. Within half an hour, the fire jumped from 10 acres to 50. And by 2:40, it had reached 465. It was burning mostly through grass and chaparel, the thick, dry brush that covers these coastal hills. Meanwhile, the wind kept throwing embers that can travel a mile or more.
- *[clip break 2:11–2:36, 26 s, natural sound/eyewitness]*
- **2:36–2:55 · 54 words · 19 s** — Those embers carried the fire north into San Juan Capistrano, the old mission town next door. That is where the worst damage came. The Orange County Fire Authority says six homes were damaged or destroyed, most of them on the San Juan Capistrano side. Crews fought to keep flames from reaching the next street.
- *[clip break 2:55–3:23, 28 s, natural sound/eyewitness]*
- **3:23–3:44 · 55 words · 21 s** — By Friday evening, about 16,000 people and 6,000 homes fell under evacuation orders and warnings. An evacuation order here is not a suggestion. It means an immediate threat to life and the area is legally closed to the public. Shelters opened at community centers in both cities while fire crews held the line behind them.
- *[clip break 3:44–4:05, 21 s, natural sound/eyewitness]*
- **4:05–4:26 · 56 words · 20 s** — At least 500 firefighters were on the lines, backed by helicopters and air tankers dropping water and retardant. Two of them were hospitalized with significant injuries, and Orange County Fire Chief Kevin Federman [ASR spelling] says both are in stable condition. By 5:45, crews had knocked down most of the fire. However, the wind was still blowing hard.
- *[clip break 4:26–4:51, 25 s, natural sound/eyewitness]*
- **4:51–5:13 · 58 words · 22 s** — That wind is the Santa Ana, a dry gust that pours out of the deserts toward the coast every fall. It is the reason this fire moved so fast. It is also why Southern California is on edge because in 2025 these same winds drove a firestorm that killed more than 30 people and burned over 16,000 structures.
- *[clip break 5:13–5:36, 24 s, natural sound/eyewitness]*
- **5:36–5:57 · 55 words · 20 s** — About 20 m south, the Henderson fire at Camp Pendleton grew to roughly 2,080 acres by Friday. Camp Pendleton is a Marine Corps base about the size of Rhode Island. Flames crossed containment lines on the northwest side. Still, crews had pushed containment to 20% by Friday evening after holding none at all on Thursday.
- *[clip break 5:57–6:23, 27 s, natural sound/eyewitness]*
- **6:23–6:44 · 58 words · 21 s** — That fire closed Interstate 5 for a second day. Around noon Friday, a spot fire, a new blaze started by flying embers, forced a full closure of the freeway through the base, and trains were thrown off schedule or stopped entirely. Up near the Norte fire, the Ortega Highway on-ramp to the southbound freeway was closed as well.
- *[clip break 6:44–7:07, 23 s, natural sound/eyewitness]*
- **7:07–7:28 · 56 words · 21 s** — The smoke brought another danger. Air quality in San Clemente, Dana Point, San Juan Capistrano, and Laguna Niguel dropped to levels unhealthy for sensitive groups, which includes older adults and people with heart or lung problems. Regulators told residents to stay inside, run their air conditioning, and wear N95 masks if they had to go out.
- *[clip break 7:28–7:53, 24 s, natural sound/eyewitness]*
- **7:53–8:14 · 55 words · 21 s** — Staying cool is not easy either. A heat advisory runs until 8 on Saturday night with temperatures climbing as high as 95°. Meanwhile, about 2,300 customers near the fire lost power. Up north, Pacific Gas and Electric has started turning electricity back on in the Bay Area. Down south, however, the danger has not passed.
- *[clip break 8:14–8:37, 23 s, natural sound/eyewitness]*
- **8:37–9:00 · 57 words · 23 s** — Governor Gavin Newsom secured a federal FEMA grant to fight the Norte fire. It covers 75% of eligible firefighting costs. On Thursday, before this fire even started, the state had already moved five engines, a bulldozer, a water tender, a helicopter, and 45 extra personnel into Orange County. So, when it broke out, help was already close.
- *[clip break 9:00–9:24, 24 s, natural sound/eyewitness]*
- **9:24–9:44 · 57 words · 20 s** — In Los Angeles County, the news was better. Crews stopped the forward progress of the Peak Fire in Azusa. And by Friday afternoon, they had begun to contain the Bryson fire in Malibu. Neither one burned any homes. Even so, evacuation orders stayed in place there since one strong gust could undo a full day of work.
- *[clip break 9:44–10:09, 26 s, natural sound/eyewitness]*
- **10:09–10:28 · 57 words · 19 s** — The threat also does not end when the flames finally do. A potentially historic El Niño is building in the Pacific and scientists see a very high chance of a wet winter in Southern California. Burned hillsides cannot soak up heavy rain, so slopes like these can send mud, rocks, and debris rushing toward the homes below.
- *[clip break 10:28–10:55, 27 s, natural sound/eyewitness]*
- **10:55–11:16 · 59 words · 21 s** — For now. Red flag warnings stay up for Los Angeles and Ventura counties through Saturday night before cooler weather and a chance of light rain arrive over the next few days. Orange County Supervisor Katrina Foley urged people to obey evacuation orders because the wind can change without warning. She pointed to the airport fire when that happened before.
- *[clip break 11:16–11:40, 24 s, natural sound/eyewitness]*
- **11:40–12:00 · 52 words · 20 s** — As of Friday night October 16th the Norte fire had burned about 465 acres with evacuation orders still in place firefighters were chasing hot spots before the wind could carry them Again down the coast, the Henderson fire kept burning across Camp Pendleton and the Santa Ana winds were still blowing hard.
- *[outro clip 12:00–end]*

### 5SOrKXWV_Ys CALIFORNIA HIT by 3 WILDFIRES — 207,000 Could Lose Power, People Evacuated (Latest Updates) dur 605

- *[clip break 0:00–0:20, 20 s, natural sound/eyewitness]*
- **0:20–0:40 · 56 words · 21 s** — This footage from Southern California on Thursday, October 15th, shows a very life-threatening situation. Wildfires broke out from a Marine base near San Diego to the hills above Malibu, forcing evacuations within hours. Yet, the winds driving them have not peaked. And stay with us because the bigger danger may come after the flames are out.
- *[clip break 0:40–1:03, 22 s, natural sound/eyewitness]*
- **1:03–1:22 · 53 words · 19 s** — The largest blaze is the Henderson fire inside Camp Pendleton, a huge Marine Corps training base on the San Diego County coast. It tore through more than 1,000 acres. By 6:00 that evening, it was 0% contained. In other words, nothing was holding it back. So, the flames ran right alongside Interstate 5.
- *[clip break 1:22–1:45, 23 s, natural sound/eyewitness]*
- **1:45–2:04 · 54 words · 20 s** — Officials briefly shut part of that highway, the main road between Los Angeles and San Diego. Evacuations were ordered nearby. Still, Camp Pendleton was not the only place burning. That same afternoon, fire also broke out in Azusa, a city pressed against the San Gabriel Mountains, and by evening, another one exploded above Malibu.
- *[clip break 2:04–2:27, 22 s, natural sound/eyewitness]*
- **2:27–2:48 · 58 words · 22 s** — The Peak fire in Azusa started around 1:00 in the afternoon and burned 43 acres in 2 hours. Helicopters dropped water while air tankers laid down retardant, a chemical that slows flames. It worked. Crews mostly wrangled the fire, so mandatory evacuations were downgraded to warnings. But on the coast, a far faster fire was just getting started.
- *[clip break 2:48–3:11, 22 s, natural sound/eyewitness]*
- **3:11–3:29 · 54 words · 19 s** — The Bryson fire ignited around 5:00 in the evening in northern Malibu, where homes climb into the Santa Monica Mountains. Within an hour, it covered roughly 80 acres. By 6:30, Cal Fire put it at 101. Meanwhile, the wind kept throwing embers out ahead of the flames, sparking new fires beyond where crews stood.
- *[clip break 3:29–3:54, 24 s, natural sound/eyewitness]*
- **3:54–4:13 · 56 words · 20 s** — By Thursday night, it had doubled to about 200 acres. Evacuation orders and warnings now cover a large part of the Santa Monica Mountains. Even a Los Angeles County juvenile detention and rehabilitation facility had to be emptied in the dark. Black smoke rose over the ridges, visible for miles, and the fire was still moving.
- *[clip break 4:13–4:37, 23 s, natural sound/eyewitness]*
- **4:37–4:56 · 58 words · 20 s** — All three fires were fed by the Santa Ana winds. These dry winds pour out of the inland deserts through the mountain passes and toward the ocean. They come every fall. However, Los Angeles knows how deadly they can be because in 2025, they drove a firestorm that killed more than 30 people and burned over 16,000 structures.
- *[clip break 4:56–5:21, 24 s, natural sound/eyewitness]*
- **5:21–5:40 · 56 words · 20 s** — Now they are back. The National Weather Service expects winds of 20 to 40 mph with gusts of 50 to 70 in the San Gabriel and Santa Susana Mountains. That is highway speed. Even the Santa Lucia Mountains in San Luis Obispo County face critical fire weather, so the danger zone stretches far beyond Los Angeles.
- *[clip break 5:40–6:04, 23 s, natural sound/eyewitness]*
- **6:04–6:26 · 51 words · 23 s** — When that strong can knock power lines into dry brush, so utilities cut the power on purpose. Pacific Gas and Electric started Wednesday night. By Thursday, nearly 62,000 customers in 26 Northern California counties were dark. Down south, about 65,000 more lost power, and Southern California Edison could cut 207,000 customers.
- *[clip break 6:26–6:48, 21 s, natural sound/eyewitness]*
- **6:48–7:07 · 54 words · 19 s** — On the ground, Los Angeles Fire Chief Jaime Moore says his department added staff and moved equipment into position ahead of time. Still, he wants residents to act, too. His message was blunt. Clear the streets, have a plan, and stay informed. On narrow canyon roads, parked cars can slow a fire engine down.
- *[clip break 7:07–7:30, 23 s, natural sound/eyewitness]*
- **7:30–7:50 · 54 words · 20 s** — Governor Gavin Newsom activated the state operation center and pulled California's top emergency officials together on Thursday. A day earlier, he ordered extra firefighters, engines, and aircraft staged ahead of red flag conditions. That warning means fire can spread fast. Those crews are now waiting, ready to move the moment the next fire starts.
- *[clip break 7:50–8:12, 22 s, natural sound/eyewitness]*
- **8:12–8:32 · 58 words · 20 s** — But fire is only half of this story. Days earlier, tropical storm Rachel slammed Southern California with heavy rain, strong winds, and dangerous surf. That is why Newsom also declared a state of emergency in Imperial, Los Angeles, Orange, and San Diego counties. Some of the same counties now burning were dealing with flooding concerns only last week.
- *[clip break 8:32–8:55, 23 s, natural sound/eyewitness]*
- **8:55–9:15 · 59 words · 20 s** — And the whiplash is not over. A potentially historic El Niño, a warming of Pacific waters that shifts weather worldwide, is building right now. Scientists see a very high chance of a wet winter in Southern California. However, burned hillsides can not hold heavy rain, so every acre lost this week raises the risk of mudslides months from now.
- *[clip break 9:15–9:38, 23 s, natural sound/eyewitness]*
- **9:38–9:57 · 59 words · 19 s** — As of late Thursday night, October 15th, the Bryson fire was still burning above Malibu, and the Henderson fire had no containment at last report. Rose Schoenfeld of the National Weather Service says the whole region should be on alert. Warnings for the Los Angeles County mountains run into Friday night, and the winds will not ease until Saturday.
- *[outro clip 9:57–end]*

### QJM8c2cevA4 LA UNDER SIEGE — Malibu Wildfire Threatens 7,200+ Structures, Thousands Lose Power (Latest Updates) dur 1503

- *[clip break 0:00–0:20, 20 s, natural sound/eyewitness]*
- **0:20–0:46 · 85 words · 27 s** — The flames in this footage are burning in the mountains above Malibu, California, one of the most famous coastlines in America. The fire broke out on Thursday, October 15th, and within a few hours it had forced families out of their canyon homes as the wind pushed it toward them. By Friday night, more than 7,000 structures sat in the threat zone. This is a life-threatening fire, but it is not the only one, and what scientists expect next could hit Los Angeles even harder.
- *[clip break 0:46–1:25, 38 s, natural sound/eyewitness]*
- **1:25–1:55 · 94 words · 30 s** — It is called the Bryson fire, and it started just before 5:00 in the evening where Encinal Canyon Road meets Mulholland Highway in western Malibu near the Ventura County line. To understand why that matters, picture the town. The beach houses and the Pacific Coast Highway sit along a thin strip of coast. Right behind them, the Santa Monica Mountains climb steeply, cut by deep canyons full of dry brush and homes reached by narrow roads. So, when a fire starts up there, the wind can push it straight downhill toward thousands of people.
- *[clip break 1:55–2:33, 38 s, natural sound/eyewitness]*
- **2:33–3:01 · 89 words · 28 s** — That is what the wind tried to do. The fire started at roughly 2 acres, and 15 minutes later it was 5. Within half an hour it covered about 20 acres. By the end of the first hour, it had reached 35, but that number does not show the real danger. Embers were flying ahead of the flames and landing in fresh brush, lighting spot fires one after another. Crews were no longer fighting one fire. Instead, they were chasing several, while the main front kept growing behind them.
- *[clip break 3:01–3:39, 38 s, natural sound/eyewitness]*
- **3:39–4:07 · 83 words · 28 s** — Shortly after 6, it reached 80 acres. Half an hour later, Cal Fire mapped it at 101 and 1/2. Evacuation orders went out for the Encinal, Trancas, and Zuma Canyon areas. In Los Angeles County, that is level three, known simply as go, and it means an immediate threat to life. A county juvenile detention facility sitting in the fire path had to be evacuated as darkness fell. By late Thursday night, it had grown to about 200 acres. Containment was still zero.
- *[clip break 4:07–4:44, 37 s, natural sound/eyewitness]*
- **4:44–5:13 · 90 words · 29 s** — Firefighters refused to back off overnight. More than 300 personnel were working the fire Thursday night, backed by aircraft that could keep flying after dark. Two super scoopers joined them. Those are planes that dip down onto the ocean, scoop up a full load of seawater while still moving, then turn and drop it on the ridges. In Malibu, the Pacific is only a few minutes away, so they could cycle back again and again. That steady air attack bought crews the time they needed to dig in before sunrise.
- *[clip break 5:13–5:51, 38 s, natural sound/eyewitness]*
- **5:51–6:21 · 83 words · 30 s** — Morning showed how much it had paid off. More precise mapping put the fire at about 146 acres, smaller than first feared, and crews had reached 17% containment. Not one home had been lost, but the fight came at a price. One firefighter was injured on the Bryson fire, according to the Los Angeles County Fire Department. Farther down the coast, near San Clemente, where a separate fire damaged or destroyed six homes on Friday, two more firefighters were hospitalized with significant injuries.
- *[clip break 6:21–6:56, 35 s, natural sound/eyewitness]*
- **6:56–7:24 · 88 words · 29 s** — The engine behind every one of these fires is the Santa Ana wind. When high pressure builds over the deserts, it pushes air down through the mountain passes and out toward the ocean. As that air sinks, it heats up and dries out, stripping moisture from every plant it crosses. It happens every fall. Still, Los Angeles has seen how deadly it can get since in January 2025, Santa Ana winds drove the Palisades and Eaton fires, which killed more than 30 people and burned over 16,000 structures.
- *[clip break 7:24–8:02, 37 s, natural sound/eyewitness]*
- **8:02–8:29 · 86 words · 27 s** — With that memory so fresh, the warnings reached far beyond the canyons. Zuma Beach, parts of the Pacific Coast Highway, and Point Dume State Beach were put under evacuation warnings, meaning be ready to leave at any moment. All four public schools in Malibu were closed Friday. The Red Cross opened a shelter at Agoura High School, while horses and pets were taken to the Agoura Animal Care Center and Pierce College. Pepperdine University, about 8 miles away, said the wind was blowing away from campus.
- *[clip break 8:29–9:07, 38 s, natural sound/eyewitness]*
- **9:07–9:38 · 86 words · 31 s** — At the same time, the power was going out. Southern California Edison shut off electricity in central and western Malibu and in Calabasas because one damaged line in this wind could start another fire. By Friday morning, close to 35,000 customers in Los Angeles County were without power, and nearly the same number in Ventura County. Another 68,000 in Los Angeles County were under consideration. Malibu officials warned that outages could also take down cell service and traffic signals right when people might need them most.
- *[clip break 9:38–10:13, 35 s, natural sound/eyewitness]*
- **10:13–10:44 · 85 words · 31 s** — Friday became a ground war. 414 personnel were assigned to the Bryson fire with 64 engines, two helicopters, and 11 hand crews. And crews cut a strip of bare ground around the fire using saws, shovels, and rakes, removing everything that could burn. Spokesman Keith Nevard called the conditions vulnerable. Dry air and strong wind pressed on the crews all day. Even so, the lines held. By Friday night, the fire was 39% contained, though the hardest test was still the next night of wind.
- *[clip break 10:44–11:19, 35 s, natural sound/eyewitness]*
- **11:19–11:50 · 85 words · 32 s** — Those conditions were extreme. Temperatures pushed close to 100°. Humidity fell into the single digits, while gusts of 40 to 65 mph were forecast around Malibu and up to 75 in the mountains. For comparison, that top gust is faster than most people drive on the interstate. The red flag warning stretched across the Malibu coast, Calabasas, the Santa Clarita, San Fernando, and San Gabriel valleys, and the freeway corridors north of Los Angeles, and it was set to run until 8:00 on Saturday night.
- *[clip break 11:50–12:26, 35 s, natural sound/eyewitness]*
- **12:26–12:55 · 89 words · 29 s** — Malibu was not the first fire that day. Around 1:15 on Thursday afternoon, the Peak Fire broke out in Azusa, at the base of the San Gabriel Mountains on the eastern side of the county. It burned 22 acres in about half an hour. Evacuation orders went out for nearby foothill neighborhoods. Crews from Los Angeles County and the Angeles National Forest hit it with helicopters and air tankers. They stopped it at about 50 acres, and the orders were downgraded to warnings before the Bryson Fire even started.
- *[clip break 12:55–13:33, 38 s, natural sound/eyewitness]*
- **13:33–14:01 · 85 words · 28 s** — Inside the city of Los Angeles, Fire Chief Jaime Moore said his department added staff and moved equipment into position before the wind arrived. That preparation was tested quickly because a small fire sparked near La Tuna Canyon Road into Tujunga that same afternoon, and crews had already fought the bike fire near Santa Clarita earlier in the week. Moore asked residents to clear the streets, have a plan, and stay informed. On narrow hillside roads, a single parked car can block a fire engine.
- *[clip break 14:01–14:37, 36 s, natural sound/eyewitness]*
- **14:37–15:06 · 86 words · 29 s** — For Malibu, this has happened before and recently. In November 2018, the Woolsey Fire started near Thousand Oaks and burned into Malibu. In December 2024, the Franklin Fire burned more than 4,000 acres and came right up against Pepperdine. Only weeks later, the Palisades Fire tore through Pacific Palisades next door. That is three major fires in about 6 years along the same mountains. Each time, the Santa Ana winds were a big part of the story, and each time, the coastal canyons paid the price.
- *[clip break 15:06–15:42, 36 s, natural sound/eyewitness]*
- **15:42–16:16 · 83 words · 34 s** — Los Angeles is still recovering from that last disaster. Homes destroyed in January 2025 are still being rebuilt. After those fires, California asked the federal government for $28 million to pay case managers who help survivors navigate insurance and aid. FEMA approved 13.2 million, less than half. By August, only one of the four payments had arrived, and late reimbursements eventually pushed the state to end the program early. Representative Judy Chu, whose district includes Altadena, warned that ending it risks abandoning survivors.
- *[clip break 16:16–16:47, 31 s, natural sound/eyewitness]*
- **16:47–17:19 · 94 words · 33 s** — Those 2025 burn areas are also a growing hazard. A burned hillside loses the roots that hold its soil together, and the scorched ground can shed water almost like a parking lot. When heavy rain falls, it rushes downhill, gathering mud, boulders, and burned trees into a debris flow. Debris flows can move fast enough to carry cars and knock homes off their foundations. Huge burn scars across Los Angeles County have already raised that danger. Now, every acre burning in Malibu this week adds another slope that people downhill will have to watch.
- *[clip break 17:19–17:55, 35 s, natural sound/eyewitness]*
- **17:55–18:23 · 86 words · 29 s** — And the rain may come hard this year. A potentially historic El Niño is building in the Pacific. El Niño is a warming of ocean water near the equator and it reshapes weather around the world, often bringing Southern California a wetter winter. This one has already raised sea levels, lifted temperatures and supercharged storms. Scientists now see a very high chance of a wet winter in Southern California. That means the hills drying out and burning this week could be facing heavy storms within months.
- *[clip break 18:23–19:00, 36 s, natural sound/eyewitness]*
- **19:00–19:33 · 86 words · 33 s** — The swing between fire and water has already started. Beginning October 11th, only days before these fires, Tropical Storm Rachel battered Southern California with heavy rain, strong winds, dangerous surf, and coastal erosion. Governor Gavin Newsom declared a state of emergency in Los Angeles, Orange, San Diego, and Imperial counties. Then, within a week, the same region was under red flag warnings and evacuation orders. Forecasters expect El Niño to keep fueling powerful storms well into next year, right on top of these new burn scars.
- *[clip break 19:33–20:05, 32 s, natural sound/eyewitness]*
- **20:05–20:37 · 85 words · 33 s** — The state has tried to stay one step ahead. Newsom activated the state operation center near Sacramento, where California coordinates its biggest emergencies. A day before the fire started, he ordered Cal Fire and the state emergency office to stage extra firefighters, engines, and aircraft ahead of the Santa Ana winds. On Friday, as another fire raced through Orange County, the state also secured a federal FEMA grant covering 75% of eligible fire costs. Help was moving, but new fires kept multiplying across the region.
- *[clip break 20:37–21:10, 32 s, natural sound/eyewitness]*
- **21:10–21:41 · 79 words · 32 s** — Those Southern fires are pulling on the same resources. Near San Clemente, the Norte fire grew from 10 acres to 465 in 3 hours on Friday, burning into San Juan Capistrano. Around 16,000 people fell under evacuation orders and warnings. At Camp Pendleton in San Diego County, the Henderson fire grew to about 2,080 acres, closing Interstate 5 two days in a row. By Friday evening, it was only 20% contained, so crews across Southern California were spread thin.
- *[clip break 21:41–22:15, 33 s, natural sound/eyewitness]*
- **22:15–22:44 · 85 words · 29 s** — Getting power back will be slow. Even after the wind dies down, Edison crews may need more than 8 hours to inspect each line before turning electricity back on. That could leave parts of Malibu and Calabasas dark for a while longer. Air conditioning and reliable phone service would go with it. Up north, Pacific Gas and Electric, which cut power to nearly 62,000 customers earlier this week, has begun restoring the Bay Area as conditions improve. Southern California is still waiting for that turn.
- *[clip break 22:44–23:20, 36 s, natural sound/eyewitness]*
- **23:20–23:48 · 87 words · 28 s** — Relief may be close. Cooler weather and a chance of light rain are expected over the next few days. That should help crews finally lock down the fire lines. Kevin McGowan, who runs emergency management for Los Angeles, has urged residents to prepare not just for one hazard, but for all of them. Meanwhile, the causes of the Bryson fire, the Peak fire, and the fires farther south remain under investigation. No one has said yet what started any of them, and the wind has not finished.
- *[clip break 23:48–24:25, 37 s, natural sound/eyewitness]*
- **24:25–24:57 · 83 words · 32 s** — As of Friday night, October 16th, the Bryson fire had burned about 146 acres above Malibu, and was 39% contained. Roughly a day after it ignited on Thursday, October 15th. No homes had been lost. Even so, evacuation orders still covered the canyons, warnings still reached the beaches, and more than 7,000 structures remained in the threat zone. The red flag warning was set to last until 8:00 on Saturday night, and firefighters were staying on the ridges until the gusts finally ease.
- *[outro clip 24:57–end]*

### 3OAlVFwN61Y TURKEY SLAMMED by POWERFUL STORMS — Istanbul Underwater, Power Outages & Rescue Operations dur 909

- *[clip break 0:00–0:20, 21 s, natural sound/eyewitness]*
- **0:20–0:46 · 73 words · 25 s** — The images you just saw come from Istanbul, Turkey, where the search for flood victims has now moved out to sea. It began on Wednesday, October 14th, 2026, when the heaviest rain the city has recorded since 1942 sent its creeks roaring through whole neighborhoods. By Sunday, October 18th, a second storm had hit that same soaked ground. And the reason those creeks turned so deadly may be sitting right on their banks.
- *[clip break 0:46–1:10, 24 s, natural sound/eyewitness]*
- **1:10–1:36 · 73 words · 26 s** — The second wave arrived on Saturday morning. Turkey's weather service put Istanbul, Kocaeli, Sakarya, Yalova, and Bursa under an orange alert, its second highest level, and 40 other provinces under yellow alerts. Emergency texts went out to phones across Istanbul. Forecaster Abdullah Macit of the National Weather Service said the soil had reached its limit, so flood risk remained high. He urged people to stay off the roads unless they had no choice.
- *[clip break 1:36–2:00, 24 s, natural sound/eyewitness]*
- **2:00–2:24 · 72 words · 24 s** — To understand why, look at a map. Istanbul is split by a narrow strait called the Bosphorus, with Europe on one side and Asia on the other. In 2 days, the city got more rain than a normal September and October combined. Beykoz, on the Asian side, measured nearly 11 in, more than a quarter of Chicago's yearly rain. Two European side districts each passed 8 in. That is where people died.
- *[clip break 2:24–2:50, 26 s, natural sound/eyewitness]*
- **2:50–3:11 · 66 words · 22 s** — As of Saturday's latest update, five people have been confirmed dead so far, four in Istanbul and one in a neighboring province. The first was a 14-year-old boy in Fatih, the historic old city. On Wednesday, he stepped into a puddle at a park and was hit by an electric current. Doctors could not save him. Investigators still do not know where that current came from.
- *[clip break 3:11–3:40, 29 s, natural sound/eyewitness]*
- **3:40–4:01 · 64 words · 20 s** — Most of the other deaths came from Ayazaga, in the northern district of Sariyer. A 34-year-old man slipped on a flooded street and struck his head on the curb. On Friday, a 66-year-old man was found under a bridge. A 56-year-old man turned up downstream beside a historic mosque, and according to one family, he had been with a man who is still missing.
- *[clip break 4:01–4:31, 30 s, natural sound/eyewitness]*
- **4:31–4:55 · 72 words · 24 s** — The fifth victim died east of Istanbul in Kocaeli, an industrial province built around a long bay. In a district called Başiskele, sudden floodwaters swept away a man who once served as a neighborhood leader. His body was found in the bay. Kocaeli also lost a bridge in that same district, and a landslide hit farther north. Still, for families in Istanbul, the hardest news is the news that has not come.
- *[clip break 4:55–5:20, 26 s, natural sound/eyewitness]*
- **5:20–5:44 · 72 words · 23 s** — Three men are still missing, and all three vanished in Ayazaga's flooded creek. At first, more names were on that list. However, one man reported missing simply showed up, explaining that his phone battery had died. Governor Davut Gül says there are no children among the missing. Teams are now searching beyond the spots where the men were last seen because the water may have pushed them much farther than anyone expected.
- *[clip break 5:44–6:11, 27 s, natural sound/eyewitness]*
- **6:11–6:33 · 71 words · 22 s** — One of the missing is 63 years old. He left home to pick up his daughter and divers found his car wedged under a bridge in the Kagithane stream. A crane lifted it out. The key was still in the ignition, his belongings were inside, and the back window was smashed. 650 ft away, a second car sat upside down under another bridge. Meanwhile, the Coast Guard is searching the sea.
- *[clip break 6:33–7:01, 28 s, natural sound/eyewitness]*
- **7:01–7:25 · 73 words · 24 s** — The other two missing men are 55 and 30. The younger man is from Turkmenistan, a former Soviet country in Central Asia, and the older one was last seen leaving his workplace. Back in Ayazaga by Friday, the entire neighborhood had lost power. Recep Uzum Cavak, who runs a business there, says water inside stood waist-high and wiped out years of work. Now, cleanup crews and search teams share the same muddy streets.
- *[clip break 7:25–7:51, 26 s, natural sound/eyewitness]*
- **7:51–8:18 · 64 words · 27 s** — The size of this operation is hard to picture. Officials say more than 2,700 people trapped by floodwater were evacuated in Istanbul. Over 46,000 workers are deployed in the city, including about 8,600 search and rescue specialists working with 14 boats. Nationwide, the number passes 58,000. Even a neighboring province sent crews. They have handled nearly 10,000 reports, and the damage tally keeps climbing.
- *[clip break 8:18–8:42, 24 s, natural sound/eyewitness]*
- **8:42–9:09 · 72 words · 27 s** — So far though, the buildings themselves have mostly held. Ali Hamza Pehlivan, who leads Turkey's disaster agency, says inspectors have not found any collapsed or heavily damaged buildings in Istanbul yet. Instead, the water got inside. In Beykoz alone, about 320 homes and 20 businesses flooded, and several retaining walls cracked. Across the city, thousands of families are now shoveling mud out of ground floors and basements, while others wait for inspectors.
- *[clip break 9:09–9:31, 22 s, natural sound/eyewitness]*
- **9:31–9:52 · 64 words · 21 s** — Floodwater got into two hospitals and poured through the ceiling of a metro station, while a main boulevard collapsed and the historic Sadabad Mosque flooded up to its pulpit. Power cuts knocked out the water supply, so some flooded homes had dry taps. At the main airport, 51 flights were diverted and 19 canceled. East of the city, the destruction took a different shape.
- *[clip break 9:52–10:22, 30 s, natural sound/eyewitness]*
- **10:22–10:44 · 68 words · 22 s** — In Sakarya province, about 93 mi east, officials say two buildings and five bridges were destroyed. Its beach town of Karasu took about 9 and 1/2 in of rain in 4 hours. That is close to what Istanbul's worst district got over 2 days. Inland, near the lake town of Sapanca, a two-story house built right on a creek bed collapsed. The family had been moved out earlier.
- *[clip break 10:44–11:12, 27 s, natural sound/eyewitness]*
- **11:12–11:37 · 71 words · 25 s** — Along the Black Sea, the old coal mining city of Zonguldak saw homes and shops flood while cars sat underwater. Far to the south, streets flooded in Antalya, the resort city on the Mediterranean. President Recep Tayyip Erdoğan said every state agency was working together, and he urged people to follow official warnings. Since then, the warnings have only spread, now reaching the capital Ankara and the coastal city of Izmir.
- *[clip break 11:37–12:02, 25 s, natural sound/eyewitness]*
- **12:02–12:27 · 71 words · 25 s** — So, why did this get so bad? City planners in Istanbul argue that the rain alone cannot explain it. They point to decades of construction pushed right up against creeks and to ground sealed under concrete that once soaked water up. That Sapanca house became the symbol. When a creek overflows, it runs straight into whatever was built in its path. This year, Turkey's rainfall ran 54% above average through August.
- *[clip break 12:27–12:53, 26 s, natural sound/eyewitness]*
- **12:53–13:22 · 69 words · 29 s** — Environment Minister Murat Kurum blames climate change and calls fixing development near waterways essential. In 2009, after deadly floods, Erdogan promised to clear Istanbul's stream beds. 17 years later, the bulldozers arrived. This Saturday, crews began tearing down risky structures in the Ayazaga creek bed, including a stadium. More than 5,000 victims have received about $200 each with more due Monday. Prosecutors are investigating while the sky keeps churning.
- *[clip break 13:22–13:42, 20 s, natural sound/eyewitness]*
- **13:42–14:04 · 68 words · 23 s** — Saturday night storm winds of 37 to 50 miles per hour were forecast for Beykoz in the Black Sea coast north of the city. Overnight those winds were set to sweep east across Turkey's northern provinces reaching Kastamonu, Sinop and Samsun by Sunday morning. The heavy rain should fade after that. Light showers could return Sunday evening however and with creeks running high it would not take much.
- *[clip break 14:04–14:31, 27 s, natural sound/eyewitness]*
- **14:31–14:53 · 65 words · 22 s** — As of Sunday October 18th Istanbul is cleaning up and still searching at the same time. The flooding that began on October 14th left wrecked cars under bridges, a neighborhood without power and families still waiting for news. Schools are set to reopen on Monday. Before that divers, police and coast guard crews will go back to the creeks, the bridges and the open sea.
- *[outro clip 14:53–end]*

### y_o9xAJaTfM BRAZIL HIT by FLASH FLOOD — São Paulo Swamped by Violent Storm, $2 BILLION SPENT ON DRAINS dur 1103

- *[clip break 0:00–0:20, 21 s, natural sound/eyewitness]*
- **0:20–0:49 · 85 words · 28 s** — This footage comes out of S. Paulo, where a violent storm on Wednesday, October 14th, turned downtown streets into rivers within minutes. Cars sank inside a tunnel. A day later, the storms hit Rio de Janeiro as well. Now, the fallout has reached a judge since the city was already under court order to plan fixes for its flooding long before this storm. And that tunnel has flooded before. Stay with us because what happened there in 1999 explains the pressure on city hall today.
- *[clip break 0:49–1:17, 29 s, natural sound/eyewitness]*
- **1:17–1:48 · 83 words · 30 s** — S Paulo is Brazil's largest city and its business capital. So one bad storm there can upend life for millions. Wednesday's storm came with hail in VA Mariana, a busy neighborhood south of downtown. Residents watched ice fall alongside the downpour. Meanwhile, rainwater got inside Periso Station on the city's Blue Line subway and on Augusta Street, water spilled over the curbs. The city's emergency center counted at least nine flooding points, but the worst of it was waiting inside a tunnel downtown.
- *[clip break 1:48–2:16, 28 s, natural sound/eyewitness]*
- **2:16–2:44 · 84 words · 28 s** — The Anhenaba tunnel runs beneath a historic valley in the heart of downtown S. Paulo, carrying traffic under a wide public plaza. On Wednesday, it filled with water. People were left stranded on top of submerged cars, and firefighters worked the scene as the water slowly began to drop. How fast did it happen? Mayor Ricardo Nunees said the water climbed more than 3 ft in just 3 minutes. And a few miles to the south, the city's most famous park was overflowing, too.
- *[clip break 2:44–3:11, 27 s, natural sound/eyewitness]*
- **3:11–3:37 · 78 words · 26 s** — Ibera Park is S. Apollo's version of Central Park, a huge green space where people jog and bike around its lakes. On Wednesday, two of those lakes spilled over. The water swept across the running path, leaving fish and even turtles on the pavement where joggers normally pass. It sounds almost harmless, but on the north side of the city, the same storm did something far worse. In a neighborhood called Brazilia, the ground itself started to move.
- *[clip break 3:37–4:10, 32 s, natural sound/eyewitness]*
- **4:10–4:35 · 77 words · 25 s** — Zendia is a workingclass district on S. Paulo's north side. On Wednesday night, a landslide there brought down a house and killed a 47year-old woman. Hers is not the only loss. As of Friday, 21 people have died in rain related events across S. Paulo State so far this year. Five died in the city, five in its suburbs, and 11 farther inland. And the reason Wednesday went so wrong starts with how fast the water came.
- *[clip break 4:35–5:07, 32 s, natural sound/eyewitness]*
- **5:07–5:35 · 85 words · 28 s** — The storms this week came as intense bursts. The kind of downpour that dumps a lot of water on one spot very fast. A city covered in concrete can't soak that up. Instead, the water races downhill to the lowest ground it can find. And downtown, that means the Anhenabau Valley. City Hall's own explanation was simple. It said the drainage system just could not handle that much water at once. But this valley has flooded before, and the city's rules came from that day.
- *[clip break 5:35–6:06, 31 s, natural sound/eyewitness]*
- **6:06–6:35 · 80 words · 29 s** — Back in 1999, a flood hit the Anhangga tunnel while its entrance stayed open. So, 160 vehicles got trapped inside. After that, the city created an alert protocol. When heavy rain is forecast over risky spots like this tunnel, the city declares what it calls a state of attention. The city's traffic agency says that plan was activated on Wednesday. Still, cars ended up underwater. That gap is where the state's governor stepped in with blunt words for city hall.
- *[clip break 6:35–7:05, 30 s, natural sound/eyewitness]*
- **7:05–7:31 · 82 words · 26 s** — Like New York, S. Paulo has both a governor running the state and a mayor running the city. Governor Taresio de Freight said the Anhenga Bau tunnel should have been closed on Wednesday. That is a serious charge. If the tunnel should have been shut, the story is no longer just about rain, but about whether anyone acted in time. City Hall sees it differently. Its answer came from the mayor himself, and he denied that anyone on his team had failed.
- *[clip break 7:31–8:00, 29 s, natural sound/eyewitness]*
- **8:00–8:28 · 84 words · 28 s** — Nunez says the protocol calls for closing the tunnel once water starts moving into Proadaband. dera a square right next to it. His point is that the water outran the rule even so he left the door open to changes saying the protocol exists. We can always try to improve. This time he says the tunnel drained in under an hour compared with up to 16 hours in past floods. But prosecutors were already watching and they had a court ruling on their side.
- *[clip break 8:28–8:59, 30 s, natural sound/eyewitness]*
- **8:59–9:27 · 84 words · 29 s** — In Brazil, state prosecutors can sue a city on behalf of the public, a bit like a state attorney general here. In October 2025, a court ruled against the city, finding failures in how it handles drainage and flood control. That ruling became final this January. It required three plans. One for fixes within 2 years, one for 2 to 5 years, and a long range plan stretching up to 15 years. Then the day after Wednesday's storm, prosecutors went back to the judge.
- *[clip break 9:27–9:54, 27 s, natural sound/eyewitness]*
- **9:54–10:21 · 79 words · 27 s** — On Thursday, they gave city hall 48 hours to hand over the emergency plan it used during Wednesday's storm. They wanted the timeline. That meant when alerts went out, how the tunnel was handled, and whether the pumps worked. They also had Mayor Nunez notified in person and they asked the judge to declare the city late on those plans. That would mean fines of about $1,800 a day up to roughly 330,000. Nunez did not take it quietly.
- *[clip break 10:21–10:51, 29 s, natural sound/eyewitness]*
- **10:51–11:17 · 80 words · 26 s** — The prosecutors are there to keep sending us paperwork. He said, "I'm there to work." Then he turned to the budget saying the city has put about $2 billion into drainage work since 2021. Part of that built giant flood basins which hold storm runoff until the drains catch up. Nine are done and 10 more are under construction. He credits that work with cutting the city's flooding by 70%. And on Friday, a judge handed city hall a win.
- *[clip break 11:17–11:50, 33 s, natural sound/eyewitness]*
- **11:50–12:14 · 76 words · 24 s** — The judges. reasoning was narrow. He ruled this lawsuit is only about the city turning in its drainage plans, not about how it handled one storm. On those plans, the city is still on time. In July 2026, another decision told the city to resubmit them, which reset the clock, so there's no fine for now. But while the court was ruling in S. Paulo, a second storm had already flooded streets in Rio de Janeiro.
- *[clip break 12:14–12:48, 34 s, natural sound/eyewitness]*
- **12:48–13:16 · 77 words · 28 s** — Rio de Janeiro sits a few hundred miles up the coast. From Thursday night into Friday morning, heavy rain hit the city and the towns around it. Neidaroy, a city just across the bay from Rio, had streets completely flooded, so getting around became a struggle. Its neighbor, Sanonula, was hit, too. So were Belelfford Roxo and Rio's northern suburbs. and Nova Fbergo, a mountain town inland. Inside Rio itself, people's phones lit up with emergency texts.
- *[clip break 13:16–13:46, 31 s, natural sound/eyewitness]*
- **13:46–14:15 · 77 words · 29 s** — Alerts came from the city's civil defense while its operation center tracked flooded streets in several neighborhoods. The heaviest rain fell in Graajo, a neighborhood in the city's north zone. It got about 1.7 in. Jordan Botanico, the area around Rio's botanical garden, was close behind, while Governor's Island, home to the main international airport, got about 1 and a half in. Forecasters warned of more storms Friday afternoon with lightning and gusts up to 47 mph.
- *[clip break 14:15–14:41, 26 s, natural sound/eyewitness]*
- **14:41–15:12 · 84 words · 31 s** — The rain is not done with this region yet. Brazil's National Disaster Warning Center, Seeden, updated its forecast early Saturday morning, and the danger zone got wider, not smaller. For Saturday, it rates the chance of flash floods and overflowing creeks as moderate around S. Paulo, Rio, and parts of Minus Jerai state. That includes Petropolis, a mountain city above Rio. Overnight, the warning also spread to southern Espirto Santo, the coastal state just north of Rio. But floods are only half the risk.
- *[clip break 15:12–15:37, 25 s, natural sound/eyewitness]*
- **15:37–16:05 · 81 words · 28 s** — The other half is the ground itself. After a day of rain, hillsides are already soaked, so one more heavy burst could set off landslides. Seedan rates that risk as moderate around S. Paulo Petropolis Jiz Deora in Mina Sharise and Victoria the capital of Espirto Sento. And there's one key change. In the early morning update, the Rio area was added to the landslide list. Meanwhile, far to the south, a different kind of flood is still on the move.
- *[clip break 16:05–16:32, 27 s, natural sound/eyewitness]*
- **16:32–16:59 · 85 words · 27 s** — In Rio Grand Soul, Brazil's southernmost state, flood risk is rated high around Uruguayana, a city on the border with Argentina. It's the only high rating in Brazil today. The reason is the Uruguay River. A crest of flood water is moving down the river, much like a flood wave rolling down the Mississippi. So, the flooding there could hold steady or spread along the streams that feed the river. Back in S. Paulo, though, the fight is about what happens before the next storm.
- *[clip break 16:59–17:28, 29 s, natural sound/eyewitness]*
- **17:28–17:57 · 82 words · 29 s** — It has been 3 days since the October 14th storm swamped the Anhungabau tunnel. Prosecutors lost this round in court. However, as of Saturday, October 17th, city hall is still rewriting the flood plans it owes the judge. The rain may not wait that long. Today's forecast puts S Paulo back under a moderate risk of flash floods and landslides with strong downpours possible through the day. So any cloud burst over downtown puts that old tunnel protocol to the test again.
- *[outro clip 17:57–end]*

### zy8u5gObPbo BRAZIL HIT by FLOODING — Rivers Overflowing, Landslides Warning (Latest Updates) dur 916

- *[clip break 0:00–0:20, 21 s, natural sound/eyewitness]*
- **0:20–0:45 · 68 words · 24 s** — This footage comes from Brazil, where on October 14th, downtown São Paulo got 11 days of normal rain in 40 minutes. 4 days later, the storms have spread across Brazil. A bridge support collapsed, hillsides gave way, and on the border with Argentina, a river sits 5 ft above flood stage. Now, a cyclone has joined in. Still, clear skies won't mean safe ground, and we'll explain why.
- *[clip break 0:45–1:13, 29 s, natural sound/eyewitness]*
- **1:13–1:38 · 67 words · 24 s** — Near the Anhangabaú, a valley in the heart of downtown, about 1.7 in fell in 40 minutes. Ibirapuera, the city's central park, got even more. Roughly 2.7 in fell there in under an hour, and a stream running through the park spilled over its banks. By Friday, the city had logged almost all of October's normal rain in just over 2 weeks. Downtown, it found a track.
- *[clip break 1:38–2:07, 29 s, natural sound/eyewitness]*
- **2:07–2:31 · 66 words · 24 s** — The Anhanguera tunnel runs under that downtown valley, and within minutes it filled, leaving drivers stranded on the roofs of their cars. Firefighters worked the scene as the water slowly dropped. Mayor Ricardo Nunes said the water rose more than 3 ft in 3 minutes. In 1999, this tunnel trapped 160 vehicles. So, the city created a protocol to close it in time. Did it work?
- *[clip break 2:31–3:01, 30 s, natural sound/eyewitness]*
- **3:01–3:25 · 75 words · 24 s** — The alert protocol was activated that Wednesday. Yet, cars still went under. Like New York, São Paulo has both a governor running the state and a mayor running the city. Governor Tarcísio de Freitas said the tunnel should have been closed. So, the fight is over why a rule born from one disaster missed the next. But, while downtown argued over a tunnel entrance, the north side of the city was facing something far worse.
- *[clip break 3:25–3:54, 29 s, natural sound/eyewitness]*
- **3:54–4:17 · 63 words · 23 s** — In a working-class district on São Paulo's north side, a landslide brought down a house on Wednesday night. A 47-year-old woman was killed. As of Saturday, state officials count 21 rain-related deaths in São Paulo state so far this year. Five were in the city, five in its suburbs, and 11 farther inland. By Friday, the storms had pushed deep into that countryside.
- *[clip break 4:17–4:49, 32 s, natural sound/eyewitness]*
- **4:49–5:14 · 71 words · 25 s** — Between Friday and Saturday, at least nine cities across São Paulo state reported storm damage. In Paulicéia, near the state's western edge, the end support of a bridge collapsed, partly cutting off the area. In Presidente Prudente, a landslide broke a water main and the road was closed. In Santo André, near the capital, a balcony gave way. Three people got out unhurt. East of the city, lightning made things worse.
- *[clip break 5:14–5:43, 29 s, natural sound/eyewitness]*
- **5:43–6:09 · 74 words · 25 s** — In São Luís do Paraitinga, a historic hill town, lightning killed eight cattle and a landslide blocked part of a highway. Closer to the capital in Aruja, walls collapsed near homes. One family had to move into a hotel. In Jau, flash floods ripped up a stretch of asphalt while other towns reported down trees and power outages. No one was hurt, but back downtown, the tunnel fight had already moved into a courtroom.
- *[clip break 6:09–6:36, 28 s, natural sound/eyewitness]*
- **6:36–6:58 · 65 words · 22 s** — State prosecutors, a bit like a state attorney general here, gave City Hall 48 hours to explain how it handled Wednesday's storm. They wanted to know when alerts went out and whether the pumps worked. They also cited a 2025 ruling that found failures in the city's flood control and asked for fines of up to roughly $330,000. On Friday, a judge turned them down.
- *[clip break 6:58–7:30, 32 s, natural sound/eyewitness]*
- **7:30–7:54 · 74 words · 25 s** — The judge ruled the case only covers the city's drainage plans, which are not yet overdue. Mayor Nunes had fired back saying the prosecutors are there to keep sending us paperwork. I'm there to work. He says the city has spent about $2 billion on drainage since 2021, including giant basins that hold storm runoff. Nine are finished and 10 more are being built. Still, on Wednesday, that was not enough for one tunnel.
- *[clip break 7:54–8:22, 27 s, natural sound/eyewitness]*
- **8:22–8:47 · 70 words · 25 s** — Then on Friday, an extra-tropical cyclone formed off Brazil's southern coast, a storm much like a nor'easter. It dragged a cold front north. That front soaked São Paulo first, then shifted toward Rio de Janeiro and Espírito Santo. Through Sunday, parts of four states were expected to get 4 in or more, with the heaviest rain near the line between Rio and Espírito Santo. Rio was right in its path.
- *[clip break 8:47–9:15, 28 s, natural sound/eyewitness]*
- **9:15–9:42 · 73 words · 28 s** — Rio had already flooded on Thursday night when streets in neighboring Niterói, just across the bay, went completely under. Phones across Rio buzzed with emergency texts. The heaviest rain fell in Grajaú, a north zone neighborhood that got about 1.7 in. Then early Saturday, Brazil's national disaster center added the Rio area to its landslide watchlist since the hillsides were already soaked. Meanwhile, far to the south, a river was refusing to drop.
- *[clip break 9:42–10:09, 26 s, natural sound/eyewitness]*
- **10:09–10:32 · 69 words · 23 s** — On Brazil's border with Argentina, the Uruguay River has been above flood stage in Uruguaiana for more than a week. As of Friday, it stood at about 33 ft, 5 ft over flood stage. City officials count 218 people displaced. Some were staying with relatives while others moved into a city sports center now used as a shelter. And the rain that drove them out mostly fell somewhere else.
- *[clip break 10:32–11:03, 31 s, natural sound/eyewitness]*
- **11:03–11:27 · 70 words · 25 s** — Uruguaiana's emergency coordinator Paulo Wouters says the water comes from rain that fell far upriver, some of it near the Santa Catarina state line. That state has been hammered. In the town of Princesa, more than 13 in fell in October's first 13 days, beating a normal full month. Over one stretch, about 8 in came down in just 3 days. And there's a reason this October is so extreme.
- *[clip break 11:27–11:55, 28 s, natural sound/eyewitness]*
- **11:55–12:20 · 70 words · 25 s** — In early October, Santa Catarina's forecasters said El Niño, the warming of the Pacific, had reached very strong intensity. That pattern often gives the American South a wet winter. In Southern Brazil, it tends to bring rain week after week, and much of it drains into rivers like the Uruguay. Upriver from Uruguaiana, Itaquí and São Borja are above flood stage, too. São Paulo, meanwhile, is getting a short break.
- *[clip break 12:20–12:46, 26 s, natural sound/eyewitness]*
- **12:46–13:06 · 65 words · 20 s** — Dry, cold air is moving in behind the front. So, Sunday should bring only a trace of rain to São Paulo. Highs should top out in the mid-70s. However, officials kept alerts in place for the hardest-hit areas. The reason is the ground, since soil that soaked up nearly a month of rain can still slide after the sky clears, and the break won't last.
- *[clip break 13:06–13:39, 33 s, natural sound/eyewitness]*
- **13:39–14:02 · 66 words · 23 s** — Forecasters expect dry weather through Tuesday, but new storms could start building again from October 22nd. That's this coming Thursday. So, São Paulo has only a few dry days before it's soaked hillsides and its tunnel protocol could be tested again. Meanwhile, the same cold air is chilling the south. In Uruguaiana, nights dropped to about 45° as displaced families wait for the river to fall.
- *[clip break 14:02–14:33, 31 s, natural sound/eyewitness]*
- **14:33–14:56 · 72 words · 23 s** — 4 days after the October 14th storm, the Anhangabaú tunnel remains the center of this fight. As of Saturday, October 17th, city hall was still rewriting the flood plans it owes the court. The judge gave it time and the city says its new plans will follow a drainage master plan released in September. Still, the weather won't wait for paperwork and the next test for that tunnel could come within days.
- *[outro clip 14:56–end]*

