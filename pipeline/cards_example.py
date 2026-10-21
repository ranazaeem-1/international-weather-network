"""EXAMPLE of an episode's project/cards.py: every card type, modelled on the user's Outer Banks video (20 Oct 2026).
Copy to project/cards.py and replace everything. Do not copy these numbers into a real episode: every number, place,
track and flood area on a card must come from that episode's research/facts.csv (list the ids in "facts").

Common keys: id (unique), type, chapter (S01..; never S00), facts, pill (red label; default per type), headline, sub
(boxed line under the headline), sub_at (seconds, default 1.6), source (small grey line), seconds (6-8, default 7),
at (seconds from the chapter start; default: first spot after the lower-third that fits under the narration).
Map keys: view [lon_min, lat_min, lon_max, lat_max] (default: fitted to the content), zoom (slow push-in, default 0.05),
focus (point the zoom heads for), low / lows, pins, route, track, lines, arrows, areas, tags.
Points: [lat, lon] or a Natural Earth place name, e.g. "Norfolk|Virginia" (name|region picks between same-name places).
Pins: "Place name" | [label, lat, lon(, side)] | {"label", "lat", "lon" or "place", "value", "side": left/right, "color"}.
Colours: red, amber, orange, yellow, blue, white, grey, green, purple or "#rrggbb".
"""

INTRO = {"headline": "NOR'EASTER HAMMERS THE OUTER BANKS", "date": "20 OCT 2026"}   # optional: "network", "kicker", "lang"

CARDS = [
    # storm / track map: spinning red L, city pins popping in
    {"id": "storm_zone", "type": "storm_map", "chapter": "S01", "facts": ["F01"], "headline": "Nor'easter off the Outer Banks",
     "source": "Storm position: WITN, early Tue 20 Oct", "view": [-93, 27, -60, 47],
     "low": [35.0, -73.6, "STORM CENTER"],                       # [lat, lon, label(, "L" or "H")]
     "pins": [["Outer Banks, NC", 35.56, -75.47], "Norfolk|Virginia", ["Ocean City, MD", 38.34, -75.08], "Atlantic City"]},

    # local closure map: the route is drawn on in red
    {"id": "hwy12", "type": "closure_map", "chapter": "S03", "facts": ["F05"], "pill": "OUTER BANKS",
     "headline": "Highway 12 closed", "sub": "Ocean broke through about 1,000 ft of dune",
     "source": "Source: NCDOT, 9 a.m. Tue 20 Oct", "view": [-76.3, 35.15, -75.1, 35.95],
     "route": [[35.80, -75.546], [35.72, -75.497], [35.60, -75.468]],
     "pins": [["Basnight Bridge", 35.80, -75.546], ["Rodanthe", 35.60, -75.468]],
     "tags": [["CLOSED", 35.70, -75.38]]},                      # [text, lat, lon(, colour)]

    # by the numbers: "value" + "label" + "detail", or "stats": [up to 3 of them]. Units after the number are drawn smaller
    {"id": "houses", "type": "stat", "chapter": "S05", "facts": ["F09"], "value": "32", "label": "Houses collapsed since 2020",
     "detail": "on Cape Hatteras National Seashore beaches", "source": "Source: National Park Service"},

    # timeline: 2-6 events, the last one is red; "\n" breaks the description
    {"id": "timeline", "type": "timeline", "chapter": "S06", "facts": ["F10", "F11"], "headline": "Two nor'easters in a month",
     "source": "Sources: NWS, NCDOT", "events": [{"date": "Sep 23-27", "text": "First nor'easter\nNC 12 damaged"},
                                                {"date": "Oct 3", "text": "NC 12\nreopens"}, {"date": "Oct 19", "text": "NC 12 closed\nagain"}]},

    # explainer map: low + wind arrows ([[from lat, lon], [to lat, lon]])
    {"id": "explainer", "type": "explainer_map", "chapter": "S07", "facts": ["H01"], "headline": "What is a nor'easter?",
     "sub": "Winds from the northeast pile ocean water against the coast", "source": "Source: National Weather Service",
     "view": [-93, 27, -60, 47], "low": [34.6, -71.2, "LOW PRESSURE"],
     "arrows": [[[38.9, -73.4], [37.7, -74.6]], [[36.9, -72.9], [35.6, -74.6]]]},

    # official alert: title + 1-5 bullets + issuer line
    {"id": "nws_alert", "type": "alert", "chapter": "S08", "facts": ["F12"], "title": "Coastal Flood Warning",
     "bullets": ["Hatteras and Ocracoke islands", "2 to 4 ft of water in low-lying areas", "Until 8 p.m. Wednesday, Oct 21"],
     "issuer": "National Weather Service Newport/Morehead City, 9:48 a.m. Tue 20 Oct"},

    # forecast map: must say forecast/outlook; coloured coast line, pins with values, tags
    {"id": "tide", "type": "forecast_map", "chapter": "S09", "facts": ["F13"], "pill": "TIDE FORECAST",
     "headline": "Wednesday evening high tide", "source": "Forecast peaks: NWS Wakefield and Mount Holly, Tue 20 Oct",
     "view": [-79.5, 36.3, -71.5, 41.2],
     "lines": [{"points": [[36.85, -75.98], [38.3, -75.1], [39.36, -74.42]], "color": "amber", "width": 8}],
     "pins": [{"label": "Norfolk", "lat": 36.85, "lon": -76.29, "value": "5.1 ft"},
              {"label": "Atlantic City", "lat": 39.36, "lon": -74.42, "value": "6.6 ft", "side": "right"}],
     "tags": [["MINOR FLOODING", 37.9, -73.2, "amber"]]},

    # outlook / track map: low + forecast track (red line with an arrow); only an official track
    {"id": "nhc", "type": "track_map", "chapter": "S10", "facts": ["F14"], "headline": "Could it become Josephine?",
     "sub": "NHC outlook: 40% chance of briefly turning subtropical", "source": "Source: National Hurricane Center",
     "view": [-93, 27, -60, 47], "low": [34.2, -73.6, "NON-TROPICAL LOW"], "track": [[35.3, -72.6], [37.6, -69.5]]},

    # flood map: polygons from a GeoJSON (Copernicus EMS delineation, NOAA...) on our map, or "image": a map picture
    # (optional "crop": [x, y, w, h] fractions). Log the source in research/sources.csv
    {"id": "flood_extent", "type": "flood_map", "chapter": "S11", "facts": ["F15"], "headline": "Where the water went",
     "source": "Source: Copernicus EMS EMSR000", "geojson": "research/flood_extent.geojson", "pins": ["Rodanthe"]},

    # satellite: an mp4 loop (NOAA STAR GOES, NASA Worldview, RAMMB); "speed" < 1 slows it, "start" skips seconds
    {"id": "sat", "type": "satellite", "chapter": "S12", "facts": ["F16"], "headline": "The storm from space",
     "sub": "GOES-19 GeoColor loop", "source": "Source: NOAA / NESDIS STAR", "video": "clips/satellite/goes19_ne.mp4",
     "speed": 0.6},

    # any other map ("map"): same layers, e.g. observed rain totals; set "pill"
]
