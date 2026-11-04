"""lat/lon -> pixel on NOAA STAR GOES-19 ABI CONUS images (fixed-grid geos projection).
Image bounds = CONUS sector scan angles (rad). Verified visually against coastlines on the 2500x1500 product."""
import math
REQ, RPOL, H, LON0 = 6378137.0, 6356752.31414, 42164160.0, -75.2
XMIN, XMAX, YMAX, YMIN = -0.101346, 0.038626, 0.128226, 0.044254
def scan(lat, lon):
    la, lo = math.radians(lat), math.radians(lon - LON0)
    e2 = 1 - RPOL**2 / REQ**2
    pc = math.atan((RPOL**2 / REQ**2) * math.tan(la))
    rc = RPOL / math.sqrt(1 - e2 * math.cos(pc)**2)
    sx = H - rc * math.cos(pc) * math.cos(lo); sy = -rc * math.cos(pc) * math.sin(lo); sz = rc * math.sin(pc)
    return math.asin(-sy / math.sqrt(sx*sx + sy*sy + sz*sz)), math.atan(sz / sx)
def px(lat, lon, W=2500, Hh=1500):
    x, y = scan(lat, lon)
    return (x - XMIN) / (XMAX - XMIN) * W, (YMAX - y) / (YMAX - YMIN) * Hh
if __name__ == "__main__":
    for n, la, lo in [("Key West", 24.555, -81.78), ("Chicago", 41.88, -87.63), ("Seattle", 47.61, -122.33), ("Brownsville", 25.90, -97.50), ("Cape Hatteras", 35.25, -75.53)]:
        print(n, [round(v) for v in px(la, lo)])
