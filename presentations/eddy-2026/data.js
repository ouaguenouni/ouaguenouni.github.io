const EDDY_DATA = {
  alternatives: ["A", "B", "C"],
  winnerProfile: [
    { order: "ABC", weight: 0.35 },
    { order: "ACB", weight: 0.25 },
    { order: "BAC", weight: 0.10 },
    { order: "BCA", weight: 0.20 },
    { order: "CAB", weight: 0.05 },
    { order: "CBA", weight: 0.05 }
  ],
  pairwiseWitness: {
    uniform: [
      { order: "ABC", weight: 1 / 6 },
      { order: "ACB", weight: 1 / 6 },
      { order: "BAC", weight: 1 / 6 },
      { order: "BCA", weight: 1 / 6 },
      { order: "CAB", weight: 1 / 6 },
      { order: "CBA", weight: 1 / 6 }
    ],
    polarized: [
      { order: "ABC", weight: 1 / 2 },
      { order: "CBA", weight: 1 / 2 }
    ]
  },
  sevenAlternativeWitness: {
    denominator: 1536,
    profiles: [
      {
        id: "central",
        name: "Central peak",
        short: "A",
        counts: [24, 144, 360, 480, 360, 144, 24],
        divisiveness: 1,
        color: "#9a1b1b"
      },
      {
        id: "twoPeaks",
        name: "Two symmetric peaks",
        short: "B",
        counts: [3, 130, 605, 60, 605, 130, 3],
        divisiveness: 1,
        color: "#1b6f7a"
      },
      {
        id: "asymmetric",
        name: "Asymmetric",
        short: "C",
        counts: [3, 18, 717, 396, 45, 354, 3],
        divisiveness: 1,
        color: "#6956a8"
      }
    ]
  },
  originalWitnesses: {
    "m": 256,
    "source": "Original figure: synth_moment.json; full rank weights recovered with the original _base_eq / _solve_lp witness generator.",
    "profiles": [
      {
        "id": "A",
        "support": [
          [
            1,
            0.16796875
          ],
          [
            128,
            0.33203124999999467
          ],
          [
            129,
            0.33203125000000533
          ],
          [
            256,
            0.16796875
          ]
        ],
        "description": "trimodal",
        "bins": [
          0.16796875,
          0,
          0,
          0,
          0.33203124999999467,
          0.33203125000000533,
          0,
          0,
          0,
          0.16796875
        ]
      },
      {
        "id": "B",
        "support": [
          [
            54,
            0.19932432432431096
          ],
          [
            55,
            0.3006756756756896
          ],
          [
            202,
            0.3006756756756754
          ],
          [
            203,
            0.19932432432432404
          ]
        ],
        "description": "bimodal symmetric",
        "bins": [
          0,
          0,
          0.5000000000000006,
          0,
          0,
          0,
          0,
          0.49999999999999944,
          0,
          0
        ]
      },
      {
        "id": "C",
        "support": [
          [
            83,
            0.3954169973307496
          ],
          [
            84,
            0.33370755750262643
          ],
          [
            249,
            0.06990690032872587
          ],
          [
            250,
            0.2009685448378982
          ]
        ],
        "description": "bimodal asymmetric (right)",
        "bins": [
          0,
          0,
          0,
          0.729124554833376,
          0,
          0,
          0,
          0,
          0,
          0.2708754451666241
        ]
      },
      {
        "id": "D",
        "support": [
          [
            7,
            0.2009685448378982
          ],
          [
            8,
            0.06990690032872587
          ],
          [
            173,
            0.33370755750262643
          ],
          [
            174,
            0.3954169973307496
          ]
        ],
        "description": "bimodal asymmetric (left)",
        "bins": [
          0.2708754451666241,
          0,
          0,
          0,
          0,
          0,
          0.729124554833376,
          0,
          0,
          0
        ]
      }
    ]
  },
  pluralityExample: {
    alternatives: ["A", "B", "C", "D"],
    profile: [
      { order: "ABCD", weight: .4 },
      { order: "BACD", weight: .3 },
      { order: "CDAB", weight: .2 },
      { order: "DCBA", weight: .1 }
    ]
  },
  rankingExample: {
    alternatives: ["A", "B", "C", "D"],
    order: ["C", "A", "D", "B"],
    triples: [
      { subset: ["A", "B", "C"], winner: "C" },
      { subset: ["A", "B", "D"], winner: "A" },
      { subset: ["A", "C", "D"], winner: "C" },
      { subset: ["B", "C", "D"], winner: "C" }
    ]
  },
  chainExample: {
    queryOrder: ["B", "D", "A", "C"],
    preferenceOrder: ["C", "A", "D", "B"],
    rounds: [
      { pair: ["B", "D"], winner: "D", prefix: ["B", "D"] },
      { pair: ["D", "A"], winner: "A", prefix: ["B", "D", "A"] },
      { pair: ["A", "C"], winner: "C", prefix: ["B", "D", "A", "C"] }
    ]
  }
};

if (typeof window !== "undefined") window.EDDY_DATA = EDDY_DATA;
if (typeof module !== "undefined" && module.exports) module.exports = EDDY_DATA;
