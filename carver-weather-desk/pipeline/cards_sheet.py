"""Contact sheet of card stills with the reserved zones outlined faintly (labels drawn with PIL; ffmpeg drawtext
crashes on this machine).
  python cards_sheet.py <out.jpg> a.png b.png ...      (or a directory: every *.png in it)
Zones: host box 600x480 top right (crimson), bug 420x120 top left (sky), ticker bottom 66 px (sky),
strap x<1320, y>820 (amber, dashed: only binding for strap_clear cards).
"""
import pathlib, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = ROOT / "brand-kit" / "fonts" / "BarlowCondensed-SemiBold.ttf"
TW, TH, COLS, LAB = 960, 540, 2, 44


def dashed_rect(d, box, fill, w=3, dash=18, gap=12):
    x0, y0, x1, y1 = box
    for (a, b, horiz, c) in ((x0, x1, True, y0), (x0, x1, True, y1), (y0, y1, False, x0), (y0, y1, False, x1)):
        p = a
        while p < b:
            q = min(b, p + dash)
            d.line([(p, c), (q, c)] if horiz else [(c, p), (c, q)], fill=fill, width=w)
            p = q + gap


def zones(im):
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.rectangle([1320, 0, 1919, 480], fill=(215, 25, 47, 38), outline=(215, 25, 47, 200), width=4)
    d.rectangle([0, 0, 420, 120], fill=(92, 200, 255, 30), outline=(92, 200, 255, 190), width=4)
    d.rectangle([0, 1014, 1919, 1079], fill=(92, 200, 255, 30), outline=(92, 200, 255, 190), width=4)
    dashed_rect(d, (2, 820, 1320, 1012), (255, 181, 31, 210), w=4)
    f = ImageFont.truetype(str(FONT), 30)
    for xy, t in (((1332, 446), "HOST BOX"), ((12, 84), "BUG"), ((12, 1022), "TICKER"), ((12, 826), "STRAP (strap_clear)")):
        d.text(xy, t, font=f, fill=(255, 255, 255, 200))
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def main():
    out = pathlib.Path(sys.argv[1])
    srcs = []
    for a in sys.argv[2:]:
        p = pathlib.Path(a)
        srcs += sorted(p.glob("*.png")) if p.is_dir() else [p]
    srcs = [s for s in srcs if not s.name.startswith("_")]
    rows = (len(srcs) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * TW, rows * (TH + LAB)), (5, 12, 26))
    d = ImageDraw.Draw(sheet); f = ImageFont.truetype(str(FONT), 30)
    for i, s in enumerate(srcs):
        x, y = (i % COLS) * TW, (i // COLS) * (TH + LAB)
        sheet.paste(zones(Image.open(s)).resize((TW, TH), Image.LANCZOS), (x, y + LAB))
        d.text((x + 14, y + 7), s.stem.upper(), font=f, fill=(233, 238, 247))
    sheet.save(out, quality=90)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
