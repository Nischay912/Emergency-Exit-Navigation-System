import re

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'addLog\(".*?Global Alarm Deactivated"\);', 'addLog("&#9989; Global Alarm Deactivated");', html)
html = re.sub(r'addLog\(`.*?Hazard Cleared at', 'addLog(`&#9989; Hazard Cleared at', html)
html = re.sub(r'addLog\(`.*?HAZARD TRIGGERED:', 'addLog(`&#9888; HAZARD TRIGGERED:', html)
html = re.sub(r'addLog\(".*?All hazards cleared\. Paths restored\."\);', 'addLog("&#9989; All hazards cleared. Paths restored.");', html)
html = re.sub(r'addLog\(\'&#9989; SOS cleared.*?person rescued at ID:', 'addLog(\'&#9989; SOS cleared | person rescued at ID:', html)

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)
