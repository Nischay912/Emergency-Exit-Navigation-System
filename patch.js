const fs = require('fs');

let html = fs.readFileSync('templates/index.html', 'utf8');

// 1. DW/DH let fix
html = html.replace('const DW=880,DH=580;', 'let DW=880,DH=580;');

// 2. new render() function
const newRender = `function render() {
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
    ctx.font = \`500 \${Math.max(R(12), 10)}px 'Roboto', sans-serif\`;
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillStyle = isUser ? (isDark?"#F28B82":"#C5221F") : onPath ? (isDark?"#8AB4F8":"#174EA6") : (isDark?"#9AA0A6":"#5F6368");
    
    const labelTxt = r.label || name.replace(/_/g," ");
    if(r.icon) {
      ctx.font = \`\${Math.max(R(16), 14)}px sans-serif\`;
      ctx.fillText(r.icon, cx, cy - Math.max(R(8), 6));
      ctx.font = \`500 \${Math.max(R(11), 9)}px 'Roboto', sans-serif\`;
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
      ctx.font = \`bold \${Math.max(R(12), 10)}px sans-serif\`;
      ctx.fillStyle = isDark?"#121212":"#FFFFFF"; ctx.textAlign="center"; ctx.textBaseline="middle";
      ctx.fillText("★", X(pos[0]), Y(pos[1]));
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
    
    ctx.beginPath();
    ctx.arc(ux, uy, R(8), 0, Math.PI*2);
    ctx.fillStyle = (isDark?"#8AB4F8":"#4285F4"); ctx.fill();
    ctx.strokeStyle = isDark?"#121212":"#FFFFFF"; ctx.lineWidth = R(3); ctx.stroke();
  }

  updateSidebar(bestExit, bCost, path);
  if(window.requestAnimationFrame) requestAnimationFrame(render);
}`;

let startIdx = html.indexOf('function render(){');
if (startIdx === -1) startIdx = html.indexOf('function render() {');
if (startIdx !== -1) {
  let openBraces = 1;
  let i = html.indexOf('{', startIdx) + 1;
  while (i < html.length && openBraces > 0) {
    if (html[i] === '{') openBraces++;
    else if (html[i] === '}') openBraces--;
    i++;
  }
  html = html.substring(0, startIdx) + newRender + html.substring(i);
}

// 3. CSS Google Maps Styling & Polish
const googleCss = `
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

:root {
  --bg: #F8F9FA; --panel: #FFFFFF; --border: #DADCE0; --text: #202124; --muted: #5F6368;
  --red: #EA4335; --green: #34A853; --amber: #FBBC04; --blue: #1A73E8; --route-bg: #E8F0FE; --map-bg: #E8EAED;
}
:root[data-theme="dark"] {
  --bg: #121212; --panel: #1E1E1E; --border: #333333; --text: #E8EAED; --muted: #9AA0A6;
  --route-bg: #174EA6; --blue: #8AB4F8; --map-bg: #1A1A1A;
}

* { box-sizing: border-box; }
body { margin: 0; padding: 0; font-family: 'Roboto', sans-serif; background: var(--bg); color: var(--text); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }

header { background: var(--panel); padding: 12px 20px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,0,0,0.1); z-index: 100; }
.logo { display: flex; align-items: center; gap: 12px; }
.logo-icon { font-size: 24px; }
.logo h1 { margin: 0; font-size: 18px; color: var(--text); font-weight: 500; }
.logo p { margin: 0; font-size: 12px; color: var(--muted); }
.hdr-right { display: flex; gap: 8px; }
.badge { padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 700; background: #F1F3F4; color: var(--muted); }
.badge-cam { background: #E8F0FE; color: #174EA6; }
.badge-live { background: #E6F4EA; color: #137333; display: flex; align-items: center; gap: 4px; }
.live-dot { width: 6px; height: 6px; background: #137333; border-radius: 50%; }

.app { display: flex; flex: 1; height: calc(100vh - 60px); position: relative; }
.sidebar { width: 380px; background: var(--panel); border-right: 1px solid var(--border); box-shadow: 2px 0 8px rgba(0,0,0,0.05); display: flex; flex-direction: column; overflow-y: auto; z-index: 50; padding: 20px; gap: 20px; }

@media(max-width: 768px) {
  .sidebar { width: 100%; height: 45vh; border-right: none; border-top: 1px solid var(--border); box-shadow: 0 -2px 10px rgba(0,0,0,0.1); }
  .app { flex-direction: column-reverse; }
}

.map-col { display: flex; flex-direction: column; flex: 1; position: relative; overflow: hidden; background: var(--map-bg); }
.canvas-wrap { flex: 1; position: relative; width: 100%; height: 100%; }
.canvas-wrap canvas { display: block; width: 100%; height: 100%; }
.info-bar { display: none; }

.sec-lbl { font-size: 12px; font-weight: 700; color: var(--muted); text-transform: uppercase; margin-bottom: 12px; letter-spacing: 0.5px; }
.loc-card { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.at { font-size: 13px; color: var(--muted); }
.name { font-size: 18px; font-weight: 700; margin-top: 4px; color: var(--text); }
.hint { font-size: 11px; color: var(--muted); margin-top: 12px; margin-bottom: 4px; }
.loc-select { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 8px; font-family: inherit; font-size: 14px; background: var(--bg); color: var(--text); }
.rec-card { background: var(--route-bg); border: 1px solid var(--blue); border-radius: 12px; padding: 16px; color: var(--text); }
.rl { font-size: 12px; font-weight: 700; margin-bottom: 4px; color: var(--blue); }
.re { font-size: 24px; font-weight: 700; margin-bottom: 8px; color: var(--blue); }
.rp { font-size: 13px; color: var(--text); line-height: 1.4; opacity: 0.9; }

/* Legend styling */
.leg-row { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text); margin-bottom: 8px; font-weight: 500; }
.leg-dot { width: 12px; height: 12px; border-radius: 50%; box-shadow: 0 1px 2px rgba(0,0,0,0.2); }
.leg-sq { width: 14px; height: 4px; border-radius: 2px; box-shadow: 0 1px 2px rgba(0,0,0,0.2); }
.legend-sec { background: var(--panel); padding: 16px; border: 1px solid var(--border); border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }

.nav-trigger { width: 100%; padding: 14px; background: var(--blue); color: white; border: none; border-radius: 24px; font-size: 15px; font-weight: 500; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 2px 6px rgba(26,115,232,0.3); transition: 0.2s; }
.nav-trigger:hover { background: #174ea6; box-shadow: 0 4px 10px rgba(26,115,232,0.4); }
.walk-btn { width: 100%; padding: 12px; background: var(--panel); border: 1px solid var(--border); color: var(--blue); border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; margin-bottom: 8px; transition: 0.2s; }
.walk-btn:hover { background: var(--bg); }
.walk-btn.start { background: var(--green); color: white; border: none; }
.walk-btn.start:hover { background: #0D652D; }

.exit-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--border); font-size: 14px; }
.exit-row.best { background: var(--route-bg); border-radius: 8px; padding-left: 8px; padding-right: 8px; border-bottom: none; }
.exit-row-name { font-weight: 500; }
.cpill { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; background: #F1F3F4; color: var(--muted); }
.cpill.Low { background: #E6F4EA; color: #137333; }
.cpill.Medium { background: #FEF7E0; color: #B06000; }
.cpill.High { background: #FCE8E6; color: #C5221F; }

/* Nav Overlay */
.nav-overlay { position: fixed; inset: 0; background: var(--bg); z-index: 200; display: flex; flex-direction: column; transform: translateY(100%); transition: transform 0.3s cubic-bezier(0.2, 0.8, 0.2, 1); }
.nav-overlay.active { transform: translateY(0); }
.nav-top { background: var(--green); color: white; padding: 24px; padding-top: max(24px, env(safe-area-inset-top)); display: flex; gap: 16px; align-items: center; box-shadow: 0 2px 6px rgba(0,0,0,0.2); }
.nav-arrow { font-size: 40px; font-weight: bold; width: 48px; text-align: center; }
.nav-action { font-size: 24px; font-weight: 700; }
.nav-target { font-size: 16px; opacity: 0.9; margin-top: 4px; }
.nav-steps-wrap { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 8px; }
.nav-step-item { background: var(--panel); padding: 16px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); display: flex; gap: 16px; align-items: center; }
.nav-step-arrow { font-size: 24px; color: var(--blue); width: 32px; text-align: center; }
.nav-step-action { font-size: 16px; font-weight: 500; color: var(--text); }
.nav-step-sub { font-size: 13px; color: var(--muted); margin-top: 4px; }
.nav-bottom { padding: 16px; background: var(--panel); border-top: 1px solid var(--border); display: flex; gap: 12px; padding-bottom: max(16px, env(safe-area-inset-bottom)); }
.nav-close-btn { flex: 1; background: var(--bg); color: var(--text); border: 1px solid var(--border); padding: 14px; border-radius: 12px; font-weight: 500; cursor: pointer; }
.nav-demo-btn { flex: 2; background: var(--blue); color: white; border: none; padding: 14px; border-radius: 12px; font-weight: 500; cursor: pointer; }
.nav-demo-btn.stop { background: var(--red); }

@keyframes flash { 0%, 100% { background: rgba(234, 67, 53, 0); } 50% { background: rgba(234, 67, 53, 0.3); } }
.alarm-overlay { position: fixed; inset: 0; pointer-events: none; z-index: 9999; display: none; animation: flash 0.6s infinite; }

/* Modal and Theme Buttons */
.floating-btn { position: fixed; top: 20px; right: 20px; width: 44px; height: 44px; border-radius: 50%; background: var(--panel); border: 1px solid var(--border); box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; align-items: center; justify-content: center; cursor: pointer; z-index: 1000; font-size: 20px; transition: 0.2s; color: var(--text); }
.floating-btn:hover { background: var(--bg); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 2000; display: flex; align-items: center; justify-content: center; opacity: 0; pointer-events: none; transition: 0.2s; }
.modal-overlay.active { opacity: 1; pointer-events: auto; }
.modal-card { background: var(--panel); border-radius: 12px; padding: 24px; width: 320px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
</style>
`;
html = html.replace(/<style>[\s\S]*?<\/style>/i, googleCss);

// 4. Inject Audio Settings Modal and Theme Toggle (only once)
if (!html.includes('id="audioModal"')) {
    const uiElements = `
<button id="themeToggle" class="floating-btn" onclick="toggleTheme()">
  <span id="themeIcon">&#127769;</span>
</button>
<button id="audioToggle" class="floating-btn" onclick="openAudioSettings()" style="top: 80px;">
  <span id="audioIcon">&#128266;</span>
</button>

<div id="audioModal" class="modal-overlay">
  <div class="modal-card">
    <h3 style="margin-top:0; color:var(--text);">Audio Settings</h3>
    <div style="margin-bottom: 12px;">
      <label style="display:block; font-size:12px; color:var(--muted); margin-bottom:4px;">Language</label>
      <select id="langSelect" class="loc-select" onchange="changeLanguage(this.value)">
        <option value="en-US">English</option>
        <option value="hi-IN">Hindi (हिंदी)</option>
        <option value="kn-IN">Kannada (ಕನ್ನಡ)</option>
      </select>
    </div>
    <div style="margin-bottom: 20px;">
      <label style="display:block; font-size:12px; color:var(--muted); margin-bottom:4px;">Voice</label>
      <button id="muteBtn" class="walk-btn start" onclick="toggleMute()" style="width:100%;">
        &#128266; Mute
      </button>
    </div>
    <button class="nav-trigger" onclick="closeAudioSettings()">Done</button>
  </div>
</div>
`;
    html = html.replace('<div class="app">', uiElements + '\\n<div class="app">');
}

// 5. Inject JS functions safely at the very end
if (!html.includes('window.audioPromptedFlag')) {
    const jsScripts = `
<script>
// --- Added UI Functions ---
function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  document.getElementById('themeIcon').innerHTML = next === 'dark' ? '&#9728;' : '&#127769;';
}

function openAudioSettings() { document.getElementById('audioModal').classList.add('active'); }
function closeAudioSettings() { document.getElementById('audioModal').classList.remove('active'); }
function toggleMute() {
  VOICE.enabled = !VOICE.enabled;
  const btn = document.getElementById('muteBtn');
  const icon = document.getElementById('audioIcon');
  if(VOICE.enabled) {
    btn.innerHTML = '&#128266; Mute';
    btn.className = 'walk-btn start';
    icon.innerHTML = '&#128266;';
  } else {
    btn.innerHTML = '&#128263; Unmute';
    btn.className = 'walk-btn';
    icon.innerHTML = '&#128263;';
  }
}

window.audioPromptedFlag = false;
const origToggleWalkMode = window.toggleWalkMode;
window.toggleWalkMode = function() {
  if(!window.audioPromptedFlag) { window.audioPromptedFlag = true; openAudioSettings(); }
  if (origToggleWalkMode) origToggleWalkMode();
};

const origToggleDemoWalk = window.toggleDemoWalk;
window.toggleDemoWalk = function() {
  if(!window.audioPromptedFlag) { window.audioPromptedFlag = true; openAudioSettings(); }
  if (origToggleDemoWalk) origToggleDemoWalk();
};
</script>
`;
    html = html.replace('</body>', jsScripts + '\\n</body>');
}

// 6. Fix RenderNavMiniMap
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

  // Calculate Bounding Box of Path to Zoom In
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  if (path && path.length > 0) {
    path.forEach(n => {
      const p = NODE_POS[n] || (GRAPH ? GRAPH.nodes[n] : null);
      if (p) {
        if (p[0] < minX) minX = p[0];
        if (p[0] > maxX) maxX = p[0];
        if (p[1] < minY) minY = p[1];
        if (p[1] > maxY) maxY = p[1];
      }
    });
  }
  
  if (minX === Infinity) {
    minX = 0; maxX = DW; minY = 0; maxY = DH;
  }

  // Add padding
  let pW = maxX - minX;
  let pH = maxY - minY;
  if (pW < 200) pW = 200; // prevent over-zooming on small paths
  if (pH < 200) pH = 200;
  
  const pad = Math.max(pW, pH) * 0.3; // 30% padding
  minX -= pad; maxX += pad;
  minY -= pad; maxY += pad;
  
  const viewW = maxX - minX;
  const viewH = maxY - minY;
  
  const scale = Math.min(nc.width / viewW, nc.height / viewH);
  const cx = (nc.width - viewW * scale) / 2;
  const cy = (nc.height - viewH * scale) / 2;
  
  const NX = x => cx + (x - minX) * scale;
  const NY = y => cy + (y - minY) * scale;
  const NR = r => r * scale;

  // Background
  nctx.fillStyle = "#080c1e";
  nctx.fillRect(0,0,nc.width,nc.height);

  // Path segments highlighted
  const pathSet = new Set();
  if (path) {
    for(let i=0;i<path.length-1;i++){
      pathSet.add(path[i]+"|"+path[i+1]);
      pathSet.add(path[i+1]+"|"+path[i]);
    }
  }

  if (GRAPH) {
    GRAPH.edges.forEach(([u,v,d]) => {
      const pu = NODE_POS[u]||GRAPH.nodes[u];
      const pv = NODE_POS[v]||GRAPH.nodes[v];
      if(!pu||!pv) return;
      const onP = pathSet.has(u+"|"+v);
      nctx.beginPath();
      nctx.moveTo(NX(pu[0]),NY(pu[1]));
      nctx.lineTo(NX(pv[0]),NY(pv[1]));
      nctx.strokeStyle = onP ? "#f59e0b" : "#1e3a5f";
      nctx.lineWidth = onP ? NR(5) : NR(1.5);
      nctx.setLineDash(onP?[]:[NR(3),NR(4)]);
      nctx.shadowColor = onP?"#f59e0b":"transparent";
      nctx.shadowBlur = onP?NR(6):0;
      nctx.stroke();
    });
  }
  
  nctx.setLineDash([]);
  nctx.shadowBlur = 0;

  if (path) {
    for(let i=0;i<path.length-1;i++){
      const pu = NODE_POS[path[i]]||GRAPH.nodes[path[i]];
      const pv = NODE_POS[path[i+1]]||GRAPH.nodes[path[i+1]];
      if(!pu||!pv) continue;
      const mx = NX((pu[0]+pv[0])/2), my = NY((pu[1]+pv[1])/2);
      const angle = Math.atan2(pv[1]-pu[1], pv[0]-pu[0]);
      nctx.save();
      nctx.translate(mx,my);
      nctx.rotate(angle);
      nctx.fillStyle="#f59e0b";
      nctx.beginPath();
      nctx.moveTo(NR(6),0);
      nctx.lineTo(-NR(4),-NR(3));
      nctx.lineTo(-NR(4),NR(3));
      nctx.closePath();
      nctx.fill();
      nctx.restore();
    }
  }

  // Nodes
  if (path) {
    path.forEach((name,idx) => {
      const pos = NODE_POS[name]||GRAPH.nodes[name];
      if(!pos) return;
      const isStart = idx===0, isEnd = idx===path.length-1;
      nctx.beginPath();
      nctx.arc(NX(pos[0]),NY(pos[1]),NR(isStart||isEnd?12:7),0,Math.PI*2);
      nctx.fillStyle = isEnd?"#f59e0b":isStart?"#ef4444":"rgba(245,158,11,0.5)";
      nctx.shadowColor = isEnd?"#f59e0b":isStart?"#ef4444":"transparent";
      nctx.shadowBlur = NR(8);
      nctx.fill();
      nctx.shadowBlur=0;
      // Label
      nctx.fillStyle="#fff";
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

// 7. Update drawDemoPointerOnMiniMap
const ptrStart = html.indexOf('function drawDemoPointerOnMiniMap(pos) {');
if (ptrStart !== -1) {
  let openBraces = 1;
  let i = html.indexOf('{', ptrStart) + 1;
  while (i < html.length && openBraces > 0) {
    if (html[i] === '{') openBraces++;
    else if (html[i] === '}') openBraces--;
    i++;
  }
  const newPtr = `function drawDemoPointerOnMiniMap(pos) {
  if (!NAV.demoRunning || !NAV._miniCtx || !NAV._miniCanvas || !pos || !window._NX) return;
  
  // Clear the mini map and redraw
  renderNavMiniMap(NAV._miniPath);
  
  const nctx = NAV._miniCtx;
  const NX = window._NX;
  const NY = window._NY;
  const NR = window._NR;
  
  const x = NX(pos.x);
  const y = NY(pos.y);
  
  nctx.beginPath();
  nctx.arc(x, y, Math.max(NR(12), 12), 0, Math.PI*2);
  nctx.fillStyle = "#ef4444";
  nctx.shadowColor = "#ef4444"; nctx.shadowBlur = Math.max(NR(12), 12);
  nctx.fill(); nctx.shadowBlur = 0;
  
  nctx.fillStyle = "#fff"; nctx.textAlign = "center"; nctx.textBaseline = "middle";
  nctx.font = \`bold \${Math.max(NR(10), 10)}px Inter\`;
  nctx.fillText("YOU", x, y);
}`;
  html = html.substring(0, ptrStart) + newPtr + html.substring(i);
}

// Speed slow down logic (const duration = Math.max(3000, step.dist * 150);)
html = html.replace('Math.max(3000, step.dist * 150)', 'Math.max(6000, step.dist * 450)');

fs.writeFileSync('templates/index.html', html, 'utf8');
