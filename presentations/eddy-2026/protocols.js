(function () {
"use strict";
// Animation adapted from the original elicitation presentation.
    var RANK = ['c', 'a', 'd', 'b'];                 // the voter's ranking (ranking slide): c≻a≻d≻b
    var RSUBS = ['ab','ac','ad','bc','bd','cd','abc','abd','acd','bcd','abcd']; // every subset of {a,b,c,d}
    var QORD = ['b', 'd', 'a', 'c'];                 // the random query order (chain slide)
    var PREFC = { c: 0, a: 1, d: 2, b: 3 };          // the chain voter's preference c≻a≻d≻b resolves a knockout
    var SX = [20, 96, 172, 248], SY = 13;            // the four ordered slot positions inside the centred .kseq
    var T1 = null, T2 = null;
    function lt(s) { var m = {}; [].forEach.call(s.querySelectorAll('.lt'), function (l) { m[l.dataset.n] = l; }); return m; }
    function clr(e) { e.classList.remove('hl', 'hlg', 'dim'); }
    function put(e, x) { e.style.transform = 'translate(' + x + 'px,' + SY + 'px)'; }
    function conns(s) { return [].slice.call(s.querySelectorAll('.kconn')); }
    function cnt(s) { return s.querySelector('.kcount'); }
    function smps(s) { return [].slice.call(s.querySelectorAll('.smp')); }
    function smpShow(s, key) { var e = s.querySelector('.smp[data-s="' + key + '"]'); if (e) e.classList.add('show'); }
    function smpReset(s) { smps(s).forEach(function (e) { e.classList.remove('show'); }); }
    function stepN(s) { var n = 0; [].forEach.call(s.querySelectorAll('.step'), function (f) { if (f.classList.contains('visible')) n++; }); return n; }
    function hide(s) { var m = lt(s); ['a','b','c','d'].forEach(function (n) { m[n].classList.remove('on'); clr(m[n]); }); conns(s).forEach(function (c) { c.style.opacity = '0'; }); smpReset(s); cnt(s).innerHTML = ''; }
    function row(s) { var m = lt(s); ['a','b','c','d'].forEach(function (n, i) { m[n].classList.add('on'); clr(m[n]); put(m[n], SX[i]); }); conns(s).forEach(function (c) { c.style.opacity = '0'; }); smpReset(s); cnt(s).innerHTML = ''; }
    function order(s, ord) { var m = lt(s); ord.forEach(function (n, i) { m[n].classList.add('on'); clr(m[n]); put(m[n], SX[i]); }); conns(s).forEach(function (c, i) { c.style.left = ((SX[i] + 38 + SX[i + 1]) / 2) + 'px'; c.style.top = SY + 'px'; c.style.opacity = '1'; }); smpReset(s); cnt(s).innerHTML = ''; }
    function stop(s) { clearTimeout(T1); clearTimeout(T2); s.dataset.play = ''; var m = lt(s); ['a','b','c','d'].forEach(function (n) { clr(m[n]); }); smpReset(s); cnt(s).innerHTML = ''; }

    function playRank(s) {
      if (s.dataset.play === '1') return; s.dataset.play = '1';
      var m = lt(s), i = 0, c = 0;
      (function tick() {
        if (s.dataset.play !== '1') return;
        if (i >= RSUBS.length) { ['a','b','c','d'].forEach(function (n) { clr(m[n]); }); cnt(s).innerHTML = '<b>' + c + '</b> subset observations'; return; }
        var key = RSUBS[i], mem = key.split('');
        ['a','b','c','d'].forEach(function (n) { clr(m[n]); if (mem.indexOf(n) < 0) m[n].classList.add('dim'); });
        mem.forEach(function (n) { m[n].classList.add('hl'); });
        smpShow(s, key);
        c++; cnt(s).innerHTML = 'sample <b>' + c + '</b> &nbsp;/&nbsp; 11';
        i++; T1 = setTimeout(tick, 600);
      })();
    }
    function playChain(s) {
      if (s.dataset.play === '1') return; s.dataset.play = '1';
      var m = lt(s), i = 1, c = 0, champ = QORD[0], pre = [QORD[0]];
      m[champ].classList.add('hlg');
      (function tick() {
        if (s.dataset.play !== '1') return;
        if (i >= QORD.length) { cnt(s).innerHTML = '<b>' + c + '</b> subset observations'; return; }
        var ch = QORD[i], a0 = champ; pre.push(ch);
        m[ch].classList.remove('dim'); m[ch].classList.add('hl');
        cnt(s).innerHTML = '<span class="vs">(' + a0 + ' ? ' + ch + ')</span>';
        T2 = setTimeout(function () {
          if (s.dataset.play !== '1') return;
          var w = PREFC[a0] < PREFC[ch] ? a0 : ch, lo = (w === a0) ? ch : a0;
          m[lo].classList.remove('hl', 'hlg'); m[lo].classList.add('dim');
          m[w].classList.remove('hl'); m[w].classList.add('hlg');
          champ = w; c++;
          smpShow(s, pre.slice().sort().join(''));
          cnt(s).innerHTML = '<span class="vs">(' + a0 + ' ? ' + ch + ')</span> &rArr; ' + w + ' &#8827; ' + lo;
          i++; T1 = setTimeout(tick, 1250);
        }, 850);
      })();
    }
    // final step: the sample cells SHIFT (FLIP) from the wrap into degree columns
    function classify(s) {
      if (s.dataset.classified === '1') return; s.dataset.classified = '1';
      clearTimeout(T1); clearTimeout(T2); s.dataset.play = '';
      var m = lt(s); ['a','b','c','d'].forEach(function (n) { clr(m[n]); });
      var ks = s.querySelector('.ksamps'), els = smps(s);
      els.forEach(function (e) { e.classList.add('show'); e.style.transition = 'none'; e.style.transform = ''; });
      cnt(s).innerHTML = '<b>' + els.length + '</b> subset observations';
      var scale = Reveal.getScale() || 1;
      var first = els.map(function (e) { return e.getBoundingClientRect(); });
      ks.classList.add('classified');
      var last = els.map(function (e) { return e.getBoundingClientRect(); });
      els.forEach(function (e, i) { e.style.transform = 'translate(' + ((first[i].left - last[i].left) / scale) + 'px,' + ((first[i].top - last[i].top) / scale) + 'px)'; });
      void ks.offsetWidth;
      els.forEach(function (e) { e.style.transition = 'transform .65s var(--ease), opacity .35s ease'; e.style.transform = 'translate(0,0)'; });
    }
    function unclassify(s) {
      s.dataset.classified = '';
      var ks = s.querySelector('.ksamps'); if (ks) ks.classList.remove('classified');
      smps(s).forEach(function (e) { e.style.transition = ''; e.style.transform = ''; });
    }

    const root = document.getElementById("protocol-examples");
    const panels = [...root.querySelectorAll(".protocol-panel")];
    let last = "";
    function syncProtocols() {
      const active = root.classList.contains("present");
      const steps = [...root.querySelectorAll(".protocol-step.visible")];
      const build = steps.length ? Math.max(...steps.map(f => Number(f.dataset.fragmentIndex))) + 1 : 0;
      const key = active + ":" + build;
      if (key === last) return;
      last = key;
      panels.forEach(s => { stop(s); unclassify(s); hide(s); });
      const which = build >= 4 ? 1 : 0;
      panels.forEach((s, i) => { s.classList.toggle("protocol-active", i === which); s.setAttribute("aria-hidden", String(i !== which)); });
      if (!active) return;
      const s = panels[which], phase = build % 4 + 1;
      const scene = s.querySelector(".scene");
      [1,2,3,4].forEach(n => scene.classList.toggle("s" + n, phase >= n));
      if (phase === 1) row(s);
      else {
        order(s, which ? QORD : RANK);
        if (phase === 3) {
          if (matchMedia("(prefers-reduced-motion: reduce)").matches) classify(s);
          else if (which) playChain(s); else playRank(s);
        } else if (phase === 4) classify(s);
      }
    }
    ["ready","slidechanged","fragmentshown","fragmenthidden"].forEach(event => Reveal.on(event, syncProtocols));
    document.querySelector('#samples-per-level [data-branch="down"]').addEventListener("click", event => {
      event.stopPropagation();
      Reveal.slide(Reveal.getIndices().h, 1);
    });
    syncProtocols();
})();
