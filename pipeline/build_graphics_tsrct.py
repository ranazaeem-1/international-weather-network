"""Build per-chapter IWN lower-thirds (broadcast package) and an episode ticker from the brand-kit motion design.

Each graphic gets its own editable .tsrct project in graphics/src and a ProRes 4444 alpha export in graphics/.
Layout, colours, fonts and animation come from iwn-brand-kit/source/build_motion.py + build_broadcast.py;
only the copy (and the location capsule width) changes per chapter.
"""
import json, sys
from pathlib import Path
from PIL import ImageFont

EP = Path(__file__).resolve().parents[1]
KIT = EP.parents[1] / "iwn-brand-kit"
sys.path.insert(0, str(KIT / "source"))
import build_motion as m  # noqa: E402

m.CLI = KIT / "tools/tesseract/tesseract-0.3.1-windows-x86_64/bin/tsrct.exe"
FONT = ImageFont.truetype(str(KIT / "fonts/Manrope-Bold.ttf"), 27)
DFONT = ImageFont.truetype(str(KIT / "fonts/Manrope-Bold.ttf"), 24)
SRC = EP / "graphics/src"
OUT = EP / "graphics"

# id: (category, headline, sub-line, location, date)
LOWER_THIRDS = {
    "S01": ("WEATHER UPDATE", "HEADLINE", "Sub-line", "PLACE", "01 JAN 2026"),
}

TICKER_COPY = (
    "TICKER COPY     \u2022     "
)
TICKER_LABEL, TICKER_STATUS = "PLACE", "WEATHER UPDATE"


def fresh_project(path: Path, seconds: int):
    if path.exists():
        path.unlink()
    m.run("project", "create", "--project", path)
    m.run("project", "import-font", "--project", path, "--file", KIT / "fonts/Manrope.ttf")
    work = SRC / f"{path.stem}.json"
    m.run("project", "checkout", "--project", path, "--output", work)
    doc = json.loads(work.read_text(encoding="utf8"))
    doc["duration"] = seconds
    doc["dimensions"] = {"width": 1920, "height": 1080}
    work.write_text(json.dumps(doc), encoding="utf8")
    m.run("project", "commit", "--project", path, "--file", work)


def lower_third(seg, cat, head, sub, loc, date):
    m.duration = 8000
    p = SRC / f"lt_{seg}.tsrct"
    fresh_project(p, 8)
    pill_w = max(275, int(FONT.getlength(cat) * 23 / 27) + 48)
    a = [
        m.rect(1, "Headline panel", 164, 848, 1658, 150, m.D, 36),
        m.rect(2, "Update category pill", 291, 811, pill_w, 49, m.R, 24),
        m.text(3, "Category", 315, 845, 23, cat, m.W),
        m.text(4, "Headline line one", 291, 910, 35, head, m.W),
        m.text(5, "Headline line two", 291, 961, 28, sub, m.W),
    ]
    a += m.badge(10, 82, 832, 184)
    a += [
        m.group([12, 11, 10, 5, 4, 3, 2, 1]),
        m.anim(100, "positionY", "const t=input.time.seconds; const a=1-Math.pow(1-Math.min(1,t/.45),3); const b=Math.max(0,Math.min(1,(t-7.4)/.45)); return 260*(1-a+b*b);"),
        m.anim(100, "opacity", "const t=input.time.seconds;return Math.min(1,t/.2)*Math.max(0,1-(t-7.4)/.45)*100;"),
    ]
    loc_w = FONT.getlength(loc)
    sep_x = 171 + loc_w + 22
    date_x = sep_x + 26
    cap_w = date_x + DFONT.getlength(date) + 30 - 96
    a += [
        m.rect(20, "Location capsule", 96, 74, cap_w, 76, m.D, 38),
        m.rect(21, "Location signal", 119, 95, 34, 34, m.R, 17),
        m.text(22, "Location", 171, 122, 27, loc, m.W),
        m.rect(23, "Date separator", sep_x, 92, 2, 38, m.W),
        m.text(24, "Date", date_x, 122, 24, date, m.W),
        dict(type="groupFxCompositionLayers", compositionId="main", layerIds=[24, 23, 22, 21, 20], groupLayerId=200, name="Location and date", transform=m.tr()),
        m.anim(200, "positionX", "const t=input.time.seconds;return -900*Math.pow(1-Math.min(1,t/.4),3);"),
        dict(type="groupFxCompositionLayers", compositionId="main", layerIds=[200, 100], groupLayerId=300, name="Broadcast package - alpha export", transform=m.tr()),
    ]
    actions = SRC / f"lt_{seg}-actions.json"
    actions.write_text(json.dumps(a), encoding="utf8")
    m.run("project", "apply", "--project", p, "--actions", actions)
    m.run("preview", "--project", p, "--time", 2, "--output", SRC / f"lt_{seg}.png")
    m.run("export", "--project", p, "--output", OUT / f"lt_{seg}.mov", "--format", "prores", "--fx-solo", "main:300")


def ticker(seconds=16):
    m.duration = seconds * 1000
    p = SRC / "ticker.tsrct"
    fresh_project(p, seconds)
    # Point text wraps at about the canvas width, so every headline is its own layer, laid out side by side.
    tfont = ImageFont.truetype(str(KIT / "fonts/Manrope-Bold.ttf"), 31)
    items = [s.strip() for s in TICKER_COPY.split("•") if s.strip()]
    scroll, x, k = [], 510.0, 0
    while x < 510 + 1430 + seconds * 90 + 200:
        for piece in (items[k % len(items)], "•"):
            scroll.append((30 + len(scroll), x, piece))
            x += tfont.getlength(piece) + 46
        k += 1
    a = [
        m.rect(1, "Ticker background", 0, 930, 1920, 106, m.D),
        m.rect(2, "Red rule", 0, 930, 1920, 4, m.R),
        *[m.text(i, f"Scrolling copy {i}", px, 995, 31, piece, m.W) for i, px, piece in scroll],
        m.rect(4, "Fixed label backing", 0, 934, 490, 102, m.D),
        m.text(5, "Ticker label", 224, 981, 27, TICKER_LABEL, m.W),
        m.text(6, "Status", 225, 1010, 18, TICKER_STATUS, m.R),
    ]
    a += m.badge(10, 56, 896, 142)
    a += [m.group([12, 11, 10, 6, 5, 4, *[i for i, _, _ in reversed(scroll)], 2, 1])]
    a += [m.anim(i, "positionX", f"return {px:.1f}-input.time.seconds*90;") for i, px, _ in scroll]
    actions = SRC / "ticker-actions.json"
    actions.write_text(json.dumps(a), encoding="utf8")
    m.run("project", "apply", "--project", p, "--actions", actions)
    m.run("preview", "--project", p, "--time", 5, "--output", SRC / "ticker.png")
    m.run("export", "--project", p, "--output", OUT / "ticker_full.mov", "--format", "prores", "--fx-solo", "main:100")


if __name__ == "__main__":
    SRC.mkdir(parents=True, exist_ok=True)
    only = sys.argv[1:]
    for seg, args in LOWER_THIRDS.items():
        if not only or seg in only:
            lower_third(seg, *args)
            print("built", seg)
    if not only or "ticker" in only:
        ticker()
        print("built ticker")
