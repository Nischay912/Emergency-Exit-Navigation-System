import re
import sys

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the duplicate script injection
html = html.replace('let audioPrompted', '/* duplicate */') # nullify previous injections just in case

# Now append it correctly right before </body>
js_scripts = """
<script>
// --- Added UI Functions ---
function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  document.getElementById('themeIcon').innerHTML = next === 'dark' ? '&#9728;' : '&#127769;';
}

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

window.audioPromptedFlag = false;
const origToggleWalkMode = toggleWalkMode;
window.toggleWalkMode = function() {
  if(!window.audioPromptedFlag) { window.audioPromptedFlag = true; openAudioSettings(); }
  origToggleWalkMode();
};

const origToggleDemoWalk = toggleDemoWalk;
window.toggleDemoWalk = function() {
  if(!window.audioPromptedFlag) { window.audioPromptedFlag = true; openAudioSettings(); }
  origToggleDemoWalk();
};
</script>
"""

# Inject right before </body>
html = html.replace('</body>', js_scripts + '\n</body>')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
