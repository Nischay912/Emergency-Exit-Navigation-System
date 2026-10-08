import re

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

hazard_html = """
      <!-- HAZARDS -->
      <div class="section-title" style="color:var(--red);">⚠️ Hazard Simulator (Fire / Blockades)</div>
      <div style="background:var(--panel); border:1px solid var(--border); padding:16px; border-radius:12px; margin-bottom:24px;">
        <p style="font-size:0.8rem; color:var(--muted); margin-bottom:12px;">Trigger a hazard to instantly block a path. The AI will immediately recalculate all user routes away from the danger zone!</p>
        <div style="display:flex; gap:12px; flex-wrap:wrap;">
          <button class="mini-btn" style="flex:none; padding:8px 16px; border-color:var(--red); color:var(--red); font-weight:bold; cursor:pointer;" onclick="triggerHazard('Intersection_Mid1', 'fire')">🔥 Fire at Mid-Hall 1</button>
          <button class="mini-btn" style="flex:none; padding:8px 16px; border-color:var(--amber); color:var(--amber); font-weight:bold; cursor:pointer;" onclick="triggerHazard('Corridor_East', 'debris')">🚧 Collapse at East Corridor</button>
          <button class="mini-btn" style="flex:none; padding:8px 16px; border-color:var(--green); color:var(--green); font-weight:bold; cursor:pointer;" onclick="triggerHazard(null, 'clear_all')">✅ Clear All Hazards</button>
        </div>
      </div>

      <!-- ROOMS -->"""

if "Hazard Simulator" not in html:
    html = html.replace('<!-- ROOMS -->', hazard_html)

js_hazard = """
  async function triggerHazard(node, type) {
    if (type === 'clear_all') {
      await fetch('/api/hazards', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({clear_all: true})});
      addLog("✅ All hazards cleared. Paths restored.");
    } else {
      await fetch('/api/hazards', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({node, type})});
      addLog(`🚨 HAZARD TRIGGERED: ${type.toUpperCase()} at ${node.replace(/_/g,' ')}!`);
    }
  }
"""

if "triggerHazard" not in html:
    html = html.replace('function addLog(msg){', js_hazard + '\n  function addLog(msg){')

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)
