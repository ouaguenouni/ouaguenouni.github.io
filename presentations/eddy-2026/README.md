# EDDY 2026 presentation

An accessible Reveal.js presentation of **Efficient Elicitation of Collective Disagreements**.

## Run locally

From the repository root:

```bash
./dev.sh
```

Open <http://localhost:8000/presentations/eddy-2026/>.

- Right / Space: advance the horizontal story and its local builds.
- Left: step backward through the horizontal story.
- Down: enter an optional technical branch when one exists.
- `O`: overview.

## Write your reader’s notes

Edit [`reader-notes.html`](reader-notes.html) only. Each slide has a blank `note-body` block marked `<!-- Write your notes here. -->`; replace the comment with paragraphs, lists, or any HTML you need. All 22 main slides and their 43 optional detail slides are included, with the latter grouped in expandable sections. Headings link to the corresponding slides.

Save the file, then refresh <http://localhost:8000/presentations/eddy-2026/reader-notes.html> to preview it. The page is a viewer, not a browser editor: your saved HTML file is the source of truth. Styling is kept separately in `reader-notes.css`. Nothing imports these notes into the projected deck or restores the speaker-notes plugin.

This is a public website repository: notes will also be public if you commit and push this file. The `noindex` tag is not access control.

## Editable project

- `index.html` — narrative, technical branches, and visible bibliographic pointers. Speaker notes and the notes plugin are omitted.
- `deck.css` — the visual system and responsive layout.
- `opening.css` — isolated layouts and reversible animations for the five opening cards.
- `example.css` and `example.js` — the 14-build illustrative example, including grouping, normalization, rank-specific highlights, growing histograms, and probability flights into Borda computations.
- `tournament.css` and `tournament.js` — the seven-build tournament walkthrough, formula replacement, and graph-to-score probability flights.
- `continuation.css` and `continuation.js` — cards 6–8: the full-profile question, measure comparison, and original five-profile witness reveal.
- `framework.css` and `framework.js` — cards 9–11: formal definitions, the eight-build plurality-matrix walkthrough with highlighted contributors and probability flights, and the moment hierarchy.
- `elicitation.css`, `sampling-overview.css`, and `elicitation.js` — cards 13–15: recap, anonymity/cost principles, the 23-build Borda-to-protocol walkthrough, and the preserved 14-build Hoeffding development in its downward branch.
- `protocols.css` and `protocols.js` — cards 16–19: original ranking/chain animations, protocol table, degree-wise sample bounds, and the numbered application walkthrough.
- `closing.css` and `closing.js` — staged two-column conclusion, separate “efficient” emphasis, backup navigation, and the final thank-you card.
- `qr-presentation.svg` — locally generated, decoder-verified QR linking directly to the public presentation URL.
- `tradeoff-explorer.html`, `tradeoff-explorer.js`, and `tradeoff-model.js` — original frontier data and plot styling with continuously moving linked sliders; protocol selection changes only at thresholds.
- `data.js` — exact toy profiles, the seven-alternative witness, and elicitation examples.
- `sampling-model.js` — the numerical k-ranking table's rounded mean-coverage populations and merge-sort comparison bounds, shared with the validation script.
- `deck.js` — computed teaching examples, original-figure stage control, navigation, and browser-side validation.
- `validate.cjs` — checks Borda scores, all 11 rows of the four-alternative matrix, the moment formula, original witnesses, and the exact equality of all 147 degree-2 and degree-3 witness entries.

Run the exact witness check with:

```bash
node presentations/eddy-2026/validate.cjs
```

## Source and asset inventory

- Opening cards: setting → Borda score and latent profile → explicit three-alternative example → equivalent weighted tournament → uniform versus opposed camps. The example uses the existing `winnerProfile` in `data.js`.
- Card 2, “Gentle Warmup,” starts with the winner question, then separately reveals the points-by-rank sentence, arrow/Borda label, people's rankings, sample score, profile with its plain-language definition, rank-distribution definition, and expected-score formula. Its downward branch gives formal definitions of both the profile and the rank marginal; returning preserves the current build. The two transformations are reversible.
- Card 3, “Illustrative Exemple,” starts from 20 people's rankings. Its builds are: six unique rankings and counts (7, 5, 2, 4, 1, 1); total 20; normalization into pi; histogram heading/divider; A's empty axis; A rank 1; A ranks 2–3 together; all B/C bars together; score heading/divider; A's three contributions separately; A's result; B/C's complete calculations together. Values are derived from `winnerProfile`, preserving all original probabilities and scores. Navigation cancels in-flight tokens and restores deterministic state; reduced-motion users get the same builds without motion.
- Card 4 starts with “We don’t need the full profile,” scoped to the Borda score. It reveals the tournament and pairwise definition, the rank formula, then the pairwise replacement. A's two outgoing probabilities travel separately from the graph into its computation before its result appears; B and C then build together. Reverse-edge tokens show 1 minus the displayed edge probability before becoming the complement. The arrow explanation is below the graph.
- Opening scoring convention: rank 1 earns m points, so B(a) = m + 1 − E[r(a)] = 1 + sum of outgoing pairwise probabilities. This differs by a constant 1 from the m − r convention; winners and score differences are unaffected. The remaining slide content is preserved.
- Card 7 introduces measures proposed in the literature, then reveals agreement index, rank variance, and divisiveness on separate clicks, each definition together with its table row. It reuses the original comparison with 15 alternatives: agreement 0/0, variance 56/3 versus 49, and divisiveness 16/3 versus 14. The final quoted claim is a hypothesis, challenged by “Are we sure?” and refuted on card 8.
- Card 8 reuses the original A/B/C/D synthetic histograms, placing uniform U in the middle. The 256-rank weights were recovered using the original research generator's linear programs (candidates 1–3 and the reflected third candidate). The checked weights and unchanged histogram bins are stored in `data.js` under `originalWitnesses`. Every displayed focal variance is 5461.25 and every focal divisiveness is 257/3. Scores are computed from full rank weights, not histogram-bin centers.
- Feasibility construction: draw the focal alternative's rank, then uniformly permute all remaining labels into the vacant positions. “Uniform except for one alternative” refers to that conditional shuffle, not to unchanged uniform marginals for every other label.
- Card 9 starts with its definition, then reveals the profile and separator, empty degree-2 rows, the worked first cell (.4 + .2 = .6), the remaining pair cells together, empty degree-3 rows, the worked first triple cell (.4), the remaining triple cells together, and the filled degree-4 row. Worked cells highlight the relevant alternatives and contributing masses; copies of those masses move into the cells. All 11 rows are computed from the displayed profile. Reverse navigation cancels flights and restores empty layers; reduced-motion mode preserves the same reveal sequence. Card 10 defines the cumulative cutoff and presents the level-2 and level-3 propositions.
- Card 10 states the level definition in plain language, with “minimal” highlighted in burgundy. The unchanged formal cutoff/factorization definition is the first downward detail slide; the existing triple and sufficiency/necessity explanations follow it.
- Card 11 uses the manuscript's finite-difference formula, adjusted to the opening Borda convention with q = B − 1. Borda depends on the first raw moment; variance is the second central moment. The central-moment level proposition starts at k = 2 (the first central moment is zero), in the manuscript's stated range m ≥ k + 2. The former higher-moment histograms remain in its downward branch. Card 12 and its original synthetic assets are unchanged.
- Cards 13–15 recap the information hierarchy and introduce the population/load trade-off. Card 15 keeps its title visible throughout: Borda score → pairwise proportions → Q(m) pairs, then Hoeffding with only n highlighted, then its abstraction to n(m) independent samples per pair. It continues with the full-ranking and balanced single-pair protocols with burgundy numbered actions. Their costs appear together on an aligned row; the separators and random k-ranking follow. The original detailed 14-build development is preserved in the first downward branch, and its technical coverage note is the second. Down/Up enters/leaves the derivation without consuming main-slide builds; Right/Left walks its derivation builds.
- After the three protocols are complete, build 21 morphs Full ranking into an m-ranking and One pairwise comparison into a 2-ranking. Build 22 fixes m=10, retaining pairwise tolerance epsilon=.05 and simultaneous failure probability delta=.05. Q=45 and n=ceil(200 ln(40Q))=1500. Build 23 turns the population and comparison rows into a table for every k=2,...,10: endpoint values fly into their cells while the intermediate columns fill in. Populations are ceil(67500 / choose(k,2)), including 3215 for k=7 and 2411 for k=8. Full rankings need 1500 people; balanced single-pair queries need 67500. The intermediate values are rounded mean-coverage benchmarks, not guaranteed populations or expected all-pairs stopping times. Stop when every pair has n respondents, using its first n observations. Within-person pair outcomes need not be independent. Raw Borda error is at most (m−1)epsilon; this is not an optimal Borda-only estimator claim.
- Numeric ranking costs explicitly use merge sort: the recurrence C(t)=C(floor(t/2))+C(ceil(t/2))+t−1 gives worst-case upper bounds 25 for 10 alternatives and 8 for 5 alternatives; the single-pair cost is 1. These are implementable algorithm-specific bounds, not claims of optimal comparison complexity and not the cost proxy used in the later original empirical frontier.
- Card 16 has two successive scenes adapted directly from the original deck's animation code: a 4-ranking (11 subset observations), then a 4-chain (3 prefix observations). Card 17 retains the original comparison-table style, with observation independence clarified. Card 18 uses Q_ell = ell choose(m,ell) and T_ell = ceil(ln(2Q_ell/delta)/(2 epsilon²)); ranking coverage divides by choose(k,ell), not the comparison cost k log k. The technical branch covers all degrees through a measure's level.
- Card 19 reveals its four burgundy-numbered steps before showing the frontier. The original `pareto.json` is fetched directly, without changing the source data. Both sliders select the same observed protocol in opposite directions; there is no interpolation or invented protocol. These empirical degree-wise experiments are distinct from the preceding simultaneous concentration guarantee. Previous cards and later material remain unchanged.
- A downward branch beneath card 19 contains an eight-row clickable literature table: Borda, agreement/polarization, Kendall-distance diversity, partitioning ratio, rank variance, Navarrete divisiveness, Borda α-divisiveness, and pairwise discrepancy. Each row opens its complete derivation (11 pages in total); Left/Right follows that derivation, Up returns to the table, and the table returns to the preserved main-slide build. Two bibliography pages distinguish original measures from this work's plurality reformulations. Modern sources have publisher/author-hosted links; rank variance cites Colley et al. §2.3 directly, with Kendall–Smith retained as historical background. The three-measure introduction also has author/year pointers.
- `literature-data.js` stores the curated manuscript-derived content and references; `literature.js` renders the optional branches before Reveal initializes; `literature.css` scopes their layouts. `validate-literature.cjs` checks all eight coordinate identities on 59 finite profiles, including empty-camp cases; it runs as part of `validate.cjs`. Scores use raw Borda (with its deck/manuscript shift stated), independent-draw Kendall distance, and the appendix's α-divisiveness normalization; the conversion to Colley et al.'s normalization is explicit. Level labels follow the supplied inventory; the derivations show sufficiency and do not claim to prove minimality anew.
- Card 20 starts with only its headings and divider, then reveals information requirements, visible/missed structure, the first limitation, the people–questions trade-off, minimal-load/general-efficiency options with sampling guarantees, a separate emphasis on “efficient,” and the final limitation. The emphasis stays on the text baseline before and after highlighting. Moments fit the hierarchy but do not exhaust its information; minimal-load certification is specifically the chain guarantee. The eleven former trailing slides are preserved beneath the conclusion as optional backups, leaving Thank you as the final main slide.
- The conclusion's final click reveals “Divisiveness Zoo” beside its first gain. This opens the existing measures table; its return link and Up/Left navigation return to the fully revealed conclusion. Entering from card 19 still returns to the interactive figure. The final reveal reverses independently of the preceding limitation, and the next story step remains Thank you.
- The full-profile limitation is checked using two four-ranking profiles on four alternatives: uniform over {abcd, badc, cdab, dcba} versus {abdc, bacd, cdba, dcab}. All 28 plurality cells agree, while Pr(a > b and c > d) is 1/2 versus 0. Measure-specific sample savings are an outlook, not an additional universal guarantee.
- The closing QR points to `https://ouaguenouni.com/presentations/eddy-2026/`, using the repository’s canonical domain. Publish this deck before sharing the QR with attendees; local edits do not update the public site.

- Scientific claims and theorem labels: the working-paper material summarized in the supplied EDDY brief.
- Exact synthetic witness: Section 8 of the supplied EDDY brief; stored as integer counts in `data.js`.
- Original synthetic-data figure: `../elicitation-collective-disagreement/moment_plane.html?mode=explain`, with the original five builds and unchanged embedded data, traces, colors, labels, and reference distributions. The free explorer (`mode=play`) is the first downward branch; the exact `figs/fig_synth_bis.png` is the second.
- Real-election view: the original `moment_plane.html?mode=realguided`.
- Pareto explorer: the original `pareto_widget.html`, now on the main route instead of a schematic replacement.
- Original static figures are reused for printing. The original asset files are referenced directly and are not copied or modified.
- On narrow screens, the figure frames scroll horizontally to preserve the original composition and legibility.
- Logos: reused from the existing presentation assets in that folder.
- Reveal.js 5.1.0 and KaTeX 0.16.24 are version-pinned in `index.html`.

## Explicit caveats

- The three seven-alternative profiles are a synthetic teaching witness, not real-election observations.
- The seven-alternative A/B/C witness is distinct from the original 256-alternative A/B/U/C/D construction. It remains available in the technical branch and in the later higher-moments scene.
- The Pareto figure reports the source experiment's evaluated protocols and 5–95% quantiles across seeds; it does not establish global optimality over every possible elicitation strategy.
- The original synthetic figure's four reference shapes are distinct from the brief's seven-alternative A/B/C witness. Its dashed reference frontier should not be treated as a universal classifier of arbitrary discrete rank distributions.
- The real-election figure illustrates shape diversity. It does not establish exact equality of lower-degree information.
- Dataset sample sizes are intentionally omitted until rechecked against the original source files.
