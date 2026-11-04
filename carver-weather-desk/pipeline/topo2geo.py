"""TopoJSON -> GeoJSON for the US state layer used by map cards.

Source (read only): international-weather-network/iwn-brand-kit/geo/us-states-10m.json (us-atlas 10m, Census
cartographic boundaries). Writes, into carver-weather-desk/brand-kit/geo/:
  us-states.geojson        one Feature per state, properties {name, abbr, fips}  (polygon highlights)
  us-states-lines.geojson  every topology arc once (borders + coasts) as a MultiLineString (outline layer,
                           so shared borders are not stroked twice)
Usage: python topo2geo.py [src.json] [out_dir]
"""
import json, pathlib, sys

FIPS = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE", "11": "DC",
        "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
        "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT",
        "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
        "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT",
        "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI", "56": "WY", "60": "AS", "66": "GU", "69": "MP",
        "72": "PR", "78": "VI"}


def main():
    here = pathlib.Path(__file__).resolve().parent
    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else \
        here.parents[1] / "international-weather-network/iwn-brand-kit/geo/us-states-10m.json"
    out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else here.parent / "brand-kit/geo"
    out.mkdir(parents=True, exist_ok=True)
    topo = json.loads(src.read_text())
    sx, sy = topo["transform"]["scale"]; tx, ty = topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:                       # delta-decoded, quantized -> lon/lat
        x = y = 0; pts = []
        for dx, dy in arc:
            x += dx; y += dy
            pts.append([round(x * sx + tx, 4), round(y * sy + ty, 4)])
        arcs.append(pts)

    def ring(idx):
        pts = []
        for i in idx:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts.extend(a if not pts else a[1:])
        return pts

    feats = []
    for g in topo["objects"]["states"]["geometries"]:
        if g["type"] == "Polygon":
            coords = [[ring(r) for r in g["arcs"]]]
        else:
            coords = [[ring(r) for r in poly] for poly in g["arcs"]]
        fips = str(g.get("id", "")).zfill(2)
        feats.append({"type": "Feature", "properties": {"name": g["properties"]["name"], "abbr": FIPS.get(fips, ""), "fips": fips},
                      "geometry": {"type": "MultiPolygon", "coordinates": coords}})
    (out / "us-states.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": feats}, separators=(",", ":")))
    lines = {"type": "Feature", "properties": {"name": "US state borders and coasts"},
             "geometry": {"type": "MultiLineString", "coordinates": arcs}}
    (out / "us-states-lines.geojson").write_text(json.dumps(lines, separators=(",", ":")))
    print(f"{len(feats)} states, {len(arcs)} arcs -> {out}")


if __name__ == "__main__":
    main()
