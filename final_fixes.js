const fs = require('fs');

let html = fs.readFileSync('templates/index.html', 'utf8');

// 1. Restore Compass Arrow in render()
const oldPin = `/* === USER PIN === */
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
    
    ctx.beginPath();
    ctx.arc(ux, uy, R(8), 0, Math.PI*2);
    ctx.fillStyle = (isDark?"#8AB4F8":"#4285F4"); ctx.fill();
    ctx.strokeStyle = isDark?"#121212":"#FFFFFF"; ctx.lineWidth = R(3); ctx.stroke();
  }`;

const newPin = `/* === USER PIN === */
  let xr, yr;
  if (PDR.active) { xr = PDR.pos.x; yr = PDR.pos.y; }
  else {
    const upos = NODE_POS[currentUser] || GRAPH.nodes[currentUser];
    if (upos) { xr = upos[0]; yr = upos[1]; } else { xr = null; }
  }
  if(xr !== null && xr !== undefined) {
    const ux = X(xr), uy = Y(yr);
    
    // Draw Compass Cone if sensors are active
    if (PDR.sensorMode && PDR.heading !== null) {
      const mapHeading = ((PDR.heading - PDR.northOffset) + 360) % 360;
      const rad = (mapHeading * Math.PI) / 180;
      const coneLen = R(45);
      const spread = 0.5; // radians
      ctx.beginPath();
      ctx.moveTo(ux, uy);
      ctx.lineTo(ux + coneLen * Math.sin(rad - spread), uy - coneLen * Math.cos(rad - spread));
      ctx.arc(ux, uy, coneLen, rad - spread - Math.PI/2, rad + spread - Math.PI/2);
      ctx.lineTo(ux, uy);
      ctx.fillStyle = isDark ? "rgba(138, 180, 248, 0.2)" : "rgba(66, 133, 244, 0.2)";
      ctx.fill();
      
      // Arrow indicator
      const arrowLen = R(24);
      const ax = ux + arrowLen * Math.sin(rad);
      const ay = uy - arrowLen * Math.cos(rad);
      ctx.beginPath();
      ctx.moveTo(ux, uy);
      ctx.lineTo(ax, ay);
      ctx.strokeStyle = isDark ? "#8AB4F8" : "#1A73E8";
      ctx.lineWidth = R(4);
      ctx.lineCap = "round";
      ctx.stroke();
    }

    const pulse = 1 + 0.4 * Math.sin(Date.now()/300);
    ctx.beginPath();
    ctx.arc(ux, uy, R(14) * pulse, 0, Math.PI*2);
    ctx.fillStyle = (isDark?"rgba(138,180,248,0.3)":"rgba(66, 133, 244, 0.3)");
    ctx.fill();
    
    ctx.beginPath();
    ctx.arc(ux, uy, R(8), 0, Math.PI*2);
    ctx.fillStyle = (isDark?"#8AB4F8":"#4285F4"); ctx.fill();
    ctx.strokeStyle = isDark?"#121212":"#FFFFFF"; ctx.lineWidth = R(3); ctx.stroke();
  }`;
html = html.replace(oldPin, newPin);

// 2. Fix Navigation Z-Index to overlap floating buttons
html = html.replace('.nav-overlay { position: fixed; inset: 0; background: var(--bg); z-index: 200;', '.nav-overlay { position: fixed; inset: 0; background: var(--bg); z-index: 2500;');
html = html.replace('.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 2000;', '.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 3000;');

// 3. Fix invisible Language Dropdown in bottom bar
html = html.replace('background:#0c1e3c;color:var(--text);border:1px solid var(--border);', 'background:var(--bg);color:var(--text);border:1px solid var(--border);');
// Fix flex sizing so language dropdown isn't crushed
html = html.replace('<select onchange="changeLanguage(this.value)" style="', '<select onchange="changeLanguage(this.value)" style="flex:1;min-width:90px;');

// 4. Rewrite renderNavMiniMap to render the full map, scaled correctly, WITH rooms/corridors
const miniMapStart = html.indexOf('function renderNavMiniMap(path) {');
if (miniMapStart !== -1) {
  let openBraces = 1;
  let i = html.indexOf('{', miniMapStart) + 1;
  while (i < html.length && openBraces > 0) {
    if (html[i] === '{') openBraces++;
    else if (html[i] === '}') openBraces--;
    i++;
  }
  
  const newMiniMap = `function renderNavMiniMap(path) {
  const nc = document.getElementById("navCanvas");
  const nwrap = nc.parentElement;
  nc.width = nwrap.clientWidth;
  nc.height = nwrap.clientHeight;
  const nctx = nc.getContext("2d");

  // Fit map to canvas, keeping aspect ratio
  const scale = Math.min(nc.width / DW, nc.height / DH) * 0.9;
  const cx = (nc.width - DW * scale) / 2;
  const cy = (nc.height - DH * scale) / 2;
  
  const NX = x => cx + (x * scale);
  const NY = y => cy + (y * scale);
  const NR = r => Math.max(r * scale, 3); // minimum visible radius
  
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  nctx.fillStyle = isDark ? "#1A1A1A" : "#E8EAED";
  nctx.fillRect(0,0,nc.width,nc.height);

  /* === CORRIDORS === */
  nctx.fillStyle = isDark ? "#2D2D2D" : "#FFFFFF";
  CORRIDORS.forEach(c => {
    nctx.fillRect(NX(c.x), NY(c.y), c.w * scale, c.h * scale);
  });

  /* === ROOMS === */
  Object.entries(ROOM_RECTS).forEach(([name, r]) => {
    const onPath = path && path.includes(name);
    const isUser = name === currentUser;
    
    nctx.beginPath();
    nctx.rect(NX(r.x), NY(r.y), r.w * scale, r.h * scale);
    
    nctx.fillStyle = isUser ? (isDark?"#3b1414":"#FCE8E6") : onPath ? (isDark?"#122a4f":"#E8F0FE") : (isDark?"#242424":"#F1F3F4");
    nctx.fill();
    nctx.strokeStyle = isUser ? (isDark?"#F28B82":"#EA4335") : onPath ? (isDark?"#8AB4F8":"#1A73E8") : (isDark?"#333333":"#DADCE0");
    nctx.lineWidth = NR(2);
    nctx.stroke();
  });

  /* === PATHS === */
  if (path && path.length > 1) {
    nctx.beginPath();
    for(let j=0; j<path.length; j++){
      const p = NODE_POS[path[j]] || GRAPH.nodes[path[j]];
      if(!p) continue;
      if(j === 0) nctx.moveTo(NX(p[0]), NY(p[1]));
      else nctx.lineTo(NX(p[0]), NY(p[1]));
    }
    nctx.strokeStyle = (isDark?"#8AB4F8":"#1A73E8");
    nctx.lineWidth = NR(6);
    nctx.lineCap = "round"; nctx.lineJoin = "round";
    nctx.stroke();
  }

  /* === USER / START / END === */
  if (path) {
    path.forEach((name,idx) => {
      const pos = NODE_POS[name]||GRAPH.nodes[name];
      if(!pos) return;
      const isStart = idx===0, isEnd = idx===path.length-1;
      if (!isStart && !isEnd) return; // Only draw start and end dots
      
      nctx.beginPath();
      nctx.arc(NX(pos[0]),NY(pos[1]),NR(isStart||isEnd?10:6),0,Math.PI*2);
      nctx.fillStyle = isEnd?"#f59e0b":isStart?"#ef4444":"rgba(245,158,11,0.5)";
      nctx.fill();
      
      nctx.fillStyle = isDark?"#121212":"#FFFFFF";
      nctx.font=\`bold \${Math.max(NR(8), 10)}px Inter\`;
      nctx.textAlign="center";
      nctx.textBaseline="middle";
      nctx.fillText(isStart?"YOU":isEnd?"🚨":"",NX(pos[0]),NY(pos[1]));
    });
  }

  NAV._miniCtx = nctx;
  NAV._miniCanvas = nc;
  NAV._miniPath = path || [];
  
  // Store the transform functions so pointer updates work correctly
  window._NX = NX;
  window._NY = NY;
  window._NR = NR;
}`;
  html = html.substring(0, miniMapStart) + newMiniMap + html.substring(i);
}

fs.writeFileSync('templates/index.html', html, 'utf8');
