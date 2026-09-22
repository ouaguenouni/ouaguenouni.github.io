(function () {
  "use strict";
  const overview = document.getElementById("borda-elicitation");
  const development = document.getElementById("borda-hoeffding-development");
  function syncSlide(slide) {
    const visible = [...slide.querySelectorAll(".sampling-steps .fragment.visible")];
    const build = visible.length ? Math.max(...visible.map(f => Number(f.dataset.fragmentIndex))) + 1 : 0;
    slide.dataset.build = String(build);
    slide.dataset.comparison = String(build >= 7);
    if (slide === overview) {
      slide.classList.toggle("sampling-compact", build >= 5);
      slide.classList.toggle("sampling-three-protocols", build >= 15);
    }
    slide.querySelectorAll("[data-from], [data-until]").forEach(element => {
      const shown = build >= Number(element.dataset.from || 0) && build < Number(element.dataset.until || Infinity);
      element.classList.toggle("build-hidden", !shown);
      element.setAttribute("aria-hidden", String(!shown));
    });
  }
  function sync() { syncSlide(overview); syncSlide(development); }
  ["ready", "slidechanged", "fragmentshown", "fragmenthidden"].forEach(event => Reveal.on(event, sync));
  // Jump directly to the branch; Reveal.down() would consume pending builds first.
  overview.querySelector('[data-branch="down"]').addEventListener("click", event => {
    event.stopPropagation();
    Reveal.slide(Reveal.getIndices().h, 1);
  });
  sync();
})();
