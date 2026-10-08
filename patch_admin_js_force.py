import re

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

# I will just append the toggleHazard and clearHazards functions to the very end of the <script> block, right before </script>

js_to_add = """
  let admin_hazards = {};
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
      if(fBtn) { fBtn.style.background = 'transparent'; fBtn.style.color = 'var(--red)'; }
      const dBtn = document.getElementById('haz-deb');
      if(dBtn) { dBtn.style.background = 'transparent'; dBtn.style.color = 'var(--amber)'; }
      addLog("✅ All hazards cleared. Paths restored.");
  }
"""

if "function toggleHazard" not in html:
    html = html.replace('</script>', js_to_add + '\n</script>', 1)

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)
