/* Mean pair-coverage benchmarks and implementable merge-sort cost bounds. */
(function (root) {
  "use strict";
  function makeExample(m = 10, epsilon = .05, delta = .05) {
    const pairs = m * (m - 1) / 2;
    const samplesPerPair = Math.ceil(Math.log(2 * pairs / delta) / (2 * epsilon ** 2));
    const rows = Array.from({ length:m - 1 }, (_, index) => {
      const k = index + 2;
      const pairsPerVoter = k * (k - 1) / 2;
      const depth = Math.ceil(Math.log2(k));
      return {
        k, pairsPerVoter,
        population:Math.ceil(pairs * samplesPerPair / pairsPerVoter),
        comparisons:k * depth - 2 ** depth + 1
      };
    });
    return { m, epsilon, delta, pairs, samplesPerPair, rows };
  }
  const api = { makeExample };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.EDDY_SAMPLING = api;
})(typeof window !== "undefined" ? window : globalThis);
