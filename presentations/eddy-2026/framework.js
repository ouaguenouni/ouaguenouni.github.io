(function () {
  "use strict";
  const example = window.EDDY_DATA.pluralityExample;
  const slide = document.getElementById("small-group-favorites");
  const format = value => Number(value.toFixed(2)).toString();
  document.getElementById("framework-profile").innerHTML = example.profile.map((row, index) =>
    `<p data-profile-row="${index}"><i>π</i>(${[...row.order].map((a, i) => `${i ? '<span class="framework-profile-relation">≻</span>' : ''}<span class="framework-profile-letter" data-alternative="${a}">${a}</span>`).join("")}) = <span class="framework-profile-weight">${format(row.weight)}</span></p>`
  ).join("");
  const cells = [];
  const rows = [];
  for (let degree = 2; degree <= 4; degree++) {
    for (let mask = 1; mask < 16; mask++) {
      const subset = example.alternatives.filter((_, i) => mask & (1 << i));
      if (subset.length !== degree) continue;
      const key = subset.join("");
      const entries = example.alternatives.map(a => {
        const applicable = subset.includes(a);
        const contributors = applicable ? example.profile.flatMap((row, index) =>
          subset.every(b => row.order.indexOf(a) <= row.order.indexOf(b)) ? [index] : []) : [];
        const value = contributors.reduce((sum, index) => sum + example.profile[index].weight, 0);
        cells.push({ key, subset, degree, alternative:a, applicable, contributors, value });
        return `<td data-subset="${key}" data-alternative="${a}"><div><span class="matrix-value">${applicable ? format(value) : "—"}</span></div></td>`;
      });
      rows.push(`<tr class="matrix-degree-${degree}" data-degree="${degree}"><th><div>{${subset.join(",")}}</div></th>${entries.join("")}</tr>`);
    }
  }
  document.getElementById("framework-matrix-body").innerHTML = rows.join("");
  const targetFor = cell => slide.querySelector(`td[data-subset="${cell.key}"][data-alternative="${cell.alternative}"]`);
  const profileRow = index => slide.querySelector(`[data-profile-row="${index}"]`);
  const isFirst = cell => cell.alternative === "A" && (cell.key === "AB" || cell.key === "ABC");
  const motions = new Set();
  let previous = -1;
  const reduced = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
  function cancel() {
    motions.forEach(motion => motion.cancel()); motions.clear();
    document.querySelectorAll(".matrix-flight").forEach(node => node.remove());
  }
  function animate(node, frames, options) {
    if (reduced()) return;
    const motion = node.animate(frames, { easing:"cubic-bezier(.22,.61,.36,1)", ...options });
    motions.add(motion);
    motion.onfinish = () => motions.delete(motion);
    return motion;
  }
  function highlight(cell) {
    cell.contributors.forEach(index => {
      const row = profileRow(index);
      cell.subset.forEach(a => {
        const letter = row.querySelector(`[data-alternative="${a}"]`);
        letter.classList.add("framework-profile-member");
        if (a === cell.alternative) letter.classList.add("framework-profile-favorite");
      });
      row.querySelector(".framework-profile-weight").classList.add("framework-profile-contributor");
    });
    targetFor(cell).classList.add("matrix-cell-active");
  }
  function render(stage) {
    slide.dataset.build = String(stage);
    slide.classList.toggle("has-degree-three", stage >= 5);
    slide.classList.toggle("has-degree-four", stage >= 8);
    slide.querySelectorAll("[data-degree]").forEach(row => {
      const degree = Number(row.dataset.degree);
      const visible = degree === 2 ? stage >= 2 : degree === 3 ? stage >= 5 : stage >= 8;
      row.classList.toggle("matrix-layer-visible", visible);
      row.setAttribute("aria-hidden", String(!visible));
    });
    slide.querySelectorAll(".framework-profile-member, .framework-profile-favorite, .framework-profile-contributor, .matrix-cell-active").forEach(node =>
      node.classList.remove("framework-profile-member", "framework-profile-favorite", "framework-profile-contributor", "matrix-cell-active"));
    cells.forEach(cell => {
      const filled = cell.degree === 2 ? stage >= (isFirst(cell) ? 3 : 4) : cell.degree === 3 ? stage >= (isFirst(cell) ? 6 : 7) : stage >= 8;
      const value = targetFor(cell).querySelector(".matrix-value");
      value.classList.toggle("is-filled", filled);
      value.setAttribute("aria-hidden", String(!filled));
    });
    if (stage === 3 || stage === 6) highlight(cells.find(cell => isFirst(cell) && cell.degree === (stage === 3 ? 2 : 3)));
  }
  function fillCell(cell) {
    const target = targetFor(cell).querySelector(".matrix-value");
    const to = target.getBoundingClientRect();
    const scale = slide.getBoundingClientRect().width / slide.offsetWidth;
    cell.contributors.forEach(index => {
      const source = profileRow(index).querySelector(".framework-profile-weight");
      const from = source.getBoundingClientRect();
      const token = document.createElement("span");
      token.className = "matrix-flight";
      token.textContent = format(example.profile[index].weight);
      Object.assign(token.style, { left:`${from.x + from.width / 2}px`, top:`${from.y + from.height / 2}px`, fontSize:`${20 * scale}px` });
      document.body.appendChild(token);
      const dx = to.x + to.width / 2 - from.x - from.width / 2;
      const dy = to.y + to.height / 2 - from.y - from.height / 2;
      const motion = animate(token, [
        { transform:"translate(-50%,-50%)", opacity:0 },
        { transform:`translate(${dx * .1}px,${dy * .1 - 8}px) translate(-50%,-50%)`, opacity:1, offset:.15 },
        { transform:`translate(${dx}px,${dy}px) translate(-50%,-50%)`, opacity:1, offset:.85 },
        { transform:`translate(${dx}px,${dy}px) translate(-50%,-50%) scale(.8)`, opacity:0 }
      ], { duration:1150 });
      if (motion) motion.onfinish = () => { motions.delete(motion); token.remove(); };
    });
    animate(target, [{ opacity:0 }, { opacity:0, offset:.8 }, { opacity:1 }], { duration:1250, fill:"backwards" });
  }
  function sync() {
    const fragments = [...slide.querySelectorAll(".fragment.visible")];
    const stage = fragments.length ? Math.max(...fragments.map(f => Number(f.dataset.fragmentIndex))) + 1 : 0;
    const active = Reveal.getCurrentSlide() === slide;
    if (stage === previous && active) return;
    const forward = active && previous >= 0 && stage === previous + 1;
    cancel(); render(stage); previous = stage;
    if (!forward || reduced()) return;
    if (stage === 3 || stage === 6) fillCell(cells.find(cell => isFirst(cell) && cell.degree === (stage === 3 ? 2 : 3)));
    if (stage === 4 || stage === 7) cells.filter(cell => cell.degree === (stage === 4 ? 2 : 3) && !isFirst(cell)).forEach(fillCell);
  }
  ["ready", "slidechanged", "fragmentshown", "fragmenthidden"].forEach(event => Reveal.on(event, sync));
  window.addEventListener("resize", () => { cancel(); render(Math.max(0, previous)); });
  window.addEventListener("beforeprint", () => { cancel(); render(8); });
  window.addEventListener("afterprint", () => render(Math.max(0, previous)));
  render(0);
})();
