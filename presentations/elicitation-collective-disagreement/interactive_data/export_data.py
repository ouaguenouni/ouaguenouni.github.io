"""Export the exact plotted data behind four supplementary figures to JSON.

The three output files feed the interactive reveal.js widgets in
``presentation/widgets/``:

  data/pareto.json        <- pareto_yB_line_single_final.pdf  (B vs MCL)
                             fig_pareto_bis.pdf                (N vs MCL)
  data/synth_moment.json  <- fig_synth_bis.pdf  (synthetic moment plane)
  data/real_moment.json   <- final_real_world_parabole.pdf
                             (real PrefLib preferential data)

Each section re-runs the *same data-production code path* as the original
figure script (importing the original modules rather than copying logic),
so the exported numbers are identical to what was rendered. No file is
modified in the archived RESEARCH tree.

Run from the repo root:  ``.venv/bin/python presentation/export_data.py``
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(OUT_DIR, exist_ok=True)


def _jsonify(obj):
    """Recursively convert numpy scalars/arrays to plain Python for json."""
    if isinstance(obj, dict):
        return {k: _jsonify(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonify(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return [_jsonify(v) for v in obj.tolist()]
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    return obj


def _dump(name, payload):
    path = os.path.join(OUT_DIR, name)
    with open(path, "w") as f:
        json.dump(_jsonify(payload), f, indent=1)
    print(f"  wrote {os.path.relpath(path, REPO)}  "
          f"({os.path.getsize(path) / 1024:.1f} KB)")


# ---------------------------------------------------------------------------
# 1. Pareto figures (B vs MCL and N vs MCL).
# ---------------------------------------------------------------------------
def export_pareto():
    print("[pareto] B-vs-MCL + N-vs-MCL ...")
    here = os.path.join(REPO, "RESEARCH/2026-05/05/10_pareto_yB_line_single_final")
    sys.path.insert(0, here)
    import make_final as MF  # noqa: E402  (sets up build/build_ic/make_v5 paths)
    import build as B        # noqa: E402
    import build_ic as BC    # noqa: E402

    # Identical pipeline to make_final.main(): collect -> Pareto filter -> x-cut.
    pts = MF.collect_points()
    pts, _dropped = MF.filter_to_within_family_frontier(pts)
    pts, _xdrop = MF.filter_x_cutoff(pts, MF.MCL_X_CUTOFF)

    points = [
        {
            "ell": p["ell"], "k": p["k"], "kind": p["kind"],
            "mcl": p["mcl"],
            "B": p["B"], "B_lo": p["B_lo"], "B_hi": p["B_hi"],
            "N": p["N"], "N_lo": p["N_lo"], "N_hi": p["N_hi"],
        }
        for p in pts
    ]

    # Faded dashed per-family frontiers, for both y-quantities.
    frontier = {"B": {}, "N": {}}
    for y_key in ("B", "N"):
        for ell in MF.ELLS:
            fam = [p for p in pts if p["ell"] == ell]
            if not fam:
                continue
            fx, fy, _ = MF.family_frontier(fam, y_key)
            if fx:
                frontier[y_key][str(ell)] = {"x": fx, "y": fy}

    # tab:* colours resolved to hex so the widget needs no matplotlib.
    ell_color_hex = {2: "#1f77b4", 3: "#2ca02c", 4: "#ff7f0e", 5: "#d62728"}

    payload = {
        "meta": {
            "source_figures": [
                "pareto_yB_line_single_final.pdf (B vs MCL)",
                "fig_pareto_bis.pdf (N vs MCL)",
            ],
            "m": int(B.M),
            "epsilon": float(BC.EPSILON),
            "mcl_cutoff": float(MF.MCL_X_CUTOFF),
            "ells": list(MF.ELLS),
            "ell_color": {str(k): v for k, v in ell_color_hex.items()},
            "x_label": "Maximum cognitive load λ (comparisons per voter)",
            "y_label_B": "Budget B (total comparisons)",
            "y_label_N": "Population N (voters)",
            "notes": (
                "Chain protocol = filled circle (k=ℓ); Ranking protocol = "
                "open square (k>ℓ). Colour encodes the level k. Error bars are "
                "5-95% quantiles over R seeds. N = B / MCL."
            ),
        },
        "points": points,
        "frontier": frontier,
    }
    _dump("pareto.json", payload)
    sys.path.remove(here)


# ---------------------------------------------------------------------------
# 2. Synthetic moment plane (fig_synth_bis).
# ---------------------------------------------------------------------------
def export_synth_moment():
    print("[synth] moment plane (fig_synth_bis) ...")
    here = os.path.join(REPO, "RESEARCH/2026-05/05/08_moment_plane_witness_patch")
    orig_py = os.path.join(
        REPO, "RESEARCH/2026-04/30/02_final_version_parabole/figures/py")
    common = os.path.join(
        REPO, "RESEARCH/2026-04/29/02_moment_space_figures/figures/py/common")
    for p in (REPO, common, orig_py, here):
        if p not in sys.path:
            sys.path.insert(0, p)

    from diag_witness_common import generate_candidates, synthetic_cloud
    from make_witness_patch import (
        _mirror_of, _per_alt_g1_g2,
        OVERLAY, PALETTE, WITNESS_RED,
        CID_TO_LETTER, CID_TO_DESC, DISPLAY_ORDER, HIST_ORDER,
    )

    # --- identical parameters + construction to make_witness_final.main() ---
    m = 256
    n_voters = 1000
    seed = 42
    n_hist_bins = 10

    cloud_dummy = synthetic_cloud(m)
    cands_all = generate_candidates(m, cloud_dummy)
    cands = [c for c in cands_all if c.cid in (1, 2, 3, 11)]
    c3 = next((c for c in cands if c.cid == 3), None)
    if c3 is not None:
        cands.append(_mirror_of(c3, new_cid=4,
                                label="mirror of C3 (low M_4, neg. skew)"))
    feas = [c for c in cands if c.feasible]

    g1_w = np.array([c.achieved_g1 for c in feas])
    g2_w = np.array([c.achieved_g2 for c in feas])
    g1_abs_max = float(np.max(np.abs(g1_w))) if len(g1_w) else 1.0
    x_max = g1_abs_max * 1.08 + 0.02 * g1_abs_max
    x_lo, x_hi = -x_max, +x_max
    y_min, y_max = float(g2_w.min()), float(g2_w.max())
    dy = max(y_max - y_min, 1e-3)
    y_lo = y_min - 0.08 * dy
    y_hi = y_max + 0.08 * dy

    # --- per-family clouds (same RNG stream as the figure) ---
    # Per cloud point we now ALSO export the alternative's real rank-position
    # histogram (binned best->worst), so the interactive widget can show the
    # exact shape on click instead of reconstructing it from (g1, g2).
    HIST_BINS_CLOUD = 16
    cedges = np.linspace(0, m, HIST_BINS_CLOUD + 1).astype(int)

    def _alt_rank_hist(R, a):
        # NOTE: assumes R[voter, alt] = rank POSITION of alt (0=best .. m-1=worst),
        # the same convention used by the real-data export (np.bincount(R[:, col])).
        # If _per_alt_g1_g2 reads ranks differently, adjust this one line to match.
        counts = np.bincount(R[:, a].astype(int), minlength=m).astype(float)
        counts /= max(counts.sum(), 1.0)
        return [float(counts[cedges[b]:cedges[b + 1]].sum())
                for b in range(HIST_BINS_CLOUD)]

    rng_master = np.random.default_rng(seed)
    clouds = []
    for idx, (key, name, param, sampler) in enumerate(OVERLAY):
        R = sampler(n_voters, m, int(rng_master.integers(1 << 30)))
        g1, g2 = _per_alt_g1_g2(R)
        finite = np.isfinite(g1) & np.isfinite(g2)
        keep = np.where(finite)[0]
        clouds.append({
            "key": key, "name": name, "param": param,
            "color": PALETTE[idx % len(PALETTE)],
            "label": f"{name}  ·  {param}",
            "g1": g1[finite].astype(float).tolist(),
            "g2": g2[finite].astype(float).tolist(),
            "hist_bins": HIST_BINS_CLOUD,
            "hist": [_alt_rank_hist(R, int(a)) for a in keep],
        })

    # --- witnesses A,B,C,D,U ---
    feas_by_cid = {c.cid: c for c in feas}
    witnesses = []
    for cid in DISPLAY_ORDER:
        c = feas_by_cid.get(cid)
        if c is None:
            continue
        witnesses.append({
            "cid": int(cid),
            "letter": CID_TO_LETTER[cid],
            "desc": CID_TO_DESC[cid],
            "g1": float(c.achieved_g1),
            "g2": float(c.achieved_g2),
            "has_hist": cid in HIST_ORDER,
        })

    # --- binned rank distributions for A,B,C,D (10 bins; same as figure) ---
    edges = np.linspace(0, m, n_hist_bins + 1).astype(int)

    def _bin(rd):
        return np.array([rd[edges[b]:edges[b + 1]].sum()
                         for b in range(n_hist_bins)])

    histograms = []
    for cid in HIST_ORDER:
        c = feas_by_cid.get(cid)
        if c is None:
            continue
        rd = _bin(np.asarray(c.w, dtype=float))
        histograms.append({
            "cid": int(cid),
            "letter": CID_TO_LETTER[cid],
            "desc": CID_TO_DESC[cid],
            "bins": rd.astype(float).tolist(),
        })

    payload = {
        "meta": {
            "source_figure": "fig_synth_bis.pdf",
            "m": m, "n_voters": n_voters, "seed": seed,
            "n_hist_bins": n_hist_bins,
            "witness_color": WITNESS_RED,
            "bounds": {"x_lo": x_lo, "x_hi": x_hi, "y_lo": y_lo, "y_hi": y_hi},
            "x_label": "Standardised skewness γ₁",
            "y_label": "Excess kurtosis γ₂",
            "unimodal_c": 186.0 / 125.0,
            "notes": (
                "Each cloud point is one alternative's per-voter rank-position "
                "distribution summarised by (skewness γ₁, excess kurtosis "
                "γ₂). Red triangles A-D (+U) are constructed reference "
                "shapes; their 10-bin rank histograms run best (left) to worst "
                "(right). Pearson bound γ₂=γ₁²−2; unimodal bound "
                "γ₂=γ₁²−186/125."
            ),
        },
        "clouds": clouds,
        "witnesses": witnesses,
        "histograms": histograms,
    }
    _dump("synth_moment.json", payload)


# ---------------------------------------------------------------------------
# 3. Real-world moment plane (final_real_world_parabole / "fig_real").
# ---------------------------------------------------------------------------
def export_real_moment():
    print("[real] moment plane (final_real_world_parabole) ...")
    pol_dir = os.path.join(REPO, "RESEARCH/2026-04/27/01_preflib_political")
    py_dir = os.path.join(
        REPO, "RESEARCH/2026-04/30/02_final_version_parabole/figures/py")
    for p in (REPO, pol_dir, py_dir):
        if p not in sys.path:
            sys.path.insert(0, p)

    from preprocess import POLITICAL_DATASETS, build_full_rank_corpus
    import final_overlay_real_world as RW

    # Re-run the exact data-production half of RW.main().
    instances, _ = build_full_rank_corpus(min_n_full=RW.N_FULL_MIN)
    rows, by_inst = RW._per_alt_rows(instances)

    rng = np.random.default_rng(RW.SAMPLE_SEED)
    nswla_rows = [r for r in rows if r["dataset"] == "nswla"]
    rows_full = list(rows)
    if len(nswla_rows) > RW.NSWLA_SAMPLE_SIZE:
        keep_idx = set(map(int, rng.choice(
            len(nswla_rows), size=RW.NSWLA_SAMPLE_SIZE, replace=False)))
        rows = [r for r in rows if r["dataset"] != "nswla"] + \
               [nswla_rows[k] for k in keep_idx]

    UNIMODAL_C = 186.0 / 125.0

    def _find(name_substr, dataset):
        return [r for r in rows
                if r["dataset"] == dataset
                and name_substr.lower() in r["alternative_name"].lower()]

    melenchon = max(_find("Mélenchon", "voter_autrement"),
                    key=lambda r: r["g1"], default=None)
    le_pen = min(_find("Le Pen", "voter_autrement"),
                 key=lambda r: r["g1"], default=None)
    central = min(
        (r for r in rows if r["dataset"] == "nswla" and r["m"] >= 6),
        key=lambda r: r["g1"] ** 2 + r["g2"] ** 2, default=None)
    bimodal_pool = [
        r for r in rows_full
        if abs(r["g1"]) <= 0.20
        and (r["g1"] ** 2 - UNIMODAL_C) > r["g2"] >= (r["g1"] ** 2 - 2.0)
    ]
    bimodal_pick = min(bimodal_pool, key=lambda r: r["g2"], default=None)
    if bimodal_pick is not None and bimodal_pick not in rows:
        rows.append(bimodal_pick)

    picks = {"Q1": central, "Q2": bimodal_pick, "Q3": le_pen, "Q4": melenchon}

    # Bounds (identical to RW.main()).
    bg = [r for r in rows if r["dataset"] != "voter_autrement"]
    g1s = [r["g1"] for r in bg] + [p["g1"] for p in picks.values() if p]
    g2s = [r["g2"] for r in bg] + [p["g2"] for p in picks.values() if p]
    g1_max_abs = max(abs(min(g1s)), abs(max(g1s)))
    x_max = g1_max_abs + 0.10
    x_lo, x_hi = -x_max, +x_max
    y_lo = min(float(min(g2s)) - 0.20, -2.2)
    y_hi = max(float(max(g2s)) + 0.20, 0.4)

    dataset_specs = [
        {"key": s.key, "label": s.label, "color": s.color}
        for s in POLITICAL_DATASETS
    ]

    # Scatter rows grouped per dataset (signed g1, excess g2 per alternative).
    scatter = {}
    for s in POLITICAL_DATASETS:
        pts = [r for r in rows if r["dataset"] == s.key]
        scatter[s.key] = {
            "g1": [float(r["g1"]) for r in pts],
            "g2": [float(r["g2"]) for r in pts],
            "name": [r["alternative_name"] for r in pts],
            "m": [int(r["m"]) for r in pts],
        }

    # Q1..Q4 picks with full rank-position distributions.
    pick_out = []
    for q in ("Q1", "Q2", "Q3", "Q4"):
        p = picks.get(q)
        if p is None:
            pick_out.append(None)
            continue
        inst = by_inst[(p["dataset"], p["file"])]
        col = p["alt_idx"]
        rd = np.bincount(inst.R[:, col], minlength=p["m"]).astype(float)
        rd /= max(rd.sum(), 1.0)
        pick_out.append({
            "q": q,
            "dataset": p["dataset"],
            "name": p["alternative_name"],
            "g1": float(p["g1"]), "g2": float(p["g2"]),
            "m": int(p["m"]),
            "rank_distribution": rd.tolist(),
        })

    payload = {
        "meta": {
            "source_figure": "final_real_world_parabole.pdf (fig_real)",
            "bounds": {"x_lo": x_lo, "x_hi": x_hi, "y_lo": y_lo, "y_hi": y_hi},
            "x_label": "Standardised skewness γ₁",
            "y_label": "Excess kurtosis γ₂",
            "unimodal_c": UNIMODAL_C,
            "datasets": dataset_specs,
            "notes": (
                "Real PrefLib political profiles. Each point is one candidate's "
                "rank-position distribution over voters, summarised by (γ₁, "
                "γ₂). Circled Q1-Q4 are representative picks whose full "
                "rank histograms are shown best->worst. NSWLA is subsampled to "
                f"{RW.NSWLA_SAMPLE_SIZE} alternatives (seed {RW.SAMPLE_SEED})."
            ),
        },
        "scatter": scatter,
        "picks": pick_out,
    }
    _dump("real_moment.json", payload)


def main():
    print("=== exporting figure data -> presentation/data/ ===")
    export_pareto()
    export_synth_moment()
    export_real_moment()
    print("done.")


if __name__ == "__main__":
    main()
