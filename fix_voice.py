import os

file_path = 'templates/index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

old_trigger = """      if (document.getElementById("navOverlay") && document.getElementById("navOverlay").classList.contains("active")) {
        // If nav UI is open, recalculate path from new node (like a GPS) and speak
        openNavigation();
      } else {
        // If nav UI is closed, still guide them if Voice is enabled
        announceLiveNavigationStep();
      }"""

new_trigger = """      if (document.getElementById("navOverlay") && document.getElementById("navOverlay").classList.contains("active")) {
        openNavigation();
        if (typeof speakStep === 'function') {
            if (typeof VOICE !== 'undefined') VOICE.lastSpoken = -1;
            speakStep(0);
        }
      } else {
        announceLiveNavigationStep();
      }"""

if old_trigger in html:
    html = html.replace(old_trigger, new_trigger)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
