import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# --- 1. CSS POLISH ---
# Fix white backgrounds in cards to use variables
html = html.replace('.loc-card { background: #FFFFFF;', '.loc-card { background: var(--panel);')
html = html.replace('.loc-select { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 8px; font-family: inherit; font-size: 14px; background: #F8F9FA; }', '.loc-select { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 8px; font-family: inherit; font-size: 14px; background: var(--bg); color: var(--text); }')
html = html.replace('.rec-card { background: var(--route-bg); border: 1px solid #c2e7ff; border-radius: 12px; padding: 16px; color: #174ea6; }', '.rec-card { background: var(--route-bg); border: 1px solid var(--blue); border-radius: 12px; padding: 16px; color: var(--text); }')
html = html.replace('.walk-btn { width: 100%; padding: 12px; background: white;', '.walk-btn { width: 100%; padding: 12px; background: var(--panel);')
html = html.replace('.nav-step-item { background: white;', '.nav-step-item { background: var(--panel);')
html = html.replace('.nav-bottom { padding: 16px; background: white;', '.nav-bottom { padding: 16px; background: var(--panel);')

# Add missing legend CSS
legend_css = """
.leg-row { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text); margin-bottom: 8px; font-weight: 500; }
.leg-dot { width: 12px; height: 12px; border-radius: 50%; box-shadow: 0 1px 2px rgba(0,0,0,0.2); }
.leg-sq { width: 14px; height: 4px; border-radius: 2px; box-shadow: 0 1px 2px rgba(0,0,0,0.2); }
.legend-sec { background: var(--panel); padding: 16px; border: 1px solid var(--border); border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
"""
if '.leg-row' not in html:
    html = html.replace('</style>', legend_css + '\n</style>')

# --- 2. RENDER NAV MINI MAP FIX (Auto-Zoom) ---
start_idx = html.find('function renderNavMiniMap(path) {')

if start_idx != -1:
    brace_start = html.find('{', start_idx)
    open_braces = 1
    i = brace_start + 1
    while i < len(html) and open_braces > 0:
        if html[i] == '{': open_braces += 1
        elif html[i] == '}': open_braces -= 1
        i += 1
    end_idx = i

    new_render_nav = """function renderNavMiniMap(path) {
  const nc = document.getElementById("navCanvas");
  const nwrap = nc.parentElement;
  nc.width = nwrap.clientWidth;
  nc.height = nwrap.clientHeight;
  const nctx = nc.getContext("2d");

  // Auto-Zoom: Calculate Bounding Box of Path
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

  // Calculate padding based on path dimensions
  let pW = maxX - minX;
  let pH = maxY - minY;
  if (pW < 200) pW = 200; // Minimum view width
  if (pH < 200) pH = 200; // Minimum view height
  
  const pad = Math.max(pW, pH) * 0.3; // 30% padding
  minX -= pad; maxX += pad;
  minY -= pad; maxY += pad;
  
  const viewW = maxX - minX;
  const viewH = maxY - minY;
  
  // Fit bounding box to canvas
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
  
  // Directional arrows on path
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
    path.forEach((name,i) => {
      const pos = NODE_POS[name]||GRAPH.nodes[name];
      if(!pos) return;
      const isStart = i===0, isEnd = i===path.length-1;
      nctx.beginPath();
      nctx.arc(NX(pos[0]),NY(pos[1]),NR(isStart||isEnd?12:7),0,Math.PI*2);
      nctx.fillStyle = isEnd?"#f59e0b":isStart?"#ef4444":"rgba(245,158,11,0.5)";
      nctx.shadowColor = isEnd?"#f59e0b":isStart?"#ef4444":"transparent";
      nctx.shadowBlur = NR(8);
      nctx.fill();
      nctx.shadowBlur=0;
      // Label
      nctx.fillStyle="#fff";
      nctx.font=`bold ${Math.max(NR(8), 10)}px Inter`;
      nctx.textAlign="center";
      nctx.textBaseline="middle";
      nctx.fillText(isStart?"YOU":isEnd?"🚨":"",NX(pos[0]),NY(pos[1]));
    });
  }

  NAV._miniCtx = nctx;
  NAV._miniCanvas = nc;
  NAV._miniPath = path || [];
  NAV._nsx = scale; NAV._nsy = scale;
  
  // Store the transform functions so pointer updates work correctly
  window._NX = NX;
  window._NY = NY;
  window._NR = NR;
}"""
    html = html[:start_idx] + new_render_nav + html[end_idx:]

# Update drawDemoPointerOnMiniMap to use the new transform scaling
ptr_start = html.find('function drawDemoPointerOnMiniMap(pos) {')
if ptr_start != -1:
    brace_start = html.find('{', ptr_start)
    open_braces = 1
    i = brace_start + 1
    while i < len(html) and open_braces > 0:
        if html[i] == '{': open_braces += 1
        elif html[i] == '}': open_braces -= 1
        i += 1
    ptr_end = i
    
    new_ptr = """function drawDemoPointerOnMiniMap(pos) {
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
  nctx.font = `bold ${Math.max(NR(10), 10)}px Inter`;
  nctx.fillText("YOU", x, y);
}"""
    html = html[:ptr_start] + new_ptr + html[ptr_end:]

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

