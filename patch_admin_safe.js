const fs = require('fs');

let html = fs.readFileSync('templates/admin.html', 'utf8');

const newCards = `
    <!-- IICCM CROWD VISION / HAZARD DETECTION -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">👁️ CCTV AI: Hazard Detection (Theme 1 & 3)</div>
      </div>
      <p style="font-size:13px; color:var(--muted); padding:0 20px;">Simulate abnormal behavior or fire detection. Triggering a hazard will instantly broadcast to all mobile users and force the AI to recalculate safer evacuation routes.</p>
      
      <div style="padding:0 20px; margin-top:15px;">
        <button class="btn btn-outline" onclick="clearHazards()" style="width:100%; border-color:var(--green); color:var(--green);">✅ Clear All Hazards (All Clear)</button>
      </div>
      
      <div class="hazard-list" id="hazardList" style="padding: 20px; display: flex; flex-direction: column; gap: 10px;">
        Loading nodes...
      </div>
    </div>
    
    <!-- IICCM CROWD E-HEALTH (IoT) -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">⌚ Crowd e-Health & IoT (Theme 2)</div>
      </div>
      <p style="font-size:13px; color:var(--muted); padding:0 20px;">Simulated real-time vital sign aggregation from Pilgrim Smartwatches.</p>
      
      <div style="display: flex; justify-content: space-between; padding: 20px; gap: 10px;">
        <div style="text-align: center; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; flex: 1;">
          <div style="font-size:12px; color:var(--muted)">Active Trackers</div>
          <div style="font-size: 24px; font-weight: bold; color: var(--blue);">1,204</div>
        </div>
        <div style="text-align: center; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; flex: 1;">
          <div style="font-size:12px; color:var(--muted)">Avg BPM</div>
          <div style="font-size: 24px; font-weight: bold; color: var(--green);">78</div>
        </div>
      </div>
      <div style="display: flex; justify-content: space-between; padding: 0 20px 20px 20px; gap: 10px;">
        <div style="text-align: center; background: rgba(239, 68, 68, 0.1); border: 1px solid var(--red); padding: 15px; border-radius: 8px; flex: 1;">
          <div style="font-size:12px; color:var(--muted)">SOS / Panic Alerts</div>
          <div style="font-size: 24px; font-weight: bold; color: var(--red);">0</div>
        </div>
        <div style="text-align: center; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; flex: 1;">
          <div style="font-size:12px; color:var(--muted)">Fall Detections</div>
          <div style="font-size: 24px; font-weight: bold; color: var(--green);">0</div>
        </div>
      </div>
    </div>
`;

// Find the grid container in admin.html and inject the cards
const gridPos = html.indexOf('<div class="grid">');
if (gridPos !== -1) {
    const insertPos = html.indexOf('>', gridPos) + 1;
    html = html.substring(0, insertPos) + newCards + html.substring(insertPos);
}

const jsLogic = `
  // === IICCM HAZARD LOGIC ===
  let activeHazards = [];
  async function refreshHazards() {
    try {
      const hazRes = await fetch('/api/hazards');
      const hazData = await hazRes.json();
      activeHazards = hazData.hazards || [];
      renderHazardList();
    } catch(e) {}
  }

  function renderHazardList() {
    const list = document.getElementById('hazardList');
    if (!list || !GRAPH) return;
    list.innerHTML = '';
    
    const nodes = Object.keys(GRAPH.nodes).filter(n => !(GRAPH.exit_nodes || []).includes(n)); 
    
    nodes.forEach(node => {
      const isHazard = activeHazards.includes(node);
      const name = node.replace(/_/g, " ");
      
      const row = document.createElement('div');
      row.style.display = 'flex';
      row.style.justifyContent = 'space-between';
      row.style.alignItems = 'center';
      row.style.background = isHazard ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255,255,255,0.05)';
      row.style.border = isHazard ? '1px solid var(--red)' : '1px solid transparent';
      row.style.padding = '10px 15px';
      row.style.borderRadius = '8px';
      
      row.innerHTML = \`
        <span>\${isHazard ? '🔥 ' : ''}<strong>\${name}</strong></span>
        <button class="btn" style="padding: 6px 12px; font-size: 12px; background: \${isHazard ? 'var(--green)' : 'var(--red)'}; color: white;" onclick="toggleHazard('\${node}', \${isHazard})">
          \${isHazard ? 'Resolve' : 'Simulate Fire'}
        </button>
      \`;
      list.appendChild(row);
    });
  }

  async function toggleHazard(node, isCurrentlyHazard) {
    const endpoint = isCurrentlyHazard ? '/api/hazards/remove' : '/api/hazards/add';
    await fetch(endpoint, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({node})
    });
    refreshHazards();
  }

  async function clearHazards() {
    await fetch('/api/hazards/clear', {method: 'POST'});
    refreshHazards();
  }
  
  setInterval(refreshHazards, 2000);
`;

// Insert the JS logic into the existing script tag
const scriptEnd = html.lastIndexOf('</script>');
if (scriptEnd !== -1) {
    html = html.substring(0, scriptEnd) + jsLogic + html.substring(scriptEnd);
}

// Modify init() or update() to call refreshHazards() initially
html = html.replace('updateDashboard();', 'updateDashboard(); refreshHazards();');

fs.writeFileSync('templates/admin.html', html, 'utf8');
