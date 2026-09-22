const assert = require("node:assert/strict");
const { references, measures } = require("./literature-data.js");
const near = (a, b, why) => assert.ok(Math.abs(a - b) < 1e-10, why + ": " + a + " != " + b);
const permutations = xs => xs.length ? xs.flatMap(x => permutations(xs.filter(y => y !== x)).map(tail => [x, ...tail])) : [[]];
const pairs = xs => xs.flatMap((a, i) => xs.slice(i + 1).map(b => [a, b]));
assert.equal(measures.length, 8);
assert.equal(new Set(measures.map(m => m.id)).size, 8);
assert.equal(measures.flatMap(m => m.pages).length, 11);
measures.forEach(m => {
  m.refs.forEach(key => assert.ok(references[key], "Every measure has resolved references"));
  m.pages.forEach(page => assert.ok(page.title && page.body.includes("derivation-result") || page.body.includes("derivation-step")));
});
let checked = 0;
for (let m = 2; m <= 4; m++) {
  const alternatives = Array.from({ length: m }, (_, i) => i);
  const orders = permutations(alternatives), allPairs = pairs(alternatives);
  const profiles = [
    orders.map(order => ({ order, weight: 1 / orders.length })),
    ...orders.map(order => [{ order, weight: 1 }]),
    [{ order: orders[0], weight: .5 }, { order: orders.at(-1), weight: .5 }],
    ...Array.from({ length: 7 }, (_, seed) => {
      const weights = orders.map((_, i) => ((i * 17 + seed * 13 + i * i) % 29) + 1);
      const total = weights.reduce((s, w) => s + w, 0);
      return orders.map((order, i) => ({ order, weight: weights[i] / total }));
    })
  ];
  for (const profile of profiles) {
    const E = f => profile.reduce((sum, row) => sum + row.weight * f(row.order), 0);
    const before = (order, a, b) => order.indexOf(a) < order.indexOf(b);
    const p = (a, b) => E(order => Number(before(order, a, b)));
    const cell = (subset, a) => E(order => Number(subset.every(b => b === a || before(order, a, b))));
    const R = a => alternatives.filter(b => b !== a).reduce((s, b) => s + p(a, b), 0);
    const agreement = allPairs.reduce((s, [a, b]) => s + Math.abs(2 * p(a, b) - 1), 0) / allPairs.length;
    const partitionMean = allPairs.reduce((s, [a, b]) => s + 2 * Math.min(p(a, b), 1 - p(a, b)), 0) / allPairs.length;
    near(1 - agreement, partitionMean, "Agreement/polarization complement");
    const ktDirect = profile.reduce((sum, first) => sum + first.weight * profile.reduce((total, second) =>
      total + second.weight * allPairs.filter(([a, b]) => before(first.order, a, b) !== before(second.order, a, b)).length, 0), 0);
    const ktCells = 2 * allPairs.reduce((s, [a, b]) => s + p(a, b) * (1 - p(a, b)), 0);
    near(ktDirect, ktCells, "Independent-draw Kendall diversity");
    for (const a of alternatives) {
      const others = alternatives.filter(b => b !== a);
      near(1 + R(a), E(order => m - order.indexOf(a)), "Deck Borda convention");
      const meanRank = E(order => order.indexOf(a) + 1);
      const variance = E(order => (order.indexOf(a) + 1 - meanRank) ** 2);
      const triples = pairs(others).reduce((sum, [b, c]) => sum + cell([a, b, c], a), 0);
      near(variance, R(a) * (1 - R(a)) + 2 * triples, "Rank-variance plurality expansion");
      for (const alpha of [0, .5, 1]) {
        let direct = 0, matrix = 0;
        for (const b of others) {
          const prob = p(a, b);
          if (prob < 1e-12 || 1 - prob < 1e-12) continue; // Empty-camp convention.
          const conditionalWins = positive => E(order => Number(before(order, a, b) === positive) *
            (m - 1 - order.indexOf(a))) / (positive ? prob : 1 - prob);
          const S = others.filter(c => c !== b).reduce((s, c) => s + p(a, c), 0);
          const T = others.filter(c => c !== b).reduce((s, c) => s + cell([a, b, c], a), 0);
          near(conditionalWins(true), 1 + T / prob, "Positive conditional Borda");
          near(conditionalWins(false), (S - T) / (1 - prob), "Negative conditional Borda");
          const weight = (prob * (1 - prob)) ** alpha;
          direct += weight * Math.abs(conditionalWins(true) - conditionalWins(false));
          matrix += weight * Math.abs(1 + (T - prob * S) / (prob * (1 - prob)));
        }
        near(direct / (m - 1), matrix / (m - 1), "Navarrete / alpha-divisiveness");
      }
    }
    for (const [a, b] of allPairs) {
      const other = alternatives.filter(c => c !== a && c !== b);
      other.forEach(c => near(E(order => Number((order.indexOf(c) - order.indexOf(a)) *
        (order.indexOf(c) - order.indexOf(b)) < 0)), 2 - p(a, c) - p(b, c) - 2 * cell([a, b, c], c), "Between identity"));
      const gap = E(order => Math.abs(order.indexOf(a) - order.indexOf(b)));
      const formula = 2 * (m - 1) - R(a) - R(b) - 2 * other.reduce((s, c) => s + cell([a, b, c], c), 0);
      near(gap / (m - 1), formula / (m - 1), "Discrepancy plurality formula");
    }
    checked++;
  }
}
console.log("Literature validation passed: 8 measures / 11 derivation pages; all identities agree on " + checked + " profiles, including unanimous and mixed profiles.");
