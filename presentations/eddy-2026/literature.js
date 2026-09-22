/* Optional literature branches, built before Reveal initializes. */
(function renderLiterature() {
  "use strict";
  const { references, measures } = window.EDDY_LITERATURE;
  const stack = document.getElementById("results-stack");
  const rows = document.getElementById("literature-measure-rows");
  const pageId = (measure, index = 0) => `measure-${measure.id}${index ? "-" + (index + 1) : ""}`;
  const referenceLink = key => {
    const ref = references[key];
    return ref.url ? `<a href="${ref.url}" target="_blank" rel="noopener noreferrer">${ref.short}</a>` :
      `<a href="#/literature-references" data-detail-target="literature-references">${ref.short}</a>`;
  };
  rows.innerHTML = measures.map(measure => `
    <tr data-detail-target="${pageId(measure)}">
      <th scope="row"><a href="#/${pageId(measure)}" data-detail-target="${pageId(measure)}">${measure.name}<span class="literature-row-arrow" aria-hidden="true"> →</span></a></th>
      <td>${measure.scope}</td><td class="literature-level">${measure.level}</td>
      <td>${measure.refs.filter(key => key !== "kendall").map(key => references[key].short).join("<br>")}</td>
    </tr>`).join("");
  measures.forEach(measure => measure.pages.forEach((page, index) => {
    const previous = index ? pageId(measure, index - 1) : "literature-measures";
    const next = index + 1 < measure.pages.length ? pageId(measure, index + 1) : "literature-measures";
    const section = document.createElement("section");
    section.id = pageId(measure, index);
    section.className = "technical literature-derivation";
    section.dataset.detailPrevious = previous;
    section.dataset.detailNext = next;
    section.dataset.detailHome = "literature-measures";
    section.innerHTML = `
      <p class="kicker">Worked derivation · level ${measure.level} · ${index + 1}/${measure.pages.length}</p>
      <h2>${page.title}</h2>
      <div class="derivation-content">${page.body}</div>
      <p class="derivation-source">Measure: ${measure.refs.filter(key => key !== "kendall").map(referenceLink).join("; ")}.
        <span>Plurality derivation: this work · supplied appendix.</span></p>
      <nav class="literature-nav" aria-label="Derivation navigation">
        <a href="#/${previous}" data-detail-target="${previous}">${index ? "← Previous step" : "← Measures table"}</a>
        ${index ? '<a href="#/literature-measures" data-detail-target="literature-measures">Measures table</a>' : ""}
        <a href="#/${next}" data-detail-target="${next}">${index + 1 < measure.pages.length ? "Continue derivation →" : "Back to measures table →"}</a>
      </nav>`;
    stack.appendChild(section);
  }));
  [["borda", "alcalde", "can", "hashemi"], ["colley", "navarrete", "delemazure", "kendall"]].forEach((keys, index) => {
    const section = document.createElement("section");
    section.id = index ? "literature-references-2" : "literature-references";
    section.className = "technical literature-references";
    section.dataset.detailHome = "literature-measures";
    section.dataset.detailPrevious = index ? "literature-references" : "literature-measures";
    section.dataset.detailNext = index ? "literature-measures" : "literature-references-2";
    section.innerHTML = `<p class="kicker">Bibliographic pointers · ${index + 1}/2</p><h2>Original measures and related work</h2>
      <ol class="literature-reference-list" start="${index * 4 + 1}">${keys.map(key => {
        const ref = references[key];
        return `<li><p>${ref.url ? `<a href="${ref.url}" target="_blank" rel="noopener noreferrer">${ref.full}</a>` : ref.full}</p><p class="reference-note">${ref.note}</p></li>`;
      }).join("")}</ol>
      <nav class="literature-nav" aria-label="Bibliography navigation"><a href="#/literature-measures" data-detail-target="literature-measures">← Measures table</a><a href="#/${section.dataset.detailNext}" data-detail-target="${section.dataset.detailNext}">${index ? "Back to measures table →" : "More references →"}</a></nav>
      `;
    stack.appendChild(section);
  });
})();
