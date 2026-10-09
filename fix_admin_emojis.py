import os
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Admin.html replacements
    # 1. Theme toggle button
    html = re.sub(
        r'<button class="theme-btn" onclick="toggleTheme\(\)" id="themeIcon">.*?</button>',
        '<button class="theme-btn" onclick="toggleTheme()" id="themeIcon">&#127769;</button>',
        html
    )
    
    # 2. Hazard Simulator Title
    html = re.sub(
        r'<div class="section-title" style="color:var\(--red\);">.*?Hazard Simulator \(Fire / Blockades\)</div>',
        '<div class="section-title" style="color:var(--red);">&#128680; Hazard Simulator (Fire / Blockades)</div>',
        html
    )

    # 3. Fire Hazard Button
    html = re.sub(
        r'>[^<]*Fire near Staff Lounge \(Left\)</button>',
        '>&#128293; Fire near Staff Lounge (Left)</button>',
        html
    )

    # 4. Blockade Hazard Button
    html = re.sub(
        r'>[^<]*Blockade at East Hallway</button>',
        '>&#128647; Blockade at East Hallway</button>',
        html
    )

    # 5. Clear All Hazards Button
    html = re.sub(
        r'>[^<]*Clear All Hazards</button>',
        '>&#9989; Clear All Hazards</button>',
        html
    )

    # 6. toggleTheme JS
    html = re.sub(
        r"btn\.innerHTML = next === 'dark' \? '.*?' : '.*?';",
        "btn.innerHTML = next === 'dark' ? '&#9728;' : '&#127769;';",
        html
    )
    html = re.sub(
        r"btn\.innerHTML = savedTheme === 'dark' \? '.*?' : '.*?';",
        "btn.innerHTML = savedTheme === 'dark' ? '&#9728;' : '&#127769;';",
        html
    )

    # 7. JS addLogs
    html = re.sub(
        r'addLog\(".*?GLOBAL ALARM TRIGGERED"\);',
        'addLog("&#128680; GLOBAL ALARM TRIGGERED");',
        html
    )
    html = re.sub(
        r'addLog\(`.*?HAZARD TRIGGERED: \$\{type\.toUpperCase\(\)\} at \$\{node\.replace\(/_/g,\' \'\}!\`\);',
        r'addLog(`&#9888; HAZARD TRIGGERED: ${type.toUpperCase()} at ${node.replace(/_/g,\' \')}!`);',
        html
    )
    
    # Other potential corrupted stuff in admin.html:
    # "Live SOS Alerts" might have an emoji? The screenshot shows "Live SOS Alerts" clean, but wait, the badge above it?
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

fix_file('templates/admin.html')
