import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix buildAdj logic
adj_pattern = r'GRAPH\.edges\.forEach\(\(\[u,v,d\]\)=>\{[^\}]+\}\);'

new_adj_logic = """GRAPH.edges.forEach(([u,v,d])=>{
      let mult_u = CROWD_MULT[countToLevel(getNodeCount(u))] || 1;
      let mult_v = CROWD_MULT[countToLevel(getNodeCount(v))] || 1;
      
      if (GLOBAL_HAZARDS[u] || GLOBAL_HAZARDS[v]) {
          mult_u = 999999;
          mult_v = 999999;
      }
      
      adj[u].push([v,d*mult_v]);
      adj[v].push([u,d*mult_u]);
    });"""

html = re.sub(adj_pattern, new_adj_logic, html)

# 2. Fix Emojis in Render
hazard_pattern = r'/\* === HAZARDS === \*/.*?/\* === ROOM TEXTS === \*/'

new_hazard_draw = """/* === HAZARDS === */
    Object.keys(GLOBAL_HAZARDS).forEach(name => {
      const pos = NODE_POS[name] || (GRAPH ? GRAPH.nodes[name] : null);
      if (!pos) return;
      const type = GLOBAL_HAZARDS[name];
      ctx.beginPath();
      ctx.arc(X(pos[0]), Y(pos[1]), R(16), 0, Math.PI*2);
      ctx.fillStyle = type === 'fire' ? 'rgba(239,68,68,0.9)' : 'rgba(245,158,11,0.9)';
      ctx.fill();
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = R(2);
      ctx.stroke();
      
      ctx.font = `bold ${Math.max(R(16), 14)}px sans-serif`;
      ctx.fillStyle = '#FFFFFF';
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      
      const jump = Math.sin(Date.now() / 150) * R(4);
      // F for Fire, X for Blockade
      ctx.fillText(type === 'fire' ? 'F' : 'X', X(pos[0]), Y(pos[1]) + jump);
    });

    /* === ROOM TEXTS === */"""

html = re.sub(hazard_pattern, new_hazard_draw, html, flags=re.DOTALL)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
