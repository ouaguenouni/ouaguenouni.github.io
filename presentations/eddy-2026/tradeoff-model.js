(function (root) {
  "use strict";
  function frontier(points, level) {
    let best = Infinity;
    return points.filter(p => p.ell === level).slice().sort((a, b) => a.mcl - b.mcl || a.N - b.N).filter(p => {
      if (p.N >= best) return false;
      best = p.N;
      return true;
    });
  }
  function pick(points, level, index) {
    const rows = frontier(points, level);
    return rows[Math.max(0, Math.min(rows.length - 1, Math.round(index)))];
  }
  const model = { frontier, pick };
  if (typeof module !== "undefined" && module.exports) module.exports = model;
  else root.TradeoffModel = model;
})(typeof window !== "undefined" ? window : globalThis);
