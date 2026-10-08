import re

# 1. PATCH app.py
with open('app.py', 'r', encoding='utf-8') as f:
    app = f.read()

broadcast_globals = '''# --- Voice Broadcast ---
LATEST_BROADCAST = {"id": 0, "message": ""}

'''
if 'LATEST_BROADCAST' not in app:
    app = app.replace('# --- Safe Check-ins ---', broadcast_globals + '# --- Safe Check-ins ---')

broadcast_endpoint = '''
@app.route("/api/broadcast", methods=["POST"])
def api_broadcast():
    global LATEST_BROADCAST
    data = request.json or {}
    msg = data.get("message", "").strip()
    if msg:
        import time
        LATEST_BROADCAST = {"id": int(time.time()), "message": msg}
    return jsonify({"success": True})

'''
if 'api_broadcast' not in app:
    app = app.replace('if __name__ == "__main__":', broadcast_endpoint + 'if __name__ == "__main__":')

if '"broadcast": LATEST_BROADCAST' not in app:
    app = app.replace(
        '"safe_list": SAFE_LIST\n    })',
        '"safe_list": SAFE_LIST,\n        "broadcast": LATEST_BROADCAST\n    })'
    )

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app)

# 2. PATCH index.html
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add global let lastBroadcastId = 0;
if 'let lastBroadcastId = 0;' not in html:
    html = html.replace('let SMOKE_LEVEL = "none";', 'let SMOKE_LEVEL = "none";\n  let lastBroadcastId = 0;')

broadcast_js = '''
      // Broadcast logic
      if (st.broadcast && st.broadcast.id > lastBroadcastId) {
        lastBroadcastId = st.broadcast.id;
        if (typeof speak === 'function') speak(st.broadcast.message);
        
        // Show a prominent alert toast
        const toast = document.getElementById("toast");
        if (toast) {
          toast.innerHTML = `<strong style="color:#facc15">&#128227; ADMIN BROADCAST:</strong><br>${st.broadcast.message}`;
          toast.className = "toast show";
          setTimeout(() => { toast.className = "toast"; }, 8000);
        }
      }
'''
if '// Broadcast logic' not in html:
    html = html.replace(
        '// Sync global alarm state',
        broadcast_js + '\n      // Sync global alarm state'
    )

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)


# 3. PATCH admin.html
with open('templates/admin.html', 'r', encoding='utf-8') as f:
    admin = f.read()

admin_broadcast_html = '''
      <!-- ADMIN MEGAPHONE -->
      <div style="margin-bottom:24px;">
        <div class="section-title" style="color:#f59e0b;">&#128227; Global Voice Megaphone</div>
        <div style="background:var(--panel); border:1px solid var(--border); padding:16px; border-radius:12px;">
          <p style="font-size:0.8rem; color:var(--muted); margin-bottom:12px;">Type a custom message and broadcast it to all users. Connected phones will speak the message out loud via Text-to-Speech.</p>
          <div style="display:flex; gap:10px;">
            <input type="text" id="broadcastMsg" placeholder="e.g. Please avoid the west corridor, fire spreading..." style="flex:1; padding:10px; border-radius:8px; border:1px solid var(--border); background:#0a0f1d; color:#fff; font-family:inherit;">
            <button class="mini-btn" style="border-color:#f59e0b; color:#f59e0b; background:transparent; padding:10px 18px; font-weight:700; cursor:pointer;" onclick="sendBroadcast()">&#128227; Broadcast</button>
          </div>
        </div>
      </div>
'''

if 'Global Voice Megaphone' not in admin:
    admin = admin.replace('      <!-- SMOKE SIMULATOR -->', admin_broadcast_html + '\n      <!-- SMOKE SIMULATOR -->')

admin_broadcast_js = '''
  // ===== VOICE BROADCAST =====
  async function sendBroadcast() {
    const input = document.getElementById('broadcastMsg');
    const msg = input.value.trim();
    if (!msg) return;
    
    await fetch('/api/broadcast', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ message: msg })
    });
    
    addLog('&#128227; Broadcast sent: ' + msg);
    input.value = '';
  }
'''

if 'function sendBroadcast' not in admin:
    admin = admin.replace('</script>', admin_broadcast_js + '\n  </script>', 1)

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin)

print("Patch applied.")
