import re

# =================================================================
# STEP 1: app.py — Add SAFE_LIST global + endpoint
# =================================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app = f.read()

if 'SAFE_LIST = []' not in app:
    app = app.replace('# --- Smoke Simulation ---', '# --- Safe Check-ins ---\nSAFE_LIST = []\n\n# --- Smoke Simulation ---')

safe_endpoint = '''
@app.route("/api/safe", methods=["GET", "POST"])
def api_safe():
    global SAFE_LIST
    if request.method == "POST":
        data = request.json or {}
        if data.get("action") == "clear":
            SAFE_LIST = []
        else:
            import time
            entry = {
                "name": data.get("name", "Unknown User"),
                "time": time.strftime("%H:%M:%S")
            }
            # Avoid exact duplicates
            if not any(s["name"] == entry["name"] for s in SAFE_LIST):
                SAFE_LIST.append(entry)
        return jsonify({"success": True})
    return jsonify(SAFE_LIST)

'''

if 'api_safe' not in app:
    app = app.replace('if __name__ == "__main__":', safe_endpoint + 'if __name__ == "__main__":')

if '"safe_list": SAFE_LIST' not in app:
    app = app.replace(
        '"smoke_level": SMOKE_LEVEL\n    })',
        '"smoke_level": SMOKE_LEVEL,\n        "safe_list": SAFE_LIST\n    })'
    )

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app)
print("app.py patched")

# =================================================================
# STEP 2: index.html — Add Safe Check-in Button
# =================================================================
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

safe_css = """
  /* ===== SAFE BUTTON ===== */
  .safe-btn {
    width: 100%; margin-top: 10px; padding: 14px;
    background: linear-gradient(135deg, #14532d, #166534);
    border: 2px solid #22c55e; border-radius: 12px;
    color: #fff; font-size: 1rem; font-weight: 800;
    cursor: pointer; letter-spacing: 0.05em; font-family: inherit;
  }
  .safe-btn:hover { background: linear-gradient(135deg, #166534, #15803d); }
  .safe-badge-confirmed {
    display: none; margin-top: 10px; padding: 12px;
    background: rgba(34,197,94,0.15); border: 1px solid #22c55e;
    border-radius: 12px; color: #86efac; font-size: 0.9rem;
    font-weight: 700; text-align: center;
  }
"""

if '.safe-btn' not in html:
    html = html.replace('</style>', safe_css + '\n  </style>')

safe_html = """
        <!-- SAFE CHECK-IN BUTTON -->
        <button class="safe-btn" id="safeBtn" onclick="markSafe()">
          &#9989; I'm Safe &mdash; Check-in
        </button>
        <div class="safe-badge-confirmed" id="safeBadgeConfirmed">
          &#9989; You are marked Safe!
        </div>
"""

# Insert right after the SOS badge
if 'safeBtn' not in html:
    html = html.replace(
        '<div class="sos-sent-badge" id="sosBadge">\n          &#128681; SOS Sent! Rescue team notified. Stay calm &amp; stay put.\n        </div>',
        '<div class="sos-sent-badge" id="sosBadge">\n          &#128681; SOS Sent! Rescue team notified. Stay calm &amp; stay put.\n        </div>\n' + safe_html
    )

safe_js = """
  // ===== SAFE CHECK-IN =====
  let isMarkedSafe = false;
  async function markSafe() {
    if (isMarkedSafe) return;
    const name = prompt("Enter your Name or ID to check-in at the Safe Assembly Point:");
    if (!name || name.trim() === "") return;
    
    try {
      await fetch('/api/safe', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name: name.trim() })
      });
      
      isMarkedSafe = true;
      document.getElementById('safeBtn').style.display = 'none';
      document.getElementById('safeBadgeConfirmed').style.display = 'block';
      
      // Auto-cancel SOS if they were trapped but made it out
      if (sosSent && mySosId) {
        await fetch('/api/sos', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ action: 'clear', id: mySosId })
        });
        resetSOSButton();
      }

      if (typeof speak === 'function') speak('You have been accounted for at the safe assembly point.');
      showToast('&#9989; Checked in successfully!');
    } catch(e) {
      showToast('Error connecting to server.');
    }
  }

"""

if 'function markSafe' not in html:
    html = html.replace('  // ===== SOS PANIC BUTTON =====', safe_js + '  // ===== SOS PANIC BUTTON =====')

# In pollSOS, let's also optionally auto-reset the safe button if admin clears the list, but it's fine as is.
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html patched")

# =================================================================
# STEP 3: admin.html — Add Safe Check-in Panel
# =================================================================
with open('templates/admin.html', 'r', encoding='utf-8') as f:
    admin = f.read()

safe_admin_html = """
      <!-- SAFE CHECK-INS -->
      <div id="safeSection" style="margin-bottom:24px;">
        <div class="section-title" style="color:var(--green);">&#9989; Safe Assembly Check-ins</div>
        <div style="background:var(--panel); border:1px solid var(--border); padding:16px; border-radius:12px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; border-bottom:1px solid var(--border); padding-bottom:10px;">
            <div style="font-size:0.95rem; color:var(--text);">People Accounted For: <strong id="safeCountTxt" style="color:var(--green); font-size:1.2rem; margin-left:8px;">0</strong></div>
            <button class="mini-btn" style="border-color:var(--border); color:var(--muted); background:transparent; padding:6px 12px; cursor:pointer;" onclick="clearSafeList()">Reset List</button>
          </div>
          <div id="safeList" style="max-height:200px; overflow-y:auto; font-size:0.9rem; color:var(--text);">
            <div style="color:var(--muted); font-size:0.85rem;">No check-ins yet.</div>
          </div>
        </div>
      </div>

"""

# Insert right after SOS ALERTS
if 'id="safeSection"' not in admin:
    admin = admin.replace(
        '      <!-- SMOKE SIMULATOR -->',
        safe_admin_html + '      <!-- SMOKE SIMULATOR -->'
    )

safe_admin_js = """
  // ===== SAFE CHECK-INS =====
  let admin_safe_list = [];
  async function refreshSafe() {
    try {
      const r = await fetch('/api/safe');
      admin_safe_list = await r.json();
      renderSafeList();
    } catch(e) {}
  }

  function renderSafeList() {
    const list = document.getElementById('safeList');
    const count = document.getElementById('safeCountTxt');
    if (!list || !count) return;

    count.textContent = admin_safe_list.length;

    if (admin_safe_list.length === 0) {
      list.innerHTML = '<div style="color:var(--muted); font-size:0.85rem;">No check-ins yet.</div>';
      return;
    }

    list.innerHTML = admin_safe_list.map(s => `
      <div style="padding:10px 8px; border-bottom:1px solid rgba(255,255,255,0.05); display:flex; justify-content:space-between; align-items:center;">
        <div>
          <span style="color:var(--green); margin-right:8px;">&#9989;</span> 
          <strong>${s.name}</strong>
        </div>
        <div style="color:var(--muted); font-size:0.8rem;">${s.time}</div>
      </div>
    `).reverse().join(''); // show newest at top
  }

  async function clearSafeList() {
    if(!confirm("Are you sure you want to clear the assembly point ledger?")) return;
    await fetch('/api/safe', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ action: 'clear' })
    });
    addLog('&#9989; Safe Assembly ledger reset');
    refreshSafe();
  }

  setInterval(refreshSafe, 3000);
  refreshSafe();
"""

if 'function refreshSafe' not in admin:
    admin = admin.replace('</script>', safe_admin_js + '\n  </script>', 1)

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin)
print("admin.html patched")
print("Done!")
