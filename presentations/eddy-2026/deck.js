(function () {
  "use strict";

  const DATA = window.EDDY_DATA;
  const savedFragmentState = new Map();
  const detailReturnState = new Map();

  function choose(n, k) {
    if (k < 0 || k > n) return 0;
    if (k === 0 || k === n) return 1;
    let value = 1;
    for (let i = 1; i <= k; i += 1) value = value * (n - k + i) / i;
    return value;
  }

  function pairwiseMargins(profile) {
    const pairs = [["A", "B"], ["A", "C"], ["B", "C"]];
    return pairs.map(([left, right]) => {
      const leftShare = profile.reduce((sum, row) => {
        return sum + (row.order.indexOf(left) < row.order.indexOf(right) ? row.weight : 0);
      }, 0);
      return { left, right, leftShare, rightShare: 1 - leftShare };
    });
  }

  function rankDistribution(profile, alternative) {
    const distribution = Array(DATA.alternatives.length).fill(0);
    profile.forEach((row) => { distribution[row.order.indexOf(alternative)] += row.weight; });
    return distribution;
  }

  function moments(counts) {
    const total = counts.reduce((a, b) => a + b, 0);
    const probs = counts.map((count) => count / total);
    const mean = probs.reduce((sum, probability, index) => sum + probability * (index + 1), 0);
    const central = (power) => probs.reduce((sum, probability, index) => {
      return sum + probability * Math.pow(index + 1 - mean, power);
    }, 0);
    const variance = central(2);
    return {
      mean,
      variance,
      skewness: central(3) / Math.pow(variance, 1.5),
      kurtosis: central(4) / Math.pow(variance, 2) - 3
    };
  }

  function fmt(value, digits) {
    const rounded = Math.abs(value) < 1e-12 ? 0 : value;
    return rounded.toFixed(digits).replace(/\.?0+$/, "");
  }

  function renderHistogram(target, values, color, labels) {
    if (!target) return;
    const max = Math.max(...values);
    target.innerHTML = "";
    target.style.setProperty("--bar-color", color || "#9a1b1b");
    values.forEach((value, index) => {
      const bar = document.createElement("div");
      bar.className = "bar";
      bar.style.height = `${Math.max(1.5, value / max * 100)}%`;
      const label = document.createElement("span");
      label.textContent = labels ? labels[index] : String(index + 1);
      bar.appendChild(label);
      target.appendChild(bar);
    });
  }

  function bordaScore(profile, alternative) {
    return rankDistribution(profile, alternative).reduce((sum, probability, index) =>
      sum + probability * (DATA.alternatives.length - index), 0);
  }

  function openingHistogram(target, probabilities, morphFrom) {
    target.innerHTML = probabilities.map((p, index) => {
      const initial = morphFrom ? morphFrom[index] : p;
      const label = (value) => Math.abs(value - 1 / 3) < 1e-10 ? "1/3" : Math.abs(value - .5) < 1e-10 ? "1/2" : fmt(value, 2);
      return '<div class="rank-column"><div class="rank-bar-space"><div class="rank-bar" style="--initial:' + initial + ';--final:' + p + '"><span class="bar-probability"><span class="before-polarization">' + label(initial) + '</span><span class="after-polarization">' + label(p) + '</span></span></div></div><span class="rank-label">' + (index + 1) + '</span></div>';
    }).join("");
  }

  function renderOpening() {
    const profile = DATA.winnerProfile;
    const margins = pairwiseMargins(profile);
    margins.forEach(margin => {
      document.getElementById("opening-edge-" + margin.left.toLowerCase() + margin.right.toLowerCase()).textContent = fmt(margin.leftShare, 2);
    });
  }

  function renderPairwiseWitness() {
    const uniform = DATA.pairwiseWitness.uniform;
    const polarized = DATA.pairwiseWitness.polarized;
    document.getElementById("uniform-rankings").innerHTML = uniform.map(row => '<span>' + row.order.split("").join(" ≻ ") + '</span>').join("");
    document.getElementById("polarized-rankings").innerHTML = polarized.map(row => '<p>\\(\\pi_P(' + row.order.split("").join("\\succ ") + ')=\\tfrac12\\)</p>').join("");
    const uniformHistogram = rankDistribution(uniform, "A");
    openingHistogram(document.getElementById("uniform-a-hist"), uniformHistogram);
    openingHistogram(document.getElementById("polarized-a-hist"), rankDistribution(polarized, "A"), uniformHistogram);

    const uniformMargins = pairwiseMargins(uniform);
    const polarizedMargins = pairwiseMargins(polarized);
    ["uniform", "polarized"].forEach((name, i) => {
      const margins = i === 0 ? uniformMargins : polarizedMargins;
      document.getElementById(name + "-proportions").innerHTML = margins.map(m =>
        '<span>\\(p_{' + m.left.toLowerCase() + m.right.toLowerCase() + '}=\\tfrac12\\)</span>'
      ).join("");
    });
    document.getElementById("pairwise-proof-table").innerHTML = uniformMargins.map((margin, index) => {
      const other = polarizedMargins[index];
      return '<tr><th>' + margin.left + ' preferred to ' + margin.right + '</th><td>' + fmt(margin.leftShare, 2) + '</td><td>' + fmt(other.leftShare, 2) + '</td></tr>';
    }).join("");
  }

  function syncOpeningBuilds() {
    document.querySelectorAll(".opening-slide").forEach(slide => {
      const fragments = [...slide.querySelectorAll(".fragment.visible")];
      const stage = fragments.length ? Math.max(...fragments.map(f => Number(f.dataset.fragmentIndex))) + 1 : 0;
      slide.dataset.build = String(stage);
      if (slide.id === "choosing-a-winner") {
        slide.classList.toggle("has-profile", stage >= 5);
        slide.classList.toggle("has-profile-score", stage >= 7);
        slide.querySelectorAll(".borda-person-only").forEach(element => element.setAttribute("aria-hidden", String(stage >= 5)));
        slide.querySelectorAll(".borda-profile-only").forEach(element => element.setAttribute("aria-hidden", String(stage < 5)));
        slide.querySelector(".formula-sample").setAttribute("aria-hidden", String(stage >= 7));
        slide.querySelector(".formula-profile").setAttribute("aria-hidden", String(stage < 7));
      }
      if (slide.id === "weighted-tournament") {
        slide.classList.toggle("has-pairwise-formula", stage >= 3);
        slide.querySelector(".rank-formula").setAttribute("aria-hidden", String(stage >= 3));
        slide.querySelector(".pairwise-formula").setAttribute("aria-hidden", String(stage < 3));
      }
      if (slide.id === "same-margins") {
        slide.querySelector(".polarized-population").setAttribute("aria-hidden", String(stage < 1));
        slide.querySelector("#polarized-a-hist").setAttribute("aria-label", stage < 2 ?
          "Rank distribution of A: one third at each rank" : "Rank distribution of A: half first, zero second, half third");
      }
    });
  }

  function witnessCard(profile, mode) {
    const stats = moments(profile.counts);
    const card = document.createElement("div");
    card.className = "hist-card";
    card.innerHTML = `<h3>${profile.short} · ${profile.name}</h3><div class="histogram compact"></div><div class="stats-line"></div>`;
    renderHistogram(card.querySelector(".histogram"), profile.counts, profile.color);
    const line = card.querySelector(".stats-line");
    if (mode === "moments") {
      line.innerHTML = `<span class="same">variance ${fmt(stats.variance, 2)}</span><br>skewness ${fmt(stats.skewness, 3)} · excess kurtosis ${fmt(stats.kurtosis, 3)}`;
    } else {
      line.innerHTML = `<span class="same">variance ${fmt(stats.variance, 2)}</span> · <span class="same">divisiveness ${profile.divisiveness}</span>`;
    }
    return card;
  }

  function renderWitnesses() {
    const profiles = DATA.sevenAlternativeWitness.profiles;
    const witness = document.getElementById("witness-histograms");
    const moment = document.getElementById("moment-histograms");
    profiles.forEach((profile) => {
      witness.appendChild(witnessCard(profile, "scores"));
      moment.appendChild(witnessCard(profile, "moments"));
    });
    document.getElementById("witness-values-table").innerHTML = profiles.map((profile) => {
      const stats = moments(profile.counts);
      return `<tr><th>${profile.short} · ${profile.name}</th><td>${fmt(stats.mean, 4)}</td><td>${fmt(stats.variance, 4)}</td><td>${fmt(stats.skewness, 6)}</td><td>${fmt(stats.kurtosis, 6)}</td></tr>`;
    }).join("");
  }

  function syncOriginalFigure() {
    const slide = document.getElementById("moment-compass");
    if (Reveal.getCurrentSlide() !== slide) return;
    const stage = slide.querySelectorAll(".mpstep.visible").length;
    const frame = slide.querySelector("iframe");
    // Use the source figure's existing stage API; its implementation and data stay intact.
    if (frame.contentWindow) frame.contentWindow.postMessage({ stage }, window.location.origin);
  }

  function renderElicitationExamples() {
    const chain = document.getElementById("chain-rounds");
    DATA.chainExample.rounds.forEach((round, index) => {
      const row = document.createElement("div");
      row.className = "round fragment";
      row.dataset.fragmentIndex = String(index + 1);
      row.innerHTML = `<span>Comparison ${index + 1}: ${round.pair[0]} vs ${round.pair[1]}</span><span><strong>${round.winner} wins</strong> · favorite of {${round.prefix.join(", ")}}</span>`;
      chain.appendChild(row);
    });

    const triples = document.getElementById("ranking-triples");
    DATA.rankingExample.triples.forEach((triple, index) => {
      const row = document.createElement("div");
      row.className = "triple fragment";
      row.dataset.fragmentIndex = String(index + 1);
      row.innerHTML = `<span>{${triple.subset.join(", ")}}</span><span>implied favorite: <strong>${triple.winner}</strong></span>`;
      triples.appendChild(row);
    });
  }

  function pluralityOfA(profile, subsetSize) {
    const denominator = DATA.sevenAlternativeWitness.denominator;
    return profile.counts.reduce((sum, count, index) => {
      const rank = index + 1;
      return sum + count / denominator * choose(7 - rank, subsetSize - 1) / choose(6, subsetSize - 1);
    }, 0);
  }

  function validateData() {
    const tolerance = 1e-10;
    const errors = [];
    const uniformMargins = pairwiseMargins(DATA.pairwiseWitness.uniform);
    const polarizedMargins = pairwiseMargins(DATA.pairwiseWitness.polarized);
    uniformMargins.forEach((margin, index) => {
      if (Math.abs(margin.leftShare - .5) > tolerance || Math.abs(margin.leftShare - polarizedMargins[index].leftShare) > tolerance) {
        errors.push(`pairwise witness mismatch for ${margin.left}/${margin.right}`);
      }
    });

    const profiles = DATA.sevenAlternativeWitness.profiles;
    profiles.forEach((profile) => {
      if (profile.counts.reduce((a, b) => a + b, 0) !== DATA.sevenAlternativeWitness.denominator) errors.push(`${profile.id} counts do not sum to 1536`);
      const stats = moments(profile.counts);
      if (Math.abs(stats.mean - 4) > tolerance) errors.push(`${profile.id} mean is not 4`);
      if (Math.abs(stats.variance - 1.5) > tolerance) errors.push(`${profile.id} variance is not 1.5`);
    });
    [2, 3].forEach((degree) => {
      const reference = pluralityOfA(profiles[0], degree);
      profiles.slice(1).forEach((profile) => {
        if (Math.abs(pluralityOfA(profile, degree) - reference) > tolerance) errors.push(`degree-${degree} witness mismatch`);
      });
    });

    if (errors.length) {
      document.documentElement.dataset.validation = "failed";
      console.error("EDDY data validation failed", errors);
    } else {
      document.documentElement.dataset.validation = "passed";
      console.info("EDDY data validation passed: pairwise witness and degree-2/3 moment witness verified.");
    }
  }

  function currentIndices() {
    const indices = Reveal.getIndices();
    return { h: indices.h || 0, v: indices.v || 0, f: Number.isFinite(indices.f) ? indices.f : -1 };
  }

  function saveCurrentFragment() {
    const indices = currentIndices();
    if (indices.v === 0) savedFragmentState.set(indices.h, indices.f);
  }

  function openDetail(id) {
    const target = document.getElementById(id);
    if (!target) return;
    saveCurrentFragment();
    const current = currentIndices();
    if (current.v === 0) detailReturnState.set(current.h, current.f);
    const indices = Reveal.getIndices(target);
    Reveal.slide(indices.h, indices.v || 0,
      target.classList.contains("main-slide") ? detailReturnState.get(indices.h) ?? savedFragmentState.get(indices.h) ?? -1 : -1);
  }

  function setLiteratureHome(slide) {
    if (!["using-results", "conclusion"].includes(slide?.id)) return;
    const table = document.getElementById("literature-measures");
    const back = table.querySelector("[data-detail-home-link]");
    table.dataset.detailHome = slide.id;
    back.href = "#/" + slide.id;
    back.textContent = slide.id === "conclusion" ? "↑ Back to the conclusion" : "↑ Back to the interactive figure";
  }

  function storyNext() {
    const indices = currentIndices();
    const branch = Reveal.getCurrentSlide();
    if (branch?.dataset.detailNext) {
      openDetail(branch.dataset.detailNext);
      return false;
    }
    if (indices.v > 0 && branch?.dataset.stepThroughBranch === "true" && branch.querySelector(".fragment:not(.visible)")) {
      Reveal.nextFragment();
      return false;
    }
    if (indices.v > 0) {
      Reveal.slide(indices.h + 1, 0);
      return false;
    }
    const slide = Reveal.getCurrentSlide();
    if (slide && slide.querySelector(".fragment:not(.visible)")) Reveal.nextFragment();
    else Reveal.slide(indices.h + 1, 0);
    return false;
  }

  function storyPrevious() {
    const indices = currentIndices();
    const branch = Reveal.getCurrentSlide();
    if (branch?.dataset.detailPrevious || branch?.dataset.detailHome) {
      openDetail(branch.dataset.detailPrevious || branch.dataset.detailHome);
      return false;
    }
    if (indices.v > 0 && branch?.dataset.stepThroughBranch === "true") {
      if (branch.querySelector(".fragment.visible")) Reveal.prevFragment();
      else Reveal.slide(indices.h, 0, savedFragmentState.get(indices.h) ?? -1);
      return false;
    }
    if (indices.v > 0) {
      Reveal.slide(Math.max(0, indices.h - 1), 0);
      return false;
    }
    const slide = Reveal.getCurrentSlide();
    if (slide && slide.querySelector(".fragment.visible")) Reveal.prevFragment();
    else Reveal.slide(Math.max(0, indices.h - 1), 0);
    return false;
  }

  function setupBranchControls() {
    // Handle these links before Reveal's own hash-link listener changes slides.
    document.addEventListener("click", (event) => {
      const detail = event.target.closest("[data-detail-target]");
      const home = event.target.closest("[data-detail-home-link]");
      if (detail || home) {
        event.preventDefault();
        event.stopPropagation();
        openDetail(detail ? detail.dataset.detailTarget : home.closest("[data-detail-home]")?.dataset.detailHome || "using-results");
      }
    }, true);
    document.addEventListener("click", (event) => {
      const button = event.target.closest("[data-branch]");
      if (!button) return;
      const action = button.dataset.branch;
      const indices = currentIndices();
      if (action === "down") {
        saveCurrentFragment();
        if (indices.v === 0) detailReturnState.set(indices.h, indices.f);
        if (Reveal.getCurrentSlide()?.dataset.directDetails === "true") Reveal.slide(indices.h, 1);
        else Reveal.down();
      } else if (action === "up") {
        Reveal.slide(indices.h, 0, savedFragmentState.get(indices.h) ?? -1);
      } else if (action === "next") {
        Reveal.slide(indices.h + 1, 0);
      }
    });
  }

  renderOpening();
  renderPairwiseWitness();
  renderWitnesses();
  renderElicitationExamples();
  validateData();
  setupBranchControls();
  document.querySelector("#moment-compass iframe").addEventListener("load", syncOriginalFigure);

  Reveal.initialize({
    width: window.innerWidth <= 760 ? window.innerWidth : 960,
    height: window.innerWidth <= 760 ? window.innerHeight : 700,
    margin: window.innerWidth <= 760 ? 0.025 : 0.04,
    center: window.innerWidth > 760,
    hash: true,
    controls: true,
    progress: true,
    slideNumber: "c/t",
    transition: "fade",
    transitionSpeed: "fast",
    preloadIframes: false,
    navigationMode: "default",
    keyboard: {
      32: storyNext,
      34: storyNext,
      39: storyNext,
      40: () => {
        if (Reveal.getCurrentSlide()?.id === "borda-elicitation" || Reveal.getCurrentSlide()?.dataset.directDetails === "true") {
          saveCurrentFragment();
          const indices = currentIndices();
          if (indices.v === 0) detailReturnState.set(indices.h, indices.f);
          Reveal.slide(currentIndices().h, 1);
        } else Reveal.down();
        return false;
      },
      38: () => {
        if (Reveal.getCurrentSlide()?.dataset.detailHome) {
          openDetail(Reveal.getCurrentSlide().dataset.detailHome);
        } else if (["borda-hoeffding-development", "warmup-definitions"].includes(Reveal.getCurrentSlide()?.id)) {
          const h = currentIndices().h;
          Reveal.slide(h, 0, savedFragmentState.get(h) ?? -1);
        } else Reveal.up();
        return false;
      },
      33: storyPrevious,
      37: storyPrevious
    }
  }).then(() => {
    renderMathInElement(document.querySelector(".reveal .slides"), {
      delimiters: [
        { left: "$$", right: "$$", display: true },
        { left: "\\[", right: "\\]", display: true },
        { left: "\\(", right: "\\)", display: false },
        { left: "$", right: "$", display: false }
      ],
      ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"],
      throwOnError: false
    });
    saveCurrentFragment();
    syncOriginalFigure();
    syncOpeningBuilds();
  });

  Reveal.on("fragmentshown", saveCurrentFragment);
  Reveal.on("fragmenthidden", saveCurrentFragment);
  Reveal.on("fragmentshown", syncOpeningBuilds);
  Reveal.on("fragmenthidden", syncOpeningBuilds);
  Reveal.on("slidechanged", syncOpeningBuilds);
  Reveal.on("fragmentshown", syncOriginalFigure);
  Reveal.on("fragmenthidden", syncOriginalFigure);
  Reveal.on("slidechanged", syncOriginalFigure);
  Reveal.on("slidechanged", (event) => {
    if (event.currentSlide?.id === "literature-measures") setLiteratureHome(event.previousSlide);
    // The sampling overview saves its fragment index before entering its branch.
    // Reveal marks the departed parent slide's fragments visible, so counting
    // them here would overwrite that saved position with the final build.
    if (event.previousSlide && event.previousSlide.classList.contains("main-slide") && event.previousSlide.id !== "borda-elicitation" && event.previousSlide.dataset.directDetails !== "true") {
      const previous = Reveal.getIndices(event.previousSlide);
      const visible = event.previousSlide.querySelectorAll(".fragment.visible").length;
      savedFragmentState.set(previous.h, visible - 1);
    }
  });
})();
