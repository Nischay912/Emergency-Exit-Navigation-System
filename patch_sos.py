import re

# =========================================================
# STEP 1: Patch app.py - Add SOS_ALERTS global + endpoint
# =========================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

# Add SOS_ALERTS global after HAZARDS
if 'SOS_ALERTS = []' not in app_code:
    app_code = app_code.replace('HAZARDS = {}', 'HAZARDS = {}\n\n# --- SOS Alerts ---\nSOS_ALERTS = []')

# Add SOS endpoint before "if __name__"
sos_endpoint = '''
@app.route("/api/sos", methods=["GET", "POST"])
def api_sos():
    global SOS_ALERTS
    if request.method == "POST":
        data = request.json or {}
        if data.get("action") == "clear":
            alert_id = data.get("id")
            SOS_ALERTS = [a for a in SOS_ALERTS if a["id"] != alert_id]
        elif data.get("action") == "clear_all":
            SOS_ALERTS = []
        else:
            import time, uuid
            alert = {
                "id": str(uuid.uuid4())[:8],
                "room": data.get("room", "Unknown"),
                "node": data.get("node", ""),
                "message": data.get("message", "Help! I am trapped!"),
                "time": time.strftime("%H:%M:%S"),
            }
            SOS_ALERTS.append(alert)
        return jsonify({"success": True})
    return jsonify(SOS_ALERTS)

'''

if 'api_sos' not in app_code:
    app_code = app_code.replace('if __name__ == "__main__":', sos_endpoint + 'if __name__ == "__main__":')

# Also expose SOS in /api/status
app_code = app_code.replace(
    '"hazards": HAZARDS\n    })',
    '"hazards": HAZARDS,\n        "sos_alerts": SOS_ALERTS\n    })'
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

print("app.py patched OK")

# =========================================================
# STEP 2: Patch index.html - SOS Button + Beacon rendering
# =========================================================
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 2a. Add SOS CSS inside <style>
sos_css = """
  /* ===== SOS BUTTON ===== */
  .sos-btn {
    width: 100%;
    margin-top: 16px;
    padding: 14px;
    background: linear-gradient(135deg, #7f1d1d, #991b1b);
    border: 2px solid #ef4444;
    border-radius: 12px;
    color: #fff;
    font-size: 1rem;
    font-weight: 800;
    cursor: pointer;
    letter-spacing: 0.05em;
    position: relative;
    overflow: hidden;
    font-family: inherit;
  }
  .sos-btn.active {
    background: linear-gradient(135deg, #991b1b, #b91c1c);
    animation: sos-pulse 1s infinite;
  }
  @keyframes sos-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.7); }
    50%       { box-shadow: 0 0 0 12px rgba(239,68,68,0); }
  }
  .sos-sent-badge {
    display: none;
    margin-top: 8px;
    padding: 8px 12px;
    background: rgba(239,68,68,0.15);
    border: 1px solid #ef4444;
    border-radius: 8px;
    color: #fca5a5;
    font-size: 0.78rem;
    font-weight: 700;
    text-align: center;
  }
"""

if '.sos-btn' not in html:
    html = html.replace('</style>', sos_css + '\n  </style>')

# 2b. Add SOS button HTML - insert after the exit list section
sos_html = """
      <!-- SOS PANIC BUTTON -->
      <div style="margin-top:16px; border-top: 1px solid var(--border); padding-top:16px;">
        <button class="sos-btn" id="sosBtn" onclick="sendSOS()">
          &#128682; SOS — I'm Trapped!
        </button>
        <div class="sos-sent-badge" id="sosBadge">
          &#128681; SOS Sent! Rescue team notified. Stay calm &amp; stay put.
        </div>
      </div>
"""

# Insert before the exit list closing
if 'sosBtn' not in html:
    html = html.replace('<div id="exitList"></div>', '<div id="exitList"></div>' + sos_html)

# 2c. Add SOS JS - store active SOS and polling
sos_js = """
  // ===== SOS PANIC BUTTON =====
  let sosSent = false;

  async function sendSOS() {
    const btn = document.getElementById('sosBtn');
    const badge = document.getElementById('sosBadge');

    if (sosSent) {
      // Second press = cancel SOS
      sosSent = false;
      btn.classList.remove('active');
      btn.innerHTML = '&#128682; SOS — I\\'m Trapped!';
      badge.style.display = 'none';
      // We don't auto-cancel from server — admin clears it
      showToast('SOS cancelled locally. Contact admin to clear.');
      return;
    }

    sosSent = true;
    const roomName = currentUser.replace(/_/g, ' ');
    try {
      await fetch('/api/sos', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ room: roomName, node: currentUser, message: 'HELP! I am trapped at ' + roomName })
      });
    } catch(e) {}

    btn.classList.add('active');
    btn.innerHTML = '&#128681; SOS ACTIVE — Tap to Cancel';
    badge.style.display = 'block';

    // Voice alert
    if (typeof speak === 'function') speak('S O S sent! Help is on the way. Stay calm and stay put.');
    showToast('🆘 SOS sent to Admin! Stay put.', 5000);
  }

  // Track SOS alerts from server for beacon rendering
  let SOS_BEACON_NODES = [];
  async function pollSOS() {
    try {
      const r = await fetch('/api/status');
      const data = await r.json();
      SOS_BEACON_NODES = (data.sos_alerts || []).map(a => a.node);
    } catch(e) {}
  }
  setInterval(pollSOS, 3000);
"""

if 'function sendSOS' not in html:
    html = html.replace('</script>', sos_js + '\n  </script>', 1)

# 2d. Add SOS Beacon rendering in the render loop - AFTER HAZARDS, BEFORE ROOM TEXTS
sos_beacon_draw = """
    /* === SOS BEACONS === */
    SOS_BEACON_NODES.forEach(nodeName => {
      const pos = NODE_POS[nodeName] || (GRAPH ? GRAPH.nodes[nodeName] : null);
      if (!pos) return;
      const cx = X(pos[0]), cy = Y(pos[1]);
      const t = Date.now();

      // Animated radar rings
      for (let ring = 0; ring < 3; ring++) {
        const phase = ((t / 800) + ring * 0.33) % 1;
        const ringR = R(8) + phase * R(28);
        const alpha = (1 - phase) * 0.7;
        ctx.beginPath();
        ctx.arc(cx, cy, ringR, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(239, 68, 68, ${alpha})`;
        ctx.lineWidth = R(2.5);
        ctx.stroke();
      }

      // Solid red center dot
      ctx.beginPath();
      ctx.arc(cx, cy, R(9), 0, Math.PI * 2);
      ctx.fillStyle = '#ef4444';
      ctx.shadowColor = '#ef4444';
      ctx.shadowBlur = R(15);
      ctx.fill();
      ctx.shadowBlur = 0;

      // SOS label
      ctx.font = `bold ${Math.max(R(8), 9)}px Inter`;
      ctx.fillStyle = '#ffffff';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('SOS', cx, cy);
    });

    /* === ROOM TEXTS === */"""

if 'SOS BEACONS ===' not in html:
    html = html.replace('/* === ROOM TEXTS === */', sos_beacon_draw)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html patched OK")

# =========================================================
# STEP 3: Patch admin.html - Live SOS Alert Panel
# =========================================================
with open('templates/admin.html', 'r', encoding='utf-8') as f:
    admin = f.read()

# 3a. Add SOS CSS
admin_sos_css = """
  .sos-alert-card {
    display: flex; align-items: center; justify-content: space-between;
    background: rgba(239, 68, 68, 0.12);
    border: 1px solid var(--red);
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 10px;
    animation: sos-glow 1.5s ease-in-out infinite;
  }
  @keyframes sos-glow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.3); }
    50%       { box-shadow: 0 0 10px 4px rgba(239,68,68,0.2); }
  }
  .sos-alert-room { font-size: 1rem; font-weight: 800; color: #fca5a5; }
  .sos-alert-time { font-size: 0.75rem; color: var(--muted); margin-top: 2px; }
  .sos-rescue-btn {
    background: transparent; border: 1px solid var(--green);
    color: var(--green); padding: 6px 12px; border-radius: 8px;
    font-size: 0.78rem; font-weight: 700; cursor: pointer; white-space: nowrap;
    font-family: inherit;
  }
  .sos-rescue-btn:hover { background: rgba(34, 197, 94, 0.15); }
  #sosSection { margin-bottom: 24px; }
  #sosEmpty { font-size: 0.82rem; color: var(--muted); padding: 10px 0; }
"""

if '.sos-alert-card' not in admin:
    admin = admin.replace('</style>', admin_sos_css + '\n  </style>')

# 3b. Add SOS section HTML - insert before Hazard Simulator
sos_section_html = """
      <!-- SOS ALERTS -->
      <div id="sosSection">
        <div class="section-title" style="color:var(--red);">&#128682; Live SOS Alerts</div>
        <div id="sosList">
          <div id="sosEmpty" style="font-size:0.82rem; color:var(--muted); padding:10px 0;">No active SOS signals. All clear &#9989;</div>
        </div>
      </div>

"""

if 'id="sosSection"' not in admin:
    admin = admin.replace('<div class="section-title" style="color:var(--red);">',
                          sos_section_html + '<div class="section-title" style="color:var(--red);">', 1)

# 3c. Add admin SOS JS
admin_sos_js = """
  // ===== ADMIN SOS PANEL =====
  let admin_sos_alerts = [];

  async function refreshSOS() {
    try {
      const r = await fetch('/api/sos');
      const alerts = await r.json();
      admin_sos_alerts = alerts;
      renderSOSList();
    } catch(e) {}
  }

  function renderSOSList() {
    const list = document.getElementById('sosList');
    const empty = document.getElementById('sosEmpty');
    if (!list) return;

    if (admin_sos_alerts.length === 0) {
      list.innerHTML = '<div id="sosEmpty" style="font-size:0.82rem; color:var(--muted); padding:10px 0;">No active SOS signals. All clear &#9989;</div>';
      return;
    }

    list.innerHTML = admin_sos_alerts.map(a => `
      <div class="sos-alert-card">
        <div>
          <div class="sos-alert-room">&#128681; ${a.room}</div>
          <div class="sos-alert-time">SOS at ${a.time} &nbsp;|&nbsp; ID: ${a.id}</div>
        </div>
        <button class="sos-rescue-btn" onclick="markRescued('${a.id}')">&#9989; Mark Rescued</button>
      </div>
    `).join('');
  }

  async function markRescued(alertId) {
    await fetch('/api/sos', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ action: 'clear', id: alertId })
    });
    addLog('&#9989; SOS cleared — person rescued at ID: ' + alertId);
    refreshSOS();
  }

  // Poll SOS every 3 seconds
  setInterval(refreshSOS, 3000);
  refreshSOS();
"""

if 'function refreshSOS' not in admin:
    admin = admin.replace('</script>', admin_sos_js + '\n  </script>', 1)

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin)

print("admin.html patched OK")
print("All done!")
