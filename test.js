
const USER_NODE_INIT="{{user_node}}";
const POLL_MS=4000;
const CROWD_MULT={Low:1,Medium:4,High:30};
const LEVEL_THRESH={low:20,med:55};

let GLOBAL_HAZARDS = {};
  let SMOKE_LEVEL = "none";
  let lastBroadcastId = null;
let GRAPH=null,crowdData={},roomData={},currentUser=USER_NODE_INIT,bestExit=null,animT=0;

function countToLevel(n){return n<=LEVEL_THRESH.low?"Low":n<=LEVEL_THRESH.med?"Medium":"High";}

/* DIJKSTRA */
// Get effective crowd count for any node (exit crowd OR room occupancy)
function getNodeCount(n){
  if(crowdData[n]!==undefined) return crowdData[n]?.count||0;
  if(roomData[n]!==undefined)  return roomData[n]||0;
  return 0;
}
function buildAdj(){
  const adj={};
  Object.keys(GRAPH.nodes).forEach(n=>adj[n]=[]);
  GRAPH.edges.forEach(([u,v,d])=>{
      let mult_u = CROWD_MULT[countToLevel(getNodeCount(u))] || 1;
      let mult_v = CROWD_MULT[countToLevel(getNodeCount(v))] || 1;
      
      if (GLOBAL_HAZARDS[u] || GLOBAL_HAZARDS[v]) {
          mult_u = 999999;
          mult_v = 999999;
      }
      
      adj[u].push([v,d*mult_v]);
      adj[v].push([u,d*mult_u]);
    });
  return adj;
}
function dijkstra(start,adj){
  const dist={},prev={};
  Object.keys(adj).forEach(n=>{dist[n]=Infinity;prev[n]=null;});
  dist[start]=0;
  const q=[[0,start]];
  while(q.length){
    q.sort((a,b)=>a[0]-b[0]);
    const[c,u]=q.shift();
    if(c>dist[u])continue;
    for(const[v,w]of adj[u]){const nc=c+w;if(nc<dist[v]){dist[v]=nc;prev[v]=u;q.push([nc,v]);}}
  }
  return{dist,prev};
}
function getPath(prev,s,t){const p=[];let n=t;while(n){p.push(n);n=prev[n];}p.reverse();return p[0]===s?p:[];}

/* CANVAS */
const canvas=document.getElementById("floorMap");
const ctx=canvas.getContext("2d");
let DW=880,DH=580;
let sx=1,sy=1;
const X=x=>x*sx,Y=y=>y*sy,R=r=>r*Math.min(sx,sy);

/* Room rectangles for floor-plan style drawing */
const ROOM_RECTS={
  Classroom_A:  {x: 140, y: 40, w: 120, h: 80, icon: "\uD83C\uDF93"},
  Classroom_B:  {x: 380, y: 40, w: 160, h: 80, icon: "\uD83D\uDCDA"},
  AI_Lab:       {x: 540, y: 120, w: 120, h: 80, icon: "\uD83D\uDCBB"},
  HOD_Cabin:    {x: 140, y: 440, w: 120, h: 80, icon: "\uD83D\uDCBC"},
  Staff_Lounge: {x: 380, y: 240, w: 160, h: 80, icon: "\u2615"},
  Server_Room:  {x: 660, y: 440, w: 160, h: 80, icon: "\uD83D\uDDA5"},
  Library:      {x: 140, y: 240, w: 120, h: 80, icon: "\uD83D\uDCD6"}
};
const CORRIDORS=[
  {x: 80, y: 60, w: 40, h: 440}, // West V
  {x: 80, y: 260, w: 740, h: 40}, // Main H
  {x: 300, y: 60, w: 40, h: 240}, // Mid1 V (North to Mid1)
  {x: 580, y: 260, w: 40, h: 240}, // Mid2 V (Mid2 to South)
  {x: 580, y: 140, w: 40, h: 120} // Connect AI lab
];
/* Node centers mapped onto floor plan */
const NODE_POS={
  Intersection_West: [100, 280],
  Intersection_Mid1: [320, 280],
  Intersection_Mid2: [600, 280],
  Corridor_North: [320, 80],
  Corridor_South: [600, 480],
  Corridor_West_N: [100, 80],
  Corridor_West_S: [100, 480],
  Corridor_East: [780, 280],
  Classroom_A: [200, 80],
  Classroom_B: [460, 80],
  AI_Lab: [600, 160],
  HOD_Cabin: [200, 480],
  Staff_Lounge: [460, 280],
  Server_Room: [740, 480],
  Library: [200, 280],
  Main_Staircase: [100, 30],
  East_Fire_Exit: [850, 280],
  South_Emergency_Stairs: [600, 540]
};

function resizeCanvas(){
  const wrap = canvas.parentElement;
  const dpr = window.devicePixelRatio || 1;
  // Physical pixels = CSS pixels × DPR
  canvas.width  = Math.round(wrap.clientWidth  * dpr);
  canvas.height = Math.round(wrap.clientHeight * dpr);
  // Scale drawing so all coordinates stay in CSS-pixel space
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  sx = wrap.clientWidth  / DW;
  sy = wrap.clientHeight / DH;
}

function drawRoundRect(x,y,w,h,r,fill,stroke,lw){
  ctx.beginPath();
  ctx.roundRect(x,y,w,h,r);
  if(fill){ctx.fillStyle=fill;ctx.fill();}
  if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=lw||1;ctx.stroke();}
}

function render() {
  if(!ctx) return;
  const cw = canvas.width  / (window.devicePixelRatio||1);
  const ch = canvas.height / (window.devicePixelRatio||1);
  ctx.clearRect(0,0,cw,ch);
  
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  ctx.fillStyle = isDark ? "#1A1A1A" : "#E8EAED";
  ctx.fillRect(0,0,cw,ch);
  
  if(!GRAPH) return;

  /* === DIJKSTRA === */
  const adj = buildAdj();
  const {dist, prev} = dijkstra(currentUser, adj);
  let bExit = null, bCost = Infinity;
  GRAPH.exit_nodes.forEach(e => { if(dist[e]<bCost){bCost=dist[e];bExit=e;} });
  bestExit = bExit;
  const path = bExit ? getPath(prev, currentUser, bExit) : [];

  /* === CORRIDORS === */
  ctx.fillStyle = isDark ? "#2D2D2D" : "#FFFFFF";
  CORRIDORS.forEach(c => {
    ctx.fillRect(X(c.x), Y(c.y), X(c.w), Y(c.h));
  });

  /* === ROOMS === */
  Object.entries(ROOM_RECTS).forEach(([name, r]) => {
    const onPath = path.includes(name);
    const isUser = name === currentUser;
    
    ctx.beginPath();
    ctx.rect(X(r.x), Y(r.y), X(r.w), Y(r.h));
    
    ctx.fillStyle = isUser ? (isDark?"#3b1414":"#FCE8E6") : onPath ? (isDark?"#122a4f":"#E8F0FE") : (isDark?"#242424":"#F1F3F4");
    ctx.fill();
    ctx.strokeStyle = isUser ? (isDark?"#F28B82":"#EA4335") : onPath ? (isDark?"#8AB4F8":"#1A73E8") : (isDark?"#333333":"#DADCE0");
    ctx.lineWidth = R(2);
    ctx.stroke();
    
    const cx = X(r.x + r.w/2), cy = Y(r.y + r.h/2);
    ctx.font = `500 ${Math.max(R(12), 10)}px 'Roboto', sans-serif`;
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillStyle = isUser ? (isDark?"#F28B82":"#C5221F") : onPath ? (isDark?"#8AB4F8":"#174EA6") : (isDark?"#9AA0A6":"#5F6368");
    
    const labelTxt = r.label || name.replace(/_/g," ");
    if(r.icon) {
      ctx.font = `${Math.max(R(16), 14)}px sans-serif`;
      ctx.fillText(r.icon, cx, cy - Math.max(R(8), 6));
      ctx.font = `500 ${Math.max(R(11), 9)}px 'Roboto', sans-serif`;
      ctx.fillText(labelTxt, cx, cy + Math.max(R(8), 6));
    } else {
      ctx.fillText(labelTxt, cx, cy);
    }
  });

  /* === PATHS === */
  let walkedUpToIdx = 0;
  if (PDR.active && path.length > 0) {
    let minD = Infinity;
    path.forEach((name, i) => {
      const pos = NODE_POS[name] || GRAPH.nodes[name];
      if (!pos) return;
      const d = Math.hypot(PDR.pos.x - pos[0], PDR.pos.y - pos[1]);
      if (d < minD) { minD = d; walkedUpToIdx = i; }
    });
  }

  if(path.length > 1) {
    ctx.beginPath();
    for(let i=walkedUpToIdx; i<path.length; i++){
      const p = NODE_POS[path[i]] || GRAPH.nodes[path[i]];
      if(!p) continue;
      if(i === walkedUpToIdx) {
        const startX = PDR.active ? PDR.pos.x : p[0];
        const startY = PDR.active ? PDR.pos.y : p[1];
        ctx.moveTo(X(startX), Y(startY));
      }
      else ctx.lineTo(X(p[0]), Y(p[1]));
    }
    ctx.strokeStyle = (isDark?"#8AB4F8":"#1A73E8");
    ctx.lineWidth = R(8);
    ctx.lineCap = "round"; ctx.lineJoin = "round";
    ctx.stroke();

    if(walkedUpToIdx > 0) {
      ctx.beginPath();
      for(let i=0; i<=walkedUpToIdx; i++){
        const p = NODE_POS[path[i]] || GRAPH.nodes[path[i]];
        if(!p) continue;
        if(i === 0) ctx.moveTo(X(p[0]), Y(p[1]));
        else ctx.lineTo(X(p[0]), Y(p[1]));
      }
      if(PDR.active) ctx.lineTo(X(PDR.pos.x), Y(PDR.pos.y));
      ctx.strokeStyle = "#BDC1C6";
      ctx.lineWidth = R(8);
      ctx.lineCap = "round"; ctx.lineJoin = "round";
      ctx.stroke();
    }
  }

  /* === EXIT NODES === */
  GRAPH.exit_nodes.forEach(name => {
    const pos = NODE_POS[name] || GRAPH.nodes[name];
    if(!pos) return;
    const isBest = name === bestExit;
    const clr = isBest ? (isDark?"#81C995":"#1E8E3E") : (isDark?"#F28B82":"#EA4335");
    ctx.beginPath();
    ctx.arc(X(pos[0]), Y(pos[1]), R(isBest?12:10), 0, Math.PI*2);
    ctx.fillStyle = clr; ctx.fill();
    ctx.strokeStyle = isDark?"#121212":"#FFFFFF"; ctx.lineWidth = R(3); ctx.stroke();
    if(isBest) {
      ctx.font = `bold ${Math.max(R(12), 10)}px sans-serif`;
      ctx.fillStyle = isDark?"#121212":"#FFFFFF"; ctx.textAlign="center"; ctx.textBaseline="middle";
      ctx.fillText("★", X(pos[0]), Y(pos[1]));
    }
  });

  
    
    /* === HAZARDS === */
    Object.keys(GLOBAL_HAZARDS).forEach(name => {
      const pos = NODE_POS[name] || (GRAPH ? GRAPH.nodes[name] : null);
      if (!pos) return;
      const type = GLOBAL_HAZARDS[name];
      const cx = X(pos[0]), cy = Y(pos[1]);
      const t = Date.now();

      if (type === 'fire') {
        // === FIRE: layered radial glow + rising flame particles ===
        // 1. Wide outer heat glow
        const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, R(38));
        grad.addColorStop(0, `rgba(255,80,0,${0.35 + 0.1*Math.sin(t/120)})`);
        grad.addColorStop(0.5, `rgba(239,68,68,${0.18 + 0.07*Math.sin(t/180)})`);
        grad.addColorStop(1, 'rgba(239,68,68,0)');
        ctx.beginPath();
        ctx.arc(cx, cy, R(38), 0, Math.PI*2);
        ctx.fillStyle = grad;
        ctx.fill();

        // 2. Rising flame particles (30 particles, 3 layers)
        for (let i = 0; i < 30; i++) {
          const speed   = 400 + (i % 5) * 90;
          const phase   = (t / speed + i * 0.37) % 1.0;
          const life    = Math.pow(1.0 - phase, 1.4); // fade as they rise
          const yOff    = -phase * R(36);
          const xOff    = Math.sin(t / 300 + i * 1.7) * R(10) * (1 - phase * 0.4);
          const rad     = (R(11) + (i % 4) * R(2)) * life;

          let color;
          if (i % 4 === 0)      color = `rgba(255,240,80,${life})`;        // bright yellow core
          else if (i % 4 === 1) color = `rgba(255,160,20,${life * 0.95})`; // orange
          else if (i % 4 === 2) color = `rgba(239,68,68,${life * 0.85})`;  // red
          else                  color = `rgba(120,20,0,${life * 0.5})`;    // dark smoke edge

          ctx.beginPath();
          ctx.arc(cx + xOff, cy + yOff, Math.max(rad, 1), 0, Math.PI*2);
          ctx.fillStyle = color;
          ctx.fill();
        }

        // 3. Small dark smoke puffs rising above flames
        for (let i = 0; i < 8; i++) {
          const phase  = (t / 1200 + i * 0.125) % 1.0;
          const yOff   = -(R(30) + phase * R(20));
          const xOff   = Math.sin(t / 600 + i * 0.8) * R(8);
          const alpha  = Math.pow(1 - phase, 2) * 0.35;
          ctx.beginPath();
          ctx.arc(cx + xOff, cy + yOff, R(8), 0, Math.PI*2);
          ctx.fillStyle = `rgba(30,30,30,${alpha})`;
          ctx.fill();
        }

      } else if (type === 'debris') {
        // === DEBRIS: dust cloud + polygonal rocks + hazard tape ===
        // 1. Pulsing dust cloud (elliptical)
        const dustGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, R(30));
        dustGrad.addColorStop(0, `rgba(120,110,90,${0.55 + 0.1*Math.sin(t/220)})`);
        dustGrad.addColorStop(0.6, `rgba(100,90,75,0.3)`);
        dustGrad.addColorStop(1, 'rgba(80,70,60,0)');
        ctx.save();
        ctx.scale(1, 0.65);
        ctx.beginPath();
        ctx.arc(cx, cy / 0.65, R(30), 0, Math.PI*2);
        ctx.fillStyle = dustGrad;
        ctx.fill();
        ctx.restore();

        // 2. Dust particles drifting outward
        for (let i = 0; i < 10; i++) {
          const phase  = (t / 1800 + i * 0.1) % 1.0;
          const ang    = (i / 10) * Math.PI * 2;
          const drift  = phase * R(22);
          const alpha  = (1 - phase) * 0.4;
          ctx.beginPath();
          ctx.arc(cx + Math.cos(ang) * drift, cy + Math.sin(ang) * drift * 0.6, R(5), 0, Math.PI*2);
          ctx.fillStyle = `rgba(160,150,130,${alpha})`;
          ctx.fill();
        }

        // 3. Jagged rocks (5 polygons, pseudo-random placement via seed)
        const seed = pos[0] * 3.7 + pos[1] * 5.3;
        const rocks = [
          { dx: -R(12), dy: -R(6),  s: R(8)  },
          { dx:  R(8),  dy: -R(10), s: R(6)  },
          { dx:  R(14), dy:  R(4),  s: R(7)  },
          { dx: -R(4),  dy:  R(10), s: R(9)  },
          { dx:  R(2),  dy: -R(2),  s: R(5)  },
        ];
        rocks.forEach((r, i) => {
          const pts = 5 + (i % 2);
          ctx.beginPath();
          for (let p = 0; p < pts; p++) {
            const a = (p / pts) * Math.PI * 2 + seed * 0.1 * i;
            const jitter = 0.7 + ((seed * (p + i) * 11.3) % 0.6);
            const px = cx + r.dx + Math.cos(a) * r.s * jitter;
            const py = cy + r.dy + Math.sin(a) * r.s * jitter * 0.8;
            p === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
          }
          ctx.closePath();
          const shade = 60 + (i * 15);
          ctx.fillStyle = `rgb(${shade},${shade-5},${shade-10})`;
          ctx.fill();
          ctx.strokeStyle = '#1e293b';
          ctx.lineWidth = R(1);
          ctx.stroke();
        });

        // 4. Hazard tape (black + amber dashes)
        ctx.save();
        ctx.lineCap = 'round';
        ctx.lineWidth = R(6);
        ctx.beginPath();
        ctx.moveTo(cx - R(20), cy + R(8));
        ctx.lineTo(cx + R(20), cy - R(8));
        ctx.strokeStyle = '#F59E0B';
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(cx - R(20), cy + R(8));
        ctx.lineTo(cx + R(20), cy - R(8));
        ctx.setLineDash([R(6), R(6)]);
        ctx.strokeStyle = '#000000';
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.restore();
      }
    });

    /* === SOS BEACONS === */
        /* === SOS BEACONS === */
    SOS_BEACON_NODES.forEach(nodeName => {
      const pos = NODE_POS[nodeName] || (GRAPH ? GRAPH.nodes[nodeName] : null);
      if (!pos) return;
      const cx = X(pos[0]), cy = Y(pos[1]);
      const t = Date.now();

      // Animated radar rings
      for (let ring = 0; ring < 3; ring++) {
        const phase = ((t / 800) + ring * 0.33) % 1;
        const ringR = R(8) + phase * R(28);
        const alpha = (1 - phase) * 0.7;
        ctx.beginPath();
        ctx.arc(cx, cy, ringR, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(239, 68, 68, ${alpha})`;
        ctx.lineWidth = R(2.5);
        ctx.stroke();
      }

      // Solid red center dot
      ctx.beginPath();
      ctx.arc(cx, cy, R(9), 0, Math.PI * 2);
      ctx.fillStyle = '#ef4444';
      ctx.shadowColor = '#ef4444';
      ctx.shadowBlur = R(15);
      ctx.fill();
      ctx.shadowBlur = 0;

      // SOS label
      ctx.font = `bold ${Math.max(R(8), 9)}px Inter`;
      ctx.fillStyle = '#ffffff';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('SOS', cx, cy);
    });


    /* === SMOKE OVERLAY === */
    if (SMOKE_LEVEL && SMOKE_LEVEL !== "none") {
      const cw = canvas.width  / (window.devicePixelRatio||1);
      const ch = canvas.height / (window.devicePixelRatio||1);
      const t  = Date.now();

      // Background fog layer
      let fogAlpha = SMOKE_LEVEL === "light" ? 0.25 : SMOKE_LEVEL === "heavy" ? 0.60 : 0.88;
      ctx.fillStyle = `rgba(60,60,60,${fogAlpha})`;
      ctx.fillRect(0, 0, cw, ch);

      // Animated drifting smoke puffs
      const puffCount = SMOKE_LEVEL === "light" ? 14 : SMOKE_LEVEL === "heavy" ? 24 : 10;
      for (let i = 0; i < puffCount; i++) {
        const seedX = (i * 137.5) % 1.0;
        const seedY = (i * 97.3)  % 1.0;
        const phase = (t / (3000 + i * 200) + i * 0.07) % 1.0;
        const px = (seedX * cw + Math.sin(t/2000 + i) * cw * 0.08 + phase * cw * 0.12) % cw;
        const py = (seedY * ch + Math.cos(t/2500 + i * 0.7) * ch * 0.06) % ch;
        const rad = (cw * 0.06) + (i % 4) * (cw * 0.02);
        const alpha = (SMOKE_LEVEL === "blackout" ? 0.15 : 0.22) + 0.06 * Math.sin(t/800 + i);

        const grad = ctx.createRadialGradient(px, py, 0, px, py, rad);
        grad.addColorStop(0, `rgba(80,80,80,${alpha})`);
        grad.addColorStop(1, 'rgba(60,60,60,0)');
        ctx.beginPath();
        ctx.arc(px, py, rad, 0, Math.PI*2);
        ctx.fillStyle = grad;
        ctx.fill();
      }

      // === BLACKOUT MODE: make the escape path GLOW ===
      if (SMOKE_LEVEL === "blackout") {
        // Re-draw the path on top with a neon glow effect
        ctx.save();
        ctx.shadowColor = '#22c55e';
        ctx.shadowBlur  = R(20);
        ctx.strokeStyle = '#4ade80';
        ctx.lineWidth   = R(6);
        ctx.lineCap     = 'round';
        ctx.lineJoin    = 'round';
        ctx.beginPath();
        let started = false;
        for (let i = 0; i < path.length - 1; i++) {
          const p1 = NODE_POS[path[i]]   || (GRAPH ? GRAPH.nodes[path[i]]   : null);
          const p2 = NODE_POS[path[i+1]] || (GRAPH ? GRAPH.nodes[path[i+1]] : null);
          if (!p1 || !p2) continue;
          if (!started) { ctx.moveTo(X(p1[0]), Y(p1[1])); started = true; }
          ctx.lineTo(X(p2[0]), Y(p2[1]));
        }
        ctx.stroke();

        // Second glow pass (wider, dimmer)
        ctx.lineWidth = R(14);
        ctx.strokeStyle = 'rgba(34,197,94,0.25)';
        ctx.shadowBlur = R(30);
        ctx.beginPath();
        started = false;
        for (let i = 0; i < path.length - 1; i++) {
          const p1 = NODE_POS[path[i]]   || (GRAPH ? GRAPH.nodes[path[i]]   : null);
          const p2 = NODE_POS[path[i+1]] || (GRAPH ? GRAPH.nodes[path[i+1]] : null);
          if (!p1 || !p2) continue;
          if (!started) { ctx.moveTo(X(p1[0]), Y(p1[1])); started = true; }
          ctx.lineTo(X(p2[0]), Y(p2[1]));
        }
        ctx.stroke();
        ctx.shadowBlur = 0;
        ctx.restore();
      }
    }

    /* === ROOM TEXTS === */
    Object.entries(ROOM_RECTS).forEach(([name, r]) => {
      const onPath = path.includes(name);
      const isUser = name === currentUser;
      const cx = X(r.x + r.w/2), cy = Y(r.y + r.h/2);
      ctx.font = `500 ${Math.max(R(12), 10)}px 'Roboto', sans-serif`;
      ctx.textAlign = "center"; ctx.textBaseline = "middle";
      ctx.fillStyle = isUser ? (isDark?"#F28B82":"#C5221F") : onPath ? (isDark?"#8AB4F8":"#174EA6") : (isDark?"#9AA0A6":"#5F6368");
      
      const labelTxt = r.label || name.replace(/_/g," ");
      if(r.icon) {
        ctx.font = `${Math.max(R(16), 14)}px sans-serif`;
        ctx.fillText(r.icon, cx, cy - Math.max(R(8), 6));
        ctx.font = `500 ${Math.max(R(11), 9)}px 'Roboto', sans-serif`;
        ctx.fillText(labelTxt, cx, cy + Math.max(R(8), 6));
      } else {
        ctx.fillText(labelTxt, cx, cy);
      }
    });

    /* === USER PIN === */
  let xr, yr;
  if (PDR.active) { xr = PDR.pos.x; yr = PDR.pos.y; }
  else {
    const upos = NODE_POS[currentUser] || GRAPH.nodes[currentUser];
    if (upos) { xr = upos[0]; yr = upos[1]; } else { xr = null; }
  }
  if(xr !== null && xr !== undefined) {
    const ux = X(xr), uy = Y(yr);
    const pulse = 1 + 0.4 * Math.sin(Date.now()/300);
    ctx.beginPath();
    ctx.arc(ux, uy, R(14) * pulse, 0, Math.PI*2);
    ctx.fillStyle = (isDark?"rgba(138,180,248,0.3)":"rgba(66, 133, 244, 0.3)");
    ctx.fill();
      if (typeof drawHeadingArrow === "function") drawHeadingArrow(ctx, ux, uy, R, false);
    
    ctx.beginPath();
    ctx.arc(ux, uy, R(8), 0, Math.PI*2);
    ctx.fillStyle = (isDark?"#8AB4F8":"#4285F4"); ctx.fill();
    ctx.strokeStyle = isDark?"#121212":"#FFFFFF"; ctx.lineWidth = R(3); ctx.stroke();
  }

  updateSidebar(bestExit, bCost, path);
  if(window.requestAnimationFrame) requestAnimationFrame(render);
}

function updateSidebar(best,cost,path){
  document.getElementById("userLbl").textContent=currentUser.replace(/_/g," ");
  document.getElementById("bestName").textContent=best?best.replace(/_/g," "):"None";
  document.getElementById("pathTxt").textContent=path.length?
    "Path: "+path.map(n=>n.replace(/_/g," ")).join(" \u2192 "):"No path found";
  const ib=document.getElementById("infoBar");
  if(best){
    const lvl=crowdData[best]?.level||"Low";
    ib.innerHTML=`&#10003; <strong style="color:#d8b4fe">★ Safest Exit:</strong> <span style="color:#d8b4fe">${best.replace(/_/g," ")}</span> &nbsp;|&nbsp; Crowd: <strong>${lvl}</strong> &nbsp;|&nbsp; Score: <strong>${cost.toFixed(0)}</strong>`;
    ib.className="info-bar";
  }else{
    ib.textContent="No reachable exit found!";ib.className="info-bar warn";
  }
  /* update exit pills */
  document.querySelectorAll(".exit-row").forEach(el=>{
    const n=el.dataset.exit;
    const lvl=crowdData[n]?.level||"Low";
    const pill=el.querySelector(".cpill");
    if(pill){pill.textContent=lvl;pill.className="cpill "+lvl;}
    el.className="exit-row"+(n===best?" best":"");
  });
}

function buildExitList(){
  const el=document.getElementById("exitList");
  el.innerHTML="";
  (GRAPH.exit_nodes||[]).forEach(name=>{
    const row=document.createElement("div");
    row.className="exit-row";row.dataset.exit=name;
    row.innerHTML=`<span class="exit-row-name">${name.replace(/_/g," ")}</span><span class="cpill Low">Low</span>`;
    el.appendChild(row);
  });
}

function buildLocSelect(){
  const sel=document.getElementById("locSelect");
  const nodes=Object.keys(GRAPH.nodes);
  nodes.forEach(n=>{
    const o=document.createElement("option");
    o.value=n;o.textContent=n.replace(/_/g," ");
    if(n===currentUser)o.selected=true;
    sel.appendChild(o);
  });
}

function changeLocation(node){
  if(!node)return;
  currentUser=node;
  document.getElementById("userLbl").textContent=node.replace(/_/g," ");
}


function drawHeadingArrow(ctx, x, y, R_func, isDemo) {
  let dx = 0, dy = 0;
  if (isDemo && typeof NAV !== 'undefined' && NAV.demoRunning && NAV.steps && NAV.steps.length > 0) {
    const step = NAV.steps[NAV.currentStep] || NAV.steps[NAV.steps.length - 1];
    if (step && step.toPos && step.fromPos) {
      dx = step.toPos[0] - step.fromPos[0];
      dy = step.toPos[1] - step.fromPos[1];
    }
  } else if (typeof PDR !== 'undefined' && PDR.sensorsEnabled) {
    // Show arrow anytime sensors are enabled (so they can calibrate)
    const mapHeading = ((PDR.heading - PDR.northOffset) + 360) % 360;
    const rad = mapHeading * Math.PI / 180;
    dx = Math.sin(rad);
    dy = -Math.cos(rad);
  }
  
  if (dx === 0 && dy === 0) return;
  const angle = Math.atan2(dy, dx);
  
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  ctx.beginPath();
  ctx.moveTo(Math.max(R_func(24), 20), 0); // Tip
  ctx.lineTo(Math.max(R_func(10), 8), -Math.max(R_func(8), 6));
  ctx.lineTo(Math.max(R_func(10), 8), Math.max(R_func(8), 6));
  ctx.closePath();
  
  ctx.fillStyle = "#FFFFFF"; // Solid highly visible white pointer
  ctx.shadowColor = "rgba(0,0,0,0.5)"; ctx.shadowBlur = 4;
  ctx.fill(); ctx.shadowBlur = 0;
  ctx.restore();
}

async function init(){
  try{
    const r=await fetch("/api/graph");
    if(!r.ok) throw new Error("HTTP "+r.status);
    GRAPH=await r.json();
    buildExitList();
    buildLocSelect();
    await pollCrowd();
    setInterval(pollCrowd,POLL_MS);
    resizeCanvas();
    window.addEventListener("resize",()=>{resizeCanvas();});
    render();
    document.getElementById("infoBar").textContent="";
  }catch(e){
    document.getElementById("infoBar").textContent="Connecting to server...";
    setTimeout(init, 3000);
  }
}

async function pollCrowd(){
  try{
    const [cr, rr, ar] = await Promise.all([fetch("/api/crowd"), fetch("/api/rooms"), fetch(`/api/status?t=${Date.now()}`)]);
    crowdData = await cr.json();
    roomData = await rr.json();
    const st = await ar.json();
    GLOBAL_HAZARDS = st.hazards || {};
    SMOKE_LEVEL = st.smoke_level || "none";
    if (SMOKE_LEVEL !== "none" && !window.smokeVoiceTriggered) {
      window.smokeVoiceTriggered = true;
      if (typeof speak === 'function') {
          let smokeMsg = "Warning! Smoke detected. Follow the glowing path to the nearest exit immediately!";
          if (typeof VOICE !== 'undefined') {
            if (VOICE.lang === 'hi-IN') smokeMsg = "चेतावनी! धुआं पाया गया है। तुरंत चमकते हुए रास्ते से बाहर निकलें!";
            if (VOICE.lang === 'kn-IN') smokeMsg = "ಎಚ್ಚರಿಕೆ! ಹೊಗೆ ಪತ್ತೆಯಾಗಿದೆ. ಹೊಳೆಯುವ ದಾರಿಯನ್ನು ಅನುಸರಿಸಿ ತಕ್ಷಣ ಹೊರಬನ್ನಿ!";
          }
          speak(smokeMsg);
        }
        showToast("⚠️ Smoke detected! Follow the lit route!", 6000);
    } else if (SMOKE_LEVEL === "none") {
      window.smokeVoiceTriggered = false;
    }
    
      // Broadcast logic
      if (st.broadcast) {
        if (lastBroadcastId === null) {
          lastBroadcastId = st.broadcast.id; // Silent sync on first page load
        } else if (st.broadcast.id > lastBroadcastId) {
          lastBroadcastId = st.broadcast.id;
          
          let bMsg = st.broadcast.message;
        if (typeof VOICE !== 'undefined') {
            if (VOICE.lang === 'hi-IN' && st.broadcast.message_hi) bMsg = st.broadcast.message_hi;
            if (VOICE.lang === 'kn-IN' && st.broadcast.message_kn) bMsg = st.broadcast.message_kn;
        }
        
        if (typeof speak === 'function') speak(bMsg);
        
        // Show a prominent alert toast
        const toast = document.getElementById("toast");
        if (toast) {
          toast.innerHTML = `<strong style="color:#facc15">&#128227; ADMIN BROADCAST:</strong><br>${bMsg}`;
          toast.className = "toast show";
          setTimeout(() => { toast.className = "toast"; }, 10000);
          }
        }
      }

      // Sync global alarm state
    if (st.alarm_active && !alarmInterval) {
      toggleEmergency(true);
    } else if (!st.alarm_active && alarmInterval) {
      toggleEmergency(false);
    }
  }catch(_){}
}

init();




  // ===== SAFE CHECK-IN =====
  let isMarkedSafe = false;
  async function markSafe() {
    if (isMarkedSafe) return;
    const name = prompt("Enter your Name or ID to check-in at the Safe Assembly Point:");
    if (!name || name.trim() === "") return;
    
    try {
      await fetch('/api/safe', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name: name.trim() })
      });
      
      isMarkedSafe = true;
      document.getElementById('safeBtn').style.display = 'none';
      document.getElementById('safeBadgeConfirmed').style.display = 'block';
      
      // Auto-cancel SOS if they were trapped but made it out
      if (sosSent && mySosId) {
        await fetch('/api/sos', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ action: 'clear', id: mySosId })
        });
        resetSOSButton();
      }

      if (typeof speak === 'function') {
        let safeMsg = 'You have been accounted for at the safe assembly point.';
        if (typeof VOICE !== 'undefined') {
          if (VOICE.lang === 'hi-IN') safeMsg = "सुरक्षित क्षेत्र में आपकी उपस्थिति दर्ज कर ली गई है।";
          if (VOICE.lang === 'kn-IN') safeMsg = "ಸುರಕ್ಷಿತ ಸ್ಥಳದಲ್ಲಿ ನಿಮ್ಮ ಹಾಜರಾತಿಯನ್ನು ದಾಖಲಿಸಲಾಗಿದೆ.";
        }
        speak(safeMsg);
      }
      showToast('&#9989; Checked in successfully!');
    } catch(e) {
      showToast('Error connecting to server.');
    }
  }

  // ===== SOS PANIC BUTTON =====
  let sosSent = false;
  let mySosId = null; // track this user's SOS ID on server

  async function sendSOS() {
    const btn = document.getElementById('sosBtn');
    const badge = document.getElementById('sosBadge');

    if (sosSent) {
      // Cancel - remove from server using our ID
      if (mySosId) {
        try {
          await fetch('/api/sos', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ action: 'clear', id: mySosId })
          });
        } catch(e) {}
      }
      resetSOSButton();
      showToast('SOS cancelled.');
      return;
    }

    // Prevent duplicate SOS
    if (mySosId) { showToast('SOS already active!'); return; }

    const roomName = currentUser.replace(/_/g, ' ');
    try {
      const r = await fetch('/api/sos', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ room: roomName, node: currentUser, message: 'HELP! I am trapped at ' + roomName })
      });
      const data = await r.json();
      mySosId = data.alert_id || null;
    } catch(e) {}

    sosSent = true;
    btn.classList.add('active');
    btn.innerHTML = '&#128681; SOS ACTIVE &mdash; Tap to Cancel';
    badge.style.display = 'block';

    if (typeof speak === 'function') {
      let sosMsg = 'S O S sent! Help is on the way. Stay calm and stay put.';
      if (typeof VOICE !== 'undefined') {
        if (VOICE.lang === 'hi-IN') sosMsg = "एस ओ एस भेज दिया गया है! मदद आ रही है। शांत रहें और वहीं रहें।";
        if (VOICE.lang === 'kn-IN') sosMsg = "ಎಸ್ ಓ ಎಸ್ ಕಳುಹಿಸಲಾಗಿದೆ! ಸಹಾಯ ಬರುತ್ತಿದೆ. ಶಾಂತರಾಗಿರಿ ಮತ್ತು ಅಲ್ಲೇ ಇರಿ.";
      }
      speak(sosMsg);
    }
    showToast('SOS sent to Admin! Stay put.', 5000);
  }

  function resetSOSButton() {
    sosSent = false;
    mySosId = null;
    const btn = document.getElementById('sosBtn');
    const badge = document.getElementById('sosBadge');
    if (btn) { btn.classList.remove('active'); btn.innerHTML = '&#128682; SOS &mdash; I\'m Trapped!'; }
    if (badge) badge.style.display = 'none';
  }

  // Track SOS alerts from server for beacon rendering + auto-reset
  let SOS_BEACON_NODES = [];
  async function pollSOS() {
    try {
      const r = await fetch('/api/sos');
      const alerts = await r.json();
      SOS_BEACON_NODES = alerts.map(a => a.node);

      // Auto-reset user's button if admin cleared their SOS
      if (mySosId && !alerts.find(a => a.id === mySosId)) {
        resetSOSButton();
        showToast('Rescue team confirmed! You are safe.');
      }
    } catch(e) {}
  }
  setInterval(pollSOS, 3000);

  
  // Register Service Worker for PWA
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(err => console.log('SW registration failed:', err));
  }

  