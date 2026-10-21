"""Pack Natural Earth 1:10m layers (public domain, naturalearthdata.com) into geo/natural_earth_10m.npz for make_cards.py.

Only needed again to refresh the bundled file. Download the GeoJSON files from
https://github.com/nvkelso/natural-earth-vector/tree/master/geojson into one folder, then:

    python pack_natural_earth.py <folder with the .geojson files>

Layers: land (+ minor islands), lakes, country borders (land boundary lines), state/province lines, populated places.
Coordinates are rounded to 0.001 degree (about 100 m), which is finer than the 10m data itself.
"""
import json, sys
from pathlib import Path

import numpy as np

Q = 1000   # 0.001 degree steps


def rings(geom, polygons_only=False):
    t, c = geom["type"], geom["coordinates"]
    if t == "Polygon":
        return [r for r in c]
    if t == "MultiPolygon":
        return [r for p in c for r in p]
    if polygons_only:
        return []
    if t == "LineString":
        return [c]
    if t == "MultiLineString":
        return list(c)
    return []


def pack(src, names, polygons_only=False, keep=lambda p: True):
    out = []
    for n in names:
        for f in json.load(open(src / f"{n}.geojson", encoding="utf8"))["features"]:
            if f["geometry"] and keep(f["properties"]):
                for r in rings(f["geometry"], polygons_only):
                    a = np.round(np.asarray(r, np.float64)[:, :2] * Q).astype(np.int32)
                    a = a[np.r_[True, np.any(np.diff(a, axis=0) != 0, axis=1)]]     # drop repeated points
                    if len(a) >= 2:
                        out.append(a)
    coords = np.concatenate(out)
    offs = np.cumsum([0] + [len(a) for a in out]).astype(np.int64)
    print(f"{names[0]}: {len(out)} rings, {len(coords)} points")
    return coords, offs


def main():
    src = Path(sys.argv[1])
    data = {}
    for key, names, poly in (("land", ["ne_10m_land", "ne_10m_minor_islands"], True),
                             ("lakes", ["ne_10m_lakes"], True),
                             ("borders", ["ne_10m_admin_0_boundary_lines_land"], False),
                             ("states", ["ne_10m_admin_1_states_provinces_lines"], False)):
        c, o = pack(src, names, poly)
        data[key + "_xy"], data[key + "_off"] = c, o
    places = json.load(open(src / "ne_10m_populated_places_simple.geojson", encoding="utf8"))["features"]
    rows = [(p["properties"]["name"], p["properties"].get("adm1name") or "", p["properties"].get("adm0name") or "",
             p["properties"]["latitude"], p["properties"]["longitude"], p["properties"].get("pop_max") or 0) for p in places]
    data["places"] = np.array(json.dumps(rows, ensure_ascii=False))
    out = Path(__file__).with_name("natural_earth_10m.npz")
    np.savez_compressed(out, **data)
    print(out, f"{out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
