import sys

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix fetchLayout 'const DW' to 'let DW'
html = html.replace('const DW=880,DH=580;', 'let DW=880,DH=580;')

# 2. Extract the full render() function by tracking braces
start_idx = html.find('function render(){')
if start_idx == -1:
    start_idx = html.find('function render() {')

if start_idx != -1:
    # Find the opening brace
    brace_start = html.find('{', start_idx)
    open_braces = 1
    i = brace_start + 1
    while i < len(html) and open_braces > 0:
        if html[i] == '{':
            open_braces += 1
        elif html[i] == '}':
            open_braces -= 1
        i += 1
    end_idx = i

    old_render = html[start_idx:end_idx]

    new_render = """function render() {
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
}"""

    html = html[:start_idx] + new_render + html[end_idx:]

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
