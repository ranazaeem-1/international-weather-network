# Carver Weather Desk: brand kit

Owner decisions (4 Nov 2026):
- **Host frame A, the Desk Window.** A rectangle at the top right: **x 1160, y 40, 720×405**, with a crimson/sky top bar and a thin border.
  - **No text labels** (owner, 4 Nov: the "WEATHER DESK" tag and the "GLENN CARVER | REPORTING" chip are removed; so is the end-screen name chip).
  - The crop is wide: head, shoulders and chest, with the studio behind him.
  - The circle (C) is rejected and the breakout cut-out (B) is not used.
- **Glenn on screen.** Not full-screen at the start, and full-screen rarely.

**Colour, type and logo.** These are in `tokens.json`, `src/brand.css` and the logo sheet `logo/_logo_sheet.png`.
- Colours: navy plus alert crimson (Glenn's tie), radar sky and warning amber.
- Fonts: Barlow Condensed 800 for headlines, Inter for body text and the ticker.
- Emblem: a radar-scope "C".

**Overlays** come from `src/overlays.html`, `src/overlays.css` and `src/overlays.js`, rendered by `pipeline/motion.py`. They are the bug, box chrome, name chip, full-host super, headline strap, CTA cards, ticker, wipes, the intro sting and the end screen.
- Brand-level renders: `graphics/` and `motion/` (`pipeline/make_brand_motion.py`).
- Sound: `sfx/` (procedural).

**Cards:** `pipeline/cards/` (see `docs/cards.md`).

**Style frames:**
- `styleframes/sf_A.png`, `sf_M.png`, `sf_F.png`. B and C are kept only for the record.
- Motion previews: `styleframes/motion/`.
- Cards: `styleframes/cards/`.
