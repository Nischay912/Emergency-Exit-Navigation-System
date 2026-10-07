import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix the nav mini map rendering to auto-zoom to path
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

  NAV._miniPath = path || [];
}"""
    html = html[:start_idx] + new_render_nav + html[end_idx:]

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
