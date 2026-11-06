# Carver info cards: spec format

Cards are the full-frame pictures under the host box: maps, numbers, charts, timelines, lists. The compositor adds the host box, bug, strap and ticker on top. **Cards never draw those.**

- Templates: `pipeline/cards/<type>.html`, sharing `brand-kit/src/brand.css` and `pipeline/cards/card.css` / `card.js`.
- Renderer: `pipeline/make_card.py`, which calls `pipeline/render_html.py`.
- Samples: `brand-kit/styleframes/cards/<type>.json` → `<type>.mp4` + `<type>.png`. `_cards_sheet.jpg` shows them with the reserved zones outlined.

## 1. Rendering

```
python pipeline/make_card.py <spec.json> [out.mp4] [--png [out.png]]
python pipeline/make_card.py a.json b.json c.json --png -j 4      # several specs, 4 processes
python pipeline/make_card.py --episode episodes/<ep> [--force]    # stale graphics/cards/*.json, 4 processes
python pipeline/cards_sheet.py <sheet.jpg> <dir-or-pngs...>       # contact sheet with zone outlines
```

- **Output.** 1920×1080, 30 fps, opaque h264, crf 16, limited-range BT.709 `yuv420p`. Length is exactly `round(dur × 30)` frames. The file is `<spec dir>/<id>.mp4`, which matches `graphics/cards/<id>.mp4` in `timeline-schema.md`.
- **`--episode`.** Renders every `graphics/cards/*.json` whose MP4 is missing or older than the spec. `--force` re-renders all of them.
- **`--png`.** Also saves a still taken 0.4 s after the last entrance ends. `still_at` in the spec overrides that time.
- **Zone check.** During every render the page checks its content against the reserved zones (§3). Violations print as `ZONE host box: pin "WASHINGTON" [x,y -> x,y]`. Fix them before delivery, usually by moving the view, changing the pin `side` or shortening the copy.
- **Warnings.** These print as `WARN`:
  - list items over 60 characters
  - an `at` too close to the end of the card
  - copy that still overflows after auto-fit
  - a highlight phrase not found in the document body
- **Determinism.** All motion is a pure function of time: `card.js` defines `window.seek(t)`, which `render_html.py` calls for every frame. There are no CSS animations or transitions, so re-renders are frame-identical.
- **Preview.** Opening `cards/<type>.html?spec=<file URI of a spec.js>` in Chrome plays the card in real time. `make_card.py` writes that `spec.js` itself, as `window.CARD = {...resolved spec}`. You can also use `?json=<urlencoded spec>` or inject `window.CARD`.
- **Assets.** Relative paths (`bg_image`, `base.image`, `base.video`, `geojson`) resolve against the spec's folder, then the carver root, then the cwd.

## 2. Common fields (every type)

| field | type | default | meaning |
|---|---|---|---|
| `id` | string | required | Output name: `<id>.mp4`. |
| `type` | string | required | `map \| stat \| chart \| timeline \| list \| split \| document` |
| `dur` | seconds | required | Exact length, 0.5–120 s. |
| `strap_clear` | bool | `false` | Keeps x < 1320, y > 820 free for a headline strap. Content is auto-fitted above y 800; map legends move under the title block. |
| `at` | seconds | per element | When an element starts entering. Every element accepts one. Without it, elements stagger in by about 0.1 s and have all entered by 1.8 s. |
| `bg_image` | path | — | Non-map cards: a blurred, darkened footage still with a slow push. The default background is animated navy (drifting radar grid and a slow sweep). |
| `title` | object | — | `{"kicker", "h2", "sub", "at"}`. This is the frame M title block at x 60, y 132. `h2` takes `\n` line breaks and `*word*` for amber emphasis. |
| `still_at` | seconds | auto | Time of the `--png` still. |
| `crf` | int | 16 | h264 quality. |

**Colours.** Wherever a colour is accepted, use a palette name, a semantic name or a hex value:
- palette names: `crimson`, `amber`, `sky`, `royal`, `steel`, `white`, `paper`, `navy`, `navy2`
- semantic names: `warning`, `severe`, `high`, `major` = crimson · `watch`, `elevated`, `moderate`, `minor` = amber · `advisory`, `info`, `low` = sky · `none`, `neutral` = steel
- `#hex`

**Text.** `*word*` gives amber emphasis in titles, labels and list items. Plain text is escaped, so HTML is not interpreted.

## 3. Reserved zones and motion rules (enforced by the templates)

**Reserved zones:**
- Host box: x ≥ 1130, y ≤ 475. The window was 720×405 from 4 Nov; since 6 Nov main is 640×360 at x 1240, which leaves room to spare. The title block's `max-width` is 1040.
  - Since 6 Nov the window comes and goes, and it is OFF for each card's first 5 s.
  - When it appears over a card, it is always top right: main or a smaller look, all inside this zone.
  - So keep this zone clear exactly as before (`pipeline/host_box.py`).
- Bug: x ≤ 420, y ≤ 120. Titles start at y 132.
- Ticker: y ≥ 1014. Content ends by y 1000.
- Strap (`strap_clear: true` only): x < 1320, y > 820.
- Legends sit bottom left at y ≈ 944–984, as in frame M.

**Motion:**
- **Entrances.** `cubic-bezier(.2,.8,.2,1)`, 0.45–0.6 s, staggered 80–120 ms. They are rises, slides, left-to-right wipes and stroke draws.
- **No bounces.** There is no overshoot and no letter-by-letter text. The one exception is the big stat count-up, which keeps a fixed width so the unit never shifts.
- **Continuous motion:**
  - map Ken Burns
  - grid drift and radar sweep
  - blurred-still push
  - document panel push
  - pin radar ping
  - marching dashes on map arrows
- **No exit animation.** The compositor cuts or wipes.

## 4. `map`

| field | meaning |
|---|---|
| `base` | `{"image": "path"}` (default `brand-kit/src/goes_conus.jpg`) or `{"video": "loop.mp4"}`. A video base renders the overlay as a ProRes 4444 alpha MOV and composites it over the loop with ffmpeg. The loop repeats to fill `dur`. Video bases get no Ken Burns. |
| `projection` | `{"type": "goes_conus"}`: the NOAA STAR GOES-19 CONUS product, any resolution of the 2500×1500 grid, same maths as `goes_px.py`.<br>`{"type": "linear", "bbox": [lon_min, lat_min, lon_max, lat_max]}`: equirectangular, for NASA GIBS WMS EPSG:4326 images.<br>`{"type": "mercator", "bbox": [...]}`: Web Mercator.<br>The bbox is the extent of the whole image. |
| `view` | The part of the image to show, expanded to 16:9 and kept inside the image:<br>`{"crop": [x0, y0, x1, y1]}`: GOES in 2500×1500 product px, other projections in image px.<br>`{"bbox": [lon_min, lat_min, lon_max, lat_max], "pad": 0.04}`<br>Default: frame M's crop `[700, 50, 2100, 837.5]` for GOES, the whole image otherwise. |
| `zoom` | `[1.0, 1.06]`: Ken Burns scale from start to end, linear over `dur`. |
| `focus` | `[lat, lon]`: the point the push zooms toward. Default: the frame centre. |
| `dim` | 0–1: darkens the base under the overlays. |
| `gradient` | `false` drops frame M's left and bottom legibility gradients. |
| `states` | `true` or `{"color", "opacity": .38, "width": 1.4, "at"}`: US state outlines from `brand-kit/geo/us-states-lines.geojson`. Each border is drawn once. GOES GeoColor already has state lines; use this on GIBS or plain bases. |
| `pins[]` | `{"name", "lat", "lon", "at", "side": "auto\|left\|right", "color": "crimson", "pulse": true}`. The dot pops, the label wipes in, then the dot pings slowly. `side: auto` flips the label left when it would hit the host zone or the frame edge. |
| `polygons[]` | `{"states": ["TN", "Kentucky"]}` and/or `{"geojson": "file.geojson" or inline object}` and/or `{"geometry": {...}}`.<br>Plus: `"kind": "warning\|watch\|info"` or `"color"`, `"fill_opacity": 0.35`, `"width": 3.5`, `"draw": 1.0`, `"at"`, `"label"`, `"label_at": [lat, lon]`.<br>The stroke draws in, then the fill fades to 30–40 %. The label goes at `label_at` or the bbox centre. |
| `arrows[]` | `{"latlon": [[lat, lon], ...]}` (or `"lonlat"` in GeoJSON order), `"color": "white"`, `"width": 7`, `"dash": "20 13"` (`false` = solid), `"draw": 1.4`, `"at"`, `"smooth": true`, `"march": true`, `"speed": 26`, `"head": true`, `"label"`, `"label_pos": .5`.<br>The path draws along a smoothed curve with the arrowhead riding the tip. The dashes then flow toward the head. |
| `legend[]` | `{"label", "color"}`: bottom left as in frame M. With `strap_clear` it goes under the title block. |
| `stat` | `{"label", "value", "unit", "prefix", "sub", "decimals", "at", "right": 60, "bottom": 100, "count_dur": 1.1}`: the frame M stat box with a count-up. |

All overlays are SVG/HTML in the same projected pixel space as the base, inside the zoomed layer, so they stay locked to it. The base is "Ken Burns"-zoomed; overlays are in a second layer with the identical transform.

```json
{
  "id": "storm_map", "type": "map", "dur": 8, "strap_clear": false,
  "base": {"image": "../../src/goes_conus.jpg"},
  "projection": {"type": "goes_conus"},
  "view": {"crop": [730, 0, 2130, 787.5]},
  "zoom": [1.0, 1.06], "focus": [36.2, -88.0],
  "states": {"opacity": 0.22, "width": 1.2},
  "title": {"kicker": "WHERE IT GOES NEXT", "h2": "One storm,\n30 states", "sub": "GOES-19 satellite · 10:51 AM ET Wednesday"},
  "polygons": [
    {"states": ["TN", "KY"], "kind": "watch", "fill_opacity": 0.32, "at": 0.9, "label": "FLOOD WATCH", "label_at": [36.75, -84.6]},
    {"states": ["OK"], "kind": "warning", "fill_opacity": 0.34, "at": 1.1}
  ],
  "arrows": [{"latlon": [[35.2, -95.6], [37.2, -91.6], [38.9, -87.4], [39.7, -83.2], [39.9, -79.6]], "color": "white", "at": 1.2, "draw": 1.6}],
  "pins": [
    {"name": "Dallas", "lat": 32.78, "lon": -96.80, "at": 0.5},
    {"name": "Oklahoma City", "lat": 35.47, "lon": -97.52, "at": 0.6},
    {"name": "Kansas City", "lat": 39.10, "lon": -94.58, "at": 0.7},
    {"name": "Nashville", "lat": 36.16, "lon": -86.78, "at": 0.8},
    {"name": "Washington", "lat": 38.90, "lon": -77.04, "at": 0.9}
  ],
  "legend": [{"label": "Severe storms", "color": "crimson"}, {"label": "Flood watch", "color": "amber"}, {"label": "Storm track", "color": "white"}],
  "stat": {"label": "STATES UNDER ALERTS", "value": 30, "unit": "+", "sub": "from the Plains to the I-95 corridor", "at": 1.0}
}
```

GIBS example (equirectangular WMS, `BBOX=-100,24,-70,42` requested at 3000×1800):

```json
{"id": "gibs_map", "type": "map", "dur": 7,
 "base": {"image": "gibs_modis_truecolor.jpg"},
 "projection": {"type": "linear", "bbox": [-100, 24, -70, 42]},
 "view": {"bbox": [-92, 26, -74, 38]}, "states": true,
 "pins": [{"name": "Miami", "lat": 25.76, "lon": -80.19}]}
```

Radar loop example. The overlay is composited over the loop, whose frames must be in the stated projection:

```json
{"id": "radar_map", "type": "map", "dur": 10,
 "base": {"video": "../../clips/radar_loop.mp4"},
 "projection": {"type": "mercator", "bbox": [-88, 24, -78, 31]},
 "pins": [{"name": "Tampa", "lat": 27.95, "lon": -82.46}],
 "legend": [{"label": "Heavy rain", "color": "sky"}]}
```

## 5. `stat`

| field | meaning |
|---|---|
| `kicker` | Crimson chip at x 60, y 132. |
| `value` | Number or string. Write it as a string to keep decimals: `"2.54"` counts 0.00 → 2.54. |
| `decimals`, `prefix`, `unit` | `unit` is shown in amber (`FT`, `IN`, `MPH`, `%`, `+`). |
| `label` | Big uppercase line under the number. |
| `context` | One sentence of context. |
| `at` | Count-up start. |
| `count_dur` | Count-up length, default 1.4 s. |
| `bars` | Optional comparison: `{"title", "unit", "max", "at", "stagger": .45, "decimals", "items": [{"label", "sub", "value", "highlight": true, "at"}]}`. The bars grow in sequence and their values count with them. `highlight` = crimson; the others are studio blue. `max` sets the full-width value. |
| `bg_image` | Optional blurred still; the default is animated navy. |

Everything auto-fits: with `strap_clear` the whole block shrinks to end above y 800.

```json
{
  "id": "tide_stat", "type": "stat", "dur": 8, "kicker": "VIRGINIA KEY, FL",
  "value": "2.54", "unit": "FT", "label": "Above normal high tide",
  "context": "Tuesday's reading at the Virginia Key tide gauge. Only two storms on record went higher.",
  "at": 0.3, "count_dur": 1.4,
  "bars": {"title": "HOW IT COMPARES · FEET ABOVE NORMAL HIGH TIDE", "unit": "FT", "max": 4.0, "at": 1.5, "stagger": 0.45,
    "items": [
      {"label": "Wilma", "sub": "October 2005", "value": "2.54"},
      {"label": "Irma", "sub": "September 2017", "value": "3.56"},
      {"label": "Tuesday", "sub": "November 3, 2026", "value": "2.54", "highlight": true}
    ]}
}
```

## 6. `chart`

| field | meaning |
|---|---|
| `chart` | `line` (default) or `bar`. |
| `x` | **Numeric:** `{"min", "max", "ticks": [{"v", "label"}]}`, used with series `points`. Tick labels take `\n`; the second line is dimmer.<br>**Categories:** `{"labels": ["MON", ...]}`, used with series `values`. |
| `y` | `{"min", "max", "step", "decimals", "unit"}`. All are optional and default to a nice scale. `unit` is printed above the axis. |
| `series[]` | **line:** `{"name", "color", "points": [[x, y], ...]` or `"values": [...]`, `"at": .7, "draw": 2.2, "width": 6, "area": true}`. The line draws left to right with a head dot; the area gradient comes with it.<br>**bar:** `{"values", "color", "highlight": [index...], "highlight_color", "stagger": .12, "ats": [...], "decimals"}`. Bars grow from the baseline in sequence and their values count up. |
| `thresholds[]` | `{"value", "label", "color": "crimson", "at"}`: a dashed line drawn across the plot, with its label chip at the right end (for example `MAJOR FLOOD 2.5 FT`). |
| `annotations[]` | `{"series": 0, "point": "max\|min"` or `"index": -1` (last), `"text", "sub", "side": "auto\|left\|right", "color", "at"}`. An end-point dot and a callout. The default `at` is when the drawing line reaches that point. |
| `source` | The data's name and date as small text under the chart, for example `NOAA Tides & Currents · Virginia Key, FL (8723214) · preliminary data · Nov 3–4, 2026`. This is not an on-screen credit. |
| `plot` | Optional `{"x0": 200, "x1": 1780, "y0": 520, "y1": 870}`. With `strap_clear`, `y1` defaults to 730. |

The plot sits under the host box: y ≥ 520 and the full width.

```json
{
  "id": "gauge_chart", "type": "chart", "dur": 9, "chart": "line",
  "title": {"kicker": "VIRGINIA KEY TIDE GAUGE", "h2": "Two days of *rising water*", "sub": "Water level, feet above normal high tide"},
  "x": {"min": 0, "max": 48, "ticks": [{"v": 0, "label": "MON\n12 AM"}, {"v": 12, "label": "NOON"}, {"v": 24, "label": "TUE\n12 AM"}, {"v": 36, "label": "NOON"}, {"v": 48, "label": "WED\n12 AM"}]},
  "y": {"min": -1, "max": 3, "step": 1, "unit": "FT", "decimals": 0},
  "series": [{"name": "Observed", "color": "sky", "at": 0.7, "draw": 2.6,
    "points": [[0, 0.9], [3, -0.2], [6, -0.6], [9, 0.4], [12, 1.4], [15, 0.6], [18, -0.3], [21, 0.5], [24, 1.6], [27, 1.2], [30, 0.2], [33, 1.6], [35.33, 2.54], [38, 1.7], [40, 0.9]]}],
  "thresholds": [{"value": 2.5, "label": "MAJOR FLOOD 2.5 FT", "color": "crimson", "at": 0.6},
                 {"value": 1.5, "label": "MINOR FLOOD 1.5 FT", "color": "amber", "at": 0.7}],
  "annotations": [{"series": 0, "point": "max", "text": "2.54 FT", "sub": "Tue 11:20 AM · highest since Irma", "side": "left"}],
  "source": "NOAA Tides & Currents · Virginia Key, FL (8723214) · preliminary data · Nov 3–4, 2026"
}
```

Bar variant: `"chart": "bar", "x": {"labels": ["MON", "TUE", "WED"]}, "series": [{"values": [1.2, 3.4, 0.8], "highlight": [1]}]`.

## 7. `timeline`

`windows[]` holds `{"day", "date", "time", "threat", "level"` (or `"color"`), `"detail", "confidence", "at"}`:
- `level` follows the semantic colours: `high` crimson, `elevated` amber, `info`/`low` sky, `none` steel.
- Text on amber and sky threat chips is navy, for contrast.

The chips sit in one row on a rail that draws in. Each chip and its node reveal at `at`. The row auto-fits; up to 6 windows read well.

```json
{
  "id": "week_timeline", "type": "timeline", "dur": 7,
  "title": {"kicker": "THE WEEK AHEAD", "h2": "Your window, day by day", "sub": "Eastern time · confidence from the NWS Storm Prediction Center"},
  "windows": [
    {"day": "MON", "date": "NOV 3", "time": "2 PM – 10 PM", "threat": "Severe storms", "level": "high", "detail": "Dallas, Oklahoma City, Kansas City", "confidence": "high", "at": 0.7},
    {"day": "TUE", "date": "NOV 4", "time": "Overnight", "threat": "Flash flooding", "level": "elevated", "detail": "Ozarks to the Ohio Valley", "confidence": "medium", "at": 1.5},
    {"day": "WED", "date": "NOV 5", "time": "Noon – midnight", "threat": "Severe storms", "level": "high", "detail": "Tennessee and Ohio valleys", "confidence": "medium", "at": 2.3},
    {"day": "THU", "date": "NOV 6", "time": "6 AM – 8 PM", "threat": "Heavy rain", "level": "info", "detail": "I-95 from Richmond to Boston", "confidence": "high", "at": 3.1},
    {"day": "FRI", "date": "NOV 7", "time": "Morning", "threat": "Windy, clearing", "level": "none", "detail": "Gusts to 40 mph on the coast", "confidence": "low", "at": 3.9}
  ]
}
```

## 8. `list`

- `items[]` holds strings or `{"text", "at"}`. Keep each item to 60 characters or fewer; `make_card` warns above that.
- Each item slides in at its `at`. When a later item arrives, the earlier ones dim to `1 - dim` (default `dim` 0.45) and their number boxes turn navy.
- `title` defaults to `{"kicker": "WHAT TO DO"}`.

```json
{
  "id": "what_to_do", "type": "list", "dur": 8.5, "bg_image": "../../src/foot_N08_Town_streets_flooded_dusk.jpg",
  "title": {"kicker": "WHAT TO DO", "h2": "Before Wednesday's high tide"},
  "items": [
    {"text": "Move your car to a garage or higher ground by 10 AM", "at": 0.8},
    {"text": "Never drive through salt water: it ruins brakes and wiring", "at": 2.2},
    {"text": "Put sandbags at garage doors and low entryways tonight", "at": 3.6},
    {"text": "Photograph any damage before you clean up, for insurance", "at": 5.0},
    {"text": "Next high tide: 11:20 AM Wednesday at Virginia Key", "at": 6.4}
  ]
}
```

## 9. `split`

`left` and `right` are each `{"head", "icon": "check|question", "color", "at", "items": [{"text", "at"}]}`:
- Defaults: left = `WHAT'S CERTAIN`, check icon, sky; right = `WHAT ISN'T`, question icon, amber.
- The columns sit under the host box (y ≥ 500) with a divider that draws down.
- Items slide in at their `at`.

```json
{
  "id": "certain_uncertain", "type": "split", "dur": 8,
  "title": {"kicker": "THE STRAIGHT ANSWER", "h2": "What we know, what we don't"},
  "left": {"head": "WHAT'S CERTAIN", "items": [
    {"text": "Wednesday's high tide arrives at 11:20 AM", "at": 0.9},
    {"text": "The coastal flood warning runs until 8 PM Wednesday", "at": 1.6},
    {"text": "Low streets in Miami Beach will flood again", "at": 2.3}]},
  "right": {"head": "WHAT ISN'T", "items": [
    {"text": "How much extra water the onshore wind adds", "at": 3.4},
    {"text": "Whether Wednesday beats Tuesday's 2.54 ft", "at": 4.1},
    {"text": "If the warning is extended into Thursday. Next NWS update: 4 PM ET", "at": 4.8}]}
}
```

## 10. `document`

| field | meaning |
|---|---|
| `kicker` | Optional crimson chip above the panel. |
| `agency`, `product`, `issued` | Panel header. The product is in big navy capitals; the issue line is monospace. |
| `body` | Statement text, verbatim. Whitespace and line breaks are kept, and it is set in monospace (Consolas). |
| `highlights[]` | `{"phrase", "at", "dur", "color"}`. The first match of the phrase is found in `body`, exact first and then case-insensitive. An amber highlighter sweeps it line by line in reading order. |
| `stamp` | Optional outlined tag, top right, for example `SAMPLE` or `PRELIMINARY`. |
| `push` | Slow panel push, default 1.025. |
| `at` | Panel entrance, default 0.25. |

The panel auto-fits above the ticker, or above y 800 with `strap_clear`.

```json
{
  "id": "nws_chm", "type": "document", "dur": 7, "kicker": "THE OFFICIAL WORD",
  "agency": "NATIONAL WEATHER SERVICE MIAMI FL", "product": "Coastal Hazard Message", "issued": "412 AM EST Wed Nov 4 2026",
  "body": "...COASTAL FLOOD WARNING REMAINS IN EFFECT UNTIL 8 PM EST THIS EVENING...\n\n* WHAT...Up to 2 feet of saltwater flooding above ground level in low-lying areas near the coast, bays and canals.\n\n* WHERE...Coastal Miami-Dade, Broward and Palm Beach counties.\n\n* WHEN...Until 8 PM EST this evening, especially around the times of high tide.\n\n* IMPACTS...Flooding of roads, parking lots, parks and lawns. Some water may enter homes and businesses.",
  "highlights": [{"phrase": "Up to 2 feet of saltwater flooding above ground level", "at": 1.6},
                 {"phrase": "Some water may enter homes and businesses", "at": 3.6}]
}
```

## 11. Files

**Templates** (`pipeline/cards/`):
- `card.js`: runtime. Includes the timeline, entrances, count-up, auto-fit, backgrounds, projections and zone check.
- `card.css`: component styles.
- `map.html`, `stat.html`, `chart.html`, `timeline.html`, `list.html`, `split.html`, `document.html`

**Pipeline:**
- `pipeline/make_card.py`: spec → MP4. Handles validation, asset resolution, the view rectangle, GeoJSON inlining, video compositing and episode mode.
- `pipeline/render_html.py`: HTML → PNG/MOV/MP4. Its CLI is backward compatible. Added options:
  - `--at`: still time
  - `--clip x,y,w,h`
  - `--crf`
  - `--jpeg`: faster opaque frames
- `pipeline/topo2geo.py`: rebuilds `brand-kit/geo/us-states*.geojson` from the IWN `us-states-10m.json` TopoJSON (read only).
- `pipeline/cards_sheet.py`: contact sheet with zone outlines.
