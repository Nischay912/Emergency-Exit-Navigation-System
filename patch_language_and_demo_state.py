import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add ID to the overlay text
html = html.replace('<div class="exit-reached-title">', '<div class="exit-reached-title" id="exitReachedText">')

# 2. Dynamic Language Logic for Exit Reached
lang_logic = """
          let exitSpokenMsg = "Emergency Exit Reached. Evacuate Now!";
          let exitHtmlMsg = "🚨 EMERGENCY EXIT REACHED 🚨<br><br>EVACUATE NOW!";
          if (typeof VOICE !== 'undefined') {
              if (VOICE.lang === 'hi-IN') {
                  exitSpokenMsg = "आपातकालीन निकास पर पहुंच गए हैं। कृपया तुरंत बाहर निकलें।";
                  exitHtmlMsg = "🚨 आपातकालीन निकास 🚨<br><br>तुरंत बाहर निकलें!";
              } else if (VOICE.lang === 'kn-IN') {
                  exitSpokenMsg = "ತುರ್ತು ನಿರ್ಗಮನ ತಲುಪಿದ್ದೀರಿ. ದಯವಿಟ್ಟು ತಕ್ಷಣ ಹೊರಹೋಗಿ.";
                  exitHtmlMsg = "🚨 ತುರ್ತು ನಿರ್ಗಮನ 🚨<br><br>ತಕ್ಷಣ ಹೊರಹೋಗಿ!";
              }
          }
          const overlayTxt = document.getElementById('exitReachedText');
          if (overlayTxt) overlayTxt.innerHTML = exitHtmlMsg;
          document.getElementById('exitReachedOverlay').classList.add('active');
          if (typeof speak === 'function') speak(exitSpokenMsg);
"""

# Replace the hardcoded English in applyStep
old_apply_exit = """          document.getElementById('exitReachedOverlay').classList.add('active');
          if (typeof speak === 'function') speak("Emergency Exit Reached. Evacuate Now!");"""

html = html.replace(old_apply_exit, lang_logic)

# Replace the hardcoded English in finishDemoWalk
old_finish_exit = """    document.getElementById('exitReachedOverlay').classList.add('active');
    if (typeof speak === 'function') speak("Emergency Exit Reached. Evacuate Now!");"""

html = html.replace(old_finish_exit, lang_logic)


# 3. Restore User Position after Demo
old_start_demo = """function startDemoWalk() {
    if (NAV.steps.length === 0) { showToast("No route to walk"); return; }
    NAV.demoRunning = true;"""

new_start_demo = """function startDemoWalk() {
    if (NAV.steps.length === 0) { showToast("No route to walk"); return; }
    window.preDemoUserLocation = currentUser; // Save actual location
    NAV.demoRunning = true;"""

html = html.replace(old_start_demo, new_start_demo)

old_stop_demo = """function stopDemoWalk() {
    NAV.demoRunning = false;
    PDR.active = false;
    if (NAV.demoAnimFrame) cancelAnimationFrame(NAV.demoAnimFrame);
    const btn = document.getElementById("navDemoBtn");
    btn.textContent = "▶ Auto Demo Walk";
    btn.className = "nav-demo-btn";
    btn.onclick = toggleDemoWalk;
  }"""

new_stop_demo = """function stopDemoWalk() {
    NAV.demoRunning = false;
    PDR.active = false;
    if (NAV.demoAnimFrame) cancelAnimationFrame(NAV.demoAnimFrame);
    const btn = document.getElementById("navDemoBtn");
    btn.textContent = "▶ Auto Demo Walk";
    btn.className = "nav-demo-btn";
    btn.onclick = toggleDemoWalk;
    if (window.preDemoUserLocation) {
      currentUser = window.preDemoUserLocation; // Restore actual location
      window.preDemoUserLocation = null;
    }
  }"""

html = html.replace(old_stop_demo, new_stop_demo)


with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
