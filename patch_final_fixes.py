import os

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix the Source of Truth Object issue
html = html.replace("data.hazards.includes('Intersection_Mid1')", "'Intersection_Mid1' in data.hazards")
html = html.replace("data.hazards.includes('Corridor_East')", "'Corridor_East' in data.hazards")

# 2. Fix the corrupted Emoji logs
html = html.replace('addLog("o. Global Alarm Deactivated");', 'addLog("&#9989; Global Alarm Deactivated");')
html = html.replace('addLog(`o. Hazard Cleared at ${node.replace(/_/g,\' \')}`);', 'addLog(`&#9989; Hazard Cleared at ${node.replace(/_/g,\' \')}`);')
html = html.replace('addLog(`dYs" HAZARD TRIGGERED: ${type.toUpperCase()} at ${node.replace(/_/g,\' \')}!`);', 'addLog(`&#9888; HAZARD TRIGGERED: ${type.toUpperCase()} at ${node.replace(/_/g,\' \')}!`);')
html = html.replace('addLog("o. All hazards cleared. Paths restored.");', 'addLog("&#9989; All hazards cleared. Paths restored.");')
html = html.replace('addLog(\'&#9989; SOS cleared ?" person rescued at ID: \' + alertId);', 'addLog(\'&#9989; SOS cleared | person rescued at ID: \' + alertId);')

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)
