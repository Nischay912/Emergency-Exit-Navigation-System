import re
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('function render(){')
if start == -1: start = html.find('function render() {')
end = html.find('function buildExitList(){')
if end == -1: end = html.find('function buildExitList() {')

if start != -1 and end != -1:
    new_render = """function render() {
  if(!ctx) return;
  const cw = canvas.width  / (window.devicePixelRatio||1);
  const ch = canvas.height / (window.devicePixelRatio||1);
  ctx.clearRect(0,0,cw,ch);
  
  // Background
  ctx.fillStyle = "#E8EAED";
  ctx.fillRect(0,0,cw,ch);
  
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
    const isBest = name === bestExit;
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
}

"""
    html = html[:start] + new_render + html[end:]
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
