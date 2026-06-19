"""Generate pareto_widget.html — interactive population-vs-cognitive-load explorer,
built on the paper's Pareto figure (pareto.json). Three query modes:
  A. degree + population N  -> the cheapest cognitive load (MCL) + protocol
  B. degree + MCL           -> the population N + protocol
  C. population N + MCL      -> which degrees are reachable
Self-contained: data inlined, Plotly via CDN.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "interactive_data/data/pareto.json")))
PLOTLY = "https://cdn.plot.ly/plotly-2.35.2.min.js"

JS = r"""
const M = DATA.meta, COL = M.ell_color, ELLS = M.ells;
const PTS = {};               // ell -> [points sorted by mcl]
ELLS.forEach(e => PTS[e] = []);
DATA.points.forEach(p => PTS[p.ell].push(p));
ELLS.forEach(e => PTS[e].sort((a,b)=>a.mcl-b.mcl));
const SERIF='"Palatino Linotype","Book Antiqua",Palatino,Georgia,serif';
const INK="#111", MUTED="#6b6b6b";

// y-range (population)
let nlo=1e9, nhi=0;
DATA.points.forEach(p=>{ nlo=Math.min(nlo,p.N); nhi=Math.max(nhi,p.N); });
const Y0=Math.floor(Math.log10(nlo*0.8)*100)/100, Y1=Math.ceil(Math.log10(nhi*1.25)*100)/100;
const XMAX = M.mcl_cutoff;

function fmt(n){ return n.toLocaleString('en-US'); }
function proto(p){ return "$"+p.k+"$-"+p.kind; }
function protoTxt(p){ return p.k+"-"+p.kind; }

// ---------- base traces ----------
const CHAIN0 = 0;   // first NELL traces are per-ell points; then highlight; then frontiers handled separately
function buildTraces(){
  const T=[];
  // faded per-ell frontiers (population)
  ELLS.forEach(e=>{ const fr=DATA.frontier.N[e]; if(!fr) return;
    T.push({x:fr.x,y:fr.y,mode:"lines",type:"scatter",line:{color:COL[e],width:2,dash:"dot"},
      opacity:0.35,hoverinfo:"skip",showlegend:false}); });
  // points per ell
  ELLS.forEach(e=>{ const sub=PTS[e];
    T.push({x:sub.map(p=>p.mcl),y:sub.map(p=>p.N),mode:"markers",type:"scatter",name:"ℓ="+e,
      marker:{color:COL[e],size:11,
        symbol:sub.map(p=>p.kind==="chain"?"circle":"square-open"),
        line:{color:COL[e],width:2}},
      customdata:sub.map(p=>[e,p.k,p.kind,p.mcl,p.N,p.B]),
      hovertemplate:"<b>ℓ=%{customdata[0]}</b> · %{customdata[1]}-%{customdata[2]}<br>"+
        "MCL=%{customdata[3]} · N=%{customdata[4]:,} · B=%{customdata[5]:,}<extra></extra>"}); });
  // highlight trace (answer points)
  T.push({x:[],y:[],mode:"markers",type:"scatter",
    marker:{symbol:"circle-open",color:INK,size:30,line:{width:2.5}},
    hoverinfo:"skip",showlegend:false});
  return T;
}
const HID = ELLS.length*2;   // index of highlight trace
const layout = {
  margin:{l:66,r:14,t:10,b:48},
  xaxis:{title:{text:"Max cognitive load  λ  (comparisons / voter)",font:{size:14,family:SERIF}},
    range:[0,XMAX],gridcolor:"#eee",zeroline:false,tickfont:{family:SERIF},dtick:2},
  yaxis:{title:{text:"Population  N  (voters)",font:{size:14,family:SERIF}},type:"log",
    range:[Y0,Y1],gridcolor:"#eee",tickfont:{family:SERIF}},
  legend:{orientation:"h",x:0.5,y:1.02,xanchor:"center",yanchor:"bottom",font:{size:12,family:SERIF}},
  hovermode:"closest",paper_bgcolor:"#fff",plot_bgcolor:"#fff",shapes:[],
};
Plotly.newPlot("plot",buildTraces(),layout,{responsive:true,displaylogo:false,
  modeBarButtonsToRemove:["lasso2d","select2d","autoScale2d"]});

// ---------- state ----------
let mode="A", deg=3, Nval=10000, Mval=7;

function hline(y,color){ return {type:"line",x0:0,x1:XMAX,y0:y,y1:y,xref:"x",yref:"y",
  line:{color:color,width:1.5,dash:"dash"}}; }
function vline(x,color){ return {type:"line",x0:x,x1:x,y0:Math.pow(10,Y0),y1:Math.pow(10,Y1),xref:"x",yref:"y",
  line:{color:color,width:1.5,dash:"dash"}}; }
function box(x,y){ return {type:"rect",x0:0,x1:x,y0:Math.pow(10,Y0),y1:y,xref:"x",yref:"y",
  fillcolor:"rgba(120,120,120,0.10)",line:{width:0}}; }

function recompute(){
  let shapes=[], hx=[], hy=[], res="";
  if(mode==="A"){
    const feas=PTS[deg].filter(p=>p.N<=Nval);
    shapes=[hline(Nval,INK)];
    if(feas.length){ const a=feas.reduce((x,y)=>x.mcl<y.mcl?x:y); hx=[a.mcl];hy=[a.N];
      res="With <b>"+fmt(Nval)+" voters</b>, degree <b>"+deg+"</b> is reachable at the lightest load by the "+
        "<b>"+protoTxt(a)+"</b> &rarr; <b>MCL = "+a.mcl+"</b> &nbsp;(N = "+fmt(a.N)+")."; }
    else { const mn=PTS[deg].reduce((x,y)=>x.N<y.N?x:y);
      res="Degree <b>"+deg+"</b> needs more than "+fmt(Nval)+" voters — even the heaviest query (the "+
        protoTxt(mn)+") needs <b>"+fmt(mn.N)+"</b>."; }
  } else if(mode==="B"){
    const feas=PTS[deg].filter(p=>p.mcl<=Mval);
    shapes=[vline(Mval,INK)];
    if(feas.length){ const a=feas.reduce((x,y)=>x.N<y.N?x:y); hx=[a.mcl];hy=[a.N];
      res="Degree <b>"+deg+"</b> at <b>MCL &le; "+Mval+"</b>: use the <b>"+protoTxt(a)+"</b> &rarr; "+
        "<b>N = "+fmt(a.N)+" voters</b> &nbsp;(MCL = "+a.mcl+")."; }
    else { const ch=PTS[deg][0];
      res="MCL "+Mval+" is too low for degree <b>"+deg+"</b>: the cheapest query is the "+protoTxt(ch)+
        " at <b>MCL = "+ch.mcl+"</b>. Raise the load."; }
  } else { // C
    shapes=[box(Mval,Nval),hline(Nval,INK),vline(Mval,INK)];
    const ok=[];
    ELLS.forEach(e=>{ const f=PTS[e].filter(p=>p.mcl<=Mval&&p.N<=Nval);
      if(f.length){ ok.push(e); const a=f.reduce((x,y)=>x.N<y.N?x:y); hx.push(a.mcl);hy.push(a.N); } });
    res = ok.length
      ? "With <b>N &le; "+fmt(Nval)+"</b> and <b>MCL &le; "+Mval+"</b>, reachable degrees: <b>"+ok.join(", ")+"</b>."
      : "No degree is reachable with N &le; "+fmt(Nval)+" and MCL &le; "+Mval+" — loosen a constraint.";
  }
  Plotly.relayout("plot",{shapes});
  Plotly.restyle("plot",{x:[hx],y:[hy]},[HID]);
  document.getElementById("result").innerHTML=res;
}

// ---------- controls ----------
function setMode(m){ mode=m;
  document.querySelectorAll("#tabs .tab").forEach(b=>b.classList.toggle("on",b.dataset.m===m));
  document.getElementById("ctl-deg").style.display=(m==="A"||m==="B")?"":"none";
  document.getElementById("ctl-N").style.display=(m==="A"||m==="C")?"":"none";
  document.getElementById("ctl-M").style.display=(m==="B"||m==="C")?"":"none";
  const desc={A:"Fix the <b>degree</b> and how many <b>voters</b> you have → the lightest cognitive load.",
              B:"Fix the <b>degree</b> and the <b>cognitive load</b> → how many voters you need.",
              C:"Fix the <b>voters</b> and the <b>cognitive load</b> → which degrees you can reach."};
  document.getElementById("modedesc").innerHTML=desc[m];
  recompute(); }

function nFromSlider(v){ return Math.round(Math.pow(10,+v)); }
function nToSlider(n){ return Math.log10(n); }

document.querySelectorAll("#tabs .tab").forEach(b=> b.onclick=()=>setMode(b.dataset.m));
document.querySelectorAll("#ctl-deg .db").forEach(b=> b.onclick=()=>{
  deg=+b.dataset.d; document.querySelectorAll("#ctl-deg .db").forEach(x=>x.classList.toggle("on",x===b)); recompute(); });
const ns=document.getElementById("nslider"), ms=document.getElementById("mslider");
ns.oninput=()=>{ Nval=nFromSlider(ns.value); document.getElementById("nval").textContent=fmt(Nval); recompute(); };
ms.oninput=()=>{ Mval=+ms.value; document.getElementById("mval").textContent=Mval; recompute(); };

// init slider ranges
ns.min=Y0.toFixed(2); ns.max=Y1.toFixed(2); ns.step="0.01"; ns.value=nToSlider(Nval).toFixed(2);
ms.min="1"; ms.max=String(Math.round(XMAX)); ms.step="1"; ms.value=String(Mval);
document.getElementById("nval").textContent=fmt(Nval);
document.getElementById("mval").textContent=Mval;
document.querySelectorAll("#ctl-deg .db").forEach(x=>x.classList.toggle("on",+x.dataset.d===deg));
const qm=new URLSearchParams(location.search).get("mode");
setMode(["A","B","C"].includes(qm)?qm:"A");
"""

HTML = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Pareto explorer</title>
<link rel="icon" href="data:,">
<script src="__PLOTLY__" charset="utf-8"></script>
<style>
  html,body{margin:0;padding:0;height:100%;background:#fff;
    font-family:"Palatino Linotype","Book Antiqua",Palatino,Georgia,serif;color:#111;}
  #narr{height:40px;min-height:40px;line-height:40px;padding:0 18px;font-size:17px;
    border-bottom:1px solid #ededed;white-space:nowrap;overflow:hidden;}
  #narr b{color:#9a1b1b;font-weight:700;}
  #wrap{display:flex;height:calc(100% - 41px);width:100%;}
  #plot{flex:1 1 auto;min-width:0;height:100%;}
  #panel{flex:0 0 338px;display:flex;flex-direction:column;border-left:1px solid #e4e4e4;
    padding:12px 14px;box-sizing:border-box;}
  #tabs{display:flex;flex-direction:column;gap:6px;margin-bottom:12px;}
  #tabs .tab{font-family:inherit;font-size:13px;text-align:left;padding:7px 10px;border:1px solid #ccc;
    border-radius:8px;background:#fff;color:#222;cursor:pointer;line-height:1.25;}
  #tabs .tab.on{border-color:#9a1b1b;background:#faf2f2;color:#9a1b1b;}
  #modedesc{font-size:13.5px;color:#444;line-height:1.4;margin-bottom:12px;min-height:34px;}
  .ctl{margin:10px 0;}
  .ctl .cl{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#9a1b1b;margin-bottom:6px;}
  #ctl-deg .db{font:inherit;font-size:14px;width:34px;padding:4px 0;margin-right:6px;border:1px solid #ccc;
    border-radius:6px;background:#fff;cursor:pointer;}
  #ctl-deg .db.on{background:#222;color:#fff;border-color:#222;}
  input[type=range]{width:100%;}
  .val{font-size:14px;color:#111;font-weight:700;}
  #result{margin-top:16px;padding-top:12px;border-top:1px solid #ededed;font-size:15px;line-height:1.5;color:#222;}
</style></head>
<body>
<div id="narr">Reading the elicitation frontier — chain = ● &nbsp; ranking = ▢</div>
<div id="wrap">
  <div id="plot"></div>
  <div id="panel">
    <div id="tabs">
      <button class="tab" data-m="A">degree + voters → <b>load</b></button>
      <button class="tab" data-m="B">degree + load → <b>voters</b></button>
      <button class="tab" data-m="C">voters + load → <b>degrees</b></button>
    </div>
    <div id="modedesc"></div>
    <div class="ctl" id="ctl-deg"><div class="cl">Degree ℓ</div>
      <button class="db" data-d="2">2</button><button class="db" data-d="3">3</button><button class="db" data-d="4">4</button><button class="db" data-d="5">5</button></div>
    <div class="ctl" id="ctl-N"><div class="cl">Population N — <span class="val" id="nval"></span> voters</div>
      <input type="range" id="nslider"></div>
    <div class="ctl" id="ctl-M"><div class="cl">Max cognitive load λ — <span class="val" id="mval"></span></div>
      <input type="range" id="mslider"></div>
    <div id="result"></div>
  </div>
</div>
<script>
const DATA = __DATA__;
__JS__
</script>
</body></html>
"""

out = (HTML.replace("__PLOTLY__", PLOTLY)
           .replace("__DATA__", json.dumps(DATA, separators=(",", ":")))
           .replace("__JS__", JS))
open(os.path.join(HERE, "pareto_widget.html"), "w").write(out)
print("wrote pareto_widget.html  (%.1f KB)" % (len(out)/1024))
