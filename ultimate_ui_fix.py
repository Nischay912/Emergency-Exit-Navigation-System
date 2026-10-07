import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# --- 1. Fix Missing Corridors/Rooms in Minimap ---
# Find renderNavMiniMap and replace it entirely with the PERFECT version
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

  const DW = 880, DH = 580;

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
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  nctx.fillStyle = isDark ? "#0A0F1D" : "#E8EAED"; // Slightly darker blue/gray for minimap bg
  nctx.fillRect(0,0,nc.width,nc.height);

  /* === CORRIDORS === */
  nctx.fillStyle = isDark ? "#1E293B" : "#FFFFFF"; // Dark corridors
  if (typeof CORRIDORS !== 'undefined') {
    CORRIDORS.forEach(c => {
      nctx.fillRect(NX(c.x), NY(c.y), c.w * scale, c.h * scale);
    });
  }

  /* === ROOMS === */
  if (typeof ROOMS !== 'undefined') {
    ROOMS.forEach(r => {
      const isStart = path && path.length > 0 && r.id === path[0];
      const isEnd = path && path.length > 0 && r.id === path[path.length-1];
      const onPath = path && path.includes(r.id);
      
      nctx.beginPath();
      nctx.rect(NX(r.x), NY(r.y), r.w * scale, r.h * scale);
      
      nctx.fillStyle = isStart ? (isDark?"#3b1414":"#FCE8E6") : onPath ? (isDark?"#0f2240":"#E8F0FE") : (isDark?"#151C2A":"#F1F3F4");
      nctx.fill();
      nctx.strokeStyle = isStart ? (isDark?"#F28B82":"#EA4335") : onPath ? (isDark?"#8AB4F8":"#1A73E8") : (isDark?"#334155":"#DADCE0");
      nctx.lineWidth = NR(2);
      nctx.stroke();
    });
  }

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
      nctx.strokeStyle = onP ? (isDark?"#f59e0b":"#f59e0b") : (isDark?"#334155":"#DADCE0");
      nctx.lineWidth = onP ? NR(5) : NR(1.5);
      nctx.setLineDash(onP?[]:[NR(3),NR(4)]);
      nctx.stroke();
    });
  }
  
  nctx.setLineDash([]);
  
  // Nodes
  if (path) {
    path.forEach((name,i) => {
      const pos = NODE_POS[name]||GRAPH.nodes[name];
      if(!pos) return;
      const isStart = i===0, isEnd = i===path.length-1;
      nctx.beginPath();
      nctx.arc(NX(pos[0]),NY(pos[1]),NR(isStart||isEnd?12:7),0,Math.PI*2);
      nctx.fillStyle = isEnd?"#f59e0b":isStart?"#ef4444":"rgba(245,158,11,0.5)";
      nctx.fill();
      // Label
      nctx.fillStyle="#fff";
      nctx.font=`bold ${Math.max(NR(8), 10)}px Inter`;
      nctx.textAlign="center";
      nctx.textBaseline="middle";
      nctx.fillText(isStart?"YOU":isEnd?"EXIT":"",NX(pos[0]),NY(pos[1]));
    });
  }

  NAV._miniCtx = nctx;
  NAV._miniCanvas = nc;
  NAV._miniPath = path || [];
  
  // Store the transform functions so pointer updates work correctly
  window._NX = NX;
  window._NY = NY;
  window._NR = NR;
}"""
    html = html[:start_idx] + new_render_nav + html[end_idx:]

# --- 2. Fix CSS Colors for Navigate Button, Close Button, and Exit Row ---
css_fixes = """
.nav-trigger { width: 100%; padding: 14px; background: var(--blue); color: var(--panel); border: none; border-radius: 24px; font-size: 15px; font-weight: 500; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.3); transition: 0.2s; }
.nav-close-btn { flex: 1; background: var(--panel); color: var(--text); border: 1px solid var(--border); padding: 14px; border-radius: 12px; font-weight: 500; cursor: pointer; }
.exit-row.best { background: var(--route-bg); border-radius: 8px; padding-left: 8px; padding-right: 8px; border-bottom: none; }
:root[data-theme="dark"] .nav-trigger { color: #0A0F1D; font-weight: 700; }
"""
html = html.replace('.nav-trigger { width: 100%; padding: 14px; background: var(--blue); color: white;', '.nav-trigger { width: 100%; padding: 14px; background: var(--blue); color: var(--bg);')
html = html.replace('.nav-close-btn { flex: 1; background: #F1F3F4; color: var(--text); border: none;', '.nav-close-btn { flex: 1; background: var(--panel); color: var(--text); border: 2px solid var(--border);')
html = html.replace('.exit-row.best { background: #E8F0FE;', '.exit-row.best { background: var(--route-bg);')


# --- 3. Fix the Sun / Moon Theme Toggle Emoji ---
# Instead of hard-to-see characters, use proper emoji that look good in both themes
html = html.replace("next === 'dark' ? '&#9728;' : '&#127769;'", "next === 'dark' ? '☀️' : '🌙'")
html = html.replace('<span id="themeIcon">&#127769;</span>', '<span id="themeIcon">🌙</span>')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
