const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const code = fs.readFileSync(require.resolve("./speaker-notes.js"), "utf8");

// Tiny DOM doubles keep this loader's lifecycle tests dependency-free.
function fixture({ failure, timeout = false } = {}) {
  const main = { innerHTML: "<p>A <strong>main-slide</strong> note.</p>" };
  const detail = { innerHTML: "<ul><li>Only the detail slide.</li></ul>" };
  const empty = { innerHTML: "<!-- Write your notes here. -->" };
  const entries = [["main", main], ["detail", detail], ["empty", empty], ["unknown", main], ["outside", main]];
  const source = {
    querySelectorAll(selector) {
      assert.equal(selector, "section[data-slide]");
      return entries.map(([id, body]) => ({
        dataset: { slide: id },
        querySelector(selector) {
          assert.equal(selector, ":scope > .note-body", "Nested detail notes must not leak into their parent");
          return body;
        }
      }));
    }
  };
  const targets = Object.fromEntries(["main", "detail", "empty", "outside"].map(id => [id, {
    notes: [], matches: selector => selector === "section",
    querySelectorAll(selector) {
      assert.equal(selector, ":scope > aside.notes[data-reader-notes]");
      return [...this.notes];
    },
    appendChild(note) {
      this.notes.push(note);
      note.remove = () => { this.notes = this.notes.filter(other => other !== note); };
    }
  }]));
  const slides = { dataset: {}, contains: node => node !== targets.outside };
  const calls = [], warnings = [];
  let cleared = false;
  const scope = {
    window: {}, AbortController,
    console: { warn: (...args) => warnings.push(args) },
    setTimeout(callback, delay) {
      assert.equal(delay, 5000);
      if (timeout) queueMicrotask(callback);
      return 123;
    },
    clearTimeout(id) { assert.equal(id, 123); cleared = true; },
    document: {
      getElementById: id => targets[id],
      createElement(tag) {
        assert.equal(tag, "aside");
        return { dataset: {}, attributes: {}, setAttribute(name, value) { this.attributes[name] = value; } };
      }
    },
    DOMParser: class {
      parseFromString(html, type) { assert.equal(html, "fixture"); assert.equal(type, "text/html"); return source; }
    },
    async fetch(url, options) {
      assert.equal(url, "reader-notes.html");
      assert.equal(options.cache, "no-store");
      calls.push(options);
      if (failure === "network") throw new Error("Network unavailable");
      if (timeout) return new Promise((resolve, reject) => options.signal.addEventListener("abort", () => reject(new Error("Timeout"))));
      return { ok: !failure, status: failure || 200, text: async () => "fixture" };
    }
  };
  vm.runInNewContext(code, scope);
  return { plugin: scope.window.RevealReaderNotes, deck: { getSlidesElement: () => slides }, slides, targets, main, detail, empty, calls, warnings, cleared: () => cleared };
}

(async () => {
  const test = fixture();
  await test.plugin.init(test.deck);
  assert.equal(test.slides.dataset.readerNotes, "loaded");
  for (const key of ["main", "detail", "empty"]) {
    const [note] = test.targets[key].notes;
    assert.equal(note.innerHTML, test[key].innerHTML, `${key}: preserve only authored HTML`);
    assert.equal(note.hidden, true);
    assert.equal(note.attributes["aria-hidden"], "true");
    assert.equal(note.className, "notes");
  }
  assert.equal(test.targets.outside.notes.length, 0);
  assert.ok(test.cleared());
  test.main.innerHTML = "<p>Updated saved notes.</p>";
  await test.plugin.init(test.deck);
  assert.equal(test.calls.length, 2);
  assert.equal(test.targets.main.notes.length, 1, "Reload replaces notes instead of duplicating them");
  assert.equal(test.targets.main.notes[0].innerHTML, test.main.innerHTML);
  for (const options of [{ failure: 404 }, { failure: "network" }, { timeout: true }]) {
    const broken = fixture(options);
    await broken.plugin.init(broken.deck);
    assert.equal(broken.slides.dataset.readerNotes, "error");
    assert.equal(broken.warnings.length, 1);
    assert.ok(broken.cleared(), "A failed notes request must not block Reveal initialization");
  }
  console.log("Speaker-notes validation passed: HTML, separate detail notes, empty entries, fresh reloads, and non-blocking HTTP/network/timeout errors.");
})().catch(error => { console.error(error); process.exitCode = 1; });
