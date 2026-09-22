(async function () {
  "use strict";
  // Preserve the source data, curve coordinates, degree colors, and protocol symbols.
  const status = document.getElementById("status");
  try {
    const response = await fetch("../elicitation-collective-disagreement/interactive_data/data/pareto.json");
    if (!response.ok) throw new Error("Source data unavailable");
    const data = await response.json();
    const levels = data.meta.ells, colors = data.meta.ell_color;
    const serif = '"Palatino Linotype",Palatino,Georgia,serif';
    const traces = levels.map(level => ({
      x:data.frontier.N[level].x, y:data.frontier.N[level].y, mode:"lines", type:"scatter",
      line:{color:colors[level],width:2,dash:"dot"},opacity:.35,hoverinfo:"skip",showlegend:false
    }));
    levels.forEach(level => {
      const points = data.points.filter(p => p.ell === level).sort((a,b) => a.mcl-b.mcl);
      traces.push({x:points.map(p=>p.mcl),y:points.map(p=>p.N),mode:"markers",type:"scatter",name:"ℓ="+level,
        marker:{color:colors[level],size:10,symbol:points.map(p=>p.kind==="chain"?"circle":"square-open"),line:{color:colors[level],width:2}},
        customdata:points.map(p=>[p.ell,p.k,p.kind,p.mcl,p.N]),
        hovertemplate:"<b>ℓ=%{customdata[0]}</b> · %{customdata[1]}-%{customdata[2]}<br>Comparisons=%{customdata[3]} · People=%{customdata[4]:,}<extra></extra>"});
    });
    const highlight = traces.length;
    traces.push({x:[],y:[],mode:"markers",type:"scatter",marker:{symbol:"circle-open",color:"#111",size:25,line:{width:2}},hoverinfo:"skip",showlegend:false});
    // Retain fractional positions for both handles; round only the selected protocol.
    let level = 3, index = 2, selectedKey = "";
    const ns = document.getElementById("people-slider"), ls = document.getElementById("load-slider");
    const fmt = n => n.toLocaleString("en-US");
    document.getElementById("controls").hidden = false;
    status.hidden = true;
    await Plotly.newPlot("plot",traces,{
      margin:{l:67,r:10,t:28,b:43},
      xaxis:{title:{text:"Comparisons per person λ",font:{size:13,family:serif}},range:[0,20],dtick:2,gridcolor:"#eee",zeroline:false,tickfont:{family:serif,size:11}},
      yaxis:{title:{text:"People N",font:{size:13,family:serif}},type:"log",range:[2.8,5.45],gridcolor:"#eee",tickfont:{family:serif,size:11}},
      legend:{orientation:"h",x:.5,y:1.02,xanchor:"center",yanchor:"bottom",font:{size:12,family:serif}},
      hovermode:"closest",paper_bgcolor:"white",plot_bgcolor:"white",shapes:[]
    },{responsive:true,displayModeBar:false,displaylogo:false});
    function sync() {
      const rows = TradeoffModel.frontier(data.points,level);
      index = Math.max(0,Math.min(rows.length-1,index));
      const selected = TradeoffModel.pick(data.points,level,index);
      ns.max = ls.max = String(rows.length-1);
      ns.value = String(rows.length-1-index); ls.value = String(index);
      const nextKey = level + ":" + Math.round(index);
      if (nextKey === selectedKey) return;
      selectedKey = nextKey;
      ns.setAttribute("aria-valuetext",fmt(selected.N)+" people");
      ls.setAttribute("aria-valuetext",selected.mcl+" comparisons per person");
      document.getElementById("people-value").textContent = fmt(selected.N);
      document.getElementById("load-value").textContent = selected.mcl;
      document.getElementById("protocol").innerHTML = 'Use a <strong>'+selected.k+'-'+selected.kind+'</strong> · level '+level+' · '+fmt(selected.N)+' people';
      document.querySelectorAll("[data-level]").forEach(b=>b.setAttribute("aria-pressed",String(Number(b.dataset.level)===level)));
      Plotly.restyle("plot",{x:[[selected.mcl]],y:[[selected.N]]},[highlight]);
      Plotly.relayout("plot",{shapes:[
        {type:"line",x0:0,x1:selected.mcl,y0:selected.N,y1:selected.N,line:{color:"#9a1b1b",width:1,dash:"dash"}},
        {type:"line",x0:selected.mcl,x1:selected.mcl,y0:10**2.8,y1:selected.N,line:{color:"#9a1b1b",width:1,dash:"dash"}}
      ]});
    }
    ns.addEventListener("input",()=>{index=TradeoffModel.frontier(data.points,level).length-1-Number(ns.value);sync();});
    ls.addEventListener("input",()=>{index=Number(ls.value);sync();});
    document.querySelectorAll("[data-level]").forEach(button=>button.addEventListener("click",()=>{
      const oldLoad = TradeoffModel.pick(data.points,level,index).mcl;
      level = Number(button.dataset.level);
      const rows = TradeoffModel.frontier(data.points,level);
      index = rows.reduce((best,p,i)=>Math.abs(p.mcl-oldLoad)<Math.abs(rows[best].mcl-oldLoad)?i:best,0);
      sync();
    }));
    document.getElementById("plot").on("plotly_click",event=>{
      const point=event.points[0]?.customdata;
      if(!point)return;
      level=point[0];index=TradeoffModel.frontier(data.points,level).findIndex(p=>p.k===point[1]&&p.kind===point[2]);sync();
    });
    sync();
    new ResizeObserver(()=>Plotly.Plots.resize("plot")).observe(document.getElementById("plot"));
  } catch (error) {
    status.hidden=false; status.textContent="The original frontier could not load. Please reload this card.";
    console.error(error);
  }
})();
