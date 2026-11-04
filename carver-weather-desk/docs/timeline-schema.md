# Carver edit formats: `sections.json` (script → edit) and `timeline.json` (edit → render / CapCut)

The renderer (`pipeline/compose.py`, an ffmpeg MP4) and the CapCut builder (`pipeline/build_capcut.py`) both read the same `edit/timeline.json`. That keeps the MP4 and the draft identical.

## 1. `script/sections.json` (written by `pipeline/script_tools.py` from `script/script.md`)

```json
{
  "episode": "2026-11-05-slug",
  "as_of": "Wednesday, November 5, 2026, 6:00 PM Eastern",
  "ticker_updated": "6:00 PM ET",
  "cta_copy": {
    "share":     {"head": "KNOW SOMEONE IN SOUTH FLORIDA?", "sub": "Send them this before the next high tide"},
    "comment":   {"head": "WHAT'S YOUR STREET LOOK LIKE?",   "sub": "Tell Glenn where you are in the comments"},
    "subscribe": {"head": "GET THE NEXT UPDATE",            "sub": "Glenn is back before Thursday's high tide"}
  },
  "sections": [
    {
      "id": "S01",
      "title": "Cold open: the ocean in the streets",
      "layout": [{"layout": "box+footage", "at": null}, {"layout": "box+card", "at": "On this gauge"}],
      "strap": {"kicker": "WEATHER ALERT", "loc": "MIAMI BEACH, FL",
                "head": "KING TIDE FLOODS *MIAMI BEACH STREETS*", "sub": "2.54 ft above normal high tide at Virginia Key"},
      "ticker": [{"label": "COASTAL FLOOD WARNING", "text": "Miami-Dade, Broward, Palm Beach until 8 PM Wed"}],
      "visual": [{"kind": "clip", "id": "N08", "at": null},
                 {"kind": "card", "id": "gauge_chart", "at": "On this gauge"}],
      "cta": [{"kind": "share", "at": "send this"}],
      "natsound_after": {"clip": "N17", "sec": 8},
      "pause": [{"after": "major flood line", "sec": 0.5}],
      "cue": "The ocean in Miami Beach",
      "spoken": "…exact spoken text…",
      "words": 104
    }
  ]
}
```

Notes on the fields:

- `layout` values are `box+footage | box+map | box+card | full-host`.
  - `at` holds words from that section's spoken text. The layout switches at the first time those words are spoken.
  - `null` means the layout starts with the section.
- `strap.head`:
  - one line of 40 characters or fewer
  - `*word*` = amber emphasis
  - `strap: null` means no strap for that section
- `visual` lists the section's pictures in order.
  - A `clip` is a footage ID from `clips/lib/<ID>_*.mp4`. A `card` is `graphics/cards/<id>.mp4`.
  - `at` anchors where an item starts. Items without an anchor fill the time in order.
- `cta.kind` is `share | comment | subscribe`.
  - `at` holds the spoken words the card appears on.
  - The card copy comes from `cta_copy`.
- `natsound_after` is optional. It inserts a nat-sound break, with the host hidden and paused, at the END of the section.

## 2. `edit/timeline.json` (written by `pipeline/plan_edit.py`)

```json
{
  "version": 1,
  "name": "CWD_slug_v1",
  "root": "<repo>/carver-weather-desk/episodes/2026-11-05-slug",
  "w": 1920, "h": 1080, "fps": 30,
  "duration": 845.2,
  "tracks": [
    {"name": "base",      "type": "video", "items": [ … ]},
    {"name": "host_full", "type": "video", "items": [ … ]},
    {"name": "host_box",  "type": "video", "items": [ … ]},
    {"name": "chrome",    "type": "video", "items": [ … ]},
    {"name": "straps",    "type": "video", "items": [ … ]},
    {"name": "cta",       "type": "video", "items": [ … ]},
    {"name": "ticker",    "type": "video", "items": [ … ]},
    {"name": "bug",       "type": "video", "items": [ … ]},
    {"name": "wipes",     "type": "video", "items": [ … ]},
    {"name": "vo",        "type": "audio", "items": [ … ]},
    {"name": "sfx",       "type": "audio", "items": [ … ]}
  ],
  "markers": [{"t": 0.0, "label": "S01 Cold open"}]
}
```

**Tracks** run bottom to top in list order. Items on one track never overlap.

**Video item:**

```json
{"src": "edit/base/b001.mp4", "start": 12.0, "dur": 5.5, "in": 0.0,
 "x": 0, "y": 0, "w": 1920, "h": 1080, "volume": 0.0, "opacity": 1.0, "fade_in": 0.0, "fade_out": 0.0}
```

- `src` is relative to `root`, or absolute. Accepted formats:
  - `.mp4`: opaque h264
  - `.mov`: ProRes 4444 with alpha
  - `.png` / `.jpg`: still
- `start` and `dur` are timeline seconds. `in` is the source in-point in seconds; stills ignore it.
- `x, y, w, h` is the placement rectangle in canvas pixels, top-left origin. The default is the full frame.
  - Sources are pre-rendered at exactly `w × h`, so no resampling is needed. Stills may differ; they are scaled to the rectangle.
- `volume` is the item's own audio. The default is 0 (muted). Base footage uses about 0.07 under the voice and 1.0 in nat-sound breaks. `fade_in` / `fade_out` are audio fades in seconds.

**Audio item:**

```json
{"src": "host/vo.wav", "start": 0.0, "dur": 41.8, "in": 0.0, "volume": 1.0, "fade_in": 0.0, "fade_out": 0.0}
```

**Conventions:**
- `host_box` items are cut from `host/host_box.mp4`, the HeyGen video pre-cropped to 536×302 and placed at x 1344, y 38. `host_full` items are cut from `host/host_full.mp4` (1920×1080).
- Both share the HeyGen clock: `in` = HeyGen time.
- `vo` items use the same `in` values as the host video items, so lips and voice stay in sync.
