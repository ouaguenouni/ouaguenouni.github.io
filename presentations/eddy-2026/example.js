(function () {
  "use strict";
  const slide = document.getElementById("borda-example");
  const root = document.getElementById("illustrative-example");
  const profile = window.EDDY_DATA.winnerProfile;
  const alternatives = window.EDDY_DATA.alternatives;
  const total = 20;
  const counts = profile.map(row => Math.round(row.weight * total));
  const fmt = n => String(Number(n.toFixed(2)));
  const probabilities = Object.fromEntries(alternatives.map(a => [a, [0, 1, 2].map(rank =>
    profile.reduce((sum, row) => sum + (row.order[rank] === a ? row.weight : 0), 0))]));
  // Interleave repeated rankings so the grouping is a visible operation.
  const people = [];
  for (let round = 0; round < Math.max(...counts); round++) {
    profile.forEach((row, i) => { if (round < counts[i]) people.push(row.order); });
  }
  const orderMarkup = order => [...order].map((a, i) =>
    `${i ? '<span class="example-relation">≻</span>' : ''}<span class="example-letter" data-alternative="${a}" data-rank="${i}">${a}</span>`).join("");
  root.innerHTML = `<div class="example-profile"><h3 class="example-profile-title">People’s rankings</h3>
    <div class="example-people">${people.map((order, i) => `<div class="example-person" data-order="${order}"><span class="example-person-index">${i + 1}</span><span class="example-order">${order.split("").join(" ≻ ")}</span></div>`).join("")}</div>
    <div class="example-grouped"><div class="example-table-head"><span>Ranking</span><span class="example-mass-title">Count</span></div>
    ${profile.map((row, i) => `<div class="example-profile-row" data-order="${row.order}"><span class="example-order">${orderMarkup(row.order)}</span><span class="example-mass" data-row="${i}">${counts[i]}</span></div>`).join("")}
    <div class="example-total example-reveal"><span>Total</span><strong>${total}</strong></div></div></div>
    <div class="example-histograms example-reveal" data-show="4"><h3>Rank distributions</h3>
    ${alternatives.map((a, i) => `<div class="example-hist-row example-reveal" data-show="${i ? 8 : 5}" data-alternative="${a}"><strong class="example-alt">${a}</strong><div class="example-hist" role="img" aria-label="Rank distribution of ${a}">
      ${probabilities[a].map((p, r) => `<div class="example-bin" data-rank="${r}" style="--probability:${p}"><div class="example-bar example-reveal" data-show="${i ? 8 : r ? 7 : 6}"></div><span class="example-probability example-reveal" data-show="${i ? 8 : r ? 7 : 6}">${fmt(p)}</span><span class="example-rank">${r + 1}</span></div>`).join("")}</div></div>`).join("")}</div>
    <div class="example-scores example-reveal" data-show="9"><h3>Borda scores</h3>
    ${alternatives.map((a, i) => `<div class="example-score-row example-reveal" data-show="${i ? 14 : 9}" data-alternative="${a}"><div class="example-score-name">B<sub>π</sub>(${a})</div><div class="example-calculation">
      ${probabilities[a].map((p, r) => `<span class="example-score-term example-reveal" data-show="${i ? 14 : 10 + r}" data-rank="${r}">${r ? '+ ' : ''}${3 - r} × <span class="example-factor">${fmt(p)}</span></span>`).join("")}</div><div class="example-score-value example-reveal" data-show="${i ? 14 : 13}">= ${fmt(probabilities[a].reduce((sum, p, r) => sum + (3 - r) * p, 0))}</div></div>`).join("")}</div>`;
  document.getElementById("example-builds").innerHTML = Array.from({ length:14 }, (_, i) =>
    `<span class="opening-step fragment" data-fragment-index="${i}"></span>`).join("");

  let previous = -1;
  const animations = new Set();
  const timers = new Set();
  const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const select = selector => root.querySelector(selector);
  const all = selector => [...root.querySelectorAll(selector)];
  function later(fn, delay) {
    const id = setTimeout(() => { timers.delete(id); fn(); }, delay);
    timers.add(id);
  }
  function cancelMotion() {
    timers.forEach(clearTimeout); timers.clear();
    animations.forEach(animation => animation.cancel()); animations.clear();
    document.querySelectorAll(".example-flight").forEach(node => node.remove());
  }
  function animate(element, frames, options) {
    if (reducedMotion()) return;
    const animation = element.animate(frames, { easing:"cubic-bezier(.22,.61,.36,1)", ...options });
    animations.add(animation);
    animation.onfinish = () => animations.delete(animation);
    return animation;
  }
  function rect(element) { return element.getBoundingClientRect(); }
  function fly(source, target, text, delay = 0, duration = 950, color) {
    if (reducedMotion()) return;
    const from = source instanceof Element ? rect(source) : source;
    const to = rect(target);
    const token = document.createElement("span");
    token.className = "example-flight";
    token.textContent = text;
    const scale = rect(slide).width / slide.offsetWidth;
    Object.assign(token.style, { left:`${from.x}px`, top:`${from.y}px`, fontSize:`${20 * scale}px`, color:color || "#9a1b1b" });
    document.body.appendChild(token);
    const dx = to.x + to.width / 2 - from.x;
    const dy = to.y + to.height / 2 - from.y;
    const motion = animate(token, [
      { transform:"translate(0,0)", opacity:0 },
      { transform:`translate(${dx * .12}px,${dy * .12 - 10}px)`, opacity:1, offset:.18 },
      { transform:`translate(${dx}px,${dy}px) translate(-50%,-50%)`, opacity:1, offset:.82 },
      { transform:`translate(${dx}px,${dy}px) translate(-50%,-50%) scale(.8)`, opacity:0 }
    ], { duration, delay, fill:"backwards" });
    if (motion) motion.onfinish = () => { animations.delete(motion); token.remove(); };
  }
  const colors = ["#9a1b1b", "#1b6f7a", "#856021"];
  function highlight(a, ranks) {
    all(".example-profile-row").forEach((row, i) => {
      const rank = profile[i].order.indexOf(a);
      if (!ranks.includes(rank)) return;
      [row.querySelector(`[data-alternative="${a}"]`), row.querySelector(".example-mass")].forEach(node => {
        node.classList.add("example-highlight");
        node.style.setProperty("--example-color", colors[rank]);
        node.style.setProperty("--example-tint", colors[rank] + "18");
      });
    });
  }
  function buildBar(a, rank, delay = 0) {
    const bin = select(`.example-hist-row[data-alternative="${a}"] .example-bin[data-rank="${rank}"]`);
    const label = bin.querySelector(".example-probability");
    profile.forEach((row, i) => {
      if (row.order[rank] === a) fly(select(`.example-mass[data-row="${i}"]`), label, fmt(row.weight), delay, 1100, colors[rank]);
    });
    animate(bin.querySelector(".example-bar"), [{ transform:"scaleY(0)" }, { transform:"scaleY(1)" }], { duration:1100, delay, fill:"backwards" });
    animate(label, [{ opacity:0 }, { opacity:0, offset:.65 }, { opacity:1 }], { duration:1200, delay, fill:"backwards" });
  }
  function buildTerm(a, rank, delay = 0) {
    const source = select(`.example-hist-row[data-alternative="${a}"] .example-bin[data-rank="${rank}"] .example-probability`);
    const target = select(`.example-score-row[data-alternative="${a}"] .example-score-term[data-rank="${rank}"]`);
    fly(source, target.querySelector(".example-factor"), fmt(probabilities[a][rank]), delay);
    animate(source, [{ color:"#9a1b1b" }, { color:"#9a1b1b", offset:.65 }, { color:"#686868" }], { duration:1100, delay });
    animate(target, [{ opacity:0 }, { opacity:0, offset:.7 }, { opacity:1 }], { duration:1100, delay, fill:"backwards" });
  }
  function render(stage) {
    root.dataset.grouped = String(stage >= 1);
    select(".example-profile-title").textContent = stage >= 3 ? "The profile π" : stage >= 1 ? "Unique rankings" : "People’s rankings";
    select(".example-mass-title").textContent = stage >= 3 ? "π(σ)" : "Count";
    all(".example-mass").forEach((node, i) => { node.textContent = stage >= 3 ? fmt(profile[i].weight) : counts[i]; });
    all("[data-show]").forEach(node => {
      const visible = stage >= Number(node.dataset.show);
      node.classList.toggle("example-visible", visible);
      node.setAttribute("aria-hidden", String(!visible));
    });
    const showTotal = stage === 2;
    select(".example-total").classList.toggle("example-visible", showTotal);
    select(".example-total").setAttribute("aria-hidden", String(!showTotal));
    select(".example-people").setAttribute("aria-hidden", String(stage >= 1));
    select(".example-grouped").setAttribute("aria-hidden", String(stage < 1));
    all(".example-highlight").forEach(node => node.classList.remove("example-highlight"));
    if (stage === 6) highlight("A", [0]);
    if (stage === 7) highlight("A", [1, 2]);
  }
  function sync() {
    const visible = [...slide.querySelectorAll(".fragment.visible")];
    const stage = visible.length ? Math.max(...visible.map(node => Number(node.dataset.fragmentIndex))) + 1 : 0;
    const active = Reveal.getCurrentSlide() === slide;
    if (stage === previous && active) return;
    const forward = active && stage === previous + 1 && previous >= 0;
    const peopleRects = stage === 1 ? all(".example-person").map(node => ({ order:node.dataset.order, rect:rect(node.querySelector(".example-order")) })) : [];
    const totalRect = rect(select(".example-total strong"));
    cancelMotion();
    render(stage);
    previous = stage;
    if (!forward || reducedMotion()) return;
    if (stage === 1) peopleRects.forEach((person, i) => {
      fly(person.rect, select(`.example-profile-row[data-order="${person.order}"] .example-order`), person.order.split("").join(" ≻ "), i * 18, 850);
    });
    if (stage === 3) {
      all(".example-mass").forEach((node, i) => {
        node.innerHTML = `<span class="example-divisor">${counts[i]} ÷ ${total}</span>`;
        fly(totalRect, node, `÷ ${total}`, i * 45, 750);
      });
      later(() => all(".example-mass").forEach((node, i) => { node.textContent = fmt(profile[i].weight); }), 1050);
    }
    if (stage === 6) buildBar("A", 0);
    if (stage === 7) [1, 2].forEach(rank => buildBar("A", rank));
    if (stage === 8) ["B", "C"].forEach(a => [0, 1, 2].forEach(rank => buildBar(a, rank)));
    if (stage >= 10 && stage <= 12) buildTerm("A", stage - 10);
    if (stage === 14) ["B", "C"].forEach(a => {
      [0, 1, 2].forEach(rank => buildTerm(a, rank, rank * 450));
      animate(select(`.example-score-row[data-alternative="${a}"] .example-score-value`), [{ opacity:0 }, { opacity:0, offset:.85 }, { opacity:1 }], { duration:2350, fill:"backwards" });
    });
  }
  ["ready", "slidechanged", "fragmentshown", "fragmenthidden"].forEach(event => Reveal.on(event, sync));
  window.addEventListener("resize", () => { cancelMotion(); render(previous < 0 ? 0 : previous); });
  window.addEventListener("beforeprint", () => { cancelMotion(); render(14); });
  window.addEventListener("afterprint", () => render(previous < 0 ? 0 : previous));
  render(0);
})();
