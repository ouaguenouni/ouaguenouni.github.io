/* reader-notes.html is the only authored source of speaker notes. */
(function () {
  "use strict";
  window.RevealReaderNotes = {
    id: "reader-notes",
    async init(deck) {
      const slides = deck.getSlidesElement();
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 5000);
      slides.dataset.readerNotes = "loading";
      try {
        // Bypass cached copies so saving the notes file + reloading is enough.
        const response = await fetch("reader-notes.html", {
          cache: "no-store", signal: controller.signal
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const source = new DOMParser().parseFromString(await response.text(), "text/html");
        for (const entry of source.querySelectorAll("section[data-slide]")) {
          const slide = document.getElementById(entry.dataset.slide);
          // Only the direct note body: never collect a child detail slide's notes.
          const body = entry.querySelector(":scope > .note-body");
          if (!body || !slide?.matches("section") || !slides.contains(slide)) continue;
          slide.querySelectorAll(":scope > aside.notes[data-reader-notes]").forEach(note => note.remove());
          const note = document.createElement("aside");
          note.className = "notes";
          note.dataset.readerNotes = "true";
          note.hidden = true;
          note.setAttribute("aria-hidden", "true");
          note.innerHTML = body.innerHTML;
          slide.appendChild(note);
        }
        slides.dataset.readerNotes = "loaded";
      } catch (error) {
        // A missing file must not prevent the presentation from starting.
        slides.dataset.readerNotes = "error";
        console.warn("Could not load reader-notes.html. Serve the presentation over HTTP and reload to retry.", error);
      } finally {
        clearTimeout(timeout);
      }
    }
  };
})();
