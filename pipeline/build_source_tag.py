"""Build IWN On-Screen Editorial Source Attribution tags (PNG / ProRes 4444 alpha MOV).

Adheres strictly to IWN Approved Identity:
  - Palette: Charcoal (#17191D), Warm White (#F5F2EB), Signal Red (#EF343D)
  - Typography: Manrope-Bold (supersampled 2x for subpixel anti-aliasing)
  - Layout: Newsroom capsule with red 'FOOTAGE SOURCE' tag, source credit, and location divider

Usage:
  # Standalone CLI:
  python build_source_tag.py "Local Resident via X" "Santiago, Chile"
  python build_source_tag.py "Eyewitness via X" "Estación Central" --pos top_right --anim

  # Programmatic batch:
  from build_source_tag import make_source_tag
  make_source_tag("Local Resident via X", "Santiago, Chile", out_png="source_01.png")
"""
import argparse, os, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 30
SS = 2  # Supersampling factor
DARK = (0x17, 0x19, 0x1D)
WHITE = (0xF5, 0xF2, 0xEB)
RED = (0xEF, 0x34, 0x3D)

SCRIPT_DIR = Path(__file__).resolve().parent
# Locate iwn-brand-kit by searching up the directory hierarchy
KIT = None
for p in [SCRIPT_DIR] + list(SCRIPT_DIR.parents):
    cand = p / "iwn-brand-kit"
    if cand.exists() and (cand / "fonts/Manrope-Bold.ttf").exists():
        KIT = cand
        break
if KIT is None:
    raise RuntimeError(f"iwn-brand-kit with fonts/Manrope-Bold.ttf could not be located from {SCRIPT_DIR}")


def get_font(size):
    font_path = KIT / "fonts/Manrope-Bold.ttf"
    if font_path.exists():
        return ImageFont.truetype(str(font_path), int(round(size * SS)))
    raise FileNotFoundError(f"Font not found: {font_path}")


def render_source_tag_image(source_text, location_text=None, pos="bottom_left"):
    """Render a 1920x1080 transparent RGBA PIL Image containing the IWN source attribution pill."""
    im = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f24, f20 = get_font(24), get_font(20)

    tag_str = "FOOTAGE SOURCE"
    tag_w = int(f20.getlength(tag_str) / SS) + 36
    src_w = int(f24.getlength(source_text) / SS)
    loc_w = int(f24.getlength(location_text) / SS) if location_text else 0

    total_w = 18 + tag_w + 22 + src_w
    if loc_w:
        total_w += 20 + 2 + 20 + loc_w
    total_w += 26

    h = 72
    if pos == "bottom_left":
        x, y = 96, 920
    elif pos == "top_right":
        x, y = W - total_w - 96, 74
    elif pos == "top_left":
        x, y = 96, 74
    else:
        x, y = 96, 920

    # Charcoal capsule background with 1px soft white edge
    d.rounded_rectangle(
        [x * SS, y * SS, (x + total_w) * SS, (y + h) * SS],
        radius=(h / 2) * SS,
        fill=DARK + (245,),
        outline=WHITE + (40,),
        width=1 * SS,
    )

    # Signal Red accent pill for 'FOOTAGE SOURCE'
    tag_x = x + 14
    tag_y = y + 13
    tag_h = h - 26
    d.rounded_rectangle(
        [tag_x * SS, tag_y * SS, (tag_x + tag_w) * SS, (tag_y + tag_h) * SS],
        radius=(tag_h / 2) * SS,
        fill=RED + (255,),
    )
    d.text(((tag_x + 18) * SS, (tag_y + tag_h - 12) * SS), tag_str, font=f20, fill=WHITE + (255,), anchor="ls")

    # Source text
    cur_x = tag_x + tag_w + 20
    d.text((cur_x * SS, (y + 47) * SS), source_text, font=f24, fill=WHITE + (255,), anchor="ls")
    cur_x += src_w

    if loc_w:
        # Vertical divider line
        div_x = cur_x + 18
        d.rounded_rectangle(
            [div_x * SS, (y + 22) * SS, (div_x + 2) * SS, (y + h - 22) * SS],
            radius=1 * SS,
            fill=WHITE + (100,),
        )
        # Location / context text
        d.text(((div_x + 18) * SS, (y + 47) * SS), location_text, font=f24, fill=WHITE + (210,), anchor="ls")

    return im.resize((W, H), Image.LANCZOS)


def make_source_tag(source_text, location_text=None, pos="bottom_left", out_png=None, out_mov=None, duration_s=4.0):
    """Generate source tag deliverables (PNG and/or ProRes 4444 MOV with alpha)."""
    im = render_source_tag_image(source_text, location_text, pos=pos)
    
    if out_png:
        out_png = Path(out_png)
        out_png.parent.mkdir(parents=True, exist_ok=True)
        im.save(out_png, "PNG")
        print(f"Saved PNG: {out_png}")

    if out_mov:
        out_mov = Path(out_mov)
        out_mov.parent.mkdir(parents=True, exist_ok=True)
        # Generate ProRes 4444 video with smooth slide-in (0.35s) and slide-out (0.35s)
        arr = np.asarray(im, dtype=np.float32) / 255.0
        ys, xs = np.where(arr[..., 3] > 0)
        y0, y1, x0, x1 = int(ys.min()), int(ys.max()) + 1, int(xs.min()), int(xs.max()) + 1
        patch = arr[y0:y1, x0:x1]

        total_frames = int(round(duration_s * FPS))
        in_frames = int(round(0.35 * FPS))
        out_frames = int(round(0.35 * FPS))
        out_start = total_frames - out_frames

        tmp_mov = out_mov.with_suffix(".part.mov")
        cmd = [
            "ffmpeg", "-v", "error", "-y",
            "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
            "-i", "-",
            "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
            "-vendor", "apl0", str(tmp_mov)
        ]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)

        for n in range(total_frames):
            frame = np.zeros((H, W, 4), dtype=np.uint8)
            # Calculate slide / fade offset
            if n < in_frames:
                t = n / in_frames
                ease = 1 - (1 - t) ** 3
                dx = int(round(-200 * (1 - ease)))
                alpha = ease
            elif n >= out_start:
                t = (n - out_start) / out_frames
                ease = t ** 2
                dx = int(round(-200 * ease))
                alpha = max(0.0, 1.0 - ease)
            else:
                dx = 0
                alpha = 1.0

            cur_x = x0 + dx
            if cur_x < W and cur_x + (x1 - x0) > 0:
                p_copy = patch.copy()
                p_copy[..., 3] *= alpha
                # place
                dst_x0 = max(0, cur_x)
                dst_x1 = min(W, cur_x + (x1 - x0))
                src_x0 = dst_x0 - cur_x
                src_x1 = src_x0 + (dst_x1 - dst_x0)
                frame[y0:y1, dst_x0:dst_x1] = (p_copy[:, src_x0:src_x1] * 255 + 0.5).astype(np.uint8)

            p.stdin.write(frame.tobytes())

        p.stdin.close()
        if p.wait():
            raise RuntimeError("ffmpeg ProRes encoding failed for " + out_mov.name)
        tmp_mov.replace(out_mov)
        print(f"Saved MOV: {out_mov}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build IWN On-Screen Editorial Source Attribution Tag")
    parser.add_argument("source", help="Source attribution (e.g. 'Local Resident via X')")
    parser.add_argument("location", nargs="?", default=None, help="Location context (e.g. 'Santiago, Chile')")
    parser.add_argument("--pos", choices=["bottom_left", "top_right", "top_left"], default="bottom_left", help="Tag placement")
    parser.add_argument("--out", default="source_tag.png", help="Output path (PNG or MOV)")
    parser.add_argument("--anim", action="store_true", help="Also generate animated ProRes 4444 MOV")
    parser.add_argument("--dur", type=float, default=4.0, help="Duration in seconds for animated MOV")
    args = parser.parse_args()

    out_path = Path(args.out)
    if args.anim or out_path.suffix.lower() == ".mov":
        mov_path = out_path.with_suffix(".mov")
        png_path = out_path.with_suffix(".png")
        make_source_tag(args.source, args.location, pos=args.pos, out_png=png_path, out_mov=mov_path, duration_s=args.dur)
    else:
        make_source_tag(args.source, args.location, pos=args.pos, out_png=out_path)
