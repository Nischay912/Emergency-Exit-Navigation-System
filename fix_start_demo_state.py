import os

file_path = 'templates/index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

old_start = """function startDemoWalk() {
    if (NAV.steps.length === 0) { showToast("No route to walk"); return; }
    NAV.demoRunning = true;"""

new_start = """function startDemoWalk() {
    if (NAV.steps.length === 0) { showToast("No route to walk"); return; }
    window.preDemoUserLocation = currentUser;
    NAV.demoRunning = true;"""

if old_start in html:
    html = html.replace(old_start, new_start)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
