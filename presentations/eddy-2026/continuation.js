(function () {
  "use strict";
  const source = window.EDDY_DATA.originalWitnesses;

  function drawHistogram(element, bins, maximum) {
    element.innerHTML = bins.map(p => '<span class="source-hist-bar" style="--height:' + (100 * p / maximum) + '%"></span>').join("");
  }

  drawHistogram(document.getElementById("measure-uniform-hist"), Array(15).fill(1 / 15), .5);
  drawHistogram(document.getElementById("measure-antagonistic-hist"), [0.5, ...Array(13).fill(0), 0.5], .5);

  const uniform = Array.from({ length: 10 }, (_, i) =>
    (Math.floor((i + 1) * source.m / 10) - Math.floor(i * source.m / 10)) / source.m);
  const profiles = ["A", "B", "U", "C", "D"].map(id => id === "U" ?
    { id, bins: uniform, support: Array.from({ length: source.m }, (_, i) => [i + 1, 1 / source.m]) } :
    source.profiles.find(profile => profile.id === id));
  const descriptions = { A: "Three peaks", B: "Two symmetric peaks", U: "Uniform", C: "Right-skewed", D: "Left-skewed" };
  const container = document.getElementById("original-five-witnesses");
  profiles.forEach(profile => {
    const mean = profile.support.reduce((sum, [rank, p]) => sum + rank * p, 0);
    const variance = profile.support.reduce((sum, [rank, p]) => sum + p * (rank - mean) ** 2, 0);
    const before = profile.support.reduce((sum, [rank, p]) => sum + p * (source.m - rank) / (source.m - 1), 0);
    const preferredScore = profile.support.reduce((sum, [rank, p]) => sum + p * (source.m - rank) / (source.m - 1) * (source.m + 1 - rank), 0) / before;
    const rejectedScore = profile.support.reduce((sum, [rank, p]) => sum + p * (rank - 1) / (source.m - 1) * (source.m + 1 - rank), 0) / (1 - before);
    const divisiveness = Math.abs(preferredScore - rejectedScore);
    const divText = Math.abs(divisiveness - 257 / 3) < 1e-8 ? "\\frac{257}{3}" : divisiveness.toFixed(4);
    const figure = document.createElement("div");
    figure.className = "source-witness" + (profile.id === "U" ? " uniform-reference" : "");
    figure.innerHTML = '<h3>' + profile.id + '</h3><div class="source-witness-hist" role="img" aria-label="' + descriptions[profile.id] + ' rank distribution of the focal alternative"></div><p class="source-witness-caption">' + descriptions[profile.id] + '</p><div class="witness-score fragment" data-fragment-index="1"><p>\\(\\mathrm{Var}=' + variance.toFixed(2) + '\\)</p><p>\\(\\mathrm{Div}=' + divText + '\\)</p></div>';
    drawHistogram(figure.querySelector(".source-witness-hist"), profile.bins, .8);
    container.appendChild(figure);
  });

  function sync() {
    document.querySelectorAll(".continuation-slide").forEach(slide => {
      const fragments = [...slide.querySelectorAll(".fragment.visible")];
      const stage = fragments.length ? Math.max(...fragments.map(f => Number(f.dataset.fragmentIndex))) + 1 : 0;
      slide.dataset.build = String(stage);
      const corrected = slide.querySelector(".profile-defined-words");
      if (corrected) corrected.setAttribute("aria-hidden", String(stage < 4));
    });
  }
  ["ready", "slidechanged", "fragmentshown", "fragmenthidden"].forEach(event => Reveal.on(event, sync));
  sync();
})();
