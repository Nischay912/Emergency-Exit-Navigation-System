import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Voice sync and auto-stop
html = re.sub(
    r'(if\s*\(document\.getElementById\("navOverlay"\)[^{]+\{\s*openNavigation\(\);\s*\})',
    r'if(document.getElementById("navOverlay")&&document.getElementById("navOverlay").classList.contains("active")){ openNavigation(); if (typeof speakStep === "function") { if(typeof VOICE !== "undefined") VOICE.lastSpoken = -1; speakStep(0); } }',
    html,
    flags=re.DOTALL
)

# Auto stop on reaching exit
html = re.sub(
    r'(announceLiveNavigationStep\(\);\s*\})',
    r'\1\n      if (GRAPH && GRAPH.exit_nodes && GRAPH.exit_nodes.includes(near)) { showToast("✅ Emergency Exit Reached."); if (PDR.active && typeof toggleWalkMode === "function") { toggleWalkMode(); } }',
    html
)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
