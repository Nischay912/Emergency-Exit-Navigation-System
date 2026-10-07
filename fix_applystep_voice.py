import os

file_path = 'templates/index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

old_block = """    // --- LIVE VOICE NAVIGATION TRIGGER ---
      if (document.getElementById("navOverlay") && document.getElementById("navOverlay").classList.contains("active")) {
        // If nav UI is open, recalculate path from new node (like a GPS) and speak
        openNavigation();
      } else {
        // If nav UI is closed, still guide them if Voice is enabled
        announceLiveNavigationStep();
      }
        if (GRAPH && GRAPH.exit_nodes && GRAPH.exit_nodes.includes(near)) { showToast("✅ Emergency Exit Reached."); if (PDR.active && typeof toggleWalkMode === "function") { toggleWalkMode(); } }
    }"""

new_block = """    // --- LIVE VOICE NAVIGATION TRIGGER ---
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
    }"""

# Check for emoji replacement since powershell output showed o. for the checkmark emoji.
# Let's just find the block using index to be foolproof.
start_idx = html.find('// --- LIVE VOICE NAVIGATION TRIGGER ---')
end_idx = html.find('// Speed calculation', start_idx)

if start_idx != -1 and end_idx != -1:
    html = html[:start_idx] + new_block + '\n    ' + html[end_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
