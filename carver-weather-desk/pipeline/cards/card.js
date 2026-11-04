// Carver Weather Desk: card runtime shared by pipeline/cards/<type>.html
// Spec source, in order: window.CARD (injected) | ?json=<urlencoded JSON> | ?spec=<URL of a JS file that sets window.CARD>
// (make_card.py writes the resolved spec to a temp spec.js and passes ?spec=<file URI>).
// All motion is a pure function of t: window.seek(t) is called per frame by render_html.py, so renders are
// deterministic. No CSS animations/transitions are used. Opened in a normal browser, the card plays in real time.
window.cardReady = false;
function cardSpecSource() {   // resolves when window.CARD is set
  const q = new URLSearchParams(location.search);
  if (window.CARD) return Promise.resolve();
  if (q.get("json")) { window.CARD = JSON.parse(q.get("json")); return Promise.resolve(); }
  if (!q.get("spec")) return Promise.resolve();
  return new Promise((res, rej) => { const sc = document.createElement("script"); sc.src = q.get("spec");
    sc.onload = res; sc.onerror = () => rej(new Error("could not load spec " + q.get("spec"))); document.head.appendChild(sc); });
}

const CW = (() => {
  const PAL = { crimson: "#D7192F", amber: "#FFB51F", sky: "#5CC8FF", royal: "#1C4FD0", steel: "#93A3BF", white: "#FFFFFF",
    paper: "#E9EEF7", navy: "#0A1B38", navy2: "#10295A", ink: "#050C1A", crimson_dk: "#9E0F22" };
  // semantic names -> palette (warnings crimson, watches amber, info sky)
  const KIND = { warning: "crimson", severe: "crimson", high: "crimson", major: "crimson", watch: "amber", elevated: "amber",
    moderate: "amber", minor: "amber", advisory: "sky", info: "sky", low: "sky", none: "steel", neutral: "steel" };
  const color = (c, dflt = "sky") => { c = c || dflt; c = KIND[c] || c; return PAL[c] || c; };
  const darkText = c => ["#FFB51F", "#5CC8FF", "#FFFFFF", "#E9EEF7"].includes(color(c).toUpperCase());

  function bez(x1, y1, x2, y2) {
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx, cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const sx = t => ((ax * t + bx) * t + cx) * t, sy = t => ((ay * t + by) * t + cy) * t, dx = t => (3 * ax * t + 2 * bx) * t + cx;
    return x => {
      if (x <= 0) return 0; if (x >= 1) return 1;
      let t = x;
      for (let i = 0; i < 8; i++) { const e = sx(t) - x; if (Math.abs(e) < 1e-6) return sy(t); const d = dx(t); if (Math.abs(d) < 1e-6) break; t -= e / d; }
      let lo = 0, hi = 1; t = x;
      for (let i = 0; i < 40; i++) { if (sx(t) < x) lo = t; else hi = t; t = (lo + hi) / 2; }
      return sy(t);
    };
  }
  const E = { out: bez(.2, .8, .2, 1), inout: bez(.45, 0, .2, 1), sine: bez(.37, 0, .63, 1), lin: t => t, cubic: t => 1 - Math.pow(1 - t, 3) };
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, p) => a + (b - a) * p;
  const mix = (c1, c2, p) => { const h = c => [1, 3, 5].map(i => parseInt(color(c).slice(i, i + 2), 16)); const a = h(c1), b = h(c2);
    return `rgb(${a.map((v, i) => Math.round(lerp(v, b[i], p))).join(",")})`; };

  // ---------- timeline ----------
  const tl = [], loops = [];
  let end = 0;
  function tween(at, dur, fn, ease = E.out, entrance = true) {
    tl.push({ at, dur: Math.max(dur, 1e-3), fn, ease });
    if (entrance) end = Math.max(end, at + dur);
  }
  const loop = fn => loops.push(fn);
  function seek(t) { for (const w of tl) w.fn(w.ease(clamp((t - w.at) / w.dur)), t); for (const f of loops) f(t); }
  // entrance: rise/slide + fade, 0.55 s, cubic-bezier(.2,.8,.2,1)
  function enter(node, at, o = {}) {
    const dur = o.dur ?? .55, x = o.x ?? 0, y = o.y ?? 18, s0 = o.scale, base = o.base || "";
    tween(at, dur, p => {
      node.style.opacity = p;
      node.style.transform = `${base} translate(${(x * (1 - p)).toFixed(2)}px, ${(y * (1 - p)).toFixed(2)}px)` + (s0 ? ` scale(${lerp(s0, 1, p)})` : "");
    }, o.ease || E.out);
  }
  // wipe: left-to-right clip reveal (kicker chips, rails)
  function wipe(node, at, o = {}) {
    const dur = o.dur ?? .5;
    tween(at, dur, p => { node.style.clipPath = `inset(-20px ${((1 - p) * 100).toFixed(2)}% -20px -20px)`; node.style.opacity = p > 0 ? 1 : 0; }, o.ease || E.out);
  }

  // ---------- DOM helpers ----------
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const rich = s => esc(s).replace(/\*([^*]+)\*/g, "<em>$1</em>").replace(/\n/g, "<br>");   // *word* = amber emphasis
  function el(tag, cls, html, parent) { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; if (parent) parent.appendChild(e); return e; }
  function svgEl(tag, attrs, parent) { const e = document.createElementNS("http://www.w3.org/2000/svg", tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
  const decimalsOf = v => { const s = String(v); const i = s.indexOf("."); return i < 0 ? 0 : s.length - i - 1; };
  function fmt(v, dec = 0, sep = true) {
    let s = Math.abs(v).toFixed(dec);
    if (sep) { const [i, f] = s.split("."); s = i.replace(/\B(?=(\d{3})+(?!\d))/g, ",") + (f ? "." + f : ""); }
    return (v < 0 && Number(s.replace(/,/g, "")) !== 0 ? "−" : "") + s;
  }
  // count-up: the node keeps the final text width (right-aligned) so nothing next to it shifts
  function countUp(node, value, at, o = {}) {
    const v = Number(value), dec = o.decimals ?? decimalsOf(value), dur = o.dur ?? 1.2, from = o.from ?? 0, sep = o.sep ?? true;
    node.textContent = fmt(v, dec, sep);
    node.style.display = "inline-block"; node.style.textAlign = o.align || "right";
    node.style.minWidth = Math.ceil(node.getBoundingClientRect().width + 1) + "px";
    tween(at, dur, p => { node.textContent = fmt(lerp(from, v, p), dec, sep); }, o.ease || E.cubic);
  }
  // shrink a container's --k until its bottom edge is <= maxBottom (fonts/paddings in card.css use var(--k))
  function fit(node, maxBottom, o = {}) {
    let k = o.k0 ?? 1; const min = o.min ?? .62, maxRight = o.maxRight ?? 1e9;
    node.style.setProperty("--k", k);
    for (let i = 0; i < 60; i++) {
      const r = node.getBoundingClientRect();
      if ((r.bottom <= maxBottom && r.right <= maxRight) || k <= min) break;
      k = Math.max(min, k - .025); node.style.setProperty("--k", k.toFixed(3));
    }
    if (node.getBoundingClientRect().bottom > maxBottom + 1) console.warn(`fit: content still ends at y=${node.getBoundingClientRect().bottom | 0} (limit ${maxBottom}); shorten the copy`);
    return k;
  }
  const limit = S => S.strap_clear ? 800 : 1000;   // content bottom for x < 1320

  // ---------- shared blocks ----------
  function title(T, parent, o = {}) {
    if (!T) return null;
    const box = el("div", "cardtitle zc", null, parent);
    const at = T.at ?? o.at ?? .1; let i = 0;
    if (T.kicker) { const k = el("span", "k", esc(T.kicker), box); wipe(k, at, { dur: .5 }); i++; }
    if (T.h2) { const h = el("h2", null, rich(T.h2), box); enter(h, at + .1 * i, { y: 22 }); i++; }
    if (T.sub) { const p = el("p", null, rich(T.sub), box); enter(p, at + .1 * i, { y: 14 }); }
    return box;
  }
  function legend(L, parent, o = {}) {
    if (!L || !L.length) return null;
    const box = el("div", "legend", null, parent);
    const at = o.at ?? .6;
    L.forEach((it, i) => {
      const d = el("div", "zc", `<span style="background:${color(it.color || it.kind)}"></span>${esc(it.label)}`, box);
      enter(d, it.at ?? at + .08 * i, { y: 10, dur: .45 });
    });
    return box;
  }
  function statBox(st, parent, o = {}) {
    if (!st) return null;
    const box = el("div", "stat zc", null, parent);
    if (st.right != null || st.bottom != null || !o.noPos) { box.style.right = (st.right ?? 60) + "px"; box.style.bottom = (st.bottom ?? 100) + "px"; }
    const at = st.at ?? .8;
    el("small", null, esc(st.label), box);
    const strong = el("strong", null, `${st.prefix ? esc(st.prefix) : ""}<b class="cv"></b>${st.unit ? `<sub>${esc(st.unit)}</sub>` : ""}`, box);
    if (st.sub) el("span", null, rich(st.sub), box);
    strong.querySelector(".cv").style.fontWeight = "inherit";
    countUp(strong.querySelector(".cv"), st.value, at + .15, { decimals: st.decimals, dur: st.count_dur ?? 1.1 });
    enter(box, at, { y: 24 });
    return box;
  }
  // animated navy (drifting radar grid + slow sweep) or a blurred, darkened footage still
  function background(S, stage) {
    const wrap = el("div", "cbg", null, stage);
    const z = S.bg_zoom || [1.04, 1.1];
    if (S.bg_image) {
      const im = el("div", "bgimg", null, wrap); im.style.backgroundImage = `url("${S.bg_image}")`;
      el("div", "bgtint", null, wrap);
      const g = el("div", "grid faint", null, wrap);
      loop(t => { im.style.transform = `scale(${lerp(z[0], z[1], clamp(t / S.dur)).toFixed(5)})`; g.style.transform = `translate(${(-(t * 9) % 240).toFixed(2)}px, ${(-(t * 5) % 240).toFixed(2)}px)`; });
    } else {
      const nb = el("div", "navybg", null, wrap);
      const g = el("div", "grid", null, nb);
      const rings = svgEl("svg", { class: "rings", width: 1920, height: 1080, viewBox: "0 0 1920 1080" }, nb);
      for (const r of [260, 520, 780, 1040]) svgEl("circle", { cx: 1460, cy: 640, r, fill: "none", stroke: "rgba(92,200,255,.07)", "stroke-width": 2 }, rings);
      const sw = el("div", "sweep", null, nb);
      el("div", "vig", null, nb);
      loop(t => {
        g.style.transform = `translate(${(-(t * 9) % 240).toFixed(2)}px, ${(-(t * 5) % 240).toFixed(2)}px)`;
        sw.style.transform = `rotate(${(t * 16 + 200).toFixed(2)}deg)`;
      });
    }
    return wrap;
  }

  // ---------- projections (lon/lat -> natural image px) ----------
  const G = { REQ: 6378137, RPOL: 6356752.31414, H: 42164160, L0: -75.2, XMIN: -0.101346, XMAX: 0.038626, YMAX: 0.128226, YMIN: 0.044254 };
  function goesScan(lat, lon) {   // same maths as pipeline/goes_px.py and brand-kit/src/sf.html (verified)
    const d = Math.PI / 180, la = lat * d, lo = (lon - G.L0) * d, e2 = 1 - G.RPOL * G.RPOL / (G.REQ * G.REQ);
    const pc = Math.atan(G.RPOL * G.RPOL / (G.REQ * G.REQ) * Math.tan(la));
    const rc = G.RPOL / Math.sqrt(1 - e2 * Math.cos(pc) ** 2);
    const sx = G.H - rc * Math.cos(pc) * Math.cos(lo), sy = -rc * Math.cos(pc) * Math.sin(lo), sz = rc * Math.sin(pc);
    return [Math.asin(-sy / Math.hypot(sx, sy, sz)), Math.atan(sz / sx)];
  }
  function projector(P, W, H) {
    const t = (P && P.type) || "goes_conus";
    if (t === "goes_conus") return (lon, lat) => { const [x, y] = goesScan(lat, lon); return [(x - G.XMIN) / (G.XMAX - G.XMIN) * W, (G.YMAX - y) / (G.YMAX - G.YMIN) * H]; };
    const [a, b, c, d] = P.bbox;
    if (t === "linear") return (lon, lat) => [(lon - a) / (c - a) * W, (d - lat) / (d - b) * H];
    if (t === "mercator") { const my = la => Math.log(Math.tan(Math.PI / 4 + la * Math.PI / 360)); return (lon, lat) => [(lon - a) / (c - a) * W, (my(d) - my(lat)) / (my(d) - my(b)) * H]; }
    throw new Error("unknown projection " + t);
  }
  // lon/lat ring -> SVG path data in screen px, densified so long edges follow the projection
  function ringPath(ring, scr, close = true) {
    let d = "", prev = null;
    const push = (lon, lat, first) => { const [x, y] = scr(lat, lon); d += (first ? "M" : "L") + x.toFixed(1) + " " + y.toFixed(1); };
    ring.forEach(([lon, lat], i) => {
      if (prev) { const n = Math.ceil(Math.max(Math.abs(lon - prev[0]), Math.abs(lat - prev[1])) / .5); for (let j = 1; j < n; j++) push(lerp(prev[0], lon, j / n), lerp(prev[1], lat, j / n), false); }
      push(lon, lat, i === 0); prev = [lon, lat];
    });
    return d + (close ? "Z" : "");
  }
  function smoothPath(pts) {   // Catmull-Rom through points -> cubic Beziers
    if (pts.length < 3) return "M" + pts.map(p => p.map(v => v.toFixed(1)).join(" ")).join(" L");
    let d = `M${pts[0][0].toFixed(1)} ${pts[0][1].toFixed(1)}`;
    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2;
      const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6], c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
      d += ` C${c1.map(v => v.toFixed(1))} ${c2.map(v => v.toFixed(1))} ${p2.map(v => v.toFixed(1))}`;
    }
    return d;
  }

  // ---------- reserved-zone report (read by render_html.py -> make_card.py) ----------
  function zoneCheck(S) {
    const Z = [{ n: "host box", x0: 1130, y0: 0, x1: 1920, y1: 475 }, { n: "bug", x0: 0, y0: 0, x1: 420, y1: 120 }, { n: "ticker", x0: 0, y0: 1014, x1: 1920, y1: 1080 }];
    if (S.strap_clear) Z.push({ n: "strap", x0: 0, y0: 820, x1: 1320, y1: 1014 });
    const out = new Set();
    for (const t of [end + .05, S.dur - .01]) {
      seek(t);
      document.querySelectorAll(".zc").forEach(e => {
        const r = e.getBoundingClientRect(); if (r.width < 1 || r.height < 1) return;
        const what = `${e.className.replace(/\bzc\b/, "").trim() || e.tagName.toLowerCase()} "${(e.textContent || "").trim().replace(/\s+/g, " ").slice(0, 36)}" [${r.left | 0},${r.top | 0} -> ${r.right | 0},${r.bottom | 0}]`;
        if (r.right < 0 || r.left > 1920 || r.bottom < 0 || r.top > 1080) { out.add("off-frame: " + what); return; }
        for (const z of Z) if (r.left < z.x1 - .5 && r.right > z.x0 + .5 && r.top < z.y1 - .5 && r.bottom > z.y0 + .5) out.add(`${z.n}: ${what}`);
      });
    }
    return [...out];
  }

  const FONTS = ['500 20px "Barlow Condensed"', '600 20px "Barlow Condensed"', '700 20px "Barlow Condensed"', '800 20px "Barlow Condensed"',
    '400 20px Inter', '500 20px Inter', '600 20px Inter', '700 20px Inter'];
  function boot(build) {
    const go = async () => {
      try {
        await cardSpecSource();
        const S = window.CARD;
        if (!S) throw new Error("no card spec: set window.CARD, ?json=<spec> or ?spec=<spec.js URL>");
        await Promise.all(FONTS.map(f => document.fonts.load(f)));
        document.body.classList.toggle("strap-clear", !!S.strap_clear);
        if (S._alpha) document.documentElement.classList.add("alpha");   // root must be transparent too
        await build(S, document.getElementById("stage"));
        await document.fonts.ready;
        window.cardEnd = end;
        window.cardZones = zoneCheck(S);
        window.seek = seek;
        seek(0);
        window.cardReady = true;
        if (!navigator.webdriver) { const t0 = performance.now(); const tick = () => { seek(((performance.now() - t0) / 1000) % S.dur); requestAnimationFrame(tick); }; requestAnimationFrame(tick); }
      } catch (e) { window.cardError = String((e && e.stack) || e); console.error(e); }
    };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", go); else go();
  }
  const loadImg = src => new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = () => rej(new Error("image failed: " + src)); i.src = src; });

  return { PAL, color, darkText, E, bez, clamp, lerp, mix, tween, loop, seek, enter, wipe, esc, rich, el, svgEl, fmt, decimalsOf, countUp, fit, limit,
    title, legend, statBox, background, projector, ringPath, smoothPath, boot, loadImg, get end() { return end; } };
})();
