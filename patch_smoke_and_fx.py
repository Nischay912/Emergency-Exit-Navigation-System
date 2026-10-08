import re

# =================================================================
# STEP 1: app.py — Add SMOKE global + endpoint + expose in /status
# =================================================================
with open('app.py', 'r', encoding='utf-8') as f:
    app = f.read()

# Add global
if 'SMOKE_LEVEL' not in app:
    app = app.replace('# --- SOS Alerts ---', '# --- Smoke Simulation ---\nSMOKE_LEVEL = "none"  # "none" | "light" | "heavy" | "blackout"\n\n# --- SOS Alerts ---')

# Add endpoint before if __name__
smoke_endpoint = '''
@app.route("/api/smoke", methods=["GET", "POST"])
def api_smoke():
    global SMOKE_LEVEL
    if request.method == "POST":
        data = request.json or {}
        SMOKE_LEVEL = data.get("level", "none")
        return jsonify({"success": True, "level": SMOKE_LEVEL})
    return jsonify({"level": SMOKE_LEVEL})

'''
if 'api_smoke' not in app:
    app = app.replace('if __name__ == "__main__":', smoke_endpoint + 'if __name__ == "__main__":')

# Expose in /api/status
app = app.replace(
    '"sos_alerts": SOS_ALERTS\n    })',
    '"sos_alerts": SOS_ALERTS,\n        "smoke_level": SMOKE_LEVEL\n    })'
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app)
print("app.py done")

# =================================================================
# STEP 2: index.html — Replace HAZARDS block + add Smoke
# =================================================================
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# -- 2a. Replace the full HAZARDS render block with upgraded version
old_hazards_block_start = '    /* === HAZARDS === */'
old_hazards_block_end = '    /* === SOS BEACONS === */'

new_hazards = """    /* === HAZARDS === */
    Object.keys(GLOBAL_HAZARDS).forEach(name => {
      const pos = NODE_POS[name] || (GRAPH ? GRAPH.nodes[name] : null);
      if (!pos) return;
      const type = GLOBAL_HAZARDS[name];
      const cx = X(pos[0]), cy = Y(pos[1]);
      const t = Date.now();

      if (type === 'fire') {
        // === FIRE: layered radial glow + rising flame particles ===
        // 1. Wide outer heat glow
        const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, R(38));
        grad.addColorStop(0, `rgba(255,80,0,${0.35 + 0.1*Math.sin(t/120)})`);
        grad.addColorStop(0.5, `rgba(239,68,68,${0.18 + 0.07*Math.sin(t/180)})`);
        grad.addColorStop(1, 'rgba(239,68,68,0)');
        ctx.beginPath();
        ctx.arc(cx, cy, R(38), 0, Math.PI*2);
        ctx.fillStyle = grad;
        ctx.fill();

        // 2. Rising flame particles (30 particles, 3 layers)
        for (let i = 0; i < 30; i++) {
          const speed   = 400 + (i % 5) * 90;
          const phase   = (t / speed + i * 0.37) % 1.0;
          const life    = Math.pow(1.0 - phase, 1.4); // fade as they rise
          const yOff    = -phase * R(36);
          const xOff    = Math.sin(t / 300 + i * 1.7) * R(10) * (1 - phase * 0.4);
          const rad     = (R(11) + (i % 4) * R(2)) * life;

          let color;
          if (i % 4 === 0)      color = `rgba(255,240,80,${life})`;        // bright yellow core
          else if (i % 4 === 1) color = `rgba(255,160,20,${life * 0.95})`; // orange
          else if (i % 4 === 2) color = `rgba(239,68,68,${life * 0.85})`;  // red
          else                  color = `rgba(120,20,0,${life * 0.5})`;    // dark smoke edge

          ctx.beginPath();
          ctx.arc(cx + xOff, cy + yOff, Math.max(rad, 1), 0, Math.PI*2);
          ctx.fillStyle = color;
          ctx.fill();
        }

        // 3. Small dark smoke puffs rising above flames
        for (let i = 0; i < 8; i++) {
          const phase  = (t / 1200 + i * 0.125) % 1.0;
          const yOff   = -(R(30) + phase * R(20));
          const xOff   = Math.sin(t / 600 + i * 0.8) * R(8);
          const alpha  = Math.pow(1 - phase, 2) * 0.35;
          ctx.beginPath();
          ctx.arc(cx + xOff, cy + yOff, R(8), 0, Math.PI*2);
          ctx.fillStyle = `rgba(30,30,30,${alpha})`;
          ctx.fill();
        }

      } else if (type === 'debris') {
        // === DEBRIS: dust cloud + polygonal rocks + hazard tape ===
        // 1. Pulsing dust cloud (elliptical)
        const dustGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, R(30));
        dustGrad.addColorStop(0, `rgba(120,110,90,${0.55 + 0.1*Math.sin(t/220)})`);
        dustGrad.addColorStop(0.6, `rgba(100,90,75,0.3)`);
        dustGrad.addColorStop(1, 'rgba(80,70,60,0)');
        ctx.save();
        ctx.scale(1, 0.65);
        ctx.beginPath();
        ctx.arc(cx, cy / 0.65, R(30), 0, Math.PI*2);
        ctx.fillStyle = dustGrad;
        ctx.fill();
        ctx.restore();

        // 2. Dust particles drifting outward
        for (let i = 0; i < 10; i++) {
          const phase  = (t / 1800 + i * 0.1) % 1.0;
          const ang    = (i / 10) * Math.PI * 2;
          const drift  = phase * R(22);
          const alpha  = (1 - phase) * 0.4;
          ctx.beginPath();
          ctx.arc(cx + Math.cos(ang) * drift, cy + Math.sin(ang) * drift * 0.6, R(5), 0, Math.PI*2);
          ctx.fillStyle = `rgba(160,150,130,${alpha})`;
          ctx.fill();
        }

        // 3. Jagged rocks (5 polygons, pseudo-random placement via seed)
        const seed = pos[0] * 3.7 + pos[1] * 5.3;
        const rocks = [
          { dx: -R(12), dy: -R(6),  s: R(8)  },
          { dx:  R(8),  dy: -R(10), s: R(6)  },
          { dx:  R(14), dy:  R(4),  s: R(7)  },
          { dx: -R(4),  dy:  R(10), s: R(9)  },
          { dx:  R(2),  dy: -R(2),  s: R(5)  },
        ];
        rocks.forEach((r, i) => {
          const pts = 5 + (i % 2);
          ctx.beginPath();
          for (let p = 0; p < pts; p++) {
            const a = (p / pts) * Math.PI * 2 + seed * 0.1 * i;
            const jitter = 0.7 + ((seed * (p + i) * 11.3) % 0.6);
            const px = cx + r.dx + Math.cos(a) * r.s * jitter;
            const py = cy + r.dy + Math.sin(a) * r.s * jitter * 0.8;
            p === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
          }
          ctx.closePath();
          const shade = 60 + (i * 15);
          ctx.fillStyle = `rgb(${shade},${shade-5},${shade-10})`;
          ctx.fill();
          ctx.strokeStyle = '#1e293b';
          ctx.lineWidth = R(1);
          ctx.stroke();
        });

        // 4. Hazard tape (black + amber dashes)
        ctx.save();
        ctx.lineCap = 'round';
        ctx.lineWidth = R(6);
        ctx.beginPath();
        ctx.moveTo(cx - R(20), cy + R(8));
        ctx.lineTo(cx + R(20), cy - R(8));
        ctx.strokeStyle = '#F59E0B';
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(cx - R(20), cy + R(8));
        ctx.lineTo(cx + R(20), cy - R(8));
        ctx.setLineDash([R(6), R(6)]);
        ctx.strokeStyle = '#000000';
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.restore();
      }
    });

    /* === SOS BEACONS === */"""

# Find and replace the old HAZARDS block
idx_start = html.find(old_hazards_block_start)
idx_end   = html.find(old_hazards_block_end)
if idx_start != -1 and idx_end != -1:
    html = html[:idx_start] + new_hazards + '\n    ' + html[idx_end:]
    print("Hazard render block replaced OK")
else:
    print("WARNING: Could not find hazard block boundaries!")

# -- 2b. Add SMOKE_LEVEL global JS var
if 'let SMOKE_LEVEL' not in html:
    html = html.replace('let GLOBAL_HAZARDS = {};', 'let GLOBAL_HAZARDS = {};\n  let SMOKE_LEVEL = "none";')

# -- 2c. Pick up smoke from /api/status poll
if 'SMOKE_LEVEL = data.smoke_level' not in html:
    html = html.replace(
        'GLOBAL_HAZARDS = st.hazards || {};',
        'GLOBAL_HAZARDS = st.hazards || {};\n    SMOKE_LEVEL = st.smoke_level || "none";'
    )

# -- 2d. Add smoke voice alert trigger when smoke changes
if 'smokeVoiceTriggered' not in html:
    html = html.replace(
        'SMOKE_LEVEL = st.smoke_level || "none";',
        '''SMOKE_LEVEL = st.smoke_level || "none";
    if (SMOKE_LEVEL !== "none" && !window.smokeVoiceTriggered) {
      window.smokeVoiceTriggered = true;
      if (typeof speak === 'function') speak("Warning! Smoke detected. Follow the glowing path to the nearest exit immediately!");
      showToast("⚠️ Smoke detected! Follow the lit route!", 6000);
    } else if (SMOKE_LEVEL === "none") {
      window.smokeVoiceTriggered = false;
    }'''
    )

# -- 2e. Add SMOKE render block AFTER SOS BEACONS, BEFORE ROOM TEXTS
smoke_render = """
    /* === SMOKE OVERLAY === */
    if (SMOKE_LEVEL && SMOKE_LEVEL !== "none") {
      const cw = canvas.width  / (window.devicePixelRatio||1);
      const ch = canvas.height / (window.devicePixelRatio||1);
      const t  = Date.now();

      // Background fog layer
      let fogAlpha = SMOKE_LEVEL === "light" ? 0.25 : SMOKE_LEVEL === "heavy" ? 0.60 : 0.88;
      ctx.fillStyle = `rgba(60,60,60,${fogAlpha})`;
      ctx.fillRect(0, 0, cw, ch);

      // Animated drifting smoke puffs
      const puffCount = SMOKE_LEVEL === "light" ? 14 : SMOKE_LEVEL === "heavy" ? 24 : 10;
      for (let i = 0; i < puffCount; i++) {
        const seedX = (i * 137.5) % 1.0;
        const seedY = (i * 97.3)  % 1.0;
        const phase = (t / (3000 + i * 200) + i * 0.07) % 1.0;
        const px = (seedX * cw + Math.sin(t/2000 + i) * cw * 0.08 + phase * cw * 0.12) % cw;
        const py = (seedY * ch + Math.cos(t/2500 + i * 0.7) * ch * 0.06) % ch;
        const rad = (cw * 0.06) + (i % 4) * (cw * 0.02);
        const alpha = (SMOKE_LEVEL === "blackout" ? 0.15 : 0.22) + 0.06 * Math.sin(t/800 + i);

        const grad = ctx.createRadialGradient(px, py, 0, px, py, rad);
        grad.addColorStop(0, `rgba(80,80,80,${alpha})`);
        grad.addColorStop(1, 'rgba(60,60,60,0)');
        ctx.beginPath();
        ctx.arc(px, py, rad, 0, Math.PI*2);
        ctx.fillStyle = grad;
        ctx.fill();
      }

      // === BLACKOUT MODE: make the escape path GLOW ===
      if (SMOKE_LEVEL === "blackout") {
        // Re-draw the path on top with a neon glow effect
        ctx.save();
        ctx.shadowColor = '#22c55e';
        ctx.shadowBlur  = R(20);
        ctx.strokeStyle = '#4ade80';
        ctx.lineWidth   = R(6);
        ctx.lineCap     = 'round';
        ctx.lineJoin    = 'round';
        ctx.beginPath();
        let started = false;
        for (let i = 0; i < path.length - 1; i++) {
          const p1 = NODE_POS[path[i]]   || (GRAPH ? GRAPH.nodes[path[i]]   : null);
          const p2 = NODE_POS[path[i+1]] || (GRAPH ? GRAPH.nodes[path[i+1]] : null);
          if (!p1 || !p2) continue;
          if (!started) { ctx.moveTo(X(p1[0]), Y(p1[1])); started = true; }
          ctx.lineTo(X(p2[0]), Y(p2[1]));
        }
        ctx.stroke();

        // Second glow pass (wider, dimmer)
        ctx.lineWidth = R(14);
        ctx.strokeStyle = 'rgba(34,197,94,0.25)';
        ctx.shadowBlur = R(30);
        ctx.beginPath();
        started = false;
        for (let i = 0; i < path.length - 1; i++) {
          const p1 = NODE_POS[path[i]]   || (GRAPH ? GRAPH.nodes[path[i]]   : null);
          const p2 = NODE_POS[path[i+1]] || (GRAPH ? GRAPH.nodes[path[i+1]] : null);
          if (!p1 || !p2) continue;
          if (!started) { ctx.moveTo(X(p1[0]), Y(p1[1])); started = true; }
          ctx.lineTo(X(p2[0]), Y(p2[1]));
        }
        ctx.stroke();
        ctx.shadowBlur = 0;
        ctx.restore();
      }
    }

    /* === ROOM TEXTS === */"""

if 'SMOKE OVERLAY ===' not in html:
    html = html.replace('    /* === ROOM TEXTS === */', smoke_render)
    print("Smoke render block inserted OK")

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html done")

# =================================================================
# STEP 3: admin.html — Add Smoke Simulator panel
# =================================================================
with open('templates/admin.html', 'r', encoding='utf-8') as f:
    admin = f.read()

smoke_html = """
      <!-- SMOKE SIMULATOR -->
      <div style="margin-bottom:24px;">
        <div class="section-title" style="color:#64748b;">&#127787; Smoke Simulation</div>
        <div style="background:var(--panel); border:1px solid var(--border); padding:16px; border-radius:12px;">
          <p style="font-size:0.8rem; color:var(--muted); margin-bottom:14px;">Simulate smoke filling the building. Blackout mode makes the escape route glow like emergency runway lights.</p>
          <div style="display:flex; gap:10px; flex-wrap:wrap;">
            <button id="smk-none"  class="mini-btn" style="border-color:var(--green);  color:var(--green);  background:transparent; padding:8px 14px; font-weight:700; cursor:pointer;" onclick="setSmoke('none')">&#9989; Clear Smoke</button>
            <button id="smk-light" class="mini-btn" style="border-color:#94a3b8; color:#94a3b8; background:transparent; padding:8px 14px; font-weight:700; cursor:pointer;" onclick="setSmoke('light')">&#127787; Light Smoke</button>
            <button id="smk-heavy" class="mini-btn" style="border-color:#64748b; color:#64748b; background:transparent; padding:8px 14px; font-weight:700; cursor:pointer;" onclick="setSmoke('heavy')">&#128168; Heavy Smoke</button>
            <button id="smk-black" class="mini-btn" style="border-color:#0f172a; color:#e2e8f0; background:#0f172a;  padding:8px 14px; font-weight:700; cursor:pointer;" onclick="setSmoke('blackout')">&#11035; BLACKOUT</button>
          </div>
          <div id="smokeStatus" style="margin-top:10px; font-size:0.78rem; color:var(--muted);">Status: No smoke active</div>
        </div>
      </div>

"""

if 'id="smk-none"' not in admin:
    # Insert before Hazard Simulator section
    admin = admin.replace(
        '<div class="section-title" style="color:var(--red);">',
        smoke_html + '<div class="section-title" style="color:var(--red);">', 1
    )

# Add admin smoke JS
smoke_admin_js = """
  // ===== SMOKE SIMULATOR =====
  let currentSmoke = "none";
  async function setSmoke(level) {
    await fetch('/api/smoke', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({level: level})
    });
    currentSmoke = level;
    updateSmokeUI();
    const labels = { none:'Clear', light:'Light Smoke', heavy:'Heavy Smoke', blackout:'BLACKOUT' };
    addLog('&#127787; Smoke set to: ' + (labels[level] || level));
  }

  function updateSmokeUI() {
    const smkIds = ['smk-none','smk-light','smk-heavy','smk-black'];
    const smkLvl = ['none','light','heavy','blackout'];
    const colors  = ['var(--green)','#94a3b8','#64748b','#e2e8f0'];
    const bgs     = ['transparent','transparent','transparent','#0f172a'];
    smkIds.forEach((id, i) => {
      const btn = document.getElementById(id);
      if (!btn) return;
      if (smkLvl[i] === currentSmoke) {
        btn.style.background = colors[i];
        btn.style.color = smkLvl[i] === 'blackout' ? '#0f172a' : '#0a0f1d';
        btn.style.fontWeight = '900';
      } else {
        btn.style.background = bgs[i];
        btn.style.color = colors[i];
        btn.style.fontWeight = '700';
      }
    });
    const statusEl = document.getElementById('smokeStatus');
    if (statusEl) {
      const msgs = { none:'No smoke active', light:'&#127787; Light smoke drifting...', heavy:'&#128168; Heavy smoke — limited visibility!', blackout:'&#11035; BLACKOUT — emergency route glowing only!' };
      statusEl.innerHTML = 'Status: ' + (msgs[currentSmoke] || currentSmoke);
    }
  }
"""

if 'function setSmoke' not in admin:
    admin = admin.replace('</script>', smoke_admin_js + '\n  </script>', 1)

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin)
print("admin.html done")
print("All done!")
