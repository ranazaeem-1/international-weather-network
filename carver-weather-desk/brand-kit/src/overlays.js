// Builds one Carver overlay from window.DATA = {kind, dur, ...}. Rendered by pipeline/motion.py.
(function () {
  const D = window.DATA || {}; const root = document.getElementById("root");
  root.style.setProperty("--dur", (D.dur || 10) + "s");
  const esc = s => String(s == null ? "" : s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const amber = s => esc(s).replace(/\*([^*]+)\*/g, "<em>$1</em>");
  const em = (v = "white") => `<span class="emblem" data-v="${v}"></span>`;
  const H = html => { root.insertAdjacentHTML("beforeend", html); };
  const anim = (el, frames, opts) => el.animate(frames, Object.assign({ fill: "both" }, opts));

  // panel row used by wipes and the sting: [sky][crimson][navy][crimson][sky], skewed, moves right -> left
  function row(parent, scale, hold, total, keys) {
    const w = [40, 160, 2600, 60, 24].map(v => v * scale);
    const r = document.createElement("div"); r.className = "row";
    r.innerHTML = `<span style="width:${w[0]}px;background:var(--sky)"></span><span style="width:${w[1]}px;background:var(--crimson)"></span>` +
      `<span style="width:${w[2]}px;background:linear-gradient(90deg,#0A1B38,#071430 60%,#050C1A)"></span>` +
      `<span style="width:${w[3]}px;background:var(--crimson)"></span><span style="width:${w[4]}px;background:var(--sky)"></span>`;
    parent.appendChild(r);
    anim(r, keys.map(([o, x]) => ({ offset: o, left: x + "px", easing: "cubic-bezier(.72,0,.28,1)" })), { duration: total * 1000 });
    return r;
  }

  const K = D.kind;
  if (K === "bug") {
    H(`<div class="bug">${em("white")}<div class="wm"><b>CARVER</b><i>WEATHER DESK</i></div></div>`);
  } else if (K === "chrome") {
    H(`<div class="chrome"><div class="edge"></div><div class="topbar"></div></div>`);
  } else if (K === "chip") {
    H(`<div class="chip"><b>${esc(D.name || "GLENN CARVER")}</b><i>${esc(D.role || "REPORTING")}</i></div>`);
  } else if (K === "super") {
    H(`<div class="sup"><div class="n">${esc(D.name || "GLENN CARVER")}</div><div class="r">${esc(D.label || "CARVER WEATHER DESK")}</div></div>`);
  } else if (K === "strap") {
    const s = D.strap || {};
    H(`<div class="strap"><div class="kicker"><div class="tag"><span class="dot"></span>${esc(s.kicker || "WEATHER ALERT")}</div>` +
      (s.loc ? `<div class="loc">${esc(s.loc)}</div>` : "") + `</div><div class="main"><h1>${amber(s.head)}</h1>` +
      (s.sub ? `<p>${amber(s.sub)}</p>` : "") + `</div></div>`);
  } else if (K === "cta") {
    const ic = {
      subscribe: `<svg viewBox="0 0 54 54"><path d="M27 6c-8 0-13 6-13 14v9l-4 7v2h34v-2l-4-7v-9c0-8-5-14-13-14z" fill="#fff"/><circle cx="27" cy="44" r="5" fill="#fff"/><circle cx="40" cy="12" r="6" fill="#D7192F"/></svg>`,
      share: `<svg viewBox="0 0 54 54"><g class="plane"><path d="M6 26 L48 8 L36 46 L27 32 Z" fill="#fff"/><path d="M27 32 L48 8 L22 29 Z" fill="#5CC8FF"/></g></svg>`,
      comment: `<svg viewBox="0 0 54 54"><path d="M8 10h38a4 4 0 0 1 4 4v20a4 4 0 0 1-4 4H22l-10 8v-8H8a4 4 0 0 1-4-4V14a4 4 0 0 1 4-4z" fill="#fff"/><g class="dots" fill="#0A1B38"><circle cx="17" cy="24" r="3.5"/><circle cx="27" cy="24" r="3.5"/><circle cx="37" cy="24" r="3.5"/></g></svg>`,
    }[D.cta] || "";
    const act = { subscribe: ["SUBSCRIBE", "SUBSCRIBED &#10003;"], share: ["SHARE THIS REPORT", "SENT &#10003;"], comment: ["COMMENT", "WE READ THEM &#10003;"] }[D.cta] || ["", ""];
    H(`<div class="cta k-${esc(D.cta)}"><div class="ico">${ic}</div><div class="txt"><b>${esc(D.head)}</b><span>${esc(D.sub)}</span></div>` +
      `<div class="act"><span class="a1">${act[0]}</span><span class="a2">${act[1]}</span></div></div>`);
  } else if (K === "ticker_top") {
    H(`<div class="ticker top"><div class="badge">${em("white")}CARVER</div><div class="label">${esc(D.label || "THE LATEST")}</div>` +
      `<div class="run"></div><div class="clock">${esc(D.updated ? "UPDATED " + D.updated : "")}</div></div>`);
  } else if (K === "wipe_full") {
    const w = document.createElement("div"); w.className = "wipe full"; root.appendChild(w);
    const T = D.dur || 0.8;
    row(w, 1, 0, T, [[0, 2150], [0.42, -540], [0.58, -540], [1, -3200]]);
    const wm = document.createElement("div"); wm.className = "wm-c"; wm.innerHTML = em("white"); w.appendChild(wm);
    anim(wm, [{ offset: 0, opacity: 0 }, { offset: .42, opacity: .12 }, { offset: .58, opacity: .12 }, { offset: .7, opacity: 0 }, { offset: 1, opacity: 0 }], { duration: T * 1000 });
  } else if (K === "wipe_box") {
    const w = document.createElement("div"); w.className = "wipe box"; root.appendChild(w);
    const T = D.dur || 0.6, bw = D.w || 720, bh = D.h || 405, sc = bw / 1850;
    const skew = (bh * 1.4 / 2) * Math.tan(14 * Math.PI / 180), cov = -(skew + 200 * sc + 0.08 * bw);
    row(w, sc, 0, T, [[0, bw + skew + 10], [0.42, cov], [0.58, cov], [1, -(2884 * sc) - skew - 10]]);
  } else if (K === "sting") {
    const T = D.dur || 4.2; const ms = T * 1000;
    const w = document.createElement("div"); w.className = "wipe full"; root.appendChild(w);
    row(w, 1, 0, T, [[0, 2150], [0.13, -540], [0.82, -540], [1, -3200]]);
    // radar rings + glow behind the logo, visible while covered
    w.insertAdjacentHTML("beforeend", `<div class="sting-bg"></div><svg class="sting-rings" viewBox="0 0 1500 1500">` +
      [180, 330, 480, 630, 740].map(r => `<circle cx="750" cy="750" r="${r}" fill="none" stroke="rgba(92,200,255,.10)" stroke-width="2"/>`).join("") +
      `<line x1="0" y1="750" x2="1500" y2="750" stroke="rgba(92,200,255,.07)"/><line x1="750" y1="0" x2="750" y2="1500" stroke="rgba(92,200,255,.07)"/></svg>`);
    const bg = w.querySelector(".sting-bg"), rings = w.querySelector(".sting-rings");
    const vis = [{ offset: 0, opacity: 0 }, { offset: .12, opacity: 0 }, { offset: .2, opacity: 1 }, { offset: .76, opacity: 1 }, { offset: .84, opacity: 0 }, { offset: 1, opacity: 0 }];
    anim(bg, vis, { duration: ms }); anim(rings, vis, { duration: ms });
    anim(rings, [{ transform: "translate(-50%,-50%) rotate(0deg) scale(.9)" }, { transform: "translate(-50%,-50%) rotate(25deg) scale(1.05)" }], { duration: ms, composite: "replace" });
    // logo
    const L = document.createElement("div"); L.className = "sting-logo";
    L.innerHTML = `<svg class="em" viewBox="0 0 100 100"><defs><linearGradient id="sg" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#D7192F" stop-opacity=".85"/><stop offset="1" stop-color="#D7192F" stop-opacity="0"/></linearGradient></defs>` +
      `<path class="o" d="M 83.10 24.14 A 42 42 0 1 0 83.10 75.86" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round"/>` +
      `<path class="i" d="M 67.36 29.32 A 27 27 0 1 0 67.36 70.68" fill="none" stroke="#5CC8FF" stroke-width="6" stroke-linecap="round"/>` +
      `<g class="beam" style="transform-origin:50px 50px"><path d="M50 50 L 94.70 35.48 A 47 47 0 0 0 97 50 Z" fill="url(#sg)"/><line x1="50" y1="50" x2="97" y2="50" stroke="#D7192F" stroke-width="4.5" stroke-linecap="round"/></g>` +
      `<g class="dot" style="transform-origin:50px 50px"><circle cx="50" cy="50" r="8.5" fill="#D7192F"/><circle cx="50" cy="50" r="3.2" fill="#fff"/></g></svg>` +
      `<div class="wmk"><b>${"CARVER".split("").map(c => `<span>${c}</span>`).join("")}</b><div class="rule"></div><i>WEATHER DESK</i></div>` +
      `<div class="tagline">WITH GLENN CARVER</div>`;
    w.appendChild(L);
    const at = (s, d) => ({ delay: s * 1000, duration: d * 1000, easing: "cubic-bezier(.2,.8,.2,1)" });
    const o = L.querySelector(".o"), i = L.querySelector(".i");
    const lo = o.getTotalLength(), li = i.getTotalLength();
    o.style.strokeDasharray = lo; i.style.strokeDasharray = li;
    anim(o, [{ strokeDashoffset: lo }, { strokeDashoffset: 0 }], at(.55, .6));
    anim(i, [{ strokeDashoffset: li }, { strokeDashoffset: 0 }], at(.7, .55));
    anim(L.querySelector(".beam"), [{ transform: "rotate(-140deg)", opacity: 0 }, { transform: "rotate(0deg)", opacity: 1 }], at(.8, .6));
    anim(L.querySelector(".dot"), [{ transform: "scale(0)" }, { transform: "scale(1.25)", offset: .7 }, { transform: "scale(1)" }], at(1.1, .35));
    L.querySelectorAll(".wmk b span").forEach((s, k) => anim(s, [{ transform: "translateY(60px)", opacity: 0 }, { transform: "none", opacity: 1 }], at(1.0 + k * .055, .45)));
    anim(L.querySelector(".rule"), [{ transform: "scaleX(0)" }, { transform: "scaleX(1)" }], at(1.45, .45));
    anim(L.querySelector(".wmk i"), [{ opacity: 0, letterSpacing: ".9em" }, { opacity: 1, letterSpacing: ".46em" }], at(1.6, .6));
    anim(L.querySelector(".tagline"), [{ opacity: 0, transform: "translateY(10px)" }, { opacity: 1, transform: "none" }], at(2.05, .4));
    anim(L, [{ opacity: 1, transform: "translate(-50%,-52%) scale(1)" }, { opacity: 0, transform: "translate(-50%,-52%) scale(1.06)" }],
      { delay: (T - 0.95) * 1000, duration: 300, fill: "forwards", easing: "cubic-bezier(.6,0,.8,.25)" });
    anim(L, [{ opacity: 0 }, { opacity: 1 }], { duration: 1, delay: 500, fill: "backwards" });
  } else if (K === "end_bg") {
    H(`<div class="end-bg"></div><div class="end-grid"></div><div class="end-sweep"></div>` +
      `<div class="end-lock fadeup">${em("color")}<div><b>CARVER</b><i>WEATHER DESK</i></div></div>` +
      `<div class="end-foot fadeup" style="animation-delay:.6s">${esc(D.foot || "Always follow your local National Weather Service office and emergency officials.")}</div>`);
    const T = (D.dur || 30) * 1000;
    anim(root.querySelector(".end-grid"), [{ transform: "translate(0,0)" }, { transform: "translate(-80px,-80px)" }], { duration: T, easing: "linear" });
    anim(root.querySelector(".end-sweep"), [{ transform: "translate(-50%,-50%) rotate(0deg)" }, { transform: `translate(-50%,-50%) rotate(${(D.dur || 30) * 30}deg)` }], { duration: T, easing: "linear" });
  } else if (K === "end_fg") {
    H(`<div class="end-host fadeup"><div class="edge"></div><div class="topbar"></div></div>` +
      `<div class="slot-tag fadeup" style="left:1100px;top:100px;animation-delay:.25s"><b>${esc(D.slot1 || "WATCH NEXT")}</b></div>` +
      `<div class="slot fadeup" style="left:1100px;top:138px;animation-delay:.3s"></div>` +
      `<div class="slot-tag fadeup" style="left:1100px;top:562px;animation-delay:.45s"><b>${esc(D.slot2 || "LATEST ON THE DESK")}</b></div>` +
      `<div class="slot fadeup" style="left:1100px;top:600px;animation-delay:.5s"></div>` +
      `<div class="subslot fadeup" style="animation-delay:.7s"></div>` +
      `<div class="subtxt fadeup" style="animation-delay:.8s"><b>SUBSCRIBE</b><span>${esc(D.subline || "for the next update from the desk")}</span></div>`);
  } else if (K === "end_plate") {
    H(`<div class="plate"><span class="emblem" data-v="color"></span><b>SEE YOU AT THE NEXT UPDATE</b><i>CARVER WEATHER DESK</i></div>`);
  }
  if (window.CWD) CWD.mount();
  document.fonts.ready.then(() => { window.READY = true; });
})();
