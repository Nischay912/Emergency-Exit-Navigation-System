import re

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the buttons
old_buttons = """<button class="mini-btn" style="flex:none; padding:8px 16px; border-color:var(--red); color:var(--red); font-weight:bold; cursor:pointer;" onclick="triggerHazard('Intersection_Mid1', 'fire')">🔥 Fire near Staff Lounge (Left)</button>
          <button class="mini-btn" style="flex:none; padding:8px 16px; border-color:var(--amber); color:var(--amber); font-weight:bold; cursor:pointer;" onclick="triggerHazard('Corridor_East', 'debris')">🚧 Blockade at East Hallway</button>
          <button class="mini-btn" style="flex:none; padding:8px 16px; border-color:var(--green); color:var(--green); font-weight:bold; cursor:pointer;" onclick="triggerHazard(null, 'clear_all')">✅ Clear All Hazards</button>"""

new_buttons = """<button id="haz-fire" class="mini-btn" style="flex:none; padding:8px 16px; border-color:var(--red); color:var(--red); font-weight:bold; cursor:pointer; background:transparent;" onclick="toggleHazard('Intersection_Mid1', 'fire', 'haz-fire', 'var(--red)')">🔥 Fire near Staff Lounge (Left)</button>
          <button id="haz-deb" class="mini-btn" style="flex:none; padding:8px 16px; border-color:var(--amber); color:var(--amber); font-weight:bold; cursor:pointer; background:transparent;" onclick="toggleHazard('Corridor_East', 'debris', 'haz-deb', 'var(--amber)')">🚧 Blockade at East Hallway</button>
          <button class="mini-btn" style="flex:none; padding:8px 16px; border-color:var(--green); color:var(--green); font-weight:bold; cursor:pointer; background:transparent;" onclick="clearHazards()">✅ Clear All Hazards</button>"""

html = html.replace(old_buttons, new_buttons)

# Replace the JS function
old_js = """async function triggerHazard(node, type) {
    if (type === 'clear_all') {
      await fetch('/api/hazards', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({clear_all: true})});
      addLog("✅ All hazards cleared. Paths restored.");
    } else {
      await fetch('/api/hazards', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({node, type})});
      addLog(`🚨 HAZARD TRIGGERED: ${type.toUpperCase()} at ${node.replace(/_/g,' ')}!`);
    }
  }"""

new_js = """let admin_hazards = {};
  async function toggleHazard(node, type, btnId, color) {
    const btn = document.getElementById(btnId);
    if (admin_hazards[node] === type) {
        await fetch('/api/hazards', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({node: node, type: 'clear'})});
        admin_hazards[node] = null;
        btn.style.background = 'transparent';
        btn.style.color = color;
        addLog(`✅ Hazard Cleared at ${node.replace(/_/g,' ')}`);
    } else {
        await fetch('/api/hazards', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({node: node, type: type})});
        admin_hazards[node] = type;
        btn.style.background = color;
        btn.style.color = 'white';
        addLog(`🚨 HAZARD TRIGGERED: ${type.toUpperCase()} at ${node.replace(/_/g,' ')}!`);
    }
  }
  
  async function clearHazards() {
      await fetch('/api/hazards', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({clear_all: true})});
      admin_hazards = {};
      const fBtn = document.getElementById('haz-fire');
      fBtn.style.background = 'transparent'; fBtn.style.color = 'var(--red)';
      const dBtn = document.getElementById('haz-deb');
      dBtn.style.background = 'transparent'; dBtn.style.color = 'var(--amber)';
      addLog("✅ All hazards cleared. Paths restored.");
  }"""

html = html.replace(old_js, new_js)

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)
