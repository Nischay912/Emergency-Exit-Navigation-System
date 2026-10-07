import os

file_path = 'templates/index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

start_idx = html.find('function startDemoWalk()')
if start_idx != -1:
    demo_running_idx = html.find('NAV.demoRunning = true;', start_idx)
    if demo_running_idx != -1:
        # Check if already injected to avoid duplication
        if 'window.preDemoUserLocation' not in html[start_idx:demo_running_idx]:
            html = html[:demo_running_idx] + 'window.preDemoUserLocation = currentUser;\n    ' + html[demo_running_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
