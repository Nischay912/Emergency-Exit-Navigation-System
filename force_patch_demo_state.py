import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Force inject preDemoUserLocation into startDemoWalk
html = re.sub(
    r'(function startDemoWalk\(\)\s*\{[^}]*NAV\.demoRunning\s*=\s*true;)',
    r'function startDemoWalk() { if (NAV.steps.length === 0) { showToast("No route to walk"); return; } window.preDemoUserLocation = currentUser; NAV.demoRunning = true;',
    html
)

# Force inject restoration into stopDemoWalk
html = re.sub(
    r'(function stopDemoWalk\(\)\s*\{[^\}]*btn\.onclick\s*=\s*toggleDemoWalk;\s*)',
    r'\1if (window.preDemoUserLocation) { currentUser = window.preDemoUserLocation; window.preDemoUserLocation = null; } ',
    html
)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
