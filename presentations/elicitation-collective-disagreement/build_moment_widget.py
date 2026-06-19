"""Generate moment_plane.html — interactive (γ₁, γ₂) moment-plane widget.
Inlines BOTH the synthetic and real datasets; one widget, three modes:
  ?mode=explain     guided synthetic tour (5 narrated stages)
  ?mode=realguided  guided real-data view (points spread + 4 reference dists on the side)
  ?mode=play        dedicated interactive: synthetic + real points, toggle subsections, click->dist
Guided stages driven by postMessage({stage:N}) / ?stage=N.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SYNTH = json.load(open(os.path.join(HERE, "interactive_data/data/synth_moment.json")))
REAL = json.load(open(os.path.join(HERE, "interactive_data/data/real_moment.json")))
PLOTLY = "https://cdn.plot.ly/plotly-2.35.2.min.js"


def normalize_real(r):
    clouds = []
    for ds in r["meta"]["datasets"]:
        s = r["scatter"].get(ds["key"])
        if not s:
            continue
        clouds.append({"key": ds["key"], "name": ds["label"], "param": "",
                       "color": ds["color"], "label": ds["label"],
                       "g1": s["g1"], "g2": s["g2"], "hist": s["hist"],
                       "pointnames": s["name"]})
    wit, hists = [], []
    for p in r["picks"]:
        if not p:
            continue
        wit.append({"cid": 0, "letter": p["q"], "desc": p["name"],
                    "g1": p["g1"], "g2": p["g2"], "has_hist": True})
        hists.append({"letter": p["q"], "desc": p["name"], "bins": p["rank_distribution"]})
    meta = dict(r["meta"]); meta["bounds"] = dict(meta["bounds"])
    meta["bounds"]["y_hi"] = meta["bounds"]["y_hi"] + 0.5
    return {"meta": meta, "clouds": clouds, "witnesses": wit, "histograms": hists}


DATA = {"synth": SYNTH, "real": normalize_real(REAL)}

JS = r"""
const RAW = DATA;
const params = new URLSearchParams(location.search);
const MODE = params.get('mode') || 'play';
const RED = RAW.synth.meta.witness_color;
const UC = RAW.synth.meta.unimodal_c;
const XLAB = RAW.synth.meta.x_label, YLAB = RAW.synth.meta.y_label;
const INK="#111", MUTED="#6b6b6b";
const SERIF='"Palatino Linotype","Book Antiqua",Palatino,Georgia,serif';
const CLOUD_OP = 0.85, WIT_OP = (MODE==='explain') ? 1.0 : 0.85;

function ub(a,b){return {x_lo:Math.min(a.x_lo,b.x_lo),x_hi:Math.max(a.x_hi,b.x_hi),
  y_lo:Math.min(a.y_lo,b.y_lo),y_hi:Math.max(a.y_hi,b.y_hi)};}

let CLOUDS, WITS, HISTS, B;
if (MODE==='explain') { CLOUDS=RAW.synth.clouds; WITS=RAW.synth.witnesses; HISTS=RAW.synth.histograms; B=RAW.synth.meta.bounds; }
else if (MODE==='realguided') { CLOUDS=RAW.real.clouds; WITS=RAW.real.witnesses; HISTS=RAW.real.histograms; B=RAW.real.meta.bounds; }
else { // play: combined
  CLOUDS = RAW.synth.clouds.map(c=>Object.assign({},c,{group:"Synthetic models"}))
        .concat(RAW.real.clouds.map(c=>Object.assign({},c,{group:"Real elections"})));
  WITS = RAW.synth.witnesses.concat(RAW.real.witnesses);
  HISTS = RAW.synth.histograms.concat(RAW.real.histograms);
  B = ub(RAW.synth.meta.bounds, RAW.real.meta.bounds);
}
const NC = CLOUDS.length;

function lin(a,b,n){const o=[];for(let i=0;i<n;i++)o.push(a+(b-a)*i/(n-1));return o;}
const PADX = 0.6*(B.x_hi-B.x_lo);
const YLOW = B.y_lo - 2.0;
const XS = lin(B.x_lo-PADX, B.x_hi+PADX, 280);
const PEAR = XS.map(x=>x*x-2.0);
const UNI  = XS.map(x=>x*x-UC);

function bimodalPoint(){
  let best=null;
  CLOUDS.forEach((c,ci)=>{ for(let i=0;i<c.g1.length;i++){ const g1=c.g1[i],g2=c.g2[i];
    if(g2 < g1*g1-UC && Math.abs(g1)<0.22){ if(!best||g2<best.g2) best={ci,i,g1,g2,c}; } }});
  return best;
}
const BP = bimodalPoint();

// 0 infeasible fill | 1 Pearson | 2 frontier | 3 multimodal fill | 4 circle | 5.. clouds | last witnesses
const T = [];
T.push({x:XS.concat(XS.slice().reverse()),
  y:PEAR.map(y=>Math.max(y,YLOW)).concat(XS.map(()=>YLOW)),
  fill:"toself", mode:"none", type:"scatter", fillcolor:"rgba(120,120,120,0.10)",
  hoverinfo:"skip", showlegend:false, opacity:0});
T.push({x:XS, y:PEAR, mode:"lines", type:"scatter", line:{color:INK, width:2},
  hoverinfo:"skip", showlegend:false, opacity:0});
T.push({x:XS, y:UNI, mode:"lines", type:"scatter", line:{color:INK, width:1.5, dash:"dashdot"},
  hoverinfo:"skip", showlegend:false, opacity:0});
T.push({x:XS.concat(XS.slice().reverse()),
  y:UNI.map(y=>Math.min(y,B.y_hi)).concat(XS.map(()=>YLOW)),
  fill:"toself", mode:"none", type:"scatter", fillcolor:"rgba(154,27,27,0.07)",
  hoverinfo:"skip", showlegend:false, opacity:0});
T.push({x: BP?[BP.g1]:[], y: BP?[BP.g2]:[], mode:"markers", type:"scatter",
  marker:{symbol:"circle-open", color:RED, size:30, line:{width:2.5}},
  hoverinfo:"skip", showlegend:false, opacity:0});
const CLOUD0 = T.length;
const shown = (MODE!=='explain');
for (const c of CLOUDS){
  const nm = c.pointnames ? c.pointnames : c.g1.map(()=>c.label);
  T.push({x:c.g1, y:c.g2, mode:"markers", type:"scatter", name:c.label,
    marker:{color:c.color, size:6, opacity:CLOUD_OP, line:{color:"#fff", width:0.4}},
    opacity: shown?1:0, showlegend:false, customdata: nm,
    hovertemplate:"<b>%{customdata}</b><br>γ₁=%{x:.3f}, γ₂=%{y:.3f}<extra></extra>"});
}
const WIDX = T.length;
const WL = WITS.map(w=>w.letter);
T.push({x:WITS.map(w=>w.g1), y:WITS.map(w=>w.g2),
  mode:"markers+text", type:"scatter", name:"references",
  text:WL, textposition:"top center", textfont:{color:RED, size:14, family:SERIF},
  marker:{symbol:"triangle-up", color:RED, size:13, opacity:WIT_OP, line:{color:"#fff",width:0.8}},
  opacity: shown?1:0, showlegend:false,
  customdata:WITS.map(w=>[w.letter,w.desc]),
  hovertemplate:"<b>%{customdata[0]}</b> — %{customdata[1]}<br>γ₁=%{x:.3f}, γ₂=%{y:.3f}<extra></extra>"});

const baseLayout = {
  margin:{l:56, r:12, t:10, b:44},
  xaxis:{title:{text:XLAB, font:{size:16, family:SERIF}}, range:[B.x_lo,B.x_hi],
    gridcolor:"#eee", zeroline:false, tickfont:{family:SERIF}, visible:(MODE!=='explain')},
  yaxis:{title:{text:YLAB, font:{size:16, family:SERIF}}, range:[B.y_lo,B.y_hi],
    gridcolor:"#eee", zeroline:false, tickfont:{family:SERIF}, visible:(MODE!=='explain')},
  hovermode:"closest", paper_bgcolor:"#fff", plot_bgcolor:"#fff", showlegend:false,
};
const CONFIG = {responsive:true, displaylogo:false, doubleClick:"reset",
  modeBarButtonsToRemove:["lasso2d","select2d","autoScale2d"]};
Plotly.newPlot("plot", T, baseLayout, CONFIG);

// ---------- helpers ----------
function setNarr(t){ document.getElementById("narr").innerHTML = t || ""; }
function clearSide(){ Plotly.purge("side"); document.getElementById("side").innerHTML="";
  document.getElementById("sidecap").innerHTML=""; }
function gramCharlier(g1,g2,n){
  const lo=-3.2,hi=3.2,z=[],d=[]; for(let i=0;i<n;i++) z.push(lo+(hi-lo)*(i+0.5)/n);
  for(const v of z){const phi=Math.exp(-v*v/2)/Math.sqrt(2*Math.PI);
    const He3=v*v*v-3*v,He4=v*v*v*v-6*v*v+3; d.push(Math.max(phi*(1+(g1/6)*He3+(g2/24)*He4),0));}
  const s=d.reduce((a,b)=>a+b,0)||1; return d.map(x=>x/s);
}
function drawDist(bins,color,title,sub){
  const n=bins.length,xs=[];for(let i=0;i<n;i++)xs.push(i);
  Plotly.react("side",[{x:xs,y:bins,type:"bar",marker:{color:color,line:{color:"#fff",width:0.5}},
    width:0.92,hovertemplate:"rank %{x}: %{y:.3f}<extra></extra>"}],
    {margin:{l:28,r:10,t:8,b:30},
     xaxis:{tickvals:[0,n-1],ticktext:["best","worst"],tickfont:{size:12,family:SERIF},ticklen:0,range:[-0.6,n-0.4]},
     yaxis:{showticklabels:false,gridcolor:"#f0f0f0",rangemode:"tozero",fixedrange:true},
     paper_bgcolor:"#fff",plot_bgcolor:"#fff",showlegend:false,bargap:0.12},
    {responsive:true,displayModeBar:false});
  document.getElementById("sidecap").innerHTML =
    "<b style='color:"+color+"'>"+title+"</b>"+(sub?"<br><span class='sub'>"+sub+"</span>":"");
}
function regionOf(g1,g2){
  if(g2 < g1*g1-UC) return "multimodal — two camps";
  if(Math.abs(g1)<0.12 && g2>-0.4) return "near-symmetric, peaked";
  if(g1>0.2) return "consensus winner, minority tail";
  if(g1<-0.2) return "consensus rejection, minority tail";
  return "unimodal";
}
function witBins(L){
  const w=WITS.find(x=>x.letter===L), h=HISTS.find(x=>x.letter===L);
  return h?h.bins:(L==="U"?Array(10).fill(0.1):gramCharlier(w.g1,w.g2,10));
}
function showWitness(L){ const w=WITS.find(x=>x.letter===L);
  drawDist(witBins(L), RED, L+" — "+w.desc,
    "γ₁="+w.g1.toFixed(2)+",  γ₂="+w.g2.toFixed(2)+"  ·  exact rank distribution"); }
function showCloudPoint(c,i){
  const g1=c.g1[i],g2=c.g2[i];
  const ttl = (c.pointnames && c.pointnames[i]) ? (c.pointnames[i]+"  ·  "+c.label) : (c.name+" · "+c.param);
  if(c.hist && c.hist[i]) drawDist(c.hist[i], c.color, ttl,
    "γ₁="+g1.toFixed(2)+", γ₂="+g2.toFixed(2)+"  ·  "+regionOf(g1,g2)+"  ·  exact rank distribution");
  else drawDist(gramCharlier(g1,g2,21), c.color, ttl,
    "γ₁="+g1.toFixed(2)+", γ₂="+g2.toFixed(2)+"  ·  "+regionOf(g1,g2));
}
// 2x2 grid of the first four references
function drawWitnessGrid(){
  const four = WITS.slice(0,4);
  const dom=[{x:[0.02,0.47],y:[0.57,1]},{x:[0.55,1],y:[0.57,1]},
             {x:[0.02,0.47],y:[0.04,0.47]},{x:[0.55,1],y:[0.04,0.47]}];
  const traces=[], lay={margin:{l:6,r:6,t:18,b:6},paper_bgcolor:"#fff",plot_bgcolor:"#fff",
    showlegend:false,annotations:[]};
  four.forEach((w,i)=>{ const bins=witBins(w.letter), n=bins.length, xs=bins.map((_,j)=>j);
    const sfx=(i===0)?"":(i+1);
    traces.push({x:xs,y:bins,type:"bar",marker:{color:RED},xaxis:"x"+sfx,yaxis:"y"+sfx,
      width:0.9,hoverinfo:"skip"});
    lay["xaxis"+sfx]={domain:dom[i].x,anchor:"y"+sfx,tickvals:[0,n-1],ticktext:["",""],ticklen:0,showticklabels:false};
    lay["yaxis"+sfx]={domain:dom[i].y,anchor:"x"+sfx,showticklabels:false,rangemode:"tozero"};
    let nm=w.desc; if(nm.length>22) nm=nm.slice(0,20)+"…";
    lay.annotations.push({text:"<b>"+w.letter+"</b> · "+nm,x:dom[i].x[0],y:dom[i].y[1]+0.045,
      xref:"paper",yref:"paper",showarrow:false,xanchor:"left",font:{size:10,color:RED,family:SERIF}});
  });
  Plotly.react("side",traces,lay,{responsive:true,displayModeBar:false});
}

// ---------- family list below the figure (explain stage 2) ----------
function clearFamList(){ document.getElementById("famlist").innerHTML=""; }
function addFam(k){ const c=CLOUDS[k];
  const el=document.createElement("span"); el.className="famitem";
  el.innerHTML="<span class='sw' style='background:"+c.color+"'></span>"+c.name+(c.param?(" · "+c.param):"");
  document.getElementById("famlist").appendChild(el); }

// ---------- toggle buttons (play) grouped into subsections ----------
function makeToggles(){
  const host=document.getElementById("toggles"); host.innerHTML="";
  const groups={}, order=[];
  CLOUDS.forEach((c,i)=>{ const g=c.group||"Series"; if(!groups[g]){groups[g]=[];order.push(g);}
    groups[g].push({idx:CLOUD0+i,color:c.color,label:c.name+(c.param?(" · "+c.param):"")}); });
  order.forEach(g=>{
    const h=document.createElement("div"); h.className="tglsub"; h.textContent=g; host.appendChild(h);
    const row=document.createElement("div"); row.className="tglrow"; host.appendChild(row);
    groups[g].forEach(it=>{ const b=document.createElement("button"); b.className="tgl";
      b.innerHTML="<span class='sw' style='background:"+it.color+"'></span>"+it.label;
      b.onclick=function(){const off=b.classList.toggle("off"); Plotly.restyle("plot",{visible:off?false:true},[it.idx]);};
      row.appendChild(b); });
  });
  const h=document.createElement("div"); h.className="tglsub"; h.textContent="References ▲"; host.appendChild(h);
  const row=document.createElement("div"); row.className="tglrow"; host.appendChild(row);
  const b=document.createElement("button"); b.className="tgl";
  b.innerHTML="<span class='sw' style='background:"+RED+"'></span>A–D, U · Q1–Q4";
  b.onclick=function(){const off=b.classList.toggle("off"); Plotly.restyle("plot",{visible:off?false:true},[WIDX]);};
  row.appendChild(b);
}

// ---------- annotations per synthetic stage ----------
function ann(x,y,text,color,opts){ return Object.assign({x,y,text,xref:"x",yref:"y",showarrow:false,
  font:{size:12,color:color||INK,family:SERIF}, bgcolor:"rgba(255,255,255,0.85)", borderpad:2}, opts||{}); }
function annsFor(s){
  const a=[];
  if(s>=3) a.push(ann(0.80,0.80*0.80-2.0,"Pearson bound",INK,{xanchor:"left",yanchor:"top"}));
  if(s>=5) a.push(ann(0.74,0.74*0.74-UC,"bimodal frontier",MUTED,{xanchor:"left",yanchor:"bottom",font:{size:12,color:MUTED,family:SERIF}}));
  if(s>=5 && BP) a.push(ann(BP.g1,BP.g2-0.12,"two camps",RED,{xanchor:"center",yanchor:"top",font:{size:12,color:RED,family:SERIF}}));
  return a;
}

// ---------- synthetic guided stages ----------
const NARR = {
  0:"",
  1:"A plane for each alternative: <b>skewness γ₁</b> (x) and <b>excess kurtosis γ₂</b> (y) of its rank distribution.",
  2:"Each point is one alternative — coloured by the model that generated its profile.",
  3:"Nothing lies below the <b>Pearson bound</b> γ₂ = γ₁² − 2 (the two-atom limit).",
  4:"Four constructed shapes share <b>every</b> plurality entry up to degree 3 — yet skewness (level 4) and kurtosis (level 5) tell them apart.",
  5:"Below the dashed <b>bimodal frontier</b> the rank distribution splits into <b>two camps</b>.",
};
const STAGE_MSG = {
  0:"Each point is one alternative.<br>Click any point to see its rank distribution.",
  1:"The shape of an alternative's rank distribution<br>fixes its place in this plane.",
  2:"Below the dashed curve the distribution is<br><b>multimodal</b> — the voters split into camps.",
  3:"On the axis γ₁ = 0 the ranks are <b>symmetric</b>.",
  4:"<b>identical up to degree 3</b> — best → worst.",
};
let STAGE=-1;
function fadeTo(idx, to, dur){
  const gd=document.getElementById("plot");
  let from=gd.data[idx].opacity; if(from==null) from=1;
  if(Math.abs(from-to)<1e-3){ Plotly.restyle("plot",{opacity:to},[idx]); return; }
  let start=null;
  function step(ts){ if(start==null) start=ts; const t=Math.min(1,(ts-start)/dur); const e=t*t*(3-2*t);
    Plotly.restyle("plot",{opacity: from+(to-from)*e},[idx]); if(t<1) requestAnimationFrame(step); }
  requestAnimationFrame(step);
}
function staggerPoints(){ clearFamList();
  for(let i=0;i<NC;i++){ (function(k){ setTimeout(function(){ fadeTo(CLOUD0+k, 1, 360); addFam(k); }, k*220); })(i); } }
function setStage(s){
  s=Math.max(0,Math.min(5,s));
  Plotly.relayout("plot",{ "xaxis.visible":s>=1, "yaxis.visible":s>=1, annotations:annsFor(s) });
  setNarr(NARR[s]);
  fadeTo(0, s>=3?1:0, 500); fadeTo(1, s>=3?1:0, 500);
  fadeTo(2, s>=5?1:0, 500); fadeTo(3, s>=5?1:0, 500); fadeTo(4, s>=5?1:0, 500);
  fadeTo(WIDX, s>=4?1:0, 500);
  if(s>=2){ if(STAGE<2) staggerPoints(); else { for(let i=0;i<NC;i++) fadeTo(CLOUD0+i,1,300); } }
  else { for(let i=0;i<NC;i++) fadeTo(CLOUD0+i,0,300); clearFamList(); }
  if(s===4) drawWitnessGrid();
  else if(s===5 && BP) drawDist(BP.c.hist?BP.c.hist[BP.i]:gramCharlier(BP.g1,BP.g2,16), RED,
    BP.c.name+" · "+BP.c.param, "γ₁="+BP.g1.toFixed(2)+", γ₂="+BP.g2.toFixed(2)+"  ·  a bimodal alternative");
  else { Plotly.purge("side"); document.getElementById("side").innerHTML="";
    document.getElementById("sidecap").innerHTML = STAGE_MSG[s] || STAGE_MSG[0]; }
  STAGE=s;
}

// ---------- click -> distribution ----------
document.getElementById("plot").on("plotly_click", function(ev){
  const p=ev.points[0]; if(!p) return;
  if(p.curveNumber===WIDX) showWitness(WL[p.pointNumber]);
  else if(p.curveNumber>=CLOUD0) showCloudPoint(CLOUDS[p.curveNumber-CLOUD0], p.pointNumber);
});

// ---------- wire ----------
window.addEventListener("message", function(e){ if(e.data && typeof e.data.stage==="number") setStage(e.data.stage); });
document.getElementById("famlist").style.display = (MODE==='explain') ? "" : "none";
document.getElementById("tgllabel").style.display = (MODE==='play') ? "" : "none";
document.getElementById("toggles").style.display = (MODE==='play') ? "" : "none";

if (MODE==='explain') { const st=params.get('stage'); setStage(st?(+st):0); }
else if (MODE==='realguided') {
  Plotly.restyle("plot", {opacity:1}, [1,2,3]);   // Pearson + frontier + multimodal fill
  setNarr("On real elections, candidates spread across the <b>whole</b> plane — the four picks below show the range of shapes.");
  drawWitnessGrid();
  document.getElementById("sidecap").innerHTML =
    "Q1–Q4 reference candidates (best → worst).<br><span class='sub'>Le Pen (Q3) &amp; Mélenchon (Q4) are skewed/polarised. Only complete-ranking voters.</span>";
} else { // play (combined interactive)
  Plotly.restyle("plot", {opacity:1}, [0,1,2,3]);
  setNarr("Toggle synthetic models &amp; real elections below; click any point — cloud or ▲ reference — for its rank distribution.");
  document.getElementById("sidecap").innerHTML="Click any point for its rank distribution.";
  makeToggles();
}
"""

HTML = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Moment plane</title>
<link rel="icon" href="data:,">
<script src="__PLOTLY__" charset="utf-8"></script>
<style>
  html,body{margin:0;padding:0;height:100%;background:#fff;
    font-family:"Palatino Linotype","Book Antiqua",Palatino,Georgia,serif;color:#111;}
  #narr{height:42px;min-height:42px;line-height:42px;padding:0 18px;
    font-size:18px;color:#111;border-bottom:1px solid #ededed;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  #narr b{color:#9a1b1b;font-weight:700;}
  #wrap{display:flex;height:calc(100% - 43px);width:100%;}
  #leftcol{flex:1 1 auto;display:flex;flex-direction:column;min-width:0;}
  #plot{flex:1 1 auto;min-height:0;}
  #famlist{min-height:40px;display:flex;flex-wrap:wrap;gap:3px 16px;align-items:center;
    padding:5px 14px;font-size:12.5px;color:#333;}
  #famlist .famitem{display:inline-flex;align-items:center;white-space:nowrap;}
  #famlist .sw{width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:5px;}
  #sidewrap{flex:0 0 320px;display:flex;flex-direction:column;overflow-y:auto;
    border-left:1px solid #e4e4e4;padding:12px 12px 8px;box-sizing:border-box;}
  #sidettl{font-size:12.5px;letter-spacing:.12em;text-transform:uppercase;color:#9a1b1b;margin-bottom:6px;}
  #side{width:100%;height:240px;min-height:240px;}
  #sidecap{font-size:14px;line-height:1.45;color:#333;margin-top:6px;}
  #sidecap .sub{font-size:13px;color:#6b6b6b;}
  #tgllabel{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:#9a1b1b;
    margin:14px 0 7px;border-top:1px solid #ededed;padding-top:11px;}
  #toggles .tglsub{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:#6b6b6b;margin:8px 0 5px;}
  #toggles .tglrow{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:4px;}
  #toggles .tgl{font-family:inherit;font-size:12px;display:inline-flex;align-items:center;gap:6px;
    padding:3px 10px;border:1px solid #ccc;border-radius:14px;background:#fff;color:#222;cursor:pointer;}
  #toggles .tgl .sw{width:9px;height:9px;border-radius:50%;display:inline-block;}
  #toggles .tgl.off{opacity:0.45;text-decoration:line-through;background:#f4f4f4;}
</style></head>
<body>
<div id="narr"></div>
<div id="wrap">
  <div id="leftcol">
    <div id="plot"></div>
    <div id="famlist"></div>
  </div>
  <div id="sidewrap">
    <div id="sidettl">Rank distribution&nbsp;·&nbsp;best → worst</div>
    <div id="side"></div>
    <div id="sidecap"></div>
    <div id="tgllabel">show / hide series</div>
    <div id="toggles"></div>
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
open(os.path.join(HERE, "moment_plane.html"), "w").write(out)
print("wrote moment_plane.html  (%.1f KB)" % (len(out)/1024))
# the standalone real widget is no longer used (real data is folded into moment_plane.html)
old = os.path.join(HERE, "moment_plane_real.html")
if os.path.exists(old):
    os.remove(old); print("removed obsolete moment_plane_real.html")
