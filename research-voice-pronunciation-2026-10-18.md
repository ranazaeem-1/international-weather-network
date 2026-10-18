# Narration voice and pronunciation research, 18 Oct 2026

Scratch data and scripts: `C:\Users\hp\AppData\Local\Temp\claude\C--Users-hp-Desktop-international-weather-network\2d1f4672-c3e1-4152-a623-9de471c252d0\scratchpad\cmp\` (embeddings in `embed2.py`, ASR in `t2/`, A/B audio in `ab/wav/`). No episode or pipeline files were changed.

The work was cut short by a time limit, so some parts are incomplete. These are listed at the end.

---

## TL;DR

1. **The `SAY` respellings cause most of the pronunciation errors viewers hear.** edge-tts reads ALL-CAPS syllables as letters. "Cap-ih-STRAH-no" comes out as "Cap-I-C-H-S-D-R-H-N-O", "BAH-zih-lohn" as "B-H-H lone", and "Ko-JAH-eh-lee" as "Ko-J-H-lee". YouTube's own captions on the published Norte video (9SnWUC0iIAU) show this: "San Juan Caphsdn No", "San 1 cap HSD know", "BH Loan Road", "TJ Maju Vier", "via lammy dda and via de hqua", "Sano H no Frey". The respelling for San Clemente ("San CLEM-ent") is also simply wrong and produces "San Clement" every time.
2. **The A/B test shows the plain name almost always works better.** With the plain written name, Andrew Multilingual is recognisable in 9 of 10 test names. With the respelling it is recognisable in 1 of 10.
3. **Custom SSML does not work on the free edge-tts endpoint.** Every inline tag returned no audio: `<phoneme>` (ipa and sapi), `<sub>`, `<lang>`, `<break>`, `<say-as>`, `<emphasis>`, nested `<prosody>`, and a voice switch. Only the outer `<speak xml:lang>` attribute is accepted.
4. **The GWN voice is not identified. It matches none of the 47 voices tested** (edge-tts, ElevenLabs premade, OpenAI). Its pitch is also about 3.5 semitones higher than Andrew's. Confidence that it is none of the tested voices is high. Confidence about what it actually is: low.
5. **GWN does say place names well.** Whisper gets most of its names right or nearly right, with no spelled-out letters.

**Recommended fix (free, takes minutes):** empty every `SAY` dict and keep the real names in the script. Where a respelling is truly needed, write it in lowercase as one word with no hyphens or capitals, and test it once.

---

## Task 1: GWN narration voice

### Method
- **GWN samples:** 12 narration-only stretches (20–27 s each), cut where the captions show narration with no `>>` speaker change. Six came from Aw0nrvtMUr0 (Norte / San Clemente) and six from 3OAlVFwN61Y (Turkey).
- **Calibration samples:** 4 stretches from IWN's published video Fa0pKDdD3fE (Andrew Multilingual) and 6 raw IWN narration mp3 files.
- **Candidates (47 voices):**
  - 16 edge-tts voices, three ~15 s texts each: Andrew, AndrewML, Brian, BrianML, Christopher, Eric, Guy, Roger, Steffan, Ryan (UK), Thomas (UK), William ML (AU), Liam (CA), Connor (IE), Mitchell (NZ), Luke (ZA). Davis, Tony and Jason are not offered on the edge endpoint; it returned no audio for them.
  - 25 ElevenLabs premade previews, fetched without an API key: Adam (new and old), Antoni, Arnold, Bill, Brian, Callum, Charlie, Chris, Clyde, Daniel, Drew, Eric, Fin, George, Harry, Josh, Liam, Michael, Paul, River, Roger, Sam, Thomas, Will. The previews are only 1.5–5.7 s long.
  - 6 OpenAI TTS samples from OpenAI's public docs: alloy, ash, echo, fable, onyx, sage.
  - Not tested: Google, Polly, Murf, Speechify and Azure HD voices have no public previews reachable without login. The ElevenLabs Voice Library (community voices) needs a login to search.
- **Embeddings:** Resemblyzer (GE2E) and SpeechBrain ECAPA-TDNN. ECAPA separates speakers far more sharply.

### Calibration: what a real match looks like
| Comparison | Resemblyzer | ECAPA |
|---|---|---|
| IWN published video vs edge Andrew Multilingual (known same voice) | 0.946 | **0.935** |
| IWN video vs edge Andrew (non-ML, sibling voice) | 0.859 | 0.815 |
| Short 3 s crops of GWN vs GWN centroid (same voice, short clip) | 0.896 mean | **0.79 mean, 0.69 min** |

A true match should therefore score at least ~0.7 on ECAPA, even from a short preview.

### GWN ranking (centroid cosine)
| Rank by ECAPA | Candidate | Resemblyzer | ECAPA |
|---|---|---|---|
| 1 | ElevenLabs Josh | 0.616 | 0.357 |
| 2 | ElevenLabs Liam | 0.642 | 0.304 |
| 3 | edge Guy | 0.699 | 0.260 |
| 4 | edge Andrew | 0.733 | 0.250 |
| 5 | edge Andrew Multilingual (IWN's voice) | 0.778 | 0.248 |
| 6 | edge Brian / Brian ML | 0.717 | 0.238 |
| 7 | ElevenLabs Arnold | 0.637 | 0.236 |
| (Resemblyzer #4) | ElevenLabs Chris | 0.756 | 0.13 |

**No candidate comes close.** The best ECAPA score, 0.36, is far below the 0.69 minimum for the same voice. On Resemblyzer, Andrew Multilingual is the nearest at 0.78 against 0.95 for a real match. That fits the 8 Oct decision to choose Andrew because it sounded "close to GWN", but it is a different voice.

### Prosody
| | Median F0 | F0 range (5–95%) | Speaking rate |
|---|---|---|---|
| GWN | **135 Hz** | 10.4 st | **~169 wpm** (captions, 12 clips, 155–185) |
| IWN Andrew ML (published / raw) | 110 Hz | 13.4–14.1 st | 126 wpm (Fa0 video). Current scripts run ~136–145 wpm counting edge-tts silences |

- GWN is about 3.5 semitones higher, slightly flatter in pitch, and about 25–30% faster.
- Pause counts for GWN are less reliable because footage sound sits under its narration.
- Candidates within ±1 semitone of GWN's pitch: ElevenLabs Bill, Daniel, Paul and Liam, edge Roger, and OpenAI alloy. All of them score low on the embeddings.

### Verdict
- **The service is unidentified.** It is not edge/Azure-neural Andrew, Brian, Guy or Christopher. It is not any current or legacy ElevenLabs premade voice, and not any OpenAI voice.
- **Likely possibilities, all unverified:**
  - an ElevenLabs Voice Library or custom/cloned voice
  - a paid voice I could not sample (Azure HD "Dragon", Google Studio, WellSaid, Murf and similar)
  - a human narrator
- One weak hint: GWN's captions contain "[clears throat]" inside a narration line at 3OAlVFwN61Y 7:20. That would fit a human or ElevenLabs v3, but it might also be sound from the footage underneath.
- If GWN really is the user's own other channel (memory note from 16 Oct), its production notes will answer this directly.

### Does GWN mispronounce names?
These are faster-whisper medium.en transcripts of GWN narration around each name, plus YouTube's auto-captions.
- **Correct:**
  - San Clemente (×3)
  - San Juan Capistrano (×3)
  - Norte, Santa Ana
  - Steve Concialdi (whisper even got the spelling)
  - Fatih, Ayazaga, Başiskele (YouTube wrote the ş)
  - Sakarya, Yalova, Abdullah Macit, Sadabad, Samsun
  - Erdoğan (YouTube)
- **Close, minor drift:** Sarıyer → "Sarriere", Kağıthane → "Kegathain", Davut Gül → "Dabuk Gul", Kocaeli → "Kekeli", Sapanca → "Saponka", Karasu → "Kurasu", Kastamonu → "Castamonu", Pehlivan → "Pelivan".
- **No spelled-out letters and no garbled strings.** GWN's names are anglicised but recognisable. That is the standard to aim for.

---

## Task 2: IWN pronunciation audit

### Method
- **Transcription:** faster-whisper medium.en (int8, beam 5, word timestamps, no prompt) on every narration mp3. Each mp3 was compared word by word with its `.ok` paragraph text, after normalising numbers to words. The scripts write every number out in words.
- **Coverage:** Norte (39 files) and Turkey (39 files) are complete. São Paulo, Malibu, Pendleton and the Spanish episode were not transcribed because the machine was heavily loaded by other jobs.
- **Supporting evidence:** YouTube auto-captions of the published IWN videos (9SnWUC0iIAU Norte, 9qvtZhVUEwk Pendleton, VMWI72S7kp8 Malibu, Fa0pKDdD3fE Turkey 15 Oct).

### Results
| Episode | Words | (a) broken by SAY respelling | (b) mangled without a respelling | (c) numbers / dates / units |
|---|---|---|---|---|
| Norte (SAY: 14 entries) | 932 | **15** | 0 | 0 |
| Turkey 17 Oct (SAY: 23 entries) | 853 | **22** (plus ~6 that are only slightly off) | **8** (borderline) | 0 |

**(a) Norte, broken by respellings (whisper output):**
- San Clemente → "San Clement" ×4. The respelling itself is wrong.
- Capistrano → "Capuchas Dr. H", "Cap-I-C-H-S-D-R-H-N-O", "cap hstrh no", "kappa hsdrh no" ×2
- Via La Mirada → "ma-ra-h-da", "Mayrajda"
- Via De Agua → "Hgua"
- Basilone → "BHH Lone"
- McGovern → "Maggiu-Vierne"
- Portico → "Puertaico"
- Borderline but acceptable: San Onofre → "oh no fray", Trancas → "troncus", Eminencia → "emanencia".

**(a) Turkey, broken by respellings:**
- Ayazağa ×3 → "awai h zahr", "awa hsa"
- Sarıyer → "isayet riyur"
- Fatih → "fh thai"
- Kağıthane ×2 → "ka thne", "katiajne"
- Kocaeli ×4 → "ko j h lees", "koja hle", "cojhle", "kojehli"
- Başiskele → "bethany h le"
- Mustafa Çiftçi → "emoesta fakhchivchi"
- Ahmet Derin → "derayen"
- Mustafa Gedikli → "moos tafak gage k lee"
- İzmit → "aisey amaiti" (from "IZ-mit": the capitals I and Z were read out as letters)
- Sapanca → "sapie chenjia"
- Davut → "davioti"
- Göktaş → "gokthsh"
- Yalova → "yh lova"
- Osmaniye / Kahramanmaraş → "osecen komacemirac"
- Erzincan → "erzy john"
- Roughly fine: Beykoz, Turgut Dursun, Yarımca, Akçay, Çiftçi on its own.

**(b) Turkey, no respelling but still mangled:** Sakarya ×5 → "sicaria/sicario", Mersin ×2 → "mayors senior", "mersenne", Hatay → "hatui".

**(c) Numbers:** no errors found. Every number is written out in words in the scripts. The only differences were whisper's own formatting, such as "1133" for "eleven thirty-three".

**The mechanism:**
- edge-tts treats any capitalised chunk of two or more letters (STRAH, BAH, JAH, IZ, NAHL) as an initialism and spells it out.
- A trailing "h" (ah, eh, uh) is often voiced as "H".
- The hyphens break each name into separate English-looking words.

The older Turkey episode (15 Oct) had an empty `SAY`. Its YouTube captions mostly show the raw names correctly: Sapanca, Sultangazi, Basaksehir, Arnavutkoy, Kucukcekmece, Kocaeli, Sakarya. There was one miss ("Bisaccia" for Başakşehir).

### A/B test (edge-tts Andrew Multilingual −6%)
- **Setup:** 20 names, each in the carrier sentence "Officials say flooding hit X again on Tuesday."
- **Versions generated:** raw, SAY respelling, accents stripped, lowercase easy spelling, edge Brian, edge Guy and a native-voice reference. All are in `ab/wav/`.
- **Scored:** only 10 names, raw vs respelled, with whisper small.en, because of the time limit.

| Name | Raw spelling → heard as | SAY respelling → heard as | Winner |
|---|---|---|---|
| Kağıthane | Kajithan | Katiejne | raw |
| Sarıyer | Sariur | S. Atria | raw |
| Başiskele | basis skill | Boston H-Lag | raw |
| Kocaeli | Kokili | COJHLE | raw |
| Brasilândia | Brazelandia | Brazil-HNGA | raw |
| San Juan Capistrano | San Juan Capistrano ✔ | SAN. One Kappa HSDRH know | raw |
| Calabasas | Calabasas ✔ | Calleby HSUS | raw |
| San Clemente | San Clemente ✔ | San Clement | raw |
| Basilone | Barcelona ✗ | BHZIH loan ✗ | both bad |
| Mustafa Çiftçi | Mustafa Sifsi | Muztafak Chif-Chi | respelling slightly better (raw reads Ç as "s") |

**Raw wins 8 of 10.** The respelling helps only where the raw name contains a letter that English readers do not know, such as Ç. Even then the capitals and hyphens make it worse than a lowercase spelling would. The native tr-TR/pt-BR reference voices could not be scored with English ASR.

---

## Recommendations, in priority order

1. **Empty every `SAY` dict now.** This is free and removes the errors category (a) is built from: 15 of 15 in Norte and 22 of ~30 in Turkey. Andrew Multilingual already handles Spanish and Californian names well (Capistrano, Calabasas, Clemente), and handles Turkish and Portuguese tolerably.
2. **When a respelling is truly needed, write it as one lowercase word with no hyphens or capitals.** Examples: "chiftchee", "bahzeelohnay". Generate it once and check it with `tts_probe`-style listening or with whisper. Never use ALL-CAPS stress marks. Only a handful of names should need this: Basilone, Çiftçi, Sakarya and similar.
3. **Fix the bad respelling outright:** San Clemente should simply be "San Clemente".
4. **SSML phoneme/sub/lang is not available on the free endpoint.** Every tag tested was rejected. Doing this properly needs paid Azure Speech, which supports `<phoneme>` and `<lang>` with the same Andrew Multilingual voice and a custom lexicon. Azure's free tier gives 0.5 M characters per month, roughly 60 episodes, and needs an Azure key.
5. **Switching to another free edge voice does not help.** Every edge voice reads respellings the same way. Brian and Guy were not scored for names.
6. **Do not pay to copy GWN's voice; it could not be identified.** If the goal is GWN-like quality on names, ElevenLabs (Multilingual v2 or v3) is the obvious paid option. But GWN is not any ElevenLabs premade voice, so this would only be "similar", not the same voice.
7. **Optional QA step:** run whisper on each new episode's narration and flag script proper nouns that whisper does not reproduce. Norte took about 35 min of CPU here while the machine was heavily loaded, and would be much faster on an idle machine.

## Not completed (time limit)
- ASR audit of São Paulo, Malibu, Pendleton and the Spanish Norte episode.
- Full A/B scoring of 20 names × 7 versions. The audio for all of them is generated in `ab/wav/`, and the scorer is `ab/ab_score.py`.
- Testing whether the outer `xml:lang` override (`ab/outer_*.mp3`) actually changes pronunciation.
- Google, Polly, Murf, Speechify and ElevenLabs Voice Library voices were not tested (no public previews without login).
