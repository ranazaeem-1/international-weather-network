# Carver Weather Desk: script guide

For the editor-agent who writes every Carver script. Host: **Glenn Carver** (HeyGen avatar). The HeyGen voice reading the script is the final voiceover: one continuous HeyGen render per episode. English only. US events for now.

Written 4 November 2026 from: 7 transcripts of The Mercer Report (@WaltMercerReport), IWN's `worflow.md` (§0, §7, §8), `research-gwn-script-structure-2026-10-18.md`, and the two newest IWN narration scripts (`2026-10-29-sakurajima-eruption`, `2026-10-29-southern-thailand-floods`). The Etna and MN/WI tornado episode folders are no longer in `international-weather-network/episodes/`, so they were not read.

---

## 1. Findings

### 1.1 Walt Mercer stats (all 7 videos)

Word counts and timings come from YouTube auto-caption word timestamps (`*.en-orig.vtt`). "Gaps" are stretches of 1.5 s or more with no captioned speech, which are almost always inserted natural-sound clips.

| Video | Upload | Runtime | Views | Likes | Comm. | Words | WPM (whole video / speech only) | Chapters | Name line at | Nat-sound gaps |
|---|---|---|---|---|---|---|---|---|---|---|
| `-ysFYdyHewM` Storm across 30 states | 2 Nov | 14:24 | 23,321 | 153 | 5 | 1,760 | 122 / ~145 | 12 | 0:47 (after a 17 s clip at 0:30) | 8 × ~17 s (135 s) |
| `GYhANjTrPJE` Las Vegas floods | 1 Nov | 15:03 | 7,066 | 33 | 1 | 1,899 | 126 / ~134 | 16 | 0:54 | 3 × ~17 s (54 s) |
| `8XbRroqxrSQ` Florida king tide / Thanksgiving | 31 Oct | 10:22 | 23,321* | 151 | 26 | 1,188 | 115 / ~125 | 14 | 0:41 | 3 × ~17 s (52 s) |
| `ZlU5XlPYlD4` Huntington Beach emergency | 30 Oct | 13:34 | 12,299 | 173 | 21 | 2,419 | 178 | 11 | 0:43 | 0 |
| `G7CBVr_Dnfw` Miami major flood | 28 Oct | 15:25 | 17,130 | 146 | 12 | 2,766 | 180 | 11 | 0:54 | 0 |
| `HqcM66AJWyc` El Niño outlook | 20 Oct | 14:22 | 2,117 | 7 | n/a | 2,432 | 170 | 12 | 0:36 | 0 |
| `ujUttka1HsM` North Carolina coast | 19 Oct | 12:52 | 5,924 | 21 | 2 | 2,302 | 179 | 13 | 0:39 | 0 |

\* The info.json files for `8XbRroqxrSQ` and `-ysFYdyHewM` both report exactly 23,321 views, though their likes and comments differ. Re-check before quoting it.

**Runtime:** Walt averages 13:43 (range 10:22–15:25). **Carver's cap is 12:00 (owner, 4 Nov 2026)**: a tighter episode with about 11:00 of speech. Walt narrates nearly wall to wall (85–100% of runtime). That is the model for Carver, not IWN's 45–50%.

**Format shift:** the three newest videos (31 Oct–2 Nov) added ~17 s nat-sound breaks and slowed to ~125–145 wpm, against ~170–180 before. Those videos got 23k, 23k and 7k views; the older ones got 17k, 12k, 6k and 2k. Seven videos on a young channel can't separate format from growth, so don't treat this as proof.

**Per-video structure:**

| | Hook formula | Open loop: planted → paid | Explainer / analogy | Numbers made concrete | Safety list | Certain vs. uncertain | CTA (placement) | Sign-off |
|---|---|---|---|---|---|---|---|---|
| Miami | Number + place ("Two and a half feet above the normal high tide"), the unusual part ("no hurricane"), rarity (only Wilma 2005 and Irma 2017), places, promise of three, loop | "one place in Florida where this water may not leave" 0:45 → 7:46, "here's the part I promised you at the start" | Minor/moderate/major flood "ladder" 1:57. High pressure squeezing air "like water forced through a narrow hose" 3:25. Wind on "hot soup" piling up in a bowl 3:56 | Tide forecast said 9 in, water reached 30 in, "nearly 2 ft … was never on any tide calendar". 8–13 ft waves = "a one-story house". Sea up 1¼ in per decade ≈ "roughly a foot" | Six numbered steps 12:08–13:33, each with a consequence (salt water in brakes, rip current: float, think "in days, not hours") | 13:33: "What's not final is the exact numbers … I'm not going to call it a record until NOAA does" | End only. Specific: "tell me where you are … Miami Beach, Fort Lauderdale, the Keys … it helps your neighbors" plus subscribe "when the November tides come in" | "I'm Walt Mercer. Stay dry out there, and I'll see you in…" |
| Storm, 30 states | Same storm, new threat: "pushing a river toward a crest higher than the flood of 1911", then 30 states by day | "one night this week that worries me more … nothing to do with how much rain falls" 0:58 → 9:57 ("this is the night I told you about") | Atmospheric river = "fire hose aimed at Arizona" 5:54 | Oak Creek "rose about 12 ft in a single night". 22 ft forecast vs 17.8 ft record | 13:59: 6 in knocks over an adult, 12 in moves cars, 2 ft moves SUVs, turn around | 13:12: "confident … less sure about where any tornado forms". The Pagosa forecast went from 17 to 22 ft | End: "If this video helped you, please subscribe … where are you watching from?" | (cut) |
| Las Vegas | "Two days in a row, the streets of Las Vegas turned into rivers" + "what most people are missing" + promise | "why all of this water still can't fix [Lake Mead]" 0:30 → 11:27 "the part almost nobody is talking about", recalled in the bottom line | Ground "baked as hard as a clay pot", rain runs off "a cookie sheet" 2:31. What a wash is 5:01 | "more than a third of what Las Vegas usually gets in an entire year … in a few hours". October = "nearly four times" normal | 12:54: same 6 in / 12 in / 2 ft, stay out of washes "even for a picture" | 13:23: confident about tonight's rain, unsure where storms set up | End: "subscribe and turn on the bell … did the water reach your street?" | (cut) |
| FL Thanksgiving | Seawater over seawalls, Fernandina to Key West, "no hurricane", record "higher than Nicole" | "next round of king tides" → Thanksgiving week 7:56 | Reuses "why it happened without a hurricane" | Tide-table dates as astronomy facts | "here's what I do" list 8:38 | 9:22: "a week to watch, not a week to panic" | **Early, ~1:10** ("if you want clear information without the hype…") + end | — |
| Huntington Beach | 100+ homes damaged, local emergency, "nothing on the radar", highest tide on record | "two dates … circle on your calendar": Thanksgiving given at ~1:15, Christmas Eve held to ~8:47 | Why the ocean is so high 4:19 | "four tide records in one week" | Numbered to 6, plus photos for the insurance claim | 12:18: tide tables certain, extra water not | **Early ~1:00:** "I keep this channel simple, not hype, not panic … please subscribe. It really does help us reach more people" + end | "Stay…" |
| El Niño | "83% chance … strongest since 1950", one state where forecasters worry "not because of snow" | Florida loop 0:30 → 3:28 | Jet stream = "a conveyor belt" 1:04. El Niño "loaded the dice" 12:49 | — | Weather-radio batteries | 12:49: chaotic weather, Arctic Oscillation, next NOAA dates (12 and 19 Nov) | End: "what kind of winter are you hoping for?" | — |
| NC coast | "Two to four feet of ocean water standing on dry land … not from a hurricane … it isn't leaving" | "something on Hatteras Island that may not make it through this week" 0:35 → houses at 5:05 | Why it won't leave 1:43 | "tide after tide after tide" | DriveNC, the free ferry alert system, rip currents | 11:26: track uncertainty, no name yet | End: "Have you ever been on the Outer Banks during a storm…?" | "I'm Walt Mercer. Stay safe out there and…" |

### 1.2 What Walt does well (keep all of it)

1. **The hook formula:** a concrete number and place, then why it's unusual, a historical comparison, the scope, a promise of three things, and one open loop. The name line comes at 0:36–0:54.
2. **An audience qualifier right after the name line:** "If you live anywhere on Florida's Atlantic coast, from Jacksonville all the way down to Key West, this is your story … if you have family down there, it's theirs, too." (Miami 0:59)
3. **An explicit loop payoff:** "Now, here's the part I promised you at the start." (Miami 7:46). The viewer is told the promise was kept.
4. **A picture for every mechanism:** soup bowl, hose, fire hose, clay pot, cookie sheet, conveyor belt. Each takes one sentence.
5. **Numbers turned into meaning:** "nearly 2 ft … was never on any tide calendar", "a third of a year's rain in a few hours".
6. **A numbered safety list where each step has a consequence**, not bare slogans.
7. **A "what's certain and what isn't" segment every time**, including "I'm not going to call it a record until NOAA does." This is his strongest trust device.
8. **A bottom line that calls back to the hook and names the next date** (Miami 14:31).
9. **Attribution by office:** "the Key West office", "the Melbourne office put it plainly". The viewer always knows whose number it is.
10. **A first-person, calm, anti-hype position:** "not hype, not panic, just clear information from the agencies that measure this stuff." (Huntington 1:01)

### 1.3 Where Walt is weak (Carver must beat these)

| # | Weakness | Evidence |
|---|---|---|
| W1 | **Nat-sound clips cut his sentences.** Words go missing at every ~17 s insert | Storm 4:43 "out of a second car that — Then on Sunday morning". 5:13 "even a short burst of rain can — So, why". 9:57 "A small room on the — Tuesday is election day". Vegas 0:30 "can't fix the — I'm Walt Mercer". Vegas 4:14 "and our —" |
| W2 | **City and road lists read aloud** that nobody can hold in their head | Storm 3:28 (I-17, SR 179, 89A, Kachina Village). Vegas 5:01, four intersections in one sentence. Storm 10:44–12:27: Shreveport, Little Rock, Memphis, Nashville, Atlanta, Louisville, Cincinnati, Knoxville, Birmingham, Washington, Philadelphia, New York, Boston in about 100 s. NC 1:05, county list |
| W3 | **The back third sags** once the single loop is paid | Storm: loop paid at 9:57, then 2.5 min of city-by-city almanac. Vegas: loop paid at 11:27, but 5:58–6:40 is trivia ("drag racing … a rainbow stretched over the strip. A quiet ending") |
| W4 | **The same beats repeat within and across videos** | "No hurricane" appears 4 times in Miami (0:02, 2:26, 4:53, 14:31) and is the hook of 3 videos in 5 days (Miami, FL Thanksgiving, Huntington). The Phoenix 40th Street and Camelback rescue is told almost word for word in Storm 4:15 and Vegas 7:27. "Here's the part…" opens many turns |
| W5 | **Generic CTAs**, and early ones that interrupt | "If this video helped you, please subscribe so you don't miss the next update" (Storm 13:59). "subscribe and turn on the bell so the next one finds you" (Vegas 14:36). "please subscribe. It really does help us reach more people" at 1:00, before any content (Huntington). "Where are you watching from?" in 4 videos. Comments: 1–26 per video |
| W6 | **Almost no spoken visual hand-offs.** The script rarely tells the editor or the viewer what to look at | One good exception: "This is what 15 ft looked like 9 days ago" (Storm 8:15). The day-by-day section has no "on this map" cue at all |
| W7 | **No spoken "as of" time.** "Tonight" and "this weekend" go stale after upload | Storm 0:02 "Tonight, it's pushing…". Vegas "More rain is moving in tonight". No clock time is given |
| W8 | **Inconsistent pace:** 125 to 180 wpm across seven videos | Table above |
| W9 | **The forecast-only video flopped**: El Niño, 2.1k views and 7 likes, against 6k–23k for event videos | Table above |

### 1.4 Where IWN's scripts are weak compared with Walt

| # | IWN gap | Evidence |
|---|---|---|
| G1 | **No host and no "I".** Faceless "us", no name line, no persona to trust | Sakurajima S01 "Stay with us, because…". Thailand S14 "tell us in the comments" |
| G2 | **No "certain vs. uncertain" segment.** Closes with an "As of" recap only | Sakurajima S15, Thailand S14 |
| G3 | **Clock-time dumps** | Sakurajima S03: six clock times in about 80 words. S08: "at three twenty-three, four twenty-one, five fifteen and seven fifty-six" |
| G4 | **Street lists, against IWN's own rule** | Thailand S02 "Soi Nanai Three and Soi Nanai Eight". S06 "Soi Patak Two, Four and Six" |
| G5 | **Definitions but almost no analogies** | Sakurajima S06 defines a pyroclastic flow. Thailand S03 defines a debris flow. Neither gives a picture. Walt pairs every mechanism with one |
| G6 | **No viewer-facing "what to do, when"** unless the story is local. Even then it's generic | Sakurajima: none. Thailand S12: advice with no time windows |
| G7 | **The mid-video recap repeats S01 nearly word for word** | Sakurajima S07 restates the S01 explosion facts at ~45% |
| G8 | **The open loop is a teaser with a small payoff**, and there is only one | Thailand S01 "that hillside has a deadly history" pays off once, with no second loop for the back half |
| G9 | **Built around 25–30 s clip breaks** (narration ~45–50% of runtime). That doesn't fit a continuous HeyGen read | `worflow.md` §0 and §7 |
| G10 | **Pronunciation fixed by rewording only** (edge-tts limits). HeyGen has a real glossary (§4.6) | `worflow.md` "No phonetic respellings" |

Keep from IWN: numbers written as words, one idea per sentence (~14 words), batons that name the next subject, a definition right after each term, every number tied to a source and a time, distance and direction for every new place, "never join a CTA to a plot beat with *because*", no filmer credits in narration, and facts only from `research/facts.csv`.

---

## 2. Glenn Carver's on-air voice

### 2.1 Persona

- **Who he is on air:** the steady desk anchor who reads the official data for you, translates it, and tells you plainly what to do and what isn't known yet. Calm, warm, exact. He sounds like a good local TV meteorologist talking to one viewer at a kitchen table, not a storm chaser.
- **Values he states through behavior, not slogans:** he attributes every number, admits uncertainty, names the next official update time, and never calls a record before the agency does.
- **Tone ceiling:** concern is allowed ("this is the part that worries me"), at most twice an episode. Alarm, hype and jokes about damage or victims are not.

### 2.2 First-person rules

- **Glenn may:** read, check, watch, compare and follow data. For example: "I checked the gauge record", "I'm watching the crest forecast", "here's how I read this map", "I'll tell you when that changes".
- **Glenn must never claim:**
  - to be on location, or to have seen, felt or smelled anything
  - to have interviewed anyone ("a resident told me")
  - credentials or experience ("as a meteorologist", "in my thirty years")
  - his own forecast that disagrees with the official one. He can say which official scenario he's watching.
- **"I" sparingly, "you" often.** Aim for at least twice as many "you/your" as "I/me/my" in each section.
- **"We" means Glenn and the viewer** ("we'll go day by day"), never an implied newsroom.
- **Quotes:** attribute in speech ("the Key West office put it bluntly: …"). Never put quotation marks in the paste file (§4.5).

### 2.3 Signature open line (name line), at 0:35–0:55

Pick one and keep it forever. Consistency is the brand.

1. **"I'm Glenn Carver, and this is the Carver Weather Desk."** (recommended: short, unambiguous, easy for HeyGen)
2. "This is the Carver Weather Desk. I'm Glenn Carver, and here's what you need to know."
3. "I'm Glenn Carver. On the Carver Weather Desk today: what happened, what's next, and what to do."

Right after it comes the **as-of line**: "As of [time] Eastern on [day], here's where things stand." Walt never gives one (W7).

### 2.4 Signature sign-off

Each option has a slot tied to the story's next milestone. That makes it better than Walt's generic close.

1. **"I'm Glenn Carver. Keep your alerts on, check on your neighbors, and I'll be back on the desk before [next milestone]."** (recommended)
2. "That's the desk for now. I'm Glenn Carver. Stay weather-aware, and I'll see you when [the next front / the next high tide] arrives."
3. "From the Carver Weather Desk, I'm Glenn Carver. Stay safe tonight, and I'll see you at the next update."

### 2.5 Phrases to avoid

- **AI-sounding:**
  - "delve", "dive in", "let's dive into"
  - "in today's video"
  - "it's important to note", "it's worth noting"
  - "a stark reminder", "a testament to"
  - "navigating", "amidst", "in the realm of"
  - "not just X, it's Y"
  - "buckle up", "without further ado"
- **Hype:**
  - "monster", "apocalyptic", "catastrophic" (unless an agency used the word, attributed), "unprecedented" or "record" (unless official), "insane", "shocking", "you won't believe"
  - "Mother Nature's fury", "brace yourselves", "the calm before the storm"
  - exclamation marks
- **Filler:**
  - "basically", "so yeah", "as you can see" (unless the edit shows it, §5)
  - "devastating scenes", "plumes could be seen for miles", "families left with only minutes"
  - IWN §4.7 generic lines: any sentence any storm could use
- **Teasers:**
  - "And it came at a cost.", "But that was just the beginning.", "And the search was not over."
- **Walt formulas to ration:**
  - "Here's the part…": at most 2 per episode
  - "And it isn't over": at most once
  - "There was no hurricane": once
- **CTA clichés** (the lint flags them):
  - "smash that like", "hit the bell", "ring the bell", "turn on the bell", "where are you watching from?"
  - "like and subscribe", "don't forget to subscribe", "hit subscribe", "consider subscribing", "drop a like"
  - "it really helps the channel", "if this video helped you", "if you enjoyed this video", "if you're new here"

---

## 3. Episode structure template: max 12:00 (owner, 4 Nov 2026), about 11:00 of speech

**Hard cap: the finished video is 12:00 or less.** That covers Glenn's voice, the nat-sound breaks and the end-screen tail together. `script_tools.py` estimates it as words ÷ `carver_wpm`, plus breaks, plus 4 s, and **fails the build above 12:00**, saying how many words to cut.

**Word budget:** HeyGen's speaking rate for Glenn's voice is not yet measured.

1. Plan for **~150 wpm**, which gives **~1,600–1,700 spoken words** for about 11:00 of speech.
2. Nat-sound breaks add 0–30 s on top: at most 3, each 6–10 s.
3. After the pilot (§4.8), set `carver_wpm` = words ÷ audio minutes, and `target_words` = `carver_wpm × 11`.

**Layouts:**

- `box+footage`: Glenn in the Desk Window over clips (the default). Since 6 Nov the window comes and goes, and changes size and position, inside `box*` layouts on its own (`workflow.md` › Screen layout rules). The script never times it.
- `box+map`: the window over a map or radar loop
- `box+card`: the window over an animated card or chart
- `full-host`: Glenn full screen. **At most 2 per episode, each ≤ 30 s.**
- The sign-off is **not** full-host. The end screen starts on the closing watch-next line (`cta: endscreen`), with Glenn in its large frame.

| ID | Segment | Time | Words | Layout | What goes in it |
|---|---|---|---|---|---|
| S01 | **Cold open** | 0:00–0:38 | 85–105 | box+footage | **Hook formula:** concrete number + place → why it's unusual → one history comparison → scope (2–3 places max) → "In the next few minutes, I'll show you [1], [2], and [3]." → **Open loop A** (a specific, sourced fact paid off in S07): "And there's one [thing] … I'll get to that." |
| S02 | **Name line + as-of + audience qualifier + desk report** | 0:38–0:58 | 45–60 | box+footage | Name line (§2.3), the as-of line, then "If you live anywhere from [A] to [B] … if you have family there, [segment] near the end is the part they need." Last sentence: the **desk-report invite** (§6 beat 1). **No subscribe here.** The intro sting plays on the name line. |
| S03 | **Worst-hit place first** | 0:58–2:22 | 195–225 | box+footage → box+map | Open on the place, the clock time and the number. One human-scale detail from facts.csv and one spoken visual hand-off ("On this gauge, the red line is flood stage…"). End on a baton. |
| S04 | **The scale / second place** | 2:22–3:22 | 140–160 | box+footage | Distance + direction + why the place matters. One "number made concrete" line. ★ **Mini-loop ~3:00**, paid within 60 s ("and the number that surprised me most is still coming"). From episode 2 on: the **inbox callback** (§6 beat 2), when a real report from the last video fits the story. |
| S05 | **Explainer: why it happened** | 3:22–4:46 | 195–225 | **full-host** (first 10–20 s) → box+card | **Full-host moment 1:** Glenn asks the question straight to camera, then the cut to an animated card. Mechanism in 3–4 plain sentences + **one analogy** + one history comparison. Lands at 30–40% of the runtime. ★ Mid-roll ad slot at the S05/S06 boundary. |
| S06 | **Impacts and the response** | 4:46–6:12 | 200–230 | box+footage | Roads, power, schools, rescues, crews, declarations: one impact per sentence, each with a number and who did what and when. **≤ 3 place names per sentence**; longer lists go on a card or the ticker. **Plant open loop B**: a sourced fact about the next 48 h, paid in S08 or S09. When a list is too long to read (shelters, closures, gauges), point to it with the **pinned-comment beat** (§6 beat 3). |
| S07 | **Re-anchor + payoff of loop A** | 6:12–7:17 | 150–175 | box+map or box+footage | The first sentence re-anchors: "If you're just joining me: [where], [what], [latest number], as of [time]." Then "Now, the [thing] I told you about at the start." Pay it with a real number, a mechanism and a consequence, by ~60% of the runtime. ★ Mid-roll ad slot after this section. |
| S08 | **What's next: timeline by impact window** | 7:17–8:43 | 200–230 | box+map → box+card | Group by **window, not city**: "If you're in [area], your window is [day], [time] to [time]." ≤ 3 cities per sentence, with the full city list on the timeline card. Give each window's threat and confidence. **Share-to-one-person beat** (§6 beat 4) as the last sentence. |
| S09 | **What to do** | 8:43–9:35 | 120–140 | box+card | 4–5 numbered actions, each tied to **this** event's timing or place and with a consequence. Pay loop B here if it wasn't paid in S08. |
| S10 | **Certain vs. uncertain** | 9:35–10:15 | 90–110 | **full-host** (opening 15–25 s) → box+card | **Full-host moment 2.** "Let me be straight with you about what's certain and what isn't." 2 certain points, 2 uncertain ones, **what would change the picture**, and **when the next official update comes** (office + time). Last sentences: the **subscribe-for-the-answer beat** (§6 beat 5). |
| S11 | **Bottom line** | 10:15–10:38 | 50–65 | box+footage | One-sentence summary, a callback to the hook number, and the next milestone with day and time. |
| S12 | **Question of the day + watch next + sign-off** | 10:38–10:58 | 40–55 | box+footage → **end screen** on the watch-next line | **Question of the day** (§6 beat 6) + the **watch-next line** (`cta: endscreen @ "…"`, §6) + "follow your local National Weather Service office" + sign-off (§2.4). The planner starts the end screen on the watch-next line, and Glenn talks through it. |

**Rules for the structure:**

- **Two open loops, one at a time.** A is planted at 0:30 and paid in S07 (~60%). B is planted in S06 and paid in S08 or S09. Each is a fact from `facts.csv`, never invented suspense. Each payoff opens with words that point back to the promise.
- **Retention beats roughly every 90–120 s:** a new place, a number made concrete, a visual hand-off, a mini-loop paid within 60 s, or a full-host moment. ★ marks the three manual mid-roll ad slots. Each sits at a section boundary, and the next section's first sentence must re-hook on its own.
- **Nat-sound breaks:** optional, **only at section ends**, 6–10 s each, at most 3 per episode (they count toward the 12:00 cap). Mark them `natsound_after:` in `script.md`. The editor splits the continuous HeyGen render at the section start found by alignment (§5.3) and hides the corner box during the break. A sentence is never cut (W1).
- **Full-host moments:** use only where the line needs no picture: the explainer question and the certain/uncertain opening. The sign-off plays on the end screen. Never during damage, a rescue or a timeline. Never in S01–S04.
- **Forecast-only stories** (outlooks, seasonal) need the most footage and card support. Prefer events with real footage (W9).

---

## 4. Writing rules for HeyGen TTS

### 4.1 Confirmed HeyGen facts this guide relies on

1. **Pauses in the web editor:** place the cursor and click the **Pause** button under the scene's script box. Each pause is 0.5 s, and you can edit the seconds. A scene containing only a pause gives a silent, still avatar between scenes. [help.heygen.com/en/articles/9574152-script-tips](https://help.heygen.com/en/articles/9574152-script-tips)
2. **Punctuation:**
   - commas give short breaks
   - periods give longer breaks with a downward inflection
   - hyphens split syllables for clearer pronunciation
   - don't mix languages in one script

   (same article)
3. **Numbers:** "write numbers out or use phonetic spelling".
   - 2012 → "twenty twelve"
   - 01:18 → "one minute and eighteen seconds"
   - 10-19-2016 → "October nineteenth, two thousand sixteen"
   - "150th CT NE, Redmond, WA" → "150th Court Northeast, Redmond, Washington"

   (same article)
4. **Pronunciation tool:** double-click a word → *Pronunciation* → type how it should sound. The rule is saved to the **Brand Glossary**. Examples: AI → "a-eye", AWS → "a-double you-s". (same article)
5. **Brand Glossary:**
   - lives in the app under **Brand Kit**
   - one per workspace
   - matching is case-insensitive
   - respellings are read by every voice
   - **pronunciations change the audio only. Captions and subtitles keep the original spelling.**
   - IPA is also supported, but enabled per account through sales

   [developers.heygen.com/docs/brand-glossary](https://developers.heygen.com/docs/brand-glossary) · [/docs/brand-glossary/pronunciations](https://developers.heygen.com/docs/brand-glossary/pronunciations.md)
6. **`<break time="1s"/>` tags are officially supported in API script text** (`POST /v3/videos`) and the speech endpoint. `<break>` is the only markup to use, and wrapping text in `<speak>` "can add spoken artifacts". Check `support_pause` on the voice first. [developers.heygen.com/docs/voices/speech.md](https://developers.heygen.com/docs/voices/speech.md)
7. **API limits:**
   - Avatar input script text: maximum **5,000 characters**
   - max **50 scenes** per video
   - max **30 minutes per scene**
   - multi-scene (Studio) videos run as long as the sum of their scenes

   [developers.heygen.com/docs/usage-limits.md](https://developers.heygen.com/docs/usage-limits.md)
8. **Plan limits** (HeyGen blog, updated 2 Nov 2026), max length per video:
   - Free: 1 min
   - Creator: 30 min
   - Pro: 30 min
   - Business: 60 min
   - Enterprise: no standard maximum

   Avatar IV costs 20 credits per generated minute. [heygen.com/blog/heygen-monthly-video-duration-limits](https://www.heygen.com/blog/heygen-monthly-video-duration-limits)

### 4.2 Not confirmed: test in the pilot (§4.8) before relying on them

- Whether the **web editor** honors `<break time="1s"/>` **typed into the script box**. The only documented web method is the Pause button. If the tag isn't honored, the voice might read it aloud or skip it.
- Whether the web editor has a **per-scene character limit**. The 5,000 figure is the API's. A third-party "1,200 per text box" figure is unverified and probably outdated.
- How the voice reads **em dashes, ellipses, colons, semicolons and parentheses**. No HeyGen documentation covers them.
- Glenn's voice's **words per minute**, and how it handles question intonation.
- The reliability of very long renders. One third-party write-up claims higher failure rates past 8–10 min. That is not official.

**One script (owner, 4 Nov 2026).** The owner pastes the whole episode into HeyGen as ONE script. A 12-minute script is about 9,500–10,500 characters, and the paid plans allow 30-minute videos. The 5,000-character figure is the API's per-scene limit. If the web editor ever refuses the length, `script_tools.py build --parts` writes ≤ 4,500-character parts split at section boundaries, as a fallback only.

### 4.3 Sentences

- **Average 12–16 words. Hard cap 28.** One idea per sentence, subject and verb up front.
- Long sentences with little punctuation make avatars sound machine-like (third-party observation, consistent with HeyGen's comma and period guidance).
- Use one short punch sentence per section ("It went to thirty.") for rhythm.
- No stacked clauses ("which…, who…, after…"). Split them.
- Questions are fine as section openers ("So why did the river keep rising?"). Answer them in the next sentence.
- Paragraph = section. Inside a section, start a new paragraph only where you want a breath.

### 4.4 Numbers, units, times, dates

| Write in the paste file | Not |
|---|---|
| "forty miles per hour", "gusts near forty" | 40 mph |
| "two and a half feet", "just over two and a half feet" | 2.54 ft (round unless the decimal is the story; then "two point five four feet") |
| "four to six inches" | 4-6", 4–6 in |
| "seventy-two degrees" | 72°F |
| "eighty-three percent" | 83% |
| "ten eighteen in the morning", "two in the morning", "eight in the evening", "noon", "midnight" | 10:18 a.m., 2 AM |
| "Central time", "Eastern time" (once per section where it matters) | CT, EST |
| "Tuesday, November fourth" (no year unless needed; then "twenty twenty-six") | 11/4, Nov. 4th, 2026 |
| "nineteen eleven", "two thousand five" (match normal US speech) | 1911, 2005 |
| "about four thousand customers" | 4,012 customers (round, keep the exact number on screen) |
| "Category four", "an E-F three tornado" (glossary-check "E-F") | Cat 4, EF3 |
| "Interstate ninety-five", "Highway one sixty", "State Route one seventy-nine" | I-95, US-160, SR 179 |
| "level three of four" | Level 3/4 |
| Phone number digit by digit with commas: "five one one" | 511 |

- **At most two numbers per sentence and four per section** before a sentence that interprets them.
- **No clock-time dumps** (G3): more than two clock times in a section → move them to a timeline card.
- **Every number gets a source and a time**, in speech or in the section's `facts:` line.

### 4.5 Abbreviations, symbols, punctuation

- **Agencies:**
  - First mention: "the National Weather Service". After that: "the weather service" or "the [city] office".
  - "the Storm Prediction Center", "the National Hurricane Center", "the Weather Prediction Center": never SPC, NHC or WPC.
  - **NOAA:** write "NOAA" and add a glossary entry, NOAA → "Noah". FEMA: write "FEMA" and glossary-check it. Never spell letters with periods ("N.W.S.").
- **Address abbreviations:** expand all of them.
  - St. → Saint or Street
  - Mt. → Mount, Ft. → Fort, Hwy → Highway, Blvd → Boulevard, Co. → County
  - state codes → full state names
  - a.m./p.m. → "in the morning / afternoon / evening"
- **Never in the paste file** (the voice may read them literally or stumble):
  - `[ ] ( ) { } / \ & % $ # @ * _ ~ + = < > | ^`
  - digits, URLs, hashtags, emoji, ALL-CAPS words (except glossary acronyms), markdown, quotation marks
  - Allowed exception: `<break time="Ns"/>`, and only after the pilot confirms it works in the web editor.
- **Helps:** periods (a clear stop), commas (short breath), question marks.
- **Hurts or untested:**
  - em dashes, ellipses, semicolons, colons: replace with a period or comma
  - parentheses: rewrite as a separate sentence
- **URLs:** say "on the weather service's website" and put the URL on screen. Use "weather dot gov" only if the owner wants it spoken.

### 4.6 Place names and hard words

1. **Write the real spelling in the script.** It keeps faster-whisper alignment and on-screen captions right. Then fix the sound in HeyGen's **Brand Glossary** (audio only; captions keep the spelling). Avoid in-script respellings: they would also become the caption text and break word matching.
2. Keep a running file `docs/pronunciation-glossary.csv` (`term,respelling,heard_ok_date,episode`). Add each new term to HeyGen's Brand Kit glossary before the render.
3. **Starter list to verify by ear in the pilot** (common US mis-reads; respellings are suggestions):
   - Boise → "BOY-see"
   - Willamette → "wil-AM-it"
   - Puyallup → "pew-AL-up"
   - Spokane → "spo-KAN"
   - Des Moines → "deh MOYN"
   - Gila → "HEE-luh"
   - Tehachapi → "teh-HATCH-uh-pee"
   - Ouachita → "WASH-ih-taw"
   - Natchitoches → "NAK-uh-tush"
   - Kissimmee → "kih-SIM-ee"
   - Okeechobee → "oh-kee-CHO-bee"
   - Cairo, Illinois → "KAY-roh"
   - Versailles, Kentucky → "ver-SAILS"
   - Louisville → "LOO-uh-vul"
   - Pierre, South Dakota → "PEER"
   - Arkansas River in Kansas → "ar-KAN-zus"
   - La Jolla → "la HOY-uh"
   - Sault Sainte Marie → "SOO saint muh-REE"
   - Houston Street, New York → "HOW-stun"
   - NOAA → "Noah"
4. If the glossary fails after two tries, **reword around the name** ("the river that runs through downtown") rather than respell it in the script.
5. Don't mix languages: Spanish or Native place names are fine as names, but no foreign phrases.

### 4.7 Pauses

- **Default:** no tags. Pauses come from structure: a period, a short sentence, and a new section (= a new paragraph in the paste file). Each section is one paragraph; blank lines inside `spoken:` are joined.
- **Where a real pause helps**, mark it in `script.md` as `pause: after "<words>" 0.5s` (several: separate with `|`). A pause "before X" is written as after the words that come just before X. The build inserts `<break time="0.5s"/>` into the one script only when `break_tags: true` (after the pilot confirms tags work). Otherwise the pause isn't exported, because the owner gets one script and no extra instructions. So the pacing comes from punctuation and short sentences:
  1. after the hook's key number (0.5 s)
  2. before the name line (0.5 s)
  3. before each loop payoff (0.5 s)
  4. before "Let me be straight with you" (1 s)
  5. before the sign-off (0.5 s)
- At most 8 pauses per episode. More makes the delivery drag.

### 4.8 One-time pilot (do this before episode 1)

Render a ~45 s test in the owner's HeyGen account with Glenn's voice. It should contain:

- a typed `<break time="1s"/>`
- an em dash and a colon
- "NOAA", "FEMA", "E-F three"
- "ten eighteen in the morning"
- "two point five four feet"
- three starter place names
- a question

Measure WPM and record what was read literally. Update §4.2 and set `CARVER_WPM`.

---

## 5. Script file format: two outputs per episode

Folder: `carver-weather-desk/episodes/<YYYY-MM-DD-slug>/script/`

### 5.1 `script.md` (the master; the editor works from this)

`pipeline/script_tools.py` parses this file into `script/sections.json` (schema: `docs/timeline-schema.md` §1). Write it exactly in this shape. A full working example is `episodes/0000-00-00-pipeline-demo/script/script.md`.

```markdown
---
episode: 2026-11-05-<slug>            # must equal the episode folder name
working_title: <English title>
sample: false                          # true only for test scripts (skips the facts: warning)
as_of: "Wednesday, November 5, 2026, 6:00 PM Eastern"
ticker_updated: "6:00 PM ET"           # shown on the ticker clock
target_runtime: "11:00"
target_words: 1650        # carver_wpm x 11 (12:00 cap incl. breaks + end tail)
carver_wpm: 150                        # update after the pilot
break_tags: false                      # true only after the HeyGen pilot confirms typed <break> tags work
facts: research/facts.csv
loops:
  A: {planted: S01, paid: S07, fact: F14}
  B: {planted: S06, paid: S09, fact: F22}
cta_copy:                              # on-screen CTA card copy, one per kind used in cta: (not endscreen)
  report:    {head: "IS WATER ON YOUR STREET?", sub: "Send a desk report: your town + what you see"}
  pinned:    {head: "EVERY ROAD CLOSURE, ONE LIST", sub: "The full county list is in the pinned comment"}
  share:     {head: "KNOW SOMEONE IN SOUTH FLORIDA?", sub: "Send them this before the next high tide"}
  subscribe: {head: "THE ANSWER COMES THURSDAY", sub: "Subscribe, notifications on All, and it finds you"}
  question:  {head: "DID THE ALERT BEAT THE WATER?", sub: "Yes or no. It tells us if the warnings worked"}
pinned_comment: |                      # required when a pinned CTA is used; build writes script/pinned_comment.txt
  Every road closure from tonight's update, by county (as of 6 PM ET Wed):
  Miami-Dade: ...
---

## [S01] Cold open: the ocean in the streets
layout: box+footage -> box+card @ "On this gauge"
strap: WEATHER ALERT | MIAMI BEACH, FL | KING TIDE FLOODS *MIAMI BEACH STREETS* | 2.54 ft above normal high tide at Virginia Key
ticker:
  - COASTAL FLOOD WARNING: Miami-Dade, Broward, Palm Beach until 8 PM Wed
  - Rip current risk high on all Atlantic beaches
visual: N08 | N13 @ "Collins Avenue" | card:gauge_chart @ "On this gauge"
facts: F01, F02, F05
pause: after "major flood line" 0.5s
cta: share @ "send this"            # optional; kinds in section 6
natsound_after: N17 8               # or 0
spoken: |
  The exact spoken text, indented. Line breaks inside the block are joined into one paragraph.
```

A ` # comment` at the end of a field line is ignored (not inside `spoken:`).

**Field rules** (the lint enforces every one):

- **Section header:** `## [S01] <title>`. IDs run S01, S02… in order. The title is free text and goes to `sections.json` `title`.
- **`layout:`** one of `box+footage | box+map | box+card | full-host`, or a switch chain `full-host -> box+card @ "Here's how"`.
  - `->` and `→` are both accepted.
  - The first layout starts with the section and takes no anchor. Every later one needs `@ "words"` and switches the first time those words are spoken in the section.
- **`strap:`** four fields separated by `|`: `KICKER | LOCATION | HEADLINE | subline`.
  - KICKER is one of `WEATHER ALERT | DEVELOPING | FORECAST | AFTERMATH`.
  - LOCATION is uppercase.
  - HEADLINE is uppercase and at most 40 characters, not counting the `*` marks. `*word*` marks amber emphasis.
  - The subline is at most 90 characters, sentence case. It is on-screen text, so digits and units are fine (`2.54 ft`, `8 PM`).
  - `strap: none` means no strap. A missing `strap:` line is an error.
- **`ticker:`** a YAML list. Each item is `LABEL: text`; the label is optional, uppercase, and shown bold amber.
  - A section without a `ticker:` line keeps the previous section's lines (the build writes them out in full). `ticker: []` clears it.
  - Lists the voice must not read (all counties, all roads, all crest times) go here or on a card.
- **`visual:`** an ordered, `|`-separated list:
  - `N08` is a clip: the ID prefix of `clips/lib/<ID>_*.mp4`. Exactly one file must match.
  - `card:map_storm` is `graphics/cards/<id>.mp4`. A card not rendered yet is only a warning.
  - `@ "words"` anchors that item's start to the first time those words are spoken in the section. Unanchored items fill the time in order. Anchors must run in list order.
  - Every spoken hand-off ("On this map…") must have a matching anchored card, and the reverse.
- **`cta:`** optional, `|`-separated: `share @ "words" | subscribe @ "words"`.
  - Kinds: `report | pinned | share | subscribe | question | comment | endscreen` (the beats in §6).
  - Each kind used needs a `cta_copy` entry, except `endscreen`, which has no card and only starts the end screen.
  - The CTA card appears on the anchor words, under main TR. Anchor on the first words of the ask.
  - A `pinned` CTA needs `pinned_comment: |` in the front matter.
- **`natsound_after:`** `<clip ID> <seconds>` (6–12 s), or `0`. It inserts a nat-sound break, with the host hidden and paused, after the section. At most 4 per episode.
- **`pause:`** `after "words" 0.5s`, several separated by `|` (§4.7). At most 8 per episode.
- **`cue:`** optional. The build always derives the cue from the first 6 spoken words. If you write `cue:`, it must match.
- **`facts:`** fact IDs for every number and claim. A missing line is a warning unless `sample: true`.
- **`spoken: |`** the exact text read by HeyGen, indented under the key. It must pass §4: no digits or symbols, no sentence over 28 words.
- **Anchors** (`@ "…"`, `after "…"`) match case- and punctuation-insensitively, and must occur in that section's spoken text.

Estimated times in the lint report are on the HeyGen clock: words ÷ `carver_wpm`, nat-sound breaks not counted.

### 5.2 `heygen_paste.txt` (exactly what the owner pastes)

Never write these files by hand. Build them:

```text
python pipeline/script_tools.py lint  episodes/<episode>            # report only
python pipeline/script_tools.py build episodes/<episode>            # lint, then write the outputs
python pipeline/script_tools.py build episodes/<episode> --demo     # test scripts: template/position checks become warnings
```

`build` writes nothing if there are errors (exit code 1). Warnings don't block. Outputs, all in `script/`:

- **`heygen_paste.txt`**: spoken text only, one paragraph per section, a blank line between sections. No IDs, titles, markers or placeholders. UTF-8, straight apostrophes.
- **One script only** (owner, 4 Nov): no part files and no pause list. `--parts` is a fallback only, for if HeyGen refuses the full length.
- **`sections.json`**: the edit handoff (`docs/timeline-schema.md` §1).

**What the lint checks:**

| Errors (always) | Template / position: errors, warnings with `--demo` | Warnings |
|---|---|---|
| Forbidden characters in spoken text: `[0-9[](){}/\&%$#@*_~+=<>\|^"“”…—–;:!]` | Section word counts vs the §3 template ±15% (ranges scale with `target_words`) | Card mp4 not rendered yet |
| Abbreviations (mph, a.m., St., Hwy…) and ALL-CAPS words not in the glossary (NOAA, FEMA, TV allowed) | Section count ≠ 14 | Banned phrases (§2.5), "Here's the part" > 2 |
| Sentence > 28 words | Name line outside 0:35–0:55 | Average sentence > 16 words |
| Total words outside `target_words` ±5% | Any CTA before 2:00 (a `report` CTA: before the name-line window) | Nat-sound outside 6–12 s, more than 4 breaks |
| Estimated video > 12:00 | Full-host before 2:30 | More than 8 pauses, pause words that occur twice |
| Cue not unique anywhere in the script, or starting with a number word | | Missing `facts:` (unless `sample: true`) |
| Any `@`/`after` anchor not in the section's spoken text, or anchors out of order | | Missing name line |
| Strap: 4 fields, kicker list, headline ≤ 40 uppercase, subline ≤ 90 | | |
| Full-host in more than 3 sections, or one stretch over 30 s | | |
| Clip ID with no `clips/lib/<ID>_*.mp4` (or several), nat-sound clip missing | | |
| Unknown `cta` kind or no `cta_copy` for it, bad field syntax, missing `layout`/`strap`/`spoken` | CTA plan: a missing report / share / subscribe / (question or comment) beat; the same beat twice (comment: three times) | Two CTA asks less than 75 s apart |
| More than 6 CTA asks; a `pinned` CTA without `pinned_comment` | | |

### 5.3 Finding section starts in the HeyGen audio (for alignment)

1. **Distinctive first words.** The first 6 words of every section must be unique across the script.
   - Never start two sections the same way ("Now, let's…").
   - Include at least one content word (place, river, day or object).
   - **Don't start with a number word or a hard proper noun**: whisper writes numbers as digits and may mangle rare names. Good: "Let's start in Sedona, where…", "The weather service in Key West…", "So why did the river keep rising…".
   - Put the hard name third to sixth, not first.
2. **Align:**
   1. Extract audio from the HeyGen MP4 and run faster-whisper (`medium.en` or better, `word_timestamps=True`).
   2. Normalize both sides: lowercase, strip punctuation, convert digits to words (`num2words`), apply glossary-term mappings.
   3. For each section in order, search forward from the previous match for the 6-word cue (fuzzy ratio ≥ 80 over a sliding 6-token window, within ±60 s of the expected time from cumulative word counts ÷ `CARVER_WPM`).
   4. Start = first word's start − 0.15 s.
   5. Confirm with the silence just before it (≥ 0.3 s; it is longer at multi-scene boundaries).
   6. Write `edit/section_times.json` (`{"S01": 0.00, "S02": 41.8, …}`) and flag any section with no match ≥ 80.
3. Sub-section cues (card appearances) use the same method with the `visual:` hand-off words.

---

## 6. CTA beats: spoken and on screen (owner, 6 Nov 2026)

The owner wants more subscribers and engagement, "but it doesn't need to be typical".

So the asks are never "please subscribe". Each one is a **beat with a job**:
- the viewer gets something (an answer, a list, a voice in the next update), or
- does something useful (warn one person, report what they see).

Walt's channel shows what not to do (§1, W5): generic subscribe pleas earn 1 to 26 comments per video.

Each beat has a `cta:` kind. The planner shows that kind's card (`cta_copy`) on the anchor words, with Glenn's window up as main TR. Fill every [slot] from `facts.csv` or real viewer comments.

| # | Beat | Where | `cta:` kind | Job |
|---|---|---|---|---|
| 1 | **Desk report** | S02, the last sentence | `report` | Earliest engagement, and it makes the viewer a contributor, not an audience |
| 2 | **Inbox callback** | S04, from episode 2 | none (it isn't an ask) | Proves the comments get read, which is what makes beat 1 work |
| 3 | **Pinned list** | S06 (or wherever a list is too long to speak) | `pinned` | Turns a list Glenn can't read out into a visit to the comments |
| 4 | **Share to one person** | S08, the last sentence | `share` | Sharing when it's most useful: right after the timeline |
| 5 | **Subscribe for the answer** | S10, the last sentences | `subscribe` | Subscribing as the way to get the one thing still unknown |
| 6 | **Question of the day** | S12, before the watch-next line | `question` (or `comment`) | A one-word answer is easy, and it serves the story |
| | **Watch next** | S12, starting the end screen | `endscreen` (no card) | Keeps the session going: names the video on the end screen |

**Rules:**

- **At most 6 asks** per episode (`report`, `pinned`, `share`, `subscribe`, `question`, `comment`), **at least 75 s apart**, and never the same beat twice. The exception is `comment`: at most twice, and only as different check-ins.
- **At most 2 sentences per beat**, about 35 words.
- No ask inside a damage, casualty, rescue or timeline sentence. Never join an ask to a plot beat with "because" or "so".
- **Deaths or injuries in the story:** beats 1 and 6 ask for information (a report, a check-in, did the alert arrive), never an opinion or a poll about the disaster. Drop beat 6 if it can't be both useful and respectful.
- **Subscribe is asked once** (beat 5). The end screen's subscribe button does the rest.
- **Notifications:** say "notifications on All" only inside beat 5. Never "bell".
- **Honesty:** promise only what the channel does.
  - "I read them" means the owner or I really read them, and beat 2 proves it.
  - "My next update before Thursday" means one is planned.
  - The pinned comment must exist, written in `pinned_comment:`.
- **Inbox callbacks quote real comments only**, from the previous Carver upload. Give the first name or handle and the town exactly as the viewer wrote them, and keep it short. If no comment fits the story, skip the beat. Never invent one.

**Lines to adapt** (rewrite them every episode; never paste the same wording twice in a row):

1. **Desk report** (`report`):
   - "If you're in [area] right now, you're my eyes on the ground. Tell me your town and one thing you're seeing, water, wind or power, and I'll read the best reports in my next update."
   - "If you've measured the water at your place, put the number and your town in the comments. Official gauges are miles apart, and your report fills the gap."
2. **Inbox callback** (no card):
   - "After my last update, [handle] in [town] wrote that [their report in a few words]. That's exactly what the gauge showed an hour later."
   - "A lot of you in [area] told me [pattern from comments]. Here's why that happened."
3. **Pinned list** (`pinned`):
   - "There are [number] closures, and I won't read them all. Every one, by county, is in the pinned comment."
   - "Your county's shelter and the number to call are in the pinned comment. Find yours now, before you need it."
4. **Share to one person** (`share`):
   - "Think of one person in [window towns] who won't see the alert in time. Send them this before [window start]."
   - "If someone you love sleeps through storms, send them this now, and ask them to turn on emergency alerts tonight."
   - "If someone is driving [route] this [weekend], send them the window I just gave you. It could save them hours on a closed road."
5. **Subscribe for the answer** (`subscribe`):
   - "The one thing I can't tell you yet is [uncertainty]. The weather service will know by [time]. Subscribe, set notifications to All, and you'll have my answer before [event]."
   - "The next [crest / high tide / round] that matters is [day] [time of day]. Subscribe, and my update will be up before it arrives, not after."
6. **Question of the day** (`question`):
   - "One question before I go. Did the alert reach your phone before the water did? Yes or no in the comments. It tells me, and the forecasters, whether the warnings worked."
   - "Quick one for you: how much rain did you get? Just the number and your town. I'll put the highest totals in my next update."
   - Use `comment` instead for a check-in: "If your power is still out, tell me the neighborhood and how long it's been. It helps people nearby see who is still waiting."
- **Watch next** (`endscreen`):
   - "If you want to see how [similar past event] played out, that's the video on your screen now. It's the closest thing we have to a preview."
   - "The video on your screen walks through [related topic]. It's the best next ten minutes if you're in [area]."

Always end with "And follow your local National Weather Service office and your emergency officials." (Walt does this; keep it.) Then the sign-off (§2.4).

**On-screen cards** (`cta_copy`): the head is a question or a promise in at most 30 characters. The sub says what to do in at most 50 characters. Cards: `brand-kit/styleframes/cta-2026-11-06/cta_cards.jpg`.

---

## 7. Worked example (EXAMPLE ONLY: placeholders, no real facts)

This is an invented scenario to show the rules. A river is forecast to crest after rain has ended. Every bracket is a placeholder for a number or name from `facts.csv`. In the real `heygen_paste.txt`, the brackets are replaced by words and the lint blocks any that remain.

**Draft in `script.md`:**

```markdown
## [S01] Cold open: The river is still rising
layout: box+footage
strap: WEATHER ALERT | [TOWN], [ST] | [RIVER] *STILL RISING* | Crest forecast [CREST FT] ft [CREST DAY], flood stage [FLOOD STAGE] ft
ticker:
  - FLOOD WARNING: [RIVER] at [TOWN] until [DAY] [TIME]
  - FORECAST CREST: [CREST FT] ft [CREST DAY]
visual: [CLIP ID] | card:crest_record @ "only gone higher"
facts: [F01 crest forecast], [F02 flood stage], [F03 record crests], [F04 rain ended]
cue: The rain stopped [DAY] morning, but
pause: after "still on its way" 0.5s | after "I'll get to that" 0.5s
spoken: |
  The rain stopped [DAY] morning, but the [RIVER] River is still rising. The weather service expects it to crest in [TOWN], [STATE], at [CREST FT IN WORDS] feet by [CREST DAY] night. Flood stage there is [FLOOD STAGE IN WORDS] feet. The river has only gone higher [N IN WORDS] times since records began, and the last time was [RECORD YEAR IN WORDS]. The water that will do it fell days ago, upstream. It's still on its way. In the next few minutes, I'll show you what the river has already done, why a river can keep rising after the sky clears, and exactly when the crest reaches each town. And there's one [LOOP A OBJECT, e.g. a bridge with a published closure level] on this river that matters more this week than the crest itself. I'll get to that.

## [S02] Name line
layout: box+footage
strap: none
visual: [CLIP ID] | [CLIP ID] @ "If you live along"
cue: I'm Glenn Carver, and this is
spoken: |
  I'm Glenn Carver, and this is the Carver Weather Desk. As of [TIME IN WORDS] Eastern on [DAY], here's where things stand. If you live along the [RIVER] from [UPSTREAM TOWN] down to [DOWNSTREAM TOWN], or you cross it on [HIGHWAY IN WORDS] to get to work, this is your week. And if you have family there, the timeline near the end is the part they need.

## [S03] [WORST-HIT TOWN]: the fastest rise
layout: box+footage → box+card @ "On this gauge"
strap: DEVELOPING | [WORST-HIT TOWN], [ST] | RIVER UP *[RISE FT] FT* IN [HOURS] HOURS | Gauge at [GAUGE NAME], [TIME] [DAY]
visual: [CLIP ID] | card:gauge_hydrograph @ "On this gauge"
facts: [F06 gauge reading 1], [F07 gauge reading 2], [F08 closure]
cue: Let's start in [WORST-HIT TOWN], where
spoken: |
  Let's start in [WORST-HIT TOWN], where the river came up fastest. On [DAY] evening, the gauge there read [GAUGE HEIGHT IN WORDS] feet. By [TIME IN WORDS] the next morning, it read [GAUGE HEIGHT 2 IN WORDS]. That's [RISE IN WORDS] feet in [HOURS IN WORDS] hours, [RELATABLE COMPARISON, only if the math holds, e.g. about the height of a basketball hoop]. On this gauge, the red line is flood stage. The river crossed it at [TIME IN WORDS], and it hasn't come back down…
```

**What it shows:**

- **Hook:** the number, place, rarity and scope come in the first 25 s, then a promise of three, then loop A.
- **Name line:** ~0:38, followed by the as-of time and an audience qualifier that teases the timeline (S08) instead of asking for a subscribe.
- **First-section cue:** a unique 6-word cue that starts with common words, not the hard name.
- **Visual hand-off:** "On this gauge" is matched by a `visual:` entry.
- **Numbers:** at most two per sentence, all as words. No dashes, colons or brackets will reach the paste file.
- **Glenn's claims:** he reads the data and never claims to have been there.

**The same S02 in `heygen_paste.txt`** (after the slots are filled, illustrated with neutral words):

```text
I'm Glenn Carver, and this is the Carver Weather Desk. As of six o'clock Eastern on Wednesday, here's where things stand. If you live along the river from the upper valley down to the delta towns, or you cross it on the interstate to get to work, this is your week. And if you have family there, the timeline near the end is the part they need.
```

---

## 8. Pre-flight checklist (per script)

- [ ] Runtime math: words ÷ `CARVER_WPM` + nat-sound breaks = 13:00–15:00.
- [ ] Hook formula complete. Name line at 0:35–0:55. As-of line spoken.
- [ ] Two loops (A paid in S07 by ~60%, B in S08 or S09), each a facts.csv fact, each payoff pointing back to its promise.
- [ ] One analogy in the explainer, at 30–40% of runtime. At least 3 "numbers made concrete" lines.
- [ ] No spoken list over 3 names. No more than 2 clock times per section. Lists are on cards or tickers.
- [ ] Every spoken visual hand-off has a `visual:` entry.
- [ ] What to do: 4–6 numbered steps, each with this event's timing or consequence.
- [ ] Certain vs. uncertain, with what would change it and the next official update time.
- [ ] CTA beats (§6): desk report (S02), inbox callback if there is a real report (S04), pinned list if a list exists (S06), share to one person (S08), subscribe for the answer (S10), question of the day + watch next (S12). Every slot filled from the story; the pinned comment is written; at least 75 s between asks.
- [ ] At most 3 full-host moments, all ≤ 30 s, none in S01–S04.
- [ ] Banned phrases (§2.5) absent. "Here's the part…" ≤ 2.
- [ ] Lint passes (§5.2). Estimated video ≤ 12:00 (the lint checks it). One script. Cues unique. New hard names added to the Brand Glossary.
- [ ] No beat copied from an earlier Carver episode unless it's updated and framed as an update ("Last time I told you… here's what changed").
