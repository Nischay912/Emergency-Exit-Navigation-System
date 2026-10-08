import re

# =========================================================
# Fix index.html - Full SOS JS replacement
# =========================================================
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_sos_js = """  // ===== SOS PANIC BUTTON =====
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
  setInterval(pollSOS, 3000);"""

new_sos_js = """  // ===== SOS PANIC BUTTON =====
  let sosSent = false;
  let mySosId = null; // track this user's SOS ID on server

  async function sendSOS() {
    const btn = document.getElementById('sosBtn');
    const badge = document.getElementById('sosBadge');

    if (sosSent) {
      // Cancel - remove from server using our ID
      if (mySosId) {
        try {
          await fetch('/api/sos', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ action: 'clear', id: mySosId })
          });
        } catch(e) {}
      }
      resetSOSButton();
      showToast('SOS cancelled.');
      return;
    }

    // Prevent duplicate SOS
    if (mySosId) { showToast('SOS already active!'); return; }

    const roomName = currentUser.replace(/_/g, ' ');
    try {
      const r = await fetch('/api/sos', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ room: roomName, node: currentUser, message: 'HELP! I am trapped at ' + roomName })
      });
      const data = await r.json();
      mySosId = data.alert_id || null;
    } catch(e) {}

    sosSent = true;
    btn.classList.add('active');
    btn.innerHTML = '&#128681; SOS ACTIVE &mdash; Tap to Cancel';
    badge.style.display = 'block';

    if (typeof speak === 'function') speak('S O S sent! Help is on the way. Stay calm and stay put.');
    showToast('SOS sent to Admin! Stay put.', 5000);
  }

  function resetSOSButton() {
    sosSent = false;
    mySosId = null;
    const btn = document.getElementById('sosBtn');
    const badge = document.getElementById('sosBadge');
    if (btn) { btn.classList.remove('active'); btn.innerHTML = '&#128682; SOS &mdash; I\\'m Trapped!'; }
    if (badge) badge.style.display = 'none';
  }

  // Track SOS alerts from server for beacon rendering + auto-reset
  let SOS_BEACON_NODES = [];
  async function pollSOS() {
    try {
      const r = await fetch('/api/sos');
      const alerts = await r.json();
      SOS_BEACON_NODES = alerts.map(a => a.node);

      // Auto-reset user's button if admin cleared their SOS
      if (mySosId && !alerts.find(a => a.id === mySosId)) {
        resetSOSButton();
        showToast('Rescue team confirmed! You are safe.');
      }
    } catch(e) {}
  }
  setInterval(pollSOS, 3000);"""

html = html.replace(old_sos_js, new_sos_js)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html fixed")

# =========================================================
# Fix app.py - return alert_id in POST response
# =========================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

old_sos_endpoint = '''        else:
            import time, uuid
            alert = {
                "id": str(uuid.uuid4())[:8],
                "room": data.get("room", "Unknown"),
                "node": data.get("node", ""),
                "message": data.get("message", "Help! I am trapped!"),
                "time": time.strftime("%H:%M:%S"),
            }
            SOS_ALERTS.append(alert)
        return jsonify({"success": True})'''

new_sos_endpoint = '''        else:
            import time, uuid
            alert_id = str(uuid.uuid4())[:8]
            alert = {
                "id": alert_id,
                "room": data.get("room", "Unknown"),
                "node": data.get("node", ""),
                "message": data.get("message", "Help! I am trapped!"),
                "time": time.strftime("%H:%M:%S"),
            }
            SOS_ALERTS.append(alert)
            return jsonify({"success": True, "alert_id": alert_id})
        return jsonify({"success": True})'''

app_code = app_code.replace(old_sos_endpoint, new_sos_endpoint)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

print("app.py fixed")
print("Done!")
