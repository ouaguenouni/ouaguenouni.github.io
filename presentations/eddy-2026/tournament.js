(function () {
  "use strict";
  const slide = document.getElementById("weighted-tournament");
  const profile = window.EDDY_DATA.winnerProfile;
  const alternatives = window.EDDY_DATA.alternatives;
  const fmt = value => String(Number(value.toFixed(2)));
  const probability = (a, b) => profile.reduce((sum, row) =>
    sum + (row.order.indexOf(a) < row.order.indexOf(b) ? row.weight : 0), 0);
  const scores = alternatives.map(a => {
    const terms = alternatives.filter(b => b !== a).map(b => ({
      value:probability(a, b), edge:[a, b].sort().join("").toLowerCase(), reverse:a > b
    }));
    return { alternative:a, terms, value:1 + terms.reduce((sum, term) => sum + term.value, 0) };
  });
  document.getElementById("opening-tournament-scores").innerHTML = scores.map(score =>
    `<div class="tournament-score" data-alternative="${score.alternative}"><div class="tournament-score-heading">B<sub>π</sub>(${score.alternative})</div><div class="tournament-calculation"><span>1</span>${score.terms.map((term, i) => `<span class="tournament-term" data-term="${i}">+ <span class="tournament-factor">${fmt(term.value)}</span></span>`).join("")}<strong class="tournament-result">= ${fmt(score.value)}</strong></div></div>`
  ).join("");
  const motions = new Set();
  const timers = new Set();
  let previous = -1;
  const reduced = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
  const select = selector => slide.querySelector(selector);
  function cancel() {
    motions.forEach(motion => motion.cancel()); motions.clear();
    timers.forEach(clearTimeout); timers.clear();
    document.querySelectorAll(".tournament-flight").forEach(node => node.remove());
  }
  function animate(node, frames, options) {
    if (reduced()) return;
    const motion = node.animate(frames, { easing:"cubic-bezier(.22,.61,.36,1)", ...options });
    motions.add(motion);
    motion.onfinish = () => motions.delete(motion);
    return motion;
  }
  function visibility(node, visible) {
    node.classList.toggle("is-shown", visible);
    node.setAttribute("aria-hidden", String(!visible));
  }
  function render(stage) {
    scores.forEach(score => {
      const row = select(`.tournament-score[data-alternative="${score.alternative}"]`);
      const first = score.alternative === "A";
      visibility(row, stage >= (first ? 4 : 7));
      row.querySelectorAll(".tournament-term").forEach((term, i) => visibility(term, stage >= (first ? 4 + i : 7)));
      visibility(row.querySelector(".tournament-result"), stage >= (first ? 6 : 7));
    });
    slide.querySelectorAll(".tournament-edge-active").forEach(node => node.classList.remove("tournament-edge-active"));
    if (stage === 4 || stage === 5) {
      const edge = stage === 4 ? "ab" : "ac";
      select(`#opening-edge-${edge}`).classList.add("tournament-edge-active");
      select(`#tournament-line-${edge}`).classList.add("tournament-edge-active");
    }
  }
  function moveTerm(score, index, delay = 0) {
    const term = score.terms[index];
    const source = select(`#opening-edge-${term.edge}`);
    const destination = select(`.tournament-score[data-alternative="${score.alternative}"] .tournament-term[data-term="${index}"]`);
    const target = destination.querySelector(".tournament-factor");
    const from = source.getBoundingClientRect();
    const to = target.getBoundingClientRect();
    const scale = slide.getBoundingClientRect().width / slide.offsetWidth;
    const token = document.createElement("span");
    token.className = "tournament-flight";
    token.textContent = term.reverse ? `1 − ${source.textContent}` : source.textContent;
    Object.assign(token.style, { left:`${from.x + from.width / 2}px`, top:`${from.y + from.height / 2}px`, fontSize:`${24 * scale}px` });
    document.body.appendChild(token);
    const dx = to.x + to.width / 2 - from.x - from.width / 2;
    const dy = to.y + to.height / 2 - from.y - from.height / 2;
    const motion = animate(token, [
      { transform:"translate(-50%,-50%)", opacity:0 },
      { transform:`translate(${dx * .1}px,${dy * .1 - 10}px) translate(-50%,-50%)`, opacity:1, offset:.15 },
      { transform:`translate(${dx}px,${dy}px) translate(-50%,-50%)`, opacity:1, offset:.86 },
      { transform:`translate(${dx}px,${dy}px) translate(-50%,-50%)`, opacity:0 }
    ], { duration:1100, delay, fill:"backwards" });
    if (motion) motion.onfinish = () => { motions.delete(motion); token.remove(); };
    if (term.reverse) {
      const timer = setTimeout(() => { token.textContent = fmt(term.value); timers.delete(timer); }, delay + 700);
      timers.add(timer);
    }
    animate(destination, [{ opacity:0 }, { opacity:0, offset:.75 }, { opacity:1 }], { duration:1200, delay, fill:"backwards" });
  }
  function sync() {
    const fragments = [...slide.querySelectorAll(".fragment.visible")];
    const stage = fragments.length ? Math.max(...fragments.map(node => Number(node.dataset.fragmentIndex))) + 1 : 0;
    const active = Reveal.getCurrentSlide() === slide;
    if (stage === previous && active) return;
    const forward = active && previous >= 0 && stage === previous + 1;
    cancel(); render(stage); previous = stage;
    if (!forward || reduced()) return;
    if (stage === 4 || stage === 5) moveTerm(scores[0], stage - 4);
    if (stage === 7) scores.slice(1).forEach(score => {
      moveTerm(score, 0);
      moveTerm(score, 1, 450);
      animate(select(`.tournament-score[data-alternative="${score.alternative}"] .tournament-result`), [{ opacity:0 }, { opacity:0, offset:.83 }, { opacity:1 }], { duration:2100, fill:"backwards" });
    });
  }
  ["ready", "slidechanged", "fragmentshown", "fragmenthidden"].forEach(event => Reveal.on(event, sync));
  window.addEventListener("resize", () => { cancel(); render(Math.max(0, previous)); });
  window.addEventListener("beforeprint", () => { cancel(); render(7); });
  window.addEventListener("afterprint", () => render(Math.max(0, previous)));
  render(0);
})();
