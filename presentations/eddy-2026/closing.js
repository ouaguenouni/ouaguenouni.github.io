(function () {
  "use strict";
  document.querySelector('#conclusion [data-branch="down"]').addEventListener("click", event => {
    event.stopPropagation();
    Reveal.slide(Reveal.getIndices().h, 1);
  });
})();
