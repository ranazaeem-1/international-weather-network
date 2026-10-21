"""IWN animated info cards (user, 21 Oct 2026): 6-9 per video, 6-8 s each, every card different, none in the cold open.

Reads CARDS from the episode's project/cards.py, writes graphics/cards/<id>.mp4 (full-frame, opaque; build_capcut.py
fades it in/out with CapCut alpha keyframes) and graphics/cards/<id>.png (a still for review).

Card types (pill = the red category label top-left; every type takes pill / headline / sub / source / seconds):
  storm_map     STORM ZONE: spinning red "L" (low), city pins popping in, optional track line
  closure_map   local map: a red route drawn on (e.g. Highway 12) with pins and a CLOSED tag
  forecast_map  TIDE / RAIN FORECAST: coloured coast segments or areas, pins with values, tags
  explainer_map EXPLAINER: low + wind arrows
  track_map     NHC OUTLOOK: low + forecast track
  stat          BY THE NUMBERS: 1-3 big numbers that count up, label + detail
  timeline      TIMELINE: 2-6 dated events on a line, the last one in red
  alert         NWS ALERT: red header with the warning name + bullets
  flood_map     FLOOD MAP: polygons from a GeoJSON file on our map, or a supplied image (Copernicus EMS etc.)
  satellite     SATELLITE: a supplied mp4 (NASA / NOAA / RAMMB loop) with the card chrome on top

Maps use Natural Earth 1:10m (public domain), bundled in pipeline/geo/natural_earth_10m.npz: no network, no API.

Usage (from the episode's project/ folder):
    python make_cards.py                 # all cards (4 in parallel)
    python make_cards.py storm_zone stat # only these ids
    python make_cards.py --stills        # review stills only (fast)
    python make_cards.py --contact       # also graphics/cards/_contact.png with every still
"""
import argparse, csv, json, math, re, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image

import iwn_gfx as G

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
from iwn_gfx import W, H, FPS, Sprite, paste, ease_out, ease_in_out, back_out

SAFE_Y = G.SAFE_BOTTOM - 20   # map labels stay above the headline ticker
SB = 1.2              # base map resolution relative to the frame (room for the slow zoom)
TYPES = {
    "storm_map": "STORM ZONE", "closure_map": "ROAD CLOSED", "forecast_map": "FORECAST", "explainer_map": "EXPLAINER",
    "track_map": "NHC OUTLOOK", "stat": "BY THE NUMBERS", "timeline": "TIMELINE", "alert": "NWS ALERT",
    "flood_map": "FLOOD MAP", "satellite": "SATELLITE", "map": "MAP",
}
MAP_TYPES = {"map", "storm_map", "closure_map", "forecast_map", "explainer_map", "track_map", "flood_map"}


# ---- geography ------------------------------------------------------------------------------------------------------
_GEO = {}
def geo(layer):
    if not _GEO:
        z = np.load(G.geo_file())
        for k in ("land", "lakes", "borders", "states"):
            xy = z[k + "_xy"].astype(np.float64) / 1000.0
            off = z[k + "_off"]
            starts = off[:-1]
            mn = np.minimum.reduceat(xy, starts, axis=0)
            mx = np.maximum.reduceat(xy, starts, axis=0)
            _GEO[k] = (xy, off, mn, mx)
        _GEO["places"] = json.loads(str(z["places"]))
    return _GEO[layer]


def merc(lon, lat):
    lat = np.clip(np.asarray(lat, np.float64), -85, 85)
    return np.asarray(lon, np.float64), np.degrees(np.log(np.tan(np.pi / 4 + np.radians(lat) / 2)))


def inv_merc_lat(y):
    return np.degrees(2 * np.arctan(np.exp(np.radians(y))) - np.pi / 2)


def place(spec):
    """'Norfolk' or 'Norfolk|Virginia' -> (lat, lon) of the most populous Natural Earth place with that name."""
    name, _, region = spec.partition("|")
    rows = [r for r in geo("places") if r[0].lower() == name.strip().lower()
            and (not region or region.strip().lower() in (r[1] + " " + r[2]).lower())]
    if not rows:
        raise SystemExit(f"place '{spec}' not in Natural Earth places: give it as [label, lat, lon]")
    r = max(rows, key=lambda r: r[5])
    print(f"  place {spec!r} -> {r[0]}, {r[1]}, {r[2]} ({r[3]:.3f}, {r[4]:.3f})")
    return r[3], r[4]


def point(p):
    """[lat, lon] | {'lat','lon'} | 'Place name' -> (lat, lon)."""
    if isinstance(p, str):
        return place(p)
    if isinstance(p, dict):
        return place(p["place"]) if "place" in p else (p["lat"], p["lon"])
    return float(p[0]), float(p[1])


class MapView:
    """Mercator view fitted to 1920x1080. view = [lon_min, lat_min, lon_max, lat_max]."""
    def __init__(self, view):
        lon0, lat0, lon1, lat1 = view
        x0, y0 = merc(lon0, lat0)
        x1, y1 = merc(lon1, lat1)
        w, h = float(x1 - x0), float(y1 - y0)
        if w / h < W / H:
            w = h * W / H
        else:
            h = w * H / W
        self.cx, self.cy, self.s = float(x0 + x1) / 2, float(y0 + y1) / 2, W / w
        self.lon = (self.cx - w / 2, self.cx + w / 2)
        self.lat = (float(inv_merc_lat(self.cy - h / 2)), float(inv_merc_lat(self.cy + h / 2)))

    def xy(self, lat, lon):
        x, y = merc(lon, lat)
        return W / 2 + (x - self.cx) * self.s, H / 2 - (y - self.cy) * self.s

    def base(self):
        """Land / lakes / borders / state lines at SB x the frame size (drawn at 2x, scaled down once)."""
        k = 2 * SB
        im = Image.new("RGB", (round(W * k), round(H * k)), G.OCEAN)
        from PIL import ImageDraw
        d = ImageDraw.Draw(im)
        pad_lon = (self.lon[1] - self.lon[0]) * 0.05
        pad_lat = (self.lat[1] - self.lat[0]) * 0.05
        min_px = 1.2 / (self.s * k)

        def rings(layer):
            xy, off, mn, mx = geo(layer)
            sel = np.where((mx[:, 0] >= self.lon[0] - pad_lon) & (mn[:, 0] <= self.lon[1] + pad_lon) &
                           (mx[:, 1] >= self.lat[0] - pad_lat) & (mn[:, 1] <= self.lat[1] + pad_lat) &
                           (np.maximum(mx[:, 0] - mn[:, 0], mx[:, 1] - mn[:, 1]) > min_px))[0]
            for i in sel:
                r = xy[off[i]:off[i + 1]]
                X, Y = self.xy(r[:, 1], r[:, 0])
                yield list(zip((X * k).tolist(), (Y * k).tolist()))

        for r in rings("land"):
            if len(r) > 2:
                d.polygon(r, fill=G.LAND, outline=G.LAND_EDGE)
        for r in rings("lakes"):
            if len(r) > 2:
                d.polygon(r, fill=G.OCEAN, outline=G.LAND_EDGE)
        for r in rings("states"):
            d.line(r, fill=G.STATE, width=max(2, round(1.1 * k)))
        for r in rings("borders"):
            d.line(r, fill=G.BORDER, width=max(2, round(1.6 * k)))
        return im.resize((round(W * SB), round(H * SB)), Image.LANCZOS)


# ---- map sprites ------------------------------------------------------------------------------------------------------
def color(c, default=G.RED):
    if c is None:
        return default
    if isinstance(c, str):
        if c.startswith("#"):
            return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
        return G.COLORS[c]
    return tuple(c)


def label_pill(text, size=26, fill=(17, 20, 25), fg=G.WH, a=228, kind="semibold"):
    w, h = G.text_w(text, size, kind) + 28, size * 1.75
    s = Sprite(w + 2, h + 2)
    s.rect(0, 0, w, h, fill, 6, a=a)
    s.text(14, h / 2 + size * 0.36, size, text, fg, kind)
    return s.img


def pin_sprite(c=G.RED):
    s = Sprite(48, 48, 24, 24)
    s.circle(24, 24, 20, c, a=60)
    s.circle(24, 24, 13, (17, 20, 25), a=235)
    s.circle(24, 24, 9.5, c)
    return s.img


def low_sprites(letter="L", c=G.RED):
    """(disc with letter, rotating arrows) for a low ('L') or high ('H')."""
    R0 = 62
    disc = Sprite(2 * R0 + 8, 2 * R0 + 8, R0 + 4, R0 + 4)
    disc.circle(R0 + 4, R0 + 4, R0, c)
    disc.text(R0 + 4, R0 + 4 + 2, 82, letter, G.WH, "bold", anchor="mm")
    RA, S = 96, 230
    arr = Sprite(S, S, S / 2, S / 2)
    cx = cy = S / 2
    for a0 in (200, 20):                                     # two arcs with heads, like the reference
        arr.arc(cx, cy, RA, a0, a0 + 115, G.WH, 5)
        a = math.radians(a0)                                # head at the start of the arc, pointing backwards (CCW flow)
        hx, hy = cx + RA * math.cos(a), cy + RA * math.sin(a)
        tx, ty = -math.sin(a), math.cos(a)                  # tangent (direction of increasing angle on screen)
        nx, ny = math.cos(a), math.sin(a)
        tip = (hx - tx * 16, hy - ty * 16)
        arr.polygon([tip, (hx + tx * 6 + nx * 11, hy + ty * 6 + ny * 11), (hx + tx * 6 - nx * 11, hy + ty * 6 - ny * 11)], G.WH)
    return disc.img, arr.img


def arrowhead(sprite, p0, p1, c, size=20):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    tip = (p1[0] + ux * size * 0.4, p1[1] + uy * size * 0.4)
    sprite.polygon([tip, (p1[0] - ux * size + uy * size * 0.6, p1[1] - uy * size - ux * size * 0.6),
                    (p1[0] - ux * size - uy * size * 0.6, p1[1] - uy * size + ux * size * 0.6)], c)


class GeoLine:
    """A line in base-map pixels (zooms with the map), drawn on from t0 over `dur` seconds."""
    def __init__(self, pts, c, width, t0, dur=1.2, arrow=False, casing=True, a=255):
        self.pts = [(x * SB, y * SB) for x, y in pts]
        self.c, self.w, self.t0, self.dur, self.arrow, self.casing, self.a = c, width * SB, t0, dur, arrow, casing, a
        seg = [math.hypot(self.pts[i + 1][0] - self.pts[i][0], self.pts[i + 1][1] - self.pts[i][1]) for i in range(len(self.pts) - 1)]
        self.cum = np.concatenate([[0], np.cumsum(seg)])
        xs, ys = [p[0] for p in self.pts], [p[1] for p in self.pts]
        m = self.w * 2 + 30
        self.x0, self.y0 = min(xs) - m, min(ys) - m
        self.size = (max(xs) - self.x0 + m, max(ys) - self.y0 + m)
        self.full = None

    def _draw(self, frac):
        total = self.cum[-1]
        upto = total * frac
        pts = [self.pts[0]]
        for i in range(1, len(self.pts)):
            if self.cum[i] <= upto:
                pts.append(self.pts[i])
            else:
                f = (upto - self.cum[i - 1]) / max(1e-9, self.cum[i] - self.cum[i - 1])
                p0, p1 = self.pts[i - 1], self.pts[i]
                pts.append((p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f))
                break
        s = Sprite(*self.size)
        loc = [(x - self.x0, y - self.y0) for x, y in pts]
        if len(loc) < 2:
            loc = loc * 2
        if self.casing:
            s.line(loc, (12, 15, 20), self.w + 5 * SB, a=150)
        s.line(loc, self.c, self.w, a=self.a)
        if self.arrow and frac > 0.98 and len(loc) >= 2:
            arrowhead(s, loc[-2], loc[-1], self.c, size=self.w * 2.6)
        return s.img

    def draw(self, canvas, t):
        p = ease_in_out((t - self.t0) / self.dur)
        if p <= 0:
            return
        if p >= 1:
            if self.full is None:
                self.full = self._draw(1.0)
            img = self.full
        else:
            img = self._draw(p)
        canvas.paste(img, (round(self.x0), round(self.y0)), img)


class GeoArea:
    """Filled polygons in base-map pixels (flood extent, warning area), faded in from t0."""
    def __init__(self, polys, c, t0, alpha=0.5, dur=0.9):
        self.t0, self.dur = t0, dur
        allp = [p for poly in polys for p in poly]
        xs, ys = [p[0] * SB for p in allp], [p[1] * SB for p in allp]
        self.x0, self.y0 = int(min(xs)) - 6, int(min(ys)) - 6
        s = Sprite(max(xs) - self.x0 + 6, max(ys) - self.y0 + 6)
        for poly in polys:
            loc = [(x * SB - self.x0, y * SB - self.y0) for x, y in poly]
            if len(loc) > 2:
                s.polygon(loc, c, a=int(255 * alpha))
                s.line(loc + [loc[0]], c, 2.4 * SB, a=235)
        self.img = s.img

    def draw(self, canvas, t):
        a = ease_out((t - self.t0) / self.dur)
        if a > 0:
            img = self.img
            if a < 1:
                img = img.copy()
                img.putalpha(img.getchannel("A").point(lambda v: int(v * a)))
            canvas.paste(img, (self.x0, self.y0), img)


def read_geojson_polys(path):
    d = json.loads(Path(path).read_text(encoding="utf8"))
    feats = d["features"] if d.get("type") == "FeatureCollection" else [d]
    out = []
    for f in feats:
        g = f.get("geometry", f)
        if g["type"] == "Polygon":
            out.append(g["coordinates"][0])
        elif g["type"] == "MultiPolygon":
            out += [p[0] for p in g["coordinates"]]
    return [[(lat, lon) for lon, lat, *_ in ring] for ring in out]


# ---- cards ------------------------------------------------------------------------------------------------------------
def _hit(box, boxes, pad=10):
    x, y, w, h = box
    return any(x < bx + bw + pad and bx - pad < x + w and y < by + bh + pad and by - pad < y + h for bx, by, bw, bh in boxes)


class MapCard:
    def __init__(self, c, ep, avoid=()):
        self.c, self.dur = c, c["_seconds"]
        typ = c["type"]
        lows = c.get("lows") or ([c["low"]] if c.get("low") else [])
        pins = [self._pin(p) for p in c.get("pins", [])]
        lines = list(c.get("lines", []))
        if c.get("route"):
            lines.append({"points": c["route"], "color": c.get("route_color", "red"), "width": 9})
        if c.get("track"):
            lines.append({"points": c["track"], "color": c.get("track_color", "red"), "width": 6, "arrow": True})
        for a in c.get("arrows", []):
            lines.append({"points": a, "color": "yellow", "width": 5, "arrow": True, "casing": False})
        areas = list(c.get("areas", []))
        if c.get("geojson"):
            gp = (ep / c["geojson"]) if not Path(c["geojson"]).is_absolute() else Path(c["geojson"])
            areas.append({"polys": read_geojson_polys(gp), "color": c.get("area_color", "blue"), "alpha": 0.55})
        tags = c.get("tags", [])
        geo_pts = [point(l[:2] if not isinstance(l, dict) else l) for l in lows] + [p["ll"] for p in pins]
        geo_pts += [point(q) for l in lines for q in l["points"]]
        geo_pts += [(la, lo) for a in areas for poly in a.get("polys", []) for la, lo in poly]
        geo_pts += [point(a2) for a in areas for poly in a.get("points", []) for a2 in poly]
        view = c.get("view")
        if not view:
            if not geo_pts:
                raise SystemExit(f"card {c['id']}: a map needs 'view' or something to show")
            la = [p[0] for p in geo_pts]
            lo = [p[1] for p in geo_pts]
            span = max(max(lo) - min(lo), (max(la) - min(la)) * 1.6, c.get("min_span", 1.5))
            cy, cx = (max(la) + min(la)) / 2, (max(lo) + min(lo)) / 2
            # content sits in the right/lower part, leaving the top-left for the headline
            view = [cx - span * 0.95, cy - span * 0.45, cx + span * 0.75, cy + span * 0.42]
        self.mv = MapView(view)
        self.base = self.mv.base()
        T = 0.7
        self.geo = []
        for a in areas:
            polys = a.get("polys") or [[point(q) for q in poly] for poly in a.get("points", [])]
            self.geo.append(GeoArea([[self.mv.xy(la, lo) for la, lo in poly] for poly in polys], color(a.get("color"), G.BLUE),
                                    T, a.get("alpha", 0.45)))
        for l in lines:
            pts = [self.mv.xy(*point(q)) for q in l["points"]]
            self.geo.append(GeoLine(pts, color(l.get("color")), l.get("width", 7), T + 0.1, l.get("dur", 1.3),
                                    l.get("arrow", False), l.get("casing", True), int(255 * l.get("alpha", 1.0))))
        t_pin = T + (0.9 if lines or areas else 0.3)
        self.lows = []
        for k, l in enumerate(lows):
            if isinstance(l, dict):
                ll, lab, letter = point(l), l.get("label"), l.get("letter", "L")
            else:
                ll, lab, letter = (l[0], l[1]), (l[2] if len(l) > 2 else None), (l[3] if len(l) > 3 else "L")
            disc, arr = low_sprites(letter, G.RED if letter == "L" else G.BLUE)
            self.lows.append((self.mv.xy(*ll), disc, arr, label_pill(lab.upper(), 24) if lab else None, 0.5 + 0.2 * k,
                              1 if ll[0] >= 0 else -1, letter))
        self.pins = []
        avoid = list(avoid)
        for q, disc, arr, lab, *_ in self.lows:                  # the low and its label are obstacles too
            avoid.append((q[0] - 100, q[1] - 100, 200, 200))
            if lab:
                avoid.append((q[0] - lab.width / 2, q[1] + 112, lab.width, lab.height))
        for k, p in enumerate(pins):
            x, y = self.mv.xy(*p["ll"])
            lab = label_pill(p["text"]) if p["text"] else None
            side = p.get("side") or ("left" if x > W * 0.45 else "right")
            if lab is not None:
                box = lambda sd: ((x - lab.width - 26) if sd == "left" else (x + 26), y - lab.height / 2, lab.width, lab.height)
                if _hit(box(side), avoid) and not p.get("side"):
                    other = "right" if side == "left" else "left"
                    if not _hit(box(other), avoid):
                        side = other
                if _hit(box(side), avoid) or not (0 <= box(side)[0] and box(side)[0] + lab.width <= W and 0 <= y <= SAFE_Y):
                    print(f"  card {c['id']}: label '{p['text']}' collides with the headline/logo/another label or leaves "
                          f"the frame; widen 'view' or set 'side'")
                avoid.append(box(side))
            avoid.append((x - 14, y - 14, 28, 28))
            self.pins.append(((x, y), pin_sprite(color(p.get("color"))), lab, side, t_pin + 0.22 * k))
        t_tag = t_pin + 0.22 * len(pins) + 0.2
        self.tags = []
        for k, tg in enumerate(tags):
            if isinstance(tg, dict):
                txt, ll, col = tg["text"], point(tg), tg.get("color", "red")
            else:
                txt, ll, col = tg[0], (tg[1], tg[2]), (tg[3] if len(tg) > 3 else "red")
            cc = color(col)
            fg = (40, 26, 6) if col in ("amber", "yellow") else G.WH
            self.tags.append((self.mv.xy(*ll), label_pill(txt.upper(), 22, cc, fg, 255, "bold"), t_tag + 0.2 * k))
        f = c.get("focus")
        self.focus = self.mv.xy(*point(f)) if f else (self.lows[0][0] if self.lows else
                                                       (np.mean([p[0][0] for p in self.pins]), np.mean([p[0][1] for p in self.pins])) if self.pins else (W / 2, H / 2))
        self.zoom = c.get("zoom", 0.05)

    def _pin(self, p):
        if isinstance(p, str):
            name = p.split("|")[0]
            return {"ll": place(p), "text": name}
        if isinstance(p, dict):
            ll = point(p)
            text = p.get("label", p.get("place", "").split("|")[0])
            if p.get("value"):
                text = f"{text} {p['value']}"
            return {"ll": ll, "text": text, "side": p.get("side"), "color": p.get("color")}
        return {"ll": (float(p[1]), float(p[2])), "text": p[0], "side": p[3] if len(p) > 3 else None}

    def frame(self, t):
        z = 1 + self.zoom * ease_in_out(t / self.dur)
        fx, fy = self.focus
        box = ((fx - fx / z) * SB, (fy - fy / z) * SB, (fx + (W - fx) / z) * SB, (fy + (H - fy) / z) * SB)
        canvas = self.base
        if self.geo:
            canvas = self.base.copy()
            for g in self.geo:
                g.draw(canvas, t)
        fr = canvas.resize((W, H), Image.BILINEAR, box=box)
        P = lambda q: (fx + (q[0] - fx) * z, fy + (q[1] - fy) * z)
        for q, disc, arr, lab, t0, hemi, letter in self.lows:
            x, y = P(q)
            s = back_out((t - t0) / 0.5)
            if s <= 0:
                continue
            ang = (t - t0) * 55 * hemi * (1 if letter == "L" else -1)       # NH low: counter-clockwise
            paste(fr, arr.rotate(ang, Image.BICUBIC), x, y, min(1, (t - t0) / 0.3), s, arr.width / 2, arr.height / 2)
            paste(fr, disc, x, y, 1, s, disc.width / 2, disc.height / 2)
            if lab:
                a = ease_out((t - t0 - 0.35) / 0.4)
                paste(fr, lab, x, y + 112, a, ax=lab.width / 2)
        for q, pin, lab, side, t0 in self.pins:
            x, y = P(q)
            s = back_out((t - t0) / 0.4)
            if s <= 0:
                continue
            paste(fr, pin, x, y, 1, s, 24, 24)
            if lab:
                a = ease_out((t - t0 - 0.1) / 0.35)
                dx = -(lab.width + 26) if side == "left" else 26
                paste(fr, lab, x + dx + (12 if side == "left" else -12) * (1 - a), y, a, ay=lab.height / 2)
        for q, img, t0 in self.tags:
            x, y = P(q)
            s = back_out((t - t0) / 0.4, 1.4)
            if s > 0:
                paste(fr, img, x, y, min(1, (t - t0) / 0.2), s, img.width / 2, img.height / 2)
        return fr


def count_text(value, p):
    """'32' -> '0'..'32' as p goes 0..1 (keeps commas, decimals, prefix/suffix such as '$' or ' ft')."""
    m = re.search(r"\d[\d,]*(\.\d+)?", value)
    if not m or p >= 1:
        return value
    num = float(m.group(0).replace(",", ""))
    dec = len(m.group(1)) - 1 if m.group(1) else 0
    v = num * ease_out(p)
    s = f"{v:,.{dec}f}" if "," in m.group(0) else f"{v:.{dec}f}"
    return value[:m.start()] + s + value[m.end():]


def split_value(v):
    """'235 mm' -> ('235', ' mm'); '40%' -> ('40', '%'); '$1.2M' -> ('$1.2', 'M'). Units are drawn smaller."""
    m = re.match(r"^(\D{0,2}\d[\d,\.]*)(.*)$", v.strip())
    return (m.group(1), m.group(2)) if m else (v, "")


class StatCard:
    def __init__(self, c, ep):
        self.c, self.dur = c, c["_seconds"]
        stats = c.get("stats") or [{"value": c["value"], "label": c.get("label", ""), "detail": c.get("detail")}]
        if not 1 <= len(stats) <= 3:
            raise SystemExit(f"card {c['id']}: 1-3 stats")
        self.stats = stats
        n = len(stats)
        col_w = 1560 / n - 60
        size = {1: 300, 2: 230, 3: 190}[n]
        for st in stats:                                   # one size for all numbers, fitted to the column
            num, unit = split_value(str(st["value"]))
            while G.text_w(num, size, "anton") + G.text_w(unit, size * 0.42, "anton") > col_w and size > 80:
                size -= 4
        self.size = size
        self.cols = [W / 2] if n == 1 else [W / 2 + (k - (n - 1) / 2) * (1560 / n) for k in range(n)]
        self.labels = []
        for st in stats:
            ls = 54 if n == 1 else 38
            while G.text_w(st.get("label", "").upper(), ls, "bold") > col_w and ls > 24:
                ls -= 2
            lab = Sprite(G.text_w(st.get("label", "").upper(), ls, "bold") + 4, ls * 1.4, 0, ls * 1.1)
            lab.text(0, ls * 1.1, ls, st.get("label", "").upper(), G.WH, "bold")
            det = None
            if st.get("detail"):
                ds = 32 if n == 1 else 26
                while G.text_w(st["detail"], ds, "light") > col_w + 40 and ds > 18:
                    ds -= 1
                det = Sprite(G.text_w(st["detail"], ds, "light") + 4, ds * 1.5, 0, ds * 1.15)
                det.text(0, ds * 1.15, ds, st["detail"], G.GREY, "light")
            self.labels.append((lab, det))
        self.bg = G.background()

    def frame(self, t):
        fr = self.bg.copy()
        base = 560 if len(self.stats) == 1 else 540
        S = self.size
        for k, (st, x, (lab, det)) in enumerate(zip(self.stats, self.cols, self.labels)):
            t0 = 0.45 + 0.25 * k
            a = ease_out((t - t0) / 0.4)
            if a <= 0:
                continue
            num, unit = split_value(str(st["value"]))
            shown = count_text(num, (t - t0) / 1.1)
            wn, wu = G.text_w(num, S, "anton"), G.text_w(unit, S * 0.42, "anton")
            s = Sprite(wn + wu + 16, S * 1.2, 0, S * 1.05)
            s.text(wn, S * 1.05, S, shown, G.WH, "anton", anchor="rs")       # right-aligned: counting doesn't jiggle
            if unit:
                s.text(wn + 6, S * 1.05, S * 0.42, unit.strip(), G.WH, "anton")
            paste(fr, s.img, x - (wn + wu) / 2, base + 30 * (1 - a), a, ay=S * 1.05)
            r = ease_in_out((t - t0 - 0.3) / 0.5)
            if r > 0:
                rw = min(520, 0.85 * 1560 / len(self.stats)) * r
                ln = Sprite(rw + 2, 8)
                ln.rect(0, 0, rw, 6, G.RED, 3)
                paste(fr, ln.img, x - rw / 2, base + 30)
            la = ease_out((t - t0 - 0.55) / 0.4)
            paste(fr, lab.img, x - lab.w / 2, base + 112 + 12 * (1 - la), la, ay=lab.ay)
            if det:
                paste(fr, det.img, x - det.w / 2, base + 160, ease_out((t - t0 - 0.75) / 0.4) * 0.95, ay=det.ay)
        return fr


class TimelineCard:
    def __init__(self, c, ep):
        self.c, self.dur = c, c["_seconds"]
        ev = c["events"]
        if not 2 <= len(ev) <= 6:
            raise SystemExit(f"card {c['id']}: timeline needs 2-6 events")
        self.n = len(ev)
        sp = 1520 / self.n
        self.xs = [200 + k * sp for k in range(self.n)]
        self.x_end = 200 + self.n * sp
        self.y = 560
        self.items = []
        for k, e in enumerate(ev):
            last = k == self.n - 1
            date = Sprite(G.text_w(e["date"].upper(), 34, "semibold") + 4, 48, 0, 36)
            date.text(0, 36, 34, e["date"].upper(), G.RED if last else G.WH, "semibold")
            lines = [l for l in str(e.get("text", "")).split("\n") if l]
            desc = []
            for l in lines:
                d = Sprite(G.text_w(l, 28, "light") + 4, 40, 0, 30)
                d.text(0, 30, 28, l, G.WH if last else (210, 214, 220), "light")
                desc.append(d)
            dot = Sprite(44, 44, 22, 22)
            if last:
                dot.circle(22, 22, 18, G.RED, a=90)
                dot.circle(22, 22, 12, G.RED)
                dot.circle(22, 22, 5, G.WH)
            else:
                dot.circle(22, 22, 13, G.WH)
                dot.circle(22, 22, 6, (30, 36, 46))
            self.items.append((date, desc, dot.img, k % 2 == 0))
        self.bg = G.background()

    def frame(self, t):
        fr = self.bg.copy()
        x0 = 200
        g = Sprite(self.x_end - x0 + 4, 8)
        g.rect(0, 0, self.x_end - x0, 4, (90, 100, 114), 2)
        paste(fr, g.img, x0, self.y - 2, ease_out((t - 0.3) / 0.4))
        step = 0.55
        prog = (t - 0.7) / step                                 # dots reached so far (float)
        k_last = self.n - 1
        reach = self.xs[0] + (self.xs[k_last] - self.xs[0]) * min(1, max(0, prog / max(1, k_last)))
        if prog > 0:
            ln = Sprite(reach - x0 + 4, 8)
            ln.rect(0, 0, reach - x0, 4, G.RED, 2)
            paste(fr, ln.img, x0, self.y - 2)
        for k, (date, desc, dot, above) in enumerate(self.items):
            tk = 0.7 + step * k
            s = back_out((t - tk) / 0.35)
            if s <= 0:
                continue
            x = self.xs[k]
            paste(fr, dot, x, self.y, 1, s, 22, 22)
            a = ease_out((t - tk - 0.1) / 0.4)
            if above:
                paste(fr, date.img, x - date.w / 2, self.y - 44 - 10 * (1 - a), a, ay=36)
                for j, d in enumerate(reversed(desc)):
                    paste(fr, d.img, x - d.w / 2, self.y - 98 - 38 * j - 10 * (1 - a), a * 0.95, ay=30)
            else:
                paste(fr, date.img, x - date.w / 2, self.y + 76 + 10 * (1 - a), a, ay=36)
                for j, d in enumerate(desc):
                    paste(fr, d.img, x - d.w / 2, self.y + 122 + 38 * j + 10 * (1 - a), a * 0.95, ay=30)
        return fr


class AlertCard:
    def __init__(self, c, ep):
        self.c, self.dur = c, c["_seconds"]
        self.bullets = c["bullets"]
        if not 1 <= len(self.bullets) <= 5:
            raise SystemExit(f"card {c['id']}: alert needs 1-5 bullets")
        self.bw = 1180
        self.x = (W - self.bw) / 2
        self.top = 300 if c.get("headline") else 250
        self.hh = 96
        title = c["title"].upper()
        ts = 46
        while G.text_w(title, ts, "semibold") > self.bw - 140 and ts > 28:
            ts -= 2
        body_h = 46 + len(self.bullets) * 66 + (60 if c.get("issuer") else 24)
        box = Sprite(self.bw + 2, self.hh + body_h + 2)
        box.rect(0, 0, self.bw, self.hh + body_h, (19, 23, 29), 12, a=245)
        box.rect(0, 0, self.bw, self.hh, G.RED, 12)
        box.rect(0, self.hh - 12, self.bw, 12, G.RED)
        cx, cy = 52, self.hh / 2                                  # warning triangle
        box.polygon([(cx, cy - 20), (cx + 22, cy + 18), (cx - 22, cy + 18)], G.WH)
        box.rect(cx - 2.5, cy - 7, 5, 15, G.RED, 2)
        box.circle(cx, cy + 12, 3, G.RED)
        box.text(92, cy + ts * 0.36, ts, title, G.WH, "semibold")
        if c.get("issuer"):
            box.text(48, self.hh + body_h - 30, 19, c["issuer"], G.SOURCE, "regular")
        self.box, self.body_h = box.img, body_h
        self.lines = []
        for b in self.bullets:
            bs = 38
            while G.text_w(b, bs, "light") > self.bw - 140 and bs > 24:
                bs -= 1
            s = Sprite(self.bw - 60, 60, 0, 40)
            s.circle(16, 40 - bs * 0.36, 7, G.RED)
            s.text(44, 40, bs, b, G.WH, "light")
            self.lines.append(s.img)
        self.bg = G.background()

    def frame(self, t):
        fr = self.bg.copy()
        a = ease_out((t - 0.35) / 0.45)
        paste(fr, self.box, self.x, self.top + 30 * (1 - a), a)
        for k, img in enumerate(self.lines):
            b = ease_out((t - 1.0 - 0.45 * k) / 0.4)
            paste(fr, img, self.x + 48 - 20 * (1 - b), self.top + self.hh + 26 + 66 * k, b, ay=0)
        return fr


class ImageCard:
    """flood_map from an image (Copernicus EMS / Sentinel map...): cover-fit, slow zoom."""
    def __init__(self, c, ep):
        self.c, self.dur = c, c["_seconds"]
        p = ep / c["image"] if not Path(c["image"]).is_absolute() else Path(c["image"])
        im = Image.open(p).convert("RGB")
        if c.get("crop"):                                       # [x, y, w, h] fractions
            x, y, w, h = c["crop"]
            im = im.crop((round(x * im.width), round(y * im.height), round((x + w) * im.width), round((y + h) * im.height)))
        k = max(W * SB / im.width, H * SB / im.height)
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        l, t = (im.width - W * SB) / 2, (im.height - H * SB) / 2
        self.base = im.crop((round(l), round(t), round(l + W * SB), round(t + H * SB)))
        self.zoom = c.get("zoom", 0.06)

    def frame(self, t):
        z = 1 + self.zoom * ease_in_out(t / self.dur)
        fx, fy = W / 2, H / 2
        box = ((fx - fx / z) * SB, (fy - fy / z) * SB, (fx + (W - fx) / z) * SB, (fy + (H - fy) / z) * SB)
        return self.base.resize((W, H), Image.BILINEAR, box=box)


class VideoCard:
    """satellite: frames from a supplied mp4 (cover-fit, looped if short, optional speed-up)."""
    def __init__(self, c, ep):
        import subprocess
        self.c, self.dur = c, c["_seconds"]
        p = ep / c["video"] if not Path(c["video"]).is_absolute() else Path(c["video"])
        if not p.exists():
            raise SystemExit(f"card {c['id']}: video {p} not found")
        speed = float(c.get("speed", 1.0))
        vf = (f"setpts=PTS/{speed},fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},format=rgb24")
        self.proc = subprocess.Popen(["ffmpeg", "-v", "error", "-stream_loop", "-1", "-ss", str(c.get("start", 0)), "-i", str(p),
                                      "-t", str(self.dur), "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                     stdout=subprocess.PIPE)
        self.last = None

    def frame(self, t):
        buf = self.proc.stdout.read(W * H * 3)
        if len(buf) == W * H * 3:
            self.last = Image.frombytes("RGB", (W, H), buf)
        return (self.last or G.background()).copy()


def build_card(c, ep, out_dir, stills_only=False):
    typ = c["type"]
    if typ == "flood_map" and c.get("image"):
        body, dark = ImageCard(c, ep), True
    elif typ == "satellite":
        body, dark = VideoCard(c, ep), True
    elif typ in MAP_TYPES:
        body, dark = None, False
    else:
        body, dark = {"stat": StatCard, "timeline": TimelineCard, "alert": AlertCard}[typ](c, ep), False
    pill_txt = c.get("pill") or TYPES[typ]
    chrome = G.Chrome(pill_txt, c.get("headline"), c.get("sub"), c.get("source"), c.get("sub_at", 1.6), dark_top=dark)
    if body is None:
        body = MapCard(c, ep, chrome.boxes())
    dur = c["_seconds"]
    n = int(round(dur * FPS))

    def frame(i):
        t = i / FPS
        fr = body.frame(t)
        chrome.draw(fr, t)
        return fr

    still_t = min(dur - 0.5, 4.0)
    if stills_only:
        if isinstance(body, VideoCard):
            for i in range(int(still_t * FPS)):
                body.frame(i / FPS)
            body.proc.kill()
        frame(int(still_t * FPS)).save(out_dir / f"{c['id']}.png")
        return c["id"] + " still"
    def gen():
        for i in range(n):
            f = frame(i)
            if i == int(still_t * FPS):
                f.save(out_dir / f"{c['id']}.png")
            yield f
    G.encode_mp4(gen(), out_dir / f"{c['id']}.mp4")
    return f"{c['id']} {dur:.1f}s"


# ---- config checks ------------------------------------------------------------------------------------------------------
def check(cards, ep, facts_check=True):
    """No repeats, no cards in the cold open, facts from research/facts.csv, forecast maps say 'forecast'."""
    if not cards:
        raise SystemExit("no CARDS in project/cards.py")
    fact_ids = set()
    fp = ep / "research/facts.csv"
    if fp.exists():
        fact_ids = {(r.get("fact_id") or "").strip() for r in csv.DictReader(open(fp, encoding="utf8"))}
    seen_id, seen_head, seen_media = set(), set(), set()
    for c in cards:
        cid = c.get("id")
        if not cid or not re.fullmatch(r"[A-Za-z0-9_\-]+", cid):
            raise SystemExit(f"card {c}: needs an 'id' (letters, digits, _ or -)")
        if c.get("type") not in TYPES:
            raise SystemExit(f"card {cid}: type must be one of {', '.join(TYPES)}")
        if cid in seen_id:
            raise SystemExit(f"card {cid}: id used twice (every card is shown once)")
        seen_id.add(cid)
        key = (c.get("headline") or c.get("title") or "").strip().upper()
        if key and key in seen_head:
            raise SystemExit(f"card {cid}: same headline as another card ({key}); no repeats")
        seen_head.add(key)
        for m in ("image", "video", "geojson"):
            if c.get(m):
                if c[m] in seen_media:
                    raise SystemExit(f"card {cid}: {c[m]} is already used by another card; no repeats")
                seen_media.add(c[m])
        if c.get("chapter") in (None, "S00"):
            raise SystemExit(f"card {cid}: 'chapter' must be a narration chapter (S01...), never the cold open S00")
        c["_seconds"] = max(6.0, min(8.0, float(c.get("seconds", 7.0))))
        if c["type"] == "flood_map" and not (c.get("image") or c.get("geojson")):
            raise SystemExit(f"card {cid}: flood_map needs 'image' or 'geojson'")
        if c["type"] == "satellite" and not c.get("video"):
            raise SystemExit(f"card {cid}: satellite needs 'video' (an mp4)")
        if c["type"] in ("forecast_map", "track_map"):        # forecast maps say "forecast" (worflow.md §0)
            txt = " ".join(str(c.get(k) or "") for k in ("pill", "headline", "sub", "source")) + " " + (c.get("pill") or TYPES[c["type"]])
            if not re.search(r"forecast|outlook|expected|predicted|pron[oó]stico|previsi[oó]n", txt, re.I):
                raise SystemExit(f"card {cid}: a forecast map must say 'forecast' or 'outlook' (pill, headline or sub)")
        if facts_check:
            fl = c.get("facts") or []
            if not fl:
                raise SystemExit(f"card {cid}: list the research/facts.csv ids it shows in 'facts' (or run with --no-facts-check)")
            missing = [f for f in fl if f not in fact_ids]
            if missing:
                raise SystemExit(f"card {cid}: facts {missing} not in research/facts.csv")
    types = [c["type"] for c in cards]
    dup = sorted({t for t in types if types.count(t) > 1})
    if dup:
        print("note: more than one card of type", ", ".join(dup), "- make sure they show different things")


def _job(args):
    c, ep, out, stills = args
    try:
        return build_card(c, Path(ep), Path(out), stills)
    except SystemExit as e:
        return f"{c['id']} FAILED: {e}"
    except Exception as e:
        import traceback
        return f"{c['id']} FAILED: {e!r}\n{traceback.format_exc()[-1500:]}"


def contact(out_dir, ids):
    ims = [Image.open(out_dir / f"{i}.png").convert("RGB").resize((640, 360), Image.LANCZOS) for i in ids if (out_dir / f"{i}.png").exists()]
    if not ims:
        return
    cols = 3
    rows = math.ceil(len(ims) / cols)
    sheet = Image.new("RGB", (cols * 640 + (cols + 1) * 8, rows * 360 + (rows + 1) * 8), (8, 10, 12))
    for k, im in enumerate(ims):
        sheet.paste(im, (8 + (k % cols) * 648, 8 + (k // cols) * 368))
    sheet.save(out_dir / "_contact.png")
    print("contact sheet:", out_dir / "_contact.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--stills", action="store_true", help="review stills only")
    ap.add_argument("--contact", action="store_true", help="contact sheet of all stills")
    ap.add_argument("--no-facts-check", action="store_true")
    ap.add_argument("--project", default=".", help="the episode's project/ folder")
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    proj = Path(a.project).resolve()
    ep = proj.parent
    _, cards = G.load_config(proj)
    check(cards, ep, not a.no_facts_check)
    sel = [c for c in cards if not a.ids or c["id"] in a.ids]
    out = ep / "graphics/cards"
    out.mkdir(parents=True, exist_ok=True)
    print(f"{len(sel)} card(s) -> {out}", flush=True)
    jobs = [(c, str(ep), str(out), a.stills) for c in sel]
    if a.jobs > 1 and len(jobs) > 1:
        with ProcessPoolExecutor(min(a.jobs, len(jobs))) as ex:
            for r in ex.map(_job, jobs):
                print(r, flush=True)
    else:
        for j in jobs:
            print(_job(j), flush=True)
    if a.contact or a.stills:
        contact(out, [c["id"] for c in sel])


if __name__ == "__main__":
    main()
