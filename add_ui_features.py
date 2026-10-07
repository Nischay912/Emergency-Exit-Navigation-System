import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. We will append the Light/Dark toggle button HTML and Audio Modal
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
        <option value="hi-IN">Hindi (हिंदी)</option>
        <option value="kn-IN">Kannada (ಕನ್ನಡ)</option>
      </select>
    </div>
    <div style="margin-bottom: 20px;">
      <label style="display:block; font-size:12px; color:var(--muted); margin-bottom:4px;">Voice</label>
      <button id="muteBtn" class="walk-btn start" onclick="toggleMute()" style="width:100%;">
        &#128266; Mute
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
    btn.className = 'walk-btn start';
    icon.innerHTML = '&#128266;';
  } else {
    btn.innerHTML = '&#128263; Unmute';
    btn.className = 'walk-btn';
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
if 'function toggleTheme()' not in html:
    html = html.replace('</script>', js_additions + '\n</script>')

# 3. Add CSS for floating buttons and modals
modal_css = """
<style>
.floating-btn { position: fixed; top: 20px; right: 20px; width: 44px; height: 44px; border-radius: 50%; background: var(--panel); border: 1px solid var(--border); box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; align-items: center; justify-content: center; cursor: pointer; z-index: 1000; font-size: 20px; }
.floating-btn:hover { background: var(--bg); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 2000; display: flex; align-items: center; justify-content: center; opacity: 0; pointer-events: none; transition: 0.2s; }
.modal-overlay.active { opacity: 1; pointer-events: auto; }
.modal-card { background: var(--panel); border-radius: 12px; padding: 24px; width: 320px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
</style>
"""
if '.floating-btn' not in html:
    html = html.replace('</head>', modal_css + '\n</head>')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
