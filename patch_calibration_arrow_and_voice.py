import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix Arrow Visibility during Calibration
# Change `PDR.active` to `PDR.sensorsEnabled` in drawHeadingArrow
html = html.replace("} else if (typeof PDR !== 'undefined' && PDR.active) {",
                    "} else if (typeof PDR !== 'undefined' && PDR.sensorsEnabled) {")


# 2. Fix Live Voice Sync & 3. Auto Stop on Exit Reached
old_apply_step_trigger = """      if (document.getElementById("navOverlay") && document.getElementById("navOverlay").classList.contains("active")) {
        // If nav UI is open, recalculate path from new node (like a GPS) and speak
        openNavigation();
      } else {
        // If nav UI is closed, still guide them if Voice is enabled
        announceLiveNavigationStep();
      }
    }"""

new_apply_step_trigger = """      if (document.getElementById("navOverlay") && document.getElementById("navOverlay").classList.contains("active")) {
        openNavigation();
        if (typeof speakStep === 'function') {
            // Force reset of lastSpoken to ensure it speaks the new step 0
            if (typeof VOICE !== 'undefined') VOICE.lastSpoken = -1;
            speakStep(0);
        }
      } else {
        announceLiveNavigationStep();
      }
      
      // Auto-stop if we reached an exit
      if (GRAPH && GRAPH.exit_nodes && GRAPH.exit_nodes.includes(near)) {
          showToast("✅ Emergency Exit Reached.");
          if (PDR.active && typeof toggleWalkMode === 'function') {
              toggleWalkMode(); // Turn off pedometer to prevent wandering away
          }
      }
    }"""

if old_apply_step_trigger in html:
    html = html.replace(old_apply_step_trigger, new_apply_step_trigger)


with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
