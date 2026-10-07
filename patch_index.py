import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update global vars and init
old_init = """let GRAPH=null,crowdData={},roomData={},currentUser=USER_NODE_INIT,bestExit=null,animT=0;"""
new_init = """let GRAPH=null, LAYOUT=null, ROOM_RECTS={}, CORRIDORS=[], NODE_POS={}, crowdData={}, roomData={}, currentUser=USER_NODE_INIT, bestExit=null, animT=0;"""
html = html.replace(old_init, new_init)

# 2. Remove hardcoded ROOM_RECTS, CORRIDORS, NODE_POS
html = re.sub(r'const ROOM_RECTS=\{.*?\};\s*const CORRIDORS=\[.*?\];\s*/\* Node centers mapped onto floor plan \*/\s*const NODE_POS=\{.*?\};\s*', '', html, flags=re.DOTALL)

# 3. Add fetchLayout to init()
fetch_fn = """
async function fetchLayout() {
  try {
    const res = await fetch("/api/layout");
    LAYOUT = await res.json();
    ROOM_RECTS = LAYOUT.rooms || {};
    CORRIDORS = LAYOUT.corridors || [];
    NODE_POS = LAYOUT.nodes || {};
    if (LAYOUT.width) DW = LAYOUT.width;
    if (LAYOUT.height) DH = LAYOUT.height;
    
    // Dynamically build the select dropdown based on NODE_POS
    const sel = document.getElementById("locSelect");
    if(sel) {
      sel.innerHTML = '<option value="">-- Select your location --</option>' + 
        Object.keys(NODE_POS).map(k => `<option value="${k}">${k.replace(/_/g," ")}</option>`).join("");
      sel.value = currentUser;
    }
  } catch(e) { console.error("Map Layout error", e); }
}
"""
html = html.replace('async function fetchGraph()', fetch_fn + '\nasync function fetchGraph()')

old_init_call = """async function init() {
  await fetchGraph();"""
new_init_call = """async function init() {
  await fetchLayout();
  await fetchGraph();"""
html = html.replace(old_init_call, new_init_call)


# 4. Completely replace the CSS to a Google Maps style UI
google_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

:root {
  --bg: #F8F9FA;
  --panel: #FFFFFF;
  --border: #DADCE0;
  --text: #202124;
  --muted: #5F6368;
  --red: #EA4335;
  --green: #34A853;
  --amber: #FBBC04;
  --blue: #1A73E8;
  --route-bg: #E8F0FE;
}

* { box-sizing: border-box; }
body { margin: 0; padding: 0; font-family: 'Roboto', sans-serif; background: var(--bg); color: var(--text); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }

/* Header */
header {
  background: var(--panel); padding: 12px 20px; display: flex; align-items: center; justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1); z-index: 100;
}
.logo { display: flex; align-items: center; gap: 12px; }
.logo-icon { font-size: 24px; }
.logo h1 { margin: 0; font-size: 18px; color: var(--text); font-weight: 500; }
.logo p { margin: 0; font-size: 12px; color: var(--muted); }
.hdr-right { display: flex; gap: 8px; }
.badge { padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 700; background: #F1F3F4; color: var(--muted); }
.badge-live { background: #E6F4EA; color: #137333; display: flex; align-items: center; gap: 4px; }
.live-dot { width: 6px; height: 6px; background: #137333; border-radius: 50%; }

/* App Layout */
.app { display: flex; flex: 1; height: calc(100vh - 60px); position: relative; }

/* Sidebar (Floating panel on desktop, bottom sheet on mobile) */
.sidebar {
  width: 380px; background: var(--panel); border-right: 1px solid var(--border); box-shadow: 2px 0 8px rgba(0,0,0,0.05);
  display: flex; flex-direction: column; overflow-y: auto; z-index: 50; padding: 20px; gap: 20px;
}
@media(max-width: 768px) {
  .sidebar { width: 100%; border-right: none; border-top: 1px solid var(--border); box-shadow: 0 -2px 10px rgba(0,0,0,0.1); }
  .app { flex-direction: column-reverse; }
}

/* Map Wrap */
.map-wrap { flex: 1; position: relative; background: #E8EAED; overflow: hidden; }
canvas { display: block; width: 100%; height: 100%; }

/* Cards & Sections */
.sec-lbl { font-size: 12px; font-weight: 700; color: var(--muted); text-transform: uppercase; margin-bottom: 12px; letter-spacing: 0.5px; }
.loc-card { background: #FFFFFF; border: 1px solid var(--border); border-radius: 12px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.loc-select { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 8px; margin-top: 8px; font-family: inherit; font-size: 14px; background: #F8F9FA; }
.rec-card { background: var(--route-bg); border: 1px solid #c2e7ff; border-radius: 12px; padding: 16px; color: #174ea6; }
.rl { font-size: 12px; font-weight: 700; margin-bottom: 4px; color: var(--blue); }
.re { font-size: 24px; font-weight: 700; margin-bottom: 8px; color: #001d35; }
.rp { font-size: 13px; color: #185abc; line-height: 1.4; }

/* Buttons */
.nav-trigger { width: 100%; padding: 14px; background: var(--blue); color: white; border: none; border-radius: 24px; font-size: 15px; font-weight: 500; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 2px 6px rgba(26,115,232,0.3); transition: 0.2s; }
.nav-trigger:hover { background: #174ea6; box-shadow: 0 4px 10px rgba(26,115,232,0.4); }
.walk-btn { width: 100%; padding: 12px; background: white; border: 1px solid var(--border); color: var(--blue); border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; margin-bottom: 8px; transition: 0.2s; }
.walk-btn:hover { background: #F8F9FA; }
.walk-btn.start { background: var(--green); color: white; border: none; }
.walk-btn.start:hover { background: #0D652D; }

/* Lists */
.list-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--border); font-size: 14px; }
.list-item:last-child { border: none; }
.item-title { font-weight: 500; }
.badge.Low { background: #E6F4EA; color: #137333; }
.badge.Medium { background: #FEF7E0; color: #B06000; }
.badge.High { background: #FCE8E6; color: #C5221F; }

/* Navigation Overlay */
.nav-overlay { position: fixed; inset: 0; background: var(--bg); z-index: 200; display: flex; flex-direction: column; transform: translateY(100%); transition: transform 0.3s cubic-bezier(0.2, 0.8, 0.2, 1); }
.nav-overlay.active { transform: translateY(0); }
.nav-top { background: var(--green); color: white; padding: 24px; padding-top: max(24px, env(safe-area-inset-top)); display: flex; gap: 16px; align-items: center; box-shadow: 0 2px 6px rgba(0,0,0,0.2); }
.nav-arrow { font-size: 40px; font-weight: bold; width: 48px; text-align: center; }
.nav-action { font-size: 24px; font-weight: 700; }
.nav-target { font-size: 16px; opacity: 0.9; margin-top: 4px; }
.nav-steps-wrap { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 8px; }
.nav-step-item { background: white; padding: 16px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); display: flex; gap: 16px; align-items: center; }
.nav-step-arrow { font-size: 24px; color: var(--blue); width: 32px; text-align: center; }
.nav-step-action { font-size: 16px; font-weight: 500; color: var(--text); }
.nav-step-sub { font-size: 13px; color: var(--muted); margin-top: 4px; }
.nav-bottom { padding: 16px; background: white; border-top: 1px solid var(--border); display: flex; gap: 12px; padding-bottom: max(16px, env(safe-area-inset-bottom)); }
.nav-close-btn { flex: 1; background: #F1F3F4; color: var(--text); border: none; padding: 14px; border-radius: 12px; font-weight: 500; cursor: pointer; }
.nav-demo-btn { flex: 2; background: var(--blue); color: white; border: none; padding: 14px; border-radius: 12px; font-weight: 500; cursor: pointer; }
.nav-demo-btn.stop { background: var(--red); }

@keyframes flash { 0%, 100% { background: rgba(234, 67, 53, 0); } 50% { background: rgba(234, 67, 53, 0.3); } }
.alarm-overlay { position: fixed; inset: 0; pointer-events: none; z-index: 9999; display: none; animation: flash 0.6s infinite; }
</style>
"""
html = re.sub(r'<style>.*?</style>', google_css, html, flags=re.DOTALL)

# 5. Replace Map Drawing Logic (Google Maps Style Render)
render_code_old = r'function render\(\) \{.*?(?=function updateExitList\(\) \{)'
render_code_new = """function render() {
  if(!ctx) return;
  ctx.clearRect(0,0,canvas.width,canvas.height);
  
  // Background
  ctx.fillStyle = "#E8EAED";
  ctx.fillRect(0,0,canvas.width,canvas.height);
  
  if(!GRAPH) return;
  
  // 1. Corridors (Walkways) -> White Floor
  ctx.fillStyle = "#FFFFFF";
  CORRIDORS.forEach(c => {
    ctx.fillRect(X(c.x), Y(c.y), X(c.w), Y(c.h));
  });
  
  // 2. Rooms -> Solid blocks with borders
  Object.entries(ROOM_RECTS).forEach(([name, r]) => {
    const onPath = path.includes(name);
    const isUser = name === currentUser;
    
    // Draw Room Shadow/Border
    ctx.beginPath();
    if(ctx.roundRect) ctx.roundRect(X(r.x), Y(r.y), X(r.w), Y(r.h), R(6));
    else ctx.rect(X(r.x), Y(r.y), X(r.w), Y(r.h));
    
    ctx.fillStyle = isUser ? "#FCE8E6" : onPath ? "#E8F0FE" : "#F1F3F4";
    ctx.fill();
    ctx.strokeStyle = isUser ? "#EA4335" : onPath ? "#1A73E8" : "#DADCE0";
    ctx.lineWidth = R(2);
    ctx.stroke();
    
    // Room Text
    const cx = X(r.x + r.w/2), cy = Y(r.y + r.h/2);
    ctx.font = `500 ${Math.max(R(12), 10)}px 'Roboto', sans-serif`;
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillStyle = isUser ? "#C5221F" : onPath ? "#174EA6" : "#5F6368";
    
    const labelTxt = r.label || name.replace(/_/g," ");
    // Draw icon slightly above label
    if(r.icon) {
      ctx.font = `${Math.max(R(16), 14)}px sans-serif`;
      ctx.fillText(r.icon, cx, cy - Math.max(R(8), 6));
      ctx.font = `500 ${Math.max(R(11), 9)}px 'Roboto', sans-serif`;
      ctx.fillText(labelTxt, cx, cy + Math.max(R(8), 6));
    } else {
      ctx.fillText(labelTxt, cx, cy);
    }
  });
  
  // 3. Navigation Path (Thick Google Blue Line)
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
    // Draw un-walked path
    ctx.beginPath();
    for(let i=walkedUpToIdx; i<path.length; i++){
      const p = NODE_POS[path[i]] || GRAPH.nodes[path[i]];
      if(!p) continue;
      if(i === walkedUpToIdx) {
        // start from PDR pos if active, else node center
        const startX = PDR.active ? PDR.pos.x : p[0];
        const startY = PDR.active ? PDR.pos.y : p[1];
        ctx.moveTo(X(startX), Y(startY));
      }
      else ctx.lineTo(X(p[0]), Y(p[1]));
    }
    ctx.strokeStyle = "#1A73E8"; // Google Blue
    ctx.lineWidth = R(8);
    ctx.lineCap = "round"; ctx.lineJoin = "round";
    ctx.stroke();

    // Draw walked path (gray)
    if(walkedUpToIdx > 0) {
      ctx.beginPath();
      for(let i=0; i<=walkedUpToIdx; i++){
        const p = NODE_POS[path[i]] || GRAPH.nodes[path[i]];
        if(!p) continue;
        if(i === 0) ctx.moveTo(X(p[0]), Y(p[1]));
        else ctx.lineTo(X(p[0]), Y(p[1]));
      }
      if(PDR.active) {
        ctx.lineTo(X(PDR.pos.x), Y(PDR.pos.y));
      }
      ctx.strokeStyle = "#BDC1C6"; // Gray
      ctx.lineWidth = R(8);
      ctx.lineCap = "round"; ctx.lineJoin = "round";
      ctx.stroke();
    }
  }
  
  // 4. Exit Nodes
  GRAPH.exit_nodes.forEach(name => {
    const pos = NODE_POS[name] || GRAPH.nodes[name];
    if(!pos) return;
    const isBest = name === bExit;
    const clr = isBest ? "#1E8E3E" : "#EA4335";
    
    ctx.beginPath();
    ctx.arc(X(pos[0]), Y(pos[1]), R(isBest?12:10), 0, Math.PI*2);
    ctx.fillStyle = clr; ctx.fill();
    ctx.strokeStyle = "#FFFFFF"; ctx.lineWidth = R(3); ctx.stroke();
    
    if(isBest) {
      ctx.font = `bold ${Math.max(R(12), 10)}px sans-serif`;
      ctx.fillStyle = "#FFFFFF"; ctx.textAlign="center"; ctx.textBaseline="middle";
      ctx.fillText("★", X(pos[0]), Y(pos[1]));
    }
  });

  // 5. User Dot
  let xr, yr;
  if (PDR.active) { xr = PDR.pos.x; yr = PDR.pos.y; }
  else {
    const upos = NODE_POS[currentUser] || GRAPH.nodes[currentUser];
    if (upos) { xr = upos[0]; yr = upos[1]; } else { xr = null; }
  }
  
  if(xr !== null && xr !== undefined) {
    const ux = X(xr), uy = Y(yr);
    // Pulse
    const pulse = 1 + 0.4 * Math.sin(Date.now()/300);
    ctx.beginPath();
    ctx.arc(ux, uy, R(14) * pulse, 0, Math.PI*2);
    ctx.fillStyle = "rgba(66, 133, 244, 0.3)";
    ctx.fill();
    
    // Core Dot
    ctx.beginPath();
    ctx.arc(ux, uy, R(8), 0, Math.PI*2);
    ctx.fillStyle = "#4285F4"; ctx.fill();
    ctx.strokeStyle = "#FFFFFF"; ctx.lineWidth = R(3); ctx.stroke();
  }

  if(window.requestAnimationFrame) requestAnimationFrame(render);
}

"""
html = re.sub(r'function render\(\) \{.*?(?=function updateExitList\(\) \{)', render_code_new, html, flags=re.DOTALL)

# Add class to exit items for proper styling
html = html.replace('class="exit-item"', 'class="list-item"')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
