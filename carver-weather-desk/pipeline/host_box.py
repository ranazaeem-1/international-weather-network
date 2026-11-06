"""Desk Window looks + the on/off rhythm (owner, 6 Nov 2026).

The owner's notes: the window is not on screen all the time. It shows for a while, goes off, comes back ("like mix").
Each time it comes back it can be a different size and sometimes a different place.
  main  640x360, crop 4.6x face width: head to upper chest, the most common look. Owner 6 Nov: 720x405 "still large,
        a little smaller" -> 640x360; then "a little cropped so his hands don't show when he is talking" -> 4.6x
        (was 6.2x, head to waist). A/B/C each moved one step down in size and crop so main stays the biggest/widest
  A     608x342, crop 4.2x: head, collar, tie knot
  B     576x324, crop 3.8x: head and shoulders
  C     544x306, crop 3.5x: head, top of the shoulders
Every look cuts above the hands (the lowest cut, main, ends at about 72% of the frame height on the studio framing). Positions: TR top right (default), TL top left under the bug, BR bottom right above the ticker.
Rules the scheduler keeps:
  - every section starts with the window ON (Glenn opens the section); the video opens on main TR
  - every card/map gets the full frame first: window OFF for its first 5 s (this beats the section-start rule)
  - ON 10-17 s, OFF 7-13 s, in a fixed pattern; no ON shorter than 5 s, no OFF shorter than 4 s
  - CTA cards sit under main TR, so the window is ON as main TR for every CTA
  - over a card or map the window stays top right (cards keep that corner clear); other spots only over footage
  - no window change during the intro sting or within 0.8 s of a layout wipe
Used by prep_host (crops), make_brand_motion (chrome + wipe per size) and plan_edit (schedule).
"""
PRESETS = {               # window size on the 1920x1080 frame; crop = crop width as a multiple of Glenn's face width
    "main": {"w": 640, "h": 360, "crop": 4.6},
    "A": {"w": 608, "h": 342, "crop": 4.2},
    "B": {"w": 576, "h": 324, "crop": 3.8},
    "C": {"w": 544, "h": 306, "crop": 3.5},
}
MARGIN, TL_Y, TICKER_Y, TICKER_GAP = 40, 128, 1014, 28      # TL_Y: below the bug (bug ends at y 103)
CHROME_PAD = (84, 64, 84, 106)     # l, t, r, b: the window's drop shadow (0 22px 54px) around the box
CHROME_AT = (200, 200)             # where the chrome PNG is drawn when rendered (inside the canvas with its shadow)

# (preset, position) for each window appearance after the opening one (which is main TR). The first one is a small look
# somewhere else so the mix shows early; main ~40% overall; never the same look twice in a row.
STYLE_SEQ = [("B", "TL"), ("main", "TR"), ("A", "BR"), ("C", "TR"), ("main", "TL"), ("B", "BR"), ("main", "TR"), ("A", "TL"),
             ("C", "BR"), ("main", "TR"), ("B", "TR"), ("A", "TR"), ("main", "BR"), ("C", "TL"), ("main", "TR")]
# Window transitions (owner 6 Nov: "I like the animation, add other animations too"). Every on/off uses one, rotating.
#   cover: a 0.6 s alpha overlay at the window rect hides the switch (covered 0.25-0.35 s, switch at 0.30 s)
#   move:  the window itself animates (position / opacity keyframes on the host + chrome items; MP4 and CapCut alike)
FX = {
    "panel": {"type": "cover", "sfx": "whoosh_small"},   # the original skewed panel sweep (the one the owner liked)
    "radar": {"type": "cover", "sfx": "ping"},           # radar-scope disc + rotating beam closes, then opens
    "doors": {"type": "cover", "sfx": "whoosh_small"},   # two navy doors with crimson edges meet (emblem flash), open
    "blinds": {"type": "cover", "sfx": "whoosh_small"},  # six slats slice across right -> left
    "slide": {"type": "move", "sfx": "whoosh_small"},    # slides in from the nearest screen edge, out the same way
    "rise": {"type": "move", "sfx": "tick"},             # fades in while rising 36 px; fades out sinking 24 px
}
FX_SEQ = ["panel", "slide", "radar", "rise", "doors", "panel", "blinds", "slide", "radar", "panel", "rise", "doors",
          "blinds", "panel"]                             # panel ~30%; never the same transition twice in a row
SLIDE_IN, SLIDE_OUT, RISE_IN, RISE_OUT, FADE = 0.45, 0.40, 0.40, 0.30, 0.30

ON_SEC = [14, 11, 17, 12, 15, 10]
OFF_SEC = [9, 12, 7, 10, 13, 8]
FIRST_ON, CARD_LAND, MIN_ON, MIN_OFF, CLEAR = 5.0, 5.0, 5.0, 4.0, 0.8


def rect(preset, pos="TR"):
    w, h = PRESETS[preset]["w"], PRESETS[preset]["h"]
    x = 1920 - MARGIN - w if pos in ("TR", "BR") else MARGIN
    y = {"TR": MARGIN, "TL": TL_Y, "BR": TICKER_Y - TICKER_GAP - h}[pos]
    return [x, y, w, h]


def cta_rect():
    """CTA card: right under main TR, same left edge and width -> (x, y, w) and its render clip (room for the slide-in)."""
    x, y, w, h = rect("main", "TR"); cy = y + h + 22
    return (x, cy, w), [x - 40, cy - 27, 1920 - (x - 40), 260]


def host_src(preset):
    return "host/host_box.mp4" if preset == "main" else f"host/host_box_{preset}.mp4"


def chrome_src(preset):
    return f"brand-kit/graphics/box_chrome_{preset}.png"


def wipe_src(preset, fx="panel"):
    """Cover overlay for this window size: panel = wipe_box_<look>.mov, others box_<fx>_<look>.mov."""
    return f"brand-kit/motion/wipe_box_{preset}.mov" if fx == "panel" else f"brand-kit/motion/box_{fx}_{preset}.mov"


def _ease(a, b, T, t0, out=True, n=6):
    """[[t, v]] samples of a cubic ease (out = decelerate, else accelerate) from a to b over T s starting at t0."""
    ks = []
    for i in range(n + 1):
        u = i / n; e = 1 - (1 - u) ** 3 if out else u ** 3
        ks.append([round(t0 + u * T, 4), round(a + (b - a) * e, 2)])
    return ks


def move_keys(fx, preset, pos, dur, do_in, do_out):
    """Keyframes for a 'move' transition, relative to the item start: {"kf_x"|"kf_y": [[t, px offset]], "alpha_in"|"alpha_out": s}.
    Applied identically to the host item and its chrome item, so they move as one."""
    k = {}
    x, y, w, h = rect(preset, pos)
    if fx == "slide":
        off = (1920 - x + 100) if pos in ("TR", "BR") else -(x + w + 100)     # fully off screen, shadow included
        ks = (_ease(off, 0, SLIDE_IN, 0.0, True) if do_in else []) + (_ease(0, off, SLIDE_OUT, dur - SLIDE_OUT, False) if do_out else [])
        if ks:
            k["kf_x"] = ks
    elif fx == "rise":
        ks = (_ease(36, 0, RISE_IN, 0.0, True) if do_in else []) + (_ease(0, 24, RISE_OUT, dur - RISE_OUT, False) if do_out else [])
        if ks:
            k["kf_y"] = ks
        if do_in:
            k["alpha_in"] = FADE
        if do_out:
            k["alpha_out"] = FADE
    return k


def chrome_rect(preset, pos):
    x, y, w, h = rect(preset, pos); l, t, r, b = CHROME_PAD
    return [x - l, y - t, w + l + r, h + t + b]


def chrome_clip(preset):
    """Screenshot clip for rendering the chrome PNG of this size at CHROME_AT."""
    w, h = PRESETS[preset]["w"], PRESETS[preset]["h"]; l, t, r, b = CHROME_PAD
    return [CHROME_AT[0] - l, CHROME_AT[1] - t, w + l + r, h + t + b]


def _runs(st):
    out, i = [], 0
    while i < len(st):
        j = i
        while j < len(st) and st[j] == st[i]:
            j += 1
        out.append((i, j, st[i])); i = j
    return out


def schedule(runs, fps, starts=(), forced=(), busy=(), cards=(), seed=0):
    """Plan the window's appearances.
    runs    [(a, b)] output-time spans where the layout is 'box' (window allowed)
    starts  section start times (window ON for FIRST_ON s)
    forced  [(a, b)] spans that must show main TR (CTA cards)
    busy    [(a, b)] spans where the window must not switch (sting, layout wipes)
    cards   [(a, b)] spans with a card/map as the base (window stays top right)
    Returns [{"t0", "t1", "preset", "pos", "forced"}], frame-exact, in time order."""
    F = lambda t: int(round(t * fps))
    pieces, k_on, k_off = [], 0, 0
    for a, b in runs:
        n0, n1 = F(a), F(b); N = n1 - n0
        if N <= 0:
            continue
        st = [False] * N; fm = [False] * N
        i, on = 0, True                                       # 1. the rhythm: ON, OFF, ON, ...
        while i < N:
            L = F(ON_SEC[k_on % len(ON_SEC)] if on else OFF_SEC[k_off % len(OFF_SEC)])
            k_on, k_off = (k_on + 1, k_off) if on else (k_on, k_off + 1)
            for j in range(i, min(N, i + L)):
                st[j] = on
            i += L; on = not on
        for s in starts:                                      # 2a. sections open on Glenn
            if a - 1e-6 <= s < b:
                for j in range(max(0, F(s) - n0), min(N, F(s) - n0 + F(FIRST_ON))):
                    st[j] = True
        for c0, _ in cards:                                   # 2b. ...unless a card/map opens it: the card lands full frame
            if a - 1e-6 <= c0 < b:
                for j in range(max(0, F(c0) - n0), min(N, F(c0) - n0 + F(CARD_LAND))):
                    st[j] = False
        for f0, f1 in forced:                                 # 3. CTA spans
            for j in range(max(0, F(f0) - n0), min(N, F(f1) - n0)):
                st[j] = fm[j] = True

        def clean():
            for _ in range(20):
                changed = False
                for i0, i1, v in _runs(st):
                    L = (i1 - i0) / fps
                    if not v and L < MIN_OFF:                 # short gap: keep the window up
                        st[i0:i1] = [True] * (i1 - i0); changed = True; break
                    if v and L < MIN_ON and not any(fm[i0:i1]) and not (i0 == 0 and any(abs(F(s) - n0) <= 1 for s in starts)):
                        st[i0:i1] = [False] * (i1 - i0); changed = True; break
                if not changed:
                    return
        clean()
        for u0, u1 in busy:                                   # 4. no switch under the sting / near a layout wipe
            j0, j1 = max(1, F(u0 - CLEAR) - n0), min(N, F(u1 + CLEAR) - n0)
            if j0 < j1 and any(st[j] != st[j - 1] for j in range(j0, j1)):
                v = st[j0 - 1]
                for j in range(j0, j1):
                    if not fm[j]:
                        st[j] = v
        clean()
        for i0, i1, v in _runs(st):
            if v:
                pieces.append({"t0": round((n0 + i0) / fps, 4), "t1": round((n0 + i1) / fps, 4), "forced": any(fm[i0:i1]),
                               "run_start": i0 == 0, "run_end": i1 == N})
    k, prev = seed % len(STYLE_SEQ), None
    for n, p in enumerate(pieces):
        on_card = any(c0 < p["t1"] - 1e-3 and c1 > p["t0"] + 1e-3 for c0, c1 in cards)
        if n == 0 or p["forced"]:
            style = ("main", "TR")
        else:
            for _ in range(len(STYLE_SEQ)):
                style = STYLE_SEQ[k % len(STYLE_SEQ)]; k += 1
                if on_card:
                    style = (style[0], "TR")
                if style != prev:
                    break
        p["preset"], p["pos"] = style; prev = style
    for n, p in enumerate(pieces):                            # transitions rotate through FX_SEQ (in and out share one)
        p["fx"] = FX_SEQ[n % len(FX_SEQ)]
    return pieces
