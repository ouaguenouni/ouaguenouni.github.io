"""Regenerate synth_moment.json EXACTLY as the original export (same seed ->
identical points to the paper figure), but ALSO store each cloud point's real
rank-position histogram so the widget can show exact shapes on click.

Run with the research project's venv:
  /Users/mohamedouaguenouni/Incremental_Elicitation_Implementation/.venv/bin/python _regen_synth.py
"""
import os, sys, json
import numpy as np

REPO = "/Users/mohamedouaguenouni/Incremental_Elicitation_Implementation"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "synth_moment.json")

here = os.path.join(REPO, "RESEARCH/2026-05/05/08_moment_plane_witness_patch")
orig_py = os.path.join(REPO, "RESEARCH/2026-04/30/02_final_version_parabole/figures/py")
common = os.path.join(REPO, "RESEARCH/2026-04/29/02_moment_space_figures/figures/py/common")
for p in (REPO, common, orig_py, here):
    if p not in sys.path:
        sys.path.insert(0, p)

from diag_witness_common import generate_candidates, synthetic_cloud
from make_witness_patch import (
    _mirror_of, _per_alt_g1_g2,
    OVERLAY, PALETTE, WITNESS_RED,
    CID_TO_LETTER, CID_TO_DESC, DISPLAY_ORDER, HIST_ORDER,
)

# --- identical parameters + construction to make_witness_patch.main() ---
m = 256
n_voters = 1000
seed = 42
n_hist_bins = 10

cloud_dummy = synthetic_cloud(m)
cands_all = generate_candidates(m, cloud_dummy)
cands = [c for c in cands_all if c.cid in (1, 2, 3, 11)]
c3 = next((c for c in cands if c.cid == 3), None)
if c3 is not None:
    cands.append(_mirror_of(c3, new_cid=4, label="mirror of C3 (low M_4, neg. skew)"))
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

# --- per-family clouds (same RNG stream as the figure) + exact rank histograms ---
HIST_BINS_CLOUD = 16
cedges = np.linspace(0, m, HIST_BINS_CLOUD + 1).astype(int)

def alt_hist(R, a):
    # R[:, a] = positions (0=best .. m-1=worst) of alternative a over voters;
    # same column _per_alt_g1_g2 uses, so the histogram matches its (g1, g2).
    counts = np.bincount(R[:, a].astype(int), minlength=m).astype(float)
    counts /= max(counts.sum(), 1.0)
    return [float(counts[cedges[b]:cedges[b + 1]].sum()) for b in range(HIST_BINS_CLOUD)]

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
        "hist": [alt_hist(R, int(a)) for a in keep],
    })

feas_by_cid = {c.cid: c for c in feas}
witnesses = []
for cid in DISPLAY_ORDER:
    c = feas_by_cid.get(cid)
    if c is None:
        continue
    witnesses.append({
        "cid": int(cid), "letter": CID_TO_LETTER[cid], "desc": CID_TO_DESC[cid],
        "g1": float(c.achieved_g1), "g2": float(c.achieved_g2),
        "has_hist": cid in HIST_ORDER,
    })

edges = np.linspace(0, m, n_hist_bins + 1).astype(int)
def _bin(rd):
    return np.array([rd[edges[b]:edges[b + 1]].sum() for b in range(n_hist_bins)])
histograms = []
for cid in HIST_ORDER:
    c = feas_by_cid.get(cid)
    if c is None:
        continue
    rd = _bin(np.asarray(c.w, dtype=float))
    histograms.append({
        "cid": int(cid), "letter": CID_TO_LETTER[cid], "desc": CID_TO_DESC[cid],
        "bins": rd.astype(float).tolist(),
    })

payload = {
    "meta": {
        "source_figure": "fig_synth_bis.pdf",
        "m": m, "n_voters": n_voters, "seed": seed, "n_hist_bins": n_hist_bins,
        "witness_color": WITNESS_RED,
        "bounds": {"x_lo": x_lo, "x_hi": x_hi, "y_lo": y_lo, "y_hi": y_hi},
        "x_label": "Standardised skewness γ₁",
        "y_label": "Excess kurtosis γ₂",
        "unimodal_c": 186.0 / 125.0,
        "notes": ("Each cloud point is one alternative's per-voter rank-position "
                  "distribution; (g1,g2) plus a 16-bin best->worst histogram. "
                  "A-D (+U) are constructed reference shapes."),
    },
    "clouds": clouds, "witnesses": witnesses, "histograms": histograms,
}

with open(OUT, "w") as f:
    json.dump(payload, f, separators=(",", ":"))
print("wrote", OUT, "(%.1f KB)" % (os.path.getsize(OUT) / 1024))
print("clouds:", len(clouds), "| pts/family:", [len(c["g1"]) for c in clouds])
print("sample witness:", witnesses[0])
print("cloud[0] first hist (16 bins):", [round(x, 3) for x in clouds[0]["hist"][0]])
