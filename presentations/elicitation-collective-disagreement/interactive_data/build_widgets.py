"""Build self-contained interactive Plotly widgets from the exported JSON.

Reads ``presentation/data/*.json`` and writes three standalone HTML files to
``presentation/widgets/``. Each file inlines its own data (so it works from
``file://`` with no server) and pulls Plotly from a CDN. Drop any of them
into a reveal.js slide via an ``<iframe>`` (see ../index.html).

Run after export_data.py:  ``.venv/bin/python presentation/build_widgets.py``
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "widgets")
os.makedirs(OUT, exist_ok=True)

PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.35.2.min.js"


def _load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def _page(title, data_obj, body_js):
    """Assemble a standalone HTML page: Plotly CDN + inlined DATA + render JS."""
    data_js = json.dumps(data_obj, separators=(",", ":"))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title}</title>
<script src="{PLOTLY_CDN}" charset="utf-8"></script>
<style>
  html, body {{ margin:0; padding:0; height:100%; background:#fff;
    font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }}
  #plot {{ width:100%; height:100%; }}
  .ctrl {{ position:absolute; top:8px; left:14px; z-index:10;
    font-size:14px; color:#333; }}
  .ctrl button {{ font:inherit; padding:4px 12px; margin-right:6px;
    border:1px solid #bbb; border-radius:6px; background:#f5f5f5;
    cursor:pointer; }}
  .ctrl button.on {{ background:#222; color:#fff; border-color:#222; }}
</style>
</head>
<body>
<div id="plot"></div>
<script>
const DATA = {data_js};
{body_js}
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Pareto widget: B-vs-MCL / N-vs-MCL toggle.
# ---------------------------------------------------------------------------
PARETO_JS = r"""
const M = DATA.meta;
const COL = M.ell_color;
const KIND_SYMBOL = {chain:"circle", ranking:"square-open"};
let current = "B";  // "B" or "N"

function build(which) {
  const lo = which + "_lo", hi = which + "_hi";
  const traces = [];

  // faded dashed per-family frontiers
  for (const ell of M.ells) {
    const fr = DATA.frontier[which][ell];
    if (!fr) continue;
    traces.push({
      x: fr.x, y: fr.y, mode:"lines", type:"scatter",
      line:{color:COL[ell], width:2, dash:"dash"}, opacity:0.40,
      hoverinfo:"skip", showlegend:false,
    });
  }

  // data markers, grouped by (kind, ell)
  for (const kind of ["chain","ranking"]) {
    for (const ell of M.ells) {
      const sub = DATA.points.filter(p => p.kind===kind && p.ell===ell);
      if (!sub.length) continue;
      traces.push({
        x: sub.map(p=>p.mcl), y: sub.map(p=>p[which]),
        error_y:{type:"data", symmetric:false,
          array: sub.map(p=>p[hi]-p[which]),
          arrayminus: sub.map(p=>p[which]-p[lo]),
          color: COL[ell], thickness:1.2, width:3},
        mode:"markers", type:"scatter",
        marker:{symbol: KIND_SYMBOL[kind], color: kind==="chain"?COL[ell]:"#fff",
          line:{color:COL[ell], width: kind==="chain"?1.8:2.4},
          size: kind==="chain"?11:9},
        customdata: sub.map(p=>[p.k, kind, p[lo], p[hi]]),
        hovertemplate:
          "<b>k=%{customdata[0]}</b> ("+kind+")<br>"+
          "λ = %{x}<br>"+(which==="B"?"B":"N")+" = %{y:,.0f}"+
          "<br>CI: [%{customdata[2]:,.0f}, %{customdata[3]:,.0f}]<extra></extra>",
        showlegend:false,
      });
    }
  }

  // legend-only dummy traces: protocol (shape) + level (colour)
  traces.push({x:[null], y:[null], mode:"markers", type:"scatter",
    name:"Chain (k=ℓ)", marker:{symbol:"circle", color:"#555", size:10},
    legendgroup:"proto"});
  traces.push({x:[null], y:[null], mode:"markers", type:"scatter",
    name:"Ranking (k>ℓ)", marker:{symbol:"square-open", color:"#555",
      line:{color:"#555",width:2}, size:9}, legendgroup:"proto"});
  for (const ell of M.ells)
    traces.push({x:[null], y:[null], mode:"lines", type:"scatter",
      name:"k="+ell, line:{color:COL[ell], width:3}, legendgroup:"level"});

  return traces;
}

function layout(which) {
  return {
    margin:{l:78, r:24, t:54, b:60},
    title:{text:"<b>"+(which==="B"?"Budget B":"Population N")+
      "</b> vs cognitive load &nbsp;(IC, m="+M.m+", ε="+M.epsilon+")",
      font:{size:18}},
    xaxis:{title:{text:M.x_label, font:{size:15}}, range:[0, M.mcl_cutoff],
      dtick:2, gridcolor:"#eee", zeroline:false},
    yaxis:{title:{text:which==="B"?M.y_label_B:M.y_label_N, font:{size:15}},
      type:"log", gridcolor:"#eee"},
    legend:{x:1, y:1, xanchor:"right", yanchor:"top",
      bgcolor:"rgba(255,255,255,0.92)", bordercolor:"#ccc", borderwidth:1,
      font:{size:13}},
    hovermode:"closest", paper_bgcolor:"#fff", plot_bgcolor:"#fff",
  };
}

function render(which) {
  current = which;
  Plotly.react("plot", build(which), layout(which),
    {responsive:true, displaylogo:false,
     modeBarButtonsToRemove:["lasso2d","select2d"]});
  document.getElementById("btnB").className = which==="B"?"on":"";
  document.getElementById("btnN").className = which==="N"?"on":"";
}

const ctrl = document.createElement("div");
ctrl.className = "ctrl";
ctrl.innerHTML =
  '<button id="btnB" class="on">Budget&nbsp;B</button>'+
  '<button id="btnN">Population&nbsp;N</button>';
document.body.appendChild(ctrl);
document.getElementById("btnB").onclick = ()=>render("B");
document.getElementById("btnN").onclick = ()=>render("N");
render("B");
"""


# ---------------------------------------------------------------------------
# Shared parabola geometry for the two moment-plane widgets.
# ---------------------------------------------------------------------------
MOMENT_GEO_JS = r"""
function linspace(a, b, n){const o=[];for(let i=0;i<n;i++)o.push(a+(b-a)*i/(n-1));return o;}

// Pearson + unimodal parabolas and a shaded infeasible region (below Pearson).
function geometryTraces(B, uniC){
  const xs = linspace(B.x_lo, B.x_hi, 240);
  const pear = xs.map(x=>x*x-2.0);
  const uni  = xs.map(x=>x*x-uniC);

  // infeasible polygon: along Pearson curve then back along the floor.
  const polyX = xs.concat(xs.slice().reverse());
  const polyY = pear.map(y=>Math.max(y, B.y_lo))
                    .concat(xs.map(()=>B.y_lo));
  const infeasible = {
    x: polyX, y: polyY, fill:"toself", type:"scatter", mode:"none",
    fillcolor:"rgba(120,120,120,0.10)", hoverinfo:"skip", showlegend:false,
  };
  // band between Pearson and unimodal (unimodal-but-allowed zone)
  const bandX = xs.concat(xs.slice().reverse());
  const bandTop = uni.map(y=>Math.min(y, B.y_hi));
  const bandBot = pear.map(y=>Math.max(y, B.y_lo));
  const band = {
    x: bandX, y: bandTop.concat(bandBot.slice().reverse()),
    fill:"toself", type:"scatter", mode:"none",
    fillcolor:"rgba(120,120,120,0.10)", hoverinfo:"skip", showlegend:false,
  };
  const pearsonLine = {x:xs, y:pear, mode:"lines", type:"scatter",
    line:{color:"#404040", width:1.6}, hoverinfo:"skip", showlegend:false,
    name:"Pearson γ₂=γ₁²−2"};
  const uniLine = {x:xs, y:uni, mode:"lines", type:"scatter",
    line:{color:"#404040", width:1.3, dash:"dashdot"}, hoverinfo:"skip",
    showlegend:false, name:"unimodal γ₂=γ₁²−186/125"};
  return [infeasible, band, pearsonLine, uniLine];
}

// 2x2 histogram-panel axis domains on the right of the figure.
const HIST_DOMAINS = [
  {x:[0.70,0.835], y:[0.60,1.00]},   // top-left
  {x:[0.865,1.00], y:[0.60,1.00]},   // top-right
  {x:[0.70,0.835], y:[0.00,0.40]},   // bottom-left
  {x:[0.865,1.00], y:[0.00,0.40]},   // bottom-right
];
"""


SYNTH_JS = MOMENT_GEO_JS + r"""
const M = DATA.meta, B = M.bounds;
const traces = geometryTraces(B, M.unimodal_c);

// cloud families
for (const c of DATA.clouds) {
  traces.push({
    x:c.g1, y:c.g2, mode:"markers", type:"scatter", name:c.label,
    marker:{color:c.color, size:6, opacity:0.75,
      line:{color:"#fff", width:0.4}},
    hovertemplate:c.label+"<br>γ₁=%{x:.3f}, γ₂=%{y:.3f}<extra></extra>",
  });
}

// witnesses
const wx = DATA.witnesses.map(w=>w.g1), wy = DATA.witnesses.map(w=>w.g2);
traces.push({
  x:wx, y:wy, mode:"markers+text", type:"scatter", name:"reference shapes",
  text:DATA.witnesses.map(w=>w.letter), textposition:"top center",
  textfont:{color:M.witness_color, size:13, family:"Georgia, serif"},
  marker:{symbol:"triangle-up", color:M.witness_color, size:14,
    line:{color:"#fff", width:0.6}},
  customdata:DATA.witnesses.map(w=>[w.letter, w.desc]),
  hovertemplate:"<b>%{customdata[0]}</b> — %{customdata[1]}"+
    "<br>γ₁=%{x:.3f}, γ₂=%{y:.3f}<extra></extra>",
  showlegend:false,
});

// histogram bars (A,B,C,D) on their own axes
const binMid = []; for (let i=0;i<10;i++) binMid.push(i);
DATA.histograms.forEach((h, i) => {
  const ax = i+2;  // x2..x5 / y2..y5
  traces.push({
    x:binMid, y:h.bins, type:"bar",
    marker:{color:M.witness_color, line:{color:"#000", width:0.4}},
    xaxis:"x"+ax, yaxis:"y"+ax, width:0.92,
    hovertemplate:h.letter+" bin %{x}: %{y:.3f}<extra></extra>",
    showlegend:false,
  });
});

const layout = {
  margin:{l:64, r:8, t:34, b:120},
  xaxis:{domain:[0.0,0.595], title:{text:M.x_label, font:{size:15}},
    range:[B.x_lo,B.x_hi], gridcolor:"#eee", zeroline:false},
  yaxis:{domain:[0.0,1.0], title:{text:M.y_label, font:{size:15}},
    range:[B.y_lo,B.y_hi], gridcolor:"#eee", zeroline:false},
  legend:{orientation:"h", x:0.30, y:-0.16, xanchor:"center", yanchor:"top",
    font:{size:11.5}, title:{text:"Sampled alternatives (per profile family) · ▲ reference shapes",
    font:{size:12}}},
  barmode:"overlay", hovermode:"closest",
  paper_bgcolor:"#fff", plot_bgcolor:"#fff",
  annotations:[],
};

// build the 4 hist axes + their red-circle letter titles
DATA.histograms.forEach((h, i) => {
  const ax = i+2, d = HIST_DOMAINS[i];
  layout["xaxis"+ax] = {domain:d.x, anchor:"y"+ax,
    tickvals:[0,9], ticktext:["best","worst"], tickfont:{size:10}, ticklen:0};
  layout["yaxis"+ax] = {domain:d.y, anchor:"x"+ax,
    showticklabels:true, tickfont:{size:9}, gridcolor:"#f0f0f0"};
  layout.annotations.push({
    text:"<b>"+h.letter+"</b>", x:(d.x[0]+d.x[1])/2, y:d.y[1]+0.035,
    xref:"paper", yref:"paper", showarrow:false,
    font:{color:M.witness_color, size:13},
  });
});
// title for the histogram column
layout.annotations.push({
  text:"Rank of a over reference profiles  (best → worst)",
  x:0.85, y:1.06, xref:"paper", yref:"paper", showarrow:false,
  font:{size:11.5, color:"#333"},
});

Plotly.newPlot("plot", traces, layout,
  {responsive:true, displaylogo:false,
   modeBarButtonsToRemove:["lasso2d","select2d"]});
"""


REAL_JS = MOMENT_GEO_JS + r"""
const M = DATA.meta, B = M.bounds;
const traces = geometryTraces(B, M.unimodal_c);

// Gaussian (0,0) and two-point symmetric (0,-2) reference '+' glyphs
traces.push({x:[0,0], y:[0,-2], mode:"markers", type:"scatter",
  marker:{symbol:"cross-thin", color:"#000", size:12,
    line:{color:"#000", width:2}},
  hovertemplate:"reference (%{x}, %{y})<extra></extra>", showlegend:false});

// dataset clouds
const colByKey = {};
for (const d of M.datasets) colByKey[d.key] = d.color;
for (const d of M.datasets) {
  const s = DATA.scatter[d.key];
  if (!s) continue;
  traces.push({
    x:s.g1, y:s.g2, mode:"markers", type:"scatter",
    name:d.label+"  ·  "+s.g1.length+" alt.",
    marker:{color:d.color, size: d.key==="nswla"?6:7,
      opacity: d.key==="nswla"?0.7:0.85, line:{color:"#fff", width:0.4}},
    customdata:s.name.map((nm,i)=>[nm, s.m[i]]),
    hovertemplate:"%{customdata[0]} (m=%{customdata[1]})"+
      "<br>γ₁=%{x:.3f}, γ₂=%{y:.3f}<extra></extra>",
  });
}

// Q1..Q4 picks: circled markers + Q labels
const picks = DATA.picks.filter(p=>p);
traces.push({
  x:picks.map(p=>p.g1), y:picks.map(p=>p.g2), mode:"markers+text",
  type:"scatter", text:picks.map(p=>p.q), textposition:"middle right",
  textfont:{color:"#000", size:13}, cliponaxis:false,
  marker:{symbol:"circle-open", color:"#000", size:18, line:{width:1.8}},
  customdata:picks.map(p=>[p.name, p.q]),
  hovertemplate:"<b>%{customdata[1]}</b> %{customdata[0]}"+
    "<br>γ₁=%{x:.3f}, γ₂=%{y:.3f}<extra></extra>",
  showlegend:false,
});

// histograms for Q1..Q4 (full rank distributions)
picks.forEach((p, i) => {
  const ax = i+2;
  const xs = []; for (let k=0;k<p.m;k++) xs.push(k);
  traces.push({
    x:xs, y:p.rank_distribution, type:"bar",
    marker:{color:colByKey[p.dataset]||"#777", line:{color:"#000", width:0.4}},
    xaxis:"x"+ax, yaxis:"y"+ax, width:0.95,
    hovertemplate:p.q+" rank %{x}: %{y:.3f}<extra></extra>",
    showlegend:false,
  });
});

const layout = {
  margin:{l:64, r:8, t:34, b:96},
  xaxis:{domain:[0.0,0.595], title:{text:M.x_label, font:{size:15}},
    range:[B.x_lo,B.x_hi], gridcolor:"#eee", zeroline:false},
  yaxis:{domain:[0.0,1.0], title:{text:M.y_label, font:{size:15}},
    range:[B.y_lo,B.y_hi], gridcolor:"#eee", zeroline:false},
  legend:{orientation:"h", x:0.30, y:-0.13, xanchor:"center", yanchor:"top",
    font:{size:11.5}},
  barmode:"overlay", hovermode:"closest",
  paper_bgcolor:"#fff", plot_bgcolor:"#fff", annotations:[],
};

picks.forEach((p, i) => {
  const ax = i+2, d = HIST_DOMAINS[i];
  layout["xaxis"+ax] = {domain:d.x, anchor:"y"+ax,
    tickvals:[0, p.m-1], ticktext:["best","worst"], tickfont:{size:10}, ticklen:0};
  layout["yaxis"+ax] = {domain:d.y, anchor:"x"+ax,
    showticklabels:true, tickfont:{size:9}, gridcolor:"#f0f0f0"};
  const nm = p.name.length>20 ? p.name.slice(0,18)+"…" : p.name;
  layout.annotations.push({
    text:"<b>"+p.q+"</b> "+nm+"<br>γ₁="+p.g1.toFixed(2)+", γ₂="+p.g2.toFixed(2),
    x:d.x[0], y:d.y[1]+0.055, xref:"paper", yref:"paper", showarrow:false,
    align:"left", xanchor:"left", font:{size:9.5, color:"#222"},
  });
});

Plotly.newPlot("plot", traces, layout,
  {responsive:true, displaylogo:false,
   modeBarButtonsToRemove:["lasso2d","select2d"]});
"""


def main():
    widgets = [
        ("pareto.html", "Pareto — Budget/Population vs cognitive load",
         _load("pareto.json"), PARETO_JS),
        ("synth_moment.html", "Synthetic moment plane (γ₁, γ₂)",
         _load("synth_moment.json"), SYNTH_JS),
        ("real_moment.html", "Real preferential data — moment plane (γ₁, γ₂)",
         _load("real_moment.json"), REAL_JS),
    ]
    for fname, title, data, js in widgets:
        html = _page(title, data, js)
        path = os.path.join(OUT, fname)
        with open(path, "w") as f:
            f.write(html)
        print(f"  wrote widgets/{fname}  ({len(html)/1024:.1f} KB)")
    print("done.")


if __name__ == "__main__":
    main()
