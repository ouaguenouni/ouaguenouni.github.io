const assert = require("node:assert/strict");
const DATA = require("./data.js");

// Independently compare rank-based and pairwise scores, including every point mass.
const expectedScores = { A: 2.35, B: 2, C: 1.65 };
const expectedHistograms = { A: [.6, .15, .25], B: [.3, .4, .3], C: [.1, .45, .45] };
const near = (actual, expected, message) => assert.ok(Math.abs(actual - expected) < 1e-12, message);
near(DATA.winnerProfile.reduce((sum, row) => sum + row.weight, 0), 1, "Opening profile is normalized");
DATA.alternatives.forEach(a => {
  const histogram = DATA.alternatives.map((_, rank) =>
    DATA.winnerProfile.reduce((sum, row) => sum + (row.order[rank] === a ? row.weight : 0), 0));
  histogram.forEach((p, rank) => near(p, expectedHistograms[a][rank], a + ": rank probability"));
  const rankScore = histogram.reduce((sum, p, rank) => sum + p * (3 - rank), 0);
  const pairwiseScore = 1 + DATA.alternatives.filter(b => b !== a).reduce((sum, b) =>
    sum + DATA.winnerProfile.reduce((total, row) =>
      total + (row.order.indexOf(a) < row.order.indexOf(b) ? row.weight : 0), 0), 0);
  near(rankScore, expectedScores[a], a + ": displayed Borda score");
  near(pairwiseScore, rankScore, a + ": tournament and rank scores agree");
});
DATA.winnerProfile.forEach(({ order }) => {
  DATA.alternatives.forEach(a => {
    const rank = order.indexOf(a) + 1;
    const beaten = DATA.alternatives.filter(b => order.indexOf(a) < order.indexOf(b)).length;
    assert.equal(3 + 1 - rank, 1 + beaten, "Borda identity for " + order + ", " + a);
  });
});
console.log("Opening validation passed: rank histograms, displayed Borda scores, and tournament identity agree.");

// The animated example starts from exactly 20 individual rankings.
const illustrativeCounts = DATA.winnerProfile.map(row => Math.round(20 * row.weight));
assert.deepEqual(illustrativeCounts, [7, 5, 2, 4, 1, 1]);
assert.equal(illustrativeCounts.reduce((sum, count) => sum + count, 0), 20);
DATA.winnerProfile.forEach((row, i) => near(illustrativeCounts[i] / 20, row.weight, "Count normalization: " + row.order));
DATA.alternatives.forEach(a => [0, 1, 2].forEach(rank => {
  const matchingCount = DATA.winnerProfile.reduce((sum, row, i) => sum + (row.order[rank] === a ? illustrativeCounts[i] : 0), 0);
  near(matchingCount / 20, expectedHistograms[a][rank], "Animated histogram: " + a + ", rank " + (rank + 1));
}));
console.log("Illustrative example validation passed: 20 people, six exact counts, normalization, and all nine bars agree.");

// Card 9: recompute the complete example matrix independently from rankings.
const four = DATA.pluralityExample;
near(four.profile.reduce((sum, row) => sum + row.weight, 0), 1, "Four-alternative profile normalization");
const expectedRows = {
  AB: [.6, .4], AC: [.7, .3], AD: [.7, .3], BC: [.7, .3], BD: [.7, .3], CD: [.9, .1],
  ABC: [.4, .3, .3], ABD: [.4, .3, .3], ACD: [.7, .2, .1], BCD: [.7, .2, .1], ABCD: [.4, .3, .2, .1]
};
for (const [set, expected] of Object.entries(expectedRows)) {
  const sums = Object.fromEntries([...set].map(a => [a, 0]));
  four.profile.forEach(row => { sums[[...row.order].find(a => set.includes(a))] += row.weight; });
  [...set].forEach((a, i) => near(sums[a], expected[i], set + ": plurality of " + a));
  near(Object.values(sums).reduce((a, b) => a + b, 0), 1, set + ": row sums to one");
}

// Card 11: compare the displayed finite-difference formula with direct central
// moments for every candidate, every point mass, and nonuniform full-support profiles.
function permutations(items) {
  if (items.length === 0) return [[]];
  return items.flatMap((a, i) => permutations(items.filter((_, j) => j !== i)).map(tail => [a, ...tail]));
}
for (let m = 3; m <= 6; m += 1) {
  const alternatives = Array.from({ length: m }, (_, i) => String.fromCharCode(65 + i));
  const orders = permutations(alternatives);
  const weights = orders.map((_, i) => 1 + (i * 13 % 29));
  const total = weights.reduce((a, b) => a + b, 0);
  const profiles = [orders.map((order, i) => ({ order, weight: weights[i] / total })),
    ...orders.map(order => [{ order, weight: 1 }])];
  for (const profile of profiles) for (const a of alternatives) {
    const mu = profile.reduce((sum, row) => sum + row.weight * (row.order.indexOf(a) + 1), 0);
    const q = m - mu; // Borda score minus 1, for the m,...,1 convention.
    const aggregates = [1];
    for (let s = 1; s < m; s += 1) {
      aggregates[s] = combinations(alternatives.filter(b => b !== a), s).reduce((sum, subset) =>
        sum + profile.reduce((mass, row) => mass + (subset.every(b => row.order.indexOf(a) < row.order.indexOf(b)) ? row.weight : 0), 0), 0);
    }
    for (let k = 1; k < m; k += 1) {
      const direct = profile.reduce((sum, row) => sum + row.weight * (row.order.indexOf(a) + 1 - mu) ** k, 0);
      let fromMatrix = 0;
      for (let s = 0; s <= k; s += 1) {
        let coefficient = 0;
        for (let j = 0; j <= s; j += 1) coefficient += (-1) ** (s - j) * Number(choose(s, j)) * (j - q) ** k;
        fromMatrix += (-1) ** k * coefficient * aggregates[s];
      }
      assert.ok(Math.abs(fromMatrix - direct) < 1e-8, "Central-moment formula: m=" + m + ", k=" + k + ", a=" + a);
    }
  }
}
console.log("Framework validation passed: all 11 plurality rows and finite-difference moments (3–6 alternatives, including point masses) agree.");

// Card 15: simultaneous Hoeffding bound and pair coverage of uniform k-subsets.
for (let m = 2; m <= 30; m += 1) {
  const epsilon = .05, delta = .05, Q = m * (m - 1) / 2;
  const n = Math.ceil(Math.log(2 * Q / delta) / (2 * epsilon ** 2));
  assert.equal(n, Math.ceil(200 * Math.log(40 * Q)), "Simplified Hoeffding sample count");
  assert.ok(2 * Q * Math.exp(-2 * n * epsilon ** 2) <= delta + 1e-12);
  assert.ok(2 * Q * Math.exp(-2 * (n - 1) * epsilon ** 2) > delta - 1e-12, "Ceiling is minimal for the bound");
  for (let k = 2; k <= m; k += 1) {
    const q = k * (k - 1) / 2;
    const inclusion = Number(choose(m - 2, k - 2)) / Number(choose(m, k));
    near(inclusion, q / Q, "Fixed-pair subset inclusion probability");
    const benchmark = n * Q / q;
    assert.ok(Math.abs(benchmark * inclusion - n) < 1e-9, "Mean coverage equals n");
    if (k === m) assert.equal(benchmark, n, "Full ranking endpoint");
    if (k === 2) assert.equal(benchmark, Q * n, "Balanced pair endpoint");
  }
}
for (let m = 2; m <= 8; m += 1) {
  const alternatives = Array.from({ length: m }, (_, i) => i);
  for (let k = 2; k <= m; k += 1) {
    const subsets = combinations(alternatives, k);
    const counts = combinations(alternatives, 2).map(pair => subsets.filter(s => pair.every(a => s.includes(a))).length);
    counts.forEach(count => near(count / subsets.length, k * (k - 1) / (m * (m - 1)), "Enumerated pair coverage"));
  }
}
console.log("Elicitation validation passed: simultaneous Hoeffding threshold, both endpoints, and random-subset coverage identities.");

// Main sampling overview: fixed m=10 and illustrative k=5, with merge-sort cost bounds.
const overviewN = Math.ceil(200 * Math.log(40 * 45));
assert.equal(overviewN, 1500);
assert.equal(45 * overviewN, 67500);
assert.equal(45 * overviewN / 10, 6750);
function mergeSortWorstCase(t) {
  return t <= 1 ? 0 : mergeSortWorstCase(Math.floor(t / 2)) + mergeSortWorstCase(Math.ceil(t / 2)) + t - 1;
}
for (let t = 2; t <= 30; t++) {
  const depth = Math.ceil(Math.log2(t));
  assert.equal(mergeSortWorstCase(t), t * depth - 2 ** depth + 1);
}
assert.equal(mergeSortWorstCase(10), 25);
assert.equal(mergeSortWorstCase(5), 8);
console.log("Sampling overview validation passed: 1500 / 67500 / 6750 people and merge-sort caps 25 / 1 / 8.");

// Higher-degree sampling and the source-backed protocol selector.
for (let m = 3; m <= 12; m += 1) for (let ell = 2; ell <= m; ell += 1) {
  const rows = Number(choose(m, ell)), Q = ell * rows;
  const T = Math.ceil(Math.log(2 * Q / .05) / (2 * .05 ** 2));
  assert.ok(2 * Q * Math.exp(-2 * T * .05 ** 2) <= .05 + 1e-12);
  for (let k = ell; k <= m; k += 1) {
    const yieldPerRanking = Number(choose(k, ell));
    const inclusion = Number(choose(m - ell, k - ell)) / Number(choose(m, k));
    near(inclusion, yieldPerRanking / rows, "Degree-ell subset inclusion");
    assert.ok(Math.abs(rows * T / yieldPerRanking * inclusion - T) < 1e-8);
    if (k === ell) assert.equal(yieldPerRanking, 1, "No ranking reuse when k=ell");
  }
}
const frontierData = require("../elicitation-collective-disagreement/interactive_data/data/pareto.json");
const tradeoff = require("./tradeoff-model.js");
for (const level of frontierData.meta.ells) {
  const rows = tradeoff.frontier(frontierData.points, level);
  assert.deepEqual(rows.map(p => p.mcl), frontierData.frontier.N[level].x, "Original frontier x coordinates");
  assert.deepEqual(rows.map(p => p.N), frontierData.frontier.N[level].y, "Original frontier y coordinates");
  rows.forEach((p, index) => {
    assert.equal(tradeoff.pick(frontierData.points, level, index), p, "Load slider selects source protocol");
    const peopleIndex = rows.length - 1 - index;
    assert.equal(tradeoff.pick(frontierData.points, level, rows.length - 1 - peopleIndex), p, "People slider selects identical protocol");
    // Continuous handle positions must preserve the protocol until a midpoint threshold.
    if (index < rows.length - 1) {
      assert.equal(tradeoff.pick(frontierData.points, level, index + .01), p);
      assert.equal(tradeoff.pick(frontierData.points, level, index + .499), p);
      assert.equal(tradeoff.pick(frontierData.points, level, index + .501), rows[index + 1]);
      const fractionalPeople = rows.length - 1 - (index + .27);
      assert.equal(tradeoff.pick(frontierData.points, level, rows.length - 1 - fractionalPeople), p);
    }
    if (index) { assert.ok(p.mcl > rows[index - 1].mcl); assert.ok(p.N < rows[index - 1].N); }
  });
}
console.log("Protocol validation passed: higher-degree bounds, subset yields, and every linked-slider state match the original frontier.");

// Conclusion: full plurality information still need not determine cross-set joints.
const crossSetProfiles = [["abcd", "badc", "cdab", "dcba"], ["abdc", "bacd", "cdba", "dcab"]];
let fullCells = 0;
for (let degree = 2; degree <= 4; degree += 1) {
  for (const subset of combinations(["a", "b", "c", "d"], degree)) for (const a of subset) {
    const counts = crossSetProfiles.map(profile => profile.filter(order => subset.every(b => order.indexOf(a) <= order.indexOf(b))).length);
    assert.equal(counts[0], counts[1], "Cross-set witness has identical plurality cell " + subset + "/" + a);
    fullCells += 1;
  }
}
assert.equal(fullCells, 28);
const joint = crossSetProfiles.map(profile => profile.filter(order => order.indexOf("a") < order.indexOf("b") && order.indexOf("c") < order.indexOf("d")).length / 4);
assert.deepEqual(joint, [.5, 0]);
console.log("Conclusion validation passed: all 28 plurality cells agree, while the cross-set joint is 1/2 versus 0.");

const originalSource = require("../elicitation-collective-disagreement/interactive_data/data/synth_moment.json");
const original = DATA.originalWitnesses;
assert.equal(original.m, originalSource.meta.m);
const allOriginal = original.profiles.concat({ id: "U", support: Array.from({ length: original.m }, (_, i) => [i + 1, 1 / original.m]) });
for (const profile of allOriginal) {
  const close = (actual, expected, label) => assert.ok(Math.abs(actual - expected) < 1e-8, profile.id + ": " + label);
  close(profile.support.reduce((sum, [, p]) => sum + p, 0), 1, "normalization");
  profile.support.forEach(([rank, p]) => assert.ok(rank >= 1 && rank <= original.m && p >= 0));
  const mean = profile.support.reduce((sum, [rank, p]) => sum + rank * p, 0);
  const variance = profile.support.reduce((sum, [rank, p]) => sum + p * (rank - mean) ** 2, 0);
  close(mean, 128.5, "mean rank");
  close(variance, 5461.25, "rank variance");
  // Direct conditional Borda expectations, independent of the closed-form variance identity.
  let wins = 0, loses = 0, winScore = 0, loseScore = 0;
  for (const [rank, p] of profile.support) {
    const winMass = p * (original.m - rank) / (original.m - 1);
    const loseMass = p * (rank - 1) / (original.m - 1);
    wins += winMass; loses += loseMass;
    winScore += winMass * (original.m + 1 - rank);
    loseScore += loseMass * (original.m + 1 - rank);
  }
  close(Math.abs(winScore / wins - loseScore / loses), 257 / 3, "divisiveness");
  if (profile.id !== "U") {
    const sourceBins = originalSource.histograms.find(h => h.letter === profile.id).bins;
    assert.deepEqual(profile.bins, sourceBins, "Original histogram bins are preserved");
    const binned = Array(10).fill(0);
    for (const [rank, p] of profile.support) {
      const bin = binned.findIndex((_, i) => rank - 1 < Math.floor((i + 1) * original.m / 10));
      binned[bin] += p;
    }
    binned.forEach((p, i) => close(p, sourceBins[i], "recovered weights match source histogram"));
  }
}
console.log("Original witness validation passed: A, B, U, C, D are feasible and share the displayed variance and divisiveness; source histograms match.");

function choose(n, k) {
  if (k < 0 || k > n) return 0n;
  let value = 1n;
  for (let i = 1; i <= k; i += 1) value = value * BigInt(n - k + i) / BigInt(i);
  return value;
}

function combinations(items, size) {
  if (size === 0) return [[]];
  const output = [];
  for (let i = 0; i <= items.length - size; i += 1) {
    combinations(items.slice(i + 1), size - 1).forEach((tail) => output.push([items[i], ...tail]));
  }
  return output;
}

function equalFraction(left, right) {
  return left[0] * right[1] === right[0] * left[1];
}

function pluralityMatrix(profile) {
  const alternatives = ["A", "B", "C", "D", "E", "F", "G"];
  const entries = [];
  [2, 3].forEach((degree) => {
    combinations(alternatives, degree).forEach((subset) => {
      if (!subset.includes("A")) {
        subset.forEach((winner) => entries.push({ subset, winner, value: [1n, BigInt(degree)] }));
        return;
      }
      const denominator = BigInt(DATA.sevenAlternativeWitness.denominator) * choose(6, degree - 1);
      const numeratorA = profile.counts.reduce((sum, count, index) => {
        const rank = index + 1;
        return sum + BigInt(count) * choose(7 - rank, degree - 1);
      }, 0n);
      subset.forEach((winner) => {
        const value = winner === "A"
          ? [numeratorA, denominator]
          : [denominator - numeratorA, denominator * BigInt(degree - 1)];
        entries.push({ subset, winner, value });
      });
    });
  });
  return entries;
}

const profiles = DATA.sevenAlternativeWitness.profiles;
profiles.forEach((profile) => {
  assert.equal(profile.counts.reduce((sum, value) => sum + value, 0), 1536, `${profile.id}: probabilities sum to one`);
  const first = profile.counts.reduce((sum, value, index) => sum + value * (index + 1), 0);
  const second = profile.counts.reduce((sum, value, index) => sum + value * (index + 1) ** 2, 0);
  assert.equal(first, 4 * 1536, `${profile.id}: mean rank is four`);
  assert.equal(second, 17.5 * 1536, `${profile.id}: variance is 1.5`);
});

const matrices = profiles.map(pluralityMatrix);
assert.equal(matrices[0].length, 147, "42 degree-2 plus 105 degree-3 entries");
for (let p = 1; p < matrices.length; p += 1) {
  matrices[0].forEach((entry, index) => {
    assert.deepEqual(entry.subset, matrices[p][index].subset);
    assert.equal(entry.winner, matrices[p][index].winner);
    assert.ok(equalFraction(entry.value, matrices[p][index].value), `${profiles[p].id}: entry ${index} differs`);
  });
}

console.log("EDDY witness validation passed: all 147 degree-2/3 entries are exactly equal across profiles.");
require("./validate-literature.cjs");
