(function () {
  "use strict";
  const overview = document.getElementById("borda-elicitation");
  const development = document.getElementById("borda-hoeffding-development");
  const example = window.EDDY_SAMPLING.makeExample();
  const format = value => String(value).replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  const endpoint = row => row.k === 2 ? "pair" : row.k === example.m ? "full" : "";
  const table = overview.querySelector(".sampling-numerical-table table");
  table.innerHTML = `<thead><tr><th scope="col">Ranking size <i>k</i></th>${example.rows.map(row => `<th scope="col"${endpoint(row) ? ' class="sampling-endpoint"' : ""}>${row.k}</th>`).join("")}</tr></thead>
    <tbody>${[
      { key:"population", label:'Population<span class="sampling-table-qualifier">mean coverage · rounded up</span>' },
      { key:"comparisons", label:'Comparisons per voter<span class="sampling-table-qualifier">merge-sort upper bound</span>' }
    ].map(metric => `<tr data-metric="${metric.key}"><th scope="row">${metric.label}</th>${example.rows.map(row => `<td data-k="${row.k}"${endpoint(row) ? ' class="sampling-endpoint"' : ""}><span${endpoint(row) ? ` data-sampling-target="${metric.key === "population" ? "population" : "cost"}-${endpoint(row)}"` : ""}>${format(row[metric.key])}</span></td>`).join("")}</tr>`).join("")}</tbody>`;
  const motions = new Set();
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
  let previousBuild = -1;
  let previouslyActive = false;
  const buildOf = slide => {
    const visible = [...slide.querySelectorAll(".sampling-steps .fragment.visible")];
    return visible.length ? Math.max(...visible.map(f => Number(f.dataset.fragmentIndex))) + 1 : 0;
  };
  function cancelMotions() {
    motions.forEach(motion => motion.cancel()); motions.clear();
    document.querySelectorAll(".sampling-metric-flight").forEach(node => node.remove());
  }
  function animate(node, frames, options, done) {
    const motion = node.animate(frames, { easing:"cubic-bezier(.22,.61,.36,1)", fill:"backwards", ...options });
    motions.add(motion);
    motion.onfinish = () => { motions.delete(motion); done?.(); };
  }
  function moveMetricsToTable(origins) {
    // The endpoint values keep their identity while the general k columns fill in.
    origins.forEach(({ key, text, rect, fontSize }, index) => {
      const target = overview.querySelector(`[data-sampling-target="${key}"]`);
      const to = target.getBoundingClientRect();
      const token = document.createElement("span");
      token.className = "sampling-metric-flight";
      token.setAttribute("aria-hidden", "true");
      token.textContent = text;
      Object.assign(token.style, { left:`${rect.x + rect.width / 2}px`, top:`${rect.y + rect.height / 2}px`, fontSize:`${fontSize}px` });
      document.body.appendChild(token);
      const dx = to.x + to.width / 2 - rect.x - rect.width / 2;
      const dy = to.y + to.height / 2 - rect.y - rect.height / 2;
      const scale = to.width / rect.width;
      const delay = index * 75;
      const bend = key.endsWith("full") ? -20 : 20;
      animate(token, [
        { transform:"translate(-50%,-50%)", opacity:1 },
        { transform:`translate(${dx * .4}px,${dy * .4 + bend}px) translate(-50%,-50%) scale(${1 + (scale - 1) * .4})`, opacity:1, offset:.45 },
        { transform:`translate(${dx}px,${dy}px) translate(-50%,-50%) scale(${scale})`, opacity:1 }
      ], { duration:950, delay }, () => token.remove());
      animate(target, [{ opacity:0 }, { opacity:0, offset:.88 }, { opacity:1 }], { duration:1070, delay });
    });
    table.querySelectorAll("tbody td:not(.sampling-endpoint)").forEach(cell => {
      animate(cell, [{ opacity:0, transform:"translateY(8px)" }, { opacity:1, transform:"none" }], {
        duration:550, delay:300 + (Number(cell.dataset.k) - 2) * 65
      });
    });
  }
  function syncSlide(slide) {
    const build = buildOf(slide);
    slide.dataset.build = String(build);
    slide.dataset.comparison = String(build >= 7);
    if (slide === overview) {
      slide.classList.toggle("sampling-compact", build >= 5);
      slide.classList.toggle("sampling-three-protocols", build >= 15);
      slide.classList.toggle("sampling-table-view", build >= 23);
    }
    slide.querySelectorAll("[data-from], [data-until]").forEach(element => {
      const shown = build >= Number(element.dataset.from || 0) && build < Number(element.dataset.until || Infinity);
      element.classList.toggle("build-hidden", !shown);
      element.setAttribute("aria-hidden", String(!shown));
    });
  }
  function sync() {
    const build = buildOf(overview);
    const active = Reveal.getCurrentSlide() === overview;
    const enteringTable = active && previouslyActive && previousBuild === 22 && build === 23 && !reducedMotion.matches;
    const scale = overview.getBoundingClientRect().width / overview.offsetWidth;
    const origins = enteringTable ? [...overview.querySelectorAll("[data-sampling-source]")].map(node => ({
      key:node.dataset.samplingSource, text:node.textContent, rect:node.getBoundingClientRect(),
      fontSize:parseFloat(getComputedStyle(node).fontSize) * scale
    })) : [];
    if (build !== previousBuild || active !== previouslyActive) cancelMotions();
    syncSlide(overview); syncSlide(development);
    if (enteringTable) moveMetricsToTable(origins);
    previousBuild = build; previouslyActive = active;
  }
  ["ready", "slidechanged", "fragmentshown", "fragmenthidden"].forEach(event => Reveal.on(event, sync));
  window.addEventListener("resize", cancelMotions);
  window.addEventListener("beforeprint", cancelMotions);
  reducedMotion.addEventListener("change", cancelMotions);
  // The shared direct-details handler also saves the exact main-slide build.
  sync();
})();
