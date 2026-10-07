import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. We will append the Light/Dark toggle button HTML
toggle_html = """
<button id="themeToggle" class="floating-btn" onclick="toggleTheme()">
  <span id="themeIcon">&#127769;</span>
</button>
<button id="audioToggle" class="floating-btn" onclick="openAudioSettings()" style="top: 80px;">
  <span id="audioIcon">&#128266;</span>
</button>

<div id="audioModal" class="modal-overlay">
  <div class="modal-card">
    <h3 style="margin-top:0; color:var(--text);">Audio Settings</h3>
    <div style="margin-bottom: 12px;">
      <label style="display:block; font-size:12px; color:var(--muted); margin-bottom:4px;">Language</label>
      <select id="langSelect" class="loc-select" onchange="changeLanguage(this.value)">
        <option value="en-US">English</option>
        <option value="hi-IN">Hindi (~~~<~~)</option>
        <option value="kn-IN">Kannada ("3؅_-)</option>
      </select>
    </div>
    <div style="margin-bottom: 20px;">
      <label style="display:block; font-size:12px; color:var(--muted); margin-bottom:4px;">Voice</label>
      <button id="muteBtn" class="walk-btn calib" onclick="toggleMute()" style="width:100%;">
        &#128266; Mute / Unmute
      </button>
    </div>
    <button class="nav-trigger" onclick="closeAudioSettings()">Done</button>
  </div>
</div>
"""
if 'id="themeToggle"' not in html:
    html = html.replace('<div class="app">', toggle_html + '\n<div class="app">')

# 2. Add the JS functions for Theme and Audio Settings
js_additions = """
// Theme logic
function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  document.getElementById('themeIcon').innerHTML = next === 'dark' ? '&#9728;' : '&#127769;';
}

// Audio Settings Modal
function openAudioSettings() { document.getElementById('audioModal').classList.add('active'); }
function closeAudioSettings() { document.getElementById('audioModal').classList.remove('active'); }
function toggleMute() {
  VOICE.enabled = !VOICE.enabled;
  const btn = document.getElementById('muteBtn');
  const icon = document.getElementById('audioIcon');
  if(VOICE.enabled) {
    btn.innerHTML = '&#128266; Mute';
    btn.style.background = 'var(--green)'; btn.style.color = 'white';
    icon.innerHTML = '&#128266;';
  } else {
    btn.innerHTML = '&#128263; Unmute';
    btn.style.background = '#F1F3F4'; btn.style.color = 'var(--text)';
    icon.innerHTML = '&#128263;';
  }
}
// Automatically open audio settings before walk/demo if language not yet picked
let audioPrompted = false;

// Override toggleWalkMode to prompt audio first
const origToggleWalkMode = toggleWalkMode;
toggleWalkMode = function() {
  if(!audioPrompted) { audioPrompted = true; openAudioSettings(); }
  origToggleWalkMode();
};
// Override toggleDemoWalk to prompt audio first
const origToggleDemoWalk = toggleDemoWalk;
toggleDemoWalk = function() {
  if(!audioPrompted) { audioPrompted = true; openAudioSettings(); }
  origToggleDemoWalk();
};
"""
if 'function toggleTheme' not in html:
    html = html.replace('</script>', js_additions + '\n</script>')

# 3. Apply the CSS Overhaul
css_overhaul = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

:root {
  --bg: #F8F9FA; --panel: #FFFFFF; --border: #DADCE0; --text: #202124; --muted: #5F6368;
  --red: #EA4335; --green: #34A853; --amber: #FBBC04; --blue: #1A73E8; --route-bg: #E8F0FE;
  --map-bg: #E8EAED; --corridor: #FFFFFF; --room: #F1F3F4;
}
:root[data-theme="dark"] {
  --bg: #121212; --panel: #1E1E1E; --border: #333333; --text: #E0E0E0; --muted: #9AA0A6;
  --red: #F28B82; --green: #81C995; --amber: #FDE293; --blue: #8AB4F8; --route-bg: rgba(138,180,248,0.15);
  --map-bg: #1A1A1A; --corridor: #2D2D2D; --room: #242424;
}

* { box-sizing: border-box; }
body { margin: 0; padding: 0; font-family: 'Roboto', sans-serif; background: var(--bg); color: var(--text); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }

/* Floating Buttons */
.floating-btn { position: absolute; right: 20px; top: 20px; width: 48px; height: 48px; border-radius: 24px; background: var(--panel); border: 1px solid var(--border); box-shadow: 0 2px 6px rgba(0,0,0,0.15); display: flex; align-items: center; justify-content: center; font-size: 20px; cursor: pointer; z-index: 100; transition: 0.2s; color: var(--text); }
.floating-btn:hover { background: var(--route-bg); }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 1000; display: none; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.3s; }
.modal-overlay.active { display: flex; opacity: 1; }
.modal-card { background: var(--panel); padding: 24px; border-radius: 16px; width: 90%; max-width: 320px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); border: 1px solid var(--border); }

/* Layout */
.app { display: block; position: absolute; inset: 0; }
.map-col { position: absolute; inset: 0; z-index: 1; background: var(--map-bg); }
.canvas-wrap { position: absolute; inset: 0; width: 100%; height: 100%; }
canvas { display: block; width: 100%; height: 100%; }

/* Bottom Sheet / Sidebar */
.sidebar { 
  position: absolute; bottom: 0; left: 0; right: 0; z-index: 10; max-height: 50vh; 
  background: var(--panel); border-radius: 20px 20px 0 0; padding: 20px; 
  box-shadow: 0 -4px 15px rgba(0,0,0,0.15); overflow-y: auto; border-top: 1px solid var(--border); 
}
@media(min-width: 768px) {
  .sidebar { 
    top: 20px; left: 20px; bottom: 20px; width: 400px; max-height: none; 
    border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.15); border: 1px solid var(--border);
  }
}

.info-bar { display: none; }

.sec { margin-bottom: 20px; }
.sec-lbl { font-size: 12px; font-weight: 700; color: var(--muted); text-transform: uppercase; margin-bottom: 12px; letter-spacing: 0.5px; }
.loc-card { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 16px; }
.at { font-size: 13px; color: var(--muted); }
.name { font-size: 18px; font-weight: 700; margin-top: 4px; color: var(--text); }
.hint { font-size: 11px; color: var(--muted); margin-top: 12px; margin-bottom: 4px; }
.loc-select { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 8px; font-family: inherit; font-size: 14px; background: var(--bg); color: var(--text); }
.rec-card { background: var(--route-bg); border: 1px solid var(--blue); border-radius: 12px; padding: 16px; color: var(--blue); }
.rl { font-size: 12px; font-weight: 700; margin-bottom: 4px; color: var(--blue); }
.re { font-size: 24px; font-weight: 700; margin-bottom: 8px; color: var(--text); }
.rp { font-size: 13px; color: var(--blue); line-height: 1.4; }

.nav-trigger { width: 100%; padding: 14px; background: var(--blue); color: white; border: none; border-radius: 24px; font-size: 15px; font-weight: 500; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 2px 6px rgba(26,115,232,0.3); transition: 0.2s; }
.nav-trigger:hover { background: #174ea6; box-shadow: 0 4px 10px rgba(26,115,232,0.4); }
.walk-btn { width: 100%; padding: 12px; background: var(--panel); border: 1px solid var(--border); color: var(--blue); border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; margin-bottom: 8px; transition: 0.2s; }
.walk-btn:hover { background: var(--bg); }
.walk-btn.start { background: var(--green); color: white; border: none; }
.walk-btn.start:hover { background: #0D652D; }

/* Exit List styling */
.exit-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--border); font-size: 14px; color: var(--text); }
.exit-row.best { background: var(--route-bg); border-radius: 8px; padding-left: 8px; padding-right: 8px; border-bottom: none; }
.exit-row-name { font-weight: 500; }
.cpill { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; background: var(--bg); color: var(--muted); border: 1px solid var(--border); }
.cpill.Low { background: #E6F4EA; color: #137333; border-color: #137333; }
.cpill.Medium { background: #FEF7E0; color: #B06000; border-color: #B06000; }
.cpill.High { background: #FCE8E6; color: #C5221F; border-color: #C5221F; }

/* Full Navigation Overlay Fixes */
.nav-overlay { position: fixed; inset: 0; background: var(--panel); z-index: 300; display: flex; flex-direction: column; transform: translateY(100%); transition: transform 0.3s cubic-bezier(0.2, 0.8, 0.2, 1); overflow: hidden; }
.nav-overlay.active { transform: translateY(0); }

/* The top part of the navigation overlay */
.nav-street { padding: 20px; font-size: 16px; color: var(--muted); background: var(--bg); border-bottom: 1px solid var(--border); }
#navFrom { font-weight: bold; color: var(--text); }
.nav-arrow-row { display: flex; align-items: center; gap: 16px; padding: 24px; background: var(--green); color: white; }
.nav-arrow { font-size: 48px; font-weight: bold; }
.nav-action { font-size: 28px; font-weight: bold; }
.nav-target { font-size: 18px; margin-top: 8px; opacity: 0.9; }
.nav-dist { font-size: 16px; margin-top: 4px; opacity: 0.8; }
.nav-compass-badge { display: none; }
.nav-next { padding: 16px; background: var(--bg); display: flex; align-items: center; gap: 12px; border-bottom: 1px solid var(--border); }
.nav-next-icon { font-size: 20px; color: var(--muted); }
.nav-next-txt { font-size: 14px; color: var(--text); }
.nav-prog-bar { height: 4px; background: var(--border); width: 100%; }
.nav-prog-fill { height: 100%; background: var(--blue); transition: width 0.3s; }

/* Canvas in nav */
#navCanvas { flex: 1; min-height: 200px; width: 100%; background: var(--map-bg); }

/* Step List */
#navStepList { max-height: 30vh; overflow-y: auto; background: var(--panel); padding: 16px; display: flex; flex-direction: column; gap: 8px; border-top: 1px solid var(--border); }
.nav-step-item { background: var(--bg); padding: 16px; border-radius: 12px; border: 1px solid var(--border); display: flex; gap: 16px; align-items: center; }
.nav-step-item.current { border-color: var(--blue); box-shadow: 0 2px 8px rgba(26,115,232,0.2); }
.nav-step-arrow { font-size: 24px; color: var(--blue); width: 32px; text-align: center; }
.nav-step-info { flex: 1; }
.nav-step-action { font-size: 16px; font-weight: 500; color: var(--text); }
.nav-step-sub { font-size: 13px; color: var(--muted); margin-top: 4px; }
.nav-step-badge { font-size: 11px; font-weight: 700; background: var(--green); color: white; padding: 4px 8px; border-radius: 8px; }

.nav-bottom { padding: 16px; background: var(--panel); border-top: 1px solid var(--border); display: flex; gap: 12px; padding-bottom: max(16px, env(safe-area-inset-bottom)); }
.nav-close-btn { flex: 1; background: var(--bg); color: var(--text); border: 1px solid var(--border); padding: 14px; border-radius: 12px; font-weight: 500; cursor: pointer; }
.nav-demo-btn { flex: 2; background: var(--blue); color: white; border: none; padding: 14px; border-radius: 12px; font-weight: 500; cursor: pointer; }
.nav-demo-btn.stop { background: var(--red); }

@keyframes flash { 0%, 100% { background: rgba(234, 67, 53, 0); } 50% { background: rgba(234, 67, 53, 0.3); } }
.alarm-overlay { position: fixed; inset: 0; pointer-events: none; z-index: 9999; display: none; animation: flash 0.6s infinite; }
</style>
"""
html = re.sub(r'<style>.*?</style>', css_overhaul, html, flags=re.DOTALL)

# 4. Modify the canvas drawing logic in `render()` to respect Dark Theme
start_draw = html.find('// Background')
end_draw = html.find('Object.entries(ROOM_RECTS)')
if start_draw != -1 and end_draw != -1:
    new_draw = """const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    
    // Background
    ctx.fillStyle = isDark ? "#1A1A1A" : "#E8EAED";
    ctx.fillRect(0,0,cw,ch);
    
    if(!GRAPH) return;
    
    // 1. Corridors
    ctx.fillStyle = isDark ? "#2D2D2D" : "#FFFFFF";
    CORRIDORS.forEach(c => {
      ctx.fillRect(X(c.x), Y(c.y), X(c.w), Y(c.h));
    });
    
    // 2. Rooms
    """
    html = html[:start_draw] + new_draw + html[end_draw:]

# 5. Fix Room drawing colors to be theme aware
html = html.replace('ctx.fillStyle = isUser ? "#FCE8E6" : onPath ? "#E8F0FE" : "#F1F3F4";',
                    'ctx.fillStyle = isUser ? (isDark?"#3b1414":"#FCE8E6") : onPath ? (isDark?"#122a4f":"#E8F0FE") : (isDark?"#242424":"#F1F3F4");')
html = html.replace('ctx.strokeStyle = isUser ? "#EA4335" : onPath ? "#1A73E8" : "#DADCE0";',
                    'ctx.strokeStyle = isUser ? (isDark?"#F28B82":"#EA4335") : onPath ? (isDark?"#8AB4F8":"#1A73E8") : (isDark?"#333333":"#DADCE0");')
html = html.replace('ctx.fillStyle = isUser ? "#C5221F" : onPath ? "#174EA6" : "#5F6368";',
                    'ctx.fillStyle = isUser ? (isDark?"#F28B82":"#C5221F") : onPath ? (isDark?"#8AB4F8":"#174EA6") : (isDark?"#9AA0A6":"#5F6368");')


with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
