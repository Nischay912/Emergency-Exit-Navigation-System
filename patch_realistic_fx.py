import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

hazard_pattern = r'/\* === HAZARDS === \*/.*?/\* === ROOM TEXTS === \*/'

new_hazard_draw = """/* === HAZARDS === */
    Object.keys(GLOBAL_HAZARDS).forEach(name => {
      const pos = NODE_POS[name] || (GRAPH ? GRAPH.nodes[name] : null);
      if (!pos) return;
      const type = GLOBAL_HAZARDS[name];
      const cx = X(pos[0]);
      const cy = Y(pos[1]);
      const t = Date.now();

      if (type === 'fire') {
          // Dynamic Fire Particle System
          // Pulsing base glow
          ctx.beginPath();
          ctx.arc(cx, cy, R(22), 0, Math.PI*2);
          ctx.fillStyle = `rgba(239, 68, 68, ${0.4 + 0.15*Math.sin(t/150)})`;
          ctx.fill();
          
          // Flames
          for (let i = 0; i < 12; i++) {
            const pt = (t + i * 150) / 800; 
            const yOffset = (pt % 1.5) * R(18);
            const life = 1 - (yOffset / R(18));
            const xOffset = Math.sin(pt * 8 + i * 2) * R(12);
            const rad = R(14) * Math.pow(life, 1.5);
            
            ctx.beginPath();
            ctx.arc(cx + xOffset, cy + R(10) - yOffset, rad, 0, Math.PI*2);
            if (i % 3 === 0) ctx.fillStyle = `rgba(250, 204, 21, ${life})`; // Yellow core
            else if (i % 3 === 1) ctx.fillStyle = `rgba(249, 115, 22, ${life})`; // Orange mid
            else ctx.fillStyle = `rgba(239, 68, 68, ${life * 0.8})`; // Red outer
            ctx.fill();
          }
      } else if (type === 'debris') {
          // Earthquake Rubble / Debris System
          // Pulsing dust cloud
          ctx.beginPath();
          ctx.arc(cx, cy, R(24), 0, Math.PI*2);
          ctx.fillStyle = `rgba(100, 116, 139, ${0.4 + 0.1*Math.sin(t/200)})`;
          ctx.fill();

          // Jagged Rocks
          const seed = pos[0] + pos[1]; 
          for(let i = 0; i < 7; i++) {
            const rx = cx + (((seed * i * 13.7) % 40) - 20) * (R(1)/2); // Scale properly
            const ry = cy + (((seed * i * 19.3) % 40) - 20) * (R(1)/2);
            const size = R(6) + (((seed * i) % 10) * R(0.5));
            
            ctx.beginPath();
            ctx.moveTo(rx, ry - size);
            ctx.lineTo(rx + size * 1.2, ry + size*0.3);
            ctx.lineTo(rx + size*0.5, ry + size);
            ctx.lineTo(rx - size, ry + size*0.8);
            ctx.closePath();
            ctx.fillStyle = i % 2 === 0 ? '#475569' : '#64748b'; // Slate gray colors
            ctx.fill();
            ctx.strokeStyle = '#1e293b';
            ctx.lineWidth = R(1);
            ctx.stroke();
          }
          
          // Hazard tape stripe across the debris
          ctx.beginPath();
          ctx.moveTo(cx - R(18), cy + R(10));
          ctx.lineTo(cx + R(18), cy - R(10));
          ctx.strokeStyle = '#F59E0B'; // Amber
          ctx.lineWidth = R(5);
          ctx.lineCap = "round";
          ctx.stroke();
          
          ctx.beginPath();
          ctx.moveTo(cx - R(18), cy + R(10));
          ctx.lineTo(cx + R(18), cy - R(10));
          ctx.strokeStyle = '#000000'; // Black stripes on tape
          ctx.setLineDash([R(5), R(5)]);
          ctx.lineWidth = R(5);
          ctx.stroke();
          ctx.setLineDash([]); // reset
      }
    });

    /* === ROOM TEXTS === */"""

html = re.sub(hazard_pattern, new_hazard_draw, html, flags=re.DOTALL)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
