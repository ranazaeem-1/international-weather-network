"""IWN intro title card (user, 21 Oct 2026): ~3.4 s, placed right after the cold open (S00), before S01.

Navy background -> the iwn letters fade in -> the red dot drops onto the i -> a red rule opens -> "INDEPENDENT WEATHER
NETWORK" -> the episode headline (Anton, caps) -> "LATEST UPDATES · <date>" -> hold -> a red bar wipes left to right.
Behind the bar the frame turns transparent, so in CapCut the wipe reveals the first narration clip (S01).
Timing matches the user's hand-made intro in https://www.youtube.com/watch?v=Bsw35dVmjLo (0:19-0:22).

Input: INTRO = {"headline": "...", "date": "20 OCT 2026"} in project/cards.py (optional "network", "kicker").
Output: graphics/intro.mov (ProRes 4444 with alpha) + graphics/intro_still.png (for review).

Usage (from the episode's project/ folder):
    python make_intro.py
    python make_intro.py --headline "NOR'EASTER HAMMERS THE OUTER BANKS" --date "20 OCT 2026" [--lang es]
"""
import argparse, sys
from pathlib import Path

import numpy as np
from PIL import Image

import iwn_gfx as G

LENGTH = 3.4          # seconds; the last WIPE seconds overlap the start of S01 in the draft
WIPE = 0.45
NETWORK = {"en": "INDEPENDENT WEATHER NETWORK", "es": "INSTANT WEATHER NETWORK"}
KICKER = {"en": "LATEST UPDATES", "es": "ÚLTIMAS NOTICIAS"}


def build(headline, date, out_dir, network=None, kicker=None, lang="en"):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    network = (network or NETWORK.get(lang, NETWORK["en"])).upper()
    kicker = f"{(kicker or KICKER.get(lang, KICKER['en'])).upper()} · {date.upper()}"
    letters, dot, _ = G.logo_parts()
    LW = 524                                                       # letters width on screen (reference: 696-1220)
    letters = letters.resize((LW, round(letters.height * LW / letters.width)), Image.LANCZOS)
    k = LW / G.logo_parts()[0].width
    dot = dot.resize((max(1, round(dot.width * k)), max(1, round(dot.height * k))), Image.LANCZOS)
    cx = G.W / 2
    lx, ly = cx - LW / 2, 410                                      # letters top-left
    dot_x, dot_y = lx, ly - dot.height - 44 * k                  # above the stem of the i, as in the logo (44 px gap at 904 px)

    rule_y, rule_w = 614, 658
    net = G.Sprite(G.text_w(network, 30, "semibold") + 4, 44, 0, 34)
    net.text(0, 34, 30, network, G.WH, "semibold")
    head_img, head_asc = G.headline_sprite(headline.upper(), size=66, max_w=1500)
    kick = G.Sprite(G.text_w(kicker, 22, "light") + 4, 34, 0, 26)
    kick.text(0, 26, 22, kicker, G.GREY, "light")

    bg = G.background().convert("RGBA")
    n = int(round(LENGTH * G.FPS))
    bar_w = 380

    def frame(t):
        fr = bg.copy()
        a = G.ease_out((t - 0.12) / 0.45)                          # letters: fade from grey to white + settle
        if a > 0:
            lt = letters.resize((round(letters.width * (0.94 + 0.06 * a)), round(letters.height * (0.94 + 0.06 * a))), Image.BICUBIC)
            G.paste(fr, lt, cx, ly + letters.height / 2, a, ax=lt.width / 2, ay=lt.height / 2)
        d = G.back_out((t - 0.55) / 0.35, 1.4)                     # dot drops in from above
        if t > 0.55:
            G.paste(fr, dot, dot_x, dot_y - 90 * (1 - d), min(1, (t - 0.55) / 0.15))
        r = G.ease_in_out((t - 0.95) / 0.35)                        # red rule opens from the centre
        if r > 0:
            w = rule_w * r
            s = G.Sprite(w + 2, 6)
            s.rect(0, 0, w, 5, G.RED, 2)
            G.paste(fr, s.img, cx - w / 2, rule_y)
        G.paste(fr, net.img, cx - net.w / 2, 672 + 10 * (1 - G.ease_out((t - 1.15) / 0.3)), G.ease_out((t - 1.15) / 0.3), ay=34)
        h = G.ease_out((t - 1.4) / 0.4)
        G.paste(fr, head_img, cx - head_img.width / 2, 772 + 18 * (1 - h), h, ay=head_asc)
        G.paste(fr, kick.img, cx - kick.w / 2, 822, G.ease_out((t - 1.6) / 0.4) * 0.9, ay=26)
        arr = np.array(fr)
        w0 = LENGTH - WIPE                                         # red bar wipes left -> right; behind it: transparent
        if t >= w0:
            p = G.ease_in_out((t - w0) / WIPE)
            x1 = int(-bar_w + (G.W + bar_w) * p)                   # bar's left edge
            arr[:, :max(0, x1), 3] = 0
            arr[:, max(0, x1):max(0, min(G.W, x1 + bar_w))] = G.RED + (255,)
        return arr

    G.encode_prores((frame(i / G.FPS) for i in range(n)), out_dir / "intro.mov")
    Image.fromarray(frame(2.4)).save(out_dir / "intro_still.png")
    print(f"intro: {out_dir / 'intro.mov'} ({LENGTH:.1f} s, red wipe in the last {WIPE:.2f} s)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--headline")
    ap.add_argument("--date")
    ap.add_argument("--lang", default=None)
    ap.add_argument("--out", default=None, help="graphics folder (default: ../graphics)")
    a = ap.parse_args()
    here = Path.cwd()
    intro, _ = G.load_config(here)
    intro = dict(intro or {})
    if a.headline:
        intro["headline"] = a.headline
    if a.date:
        intro["date"] = a.date
    if not intro.get("headline") or not intro.get("date"):
        sys.exit('need INTRO = {"headline": ..., "date": "20 OCT 2026"} in project/cards.py, or --headline and --date')
    lang = a.lang or intro.get("lang")
    if not lang:
        import json
        edl = here / "edl.json"
        lang = json.loads(edl.read_text(encoding="utf8")).get("lang", "en") if edl.exists() else "en"
    build(intro["headline"], intro["date"], a.out or here.parent / "graphics", intro.get("network"), intro.get("kicker"), lang)


if __name__ == "__main__":
    main()
