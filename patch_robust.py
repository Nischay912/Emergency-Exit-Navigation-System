import re

# --- PATCH INDEX.HTML ---
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Inject into init()
if 'evac_userLoc' not in html:
    # Find `async function init(){`
    html = re.sub(
        r'async function init\(\)\s*\{',
        'async function init(){\n    const savedLoc = localStorage.getItem(\'evac_userLoc\');\n    if(savedLoc) {\n        currentUser = savedLoc;\n        document.getElementById("userLbl").textContent = currentUser.replace(/_/g," ");\n    }\n',
        html
    )
    
    # Find `function changeLocation(node){`
    html = re.sub(
        r'function changeLocation\(node\)\s*\{',
        'function changeLocation(node){\n    localStorage.setItem(\'evac_userLoc\', node);\n',
        html
    )
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("index.html patched successfully.")
else:
    print("index.html already patched.")


# --- PATCH ADMIN.HTML ---
with open('templates/admin.html', 'r', encoding='utf-8') as f:
    admin_html = f.read()

if 'admin_events' not in admin_html:
    # Inject into addLog
    admin_html = re.sub(
        r'function addLog\(msg\)\s*\{',
        'function addLog(msg){\n    // INJECTED LOG SAVE\n    setTimeout(() => { sessionStorage.setItem(\'admin_events\', document.getElementById("logList").innerHTML); }, 50);\n',
        admin_html
    )

    # Inject into toggleSim to save state
    # function toggleSim(){ simRunning=!simRunning; ... }
    # We will just append logic to the end of the script to monkeypatch toggleSim or handle it.
    # Actually, toggleSim uses `setInterval` internally.
    # Let's just put the restore logic at the bottom.
    
    restore_script = """
// ==========================================
// ROBUST STATE RESTORATION ON LOAD
// ==========================================
window.addEventListener('DOMContentLoaded', () => {
    // 1. Restore Logs
    const savedLogs = sessionStorage.getItem('admin_events');
    if(savedLogs) document.getElementById('logList').innerHTML = savedLogs;

    // 2. Source of Truth Sync (Hazards & Smoke)
    fetch('/api/status').then(r=>r.json()).then(data => {
        if(data.hazards) {
            if(data.hazards.includes('Intersection_Mid1')) {
                const b = document.getElementById('haz-fire');
                if(b) { b.style.background = 'var(--red)'; b.style.color = 'white'; }
            }
            if(data.hazards.includes('Corridor_East')) {
                const b = document.getElementById('haz-deb');
                if(b) { b.style.background = 'var(--amber)'; b.style.color = 'white'; }
            }
        }
        if(data.smoke_level && data.smoke_level !== 'none') {
            const lbl = {light:'Light Smoke', heavy:'Heavy Smoke', blackout:'BLACKOUT'};
            document.getElementById('smokeStat').innerHTML = 'Status: <span style="color:var(--amber)">' + (lbl[data.smoke_level] || data.smoke_level) + '</span>';
            // Also color the active smoke button if possible (we don't have IDs on them, so this is fine)
        }
    });
});
"""
    admin_html = admin_html.replace('</script>\n</body>', restore_script + '\n</script>\n</body>')

    with open('templates/admin.html', 'w', encoding='utf-8') as f:
        f.write(admin_html)
    print("admin.html patched successfully.")
else:
    print("admin.html already patched.")

