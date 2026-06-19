# Interactive figure data for the reveal.js presentation

Self-contained, interactive (Plotly) versions of four supplementary figures,
plus the exact data behind them as JSON. Built by re-running the *original*
figure code paths, so the numbers match the PDFs precisely — nothing in the
archived `RESEARCH/` tree was modified.

```
presentation/
  export_data.py      # regenerates data/*.json from the original code paths
  build_widgets.py    # turns data/*.json into self-contained widgets/*.html
  data/               # the plotted data (the deliverable you asked for)
    pareto.json
    synth_moment.json
    real_moment.json
  widgets/            # standalone interactive plots (data inlined, Plotly via CDN)
    pareto.html
    synth_moment.html
    real_moment.html
  index.html          # reveal.js demo deck embedding all three widgets
```

## Figure → file mapping

| Widget | Source PDF | Data |
|---|---|---|
| `widgets/pareto.html` | `…/10_pareto_yB_line_single_final/figs/pareto_yB_line_single_final.pdf` (B) and `fig_pareto_bis.pdf` (N) | `data/pareto.json` |
| `widgets/synth_moment.html` | `…/10_pareto_yB_line_single_final/figs/fig_synth_bis.pdf` | `data/synth_moment.json` |
| `widgets/real_moment.html` | `…/2026-04/30/02_final_version_parabole/figures/pdf/final_real_world_parabole.pdf` (the "fig_real" PrefLib figure) | `data/real_moment.json` |

The Budget (B) and Population (N) Pareto plots share one widget — toggle with
the buttons top-left.

## Viewing

The widgets inline their own data, so they work straight off `file://`:

```
open presentation/widgets/pareto.html        # or any widget
```

For the full reveal.js deck, serve the folder (iframes load most reliably over
http):

```
cd presentation && python3 -m http.server 8000
# then open http://localhost:8000/index.html
```

## Embedding a widget in your own reveal.js slide

Each widget is a complete page; drop it into a slide with an `<iframe>`:

```html
<section data-background-color="#ffffff">
  <h2>Cost of the precision target</h2>
  <iframe data-src="widgets/pareto.html" loading="lazy"
          style="width:92vw; height:78vh; border:0;"></iframe>
</section>
```

`data-src` (instead of `src`) lets reveal.js lazy-load the iframe, and
`preloadIframes: true` in `Reveal.initialize` keeps it interactive on the
current slide. All three widgets are `responsive: true`, so they fill whatever
box you give them.

## Regenerating

Run from the repo root with the project venv:

```
.venv/bin/python presentation/export_data.py     # data/*.json
.venv/bin/python presentation/build_widgets.py   # widgets/*.html
```

`export_data.py` is deterministic (fixed seeds: synthetic clouds use
`seed=42`, the NSWLA subsample uses `SAMPLE_SEED=42`), so reruns reproduce the
same numbers. Dependencies: `numpy`, `preflibtools` (for the real figure),
and the `elicitation.sampling` module (for the synthetic figure) — all already
present in the project venv.

---

## Data schema

### `pareto.json`

```jsonc
{
  "meta": {
    "m": 10, "epsilon": 0.05, "mcl_cutoff": 20.0,
    "ells": [2,3,4,5],
    "ell_color": {"2":"#1f77b4","3":"#2ca02c","4":"#ff7f0e","5":"#d62728"},
    "x_label": "...", "y_label_B": "...", "y_label_N": "..."
  },
  "points": [
    { "ell":2, "k":2, "kind":"chain",      // kind ∈ {chain (k=ℓ), ranking (k>ℓ)}
      "mcl":1.0,                            // max cognitive load (comparisons/voter)
      "B":31197, "B_lo":26187, "B_hi":33642,   // total comparisons + 5–95% CI
      "N":31197, "N_lo":26187, "N_hi":33642 }  // voters = B / MCL + CI
  ],
  "frontier": {                            // faded dashed per-family frontiers
    "B": { "2": {"x":[...], "y":[...]}, ... },
    "N": { "2": {"x":[...], "y":[...]}, ... }
  }
}
```

### `synth_moment.json`

```jsonc
{
  "meta": {
    "m":256, "n_voters":1000, "seed":42, "n_hist_bins":10,
    "witness_color":"#B22222", "unimodal_c":1.488,
    "bounds": {"x_lo":-1.13,"x_hi":1.13,"y_lo":-2.16,"y_hi":0.13},
    "x_label":"Standardised skewness γ₁", "y_label":"Excess kurtosis γ₂"
  },
  "clouds": [                              // one entry per synthetic profile family
    { "key":"mallows_0.85", "name":"Mallows", "param":"φ=0.85",
      "color":"#0072B2", "label":"Mallows  ·  φ=0.85",
      "g1":[... 256 ...], "g2":[... 256 ...] }   // per-alternative (γ₁, γ₂)
  ],
  "witnesses": [                           // constructed reference shapes
    { "cid":1, "letter":"A", "desc":"trimodal",
      "g1":0.0, "g2":-0.023, "has_hist":true }   // U has has_hist=false
  ],
  "histograms": [                          // 10-bin rank distribution, best→worst
    { "cid":1, "letter":"A", "desc":"trimodal", "bins":[... 10 ...] }
  ]
}
```

Pearson lower bound: `γ₂ = γ₁² − 2`. Unimodal bound: `γ₂ = γ₁² − 186/125`
(`meta.unimodal_c`). Both are drawn analytically in the widget.

### `real_moment.json`

```jsonc
{
  "meta": {
    "bounds": {...}, "unimodal_c":1.488,
    "x_label":"Standardised skewness γ₁", "y_label":"Excess kurtosis γ₂",
    "datasets": [ {"key":"glasgow","label":"Glasgow STV (city council)","color":"#0072B2"}, ... ]
  },
  "scatter": {                             // per dataset, one entry per candidate
    "glasgow": { "g1":[...], "g2":[...], "name":[...], "m":[...] },
    "nswla":   {...}, "voter_autrement": {...}
  },
  "picks": [                               // Q1–Q4 representatives (null if absent)
    { "q":"Q1", "dataset":"nswla", "name":"HAMILTON Ross",
      "g1":-0.038, "g2":-0.165, "m":7,
      "rank_distribution":[... m ...] }     // normalised, best→worst
  ]
}
```
