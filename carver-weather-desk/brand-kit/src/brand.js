// Carver Weather Desk — shared SVG marks. Usage: <span class="emblem" data-v="color|white|mono"></span>
const CWD = {
  // Emblem: a radar scope shaped like a "C" — two range rings open to the right,
  // a crimson sweep beam leaving through the opening, and a storm cell at the centre.
  emblem(v = "color") {
    const ring = v === "mono" ? "#0A1B38" : "#FFFFFF";
    const inner = v === "color" ? "#5CC8FF" : ring;
    const red = v === "white" ? "#FFFFFF" : "#D7192F";
    const a = (deg, r) => [50 + r * Math.cos(deg * Math.PI / 180), 50 - r * Math.sin(deg * Math.PI / 180)];
    const arc = (r, gap) => { const [x1, y1] = a(gap, r), [x2, y2] = a(-gap, r);
      return `M ${x1.toFixed(2)} ${y1.toFixed(2)} A ${r} ${r} 0 1 0 ${x2.toFixed(2)} ${y2.toFixed(2)}`; };
    return `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="sw${v}" x1="0" y1="1" x2="0" y2="0">
        <stop offset="0" stop-color="${red}" stop-opacity=".85"/><stop offset="1" stop-color="${red}" stop-opacity="0"/></linearGradient></defs>
      <path d="${arc(42, 38)}" fill="none" stroke="${ring}" stroke-width="9" stroke-linecap="round"/>
      <path d="${arc(27, 50)}" fill="none" stroke="${inner}" stroke-width="6" stroke-linecap="round" opacity=".95"/>
      <path d="M50 50 L ${a(18, 47).map(n => n.toFixed(2)).join(" ")} A 47 47 0 0 0 ${a(0, 47).map(n => n.toFixed(2)).join(" ")} Z" fill="url(#sw${v})"/>
      <line x1="50" y1="50" x2="97" y2="50" stroke="${red}" stroke-width="4.5" stroke-linecap="round"/>
      <circle cx="50" cy="50" r="8.5" fill="${red}"/><circle cx="50" cy="50" r="3.2" fill="${v === "white" ? "#0A1B38" : "#FFFFFF"}"/>
    </svg>`;
  },
  mount() { document.querySelectorAll(".emblem").forEach(el => { el.innerHTML = CWD.emblem(el.dataset.v || "color"); }); },
};
document.addEventListener("DOMContentLoaded", () => CWD.mount());
