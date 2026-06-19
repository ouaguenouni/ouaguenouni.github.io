"""Regenerate real_moment.json EXACTLY as the original export, but ALSO store each
candidate's real rank-position histogram (so every point is clickable-exact).
Run with the research venv:
  /Users/mohamedouaguenouni/Incremental_Elicitation_Implementation/.venv/bin/python _regen_real.py
"""
import os, sys, json
import numpy as np

REPO = "/Users/mohamedouaguenouni/Incremental_Elicitation_Implementation"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "real_moment.json")

pol_dir = os.path.join(REPO, "RESEARCH/2026-04/27/01_preflib_political")
py_dir = os.path.join(REPO, "RESEARCH/2026-04/30/02_final_version_parabole/figures/py")
for p in (REPO, pol_dir, py_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

from preprocess import POLITICAL_DATASETS, build_full_rank_corpus
import final_overlay_real_world as RW

instances, _ = build_full_rank_corpus(min_n_full=RW.N_FULL_MIN)
rows, by_inst = RW._per_alt_rows(instances)

rng = np.random.default_rng(RW.SAMPLE_SEED)
nswla_rows = [r for r in rows if r["dataset"] == "nswla"]
rows_full = list(rows)
if len(nswla_rows) > RW.NSWLA_SAMPLE_SIZE:
    keep_idx = set(map(int, rng.choice(len(nswla_rows), size=RW.NSWLA_SAMPLE_SIZE, replace=False)))
    rows = [r for r in rows if r["dataset"] != "nswla"] + [nswla_rows[k] for k in keep_idx]

UNIMODAL_C = 186.0 / 125.0

def _find(name_substr, dataset):
    return [r for r in rows if r["dataset"] == dataset
            and name_substr.lower() in r["alternative_name"].lower()]

melenchon = max(_find("Mélenchon", "voter_autrement"), key=lambda r: r["g1"], default=None)
le_pen = min(_find("Le Pen", "voter_autrement"), key=lambda r: r["g1"], default=None)
central = min((r for r in rows if r["dataset"] == "nswla" and r["m"] >= 6),
              key=lambda r: r["g1"] ** 2 + r["g2"] ** 2, default=None)
bimodal_pool = [r for r in rows_full if abs(r["g1"]) <= 0.20
                and (r["g1"] ** 2 - UNIMODAL_C) > r["g2"] >= (r["g1"] ** 2 - 2.0)]
bimodal_pick = min(bimodal_pool, key=lambda r: r["g2"], default=None)
if bimodal_pick is not None and bimodal_pick not in rows:
    rows.append(bimodal_pick)
picks = {"Q1": central, "Q2": bimodal_pick, "Q3": le_pen, "Q4": melenchon}

bg = [r for r in rows if r["dataset"] != "voter_autrement"]
g1s = [r["g1"] for r in bg] + [p["g1"] for p in picks.values() if p]
g2s = [r["g2"] for r in bg] + [p["g2"] for p in picks.values() if p]
g1_max_abs = max(abs(min(g1s)), abs(max(g1s)))
x_max = g1_max_abs + 0.10
x_lo, x_hi = -x_max, +x_max
y_lo = min(float(min(g2s)) - 0.20, -2.2)
y_hi = max(float(max(g2s)) + 0.20, 0.4)

dataset_specs = [{"key": s.key, "label": s.label, "color": s.color} for s in POLITICAL_DATASETS]

def hist_of(r):
    inst = by_inst[(r["dataset"], r["file"])]
    rd = np.bincount(inst.R[:, r["alt_idx"]].astype(int), minlength=r["m"]).astype(float)
    rd /= max(rd.sum(), 1.0)
    return rd.tolist()

scatter = {}
for s in POLITICAL_DATASETS:
    pts = [r for r in rows if r["dataset"] == s.key]
    scatter[s.key] = {
        "g1": [float(r["g1"]) for r in pts],
        "g2": [float(r["g2"]) for r in pts],
        "name": [r["alternative_name"] for r in pts],
        "m": [int(r["m"]) for r in pts],
        "hist": [hist_of(r) for r in pts],
    }

pick_out = []
for q in ("Q1", "Q2", "Q3", "Q4"):
    p = picks.get(q)
    if p is None:
        pick_out.append(None); continue
    pick_out.append({
        "q": q, "dataset": p["dataset"], "name": p["alternative_name"],
        "g1": float(p["g1"]), "g2": float(p["g2"]), "m": int(p["m"]),
        "rank_distribution": hist_of(p),
    })

payload = {
    "meta": {
        "source_figure": "final_real_world_parabole.pdf (fig_real)",
        "bounds": {"x_lo": x_lo, "x_hi": x_hi, "y_lo": y_lo, "y_hi": y_hi},
        "x_label": "Standardised skewness γ₁", "y_label": "Excess kurtosis γ₂",
        "unimodal_c": UNIMODAL_C, "datasets": dataset_specs,
        "notes": ("Real PrefLib political profiles; per-candidate rank distribution "
                  "summarised by (g1,g2) with a full best->worst histogram. Q1-Q4 are "
                  "representative picks. Only complete-ranking voters are used."),
    },
    "scatter": scatter, "picks": pick_out,
}
with open(OUT, "w") as f:
    json.dump(payload, f, separators=(",", ":"))
print("wrote", OUT, "(%.1f KB)" % (os.path.getsize(OUT) / 1024))
for k, v in scatter.items():
    print(" ", k, "candidates:", len(v["g1"]), "| hist lens:", sorted(set(len(h) for h in v["hist"])))
print("picks:", [(p["q"], p["name"], "m=%d" % p["m"]) for p in pick_out if p])
