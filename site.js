/* ---------------------------------------------------------------------------
 * site.js — the "alive" layer for the homepage and the talks listing.
 *
 * Homepage: a tabbed page (Research shown by default; the rest revealed on
 * demand) with the reveal.js deck's motion — items ease up when their panel is
 * shown, a self-locating sticky tab bar, and the accent progress bar. Tabs are
 * deep-linkable via the URL hash (#research, #publications, …) so cross-page
 * links and the back button work.
 *
 * Talks listing (no tabs): the same items ease up on scroll instead.
 *
 * The hidden initial state lives in style.css under `.js`; the `.js` class is
 * set synchronously in the page <head>, so there is no flash of unstyled
 * content. Without JS, every panel is simply shown. Everything degrades
 * gracefully without IntersectionObserver too.
 * ------------------------------------------------------------------------- */
(function () {
  'use strict';

  var docEl = document.documentElement;
  docEl.classList.add('js'); // idempotent — the head shim already added it

  var reduce = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var RISE = '12px';

  // Elements that ease up. Kept in sync with the matching block in style.css.
  var REVEAL = [
    '.kicker', '.panel > h2', '.block > h2', '.block-note', '.intro p',
    '.theme', '.pub', '.course', '.article-item', '.talk.featured',
    '.talklist li', 'h3.sub', '.more', '.preview-cta-wrap', '.video-card', '.service'
  ].join(',');

  /* ---- lazy YouTube: swap the thumbnail facade for the embed on click ---- */
  [].forEach.call(document.querySelectorAll('.yt-facade'), function (btn) {
    btn.addEventListener('click', function () {
      var id = btn.getAttribute('data-id');
      var start = parseInt(btn.getAttribute('data-start'), 10) || 0;
      var ifr = document.createElement('iframe');
      ifr.className = 'video-iframe';
      ifr.src = 'https://www.youtube-nocookie.com/embed/' + id +
        '?autoplay=1&rel=0' + (start > 0 ? '&start=' + start : '');
      ifr.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      ifr.setAttribute('allowfullscreen', '');
      ifr.setAttribute('title', btn.getAttribute('aria-label') || 'YouTube video');
      btn.replaceWith(ifr);
    });
  });

  function reveal(el, delay) {
    el.style.transitionDelay = (delay || 0) + 'ms';
    el.style.opacity = '1';
    el.style.translate = '0 0';
  }
  function hide(el) {
    el.style.transition = 'none';
    el.style.opacity = '0';
    el.style.translate = '0 ' + RISE;
  }

  /* ====================================================================== *
   *  Tabbed homepage                                                        *
   * ====================================================================== */
  var tabs = [].slice.call(document.querySelectorAll('.tabs .tab[data-tab]'));
  var panels = {};
  [].forEach.call(document.querySelectorAll('.panel'), function (p) {
    panels[p.id.replace('panel-', '')] = p;
  });
  var hasTabs = tabs.length > 0 && Object.keys(panels).length > 0;

  function animateIn(panel) {
    var items = [].slice.call(panel.querySelectorAll(REVEAL));
    if (reduce) { items.forEach(function (el) { reveal(el, 0); }); return; }
    items.forEach(hide);
    // force reflow so the "hidden" state is committed before we transition in
    void panel.offsetWidth;
    items.forEach(function (el, i) {
      el.style.transition = '';
      reveal(el, Math.min(i, 10) * 45);
    });
  }

  function activate(name, opts) {
    opts = opts || {};
    if (!panels[name]) name = 'research';
    tabs.forEach(function (t) {
      var on = t.dataset.tab === name;
      t.classList.toggle('active', on);
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
    });
    Object.keys(panels).forEach(function (k) {
      var on = k === name;
      panels[k].classList.toggle('active', on);
      panels[k].hidden = !on;
    });
    animateIn(panels[name]);
    if (opts.focus) { var ct = document.getElementById('tab-' + name); if (ct) ct.focus(); }
    if (opts.scroll) window.scrollTo(0, 0);
    if (opts.push && ('#' + name) !== location.hash) {
      history.replaceState(null, '', '#' + name);
    }
    if (typeof updateBar === 'function') updateBar();
  }

  if (hasTabs) {
    tabs.forEach(function (t, idx) {
      t.addEventListener('click', function (e) {
        e.preventDefault();
        activate(t.dataset.tab, { push: true, scroll: true });
      });
      t.addEventListener('keydown', function (e) {
        var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (!d) return;
        e.preventDefault();
        var next = tabs[(idx + d + tabs.length) % tabs.length];
        activate(next.dataset.tab, { push: true, focus: true });
      });
    });
    window.addEventListener('hashchange', function () {
      activate(location.hash.slice(1), {});
    });
    // initial tab from the URL hash (deep link / back button), else Research
    activate(location.hash.slice(1) || 'research', {});
  } else {
    /* ---- talks listing: ease items up on scroll ---- */
    var items = [].slice.call(document.querySelectorAll(REVEAL));
    if (reduce || !('IntersectionObserver' in window)) {
      items.forEach(function (el) { reveal(el, 0); });
    } else {
      var counters = new Map();
      items.forEach(function (el) {
        var p = el.parentNode;
        var i = counters.get(p) || 0;
        counters.set(p, i + 1);
        el.dataset.d = Math.min(i, 8) * 55;
      });
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { reveal(e.target, +e.target.dataset.d || 0); io.unobserve(e.target); }
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
      items.forEach(function (el) { io.observe(el); });
    }
  }

  /* ====================================================================== *
   *  Shared chrome: sticky-nav backdrop + accent progress bar              *
   * ====================================================================== */
  var nav = document.querySelector('.masthead .topnav');
  if (nav && 'IntersectionObserver' in window) {
    var sentinel = document.createElement('div');
    sentinel.className = 'nav-sentinel';
    nav.parentNode.insertBefore(sentinel, nav);
    new IntersectionObserver(function (entries) {
      nav.classList.toggle('stuck', !entries[0].isIntersecting);
    }, { threshold: 0 }).observe(sentinel);
  }

  var bar = document.querySelector('.scroll-progress');
  var ticking = false;
  function updateBar() {
    if (!bar || reduce) return;
    var max = docEl.scrollHeight - docEl.clientHeight;
    var y = window.pageYOffset || docEl.scrollTop;
    bar.style.width = (max > 0 ? (y / max) * 100 : 0) + '%';
    ticking = false;
  }
  if (bar && !reduce) {
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; window.requestAnimationFrame(updateBar); }
    }, { passive: true });
    window.addEventListener('resize', updateBar, { passive: true });
    updateBar();
  }
})();
