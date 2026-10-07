import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix the setInterval to stop spamming voice every 5 seconds
spam_interval = r'setInterval\(async \(\) => \{\s*if\(document\.getElementById\("navOverlay"\)&&document\.getElementById\("navOverlay"\)\.classList\.contains\("active"\)\)\{\s*openNavigation\(\);\s*if\s*\(typeof speakStep === "function"\)\s*\{\s*if\(typeof VOICE !== "undefined"\)\s*VOICE\.lastSpoken = -1;\s*speakStep\(0\);\s*\}\s*\}\s*\}, 5000\);'
good_interval = """setInterval(async () => {
    if (document.getElementById("navOverlay") && document.getElementById("navOverlay").classList.contains("active") && typeof NAV !== 'undefined' && !NAV.demoRunning && typeof PDR !== 'undefined' && PDR.active) {
      openNavigation();
    }
  }, 5000);"""
html = re.sub(spam_interval, good_interval, html)

# 2. Add the Emergency Exit Overlay CSS and HTML
overlay_css = """
.exit-reached-overlay { position: fixed; inset: 0; background: rgba(220, 38, 38, 0.95); z-index: 9999; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; opacity: 0; pointer-events: none; transition: 0.3s; }
.exit-reached-overlay.active { opacity: 1; pointer-events: auto; }
.exit-reached-title { font-size: 32px; font-weight: 900; text-transform: uppercase; margin-bottom: 16px; text-align: center; animation: pulse-text 1s infinite alternate; }
@keyframes pulse-text { 0% { transform: scale(1); } 100% { transform: scale(1.1); } }
.exit-reached-btn { background: white; color: #dc2626; border: none; padding: 16px 32px; font-size: 18px; font-weight: bold; border-radius: 30px; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
"""
if 'exit-reached-overlay' not in html:
    html = html.replace('</style>', overlay_css + '\n</style>')

overlay_html = """
<div class="exit-reached-overlay" id="exitReachedOverlay">
  <div class="exit-reached-title">🚨 EMERGENCY EXIT REACHED 🚨<br><br>EVACUATE NOW!</div>
  <button class="exit-reached-btn" onclick="document.getElementById('exitReachedOverlay').classList.remove('active')">Dismiss</button>
</div>
"""
if 'id="exitReachedOverlay"' not in html:
    html = html.replace('</body>', overlay_html + '\n</body>')

# 3. Patch applyStep to properly speak on new nodes and show the big overlay on exit
apply_step_match = r'// --- LIVE VOICE NAVIGATION TRIGGER ---.*?(?=    // Speed calculation)'
new_apply_step = """// --- LIVE VOICE NAVIGATION TRIGGER ---
      let isExit = GRAPH && GRAPH.exit_nodes && GRAPH.exit_nodes.includes(near);
      
      if (document.getElementById("navOverlay") && document.getElementById("navOverlay").classList.contains("active")) {
        openNavigation();
        if (!isExit && typeof speakStep === 'function') {
            if (typeof VOICE !== 'undefined') VOICE.lastSpoken = -1;
            speakStep(0);
        }
      } else {
        if (!isExit && typeof announceLiveNavigationStep === 'function') announceLiveNavigationStep();
      }
      
      if (isExit) {
          showToast("🚨 Emergency Exit Reached.");
          document.getElementById('exitReachedOverlay').classList.add('active');
          if (typeof speak === 'function') speak("Emergency Exit Reached. Evacuate Now!");
          if (PDR.active && typeof toggleWalkMode === 'function') toggleWalkMode();
      }
"""
html = re.sub(apply_step_match, new_apply_step, html, flags=re.DOTALL)


# 4. Patch finishDemoWalk so it also shows the overlay and speaks the final phrase!
old_finish_demo = r'function finishDemoWalk\(\)\s*\{([^}]*)\}'
def new_finish_demo(m):
    body = m.group(1)
    # inject speakStep and overlay
    injection = """
    if (typeof speakStep === 'function') speakStep(NAV.steps.length);
    document.getElementById('exitReachedOverlay').classList.add('active');
    if (typeof speak === 'function') speak("Emergency Exit Reached. Evacuate Now!");
    """
    return f"function finishDemoWalk() {{{injection}{body}}}"

html = re.sub(old_finish_demo, new_finish_demo, html)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
